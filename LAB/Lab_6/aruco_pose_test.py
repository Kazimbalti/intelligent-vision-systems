#!/usr/bin/env python3
"""Check your calibration with an ArUco marker and a ruler (Lab 6I, after the Drone Dojo video).

    python3 aruco_pose_test.py --make-marker            # writes marker_id72.png: print it, measure its size
    python3 aruco_pose_test.py --size 200 --id 72       # Pi camera; marker 200 mm wide
    python3 aruco_pose_test.py --size 200 --id 72 --usb 0

Shows the marker's position (x, y, z in mm) relative to the camera, using calibration_files/cameraMatrix.txt and
cameraDistortion.txt from pi_calibrate_20.py. Test: centre the marker (x ~ 0), slide it 60 mm to the side with a
ruler and check that x changes by ~60 mm. If it is far off, recalibrate. Use the SAME resolution as for calibration.
"""
import argparse
import time

import cv2
import numpy as np


def marker_object_points(size):
    s = size / 2.0   # corner order of ArUco: top-left, top-right, bottom-right, bottom-left
    return np.array([[-s, s, 0], [s, s, 0], [s, -s, 0], [-s, -s, 0]], np.float32)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--id", type=int, default=72)
    ap.add_argument("--size", type=float, default=100.0, help="printed marker size in mm (black square, edge to edge)")
    ap.add_argument("--dict", default="DICT_ARUCO_ORIGINAL")
    ap.add_argument("--width", type=int, default=640)
    ap.add_argument("--height", type=int, default=480)
    ap.add_argument("--calib", default="calibration_files")
    ap.add_argument("--usb", type=int, default=None)
    ap.add_argument("--make-marker", action="store_true")
    a = ap.parse_args()
    dictionary = cv2.aruco.getPredefinedDictionary(getattr(cv2.aruco, a.dict))
    if a.make_marker:
        img = cv2.aruco.generateImageMarker(dictionary, a.id, 800)
        img = cv2.copyMakeBorder(img, 100, 100, 100, 100, cv2.BORDER_CONSTANT, value=255)
        cv2.imwrite(f"marker_id{a.id}.png", img)
        print(f"wrote marker_id{a.id}.png - print it, then measure the black square in mm")
        return

    K = np.loadtxt(f"{a.calib}/cameraMatrix.txt", delimiter=",")
    D = np.loadtxt(f"{a.calib}/cameraDistortion.txt", delimiter=",")
    detector = cv2.aruco.ArucoDetector(dictionary, cv2.aruco.DetectorParameters())
    obj = marker_object_points(a.size)
    if a.usb is None:
        from picamera2 import Picamera2
        cam = Picamera2()
        cam.configure(cam.create_video_configuration(main={"size": (a.width, a.height), "format": "RGB888"}))
        cam.start(); time.sleep(1)
        grab = cam.capture_array
    else:
        cap = cv2.VideoCapture(a.usb)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, a.width); cap.set(cv2.CAP_PROP_FRAME_HEIGHT, a.height)
        grab = lambda: cap.read()[1]  # noqa: E731
    while True:
        frame = grab()
        if frame is None:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = detector.detectMarkers(gray)
        if ids is not None and a.id in ids.ravel():
            k = list(ids.ravel()).index(a.id)
            img_pts = corners[k].reshape(4, 2).astype(np.float32)
            ok, rvec, tvec = cv2.solvePnP(obj, img_pts, K, D, flags=cv2.SOLVEPNP_IPPE_SQUARE)
            if ok:
                cv2.aruco.drawDetectedMarkers(frame, [corners[k]], ids[k:k + 1])
                cv2.drawFrameAxes(frame, K, D, rvec, tvec, a.size / 2)
                x, y, z = tvec.ravel()
                cv2.putText(frame, f"MARKER x={x:6.1f} y={y:6.1f} z={z:6.1f} mm", (10, 28),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow("aruco_pose_test (ESC to quit)", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
