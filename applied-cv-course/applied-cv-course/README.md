# Applied Intelligent Vision Systems — Edge, Embedded & Drone

A hands-on, hardware-anchored computer-vision course built around a
three-tier edge-AI stack plus a drone: **microcontroller (ESP32-CAM) → single-board
CPU (Raspberry Pi 5) → NPU-accelerated inference (Hailo AI HAT) → drone/robot
(Tello / AI drone)**. Students move from classical image processing to deep
object detection, tracking, segmentation, vision-language models, and finally to
*a drone/robot that sees, decides, and acts* — every model deployed on real
hardware.

> **Two handbooks are included:**
> - **`Applied_Intelligent_Vision_Systems_14_Lectures.md`** — the full **14
>   lectures + workshops** program (recommended; synthesises modern YOLO/YOLO26,
>   tracking & analytics, segmentation/pose, ViT/VLM/VLA, MediaPipe, drones).
> - **`Applied_Computer_Vision_Handbook.md`** — the original **12-week** version
>   (a leaner, edge-deployment-focused subset).
> - **`BEST_MATERIALS.md`** — vetted resources mapped to each lecture.

> Designed for BS/PG engineering students. The distinctive feature versus
> Stanford CS231n or UMich EECS-498 is that this course does not stop at
> training — it takes each learner all the way to a real, offline, real-time
> vision system running on their own hardware.

---

## Target hardware

| Tier | Device | Role in the course |
|------|--------|--------------------|
| Accelerator | **Raspberry Pi 5 + Hailo AI HAT (Hailo-8 / 8L, 13/26 TOPS)** or **AI HAT+ 2 (Hailo-10H, 40 TOPS)** | Real-time accelerated inference (Weeks 8–12) |
| Host CPU | **Raspberry Pi 5 (8 GB recommended)** | OS, camera pipeline, classical CV, orchestration |
| Cameras | **Pi Camera Module 3 / HQ / Global Shutter**, USB webcam | Real-time capture (Weeks 5–12) |
| Microcontroller | **ESP32-CAM (OV2640)** | On-device TinyML + networked camera node (Week 10) |
| Training | Laptop/desktop GPU **or** Google Colab (free) | Model training & ONNX export (Weeks 6, 7, 9) |

You do **not** need every camera. One Pi Camera + the ESP32-CAM is enough to run
the whole course; a USB webcam is a fine substitute for early weeks.

---

## The three-tier mental model (used throughout)

```
                 same task (e.g. object detection), three tiers

  ESP32-CAM  ───────►  Pi 5 CPU  ───────►  Pi 5 + Hailo NPU
  TinyML/FOMO         OpenCV / small       compiled .hef,
  KB models, mW       CNN, a few FPS       30+ FPS, offline
```

Every major topic is taught by asking: *where should this run, and why?*

---

## 12-week map

| Wk | Theme | Tier | Lab deliverable |
|----|-------|------|-----------------|
| 1 | Foundations & the edge-vision pipeline | all | Hardware boot + `hello vision` |
| 2 | Images, pixels & OpenCV fundamentals | CPU | Image manipulation script |
| 3 | Filtering, edges & morphology | CPU | Edge/threshold pipeline |
| 4 | Features, contours & camera calibration | CPU + cam | Calibrated feature detector |
| 5 | Real-time capture with picamera2 | Pi cam | Live FPS-benchmarked video app |
| 6 | From classical to CNNs (transfer learning) | Training | Trained classifier (Colab) |
| 7 | Object detection & the YOLO family | Training | Pretrained YOLO on images |
| 8 | Hailo NPU: accelerated inference | NPU | 30-FPS live detector on Pi |
| 9 | Train → export → **compile to .hef** → deploy | Training + NPU | Custom detector on Hailo |
| 10 | TinyML vision on ESP32-CAM | MCU | On-device FOMO + stream into Pi |
| 11 | Tracking, pose & segmentation | NPU | Multi-object tracker w/ logic |
| 12 | **Capstone:** integrated applied CV system | all | End-to-end project + demo |

Full weekly detail is in **`Applied_Computer_Vision_Handbook.md`**.

---

## Repository layout

```
applied-cv-course/
├── README.md                         # this file
├── SETUP.md                          # full environment setup for every tier
├── Applied_Computer_Vision_Handbook.md   # the 12-week course (lessons + labs)
├── requirements.txt                  # Python deps for the CPU/training tiers
├── code/
│   ├── 01_opencv_basics.py           # L2  load/convert/draw/save
│   ├── 02_filters_edges.py           # L2  blur/Canny/threshold/morphology
│   ├── 03_features.py                # L3  ORB features + contours + calibration
│   ├── 04_picamera2_stream.py        # L4  live capture + FPS benchmark
│   ├── 05_yolo_pretrained.py         # L7  pretrained YOLO (training tier)
│   ├── 06_hailo_picamera2_detect.py  # L8  Hailo + picamera2 live detection
│   ├── 07_train_export_compile.sh    # L8  YOLO → ONNX → .hef commands
│   ├── 08_esp32cam_stream_ingest.py  # L4/11 read ESP32-CAM MJPEG stream
│   ├── 09_tracking_counting.py       # L9  tracking + line-cross counting + speed
│   ├── 10_mediapipe_gesture.py       # L10 MediaPipe hand-gesture controller
│   ├── 11_clip_visual_search.py      # L12 CLIP zero-shot + visual search
│   ├── 12_tello_detect.py            # L13/14 Tello detect + perception→action
│   ├── capstone_skeleton.py          # L14 integrated pipeline skeleton
│   ├── ml/
│   │   └── train_classifier_pytorch.py   # L5  PyTorch CNN training starter
│   ├── apps/
│   │   └── gradio_classifier.py      # L6  Gradio demo for HF Spaces
│   └── esp32cam/
│       └── README_esp32cam.md        # L11 Edge Impulse FOMO + CameraWebServer
└── datasets/                         # (empty) place custom datasets here
```

## How to use this course

- **As an instructor:** the handbook is your week-by-week teaching plan. Each week
  has learning outcomes, a lecture outline, a lab with steps, and a graded
  deliverable. Adapt the assessment weights in the handbook's *Assessment* section.
- **As a self-learner:** work top to bottom. Do `SETUP.md` first, then one week
  per week; every week's lab uses the matching script in `code/`.
- **Code caveat:** the Pi/Hailo/ESP32 scripts must be run **on-device** and
  depend on installed runtime versions (HailoRT, picamera2, model-zoo). Treat
  them as reference implementations and verify against the current official
  repos linked in `SETUP.md` before a live class.

## License / attribution

Course structure and text: free to reuse and adapt for teaching (CC BY 4.0
suggested). Third-party tools (OpenCV, Ultralytics, Hailo, Edge Impulse) retain
their own licenses; students must register for the Hailo Developer Zone to
download the Dataflow Compiler.
