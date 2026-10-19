#!/usr/bin/env python3
"""Save calibration images from a webcam: press s to save, ESC to quit (Lab 6J, after Nicolai Nielsen's video).

    python3 get_images.py               # camera 0, saves images/img0.png, img1.png, ...
    python3 get_images.py --device 1 --out images
"""
import argparse
import os

import cv2


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--device", type=int, default=0)
    ap.add_argument("--out", default="images")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    cap = cv2.VideoCapture(a.device)
    num = 0
    while cap.isOpened():
        ok, img = cap.read()
        if not ok:
            break
        k = cv2.waitKey(5) & 0xFF
        if k == 27:          # ESC
            break
        if k == ord("s"):
            cv2.imwrite(os.path.join(a.out, f"img{num}.png"), img)
            print("image saved!", num)
            num += 1
        cv2.imshow("Img (s = save, ESC = quit)", img)
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
