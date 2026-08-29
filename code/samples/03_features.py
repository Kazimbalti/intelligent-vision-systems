"""
Week 4 - Features, contours & camera calibration.

Three modes:
  contours   : find + count objects by contour, draw bounding boxes
  orb        : ORB keypoints + matching between two images
  calibrate  : chessboard calibration from a folder of images -> intrinsics.npz

Usage:
    python 03_features.py contours  --image objs.jpg
    python 03_features.py orb       --image1 a.jpg --image2 b.jpg
    python 03_features.py calibrate --glob "calib/*.jpg" --cols 9 --rows 6
"""
import argparse
import glob
import cv2
import numpy as np


def contours(args):
    img = cv2.imread(args.image)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    cnts, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    count = 0
    for c in cnts:
        if cv2.contourArea(c) < 300:      # ignore specks
            continue
        count += 1
        x, y, w, h = cv2.boundingRect(c)
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.putText(img, f"objects: {count}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
    cv2.imwrite("contours_out.jpg", img)
    print(f"Found {count} objects -> contours_out.jpg")


def orb(args):
    a = cv2.imread(args.image1, cv2.IMREAD_GRAYSCALE)
    b = cv2.imread(args.image2, cv2.IMREAD_GRAYSCALE)
    orb = cv2.ORB_create(1000)
    ka, da = orb.detectAndCompute(a, None)
    kb, db = orb.detectAndCompute(b, None)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = sorted(bf.match(da, db), key=lambda m: m.distance)[:40]
    out = cv2.drawMatches(a, ka, b, kb, matches, None,
                          flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
    cv2.imwrite("orb_matches.jpg", out)
    print(f"{len(matches)} good matches -> orb_matches.jpg")


def calibrate(args):
    cols, rows = args.cols, args.rows           # inner corners
    objp = np.zeros((rows * cols, 3), np.float32)
    objp[:, :2] = np.mgrid[0:cols, 0:rows].T.reshape(-1, 2)

    objpoints, imgpoints = [], []
    files = glob.glob(args.glob)
    if not files:
        raise SystemExit(f"No images matched {args.glob}")

    shape = None
    for f in files:
        gray = cv2.imread(f, cv2.IMREAD_GRAYSCALE)
        shape = gray.shape[::-1]
        found, corners = cv2.findChessboardCorners(gray, (cols, rows))
        if found:
            objpoints.append(objp)
            corners = cv2.cornerSubPix(
                gray, corners, (11, 11), (-1, -1),
                (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001))
            imgpoints.append(corners)
    print(f"Used {len(objpoints)}/{len(files)} images with a full board.")

    ok, mtx, dist, _, _ = cv2.calibrateCamera(
        objpoints, imgpoints, shape, None, None)
    np.savez("camera_intrinsics.npz", camera_matrix=mtx, dist_coeffs=dist)
    print("Saved camera_intrinsics.npz")
    print("Camera matrix:\n", mtx)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("contours"); c.add_argument("--image", required=True)
    o = sub.add_parser("orb")
    o.add_argument("--image1", required=True); o.add_argument("--image2", required=True)
    k = sub.add_parser("calibrate")
    k.add_argument("--glob", required=True)
    k.add_argument("--cols", type=int, default=9)
    k.add_argument("--rows", type=int, default=6)

    args = ap.parse_args()
    {"contours": contours, "orb": orb, "calibrate": calibrate}[args.cmd](args)


if __name__ == "__main__":
    main()
