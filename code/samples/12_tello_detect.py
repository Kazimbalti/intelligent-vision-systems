"""
Lecture 13/14 - Tello drone: live detection + a minimal perception->action hook.

Streams video from a DJI Tello, runs YOLO detection, and computes a yaw/throttle
correction to keep a chosen target centred (perception -> action). By default it
only PRINTS the commands; pass --fly to actually send rc controls (do this only
in a safe, netted space with a spotter).

Install: pip install djitellopy ultralytics opencv-python
Usage:
    python 12_tello_detect.py --only person            # print-only, safe
    python 12_tello_detect.py --only person --fly       # sends rc commands!
"""
import argparse
import cv2
from djitellopy import Tello
from ultralytics import YOLO


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--weights", default="yolo26n.pt")
    ap.add_argument("--only", default="person")
    ap.add_argument("--conf", type=float, default=0.4)
    ap.add_argument("--fly", action="store_true", help="actually send rc commands")
    args = ap.parse_args()

    model = YOLO(args.weights)
    keep = [i for i, n in model.names.items() if n == args.only] or None

    tello = Tello()
    tello.connect()
    print(f"Battery: {tello.get_battery()}%")
    tello.streamon()
    frame_read = tello.get_frame_read()

    if args.fly:
        tello.takeoff()

    try:
        while True:
            frame = frame_read.frame
            if frame is None:
                continue
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            h, w = frame.shape[:2]
            cx_img = w // 2

            r = model.predict(frame, conf=args.conf, classes=keep, verbose=False)[0]

            yaw = 0
            if len(r.boxes):
                # pick the largest detection as the target
                boxes = r.boxes.xyxy.cpu().numpy()
                areas = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
                x0, y0, x1, y1 = boxes[areas.argmax()]
                tcx = int((x0 + x1) / 2)
                err = tcx - cx_img
                # proportional yaw control (deadband to avoid jitter)
                yaw = int(0.15 * err) if abs(err) > 40 else 0
                cv2.rectangle(frame, (int(x0), int(y0)), (int(x1), int(y1)),
                              (0, 255, 0), 2)
                cv2.line(frame, (cx_img, 0), (cx_img, h), (255, 0, 0), 1)

            cv2.putText(frame, f"yaw cmd: {yaw}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            if args.fly:
                # left_right, forward_back, up_down, yaw
                tello.send_rc_control(0, 0, 0, yaw)
            else:
                print(f"[print-only] yaw={yaw}")

            cv2.imshow("Tello detect (q to quit)", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        if args.fly:
            tello.send_rc_control(0, 0, 0, 0)
            tello.land()
        tello.streamoff()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
