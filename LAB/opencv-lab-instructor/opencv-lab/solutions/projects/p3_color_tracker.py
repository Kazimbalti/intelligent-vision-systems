"""
Project 3 - Colour tracker                               (blocks 02, 03, 05, 06, 07, 08)

Track a coloured ball live: box it, mark its centre, draw its trail, and
print how far it is from the image centre (the "steering error" a drone
controller would use).
Run:   python projects/p3_color_tracker.py                         (data/ball.mp4)
       python projects/p3_color_tracker.py --source 0              (webcam)
       python projects/p3_color_tracker.py --lower 5 120 80 --upper 20 255 255   (an orange ball)
Tip:   find your ball's range with  python tools/hsv_tuner.py --source 0

Done when: the box and trail follow the green ball and ignore the red, blue
           and yellow objects.
"""
import argparse
import sys
from collections import deque
from pathlib import Path

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if (p / "labutils.py").exists())))
import cv2
import numpy as np
from labutils import FONT, ROOT, close, delay_for, frame_limit, grid, open_source, out, show

ap = argparse.ArgumentParser()
ap.add_argument("--source", default="data/ball.mp4")
ap.add_argument("--lower", type=int, nargs=3, default=[40, 80, 50], help="H S V lower bound")
ap.add_argument("--upper", type=int, nargs=3, default=[80, 255, 255], help="H S V upper bound")
ap.add_argument("--min-area", type=int, default=300)
args = ap.parse_args()
src = args.source
if not src.isdigit() and not Path(src).exists():
    src = str(ROOT / src)

cap = open_source(src, fallback="ball.mp4")
trail = deque(maxlen=64)
kernel = np.ones((5, 5), np.uint8)
wait, n = delay_for(cap), 0


def find_ball(frame):
    """Return (cx, cy, x, y, w, h) of the biggest blob in the colour range, and the mask."""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, tuple(args.lower), tuple(args.upper))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None, mask
    c = max(contours, key=cv2.contourArea)
    if cv2.contourArea(c) < args.min_area:
        return None, mask
    M = cv2.moments(c)
    cx, cy = int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])
    return (cx, cy, *cv2.boundingRect(c)), mask


while True:
    ok, frame = cap.read()
    if not ok:
        break
    h_img, w_img = frame.shape[:2]
    found, mask = find_ball(frame)
    if found:
        cx, cy, x, y, w, h = found
        trail.appendleft((cx, cy))
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv2.circle(frame, (cx, cy), 5, (255, 255, 255), -1)
        dx, dy = cx - w_img // 2, cy - h_img // 2
        cv2.line(frame, (w_img // 2, h_img // 2), (cx, cy), (0, 255, 255), 1)
        cv2.putText(frame, f"error dx={dx:+d} dy={dy:+d}", (10, 30), FONT, 0.7, (0, 255, 255), 2)
    else:
        trail.appendleft(None)
    for i in range(1, len(trail)):                         # fading trail
        if trail[i - 1] is None or trail[i] is None:
            continue
        cv2.line(frame, trail[i - 1], trail[i], (0, 255, 0), max(1, 6 - i // 12))
    cv2.drawMarker(frame, (w_img // 2, h_img // 2), (200, 200, 200), cv2.MARKER_CROSS, 20, 1)
    panel = grid([frame, mask], ["tracker", "mask"])
    n += 1
    if show("Colour tracker (q = quit)", panel, wait) == ord("q") or frame_limit(n):
        break
cv2.imwrite(out("tracker_last.png"), panel)
cap.release()
close()
