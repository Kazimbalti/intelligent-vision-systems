# ESP32-CAM — TinyML (FOMO) + networked camera

Two roles for the ESP32-CAM in Week 10.

## Role A — Standalone on-device detection (Edge Impulse FOMO)

1. **Collect data.** In Edge Impulse, create a project and collect images of your
   2–3 classes directly from the ESP32-CAM (or upload phone photos). Aim for
   ~50–100 images/class in varied lighting.
2. **Label.** Draw bounding boxes (FOMO uses centroids, so boxes can be loose).
3. **Impulse.** Image block (e.g. 96×96, grayscale or RGB) → **Object Detection
   (FOMO)** learning block. FOMO is the memory-friendly choice for MCUs.
4. **Train.** Watch the F1 score; iterate on data if a class is weak.
5. **Deploy.** Export as an **Arduino library (.zip)**. In Arduino IDE:
   *Sketch → Include Library → Add .ZIP Library*, then open the generated
   `esp32_camera` example, select your ESP32-CAM board, and flash.
6. Open the Serial Monitor (115200) to see detections + centroids.

Docs: https://docs.edgeimpulse.com/hardware/boards/espressif-esp32
FOMO on ESP32-CAM tutorial:
https://www.makerguides.com/train-an-object-detection-model-with-edge-impulse-for-esp32-cam/

Hardware notes:
- Flash with an FTDI/USB-TTL adapter or an ESP32-CAM-MB shield.
- The OV2640 + PSRAM build is assumed; enable PSRAM in board options.
- Keep the model tiny — 96×96 grayscale FOMO fits comfortably; larger inputs
  will OOM.

## Role B — Networked camera into the Pi/Hailo pipeline

1. Arduino IDE → *File → Examples → ESP32 → Camera → CameraWebServer*.
2. Set your board model (e.g. `AI-THINKER`) and Wi-Fi SSID/password, flash.
3. Open the Serial Monitor to read the assigned IP. The web UI is at
   `http://<ip>/`; the raw MJPEG stream is usually `http://<ip>:81/stream`.
4. On the Pi, ingest it:
   ```bash
   python ../08_esp32cam_stream_ingest.py --url http://<ip>:81/stream
   ```
5. Feed those frames into the Week-8 Hailo detector to detect on the ESP32 feed.

## Teaching point — the tier comparison table

Run the *same* detection task on each tier and fill in:

| Tier | Model | Input | ~FPS | ~Power | Notes |
|------|-------|-------|------|--------|-------|
| ESP32-CAM | FOMO | 96×96 | ? | ~mW | on-device, no host |
| Pi 5 CPU | YOLOv8n | 640 | ? | ~W | flexible, slow |
| Pi 5 + Hailo | YOLOv8 .hef | 640 | ? | ~W+NPU | fast, offline |

This table is the intellectual payoff of the course: students *justify* a tier
choice with their own measured numbers (CLO5).
