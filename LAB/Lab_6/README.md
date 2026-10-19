# Lab 6 — Camera Calibration

**Intelligent Vision Systems · University of Lahore · Dr. Muhammad Kazim**

Hands-on companion to **Lecture 6 — Camera Calibration**
([slides](https://kazimbalti.github.io/intelligent-vision-systems/lectures/06_Camera_Calibration.html)).
You build the camera model yourself, calibrate a wide-angle GoPro, a car dash-cam, a ChArUco/fisheye camera with a known
ground truth and a stereo pair, and finally **your own** Raspberry Pi or USB camera.

| Part | Notebook | Lecture section | What you build |
|---|---|---|---|
| 6A | `01-pinhole-and-distortion.ipynb` | 2–3 · Pinhole model, distortion | Project points by hand, K from a datasheet (Pi Camera v2), OpenCV's distortion model in NumPy |
| 6B | `02-finding-corners.ipynb` | 5 · Finding corners | Count corners, `findChessboardCorners`, object points with `np.mgrid`, `cornerSubPix` vs the `SB` detector |
| 6C | `03-calibrate-and-undistort.ipynb` | 5 · Calibrate & undistort | `calibrateCamera`, the Udacity `cal_undistort` quiz, per-view reprojection error, dropping bad views, uncertainties, `alpha`, rational model, fast `remap`, YAML |
| 6D | `04-road-camera-birdseye.ipynb` | 7 · Perspective transform | Calibrate a dash-cam, the Udacity `corners_unwarp` quiz, bird's-eye view, lane curvature in metres |
| 6E | `05-charuco-and-fisheye.ipynb` | 6 · ChArUco & fisheye | Ray-traced views from a hidden camera: ChArUco calibration (partial views), a 190° fisheye with `cv2.fisheye` |
| 6F | `06-bug-hunt.ipynb` | Common pitfalls | **Bug hunt (pairs):** 8 planted calibration bugs (incl. OpenCV 4 → 5 changes), each with its own check and a scoreboard |
| 6G | `07-stereo-calibration.ipynb` | 6 · Stereo | `stereoCalibrate`, epipolar check, `stereoRectify` + `remap`, a first disparity map |
| 6H | `08-calibrate-your-camera.ipynb` | 6 · Your own camera | Capture with Picamera2 or a webcam, calibrate, check coverage, save `camera.yaml`, measure distance with `solvePnP` |

### Live webcam demo (Lecture 6, Level 5)

* **In the browser:** [Webcam Calibration Studio](https://kazimbalti.github.io/intelligent-vision-systems/lectures/06_webcam_calibration_studio.html) runs the real OpenCV-Python 4.10 (`cv2`, via WebAssembly) on your webcam: detect the 9 × 6 board, auto-capture views, calibrate, undistort live, measure distance, download `camera.yaml`. No install; the video stays on your computer. No webcam? It has 20 demo images.
* **Offline:** `python webcam_calibration_studio.py --board 9x6 --mm 25` (keys: SPACE capture, A auto, C calibrate, U undistort, M measure, S save).
* The pattern: [`pattern_9x6.png`](../../lectures/assets/06_camera_calibration/pattern_9x6.png): print at 100 % (or [show it on a phone](https://kazimbalti.github.io/intelligent-vision-systems/lectures/06_pattern_fullscreen.html)), measure one square.

### Video labs (one per recommended video — see the [tutorial page](https://kazimbalti.github.io/intelligent-vision-systems/tutorials/08_camera_calibration_videos.html))

| Part | Notebook | Video | What you build |
|---|---|---|---|
| 6I | `09-pi-camera-in-15-minutes.ipynb` | The Drone Dojo — *Calibrate OpenCV Camera In Under 15 Minutes* | Auto-capture 20 good frames at 640 × 480 (`pi_calibrate_20.py`), calibrate, ArUco + ruler test (`aruco_pose_test.py`) |
| 6J | `10-nicolai-get-images-and-calibrate.ipynb` | Nicolai Nielsen — *< 5 minutes* and *Python script* | `get_images.py`, the script line by line, pickle, undistort vs remap, total error vs RMS |
| 6K | `11-kevin-wood-calibration-app.ipynb` | Kevin Wood — *Explained* and *OpenCV Python* | JSON output, P = K[R\|t] by hand, straight-line test, calibration doctor |
| 6L | `12-charuco-webcam-pipeline.ipynb` | Nicolai Nielsen — *ChArUco boards* | 18 × 11 ChArUco, per-image errors, outlier removal, JSON, 3-D board view |
| 6M | `13-zhang-method-from-scratch.ipynb` | Cyrill Stachniss — *Intrinsics/extrinsics*, *Intrinsic calibration*, *Zhang's method* | DLT, homographies, Zhang's closed form in NumPy |

Scripts for 6H (and for your project): `capture_calib.py` (Picamera2 timer capture or a webcam preview with SPACE to save)
and `calibrate.py` (pinhole, rational or fisheye model; per-view errors; drop bad views; writes `camera.yaml`; optional
undistorted copies). Run either with `--help`.

## Auto-checks

After each exercise a ✅ cell (from `lab6_checks.py`, downloaded automatically) says whether your result is good enough or
prints a 💡 hint — never the answer. 6E checks your calibration against the hidden camera's true K.

## OpenCV 5 notes (all handled in the notebooks)

* `findChessboardCorners` returns corners of shape **(N, 2)** (OpenCV 4: (N, 1, 2)). Use `corners.reshape(-1, 2)`.
* `cv2.fisheye` flags moved to `cv2.CALIB_*` with new values; `cv2.fisheye.calibrate` wants points shaped **(1, N, 3)**
  float64. `lab6_checks.fisheye_flags()` picks the right flags for your version.
* ChArUco: `cv2.aruco.CharucoDetector` + `board.matchImagePoints` (the old `calibrateCameraCharuco` is gone since 4.7).

## Run it

**Google Colab (6A–6G):** open a notebook from the
[Labs page](https://kazimbalti.github.io/intelligent-vision-systems/labs.html#lab-6-calibration) and run all cells; each
notebook downloads the images it needs. **6H must run on the machine the camera is attached to.**

**Locally / Raspberry Pi 5:**

```bash
python -m venv --system-site-packages .venv && source .venv/bin/activate   # system packages: Picamera2 on the Pi
pip install -r requirements.txt
jupyter lab
```

## Deliverables

* **6A–6E, 6G:** each notebook ends with **"Your turn"** tasks. Submit the notebooks with code, outputs and short answers.
* **6F:** in-class bug hunt — show the TA your 8/8 scoreboard.
* **6H:** `camera.yaml` for your camera, the per-view error and coverage plots, a raw/undistorted pair and the answers in
  the notebook. Keep `camera.yaml`: Lab 9 (measuring objects) and your project need it.

## Data and credits

* `data/calibration_wide/` — GoPro chessboard images (8 × 6) and `test_image.jpg` from
  [udacity/CarND-Camera-Calibration](https://github.com/udacity/CarND-Camera-Calibration) (MIT licence).
* `data/camera_cal/`, `data/road/` — dash-cam calibration (9 × 6) and road images from
  [udacity/CarND-Advanced-Lane-Lines](https://github.com/udacity/CarND-Advanced-Lane-Lines) (MIT licence).
* `data/stereo/` — `left01…14`, `right01…14` (9 × 6) from the [OpenCV samples](https://github.com/opencv/opencv/tree/4.x/samples/data) (Apache 2.0).
* Capture/calibration scripts inspired by [Petros626/Camera-Calibration-with-PiCamera2-OpenCV](https://github.com/Petros626/Camera-Calibration-with-PiCamera2-OpenCV),
  [niconielsen32/camera-calibration](https://github.com/niconielsen32/camera-calibration),
  [nuwandda/Checkerboard-Calibration](https://github.com/nuwandda/Checkerboard-Calibration) and
  [ibois-epfl/rgb-camera-calibration](https://github.com/ibois-epfl/rgb-camera-calibration).
* More stereo pairs: [Kaggle — Chessboard pictures for stereo camera calibration](https://www.kaggle.com/datasets/danielwe14/stereocamera-chessboard-pictures).
