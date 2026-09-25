"""
Exercise 04 - The image as a NumPy array                 (lecture block 04)

Goal:  read and change single pixels, crop regions, understand views vs
       copies, split colour channels.
Run:   python exercises/ex04_pixels.py

Checkpoint: the pixel at row 100, col 200 is printed as three numbers (B, G, R).
            The sun crop has shape (130, 130, 3).
            After STEP 4 the top-left corner of img is black but the top-right is NOT white.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if (p / "labutils.py").exists())))
import cv2
import numpy as np
from labutils import close, data, grid, out, show

img = cv2.imread(data("scene.jpg"))

# STEP 1 - read one pixel. Indexing is [row, column] = [y, x]
b, g, r = img[100, 200]
print(f"pixel [100, 200]  B={b}  G={g}  R={r}")

# STEP 2 - write pixels
img[100, 200] = (0, 0, 255)
img[50:60, 100:110] = (0, 0, 255)

# STEP 3 - crop the sun: rows 125..254, columns 255..384
sun = img[125:255, 255:385]
print("sun crop shape:", sun.shape)
show("Step 3 - sun crop", sun)

# STEP 4 - a slice is a VIEW: changing it changes the original
view = img[0:50, 0:50]
view[:] = 0                                  # paints the original black too
safe = img[0:50, 590:640].copy()
safe[:] = 255                                # the original is untouched
print("top-left of img  :", img[10, 10], "(changed through the view)")
print("top-right of img :", img[10, 600], "(unchanged, we used .copy())")

# STEP 5 - split the channels and compare them
blue, green, red = cv2.split(img)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
print(f"mean brightness: B={blue.mean():.0f} G={green.mean():.0f} R={red.mean():.0f} gray={gray.mean():.0f}")
panel = grid([img, blue, green, red], ["image", "B channel", "G channel", "R channel"], cols=2, scale=0.6)
cv2.imwrite(out("channels.png"), panel)
show("Step 5 - channels", panel)
close()
