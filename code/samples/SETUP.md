# SETUP — Environment for every tier

Do this before Week 1. Budget one lab session. Each tier is independent; you can
set up the Pi/Hailo tier and the ESP32 tier in parallel across two benches.

---

## 0. Accounts to create (free)

- **Hailo Developer Zone** — required to download the Dataflow Compiler (DFC) and
  some model-zoo assets: https://hailo.ai/developer-zone/
- **Edge Impulse** — for the ESP32-CAM TinyML week: https://edgeimpulse.com/
- **Ultralytics / Google Colab** — for training (Colab gives a free GPU):
  https://colab.research.google.com/
- **Roboflow (optional)** — dataset labelling/hosting: https://roboflow.com/

---

## 1. Raspberry Pi 5 (host CPU tier)

Use a fresh install of **Raspberry Pi OS (64-bit, Bookworm or later; Trixie
required for AI HAT+ 2)**.

```bash
sudo apt update && sudo apt full-upgrade -y
sudo rpi-eeprom-update -a          # update firmware
sudo reboot
```

Python CV stack (system picamera2 is already present on Pi OS):

```bash
sudo apt install -y python3-opencv python3-picamera2 python3-pip git
# For training-tier tools you run ON the Pi (optional), prefer a venv:
python3 -m venv ~/cvenv --system-site-packages
source ~/cvenv/bin/activate
pip install -r requirements.txt
```

Test the Pi camera:

```bash
rpicam-hello -t 5000            # 5-second preview; confirms libcamera sees the cam
```

---

## 2. Hailo AI HAT (NPU tier)

Physical: power off, fit the HAT on the Pi 5 PCIe connector, add the active
cooler, reboot. PCIe is auto-enabled on current OS; if not, add
`dtparam=pciex1` to `/boot/firmware/config.txt`.

Install the Hailo stack (this pulls HailoRT, the Python API, and camera
integration):

```bash
sudo apt install -y hailo-all
sudo reboot
hailortcli fw-control identify      # should print your Hailo device + FW version
```

Get the runnable examples and pre-compiled models:

```bash
# Current, maintained examples:
git clone https://github.com/hailo-ai/hailo-apps.git
# Classic RPi5 examples (still a useful reference):
git clone https://github.com/hailo-ai/hailo-rpi5-examples.git
cd hailo-rpi5-examples && source setup_env.sh && ./download_resources.sh
```

- Pre-compiled `.hef` models: **Hailo Model Explorer / Model Zoo**
  (pick the file matching your chip — a Hailo-8L build will not run on Hailo-8/10H).
- Official Pi + Hailo docs: https://www.raspberrypi.com/documentation/computers/ai.html
- **Known aarch64 gotcha:** GStreamer pipelines can fail with a `libgomp` TLS
  error. Fix — add to `~/.bashrc` then reboot:
  ```bash
  export LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libgomp.so.1
  ```

> **Which HAT do you have?** The vision workflow (this course) is the same for
> AI HAT+ (Hailo-8/8L) and AI HAT+ 2 (Hailo-10H), but model files must be
> compiled for the specific NPU, and the two software packages cannot coexist.
> Pick one chip target and stick to it for the whole course.

---

## 3. Training tier (laptop GPU or Colab)

Only needed in Weeks 6, 7, 9. Cleanest on Colab (no local GPU required).

```bash
pip install ultralytics onnx onnxruntime opencv-python
# Quick sanity check:
yolo predict model=yolov8n.pt source='https://ultralytics.com/images/bus.jpg'
```

The **Hailo Dataflow Compiler** (ONNX → `.hef`) is best run in its own Docker
container to avoid dependency clashes — see `code/07_train_export_compile.sh`.

---

## 4. ESP32-CAM (microcontroller tier)

- **Arduino IDE** with the ESP32 board package (Boards Manager → "esp32" by
  Espressif), or PlatformIO.
- A USB-TTL programmer (FTDI) or an ESP32-CAM-MB shield to flash the board.
- For TinyML: the **Edge Impulse** Arduino library (exported from your trained
  project as a single `.zip`, added via *Sketch → Include Library → Add .ZIP*).
- For the "networked camera" role: flash the stock **CameraWebServer** example
  (File → Examples → ESP32 → Camera → CameraWebServer); note the MJPEG stream
  URL it prints, typically `http://<ESP32_IP>:81/stream`.

Details and code in `code/esp32cam/README_esp32cam.md`.

---

## 5. Verify the whole chain (5-minute smoke test)

1. `rpicam-hello` shows the Pi camera. ✅
2. `hailortcli fw-control identify` sees the NPU. ✅
3. `python code/06_hailo_picamera2_detect.py` draws boxes on a live feed. ✅
4. ESP32-CAM stream opens in a browser at `http://<ip>`. ✅
5. `python code/08_esp32cam_stream_ingest.py --url http://<ip>:81/stream` shows
   the ESP32 feed inside OpenCV on the Pi. ✅

If all five pass, you are ready for Week 1.
