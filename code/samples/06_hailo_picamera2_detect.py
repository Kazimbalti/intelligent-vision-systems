"""
Week 8 - Hailo NPU accelerated detection with picamera2.

Runs a pre-compiled YOLO .hef on the Hailo AI HAT, fed live frames from the Pi
camera, and overlays boxes + an FPS counter. Compare the FPS here against your
Week-5 CPU baseline to compute the NPU speed-up.

Run ON the Raspberry Pi with the Hailo stack installed (hailo-all):
    python 06_hailo_picamera2_detect.py \
        --hef resources/yolov8s.hef \
        --labels resources/coco.txt \
        --conf 0.4

NOTES
-----
* This follows the official picamera2 Hailo example pattern
  (`from picamera2.devices import Hailo`). API details and the exact
  post-processing depend on your HailoRT / picamera2 / model-zoo versions, and
  on how the .hef was compiled (some models output decoded detections, others
  need NMS on-CPU). ALWAYS diff against the current official example before a
  live class:
  https://github.com/raspberrypi/picamera2/tree/main/examples/hailo
  https://github.com/hailo-ai/hailo-apps
* Download a .hef that matches YOUR chip (8 / 8L / 10H) from the Hailo Model Zoo.
"""
import argparse
import time
import cv2
import numpy as np


def load_labels(path):
    with open(path) as f:
        return [ln.strip() for ln in f if ln.strip()]


def extract_detections(hailo_output, w, h, labels, conf):
    """Convert Hailo output to a list of (label, score, x0,y0,x1,y1).

    Assumes a detection model whose output is grouped per-class as
    [[ [ymin,xmin,ymax,xmax,score], ... ] per class ]. Adjust to match your
    compiled model's actual output layout.
    """
    dets = []
    for class_id, class_dets in enumerate(hailo_output):
        for det in class_dets:
            ymin, xmin, ymax, xmax, score = det
            if score < conf:
                continue
            dets.append((
                labels[class_id] if class_id < len(labels) else str(class_id),
                float(score),
                int(xmin * w), int(ymin * h), int(xmax * w), int(ymax * h),
            ))
    return dets


def draw(frame, dets):
    for label, score, x0, y0, x1, y1 in dets:
        cv2.rectangle(frame, (x0, y0), (x1, y1), (0, 255, 0), 2)
        cv2.putText(frame, f"{label} {score:.2f}", (x0, max(0, y0 - 6)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    return frame


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hef", required=True)
    ap.add_argument("--labels", required=True)
    ap.add_argument("--conf", type=float, default=0.4)
    args = ap.parse_args()

    from picamera2 import Picamera2
    from picamera2.devices import Hailo

    labels = load_labels(args.labels)

    with Hailo(args.hef) as hailo:
        model_h, model_w, _ = hailo.get_input_shape()
        print(f"Model input: {model_w}x{model_h}")

        picam2 = Picamera2()
        # 'main' = full-res display stream; 'lores' = model-sized inference stream
        cfg = picam2.create_preview_configuration(
            main={"size": (1280, 720), "format": "RGB888"},
            lores={"size": (model_w, model_h), "format": "RGB888"})
        picam2.configure(cfg)
        picam2.start()
        time.sleep(0.5)

        t0, n, fps = time.time(), 0, 0.0
        try:
            while True:
                disp = picam2.capture_array("main")
                lores = picam2.capture_array("lores")

                results = hailo.run(lores)                  # NPU inference
                dets = extract_detections(
                    results, disp.shape[1], disp.shape[0], labels, args.conf)

                disp = cv2.cvtColor(disp, cv2.COLOR_RGB2BGR)
                draw(disp, dets)

                n += 1
                if n % 10 == 0:
                    fps = 10.0 / (time.time() - t0)
                    t0 = time.time()
                cv2.putText(disp, f"HAILO {fps:5.1f} FPS  dets:{len(dets)}",
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                            (0, 200, 255), 2)
                cv2.imshow("Hailo detection (q to quit)", disp)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
        finally:
            picam2.stop()
            cv2.destroyAllWindows()
        print(f"[Hailo] final FPS ~ {fps:.1f}")


if __name__ == "__main__":
    main()
