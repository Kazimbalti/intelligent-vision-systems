#!/usr/bin/env python3
"""Capture chessboard images for camera calibration (Lab 6H).

Raspberry Pi camera (Picamera2):   python3 capture_calib.py --pi --res 1920x1080 --count 25 --delay 3
USB webcam / laptop camera:        python3 capture_calib.py --device 0 --res 1280x720

With --pi a picture is taken every --delay seconds (move the board in between, hold it still).
With a USB camera a live preview is shown: SPACE saves a view (only if the board is found), ESC quits.
Based on Petros626/Camera-Calibration-with-PiCamera2-OpenCV and niconielsen32/camera-calibration.
"""
import argparse
import os
import time

import cv2


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="calib_images", help="output folder")
    ap.add_argument("--board", default="9x6", help="inner corners, e.g. 9x6")
    ap.add_argument("--res", default="1280x720", help="capture resolution WxH (calibrate at the resolution you will use!)")
    ap.add_argument("--pi", action="store_true", help="use the Raspberry Pi camera via Picamera2")
    ap.add_argument("--device", type=int, default=0, help="cv2.VideoCapture index")
    ap.add_argument("--count", type=int, default=25, help="number of images (--pi)")
    ap.add_argument("--delay", type=float, default=3.0, help="seconds between shots (--pi)")
    ap.add_argument("--lens-position", type=float, default=None,
                    help="Camera Module 3: lock manual focus at this LensPosition (dioptres, e.g. 1.0 = 1 m)")
    a = ap.parse_args()
    pattern = tuple(int(v) for v in a.board.lower().split("x"))
    w, h = (int(v) for v in a.res.lower().split("x"))
    os.makedirs(a.out, exist_ok=True)
    n = len([f for f in os.listdir(a.out) if f.endswith(".jpg")])

    if a.pi:
        from picamera2 import Picamera2
        cam = Picamera2()
        cam.configure(cam.create_still_configuration(main={"size": (w, h), "format": "RGB888"}))
        cam.start()
        time.sleep(1)
        if a.lens_position is not None:
            cam.set_controls({"AfMode": 0, "LensPosition": a.lens_position})   # intrinsics depend on focus
        for _ in range(a.count):
            for s in range(int(a.delay), 0, -1):
                print(f"  next shot in {s} s ...", end="\r")
                time.sleep(1)
            frame = cam.capture_array()
            ok, _ = cv2.findChessboardCorners(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), pattern, cv2.CALIB_CB_FAST_CHECK)
            path = os.path.join(a.out, f"img_{n:03d}.jpg")
            cv2.imwrite(path, frame)
            n += 1
            print(f"{path}: " + ("board found" if ok else "NO board found - move it into view"))
        cam.stop()
        return

    cap = cv2.VideoCapture(a.device)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
    while True:
        ok, frame = cap.read()
        if not ok:
            print("camera read failed")
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        found, corners = cv2.findChessboardCorners(gray, pattern, cv2.CALIB_CB_FAST_CHECK)
        vis = frame.copy()
        if found:
            cv2.drawChessboardCorners(vis, pattern, corners, found)
        cv2.putText(vis, f"{frame.shape[1]}x{frame.shape[0]}  saved: {n}  SPACE=save ESC=quit", (15, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0) if found else (0, 0, 255), 2)
        cv2.imshow("capture_calib", vis)
        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break
        if k == 32 and found:
            path = os.path.join(a.out, f"img_{n:03d}.jpg")
            cv2.imwrite(path, frame)
            n += 1
            print("saved", path)
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
