"""
Week 3 - Filtering, edges & morphology, with live trackbars.

Pipeline: grayscale -> Gaussian blur -> threshold (Otsu/adaptive) ->
morphology (open/close) -> Canny. Tune the sliders to segment an object
cleanly under different lighting.

Usage:
    python 02_filters_edges.py --image path/to/img.jpg
    python 02_filters_edges.py --camera 0        # webcam / USB cam
"""
import argparse
import cv2
import numpy as np


def nothing(_):
    pass


def build_ui():
    cv2.namedWindow("controls", cv2.WINDOW_NORMAL)
    cv2.createTrackbar("blur (odd)", "controls", 3, 31, nothing)
    cv2.createTrackbar("canny lo", "controls", 50, 500, nothing)
    cv2.createTrackbar("canny hi", "controls", 150, 500, nothing)
    cv2.createTrackbar("morph k", "controls", 3, 25, nothing)
    cv2.createTrackbar("adaptive?", "controls", 0, 1, nothing)


def odd(v, lo=1):
    v = max(lo, v)
    return v if v % 2 == 1 else v + 1


def process(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    k = odd(cv2.getTrackbarPos("blur (odd)", "controls"))
    blurred = cv2.GaussianBlur(gray, (k, k), 0)

    if cv2.getTrackbarPos("adaptive?", "controls") == 1:
        th = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 21, 5)
    else:
        _, th = cv2.threshold(blurred, 0, 255,
                              cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    mk = odd(cv2.getTrackbarPos("morph k", "controls"))
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (mk, mk))
    morphed = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel)
    morphed = cv2.morphologyEx(morphed, cv2.MORPH_CLOSE, kernel)

    lo = cv2.getTrackbarPos("canny lo", "controls")
    hi = cv2.getTrackbarPos("canny hi", "controls")
    edges = cv2.Canny(morphed, lo, hi)

    # side-by-side: mask | edges
    return np.hstack([cv2.cvtColor(morphed, cv2.COLOR_GRAY2BGR),
                      cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image")
    ap.add_argument("--camera", type=int)
    args = ap.parse_args()

    build_ui()

    if args.camera is not None:
        cap = cv2.VideoCapture(args.camera)
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            cv2.imshow("mask | edges", process(frame))
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        cap.release()
    else:
        if not args.image:
            raise SystemExit("Provide --image or --camera")
        frame = cv2.imread(args.image)
        while True:
            cv2.imshow("mask | edges", process(frame))
            if cv2.waitKey(50) & 0xFF == ord("q"):
                break
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
