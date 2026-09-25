"""
tools/hsv_tuner.py - find the HSV range of any colour with sliders.

Run:   python tools/hsv_tuner.py data/balls.png      (an image)
       python tools/hsv_tuner.py --source 0          (your webcam)
Keys:  p = print the current range     q = quit

Move the sliders until ONLY your object is white in the mask, then press p
and copy the printed --lower / --upper values into projects/p3_color_tracker.py.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if (p / "labutils.py").exists())))
import cv2
from labutils import grid, open_source

ap = argparse.ArgumentParser()
ap.add_argument("image", nargs="?", default=None)
ap.add_argument("--source", default=None, help="camera index or video file")
args = ap.parse_args()

WIN = "HSV tuner (p = print, q = quit)"
cv2.namedWindow(WIN)
for name, value, top in [("H low", 40, 179), ("H high", 80, 179), ("S low", 80, 255),
                         ("S high", 255, 255), ("V low", 50, 255), ("V high", 255, 255)]:
    cv2.createTrackbar(name, WIN, value, top, lambda v: None)

cap = open_source(args.source, fallback="ball.mp4") if args.source else None
still = None if cap else cv2.imread(args.image or str(Path(__file__).resolve().parents[1] / "data" / "balls.png"))

while True:
    if cap:
        ok, frame = cap.read()
        if not ok:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue
    else:
        frame = still.copy()
    lo = tuple(cv2.getTrackbarPos(n, WIN) for n in ("H low", "S low", "V low"))
    hi = tuple(cv2.getTrackbarPos(n, WIN) for n in ("H high", "S high", "V high"))
    mask = cv2.inRange(cv2.cvtColor(frame, cv2.COLOR_BGR2HSV), lo, hi)
    kept = cv2.bitwise_and(frame, frame, mask=mask)
    cv2.imshow(WIN, grid([frame, mask, kept], ["image", "mask", "kept"], scale=0.6))
    key = cv2.waitKey(30) & 0xFF
    if key == ord("p"):
        print(f"--lower {lo[0]} {lo[1]} {lo[2]} --upper {hi[0]} {hi[1]} {hi[2]}")
    elif key == ord("q"):
        break
if cap:
    cap.release()
cv2.destroyAllWindows()
