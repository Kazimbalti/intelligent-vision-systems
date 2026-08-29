"""
Week 12 - Capstone pipeline skeleton.

A clean scaffold for an integrated edge vision system:
    SOURCE  ->  INFERENCE  ->  TRACK/LOGIC  ->  OUTPUT

Fill in the four stages for your chosen brief (smart camera, multi-camera node,
perception-for-robotics, or object counter). The skeleton runs as-is with a
webcam and a null detector so you can build incrementally.

Usage:
    python capstone_skeleton.py --source 0
    python capstone_skeleton.py --source http://<esp32-ip>:81/stream
"""
import argparse
import time
import cv2


# ---------------------------------------------------------------- SOURCE ----
def open_source(src):
    # int-like -> local camera index; else treat as URL / file path
    try:
        src = int(src)
    except ValueError:
        pass
    cap = cv2.VideoCapture(src)
    if not cap.isOpened():
        raise SystemExit(f"Cannot open source {src}")
    return cap


# ------------------------------------------------------------- INFERENCE ----
class Detector:
    """Swap this for your Week-8 Hailo detector or Week-7 YOLO detector."""
    def __init__(self):
        pass

    def infer(self, frame):
        # return list of (label, score, x0, y0, x1, y1)
        return []


# ------------------------------------------------------------ TRACK/LOGIC ---
class LineCrossCounter:
    """Minimal example logic: count detections whose centre crosses a line."""
    def __init__(self, line_y):
        self.line_y = line_y
        self.count = 0
        self.prev_centers = []

    def update(self, dets):
        centers = [((x0 + x1) // 2, (y0 + y1) // 2) for _, _, x0, y0, x1, y1 in dets]
        for (cx, cy) in centers:
            for (px, py) in self.prev_centers:
                if abs(px - cx) < 40 and (py < self.line_y <= cy):
                    self.count += 1
        self.prev_centers = centers
        return self.count


# ---------------------------------------------------------------- OUTPUT ----
def draw_overlay(frame, dets, line_y, count, fps):
    cv2.line(frame, (0, line_y), (frame.shape[1], line_y), (255, 0, 0), 2)
    for label, score, x0, y0, x1, y1 in dets:
        cv2.rectangle(frame, (x0, y0), (x1, y1), (0, 255, 0), 2)
        cv2.putText(frame, f"{label} {score:.2f}", (x0, max(0, y0 - 6)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    cv2.putText(frame, f"count:{count}  {fps:4.1f} FPS", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    return frame


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default="0")
    args = ap.parse_args()

    cap = open_source(args.source)
    detector = Detector()
    counter = None

    t0, n, fps = time.time(), 0, 0.0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if counter is None:
            counter = LineCrossCounter(line_y=frame.shape[0] // 2)

        dets = detector.infer(frame)          # <-- plug in your model
        count = counter.update(dets)          # <-- plug in your logic

        n += 1
        if n % 10 == 0:
            fps = 10.0 / (time.time() - t0)
            t0 = time.time()

        frame = draw_overlay(frame, dets, counter.line_y, count, fps)
        cv2.imshow("capstone (q to quit)", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    # OUTPUT stage extension ideas: log events to CSV, POST to a server,
    # publish a ROS 2 topic, or send steering commands to a rover/gimbal.


if __name__ == "__main__":
    main()
