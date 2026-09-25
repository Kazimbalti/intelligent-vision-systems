"""
Exercise 01 - Load, save and display images            (lecture block 01)

Goal:  read an image from disk, inspect it, show it, and save it in two formats.
Run:   python exercises/ex01_load_save_display.py
Keys:  press any key to close each window.

Checkpoint: the colour image has shape (400, 640, 3) and dtype uint8.
            The grayscale image has shape (400, 640).
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if (p / "labutils.py").exists())))
import cv2
from labutils import close, data, out, show

# STEP 1 - read a colour image and inspect it
img = cv2.imread(data("scene.jpg"))
if img is None:
    raise FileNotFoundError("img is None: finish STEP 1 (or check the path)")
print("shape:", img.shape, " dtype:", img.dtype)
h, w = img.shape[:2]
print(f"height = {h}, width = {w}, channels = {img.shape[2]}")
show("Step 1 - colour image", img)

# STEP 2 - read the same file as a single-channel grayscale image
gray = cv2.imread(data("scene.jpg"), cv2.IMREAD_GRAYSCALE)
print("grayscale shape:", gray.shape)
show("Step 2 - grayscale", gray)

# STEP 3 - what does imread return for a file that does not exist?
missing = cv2.imread("this_file_does_not_exist.jpg")
print("imread on a wrong path returns:", missing)

# STEP 4 - save as PNG (lossless) and as JPEG at two qualities, then compare sizes
cv2.imwrite(out("scene_copy.png"), img)
cv2.imwrite(out("scene_q90.jpg"), img, [cv2.IMWRITE_JPEG_QUALITY, 90])
cv2.imwrite(out("scene_q20.jpg"), img, [cv2.IMWRITE_JPEG_QUALITY, 20])
for name in ["scene_copy.png", "scene_q90.jpg", "scene_q20.jpg"]:
    print(f"  {name:16s} {os.path.getsize(out(name)) / 1024:7.1f} KB")

close()
