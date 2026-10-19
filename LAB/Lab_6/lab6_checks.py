"""Lab 6 auto-checks and helpers: camera calibration.

Intelligent Vision Systems · Lecture 6 · Dr. Muhammad Kazim, University of Lahore.

Every ``check_*`` function prints ✅ when your result is good enough, or a 💡 hint telling you what
to change. The checks never print the answer: use the hints, think, and try again.
"""
import glob
import os
import urllib.request

import cv2
import numpy as np

RAW = "https://raw.githubusercontent.com/Kazimbalti/intelligent-vision-systems/main/LAB/Lab_6"

GOPRO = ["GOPR%04d.jpg" % i for i in list(range(32, 39)) + list(range(40, 56)) + list(range(57, 65)) + [66, 67, 68, 69, 70]]
ROAD_CAL = ["calibration%d.jpg" % i for i in range(1, 21)]
ROAD = ["straight_lines1.jpg", "straight_lines2.jpg", "test2.jpg", "test3.jpg", "test5.jpg", "test6.jpg"]
STEREO = ["%s%02d.jpg" % (s, i) for i in [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14] for s in ("left", "right")]


# ----------------------------------------------------------------------------------------------- helpers
def _ok(msg):
    print("✅ " + msg)
    return True


def _hint(msg):
    print("💡 " + msg)
    return False


def fetch(path):
    """Download ``path`` (relative to LAB/Lab_6 on GitHub) unless it already exists."""
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        urllib.request.urlretrieve(f"{RAW}/{path}", path)
    return path


def fetch_set(name):
    """Fetch a whole image set: 'gopro', 'road_cal', 'road' or 'stereo'. Returns the local folder."""
    folder, files = {"gopro": ("data/calibration_wide", GOPRO + ["test_image.jpg"]),
                     "road_cal": ("data/camera_cal", ROAD_CAL),
                     "road": ("data/road", ROAD),
                     "stereo": ("data/stereo", STEREO)}[name]
    for f in files:
        fetch(f"{folder}/{f}")
    return folder


def board_points(nx, ny, square=1.0):
    """(nx*ny, 3) float32 object points (0,0,0), (1,0,0) ... (nx-1, ny-1, 0), times ``square``."""
    objp = np.zeros((nx * ny, 3), np.float32)
    objp[:, :2] = np.mgrid[0:nx, 0:ny].T.reshape(-1, 2) * square
    return objp


def find_corners(gray, pattern, subpix=True):
    """findChessboardCorners (+ cornerSubPix). Always returns (ok, corners) with corners shaped (N, 1, 2)."""
    ok, c = cv2.findChessboardCorners(gray, pattern, None)
    if not ok:
        return False, None
    c = c.reshape(-1, 1, 2).astype(np.float32)
    if subpix:
        c = cv2.cornerSubPix(gray, c, (11, 11), (-1, -1),
                             (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 1e-3))
    return True, c.reshape(-1, 1, 2)


def _reference(folder, pattern, size=None):
    op, ip = [], []
    for f in sorted(glob.glob(folder + "/*.jpg")):
        if "test_image" in f:
            continue
        g = cv2.imread(f, 0)
        if size and g.shape[::-1] != size:
            g = cv2.resize(g, size)
        ok, c = find_corners(g, pattern)
        if ok:
            op.append(board_points(*pattern)); ip.append(c)
    return cv2.calibrateCamera(op, ip, size or g.shape[::-1], None, None)


_cache = {}


def reference_gopro():
    """The instructor calibration of the Udacity GoPro set (K, dist)."""
    if "gopro" not in _cache:
        fetch_set("gopro")
        rms, K, D, _, _ = _reference("data/calibration_wide", (8, 6))
        _cache["gopro"] = (K, D)
    return _cache["gopro"]


def reference_road():
    if "road" not in _cache:
        fetch_set("road_cal")
        rms, K, D, _, _ = _reference("data/camera_cal", (9, 6), size=(1280, 720))
        _cache["road"] = (K, D)
    return _cache["road"]


def fisheye_flags(use_guess=False):
    """RECOMPUTE_EXTRINSIC | FIX_SKEW (| USE_INTRINSIC_GUESS) for cv2.fisheye.calibrate.

    The flag names live in cv2.fisheye.CALIB_* in OpenCV 4.x and in cv2.CALIB_* (different values) in OpenCV 5.x.
    """
    ns = cv2.fisheye if hasattr(cv2.fisheye, "CALIB_RECOMPUTE_EXTRINSIC") else cv2
    flags = ns.CALIB_RECOMPUTE_EXTRINSIC | ns.CALIB_FIX_SKEW
    return flags | ns.CALIB_USE_INTRINSIC_GUESS if use_guess else flags


# ----------------------------------------------------------------------------- synthetic camera (6A, 6E)
def render_board(texture, mm_per_px, K, D, rvec, tvec, size, fisheye=False, background=150):
    """Render a flat textured board (z = 0, x right, y down, in mm) seen by a camera with intrinsics K and
    distortion D. ``fisheye=True`` uses the cv2.fisheye (Kannala-Brandt) model with 4 coefficients.

    For every output pixel we undistort it to a ray, intersect the ray with the board plane and sample the
    texture: an exact, ray-traced picture of what that camera would see.
    """
    W, H = size
    uv = np.stack(np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32)), -1).reshape(-1, 1, 2)
    n = (cv2.fisheye.undistortPoints(uv, K, D) if fisheye else cv2.undistortPoints(uv, K, D)).reshape(-1, 2)
    d = np.hstack([n, np.ones((len(n), 1))])
    R, _ = cv2.Rodrigues(np.asarray(rvec, float))
    t = np.asarray(tvec, float).reshape(3)
    Rt_d, Rt_t = d @ R, R.T @ t
    with np.errstate(divide="ignore", invalid="ignore"):
        s = Rt_t[2] / Rt_d[:, 2]
    Xw = s[:, None] * Rt_d - Rt_t
    mx = (Xw[:, 0] / mm_per_px).reshape(H, W).astype(np.float32)
    my = (Xw[:, 1] / mm_per_px).reshape(H, W).astype(np.float32)
    bad = ~(s > 0).reshape(H, W)
    if fisheye:
        bad |= (np.linalg.norm(n, axis=1) > 25).reshape(H, W)
    mx[bad] = -1; my[bad] = -1
    return cv2.remap(texture, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=background)


def random_poses(n, seed=0, dist_mm=(300, 520), tilt_deg=35, board_mm=(280, 200)):
    """n random board poses (rvec, tvec) that keep a board of ``board_mm`` roughly in view."""
    rng = np.random.default_rng(seed)
    poses = []
    for _ in range(n):
        r = np.radians(rng.uniform(-tilt_deg, tilt_deg, 3)) * np.array([1, 1, 0.3])
        z = rng.uniform(*dist_mm)
        R, _ = cv2.Rodrigues(r)
        c = R @ np.array([board_mm[0] / 2, board_mm[1] / 2, 0])
        shift = rng.uniform(-0.35, 0.35, 2) * z
        poses.append((r, np.array([shift[0] - c[0], shift[1] - c[1], z - c[2]])))
    return poses


# ============================================================================== 6A · pinhole & distortion
def check_projection(uv):
    uv = np.asarray(uv, float).reshape(-1, 2)
    exp = np.array([[740, 310], [740, 310], [440, 560]], float)
    if uv.shape != exp.shape:
        return _hint(f"Expected 3 projected points, got an array of shape {uv.shape}.")
    if np.allclose(uv[0], [310, 740], atol=0.5):
        return _hint("You swapped u and v: u = fx·X/Z + cx is the column (x), v = fy·Y/Z + cy is the row (y).")
    err = np.abs(uv - exp).max()
    if err < 0.5:
        return _ok("All three points project correctly. Points 1 and 2 share a pixel: one camera cannot see depth.")
    if np.allclose(uv[:, 0], exp[:, 0] - 640, atol=0.5):
        return _hint("Close: you forgot to add the principal point (cx, cy).")
    return _hint("Not yet. Divide X and Y by Z first, then multiply by f and add the principal point.")


def check_intrinsics(fx, cx, cy, hfov_deg):
    good = abs(fx - 2714.3) < 2 and abs(cx - 1640) < 1 and abs(cy - 1232) < 1
    if not good:
        if abs(fx - 3.04 / 1.12) < 0.1:
            return _hint("fx must be in pixels: convert the pixel size from µm to mm first (1.12 µm = 0.00112 mm).")
        return _hint("fx = focal length / pixel size (same units!); cx, cy = half the image width and height.")
    if abs(hfov_deg - 62.3) > 0.3:
        return _hint("K is right. For the FOV use 2·atan((W/2) / fx), and convert radians to degrees.")
    return _ok("K and the field of view match the Raspberry Pi Camera v2 datasheet (62.2°).")


def check_distort(fn):
    rng = np.random.default_rng(1)
    for _ in range(5):
        k = rng.normal(0, [0.2, 0.08, 0.004, 0.004, 0.02])
        xy = rng.uniform(-0.8, 0.8, (50, 2))
        exp, _ = cv2.projectPoints(np.hstack([xy, np.ones((50, 1))]), np.zeros(3), np.zeros(3), np.eye(3), k)
        try:
            got = np.asarray(fn(xy[:, 0], xy[:, 1], k), float)
        except Exception as e:  # noqa: BLE001
            return _hint(f"Your function raised {type(e).__name__}: {e}")
        got = got.reshape(2, -1).T if got.shape[0] == 2 else got.reshape(-1, 2)
        if np.abs(got - exp.reshape(-1, 2)).max() > 1e-6:
            kk = np.array(k); kk[2:4] = 0
            exp_r, _ = cv2.projectPoints(np.hstack([xy, np.ones((50, 1))]), np.zeros(3), np.zeros(3), np.eye(3), kk)
            if np.abs(got - exp_r.reshape(-1, 2)).max() < 1e-6:
                return _hint("Radial part is right. Now add the tangential terms with p1 = k[2] and p2 = k[3].")
            return _hint("Mismatch with cv2.projectPoints. Remember OpenCV's order: k = [k1, k2, p1, p2, k3].")
    return _ok("Your distortion model matches cv2.projectPoints exactly.")


# ============================================================================== 6B · corners
def check_pattern_size(nx, ny):
    if (nx, ny) == (8, 6):
        return _ok("8 × 6 inner corners: that is the patternSize for the Udacity GoPro board.")
    if (nx, ny) == (9, 7):
        return _hint("You counted squares. Count only the inner corners, where two black and two white squares meet.")
    if (nx, ny) == (6, 8):
        return _hint("nx is the number of corners along a row (left → right), ny along a column.")
    return _hint("Not quite. Try findChessboardCorners with your guess: it returns False if the size is wrong.")


def check_object_points(objp, nx=8, ny=6):
    objp = np.asarray(objp)
    if objp.shape != (nx * ny, 3):
        return _hint(f"objp should have shape ({nx * ny}, 3), one (x, y, z) row per corner, not {objp.shape}.")
    if objp.dtype != np.float32:
        return _hint("Make objp float32: OpenCV's calibration functions expect 32-bit floats.")
    if not np.allclose(objp, board_points(nx, ny)):
        if np.allclose(objp[:, [1, 0, 2]], board_points(ny, nx)) or np.allclose(objp[1], [0, 1, 0]):
            return _hint("x must change fastest: (0,0,0), (1,0,0), (2,0,0) … matching the corner order. Check your mgrid/reshape.")
        if objp[-1].tolist() == [nx, ny, 0]:
            return _hint(f"The last corner is ({nx - 1}, {ny - 1}, 0): counting starts at 0.")
        return _hint("Use np.mgrid[0:nx, 0:ny].T.reshape(-1, 2) for the first two columns and leave z = 0.")
    return _ok("Object points are correct: (0,0,0) … (7,5,0), z = 0 on the flat board.")


def check_found(n_found, n_total):
    if n_found == n_total - 1 and n_total == len(GOPRO):
        return _ok(f"Board found in {n_found} of {n_total} images: one image has corners cut off or blurred. That is normal.")
    if n_found == 0:
        return _hint("No board found at all: check patternSize and that you pass a grayscale image.")
    if n_found < n_total - 1:
        return _hint(f"Only {n_found} / {n_total}. Did you use the right patternSize for every image?")
    return _ok(f"Board found in {n_found} / {n_total} images.")


# ============================================================================== 6C · calibrate & undistort
def check_calibration(ret, mtx, dist, size=None):
    mtx = np.asarray(mtx); dist = np.asarray(dist).ravel()
    if size is not None and tuple(size) == (960, 1280):
        return _hint("imageSize must be (width, height) = (1280, 960). Use gray.shape[::-1].")
    if mtx.shape != (3, 3):
        return _hint("mtx should be the 3 × 3 camera matrix returned by calibrateCamera.")
    fx, fy, cx, cy = mtx[0, 0], mtx[1, 1], mtx[0, 2], mtx[1, 2]
    if not (520 < fx < 600 and 520 < fy < 600):
        return _hint(f"fx = {fx:.0f} px looks wrong for this GoPro (~560). Check patternSize and the object points.")
    if not (600 < cx < 700 and 450 < cy < 550):
        return _hint(f"Principal point ({cx:.0f}, {cy:.0f}) is far from the image centre (640, 480): is imageSize (w, h)?")
    if dist[0] > -0.15:
        return _hint("k1 should be clearly negative: this is a barrel-distorting wide-angle lens.")
    if ret > 1.0:
        return _hint(f"RMS {ret:.2f} px is high. Did you refine the corners with cornerSubPix and use all images?")
    return _ok(f"Calibration looks right: fx ≈ {fx:.0f} px, k1 ≈ {dist[0]:.2f}, RMS = {ret:.2f} px.")


def check_cal_undistort(fn):
    K, D = reference_gopro()
    img = cv2.imread(fetch("data/calibration_wide/test_image.jpg"))
    folder = "data/calibration_wide"
    op, ip = [], []
    for f in sorted(glob.glob(folder + "/GOPR*.jpg"))[:12]:
        ok, c = find_corners(cv2.imread(f, 0), (8, 6))
        if ok:
            op.append(board_points(8, 6)); ip.append(c)
    try:
        out = fn(img.copy(), op, ip)
    except Exception as e:  # noqa: BLE001
        return _hint(f"cal_undistort raised {type(e).__name__}: {e}")
    if out is None or out.shape != img.shape:
        return _hint("Return the undistorted image, with the same shape as the input.")
    if np.array_equal(out, img):
        return _hint("The output is identical to the input: did you delete the `undist = np.copy(img)` line?")
    rms, K2, D2, _, _ = cv2.calibrateCamera(op, ip, img.shape[1::-1], None, None)
    ref = cv2.undistort(img, K2, D2, None, K2)
    if np.abs(out.astype(int) - ref).mean() > 3:
        return _hint("The image is changed but not the way cv2.undistort(img, mtx, dist, None, mtx) changes it.")
    return _ok("cal_undistort works: lines on the board are straight again.")


def check_per_view(errs, n_views):
    errs = np.asarray(errs, float)
    if len(errs) != n_views:
        return _hint(f"One error per calibration image: expected {n_views}, got {len(errs)}.")
    if errs.max() < 1.5:
        return _hint("Your worst view should stand out (> 3 px). Did you compute sqrt(mean(dx² + dy²)) per view?")
    return _ok(f"Per-view errors look right; the worst view is #{int(errs.argmax())} at {errs.max():.2f} px.")


def check_recalibrated(rms_before, rms_after):
    if rms_after >= rms_before:
        return _hint("The RMS should drop after removing the worst view(s). Did you remove them from BOTH lists?")
    if rms_after > 0.7:
        return _hint(f"Better ({rms_after:.2f} px), but drop the views above ~1.5 px and recalibrate.")
    return _ok(f"RMS dropped from {rms_before:.2f} to {rms_after:.2f} px by removing bad views.")


# ============================================================================== 6D · road camera & perspective
def check_road_calibration(mtx, dist):
    K, D = reference_road()
    if abs(mtx[0, 0] - K[0, 0]) > 40:
        return _hint("fx is off: this board is 9 × 6, and two images are 1281 × 721. Resize them to 1280 × 720 (or skip them).")
    return _ok(f"Road camera calibrated: fx ≈ {mtx[0, 0]:.0f} px, k1 ≈ {np.ravel(dist)[0]:.2f}.")


def check_corners_unwarp(fn):
    K, D = reference_gopro()
    img = cv2.imread(fetch("data/calibration_wide/GOPR0062.jpg"))
    try:
        warped, M = fn(img.copy(), 8, 6, K, D)
    except Exception as e:  # noqa: BLE001
        return _hint(f"corners_unwarp raised {type(e).__name__}: {e}. Tip: corners.reshape(-1, 2) works in OpenCV 4 and 5.")
    if M is None:
        return _hint("M is None: were the corners found? Undistort first, then search in the grayscale undistorted image.")
    und = cv2.undistort(img, K, D, None, K)
    ok, c = find_corners(cv2.cvtColor(und, cv2.COLOR_BGR2GRAY), (8, 6), subpix=False)
    c = c.reshape(-1, 2)
    p = cv2.perspectiveTransform(c[None].astype(np.float64), np.asarray(M, float))[0]
    g = p.reshape(6, 8, 2)
    dx = np.diff(g[:, :, 0], axis=1); dy = np.diff(g[:, :, 1], axis=0)
    rowsflat = np.abs(np.diff(g[:, :, 1], axis=1)).max(); colsflat = np.abs(np.diff(g[:, :, 0], axis=0)).max()
    if (dx < 0).all() or (dy < 0).all():
        return _hint("The board is mirrored or upside down: src and dst points must be listed in the same order.")
    if rowsflat > 6 or colsflat > 6 or dx.std() > 6 or dy.std() > 6:
        return _hint("After warping, the corners should form a regular grid. Did you undistort before finding the corners?")
    return _ok("corners_unwarp works: a regular, top-down chessboard.")


def check_birdseye(M):
    """Lane lines of straight_lines1.jpg must be vertical after warping with M."""
    left = np.float64([[[255, 685], [592, 452]]]); right = np.float64([[[1055, 685], [690, 452]]])
    M = np.asarray(M, float)
    l = cv2.perspectiveTransform(left, M)[0]; r = cv2.perspectiveTransform(right, M)[0]
    tilt = max(abs(l[0, 0] - l[1, 0]), abs(r[0, 0] - r[1, 0]))
    width_b, width_t = r[0, 0] - l[0, 0], r[1, 0] - l[1, 0]
    if width_b < 0:
        return _hint("Left and right are swapped: check the order of your src and dst points.")
    if tilt > 25:
        return _hint(f"The lane lines are still slanted by {tilt:.0f} px. Move the two top source points along the lane lines.")
    if abs(width_b - width_t) > 25:
        return _hint("The lines are not parallel yet: the lane should keep a constant width in the bird's-eye view.")
    return _ok(f"Bird's-eye view is good: both lane lines are vertical and {width_b:.0f} px apart.")


def check_curvature(R_left, R_right):
    for R in (R_left, R_right):
        if not np.isfinite(R) or R <= 0:
            return _hint("Radius must be positive and finite. Use abs(2A) in the denominator.")
    if min(R_left, R_right) < 100:
        return _hint("Radius below 100 m on a highway? Convert pixels to metres BEFORE fitting (ym = 30/720, xm = 3.7/700).")
    if max(R_left, R_right) > 10000:
        return _hint("A radius above 10 km means a nearly straight line: did you fit the curved test2.jpg frame?")
    return _ok(f"Curvature radii {R_left:.0f} m and {R_right:.0f} m: the right order of magnitude for this highway curve (~1 km).")


# ============================================================================== 6E · ChArUco & fisheye
def check_charuco(K, K_true, rms):
    K, K_true = np.asarray(K), np.asarray(K_true)
    ef = abs(K[0, 0] - K_true[0, 0]) / K_true[0, 0]
    ec = np.hypot(K[0, 2] - K_true[0, 2], K[1, 2] - K_true[1, 2])
    if rms > 1.0:
        return _hint(f"RMS {rms:.2f} px is high for synthetic images. Did you pass obj/img points from matchImagePoints?")
    if ef > 0.02 or ec > 10:
        return _hint(f"fx is off by {100 * ef:.1f}% and the principal point by {ec:.1f} px. More and more varied views help.")
    return _ok(f"Recovered the hidden camera: fx error {100 * ef:.2f} %, principal point error {ec:.2f} px.")


def check_fisheye(K, D, K_true, D_true):
    ef = abs(K[0, 0] - K_true[0, 0]) / K_true[0, 0]
    if ef > 0.02:
        return _hint(f"fx is off by {100 * ef:.1f}%. Points must be float64 with shape (1, N, 3) and (1, N, 2).")
    return _ok(f"Fisheye calibration recovered fx within {100 * ef:.2f} %. D = {np.round(np.ravel(D), 3)}")


# ============================================================================== 6F · bug hunt
_bugs_fixed = set()


def _bug(n, ok, good, hint):
    if ok:
        _bugs_fixed.add(n)
        _ok(f"Bug {n} fixed: {good}   [{len(_bugs_fixed)}/8]")
        return True
    return _hint(f"Bug {n}: {hint}")


def check_bug1(ret):
    return _bug(1, ret is True or ret == 1, "patternSize counts INNER corners.", "findChessboardCorners still returns False. Count the corners again.")


def check_bug2(mtx):
    ok = mtx is not None and 600 < mtx[0, 2] < 700 and 450 < mtx[1, 2] < 550
    return _bug(2, ok, "imageSize is (width, height).", "The principal point is swapped/odd: what does gray.shape contain, (h, w) or (w, h)?")


def check_bug3(rms):
    return _bug(3, rms is not None and rms < 1.0, "objp and the corner order match.", "RMS is huge: the object points are listed in a different order from the detected corners.")


def check_bug4(n_used, size):
    return _bug(4, n_used in (15, 17) and tuple(size) == (1280, 720), "every image has the same size.", "Two images are 1281 × 721. Resize (or skip) them so every view has the same size.")


def check_bug5(corner):
    c = np.asarray(corner, float).ravel()
    return _bug(5, c.shape == (2,), "corners.reshape(-1, 2) works in OpenCV 4 and 5.", "corners[0][0] is a single number in OpenCV 5 (corners are (N, 2)). You need an (x, y) pair.")


def check_bug6(warped_gray_mean_left, warped_gray_mean_right):
    return _bug(6, warped_gray_mean_left < warped_gray_mean_right, "src and dst are in the same order.", "The warped board is mirrored: list src and dst points in the same order (TL, TR, BR, BL).")


def check_bug7(K_small):
    K, _ = reference_gopro()
    ok = abs(K_small[0, 0] - K[0, 0] / 2) < 1 and abs(K_small[0, 2] - K[0, 2] / 2) < 1
    return _bug(7, ok, "K is scaled with the image.", "You resized the image by 0.5 but kept K. fx, fy, cx, cy must be scaled too (dist stays the same).")


def check_bug8(rms):
    return _bug(8, rms is not None and rms < 1.0, "fisheye points are float64, shape (1, N, 3).", "cv2.fisheye.calibrate needs float64 arrays shaped (1, N, 3) and (1, N, 2) (OpenCV 5 rejects (N, 1, 3)).")


def bug_score():
    print(f"🐞 Bugs fixed: {len(_bugs_fixed)}/8 " + ("🎉 all done!" if len(_bugs_fixed) == 8 else ""))


# ============================================================================== 6G · stereo
def check_stereo(rms, T, R):
    T = np.ravel(T)
    if rms > 1.0:
        return _hint(f"Stereo RMS {rms:.2f} px is high. Only use pairs where the board was found in BOTH images.")
    if not (3.0 < np.linalg.norm(T) < 3.7):
        return _hint(f"Baseline |T| = {np.linalg.norm(T):.2f} squares looks wrong (expect ≈ 3.3).")
    if T[0] > 0:
        return _hint("T should point along −x: it maps left-camera coordinates to the right camera.")
    ang = np.degrees(np.linalg.norm(cv2.Rodrigues(np.asarray(R, float))[0]))
    return _ok(f"Stereo calibration: RMS {rms:.2f} px, baseline {np.linalg.norm(T):.2f} squares, cameras rotated {ang:.1f}° apart.")


def check_rectified(rows_left, rows_right):
    d = np.abs(np.asarray(rows_left, float) - np.asarray(rows_right, float))
    if d.mean() > 1.0:
        return _hint(f"Matching corners differ by {d.mean():.1f} rows on average: rectification is not applied correctly.")
    return _ok(f"Rectified: matching corners are on the same row (mean |Δy| = {d.mean():.2f} px).")


# ============================================================================== 6H · your own camera
def check_own_calibration(rms, K, size, n_views):
    w, h = size
    if n_views < 15:
        _hint(f"Only {n_views} usable views: take 20–30 for a reliable result.")
    if rms > 1.0:
        return _hint(f"RMS {rms:.2f} px: re-shoot blurry views, check the board is flat and the square size is right.")
    if abs(K[0, 2] - w / 2) > 0.1 * w or abs(K[1, 2] - h / 2) > 0.1 * h:
        return _hint("The principal point is far from the image centre: add views near the image corners.")
    hfov = 2 * np.degrees(np.arctan(w / 2 / K[0, 0]))
    return _ok(f"Your camera: RMS {rms:.2f} px, fx = {K[0, 0]:.0f} px, horizontal FOV ≈ {hfov:.0f}°. Save camera.yaml!")


# ============================================================================== video labs (6I-6M)
def check_good_frame_filter(kept, n_target=20):
    if len(kept) < n_target:
        return _hint(f"Only {len(kept)} frames kept: lower the novelty threshold or record more frames.")
    if len(kept) > n_target:
        return _hint(f"{len(kept)} frames kept: stop as soon as you have {n_target} good frames.")
    return _ok(f"{n_target} good, different frames collected, just like the Pi script does.")


def check_marker_shift(shift_mm, true_mm=60.0):
    if not np.isfinite(shift_mm):
        return _hint("The shift is not a number: was the marker detected in both images?")
    err = abs(shift_mm - true_mm)
    if err > 0.15 * true_mm:
        return _hint(f"You measured {shift_mm:.1f} mm for a {true_mm:.0f} mm move. Is the marker size in mm, and did you use the calibrated K and dist?")
    return _ok(f"The marker moved {shift_mm:.1f} mm (true {true_mm:.0f} mm): the calibration measures real distances.")


def check_total_error(total_error, rms):
    if not (0 < total_error < rms):
        return _hint("Nicolai's 'total error' = mean over images of (L2 norm of all residuals / number of corners). It is always smaller than the RMS.")
    return _ok(f"Total error {total_error:.4f} vs RMS {rms:.3f} px: two different numbers for the same fit. Always say which one you report!")


def check_blur_scores(scores, files):
    scores = np.asarray(scores, float)
    if len(scores) != len(files):
        return _hint("One blur score per image, please.")
    if scores.std() == 0:
        return _hint("All scores are equal: use the variance of cv2.Laplacian(gray, cv2.CV_64F).")
    return _ok(f"Blur scores computed: sharpest {scores.max():.0f}, blurriest {scores.min():.0f}.")


def check_outlier_removal(rms_before, rms_after, n_removed):
    if n_removed == 0:
        return _hint("Nothing was removed: drop the views whose error is far above the median (e.g. > 2 × median).")
    if rms_after >= rms_before:
        return _hint("RMS did not improve: did you recalibrate after removing the views?")
    return _ok(f"Removed {n_removed} outlier view(s): RMS {rms_before:.3f} → {rms_after:.3f} px.")


def check_homography(H, H_ref):
    H = np.asarray(H, float); H = H / H[2, 2]; H_ref = np.asarray(H_ref, float) / H_ref[2, 2]
    if np.abs(H - H_ref).max() > 1e-3 * np.abs(H_ref).max():
        return _hint("Your homography differs from cv2.findHomography. Use the last right-singular vector of A (Vt[-1]) and reshape it to 3 × 3.")
    return _ok("Your DLT homography matches cv2.findHomography.")


def check_zhang_K(K, K_true, tol=0.02):
    K = np.asarray(K, float)
    if K.shape != (3, 3) or not np.isfinite(K).all():
        return _hint("K must be a finite 3 × 3 matrix.")
    if K[0, 0] < 0:
        return _hint("fx is negative: B is only known up to sign. Flip b if B[0, 0] < 0 before the Cholesky step.")
    e = abs(K[0, 0] - K_true[0, 0]) / K_true[0, 0]
    ec = np.hypot(K[0, 2] - K_true[0, 2], K[1, 2] - K_true[1, 2])
    if e > tol or ec > 0.02 * K_true[0, 2]:
        return _hint(f"fx off by {100 * e:.1f}%, principal point by {ec:.1f} px. Check the v_ij vectors and the two constraints per view.")
    return _ok(f"Zhang's closed form works: fx error {100 * e:.2f} %, principal point error {ec:.2f} px.")


def check_dlt(P, P_true):
    P = np.asarray(P, float); P = P / np.linalg.norm(P); Pt = np.asarray(P_true, float); Pt = Pt / np.linalg.norm(Pt)
    if min(np.abs(P - Pt).max(), np.abs(P + Pt).max()) > 1e-6:
        return _hint("P does not match. Each point gives TWO rows of A; take Vt[-1] and reshape to 3 × 4.")
    return _ok("DLT recovered the 3 × 4 projection matrix (11 degrees of freedom) from 6+ known points.")
