"""
Exercise 09 - Advanced thresholding                      (lecture block 09)

Goal:  compare a global threshold, Otsu's automatic threshold and adaptive
       thresholding on a page photographed under uneven light.
Run:   python exercises/ex09_thresholds.py

Checkpoint: global and Otsu lose the dark right side of the page;
            both adaptive versions keep every line readable.
Try:        block sizes 15, 31, 51 and C values 5, 10, 20. What changes?
"""
import sys
from pathlib import Path

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if (p / "labutils.py").exists())))
import cv2
from labutils import close, data, grid, out, show

BLOCK, C = 31, 10          # block size must be odd

page = cv2.imread(data("document.png"), cv2.IMREAD_GRAYSCALE)

# STEP 1 - one global threshold for the whole page
_, glob = cv2.threshold(page, 127, 255, cv2.THRESH_BINARY)

# STEP 2 - Otsu picks the threshold from the histogram
T, otsu = cv2.threshold(page, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
print(f"Otsu chose T = {T:.0f}")

# STEP 3 - adaptive: a different threshold for every neighbourhood
mean = cv2.adaptiveThreshold(page, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, BLOCK, C)
gauss = cv2.adaptiveThreshold(page, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, BLOCK, C)

panel = grid([page, glob, otsu, mean, gauss, page],
             ["photo (uneven light)", "global T=127", f"Otsu T={T:.0f}", f"adaptive mean {BLOCK}/{C}",
              f"adaptive gaussian {BLOCK}/{C}", "photo"], cols=3, scale=0.55)
cv2.imwrite(out("thresholds.png"), panel)
show("Thresholding compared", panel)
close()
