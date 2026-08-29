"""
Week 10 - Ingest the ESP32-CAM MJPEG stream on the Raspberry Pi.

The ESP32-CAM CameraWebServer example exposes an MJPEG stream, typically at
    http://<ESP32_IP>:81/stream
This reads that stream with OpenCV so it can be fed into any CPU or Hailo
detector (treat the ESP32-CAM as a networked camera node).

Usage:
    python 08_esp32cam_stream_ingest.py --url http://192.168.1.50:81/stream

Then, to run detection on the ESP32 feed, pipe frames into your Week-8 Hailo
detector (see the hook at the bottom).
"""
import argparse
import time
import cv2


def open_stream(url, retries=5):
    for i in range(retries):
        cap = cv2.VideoCapture(url)
        if cap.isOpened():
            return cap
        print(f"retry {i+1}/{retries} opening {url} ...")
        time.sleep(1.0)
    raise SystemExit(f"Could not open {url}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True, help="http://<ip>:81/stream")
    args = ap.parse_args()

    cap = open_stream(args.url)
    t0, n, fps = time.time(), 0, 0.0
    while True:
        ok, frame = cap.read()
        if not ok:
            print("stream hiccup, reopening...")
            cap.release()
            cap = open_stream(args.url)
            continue

        # ---- optional: run detection here ----
        # from your Week-8 module you could call hailo.run(frame) and draw boxes.
        # frame = detect_and_draw(frame)

        n += 1
        if n % 10 == 0:
            fps = 10.0 / (time.time() - t0)
            t0 = time.time()
        cv2.putText(frame, f"ESP32-CAM {fps:5.1f} FPS", (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow("ESP32-CAM (q to quit)", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
