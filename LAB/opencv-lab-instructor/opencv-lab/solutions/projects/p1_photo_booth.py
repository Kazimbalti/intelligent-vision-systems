"""
Project 1 - Photo booth                                  (blocks 01, 02, 03)

Build a live camera app:
  * show the camera with the current date/time and a frame counter drawn on it
  * press  s  to save a snapshot to output/snap_YYYYMMDD_HHMMSS.png
  * press  g  to toggle grayscale
  * press  q  to quit
Run:   python projects/p1_photo_booth.py              (webcam, falls back to a video)

Done when: snapshots appear in output/ with the timestamp visible in the image.
"""
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if (p / "labutils.py").exists())))
import cv2
from labutils import FONT, HEADLESS, close, delay_for, frame_limit, open_source, out, show


def overlay(frame, n, gray_mode):
    """Draw the timestamp, the frame counter and the mode on the frame."""
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cv2.rectangle(frame, (0, 0), (frame.shape[1], 40), (0, 0, 0), -1)
    cv2.putText(frame, stamp, (10, 28), FONT, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, f"#{n}  {'GRAY' if gray_mode else 'COLOUR'}", (frame.shape[1] - 230, 28), FONT, 0.7, (0, 255, 255), 2)
    return frame


def save_snapshot(frame):
    """Save the frame with a timestamped file name and return the name."""
    name = f"snap_{datetime.now():%Y%m%d_%H%M%S}.png"
    cv2.imwrite(out(name), frame)
    print("saved", name)
    return name


cap = open_source("0")
wait, n, gray_mode = delay_for(cap), 0, False
while True:
    ok, frame = cap.read()
    if not ok:
        break
    if gray_mode:
        frame = cv2.cvtColor(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)
    frame = overlay(frame, n, gray_mode)
    key = show("Photo booth  (s = save, g = gray, q = quit)", frame, wait)
    n += 1
    if key == ord("s") or (HEADLESS and n == 10):
        save_snapshot(frame)
    elif key == ord("g"):
        gray_mode = not gray_mode
    elif key == ord("q") or frame_limit(n):
        break
cap.release()
close()
