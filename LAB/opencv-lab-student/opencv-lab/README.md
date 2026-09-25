# OpenCV Lab: foundations of image processing

A hands-on lab for the *Introduction to OpenCV* lecture: ten exercises (one per lecture
block) and four mini-projects. Everything runs inside a Python **virtual environment**,
so nothing is installed system-wide and every student has the same setup.

## 1. Install Python (once)
* **Windows**: install Python 3.11 or 3.12 from python.org. Tick **"Add python.exe to PATH"**.
* **macOS**: install Python 3.12 from python.org (or `brew install python@3.12`).
* **Ubuntu/Debian**: `sudo apt install python3 python3-venv python3-pip`

## 2. Create the environment and install everything
Open a terminal **in this folder**, then:

| | Windows (Command Prompt) | macOS / Linux |
|---|---|---|
| One-click setup | `setup\setup_windows.bat` | `bash setup/setup_mac_linux.sh` |

Or step by step:

```bash
python -m venv .venv                 # Windows: py -3.12 -m venv .venv  ·  macOS/Linux: python3 -m venv .venv
.venv\Scripts\activate               # Windows (PowerShell: .venv\Scripts\Activate.ps1)
source .venv/bin/activate            # macOS / Linux
python -m pip install --upgrade pip
pip install -r requirements.txt
python make_samples.py               # creates the images and videos in data/
python check_env.py                  # every line should say OK
```

Your prompt now starts with `(.venv)`. Activate it again every time you open a new terminal.
Leave it with `deactivate`.

## 3. Work through the lab
```bash
python exercises/ex01_load_save_display.py
python exercises/ex02_video.py            # webcam, or falls back to data/traffic.mp4
...
python projects/p3_color_tracker.py
python tools/hsv_tuner.py data/balls.png  # find HSV ranges with sliders
jupyter lab notebooks/00_playground.ipynb # optional notebook
```
Each exercise has `# TODO` lines. Fill them in, run the file, and compare with the
**Checkpoint** at the top of the file. Results are saved in `output/`.

## Folder layout
```
opencv-lab/
├── setup/            one-click setup scripts (Windows / macOS / Linux)
├── requirements.txt  the libraries to install
├── check_env.py      checks your environment
├── make_samples.py   generates the sample images and videos
├── labutils.py       small helpers used by every exercise (do not edit)
├── data/             sample images and videos
├── exercises/        ex01 ... ex10  (fill in the TODOs)
├── projects/         p1 ... p4 mini-projects
├── tools/            hsv_tuner.py
├── notebooks/        00_playground.ipynb
└── output/           everything your programs save
```

## No webcam? No display?
* Every camera exercise falls back to the sample videos automatically.
* On a computer without a screen, run with `LAB_HEADLESS=1` and images are saved to `output/`
  instead of shown (`set LAB_HEADLESS=1` on Windows).

See the lab manual for the full step-by-step instructions and troubleshooting.
