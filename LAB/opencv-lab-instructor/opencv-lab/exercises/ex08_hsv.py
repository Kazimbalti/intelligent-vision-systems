"""
Exercise 08 - The HSV colour space                       (lecture block 08)

Goal:  see why HSV beats BGR for colour detection, build colour masks with
       cv2.inRange (including the two-range trick for red), and locate a ball.
Run:   python exercises/ex08_hsv.py
Tip:   python tools/hsv_tuner.py data/balls.png   lets you find ranges with sliders.

Checkpoint: the sunlit and shaded green pixels have (almost) the same H and S
            but very different V. The HSV mask contains the WHOLE green ball;
            the BGR mask misses its shaded half.
"""
# >>> Fill in every TODO below, run the file, and compare with the Checkpoint above. <<<
import sys
from pathlib import Path

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if (p / "labutils.py").exists())))
import cv2
from labutils import close, data, grid, out, show

img = cv2.imread(data("balls.png"))

# STEP 1 - convert to HSV (H: 0-179, S: 0-255, V: 0-255)
hsv = None  # TODO 1: convert img from BGR to HSV

# STEP 2 - the same green ball in sunlight (x=440) and in shadow (x=490)
for name, x in [("sunlit", 440), ("shaded", 490)]:
    print(f"{name}:  BGR {img[150, x]}   HSV {hsv[150, x]}")

# STEP 3 - a green mask in HSV, and a naive one in BGR for comparison
green = None  # TODO 2: inRange on hsv: H 40-80, S 80-255, V 50-255
green_bgr = cv2.inRange(img, (0, 150, 0), (140, 255, 140))

# STEP 4 - red lives at BOTH ends of the hue circle: two ranges, OR-ed together
r1 = cv2.inRange(hsv, (0, 80, 50), (10, 255, 255))
r2 = cv2.inRange(hsv, (170, 80, 50), (179, 255, 255))
red = None  # TODO 3: combine r1 and r2 into one mask

# STEP 5 - cut out the green pixels and find the ball's centre
only_green = cv2.bitwise_and(img, img, mask=green)
contours, _ = cv2.findContours(green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
ball = None  # TODO 4: keep the largest contour
M = cv2.moments(ball)
cx, cy = int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])
print(f"green ball centre: ({cx}, {cy})  area: {cv2.contourArea(ball):.0f} px")
cv2.circle(only_green, (cx, cy), 6, (255, 255, 255), -1)

panel = grid([img, green_bgr, green, red, only_green, img],
             ["image", "BGR range (misses shade)", "HSV green", "HSV red (2 ranges)", "green only + centre", "image"],
             cols=3, scale=0.55)
cv2.imwrite(out("hsv.png"), panel)
show("HSV colour masks", panel)
close()
