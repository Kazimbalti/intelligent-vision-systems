"""
Week 2 - OpenCV fundamentals.

Loads an image, converts between colour spaces, crops an ROI, annotates it,
adjusts brightness/contrast safely, and writes a 2x2 montage to disk.

Usage:
    python 01_opencv_basics.py --image path/to/img.jpg --out montage.jpg
"""
import argparse
import cv2
import numpy as np


def adjust_brightness_contrast(img, alpha=1.2, beta=20):
    """alpha = contrast gain, beta = brightness offset. Safe (saturating)."""
    return cv2.convertScaleAbs(img, alpha=alpha, beta=beta)


def label_box(img, x, y, w, h, text):
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.putText(img, text, (x, max(0, y - 8)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    return img


def to_3ch(gray):
    """Stack a single-channel image to 3 channels so it montages cleanly."""
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    ap.add_argument("--out", default="montage.jpg")
    args = ap.parse_args()

    img = cv2.imread(args.image)            # NOTE: OpenCV loads as BGR, not RGB
    if img is None:
        raise SystemExit(f"Could not read {args.image}")

    h, w = img.shape[:2]
    print(f"Loaded {w}x{h}, dtype={img.dtype}, channels={img.shape[2]}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Annotate a centre ROI on a brightened copy
    annotated = adjust_brightness_contrast(img.copy(), alpha=1.15, beta=15)
    rw, rh = w // 3, h // 3
    annotated = label_box(annotated, w // 3, h // 3, rw, rh, "ROI")

    # Build a 2x2 montage: original | gray | hsv | annotated
    top = np.hstack([img, to_3ch(gray)])
    bot = np.hstack([hsv, annotated])
    montage = np.vstack([top, bot])

    cv2.imwrite(args.out, montage)
    print(f"Wrote {args.out}")

    # Show if a display is available (skip on headless Pi)
    try:
        cv2.imshow("montage (press any key)", montage)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    except cv2.error:
        pass


if __name__ == "__main__":
    main()
