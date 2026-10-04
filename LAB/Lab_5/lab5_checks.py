"""Lab 5 auto-checks, bug-hunt checks and leaderboard scoring.

Intelligent Vision Systems · Lecture 5 Part II · Dr. Muhammad Kazim, University of Lahore.

Every ``check_*`` function prints ✅ when your result is good enough, or a 💡 hint telling you what
to change. The checks never print the answer — use the hints, think, and try again.
"""
import json
import os
import time
import urllib.request

import cv2
import numpy as np

RAW = "https://raw.githubusercontent.com/Kazimbalti/intelligent-vision-systems/main/LAB/Lab_5"

# Reference triangle for test.jpg (the 5B quiz answer is one of many triangles close to this).
_REF_TRIANGLE = ([0, 539], [900, 539], [475, 320])


# ----------------------------------------------------------------------------------------------- helpers
def _ok(msg):
    print("✅ " + msg)
    return True


def _hint(msg):
    print("💡 " + msg)
    return False


def fetch(path):
    """Download ``path`` (relative to LAB/Lab_5 on GitHub) unless it already exists."""
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        urllib.request.urlretrieve(f"{RAW}/{path}", path)
    return path


def _rgb(path):
    return cv2.cvtColor(cv2.imread(fetch(path)), cv2.COLOR_BGR2RGB)


def _triangle_mask(shape, left_bottom, right_bottom, apex):
    ysize, xsize = shape[:2]
    fit_left = np.polyfit((left_bottom[0], apex[0]), (left_bottom[1], apex[1]), 1)
    fit_right = np.polyfit((right_bottom[0], apex[0]), (right_bottom[1], apex[1]), 1)
    fit_bottom = np.polyfit((left_bottom[0], right_bottom[0]), (left_bottom[1], right_bottom[1]), 1)
    XX, YY = np.meshgrid(np.arange(xsize), np.arange(ysize))
    return ((YY > XX * fit_left[0] + fit_left[1]) & (YY > XX * fit_right[0] + fit_right[1])
            & (YY < XX * fit_bottom[0] + fit_bottom[1]))


def _bright(image, t):
    return (image[:, :, 0] >= t[0]) & (image[:, :, 1] >= t[1]) & (image[:, :, 2] >= t[2])



# ============================================================================ 5A · colour selection
def check_color_thresholds(image, red_threshold, green_threshold, blue_threshold):
    """5A quiz: do your thresholds keep the lane lines and drop (almost) everything else?"""
    if image.dtype != np.uint8:
        return _hint("Your image is not uint8 (0-255). Did you read a .png with mpimg? Use the .jpg.")
    kept = _bright(image, (red_threshold, green_threshold, blue_threshold))
    ref = _bright(image, (200, 200, 200)) & _triangle_mask(image.shape, *_REF_TRIANGLE)
    recall = (kept & ref).sum() / max(ref.sum(), 1)
    frac = kept.mean()
    print(f"   kept {100 * frac:.1f}% of all pixels · {100 * recall:.0f}% of the lane-line pixels")
    if recall < 0.85:
        return _hint("You are throwing away lane-line pixels. Lower at least one threshold a little.")
    if frac > 0.03:
        return _hint("Too much survives (sky, road, cars). Raise the thresholds — the sky has a low red value.")
    return _ok("Lane lines kept, almost everything else black. Note the few bright pixels near the horizon.")


def check_hls_mask(image, mask):
    """5A extension: does your HLS mask keep BOTH the yellow and the white line on solidYellowCurve2?"""
    if mask.shape != image.shape[:2]:
        return _hint(f"mask should be a 2-D array of shape {image.shape[:2]}, got {mask.shape}.")
    hls = cv2.cvtColor(image, cv2.COLOR_RGB2HLS).astype(int)
    roi = _triangle_mask(image.shape, [0, image.shape[0] - 1], [image.shape[1], image.shape[0] - 1],
                         [image.shape[1] // 2, int(image.shape[0] * 0.6)])
    yellow = roi & (hls[..., 0] >= 18) & (hls[..., 0] <= 30) & (hls[..., 2] >= 130) & (hls[..., 1] >= 90)
    white = roi & (image.min(axis=2) >= 210)
    on = mask > 0
    ry, rw = (on & yellow).sum() / max(yellow.sum(), 1), (on & white).sum() / max(white.sum(), 1)
    print(f"   yellow line kept {100 * ry:.0f}% · white line kept {100 * rw:.0f}% · mask covers {100 * on.mean():.1f}% of the image")
    if ry < 0.8:
        return _hint("The yellow line is getting lost. Check the hue range (OpenCV hue is 0-180, so yellow ~15-35).")
    if rw < 0.8:
        return _hint("The white line is getting lost. White = high lightness (L), any hue.")
    if on.mean() > 0.08:
        return _hint("Your mask keeps too much of the image. Tighten the saturation / lightness limits.")
    return _ok("Both the yellow and the white line survive — this is why HLS beats RGB here.")


# ============================================================================ 5B · region of interest
def check_triangle(image, left_bottom, right_bottom, apex, rgb_threshold=(200, 200, 200)):
    """5B quiz: does colour AND your triangle pick out only the lane lines?"""
    bright = _bright(image, rgb_threshold)
    yours = bright & _triangle_mask(image.shape, left_bottom, right_bottom, apex)
    ref = bright & _triangle_mask(image.shape, *_REF_TRIANGLE)
    iou = (yours & ref).sum() / max((yours | ref).sum(), 1)
    extra = (yours & ~ref).sum() / max(yours.sum(), 1)
    missed = (ref & ~yours).sum() / max(ref.sum(), 1)
    print(f"   overlap with a good selection: {100 * iou:.0f}%  (missed {100 * missed:.0f}%, extra {100 * extra:.0f}%)")
    if iou >= 0.85:
        return _ok("Only the lane lines are painted red.")
    if missed > extra:
        return _hint("Your triangle cuts off parts of the lane lines — widen the base or move the apex.")
    return _hint("Your triangle still includes things that are not lane lines — lower the apex (larger y) "
                 "towards where the lines meet, around the middle of the image.")


# ============================================================================ 5C · Canny
# Lane-line segments of the 5D quiz answer on exit-ramp.jpg (Canny 50/150, quad mask, rho 2, theta 1°,
# threshold 15, min_line_length 40, max_line_gap 20). Used as the reference for the 5C and 5D checks.
REF_SEGMENTS = np.array([[535, 326, 838, 538], [551, 331, 881, 538], [182, 490, 314, 395], [305, 403, 352, 367], [408, 324, 449, 291], [228, 445, 327, 380], [89, 538, 193, 470], [113, 538, 177, 492], [183, 475, 241, 438], [398, 331, 443, 294], [498, 294, 548, 339], [389, 342, 446, 297], [145, 516, 191, 482], [509, 300, 569, 342], [595, 369, 788, 504], [273, 415, 346, 367], [530, 322, 573, 336], [812, 496, 879, 537], [588, 354, 630, 380], [777, 474, 844, 515], [212, 456, 260, 425], [793, 506, 834, 535]])


def _ref_side(seg):
    return "left" if (seg[0] + seg[2]) / 2 < 480 else "right"


def _dist_to_segment(px, py, seg):
    x1, y1, x2, y2 = [float(v) for v in seg]
    dx, dy = x2 - x1, y2 - y1
    t = np.clip(((px - x1) * dx + (py - y1) * dy) / max(dx * dx + dy * dy, 1e-9), 0, 1)
    return float(np.hypot(px - (x1 + t * dx), py - (y1 + t * dy)))


def check_canny(edges):
    """5C quiz: are the lane lines found as edges, without too much clutter? (exit-ramp.jpg)"""
    if edges.ndim != 2 or edges.dtype != np.uint8:
        return _hint("Pass the output of cv2.Canny: a 2-D uint8 image.")
    near = cv2.dilate((edges > 0).astype(np.uint8), np.ones((9, 9), np.uint8))
    cov = {}
    for side in ("left", "right"):
        ref = np.zeros_like(edges)
        for sg in REF_SEGMENTS:
            if _ref_side(sg) == side:
                cv2.line(ref, (int(sg[0]), int(sg[1])), (int(sg[2]), int(sg[3])), 1, 1)
        cov[side] = (near[ref > 0] > 0).mean()
    n = int((edges > 0).sum())
    print(f"   lane lines covered: left {100 * cov['left']:.0f}%, right {100 * cov['right']:.0f}% · edge pixels: {n:,}")
    if min(cov.values()) < 0.8:
        return _hint("The lane lines are broken up. Lower the thresholds (keep a 1:2-1:3 ratio) or blur less.")
    if n > 30000:
        return _hint("Lots of clutter (trees, texture). Raise the thresholds and/or use a bigger odd blur kernel.")
    return _ok("Clean lane-line edges with little clutter.")


# ============================================================================ 5D · Hough
def check_hough(lines, tol=12):
    """5D quiz: do your HoughLinesP segments lie on the two lane lines only? (exit-ramp.jpg)"""
    if lines is None or len(lines) == 0:
        return _hint("No segments found. Lower the threshold / min_line_length, or check your mask.")
    segs = np.asarray(lines).reshape(-1, 4)
    on = {"left": 0, "right": 0}
    off = 0
    for sg in segs:
        x1, y1, x2, y2 = [float(v) for v in sg]
        pts = [(x1, y1), (x2, y2), ((x1 + x2) / 2, (y1 + y2) / 2)]
        if all(min(_dist_to_segment(px, py, r) for r in REF_SEGMENTS) < tol for px, py in pts):
            on[_ref_side(sg)] += 1
        else:
            off += 1
    print(f"   {len(segs)} segments: {on['left']} on the left lane, {on['right']} on the right lane, {off} elsewhere")
    if min(on.values()) == 0:
        return _hint("One lane line has no segments. Is your region wide enough? Is min_line_length too long?")
    if off > max(1, 0.1 * len(segs)):
        return _hint("Too many segments that are not lane lines. Mask a tighter region or raise threshold / min_line_length.")
    if len(segs) > 30:
        return _hint("Lots of tiny duplicate segments. Raise threshold and min_line_length, allow a bigger max_line_gap.")
    return _ok("Only the lane lines are detected.")


# ============================================================================ bug hunt
_FIXED = set()
BUGS = {
    1: "BGR vs RGB", 2: "array aliasing", 3: "PNG values are 0-1", 4: "even blur kernel",
    5: "float polygon vertices", 6: "HoughLinesP can return None", 7: "left/right slope sign",
    8: "vertical segments (divide by zero)",
}


def bug(n, passed, ok_msg, hint_msg):
    if passed:
        _FIXED.add(n)
        return _ok(f"Bug {n} ({BUGS[n]}) fixed! {ok_msg}")
    return _hint(f"Bug {n} still there: {hint_msg}")


def check_bug(n, *args):
    """Run the check for bug ``n``. Each check calls your fixed function/value."""
    try:
        return _BUG_CHECKS[n](*args)
    except Exception as e:  # a crash means the bug is still there
        return _hint(f"Bug {n} still there: your code raised {type(e).__name__}: {e}")


def _b1(yellow_fn):
    img = _rgb("test_images/solidYellowCurve2.jpg")
    mask = yellow_fn("test_images/solidYellowCurve2.jpg")
    hls = cv2.cvtColor(img, cv2.COLOR_RGB2HLS).astype(int)
    yellow = (hls[..., 0] >= 18) & (hls[..., 0] <= 30) & (hls[..., 2] >= 130) & (hls[..., 1] >= 90)
    yellow[: int(img.shape[0] * 0.6)] = False
    r = ((mask > 0) & yellow).sum() / max(yellow.sum(), 1)
    return bug(1, r > 0.7, "The yellow line is found.", f"only {100 * r:.0f}% of the yellow line is found — "
               "which channel order does cv2.imread return?")


def _b2(original, selected):
    same = np.shares_memory(original, selected)
    return bug(2, (not same) and original.max() > 200 and selected.min() == 0,
               "The original image is untouched.",
               "blacking out pixels also destroyed the original. How do you make a real copy?")


def _b3(kept_fraction):
    return bug(3, 0.003 < kept_fraction < 0.05, f"{100 * kept_fraction:.1f}% of pixels kept.",
               f"kept {100 * kept_fraction:.2f}% of pixels. What range are the values of a PNG read with mpimg?")


def _b4(blur_fn):
    out = blur_fn(np.full((20, 20), 128, np.uint8))
    return bug(4, out is not None and out.shape == (20, 20), "The blur runs.", "GaussianBlur failed.")


def _b5(mask_fn):
    m = mask_fn((540, 960))
    return bug(5, m is not None and m.dtype == np.uint8 and m[500, 480] == 255 and m[50, 480] == 0,
               "The region mask is filled.", "the mask is not filled where it should be.")


def _b6(segments_fn):
    empty = np.zeros((540, 960), np.uint8)
    out = segments_fn(empty)
    return bug(6, out is not None and len(out) == 0, "No crash on a frame with no lines.",
               "on an empty edge image your function should return an empty list.")


def _b7(split_fn):
    segs = [(200, 500, 400, 350), (760, 500, 560, 350)]
    left, right = split_fn(segs)
    ok = len(left) == 1 and left[0][0] == 200 and len(right) == 1 and right[0][0] == 760
    return bug(7, ok, "Left and right are the right way round.",
               "the lanes are swapped. In image coordinates y grows DOWNWARDS — what is the sign of the left lane's slope?")


def _b8(slopes_fn):
    segs = [(200, 500, 400, 350), (300, 100, 300, 400), (760, 500, 560, 350)]
    s = slopes_fn(segs)
    ok = len(s) == 2 and all(np.isfinite(s))
    return bug(8, ok, "Vertical segments are skipped.", f"got {s} — skip segments with x1 == x2.")


_BUG_CHECKS = {1: _b1, 2: _b2, 3: _b3, 4: _b4, 5: _b5, 6: _b6, 7: _b7, 8: _b8}


def bug_hunt_summary():
    print(f"Bugs fixed: {len(_FIXED)} / {len(BUGS)}")
    for n, name in BUGS.items():
        print(f"  {'✅' if n in _FIXED else '⬜'} {n}. {name}")
    if len(_FIXED) == len(BUGS):
        print("🏆 All bugs fixed — show your screen to the TA!")


# ============================================================================ leaderboard
def load_benchmark():
    gt = json.load(open(fetch("leaderboard/ground_truth.json")))
    for f in gt["frames"]:
        fetch("leaderboard/" + f["file"])
    return gt


def _x_at(line, y):
    x1, y1, x2, y2 = [float(v) for v in line]
    if y2 == y1:
        return np.nan
    return x1 + (x2 - x1) * (y - y1) / (y2 - y1)


def score(lane_fn, gt=None, verbose=True):
    """Score ``lane_fn(rgb) -> {'left': (x1,y1,x2,y2) or None, 'right': ...}`` on the benchmark frames.

    A lane counts as correct when its mean horizontal error over the lower part of the image is
    below ``tolerance_px`` (20 px). Reports accuracy on the clean frames, on the hard (degraded) frames
    and overall, plus the mean error (px) and speed (frames/s).
    """
    gt = gt or load_benchmark()
    tol, start = gt["tolerance_px"], gt["eval_rows_from"]
    hits = {"clean": [], "hard": []}
    errors, t, worst = [], 0.0, []
    for f in gt["frames"]:
        rgb = cv2.cvtColor(cv2.imread("leaderboard/" + f["file"]), cv2.COLOR_BGR2RGB)
        t0 = time.perf_counter()
        pred = lane_fn(rgb) or {}
        t += time.perf_counter() - t0
        rows = np.linspace(start * f["h"], f["h"] - 1, 10)
        for side in ("left", "right"):
            p = pred.get(side)
            if p is None:
                err = 100.0
            else:
                err = float(np.nanmean([abs(_x_at(p, y) - _x_at(f[side], y)) for y in rows]))
                err = 100.0 if not np.isfinite(err) else min(err, 100.0)
            errors.append(err)
            hits[f.get("set", "clean")].append(err < tol)
            worst.append((err, f["file"], side))
    acc = lambda h: round(100 * float(np.mean(h)), 1) if h else None
    res = dict(accuracy=acc(hits["clean"] + hits["hard"]), clean=acc(hits["clean"]), hard=acc(hits["hard"]),
               mean_error_px=round(float(np.mean(errors)), 1), fps=round(len(gt["frames"]) / max(t, 1e-9), 1))
    if verbose:
        print(f"Accuracy: {res['accuracy']}% overall  (clean {res['clean']}% · hard {res['hard']}%) "
              f"· mean error {res['mean_error_px']}px · {res['fps']} frames/s")
        print("Hardest cases:", ", ".join(f"{fn.split('/')[-1]} ({s}, {e:.0f}px)" for e, fn, s in sorted(worst)[-3:]))
    return res


def show_worst(lane_fn, k=4, gt=None):
    """Plot the k frames where your lanes are furthest from the labels (green = label, red = yours)."""
    import matplotlib.pyplot as plt
    gt = gt or load_benchmark()
    scored = []
    for f in gt["frames"]:
        rgb = cv2.cvtColor(cv2.imread("leaderboard/" + f["file"]), cv2.COLOR_BGR2RGB)
        pred = lane_fn(rgb) or {}
        rows = np.linspace(gt["eval_rows_from"] * f["h"], f["h"] - 1, 10)
        e = 0
        for side in ("left", "right"):
            p = pred.get(side)
            e += 100 if p is None else min(100, float(np.nanmean([abs(_x_at(p, y) - _x_at(f[side], y)) for y in rows])))
        scored.append((e, f, rgb, pred))
    scored.sort(key=lambda s: -s[0])
    fig, axs = plt.subplots(1, k, figsize=(5 * k, 3.2))
    for ax, (e, f, rgb, pred) in zip(np.atleast_1d(axs), scored[:k]):
        im = rgb.copy()
        for side in ("left", "right"):
            cv2.line(im, *[tuple(int(v) for v in f[side][i:i + 2]) for i in (0, 2)], (0, 255, 0), 4)
            if pred.get(side) is not None:
                p = [int(v) for v in pred[side]]
                cv2.line(im, (p[0], p[1]), (p[2], p[3]), (255, 0, 0), 4)
        ax.imshow(im); ax.set_title(f"{f['file'].split('/')[-1]}  error {e / 2:.0f}px"); ax.axis("off")
    plt.tight_layout(); plt.show()


def submission(team, result):
    """Print the line to send to your TA for the class leaderboard."""
    line = json.dumps(dict(team=team, **result), ensure_ascii=False)
    print("Copy this line and send it to your TA:\n" + line)
    return line
