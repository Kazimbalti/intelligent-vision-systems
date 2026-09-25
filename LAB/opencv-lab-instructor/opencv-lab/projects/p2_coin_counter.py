"""
Project 2 - Coin counter                                 (blocks 05, 06, 07)

Count the coins in data/coins.png, measure each one, and sort them into
large and small by area.
Run:   python projects/p2_coin_counter.py
       python projects/p2_coin_counter.py --image my_photo.jpg

Done when: the program prints 9 coins (5 large, 4 small) and saves
           output/coins_counted.png with every coin numbered.
Hint:  coins are DARK on light paper, so use THRESH_BINARY_INV.
"""
# >>> Fill in every TODO below, run the file, and compare with the Checkpoint above. <<<
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if (p / "labutils.py").exists())))
import cv2
import numpy as np
from labutils import FONT, close, data, out, show

ap = argparse.ArgumentParser()
ap.add_argument("--image", default=None)
ap.add_argument("--min-area", type=int, default=300)
args = ap.parse_args()

img = cv2.imread(args.image or data("coins.png"))

# 1. binary mask: coins white, paper black
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blur = None  # TODO 1: blur with a 7x7 Gaussian
_, bw = None, None  # TODO 2: inverted Otsu threshold
bw = None  # TODO 3: remove the dust with an opening

# 2. contours -> filter -> measure
contours, _ = None, None  # TODO 4: outer contours
coins = None  # TODO 5: keep contours larger than min-area
areas = [cv2.contourArea(c) for c in coins]

# 3. split large / small halfway between the smallest and largest area
split = (min(areas) + max(areas)) / 2 if areas else 0
large = 0
for i, (c, a) in enumerate(zip(coins, areas), start=1):
    (x, y), r = cv2.minEnclosingCircle(c)
    is_large = a > split
    large += is_large
    color = (0, 200, 0) if is_large else (255, 150, 0)
    cv2.circle(img, (int(x), int(y)), int(r), color, 3)
    cv2.putText(img, str(i), (int(x) - 8, int(y) + 8), FONT, 0.8, (255, 255, 255), 2)
    print(f"coin {i}: area {a:6.0f} px   {'large' if is_large else 'small'}")

summary = f"{len(coins)} coins: {large} large, {len(coins) - large} small"
print(summary)
cv2.putText(img, summary, (10, 30), FONT, 0.9, (0, 0, 200), 2)
cv2.imwrite(out("coins_counted.png"), img)
show("Coin counter", img)
close()
