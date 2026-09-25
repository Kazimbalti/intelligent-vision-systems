"""
make_samples.py - creates every image and video the lab needs in data/.

Run once after installing:   python make_samples.py
Everything is generated with OpenCV and NumPy, so no downloads are needed
and every student gets exactly the same files.
"""
from pathlib import Path

import cv2
import numpy as np

DATA = Path(__file__).resolve().parent / "data"
DATA.mkdir(exist_ok=True)
rng = np.random.default_rng(7)


def save(name, img):
    cv2.imwrite(str(DATA / name), img)
    print(f"  data/{name:18s} {img.shape}")


def hsv_to_bgr(h, s=200, v=220):
    px = np.uint8([[[h, s, v]]])
    return tuple(int(c) for c in cv2.cvtColor(px, cv2.COLOR_HSV2BGR)[0, 0])


def scene():
    """A sunset: sky gradient, sun at (320, 190) radius 60, mountains."""
    h, w = 400, 640
    img = np.zeros((h, w, 3), np.uint8)
    top, bottom = np.array([140, 40, 90]), np.array([60, 150, 255])  # BGR purple -> orange
    for y in range(h):
        img[y] = top + (bottom - top) * (y / (h - 1))
    cv2.circle(img, (320, 190), 60, (90, 225, 255), -1, cv2.LINE_AA)
    mountains = np.array([[0, 400], [0, 300], [110, 230], [210, 300], [330, 215], [470, 290], [560, 240], [640, 280], [640, 400]], np.int32)
    cv2.fillPoly(img, [mountains], (60, 25, 45), cv2.LINE_AA)
    return img


def city():
    h, w = 400, 640
    img = np.full((h, w, 3), (58, 29, 11), np.uint8)
    x = 0
    while x < w:
        bw, bh = int(rng.integers(50, 90)), int(rng.integers(120, 330))
        cv2.rectangle(img, (x, h - bh), (x + bw - 6, h), (77, 41, 22), -1)
        for yy in range(h - bh + 10, h - 10, 22):
            for xx in range(x + 8, x + bw - 16, 16):
                if rng.random() > 0.45:
                    cv2.rectangle(img, (xx, yy), (xx + 7, yy + 10), (102, 209, 255), -1)
        x += bw
    return img


def gradient():
    h, w = 400, 640
    img = np.tile(np.linspace(0, 255, w, dtype=np.float32), (h, 1)).astype(np.uint8)
    cv2.circle(img, (140, 200), 90, 60, -1)
    cv2.rectangle(img, (270, 110), (400, 290), 150, -1)
    tri = np.array([[520, 110], [610, 290], [430, 290]], np.int32)
    cv2.fillPoly(img, [tri], 215)
    return img


def shapes():
    """6 shapes (one is a ring with a hole) + 5 small noise dots."""
    img = np.full((480, 640, 3), 30, np.uint8)
    white = (240, 240, 240)
    cv2.fillPoly(img, [np.array([[90, 40], [160, 170], [20, 170]], np.int32)], white)
    cv2.rectangle(img, (220, 60), (400, 150), white, -1)          # rectangle
    cv2.rectangle(img, (460, 50), (570, 160), white, -1)          # square
    pent = [(110 + 70 * np.cos(np.radians(a)), 330 + 70 * np.sin(np.radians(a))) for a in range(-90, 270, 72)]
    cv2.fillPoly(img, [np.array(pent, np.int32)], white)          # pentagon
    cv2.circle(img, (320, 330), 70, white, -1)                    # circle
    cv2.circle(img, (520, 330), 70, white, -1)                    # ring ...
    cv2.circle(img, (520, 330), 35, (30, 30, 30), -1)             # ... with a hole
    for (x, y) in [(200, 250), (420, 240), (600, 440), (40, 440), (430, 420)]:
        cv2.circle(img, (x, y), 3, white, -1)                     # noise
    return img


def coins():
    """9 coins on uneven paper: 5 large (r=40) and 4 small (r=28), plus dust."""
    h, w = 600, 800
    paper = np.tile(np.linspace(235, 200, w, dtype=np.float32), (h, 1))
    paper += rng.normal(0, 3, (h, w))
    img = cv2.cvtColor(np.clip(paper, 0, 255).astype(np.uint8), cv2.COLOR_GRAY2BGR)
    large = [(140, 150), (380, 120), (620, 170), (260, 420), (560, 450)]
    small = [(250, 270), (470, 300), (680, 340), (110, 470)]
    for (x, y) in large + small:
        r = 40 if (x, y) in large else 28
        cv2.circle(img, (x + 4, y + 5), r, (150, 150, 150), -1, cv2.LINE_AA)   # soft shadow
        cv2.circle(img, (x, y), r, (55, 105, 150), -1, cv2.LINE_AA)
        cv2.circle(img, (x, y), int(r * 0.75), (75, 130, 175), 2, cv2.LINE_AA)
    for _ in range(40):                                              # dust specks
        x, y = int(rng.integers(0, w)), int(rng.integers(0, h))
        cv2.circle(img, (x, y), 1, (90, 90, 90), -1)
    return img


BALL_HUES = [0, 15, 30, 60, 115, 150]  # red, orange, yellow, green, blue, magenta (OpenCV hue)


def balls():
    """6 coloured balls; the green one (x=464) is half in shadow."""
    img = np.full((300, 800, 3), (110, 104, 100), np.uint8)
    for i, hue in enumerate(BALL_HUES):
        cv2.circle(img, (80 + 128 * i, 150), 45, hsv_to_bgr(hue), -1, cv2.LINE_AA)
    x0 = 464
    img[:, x0:x0 + 60] = (img[:, x0:x0 + 60] * 0.45).astype(np.uint8)  # shadow band
    return img


def document():
    """A page of text photographed under a lamp: bright left, dark right."""
    h, w = 500, 800
    img = np.full((h, w), 235, np.uint8)
    lines = ["OpenCV lab - adaptive thresholding", "The lamp lights the left side of the page",
             "while the right side falls into shadow.", "A single global threshold cannot read both.",
             "Adaptive thresholding compares every pixel", "with the mean of its own neighbourhood.",
             "Block size must be an odd number.", "C is subtracted from the local mean.",
             "Try block sizes 15, 31 and 51."]
    for i, text in enumerate(lines):
        cv2.putText(img, text, (20, 95 + i * 46), cv2.FONT_HERSHEY_SIMPLEX, 1.2, 40, 2, cv2.LINE_AA)
    yy, xx = np.mgrid[0:h, 0:w]
    light = 1.0 - 0.78 * (xx / w) - 0.12 * (yy / h)
    page = img.astype(np.float32) * light + rng.normal(0, 3, (h, w))
    return np.clip(page, 0, 255).astype(np.uint8)


def write_video(name, frames, size, fps=30):
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    vw = cv2.VideoWriter(str(DATA / name), fourcc, fps, size)
    if not vw.isOpened():
        raise IOError("VideoWriter could not open - check your OpenCV install")
    n = 0
    for f in frames:
        vw.write(f)
        n += 1
    vw.release()
    print(f"  data/{name:18s} {n} frames at {fps} fps, {size[0]}x{size[1]}")


def ball_frames(seconds=12, fps=30):
    """A green ball moving over a room, with red/blue/yellow distractors."""
    bg = np.full((480, 640, 3), (72, 64, 59), np.uint8)
    bg[340:] = (91, 81, 74)
    cv2.rectangle(bg, (40, 50), (210, 260), (105, 94, 86), -1)
    cv2.rectangle(bg, (480, 40), (660, 160), (105, 94, 86), -1)
    cv2.rectangle(bg, (90, 370), (160, 440), (69, 69, 214), -1)
    cv2.circle(bg, (600, 400), 40, (214, 111, 59), -1)
    cv2.fillPoly(bg, [np.array([[300, 450], [350, 370], [400, 450]], np.int32)], (65, 195, 224))
    for i in range(seconds * fps):
        t = i / fps
        f = bg.copy()
        x, y = int(320 + 230 * np.sin(t * 0.8)), int(210 + 130 * np.sin(t * 1.3 + 1))
        r = int(30 + 8 * np.sin(t * 0.6))
        cv2.circle(f, (x, y), r, hsv_to_bgr(60, 190, 200), -1, cv2.LINE_AA)
        cv2.circle(f, (x - r // 3, y - r // 3), r // 4, (200, 240, 210), -1, cv2.LINE_AA)
        noise = rng.normal(0, 4, f.shape)
        yield np.clip(f + noise, 0, 255).astype(np.uint8)


def traffic_frames(seconds=12, fps=30):
    """A street: three cars and a pedestrian moving over a static background."""
    w, h = 640, 360
    bg = np.full((h, w, 3), (170, 140, 110), np.uint8)
    for x, bh in [(0, 120), (90, 160), (200, 100), (320, 170), (450, 130), (560, 150)]:
        cv2.rectangle(bg, (x, 190 - bh), (x + 100, 190), (120, 110, 100), -1)
    cv2.rectangle(bg, (0, 190), (w, 320), (80, 80, 80), -1)
    for x in range(0, w, 60):
        cv2.rectangle(bg, (x, 252), (x + 30, 258), (220, 220, 220), -1)
    cv2.rectangle(bg, (0, 320), (w, h), (150, 150, 150), -1)
    cars = [(40, 205, 90, (40, 40, 200)), (160, 265, 60, (200, 120, 30)), (-140, 205, 130, (40, 200, 230))]
    for i in range(seconds * fps):
        t = i / fps
        f = bg.copy()
        for x0, y, speed, col in cars:
            x = int((x0 + speed * t) % (w + 200)) - 100
            shadow = f[y + 36:y + 50, max(0, x):max(0, x + 110)]
            f[y + 36:y + 50, max(0, x):max(0, x + 110)] = (shadow * 0.6).astype(np.uint8)
            cv2.rectangle(f, (x, y), (x + 100, y + 40), col, -1)
            cv2.rectangle(f, (x + 20, y - 14), (x + 75, y), col, -1)
        px = int(600 - 22 * t)
        cv2.rectangle(f, (px, 300), (px + 14, 350), (60, 50, 40), -1)
        cv2.circle(f, (px + 7, 292), 8, (60, 50, 40), -1)
        noise = rng.normal(0, 4, f.shape)
        yield np.clip(f + noise, 0, 255).astype(np.uint8)


if __name__ == "__main__":
    print("Creating sample data ...")
    sc = scene()
    save("scene.jpg", sc)
    save("blend_a.png", sc)
    save("blend_b.png", city())
    save("gradient.png", gradient())
    save("shapes.png", shapes())
    save("coins.png", coins())
    save("balls.png", balls())
    save("document.png", document())
    write_video("ball.mp4", ball_frames(), (640, 480))
    write_video("traffic.mp4", traffic_frames(), (640, 360))
    print("Done. All files are in the data/ folder.")
