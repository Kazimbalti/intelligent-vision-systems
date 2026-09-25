"""
Exercise 03 - Drawing shapes and text                    (lecture block 03)

Goal:  draw a line, rectangle, circle, polygon and text; then write a
       reusable function that draws a "detection" box with a label.
Run:   python exercises/ex03_drawing.py

Checkpoint: output/drawing.png matches the drawing slide in the lecture.
            Remember: colours are (B, G, R) and points are (x, y).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if (p / "labutils.py").exists())))
import cv2
import numpy as np
from labutils import FONT, close, data, out, show

# STEP 1 - a black canvas: 400 rows (height) x 640 columns (width) x 3 channels
img = np.zeros((400, 640, 3), np.uint8)

# STEP 2 - draw the five primitives
cv2.line(img, (20, 380), (300, 200), (0, 255, 0), 3)
cv2.rectangle(img, (340, 40), (600, 180), (255, 0, 0), 3)
cv2.circle(img, (470, 290), 60, (0, 0, 255), -1)
pts = np.array([[60, 60], [240, 40], [200, 160], [80, 150]], np.int32)
cv2.polylines(img, [pts], True, (255, 0, 255), 3)
cv2.putText(img, "Hi", (40, 250), FONT, 1.2, (255, 255, 255), 2, cv2.LINE_AA)
cv2.imwrite(out("drawing.png"), img)
show("Step 2 - primitives", img)


# STEP 3 - a helper you will reuse in every project
def draw_detection(image, box, label, color=(0, 255, 255)):
    """Draw a box (x, y, w, h) with a filled label bar on top, like a detector does."""
    x, y, w, h = box
    cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
    (tw, th), _ = cv2.getTextSize(label, FONT, 0.6, 1)
    cv2.rectangle(image, (x, y - th - 10), (x + tw + 8, y), color, -1)
    cv2.putText(image, label, (x + 4, y - 6), FONT, 0.6, (0, 0, 0), 1, cv2.LINE_AA)


scene = cv2.imread(data("scene.jpg"))
draw_detection(scene, (255, 125, 130, 130), "sun 0.97")
cv2.imwrite(out("detection.png"), scene)
show("Step 3 - a detection box", scene)
close()
