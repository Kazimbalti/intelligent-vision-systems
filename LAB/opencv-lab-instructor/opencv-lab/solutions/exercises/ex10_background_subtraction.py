"""
Exercise 10 - Background subtraction                     (lecture block 10)

Goal:  detect moving objects with MOG2, clean the mask, box every object,
       and compare with simple frame differencing.
Run:   python exercises/ex10_background_subtraction.py                 (data/traffic.mp4)
       python exercises/ex10_background_subtraction.py --source 0      (webcam)
Keys:  q = quit

Checkpoint: after about one second the cars and the pedestrian get red boxes.
            Shadows appear grey (127) in the raw MOG2 mask and vanish after the threshold.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if (p / "labutils.py").exists())))
import cv2
import numpy as np
from labutils import FONT, ROOT, close, delay_for, frame_limit, grid, open_source, out, show

ap = argparse.ArgumentParser()
ap.add_argument("--source", default="data/traffic.mp4")
ap.add_argument("--min-area", type=int, default=400)
args = ap.parse_args()
src = args.source
if not src.isdigit() and not Path(src).exists():
    src = str(ROOT / src)        # lets you run the script from any folder
cap = open_source(src)

# STEP 1 - the background model
bg = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=16, detectShadows=True)
kernel = np.ones((3, 3), np.uint8)
prev = None
wait, n = delay_for(cap), 0

while True:
    ok, frame = cap.read()
    if not ok:
        break

    # STEP 2 - foreground mask: 255 = moving, 127 = shadow, 0 = background
    raw = bg.apply(frame)
    _, fg = cv2.threshold(raw, 200, 255, cv2.THRESH_BINARY)
    fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, kernel)

    # STEP 3 - for comparison: plain frame differencing
    gray = cv2.GaussianBlur(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), (5, 5), 0)
    prev = gray if prev is None else prev
    _, diff = cv2.threshold(cv2.absdiff(gray, prev), 25, 255, cv2.THRESH_BINARY)
    prev = gray

    # STEP 4 - box every moving object that is big enough
    contours, _ = cv2.findContours(fg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    count = 0
    for c in contours:
        if cv2.contourArea(c) < args.min_area:
            continue
        x, y, w, h = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
        count += 1
    cv2.putText(frame, f"moving objects: {count}", (10, 30), FONT, 0.8, (0, 255, 255), 2)

    panel = grid([frame, raw, fg, diff], ["frame", "MOG2 raw (grey = shadow)", "cleaned mask", "frame difference"], cols=2, scale=0.75)
    n += 1
    if show("Background subtraction (q = quit)", panel, wait) == ord("q") or frame_limit(n):
        break

cv2.imwrite(out("bgsub_last.png"), panel)
cap.release()
close()
