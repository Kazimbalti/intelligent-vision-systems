"""
labutils.py - small helpers shared by every exercise in the OpenCV lab.

You do not need to edit this file. It gives you:
    data(name)        full path of a file in the data/ folder
    out(name)         full path of a file in the output/ folder
    show(title, img)  cv2.imshow + cv2.waitKey in one call (returns the key)
    open_source(src)  open a webcam ("0") or a video file, with a safe fallback
    grid(images)      put several images side by side, with labels
    frame_limit(n)    lets the automatic tests stop long video loops

Headless mode: if the environment variable LAB_HEADLESS=1 is set, show()
saves images into output/ instead of opening windows. This is useful on
computers without a display (servers, some cloud notebooks).
"""
import os
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)

HEADLESS = os.environ.get("LAB_HEADLESS") == "1"
MAX_FRAMES = int(os.environ.get("LAB_MAX_FRAMES", "0"))
FONT = cv2.FONT_HERSHEY_SIMPLEX


def data(name):
    """Return the full path of a sample file, with a helpful error if it is missing."""
    path = DATA / name
    if not path.exists():
        raise FileNotFoundError(f"{path} not found. Run:  python make_samples.py")
    return str(path)


def out(name):
    """Return the full path of a file in the output/ folder."""
    return str(OUT / name)


def _safe(title):
    return "".join(ch if ch.isalnum() else "_" for ch in title).strip("_")


def show(title, img, wait=0):
    """Show an image and wait. wait=0 waits for a key; wait=1 is for video loops.

    Returns the key that was pressed (or -1 / 255 when nothing was pressed).
    """
    if HEADLESS:
        cv2.imwrite(out(f"{_safe(title)}.png"), img)
        return -1
    cv2.imshow(title, img)
    return cv2.waitKey(wait) & 0xFF


def close():
    """Close every OpenCV window."""
    if not HEADLESS:
        cv2.destroyAllWindows()


def open_source(src="0", fallback="traffic.mp4"):
    """Open a camera index ("0", "1", ...) or a video file.

    If the camera cannot be opened (no webcam, permission denied, headless
    mode) the sample video data/<fallback> is used instead, so every
    exercise still works on any computer.
    """
    src = str(src)
    if src.isdigit() and not HEADLESS:
        cap = cv2.VideoCapture(int(src))
        if cap.isOpened():
            print(f"Opened camera {src}")
            return cap
        print(f"Camera {src} could not be opened, using data/{fallback} instead")
        src = data(fallback)
    elif src.isdigit():
        src = data(fallback)
    cap = cv2.VideoCapture(src)
    if not cap.isOpened():
        raise IOError(f"Could not open video source: {src}")
    print(f"Opened video file {src}")
    return cap


def delay_for(cap):
    """waitKey delay (ms) that plays a video file at its real speed; 1 ms for cameras."""
    fps = cap.get(cv2.CAP_PROP_FPS)
    frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    if frames and frames > 0 and fps and fps > 0:
        return max(1, int(1000 / fps))
    return 1


def frame_limit(n):
    """True when an automatic test asked the loop to stop after LAB_MAX_FRAMES frames."""
    return MAX_FRAMES > 0 and n >= MAX_FRAMES


def to_bgr(img):
    """Make any image 3-channel BGR so it can be shown next to colour images."""
    if img.ndim == 2:
        return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    return img


def grid(images, labels=None, cols=None, scale=1.0):
    """Place images in a grid (all resized to the first image's size) with labels."""
    cols = cols or len(images)
    h, w = images[0].shape[:2]
    h, w = int(h * scale), int(w * scale)
    tiles = []
    for i, img in enumerate(images):
        tile = cv2.resize(to_bgr(img), (w, h))
        if labels:
            cv2.rectangle(tile, (0, 0), (w, 30), (0, 0, 0), -1)
            cv2.putText(tile, labels[i], (8, 21), FONT, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
        tiles.append(tile)
    while len(tiles) % cols:
        tiles.append(np.zeros_like(tiles[0]))
    rows = [np.hstack(tiles[r:r + cols]) for r in range(0, len(tiles), cols)]
    return np.vstack(rows)
