"""
Lecture 9 - Multi-object tracking + line-crossing counting (+ rough speed).

Uses Ultralytics' built-in tracker (ByteTrack/BoT-SORT) so each object keeps a
stable ID across frames, then counts IDs whose centre crosses a horizontal line
and estimates a rough speed in px/s. Runs on CPU (slow) or Hailo-exported models
on the Pi; best on the training machine for the workshop.

Usage:
    python 09_tracking_counting.py --source 0
    python 09_tracking_counting.py --source traffic.mp4 --line 0.5 --only car
"""
import argparse
import time
import cv2
from ultralytics import YOLO


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--weights", default="yolo26n.pt")   # or yolo11n.pt / yolov8n.pt
    ap.add_argument("--source", default="0")
    ap.add_argument("--line", type=float, default=0.5, help="line y as frac of H")
    ap.add_argument("--only", help="class name to keep, e.g. 'car'")
    ap.add_argument("--conf", type=float, default=0.3)
    args = ap.parse_args()

    model = YOLO(args.weights)
    keep = None
    if args.only:
        keep = [i for i, n in model.names.items() if n == args.only] or None

    src = int(args.source) if args.source.isdigit() else args.source

    counted, last_cy, last_t = set(), {}, {}
    count_in = count_out = 0
    line_y = None

    # stream=True -> generator of per-frame Results; persist keeps track IDs
    for r in model.track(source=src, conf=args.conf, classes=keep,
                         tracker="bytetrack.yaml", persist=True,
                         stream=True, verbose=False):
        frame = r.orig_img
        h, w = frame.shape[:2]
        if line_y is None:
            line_y = int(args.line * h)

        now = time.time()
        if r.boxes is not None and r.boxes.id is not None:
            ids = r.boxes.id.int().tolist()
            xyxy = r.boxes.xyxy.cpu().numpy()
            for tid, (x0, y0, x1, y1) in zip(ids, xyxy):
                cx, cy = int((x0 + x1) / 2), int((y0 + y1) / 2)

                # speed (px/s) from centre displacement
                spd = 0.0
                if tid in last_cy and tid in last_t and now > last_t[tid]:
                    spd = abs(cy - last_cy[tid]) / (now - last_t[tid])

                # count on line crossing (direction from previous centre)
                if tid in last_cy and tid not in counted:
                    prev = last_cy[tid]
                    if prev < line_y <= cy:
                        count_in += 1; counted.add(tid)
                    elif prev > line_y >= cy:
                        count_out += 1; counted.add(tid)

                last_cy[tid], last_t[tid] = cy, now

                cv2.rectangle(frame, (int(x0), int(y0)), (int(x1), int(y1)),
                              (0, 255, 0), 2)
                cv2.putText(frame, f"id{tid} {spd:.0f}px/s", (int(x0), int(y0) - 6),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        cv2.line(frame, (0, line_y), (w, line_y), (255, 0, 0), 2)
        cv2.putText(frame, f"IN:{count_in}  OUT:{count_out}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
        cv2.imshow("tracking + counting (q to quit)", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
