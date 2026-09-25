"""
Exercise 02 - Video files and the live camera           (lecture block 02)

Goal:  open a camera (or a video file), read frames in a loop, show them,
       and record them to output/recording.mp4.
Run:   python exercises/ex02_video.py                  (webcam, falls back to data/traffic.mp4)
       python exercises/ex02_video.py --source data/traffic.mp4
Keys:  q = quit

Checkpoint: the window shows the colour and grayscale video side by side,
            and output/recording.mp4 plays in any video player.
"""
# >>> Fill in every TODO below, run the file, and compare with the Checkpoint above. <<<
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if (p / "labutils.py").exists())))
import cv2
import numpy as np
from labutils import FONT, close, delay_for, frame_limit, open_source, out, show

ap = argparse.ArgumentParser()
ap.add_argument("--source", default="0", help="0 = webcam, or the path of a video file")
args = ap.parse_args()

# STEP 1 - open the source and read its properties
cap = open_source(args.source)
w = None  # TODO 1: read the frame width with cap.get(cv2.CAP_PROP_FRAME_WIDTH)
h = None  # TODO 2: read the frame height with cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
fps = cap.get(cv2.CAP_PROP_FPS) or 30
print(f"size = {w} x {h}, fps = {fps:.1f}")

# STEP 2 - create a VideoWriter. The size is (width, height), NOT img.shape!
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
writer = None  # TODO 3: create cv2.VideoWriter(path, fourcc, fps, (w, h))

# STEP 3 - the loop: read, process, write, show, wait
n = 0
wait = delay_for(cap)
while True:
    ok, frame = None, None  # TODO 4: read one frame with cap.read()
    if not ok:
        break
    pass  # TODO 5: write the frame to the file
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.putText(frame, f"frame {n}", (10, 30), FONT, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
    both = np.hstack([frame, cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)])
    key = show("Step 3 - colour | gray   (q = quit)", both, wait)
    n += 1
    if key == ord("q") or frame_limit(n):
        break

# STEP 4 - always release the camera and the file
pass  # TODO 6: release the capture
writer.release()
close()
print(f"{n} frames written to output/recording.mp4")
