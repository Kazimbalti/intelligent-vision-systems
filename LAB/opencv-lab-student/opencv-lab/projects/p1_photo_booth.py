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
# >>> Fill in every TODO below, run the file, and compare with the Checkpoint above. <<<
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if (p / "labutils.py").exists())))
import cv2
from labutils import FONT, HEADLESS, close, delay_for, frame_limit, open_source, out, show


def overlay(frame, n, gray_mode):
    """Draw the timestamp, the frame counter and the mode on the frame."""
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pass  # TODO 1: draw a black bar across the top
    pass  # TODO 2: write the timestamp in the bar
    cv2.putText(frame, f"#{n}  {'GRAY' if gray_mode else 'COLOUR'}", (frame.shape[1] - 230, 28), FONT, 0.7, (0, 255, 255), 2)
    return frame


def save_snapshot(frame):
    """Save the frame with a timestamped file name and return the name."""
    name = f"snap_{datetime.now():%Y%m%d_%H%M%S}.png"
    pass  # TODO 3: write the frame to output/<name>
    print("saved", name)
    return name


cap = open_source("0")
wait, n, gray_mode = delay_for(cap), 0, False
while True:
    ok, frame = cap.read()
    if not ok:
        break
    if gray_mode:
        frame = None  # TODO 4: convert to gray and back to 3 channels
    frame = overlay(frame, n, gray_mode)
    key = show("Photo booth  (s = save, g = gray, q = quit)", frame, wait)
    n += 1
    if key == ord("s") or (HEADLESS and n == 10):
        save_snapshot(frame)
    elif key == ord("g"):
        gray_mode = None  # TODO 5: toggle grayscale mode
    elif key == ord("q") or frame_limit(n):
        break
cap.release()
close()
