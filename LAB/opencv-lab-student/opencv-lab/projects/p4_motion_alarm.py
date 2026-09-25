"""
Project 4 - Motion alarm                                 (blocks 02, 09, 10)

Watch a camera; when motion lasts for a few frames, start recording to
output/alarm_<time>.mp4; stop after 1 second without motion.
Run:   python projects/p4_motion_alarm.py                        (data/traffic.mp4)
       python projects/p4_motion_alarm.py --source 0             (webcam: wave at it)

Done when: 'REC' appears while something moves and one or more alarm_*.mp4
           files are written to output/.
"""
# >>> Fill in every TODO below, run the file, and compare with the Checkpoint above. <<<
import argparse
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if (p / "labutils.py").exists())))
import cv2
import numpy as np
from labutils import FONT, ROOT, close, delay_for, frame_limit, open_source, out, show

ap = argparse.ArgumentParser()
ap.add_argument("--source", default="data/traffic.mp4")
ap.add_argument("--min-area", type=int, default=1500, help="moving pixels needed to count as motion")
ap.add_argument("--start-after", type=int, default=5, help="frames of motion before recording starts")
ap.add_argument("--stop-after", type=int, default=30, help="frames without motion before recording stops")
args = ap.parse_args()
src = args.source
if not src.isdigit() and not Path(src).exists():
    src = str(ROOT / src)

cap = open_source(src)
fps = cap.get(cv2.CAP_PROP_FPS) or 30
bg = cv2.createBackgroundSubtractorMOG2(history=300, varThreshold=25, detectShadows=True)
kernel = np.ones((3, 3), np.uint8)
writer, moving_frames, still_frames, clips = None, 0, 0, 0
wait, n = delay_for(cap), 0

while True:
    ok, frame = cap.read()
    if not ok:
        break
    fg = bg.apply(frame)
    _, fg = cv2.threshold(fg, 200, 255, cv2.THRESH_BINARY)
    fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, kernel)
    motion = None  # TODO 1: motion = more than min-area white pixels in the mask

    # state machine: IDLE -> RECORDING -> IDLE
    moving_frames = moving_frames + 1 if motion else 0
    still_frames = 0 if motion else still_frames + 1
    if writer is None and moving_frames >= args.start_after and n > fps:   # skip the first second while MOG2 learns
        name = f"alarm_{datetime.now():%H%M%S}_{clips}.mp4"
        h, w = frame.shape[:2]
        writer = None  # TODO 2: open a VideoWriter for the clip
        clips += 1
        print("recording", name)
    if writer is not None and still_frames >= args.stop_after:
        pass  # TODO 3: close the clip
        writer = None
        print("stopped")

    if writer is not None:
        writer.write(frame)
        cv2.circle(frame, (25, 25), 10, (0, 0, 255), -1)
        cv2.putText(frame, "REC", (42, 33), FONT, 0.8, (0, 0, 255), 2)
    cv2.putText(frame, f"moving px: {cv2.countNonZero(fg)}", (10, frame.shape[0] - 12), FONT, 0.6, (255, 255, 255), 1)
    n += 1
    if show("Motion alarm (q = quit)", frame, wait) == ord("q") or frame_limit(n):
        break

if writer is not None:
    writer.release()
print(f"{clips} clip(s) saved in output/")
cap.release()
close()
