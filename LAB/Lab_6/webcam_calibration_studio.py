#!/usr/bin/env python3
"""Webcam Calibration Studio (desktop / offline version) - Lecture 6 live demo.

    pip install opencv-python numpy
    python webcam_calibration_studio.py                       # 9 x 6 board, 25 mm squares, camera 0
    python webcam_calibration_studio.py --board 9x6 --mm 24 --camera 1 --width 1280 --height 720

Keys (click the video window first):
    SPACE  capture a view now           A  auto-capture on/off (still board + new position)
    C      calibrate (>= 8 views)       U  live undistort: raw | split | corrected
    M      measure distance mode        G  straight-line grid on/off
    D      delete the last view         S  save camera.yaml + the captured images
    R      reset                        ESC / Q  quit

Same steps as the in-browser studio (lectures/06_webcam_calibration_studio.html), but runs without internet.
"""
import argparse
import os
import time

import cv2
import numpy as np

CRIT = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
FLAGS = cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_NORMALIZE_IMAGE


def signature(c, w, h, nx):
    c = c.reshape(-1, 2)
    a, b, d, e = c[0], c[nx - 1], c[-1], c[-nx]
    area = abs((b[0] - e[0]) * (d[1] - a[1]) - (d[0] - a[0]) * (b[1] - e[1])) / 2
    v1, v2 = b - a, e - a
    ang = np.arccos(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-9))
    return np.array([c[:, 0].mean() / w, c[:, 1].mean() / h, np.sqrt(area / (w * h)), min(1, 2 * abs(np.pi / 2 - ang))])


def coverage(sigs):
    lim = np.array([0.7, 0.7, 0.4, 0.5])
    if not sigs:
        return np.zeros(4)
    s = np.array(sigs)
    return np.minimum(1, (s.max(0) - s.min(0)) / lim)


def put(img, text, org, scale=0.6, col=(255, 255, 255), bg=(30, 30, 30)):
    (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, scale, 2)
    cv2.rectangle(img, (org[0] - 4, org[1] - th - 6), (org[0] + tw + 4, org[1] + 6), bg, -1)
    cv2.putText(img, text, org, cv2.FONT_HERSHEY_SIMPLEX, scale, col, 2, cv2.LINE_AA)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--board", default="9x6", help="inner corners (the course pattern.png is 9x6)")
    ap.add_argument("--mm", type=float, default=25.0, help="measured square size in mm")
    ap.add_argument("--camera", default="0", help="camera index, or a video file to test without a webcam")
    ap.add_argument("--width", type=int, default=640)
    ap.add_argument("--height", type=int, default=480)
    ap.add_argument("--out", default="my_webcam_calibration")
    a = ap.parse_args()
    nx, ny = (int(v) for v in a.board.lower().split("x"))
    objp = np.zeros((nx * ny, 3), np.float32)
    objp[:, :2] = np.mgrid[0:nx, 0:ny].T.reshape(-1, 2) * a.mm

    cap = cv2.VideoCapture(int(a.camera) if a.camera.isdigit() else a.camera)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, a.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, a.height)
    ok, frame = cap.read()
    if not ok:
        raise SystemExit("cannot open the webcam - try --camera 1, or close Zoom/Teams")
    h, w = frame.shape[:2]
    print(f"camera {a.camera}: {w}x{h}.  Board {nx}x{ny} inner corners, {a.mm} mm squares.")

    imgpoints, sigs, frames = [], [], []
    K = D = None
    maps = None
    auto, und_mode, measure, grid = False, 0, False, False
    last, still, last_auto, flash = None, 0, 0.0, 0.0
    win = "Webcam Calibration Studio  (SPACE capture, A auto, C calibrate, U undistort, M measure, S save, Q quit)"
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        small = cv2.resize(gray, None, fx=min(1, 640 / w), fy=min(1, 640 / w))
        s = small.shape[1] / w
        found, c = cv2.findChessboardCorners(small, (nx, ny), FLAGS | cv2.CALIB_CB_FAST_CHECK)
        corners = c.reshape(-1, 1, 2) / s if found else None
        if corners is not None and last is not None:
            still = still + 1 if np.abs(corners - last).mean() < 1.5 else 0
        else:
            still = 0
        last = corners

        def do_capture():
            nonlocal flash
            ok2, cc = cv2.findChessboardCorners(gray, (nx, ny), FLAGS)
            if not ok2:
                return False
            cc = cv2.cornerSubPix(gray, cc.reshape(-1, 1, 2), (11, 11), (-1, -1), CRIT).reshape(-1, 1, 2)
            imgpoints.append(cc); sigs.append(signature(cc, w, h, nx)); frames.append(frame.copy())
            flash = time.time()
            print(f"view {len(imgpoints)} captured")
            return True

        if auto and corners is not None and still >= 3 and time.time() - last_auto > 1.0:
            sig = signature(corners, w, h, nx)
            if all(np.abs(sig - q).sum() > 0.15 for q in sigs):
                do_capture(); last_auto = time.time()

        # ---------------- display
        if K is not None and und_mode:
            if maps is None:
                newK, _ = cv2.getOptimalNewCameraMatrix(K, D, (w, h), 0)
                maps = cv2.initUndistortRectifyMap(K, D, None, newK, (w, h), cv2.CV_16SC2)
            und = cv2.remap(frame, *maps, cv2.INTER_LINEAR)
            vis = und if und_mode == 2 else np.hstack([frame[:, : w // 2], und[:, w // 2:]])
            if und_mode == 1:
                cv2.line(vis, (w // 2, 0), (w // 2, h), (255, 255, 255), 2)
                put(vis, "raw", (10, h - 12)); put(vis, "corrected", (w // 2 + 10, h - 12))
        else:
            vis = frame.copy()
            for q in imgpoints:
                for x, y in q.reshape(-1, 2):
                    cv2.circle(vis, (int(x), int(y)), 2, (221, 118, 42), -1)
            if corners is not None:
                cv2.drawChessboardCorners(vis, (nx, ny), corners.astype(np.float32), True)
            if measure and K is not None and corners is not None:
                cc = cv2.cornerSubPix(gray, corners.astype(np.float32), (5, 5), (-1, -1), CRIT)
                _, rvec, tvec = cv2.solvePnP(objp, cc, K, D)
                R, _ = cv2.Rodrigues(rvec)
                dist_mm = np.linalg.norm(R @ objp.mean(0) + tvec.ravel())
                cv2.drawFrameAxes(vis, K, D, rvec, tvec, 3 * a.mm, 3)
                put(vis, f"{dist_mm / 10:.1f} cm away", (w - 230, h - 20), 0.9, (255, 255, 255), (60, 120, 40))
        if grid:
            for i in range(1, 8):
                cv2.line(vis, (i * w // 8, 0), (i * w // 8, h), (238, 211, 34), 1)
            for i in range(1, 6):
                cv2.line(vis, (0, i * h // 6), (w, i * h // 6), (238, 211, 34), 1)
        cov = coverage(sigs)
        for k, name in enumerate(["X", "Y", "Size", "Skew"]):
            y0 = 30 + 22 * k
            cv2.rectangle(vis, (60, y0 - 12), (220, y0 + 2), (60, 60, 60), -1)
            col = (77, 122, 31) if cov[k] >= 1 else (60, 162, 230) if cov[k] > 0.5 else (43, 57, 192)
            cv2.rectangle(vis, (60, y0 - 12), (60 + int(160 * cov[k]), y0 + 2), col, -1)
            put(vis, name, (10, y0), 0.5)
        status = f"views {len(imgpoints)}  auto {'ON' if auto else 'off'}"
        status += "  board found" if corners is not None else "  NO board"
        if K is not None:
            status += f"  calibrated (RMS {rms:.2f}px)"
        put(vis, status, (240, 30), 0.6, (255, 255, 255), (40, 86, 138))
        if time.time() - flash < 0.15:
            vis = cv2.addWeighted(vis, 0.5, np.full_like(vis, 255), 0.5, 0)
        cv2.imshow(win, vis)
        k = cv2.waitKey(1) & 0xFF
        if k in (27, ord("q")):
            break
        elif k == ord(" "):
            if not do_capture():
                print("board not found in this frame")
        elif k == ord("a"):
            auto = not auto
        elif k == ord("d") and imgpoints:
            imgpoints.pop(); sigs.pop(); frames.pop()
        elif k == ord("r"):
            imgpoints, sigs, frames, K, D, maps = [], [], [], None, None, None
        elif k == ord("g"):
            grid = not grid
        elif k == ord("u") and K is not None:
            und_mode = (und_mode + 1) % 3
        elif k == ord("m") and K is not None:
            measure = not measure; und_mode = 0
        elif k == ord("c"):
            if len(imgpoints) < 8:
                print("need at least 8 views")
                continue
            rms, K, D, rvecs, tvecs, std_in, _, per_view = cv2.calibrateCameraExtended(
                [objp] * len(imgpoints), imgpoints, (w, h), None, None)
            maps = None
            print(f"\nRMS reprojection error: {rms:.3f} px")
            print("K =\n", np.round(K, 1)); print("dist =", np.round(D.ravel(), 4))
            print("per-view errors:", np.round(per_view.ravel(), 2))
            print(f"horizontal FOV ~ {2 * np.degrees(np.arctan(w / 2 / K[0, 0])):.0f} deg")
        elif k == ord("s") and K is not None:
            os.makedirs(a.out, exist_ok=True)
            fs = cv2.FileStorage(os.path.join(a.out, "camera.yaml"), cv2.FILE_STORAGE_WRITE)
            fs.write("image_width", w); fs.write("image_height", h); fs.write("camera_matrix", K)
            fs.write("distortion_coefficients", D); fs.write("rms", rms); fs.write("square_size_mm", a.mm); fs.release()
            for i, f in enumerate(frames):
                cv2.imwrite(os.path.join(a.out, f"view_{i:02d}.jpg"), f)
            print("saved", a.out)
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
