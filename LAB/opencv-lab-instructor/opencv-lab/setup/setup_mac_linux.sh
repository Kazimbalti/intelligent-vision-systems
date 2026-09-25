#!/usr/bin/env bash
# ============================================================
#  OpenCV lab - one-command setup for macOS and Linux
#  From the lab folder run:   bash setup/setup_mac_linux.sh
#  Use a specific Python:     PYTHON=python3.12 bash setup/setup_mac_linux.sh
# ============================================================
set -e
cd "$(dirname "$0")/.."
PY="${PYTHON:-python3}"

echo "[1/5] Creating the virtual environment in .venv with $($PY --version) ..."
if ! $PY -m venv .venv; then
    echo "ERROR: could not create the venv."
    echo "  Ubuntu/Debian:  sudo apt install python3-venv python3-pip"
    echo "  macOS:          install Python 3.12 from python.org or: brew install python@3.12"
    exit 1
fi
echo "[2/5] Activating it ..."
source .venv/bin/activate
echo "[3/5] Upgrading pip ..."
python -m pip install --upgrade pip
echo "[4/5] Installing the libraries (this can take a few minutes) ..."
pip install -r requirements.txt
echo "[5/5] Creating sample data and checking everything ..."
python make_samples.py
python check_env.py || true
echo
echo "Finished. Next time, open a terminal in this folder and run:"
echo "    source .venv/bin/activate"
