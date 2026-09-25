"""
Exercise 07 - Contour features and shape naming          (lecture block 07)

Goal:  for every real object, measure the bounding box, area, perimeter
       and centroid; count corners with approxPolyDP to name the shape.
Run:   python exercises/ex07_features.py

Checkpoint: 6 objects are reported (the 5 noise dots are filtered out) and
            they are named triangle, rectangle, square, pentagon, circle, circle.
            (The ring is a circle on the outside.)
"""
# >>> Fill in every TODO below, run the file, and compare with the Checkpoint above. <<<
import sys
from pathlib import Path

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if (p / "labutils.py").exists())))
import cv2
from labutils import FONT, close, data, out, show

MIN_AREA = 500


def name_shape(n_corners, w, h):
    """Name a shape from its number of corners and its box aspect ratio."""
    if n_corners == 3:
        return "triangle"
    if n_corners == 4:
        pass  # TODO 1: square if w/h is between 0.9 and 1.1
    if n_corners == 5:
        return "pentagon"
    return "circle"


img = cv2.imread(data("shapes.png"))
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
contours, _ = cv2.findContours(bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

print(f"{'#':>2} {'shape':10s} {'x':>4} {'y':>4} {'w':>4} {'h':>4} {'area':>7} {'perim':>6} {'cx':>4} {'cy':>4}")
k = 0
for c in sorted(contours, key=lambda c: (cv2.boundingRect(c)[1] // 150, cv2.boundingRect(c)[0])):  # top row first, left to right
    area = None  # TODO 2: area of the contour
    if area < MIN_AREA:
        continue                                            # skip noise
    x, y, w, h = None, None, None, None  # TODO 3: upright bounding box
    perim = None  # TODO 4: perimeter of the closed contour
    M = cv2.moments(c)
    if M["m00"] == 0:
        continue
    cx, cy = None, None  # TODO 5: centroid from the moments
    approx = None  # TODO 6: simplify the outline to its corners (epsilon = 2% of perimeter)
    label = name_shape(len(approx), w, h)
    k += 1
    print(f"{k:>2} {label:10s} {x:4d} {y:4d} {w:4d} {h:4d} {area:7.0f} {perim:6.0f} {cx:4d} {cy:4d}")

    cv2.rectangle(img, (x, y), (x + w, y + h), (255, 120, 0), 2)
    cv2.circle(img, (cx, cy), 5, (0, 0, 255), -1)
    cv2.putText(img, f"{label} ({len(approx)})", (x, y - 8), FONT, 0.6, (0, 255, 255), 2)

print(f"{k} objects")
cv2.imwrite(out("features.png"), img)
show("Contour features", img)
close()
