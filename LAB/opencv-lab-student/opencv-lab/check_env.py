"""
check_env.py - checks that your Python environment is ready for the lab.

Run:   python check_env.py            (quick checks)
       python check_env.py --camera   (also tries to open your webcam)

Every line should say OK. Show the output to your instructor if one says FAIL.
"""
import argparse
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
results = []


def check(name, fn):
    try:
        detail = fn()
        results.append(True)
        print(f"  OK    {name:28s} {detail or ''}")
    except Exception as exc:  # noqa: BLE001 - we want to report every failure
        results.append(False)
        print(f"  FAIL  {name:28s} {exc}")


def python_version():
    v = sys.version_info
    if v < (3, 9):
        raise RuntimeError(f"Python {v.major}.{v.minor} is too old; install Python 3.10 - 3.12")
    return f"{platform.python_version()} ({platform.system()})"


def inside_venv():
    if sys.prefix == sys.base_prefix:
        raise RuntimeError("not inside a virtual environment - activate .venv first")
    return sys.prefix


def numpy_ok():
    import numpy as np
    return np.__version__


def opencv_ok():
    import cv2
    return cv2.__version__


def matplotlib_ok():
    import matplotlib
    return matplotlib.__version__


def jupyter_ok():
    import jupyterlab
    return jupyterlab.__version__


def samples_ok():
    needed = ["scene.jpg", "blend_a.png", "blend_b.png", "gradient.png", "shapes.png",
              "coins.png", "balls.png", "document.png", "ball.mp4", "traffic.mp4"]
    missing = [n for n in needed if not (ROOT / "data" / n).exists()]
    if missing:
        raise RuntimeError(f"missing {missing} - run: python make_samples.py")
    return f"{len(needed)} files"


def write_image():
    import cv2
    import numpy as np
    (ROOT / "output").mkdir(exist_ok=True)
    path = ROOT / "output" / "_check.png"
    if not cv2.imwrite(str(path), np.zeros((10, 10, 3), np.uint8)):
        raise RuntimeError("cv2.imwrite returned False")
    path.unlink()
    return "imwrite works"


def read_video():
    import cv2
    cap = cv2.VideoCapture(str(ROOT / "data" / "traffic.mp4"))
    ok, frame = cap.read()
    cap.release()
    if not ok:
        raise RuntimeError("cannot decode data/traffic.mp4")
    return f"decoded a {frame.shape[1]}x{frame.shape[0]} frame"


def gui_ok():
    import os
    if os.environ.get("LAB_HEADLESS") == "1":
        return "skipped (LAB_HEADLESS=1)"
    if platform.system() == "Linux" and not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
        raise RuntimeError("no display found - run on a desktop session, or use LAB_HEADLESS=1")
    import cv2
    import numpy as np
    cv2.namedWindow("check", cv2.WINDOW_NORMAL)
    cv2.imshow("check", np.zeros((50, 50, 3), np.uint8))
    cv2.waitKey(300)
    cv2.destroyAllWindows()
    return "windows can open"


def camera_ok():
    import cv2
    cap = cv2.VideoCapture(0)
    ok, frame = cap.read() if cap.isOpened() else (False, None)
    cap.release()
    if not ok:
        raise RuntimeError("no frame from camera 0 (check permissions, or close other apps using it)")
    return f"camera gives {frame.shape[1]}x{frame.shape[0]}"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--camera", action="store_true", help="also test the webcam")
    ap.add_argument("--no-gui", action="store_true", help="skip the window test")
    args = ap.parse_args()

    print("\nOpenCV lab - environment check\n")
    check("Python version", python_version)
    check("Virtual environment", inside_venv)
    check("NumPy", numpy_ok)
    check("OpenCV (cv2)", opencv_ok)
    check("Matplotlib", matplotlib_ok)
    check("JupyterLab", jupyter_ok)
    check("Sample data", samples_ok)
    check("Write an image", write_image)
    check("Read a video", read_video)
    if not args.no_gui:
        check("Open a window", gui_ok)
    if args.camera:
        check("Webcam", camera_ok)

    passed = sum(results)
    print(f"\n{passed}/{len(results)} checks passed.")
    if passed == len(results):
        print("You are ready for the lab.\n")
    else:
        print("Fix the FAIL lines (see Troubleshooting in the lab manual).\n")
        sys.exit(1)
