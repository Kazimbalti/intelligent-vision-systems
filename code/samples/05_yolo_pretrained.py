"""
Week 7 - Pretrained YOLO (training tier: laptop GPU / Colab, or Pi CPU).

Runs YOLOv8n on an image or webcam, lets you sweep confidence/IoU, optionally
filters to a single class, and logs per-frame inference time so you can contrast
CPU inference with the Hailo NPU in Week 8.

Usage:
    python 05_yolo_pretrained.py --image bus.jpg --conf 0.25
    python 05_yolo_pretrained.py --camera 0 --only person
"""
import argparse
import time
from ultralytics import YOLO


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--weights", default="yolov8n.pt")
    ap.add_argument("--image")
    ap.add_argument("--camera", type=int)
    ap.add_argument("--conf", type=float, default=0.25)
    ap.add_argument("--iou", type=float, default=0.45)
    ap.add_argument("--only", help="class name to keep, e.g. 'person'")
    args = ap.parse_args()

    model = YOLO(args.weights)
    names = model.names
    keep = None
    if args.only:
        keep = [i for i, n in names.items() if n == args.only]
        if not keep:
            raise SystemExit(f"'{args.only}' not in model classes")

    src = args.image if args.image else args.camera
    if src is None:
        raise SystemExit("Provide --image or --camera")

    stream = args.camera is not None
    results = model.predict(source=src, conf=args.conf, iou=args.iou,
                            classes=keep, stream=stream, show=stream, verbose=False)

    if stream:
        t0, n = time.time(), 0
        for r in results:                       # generator, one per frame
            n += 1
            if n % 30 == 0:
                dt = (time.time() - t0) / 30
                print(f"~{1/dt:5.1f} FPS  ({dt*1000:.1f} ms/frame)")
                t0 = time.time()
    else:
        r = results[0]
        print(f"Detections: {len(r.boxes)}  "
              f"inference: {r.speed['inference']:.1f} ms")
        r.save(filename="yolo_out.jpg")
        print("Saved yolo_out.jpg")


if __name__ == "__main__":
    main()
