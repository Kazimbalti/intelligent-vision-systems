"""
Lecture 10 - MediaPipe hand tracking -> a gesture controller.

Tracks one hand and maps the thumb-tip <-> index-tip distance to a 0-100 value
(a "virtual dial"). This is the pattern behind gesture-controlled volume, LED
brightness, or a drone parameter. CPU-friendly, no GPU needed.

Install: pip install mediapipe opencv-python
Usage:   python 10_mediapipe_gesture.py --camera 0
"""
import argparse
import math
import cv2
import mediapipe as mp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--camera", type=int, default=0)
    args = ap.parse_args()

    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.6,
                           min_tracking_confidence=0.6)

    cap = cv2.VideoCapture(args.camera)
    # calibrate these to your camera distance (pixels between the two tips)
    d_min, d_max = 20.0, 200.0

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        res = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        value = None
        if res.multi_hand_landmarks:
            lm = res.multi_hand_landmarks[0]
            mp_draw.draw_landmarks(frame, lm, mp_hands.HAND_CONNECTIONS)
            # landmark 4 = thumb tip, 8 = index tip
            tx, ty = lm.landmark[4].x * w, lm.landmark[4].y * h
            ix, iy = lm.landmark[8].x * w, lm.landmark[8].y * h
            dist = math.hypot(ix - tx, iy - ty)
            value = int(max(0, min(100, (dist - d_min) / (d_max - d_min) * 100)))

            cv2.circle(frame, (int(tx), int(ty)), 8, (255, 0, 255), -1)
            cv2.circle(frame, (int(ix), int(iy)), 8, (255, 0, 255), -1)
            cv2.line(frame, (int(tx), int(ty)), (int(ix), int(iy)), (255, 0, 255), 2)

        # draw the "dial" value bar
        bar = int((value or 0) / 100 * 300)
        cv2.rectangle(frame, (10, 60), (10 + bar, 90), (0, 255, 0), -1)
        cv2.putText(frame, f"value: {value if value is not None else '--'}",
                    (10, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.imshow("gesture dial (q to quit)", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
