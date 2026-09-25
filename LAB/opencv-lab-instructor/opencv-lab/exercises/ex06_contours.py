"""
Exercise 06 - Finding and drawing contours               (lecture block 06)

Goal:  turn an image into a binary mask, find the outlines of every white
       blob, compare retrieval modes and approximation modes, then run it live.
Run:   python exercises/ex06_contours.py
       python exercises/ex06_contours.py --live            (webcam / video)

Checkpoint: RETR_EXTERNAL finds 11 contours (6 shapes + 5 noise dots).
            RETR_TREE finds 12 (the ring's hole is one more).
            CHAIN_APPROX_SIMPLE stores far fewer points than CHAIN_APPROX_NONE.
"""
# >>> Fill in every TODO below, run the file, and compare with the Checkpoint above. <<<
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if (p / "labutils.py").exists())))
import cv2
from labutils import FONT, close, data, delay_for, frame_limit, open_source, out, show


def to_binary(bgr):
    """gray -> blur -> Otsu threshold. Objects must end up WHITE on black."""
    gray = None  # TODO 1: convert to grayscale
    blur = None  # TODO 2: blur with a 5x5 Gaussian
    _, bw = None, None  # TODO 3: Otsu threshold (T chosen automatically)
    return bw


ap = argparse.ArgumentParser()
ap.add_argument("--live", action="store_true", help="run on the webcam / video instead of shapes.png")
ap.add_argument("--source", default="0")
args = ap.parse_args()

if not args.live:
    img = cv2.imread(data("shapes.png"))
    bw = to_binary(img)
    show("Step 1 - binary", bw)

    # STEP 2 - outer contours only
    contours, hierarchy = None, None  # TODO 4: find outer contours with RETR_EXTERNAL
    print("RETR_EXTERNAL:", len(contours), "contours")

    # STEP 3 - the full tree also returns holes
    tree, hier = cv2.findContours(bw, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    print("RETR_TREE:    ", len(tree), "contours")

    # STEP 4 - how many points are stored?
    dense, _ = cv2.findContours(bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    print("points with CHAIN_APPROX_NONE:  ", sum(len(c) for c in dense))
    print("points with CHAIN_APPROX_SIMPLE:", sum(len(c) for c in contours))

    # STEP 5 - draw them all
    vis = img.copy()
    pass  # TODO 5: draw every contour in green, thickness 2
    cv2.putText(vis, f"{len(contours)} contours", (10, 30), FONT, 0.9, (0, 255, 255), 2)
    cv2.imwrite(out("contours.png"), vis)
    show("Step 5 - contours", vis)
else:
    # STEP 6 - the same pipeline on live video
    cap = open_source(args.source)
    wait, n = delay_for(cap), 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        bw = to_binary(frame)
        contours, _ = cv2.findContours(bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        big = [c for c in contours if cv2.contourArea(c) > 300]
        cv2.drawContours(frame, big, -1, (0, 255, 0), 2)
        cv2.putText(frame, f"{len(big)} objects", (10, 30), FONT, 0.9, (0, 255, 255), 2)
        n += 1
        if show("Step 6 - live contours (q = quit)", frame, wait) == ord("q") or frame_limit(n):
            break
    cap.release()
close()
