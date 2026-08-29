"""
Week 5 - Real-time capture with picamera2 (Raspberry Pi camera stack).

Streams from a Pi camera, overlays a live FPS counter, and applies one
Week-3 operation (Canny) per frame. Prints an average-FPS summary so you can
build the resolution-vs-FPS table used as the CPU baseline in Week 8.

Run ON the Raspberry Pi:
    python 04_picamera2_stream.py --width 1280 --height 720
    python 04_picamera2_stream.py --width 640  --height 480 --no-edges

Falls back to a USB/webcam via OpenCV if picamera2 is unavailable.
"""
import argparse
import time
import cv2
import numpy as np


def run_picamera2(w, h, do_edges):
    from picamera2 import Picamera2
    picam2 = Picamera2()
    cfg = picam2.create_preview_configuration(
        main={"size": (w, h), "format": "RGB888"})
    picam2.configure(cfg)
    picam2.start()
    time.sleep(0.5)

    t0, n, fps = time.time(), 0, 0.0
    try:
        while True:
            frame = picam2.capture_array()          # RGB888
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            if do_edges:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                edges = cv2.Canny(gray, 80, 160)
                frame = cv2.addWeighted(
                    frame, 0.7, cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR), 0.3, 0)

            n += 1
            if n % 10 == 0:
                fps = 10.0 / (time.time() - t0)
                t0 = time.time()
            cv2.putText(frame, f"{w}x{h}  {fps:5.1f} FPS", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.imshow("picamera2 (q to quit)", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        picam2.stop()
        cv2.destroyAllWindows()
    print(f"[picamera2] {w}x{h} last FPS ~ {fps:.1f}")


def run_opencv(w, h, do_edges, index=0):
    cap = cv2.VideoCapture(index)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
    t0, n, fps = time.time(), 0, 0.0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if do_edges:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 80, 160)
            frame = cv2.addWeighted(
                frame, 0.7, cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR), 0.3, 0)
        n += 1
        if n % 10 == 0:
            fps = 10.0 / (time.time() - t0)
            t0 = time.time()
        cv2.putText(frame, f"{fps:5.1f} FPS", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.imshow("webcam (q to quit)", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cap.release()
    cv2.destroyAllWindows()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--height", type=int, default=720)
    ap.add_argument("--no-edges", action="store_true")
    args = ap.parse_args()
    do_edges = not args.no_edges
    try:
        run_picamera2(args.width, args.height, do_edges)
    except Exception as e:
        print(f"picamera2 unavailable ({e}); falling back to OpenCV webcam.")
        run_opencv(args.width, args.height, do_edges)


if __name__ == "__main__":
    main()
