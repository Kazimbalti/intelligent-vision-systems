#!/usr/bin/env python3
"""Calibrate a Raspberry Pi camera in ~15 minutes (Lab 6I, after the Drone Dojo video).

    python3 pi_calibrate_20.py --mm 26 --width 640 --height 480            # Pi camera (Picamera2)
    python3 pi_calibrate_20.py --mm 26 --width 640 --height 480 --usb 0    # USB webcam instead

The script shows the live camera (needs a desktop or VNC), looks for the 9 x 6 chessboard in every frame and
automatically keeps a frame only when
  * the whole board is found, and
  * the board is in a clearly NEW place, size or angle compared with every frame kept so far.
After 20 good frames it calibrates, prints the camera matrix and distortion coefficients and saves
calibration_files/cameraMatrix.txt, calibration_files/cameraDistortion.txt and calibration_files/camera.yaml.

Tips from the video: print pattern.png on A4, glue it flat, measure one square (--mm), show the board near all
edges and corners of the image, tilt it, move it near and far. Keep --width/--height the SAME in every script that
uses the calibration.
"""
import argparse
import os
import time

import cv2
import numpy as np


def board_signature(corners, w, h):
    """(x, y, size, skew) of the detected board, each roughly in 0..1, like the ROS calibrator."""
    c = corners.reshape(-1, 2)
    x, y = c[:, 0].mean() / w, c[:, 1].mean() / h
    hull = cv2.convexHull(c.astype(np.float32))
    size = np.sqrt(cv2.contourArea(hull) / (w * h))
    a, b = c[1] - c[0], c[len(c) // 2] - c[0]
    skew = abs(a[0] * b[1] - a[1] * b[0]) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9)
    return np.array([x, y, size, 1 - skew])


def is_new(sig, kept, threshold):
    return all(np.abs(sig - k).sum() > threshold for k in kept)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mm", type=float, required=True, help="size of one chessboard square in mm (measure it!)")
    ap.add_argument("--width", type=int, default=640)
    ap.add_argument("--height", type=int, default=480)
    ap.add_argument("--board", default="9x6", help="inner corners")
    ap.add_argument("--count", type=int, default=20, help="number of good frames to keep")
    ap.add_argument("--novelty", type=float, default=0.15, help="how different a new frame must be (0..1)")
    ap.add_argument("--usb", type=int, default=None, help="use cv2.VideoCapture(index) instead of the Pi camera")
    ap.add_argument("--out", default="calibration_files")
    a = ap.parse_args()
    pattern = tuple(int(v) for v in a.board.lower().split("x"))
    w, h = a.width, a.height
    os.makedirs(a.out, exist_ok=True)

    if a.usb is None:
        from picamera2 import Picamera2
        cam = Picamera2()
        cam.configure(cam.create_video_configuration(main={"size": (w, h), "format": "RGB888"}))
        cam.start()
        time.sleep(1)
        grab = cam.capture_array
    else:
        cap = cv2.VideoCapture(a.usb)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)

        def grab():
            ok, f = cap.read()
            return f if ok else None

    objp = np.zeros((pattern[0] * pattern[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:pattern[0], 0:pattern[1]].T.reshape(-1, 2) * a.mm
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 1e-3)
    objpoints, imgpoints, sigs = [], [], []
    last = 0.0
    while len(imgpoints) < a.count:
        frame = grab()
        if frame is None:
            print("no frame from the camera")
            break
        if frame.shape[1] != w or frame.shape[0] != h:
            frame = cv2.resize(frame, (w, h))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        found, corners = cv2.findChessboardCorners(gray, pattern, cv2.CALIB_CB_FAST_CHECK)
        vis = frame.copy()
        msg, col = "show the chessboard", (0, 0, 255)
        if found:
            corners = corners.reshape(-1, 1, 2)
            cv2.drawChessboardCorners(vis, pattern, corners, found)
            sig = board_signature(corners, w, h)
            if time.time() - last > 0.7 and is_new(sig, sigs, a.novelty):
                corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), crit).reshape(-1, 1, 2)
                objpoints.append(objp); imgpoints.append(corners); sigs.append(sig)
                cv2.imwrite(os.path.join(a.out, f"good_{len(imgpoints):02d}.jpg"), frame)
                last = time.time()
                msg, col = "KEPT!", (0, 255, 0)
            else:
                msg, col = "move/tilt the board to a NEW position", (0, 200, 255)
        for s in sigs:   # where the kept boards were
            cv2.circle(vis, (int(s[0] * w), int(s[1] * h)), 6, (255, 0, 0), -1)
        cv2.putText(vis, f"{len(imgpoints)}/{a.count}  {msg}", (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.7, col, 2)
        cv2.imshow("pi_calibrate_20 (ESC to stop)", vis)
        if cv2.waitKey(1) & 0xFF == 27:
            break
    cv2.destroyAllWindows()
    if len(imgpoints) < 8:
        raise SystemExit(f"only {len(imgpoints)} good frames - not enough to calibrate")

    rms, K, D, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, (w, h), None, None)
    print(f"\nCalibration done with {len(imgpoints)} frames at {w}x{h}")
    print(f"RMS reprojection error: {rms:.3f} px  ({'good' if rms < 0.5 else 'ok' if rms < 1 else 'recalibrate!'})")
    print("camera matrix:\n", K)
    print("distortion coefficients:", D.ravel())
    np.savetxt(os.path.join(a.out, "cameraMatrix.txt"), K, delimiter=",")
    np.savetxt(os.path.join(a.out, "cameraDistortion.txt"), D, delimiter=",")
    fs = cv2.FileStorage(os.path.join(a.out, "camera.yaml"), cv2.FILE_STORAGE_WRITE)
    fs.write("image_width", w); fs.write("image_height", h); fs.write("camera_matrix", K)
    fs.write("distortion_coefficients", D); fs.write("rms", rms); fs.write("square_size_mm", a.mm); fs.release()
    print("saved to", a.out)


if __name__ == "__main__":
    main()
