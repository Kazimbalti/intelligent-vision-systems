# OpenCV Lab: instructor notes

This folder is the **instructor package**: the same as the student package plus
`solutions/` (complete, runnable code) and this file. Give students
`opencv-lab-student.zip` only.

## Before the lab
1. Share `opencv-lab-student.zip` and the lab manual at least two days ahead.
2. Ask students to run the setup script at home and bring a screenshot of `check_env.py`
   showing every line OK. This saves the first 30 minutes of the lab.
3. On lab PCs, run `setup/setup_windows.bat` once per machine, or build one `.venv`
   per student account.
4. Keep a USB drive with the zip and the Python 3.12 installer for students without internet.

## Suggested 3-hour plan
| Time | Activity |
|---|---|
| 0:00–0:20 | Setup check: everyone runs `check_env.py`; fix FAILs with the troubleshooting table |
| 0:20–0:50 | Exercises 01–04 (I/O, video, drawing, pixels) |
| 0:50–1:30 | Exercises 05–07 (arithmetic, contours, features) |
| 1:30–1:40 | Break |
| 1:40–2:15 | Exercises 08–10 (HSV, thresholds, background subtraction) |
| 2:15–2:50 | Projects: P1 + P2 for everyone, P3 / P4 for fast students |
| 2:50–3:00 | Demo two student trackers; assign unfinished projects as homework |

## Answer key: expected output of every checkpoint
Tested on OpenCV 5.0.0 (Python 3.11 and 3.12) and 4.14.0 (Python 3.10); both give identical numbers.

| Exercise | Expected output |
|---|---|
| ex01 | `shape: (400, 640, 3) dtype: uint8`; grayscale `(400, 640)`; wrong path returns `None`; sizes ≈ PNG 38 KB, JPEG q90 15 KB, q20 6 KB |
| ex02 | `size = 640 x 360, fps = 30.0` for the sample video; 360 frames written |
| ex03 | `output/drawing.png` matches the lecture slide; yellow "sun 0.97" box around the sun |
| ex04 | pixel [100, 200] `B=120 G=66 R=131`; sun crop `(130, 130, 3)`; top-left `[0 0 0]`, top-right unchanged |
| ex05 | `250 + 10 -> numpy: 4, cv2.add: 255`; `10 - 250 -> numpy: 16, cv2.subtract: 0`; NumPy brightening turns the sky cyan |
| ex06 | `RETR_EXTERNAL: 11`, `RETR_TREE: 12`; points NONE 2604 vs SIMPLE 818 |
| ex07 | 6 objects: triangle, rectangle, square, pentagon, circle, circle (ring); triangle area 9100, square 12100 |
| ex08 | sunlit HSV `[60 201 220]`, shaded `[60 201 99]` (only V changes); ball centre `(464, 150)` |
| ex09 | Otsu `T = 115`; global and Otsu lose the right side; adaptive keeps all 9 lines |
| ex10 | red boxes on 3 cars and the pedestrian after ≈1 s; shadows grey in the raw mask |
| P2 | `9 coins: 5 large, 4 small` (large ≈ 5 500 px, small ≈ 2 800 px) |
| P3 | the box and trail follow the green ball; the red, blue and yellow objects are ignored |
| P4 | `REC` appears and `output/alarm_*.mp4` is written |

## Discussion questions (with answers)
1. *Why does `cv2.imread` return `None` instead of raising?* It is a C++ API wrapped for Python;
   failure is signalled by an empty matrix. Always check.
2. *Why is the VideoWriter size `(w, h)` but `img.shape` `(h, w, c)`?* OpenCV sizes are
   width-first (x, y); NumPy shapes are rows-first.
3. *Why does the NumPy `+ 80` turn the sky cyan?* Red values above 175 wrap past 255 to small
   numbers, so red disappears and blue + green remain.
4. *Why HSV and not BGR for the tracker?* Shadow changes V, not H: see ex08's two pixels.
5. *When does adaptive thresholding fail?* Large uniform dark objects bigger than the block
   size; choose the block size larger than the objects' stroke width.
6. *Why threshold the MOG2 mask at 200?* Shadow pixels are marked 127; objects are 255.

## Grading rubric (projects, 20 marks)
| Criterion | Marks |
|---|---|
| Runs without errors from a fresh `.venv` | 4 |
| Correct result (count, tracking, recording) | 6 |
| Uses the right blocks (no hard-coded answers) | 4 |
| Clear code: names, comments, constants at the top | 3 |
| Short reflection: what failed and how you fixed it | 3 |

## Common problems seen in labs
* **`ModuleNotFoundError: cv2`**: the venv is not active (no `(.venv)` in the prompt), or VS Code
  uses another interpreter. Fix: `Python: Select Interpreter` → `.venv`.
* **Windows PowerShell refuses `Activate.ps1`**: run
  `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, or use Command Prompt and `activate.bat`.
* **Camera opens but frames are black / fail on macOS**: allow camera access for Terminal or
  VS Code in System Settings → Privacy & Security → Camera, then restart the terminal.
* **Two OpenCV packages installed**: `pip list | findstr opencv` (Windows) or
  `pip list | grep opencv`: uninstall all, reinstall only `opencv-python`.
* **`libGL.so.1` missing on Linux**: `sudo apt install libgl1`.
