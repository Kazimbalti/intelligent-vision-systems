#!/usr/bin/env python3
"""Calibrate a camera from chessboard images and save camera.yaml (Lab 6H).

    python3 calibrate.py --imgdir calib_images --board 9x6 --square 24.0
    python3 calibrate.py --imgdir calib_images --board 9x6 --square 24.0 --fisheye
    python3 calibrate.py --imgdir calib_images --board 9x6 --square 24.0 --undistort-to undistorted

--board is the number of INNER corners; --square is the measured square size in mm.
Writes camera.yaml (OpenCV FileStorage: camera_matrix, distortion_coefficients, image size, rms),
prints the per-view reprojection errors and optionally saves undistorted copies of the images.
"""
import argparse
import glob
import os

import cv2
import numpy as np


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--imgdir", default="calib_images")
    ap.add_argument("--board", default="9x6", help="inner corners, e.g. 9x6")
    ap.add_argument("--square", type=float, default=1.0, help="square size in mm")
    ap.add_argument("--out", default="camera.yaml")
    ap.add_argument("--fisheye", action="store_true", help="use the cv2.fisheye model (FOV > ~120 deg)")
    ap.add_argument("--rational", action="store_true", help="8-coefficient rational model for wide lenses")
    ap.add_argument("--max-error", type=float, default=None, help="drop views above this RMS (px) and recalibrate")
    ap.add_argument("--undistort-to", default=None, help="folder for undistorted copies of the images")
    a = ap.parse_args()

    nx, ny = (int(v) for v in a.board.lower().split("x"))
    objp = np.zeros((nx * ny, 3), np.float32)
    objp[:, :2] = np.mgrid[0:nx, 0:ny].T.reshape(-1, 2) * a.square
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 1e-3)

    files = sorted(glob.glob(os.path.join(a.imgdir, "*.jpg")) + glob.glob(os.path.join(a.imgdir, "*.png")))
    objpoints, imgpoints, used, size = [], [], [], None
    for f in files:
        gray = cv2.imread(f, cv2.IMREAD_GRAYSCALE)
        if size is None:
            size = gray.shape[::-1]
        if gray.shape[::-1] != size:
            print(f"skip {f}: size {gray.shape[::-1]} != {size}")
            continue
        ok, c = cv2.findChessboardCorners(gray, (nx, ny), cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE)
        if not ok:
            print(f"skip {f}: board not found")
            continue
        c = cv2.cornerSubPix(gray, c.reshape(-1, 1, 2), (11, 11), (-1, -1), crit).reshape(-1, 1, 2)   # OpenCV 4 and 5
        objpoints.append(objp); imgpoints.append(c); used.append(f)
    if len(used) < 5:
        raise SystemExit(f"only {len(used)} usable images - take more (20-30)")

    def calibrate(op, ip):
        if a.fisheye:
            op64 = [o.reshape(1, -1, 3).astype(np.float64) for o in op]   # (1, N, 3): accepted by OpenCV 4 and 5
            ip64 = [i.reshape(1, -1, 2).astype(np.float64) for i in ip]
            fe = cv2.fisheye   # flag names moved from cv2.fisheye.CALIB_* (OpenCV 4) to cv2.CALIB_* (OpenCV 5)
            flags = (fe.CALIB_RECOMPUTE_EXTRINSIC | fe.CALIB_FIX_SKEW if hasattr(fe, "CALIB_RECOMPUTE_EXTRINSIC")
                     else cv2.CALIB_RECOMPUTE_EXTRINSIC | cv2.CALIB_FIX_SKEW)
            crit = (cv2.TERM_CRITERIA_COUNT + cv2.TERM_CRITERIA_EPS, 100, 1e-8)
            try:
                rms, K, D, rv, tv = cv2.fisheye.calibrate(op64, ip64, size, None, None, flags=flags, criteria=crit)
            except cv2.error:
                rms = np.inf
            if rms > 5:   # did not converge: start from f = W / pi (equidistant lens with a 180 deg view)
                guess = cv2.fisheye.CALIB_USE_INTRINSIC_GUESS if hasattr(fe, "CALIB_USE_INTRINSIC_GUESS") else cv2.CALIB_USE_INTRINSIC_GUESS
                K0 = np.array([[size[0] / np.pi, 0, size[0] / 2], [0, size[0] / np.pi, size[1] / 2], [0, 0, 1]])
                rms, K, D, rv, tv = cv2.fisheye.calibrate(op64, ip64, size, K0, np.zeros(4), flags=flags | guess, criteria=crit)
        else:
            flags = cv2.CALIB_RATIONAL_MODEL if a.rational else 0
            rms, K, D, rv, tv = cv2.calibrateCamera(op, ip, size, None, None, flags=flags)
        return rms, K, D, rv, tv

    def per_view(op, ip, K, D, rv, tv):
        errs = []
        for o, i, r, t in zip(op, ip, rv, tv):
            if a.fisheye:
                p, _ = cv2.fisheye.projectPoints(o.reshape(1, -1, 3).astype(np.float64), r, t, K, D)
            else:
                p, _ = cv2.projectPoints(o, r, t, K, D)
            errs.append(float(np.sqrt(((i.reshape(-1, 2) - p.reshape(-1, 2)) ** 2).sum(1).mean())))
        return errs

    rms, K, D, rv, tv = calibrate(objpoints, imgpoints)
    errs = per_view(objpoints, imgpoints, K, D, rv, tv)
    if a.max_error:
        keep = [k for k, e in enumerate(errs) if e <= a.max_error]
        print(f"dropping {len(used) - len(keep)} views above {a.max_error} px")
        objpoints = [objpoints[k] for k in keep]; imgpoints = [imgpoints[k] for k in keep]; used = [used[k] for k in keep]
        rms, K, D, rv, tv = calibrate(objpoints, imgpoints)
        errs = per_view(objpoints, imgpoints, K, D, rv, tv)

    for f, e in sorted(zip(used, errs), key=lambda x: -x[1]):
        print(f"{e:6.3f} px  {os.path.basename(f)}")
    hfov = 2 * np.degrees(np.arctan(size[0] / 2 / K[0, 0]))
    print(f"\n{len(used)} views, image {size[0]}x{size[1]}, RMS reprojection error {rms:.3f} px")
    print("K =\n", np.array2string(K, precision=2, suppress_small=True))
    print("dist =", np.array2string(D.ravel(), precision=5, suppress_small=True))
    print(f"horizontal FOV (pinhole estimate) ~ {hfov:.1f} deg")
    if rms > 1.0:
        print("WARNING: RMS > 1 px - check blur, board flatness and the views with the largest errors")

    fs = cv2.FileStorage(a.out, cv2.FILE_STORAGE_WRITE)
    fs.write("model", "fisheye" if a.fisheye else ("rational" if a.rational else "pinhole"))
    fs.write("image_width", size[0]); fs.write("image_height", size[1])
    fs.write("camera_matrix", K); fs.write("distortion_coefficients", D)
    fs.write("rms", rms); fs.write("square_size_mm", a.square); fs.write("num_views", len(used))
    fs.release()
    print("saved", a.out)

    if a.undistort_to:
        os.makedirs(a.undistort_to, exist_ok=True)
        if a.fisheye:
            newK = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(K, D, size, np.eye(3), balance=0.0)
            m1, m2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), newK, size, cv2.CV_16SC2)
        else:
            newK, _ = cv2.getOptimalNewCameraMatrix(K, D, size, 0)
            m1, m2 = cv2.initUndistortRectifyMap(K, D, None, newK, size, cv2.CV_16SC2)
        for f in used:
            cv2.imwrite(os.path.join(a.undistort_to, os.path.basename(f)), cv2.remap(cv2.imread(f), m1, m2, cv2.INTER_LINEAR))
        print("undistorted images in", a.undistort_to)


if __name__ == "__main__":
    main()
