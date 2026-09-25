"""
Exercise 03 - Drawing shapes and text                    (lecture block 03)

Goal:  draw a line, rectangle, circle, polygon and text; then write a
       reusable function that draws a "detection" box with a label.
Run:   python exercises/ex03_drawing.py

Checkpoint: output/drawing.png matches the drawing slide in the lecture.
            Remember: colours are (B, G, R) and points are (x, y).
"""
# >>> Fill in every TODO below, run the file, and compare with the Checkpoint above. <<<
import sys
from pathlib import Path

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if (p / "labutils.py").exists())))
import cv2
import numpy as np
from labutils import FONT, close, data, out, show

# STEP 1 - a black canvas: 400 rows (height) x 640 columns (width) x 3 channels
img = np.zeros((400, 640, 3), np.uint8)

# STEP 2 - draw the five primitives
pass  # TODO 1: green line from (20, 380) to (300, 200), thickness 3
pass  # TODO 2: blue rectangle from (340, 40) to (600, 180), thickness 3
pass  # TODO 3: filled red circle, centre (470, 290), radius 60
pts = np.array([[60, 60], [240, 40], [200, 160], [80, 150]], np.int32)
pass  # TODO 4: closed magenta polygon through pts
pass  # TODO 5: white text "Hi" at (40, 250)
cv2.imwrite(out("drawing.png"), img)
show("Step 2 - primitives", img)


# STEP 3 - a helper you will reuse in every project
def draw_detection(image, box, label, color=(0, 255, 255)):
    """Draw a box (x, y, w, h) with a filled label bar on top, like a detector does."""
    x, y, w, h = box
    pass  # TODO 6: draw the box outline
    (tw, th), _ = cv2.getTextSize(label, FONT, 0.6, 1)
    pass  # TODO 7: draw a filled bar just above the box
    cv2.putText(image, label, (x + 4, y - 6), FONT, 0.6, (0, 0, 0), 1, cv2.LINE_AA)


scene = cv2.imread(data("scene.jpg"))
draw_detection(scene, (255, 125, 130, 130), "sun 0.97")
cv2.imwrite(out("detection.png"), scene)
show("Step 3 - a detection box", scene)
close()
