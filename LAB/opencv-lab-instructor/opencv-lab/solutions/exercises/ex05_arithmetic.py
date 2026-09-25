"""
Exercise 05 - Arithmetic, blending, threshold and masks  (lecture block 05)

Goal:  see why cv2.add is safer than NumPy '+', blend two images, try the
       four basic threshold types, and use bitwise operations with masks.
Run:   python exercises/ex05_arithmetic.py

Checkpoint: STEP 1 prints  numpy: 4  cv2.add: 255  and  numpy: 16  cv2.subtract: 0
            STEP 5 shows only the sun, everything else black.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if (p / "labutils.py").exists())))
import cv2
import numpy as np
from labutils import close, data, grid, out, show

# STEP 1 - uint8 arithmetic: wrap-around (NumPy) vs saturation (OpenCV)
a = np.full((2, 2), 250, np.uint8)
b = np.full((2, 2), 10, np.uint8)
print("250 + 10 ->  numpy:", (a + b)[0, 0], "  cv2.add:", cv2.add(a, b)[0, 0])
print(" 10 - 250 -> numpy:", (b - a)[0, 0], "  cv2.subtract:", cv2.subtract(b, a)[0, 0])

# STEP 2 - brighten a photo both ways and compare
scene = cv2.imread(data("scene.jpg"))
bright_np = scene + np.uint8(80)                      # wraps around: bright areas turn dark
bright_cv = cv2.add(scene, np.full_like(scene, 80))
panel = grid([scene, bright_np, bright_cv], ["original", "numpy + 80 (wraps)", "cv2.add 80 (saturates)"], scale=0.6)
cv2.imwrite(out("brighten.png"), panel)
show("Step 2 - brighten", panel)

# STEP 3 - blending with addWeighted: out = alpha*A + beta*B + gamma
A = cv2.imread(data("blend_a.png"))
B = cv2.imread(data("blend_b.png"))
blends = []
for alpha in (0.25, 0.5, 0.75):
    blends.append(cv2.addWeighted(A, alpha, B, 1 - alpha, 0))
panel = grid(blends, ["alpha 0.25", "alpha 0.50", "alpha 0.75"], scale=0.6)
cv2.imwrite(out("blend.png"), panel)
show("Step 3 - blending", panel)

# STEP 4 - the four basic threshold types at T = 127
g = cv2.imread(data("gradient.png"), cv2.IMREAD_GRAYSCALE)
_, t_bin = cv2.threshold(g, 127, 255, cv2.THRESH_BINARY)
_, t_inv = cv2.threshold(g, 127, 255, cv2.THRESH_BINARY_INV)
_, t_trunc = cv2.threshold(g, 127, 255, cv2.THRESH_TRUNC)
_, t_zero = cv2.threshold(g, 127, 255, cv2.THRESH_TOZERO)
panel = grid([g, t_bin, t_inv, t_trunc, t_zero, g],
             ["gray", "BINARY", "BINARY_INV", "TRUNC", "TOZERO", "gray"], cols=3, scale=0.5)
cv2.imwrite(out("threshold_types.png"), panel)
show("Step 4 - threshold types", panel)

# STEP 5 - bitwise operations on two masks
m1 = np.zeros((300, 400), np.uint8)
cv2.rectangle(m1, (50, 75), (250, 225), 255, -1)
m2 = np.zeros((300, 400), np.uint8)
cv2.circle(m2, (250, 150), 100, 255, -1)
AND = cv2.bitwise_and(m1, m2)
OR = cv2.bitwise_or(m1, m2)
XOR = cv2.bitwise_xor(m1, m2)
NOT = cv2.bitwise_not(m1)
panel = grid([m1, m2, AND, OR, XOR, NOT], ["A", "B", "A AND B", "A OR B", "A XOR B", "NOT A"], cols=3, scale=0.8)
cv2.imwrite(out("bitwise.png"), panel)
show("Step 5 - bitwise", panel)

# STEP 6 - use a mask to keep only the sun
mask = np.zeros(scene.shape[:2], np.uint8)
cv2.circle(mask, (320, 190), 62, 255, -1)
sun_only = cv2.bitwise_and(scene, scene, mask=mask)
cv2.imwrite(out("sun_only.png"), sun_only)
show("Step 6 - masked", sun_only)
close()
