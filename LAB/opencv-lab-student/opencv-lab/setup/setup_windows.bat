@echo off
REM ============================================================
REM  OpenCV lab - one-click setup for Windows
REM  Double-click this file, or run it from the lab folder:
REM      setup\setup_windows.bat
REM ============================================================
cd /d "%~dp0\.."
echo.
echo [1/5] Creating the virtual environment in .venv ...
py -3 -m venv .venv 2>nul || python -m venv .venv
if not exist ".venv\Scripts\python.exe" (
    echo ERROR: Python was not found. Install Python 3.11 or 3.12 from python.org
    echo        and tick "Add python.exe to PATH" during installation.
    pause
    exit /b 1
)
echo [2/5] Activating it ...
call .venv\Scripts\activate.bat
echo [3/5] Upgrading pip ...
python -m pip install --upgrade pip
echo [4/5] Installing the libraries (this can take a few minutes) ...
pip install -r requirements.txt || (echo ERROR: pip install failed & pause & exit /b 1)
echo [5/5] Creating sample data and checking everything ...
python make_samples.py
python check_env.py
echo.
echo Finished. Next time, open a terminal in this folder and run:
echo     .venv\Scripts\activate
pause
