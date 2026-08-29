# Applied Computer Vision — Edge & Embedded
## Course Handbook (12 Weeks)

**Level:** BS (final year) / PG introductory · **Credits:** 3 (2 theory + 1 lab)
**Contact:** 2 h lecture + 3 h lab per week · **Prereqs:** Python, basic linear
algebra, intro programming. No prior CV or ML assumed.

---

## Course description

Applied Computer Vision teaches students to build real vision systems that run
on constrained edge hardware. Rather than stopping at model training, the course
follows a complete pipeline — capture → classical processing → deep detection →
**compile to an edge accelerator** → deploy → integrate — across three hardware
tiers: an ESP32-CAM microcontroller, a Raspberry Pi 5 CPU, and a Hailo NPU. By
the end, each student ships an offline, real-time vision application on their own
hardware.

## Course Learning Outcomes (CLOs)

On completion, a student can:

- **CLO1** — Apply classical image-processing operations (filtering, edges,
  morphology, features) to solve well-defined vision tasks. *(Apply)*
- **CLO2** — Build real-time camera applications on a Raspberry Pi using the
  libcamera/picamera2 stack and reason about latency/throughput trade-offs.
  *(Apply)*
- **CLO3** — Explain modern CNN-based recognition and object detection, and
  train/evaluate a model using standard metrics (accuracy, IoU, mAP).
  *(Understand/Analyse)*
- **CLO4** — Compile and deploy a custom neural network onto an edge NPU (Hailo)
  and quantify the speed-up versus CPU inference. *(Create)*
- **CLO5** — Select the appropriate compute tier (MCU/CPU/NPU) for a given
  vision requirement and justify the choice on power, latency, and accuracy.
  *(Evaluate)*
- **CLO6** — Integrate perception into a working end-to-end system and
  communicate results through a demo and technical report. *(Create)*

## Assessment (indicative weights)

| Component | Weight | Maps to |
|-----------|--------|---------|
| Weekly labs (10 graded) | 30% | CLO1–CLO4 |
| Quizzes (2) | 10% | CLO1, CLO3 |
| Mid-term project — custom Hailo detector (Wk 9) | 20% | CLO3, CLO4, CLO5 |
| Capstone project + demo (Wk 12) | 30% | CLO5, CLO6 |
| Participation / lab notebook | 10% | all |

Each lab below lists its **deliverable**; the lab notebook is the running record
students keep (screenshots, FPS numbers, short reflections).

---

# WEEK 1 — Foundations & the edge-vision pipeline

**Outcomes:** describe the applied-CV pipeline; explain the three-tier edge
model; boot every device and run a "hello vision" on each. *(CLO5)*

**Lecture**
- What "applied" CV means: the gap between a trained model and a deployed system
  (capture, pre/post-processing, latency, power, thermals, offline operation).
- Image formation in one slide: light → lens → sensor → pixels; resolution,
  frame rate, rolling vs global shutter (motivates the Global Shutter camera).
- The three tiers and where each wins: ESP32-CAM (mW, KB models, always-on),
  Pi 5 CPU (flexible, a few FPS on CNNs), Pi 5 + Hailo NPU (30+ FPS, offline).
- Course tools tour: OpenCV, picamera2, Ultralytics/YOLO, Hailo toolchain,
  Edge Impulse. Ethics & privacy of vision at the edge (on-device = data stays local).

**Lab (setup + smoke test)**
1. Complete `SETUP.md` for the Pi/Hailo tier and the ESP32 tier.
2. Run the 5-step smoke test in `SETUP.md §5`.
3. "Hello vision" on each tier: Pi camera preview (`rpicam-hello`), Hailo
   `identify`, ESP32-CAM web stream in a browser.

**Deliverable:** lab notebook page with a photo of the assembled Pi 5 + Hailo +
camera, the `hailortcli ... identify` output, and the ESP32 stream URL.

---

# WEEK 2 — Images, pixels & OpenCV fundamentals

**Outcomes:** represent images as NumPy arrays; read/convert/draw/save; manage
color spaces and ROIs. *(CLO1)*

**Lecture**
- Digital image = H×W×C array; dtype (`uint8`), value ranges, channels.
- Color spaces and when to use them: BGR (OpenCV default!) vs RGB, grayscale,
  **HSV for color segmentation**, and why lighting breaks naïve RGB thresholds.
- Coordinate conventions, ROIs/slicing, drawing primitives, and the
  read→process→write loop. Image vs video I/O.
- Common beginner traps: BGR/RGB mix-ups, integer overflow in arithmetic,
  in-place vs copy.

**Lab — `code/01_opencv_basics.py`**
Load an image, convert BGR↔RGB↔HSV↔gray, crop an ROI, draw a labelled box,
adjust brightness/contrast safely, and save results. Then repeat on a frame
grabbed from the Pi camera.

**Deliverable:** a script that takes any image path and outputs a 2×2 montage
(original, gray, HSV, annotated) saved to disk.

---

# WEEK 3 — Filtering, edges & morphology

**Outcomes:** apply convolution-based filters, edge detectors, thresholding, and
morphology to clean and segment images. *(CLO1)*

**Lecture**
- Convolution intuition; kernels; separable filters; box vs Gaussian blur;
  median blur for salt-and-pepper noise.
- Gradients & edges: Sobel, Laplacian, and the **Canny** pipeline
  (smoothing → gradient → non-max suppression → hysteresis).
- Thresholding: global, Otsu, adaptive; when each fails.
- Morphology: erosion, dilation, opening, closing; structuring elements; using
  morphology to denoise masks before contouring.

**Lab — `code/02_filters_edges.py`**
Build a small pipeline with trackbars: blur → threshold (Otsu/adaptive) →
morphology → Canny. Tune it to cleanly segment a chosen object (e.g. a coloured
tag) under two lighting conditions.

**Deliverable:** before/after images plus a one-paragraph note on which lighting
condition broke the pipeline and how you fixed it. *(Quiz 1 covers Wks 2–3.)*

---

# WEEK 4 — Features, contours & camera calibration

**Outcomes:** detect contours/shapes and keypoint features; calibrate a camera
and explain distortion. *(CLO1, CLO2)*

**Lecture**
- Contours: finding, hierarchy, area/perimeter, approximating polygons, bounding
  boxes/rotated boxes; simple shape & size measurement.
- Classical features: Harris corners; ORB keypoints & descriptors; matching with
  BFMatcher; when classical features still beat CNNs (low power, no training).
- Template matching and its limits (scale/rotation).
- **Camera calibration:** pinhole model, intrinsics, lens distortion; chessboard
  calibration; why calibration matters for measurement, AR, and robotics.

**Lab — `code/03_features.py`**
Detect and count objects by contour; then run ORB matching between two views of
a scene. Capture ~15 chessboard images from your Pi camera and compute the camera
matrix + distortion coefficients; undistort a live frame.

**Deliverable:** the saved calibration file (`camera_intrinsics.npz`) and a
side-by-side distorted/undistorted frame.

---

# WEEK 5 — Real-time capture with picamera2

**Outcomes:** build a real-time video application on the Pi; measure and reason
about FPS/latency. *(CLO2, CLO5)*

**Lecture**
- The Pi camera stack: libcamera → rpicam-apps → **picamera2** (Python).
- Configurations: preview vs still vs video; resolution, format, framerate;
  sensor differences (Module 3 autofocus, HQ optics, **Global Shutter** for fast
  motion / drones).
- The real-time loop: capture → process → display; measuring FPS; where time
  goes (capture vs copy vs processing vs draw); threading/queues to avoid stalls.
- Trade-off framing: resolution vs FPS vs accuracy — the recurring edge dilemma.

**Lab — `code/04_picamera2_stream.py`**
Stream from the Pi camera, overlay a live FPS counter, and apply one Week-3
operation per frame (e.g. Canny). Sweep resolution (640×480 → 1280×720 →
1920×1080) and record FPS at each.

**Deliverable:** an FPS-vs-resolution table + a two-sentence interpretation.
This table becomes the CPU baseline you compare the NPU against in Week 8.

---

# WEEK 6 — From classical features to CNNs (transfer learning)

**Outcomes:** explain CNN building blocks; train an image classifier via transfer
learning and evaluate it. *(CLO3)* *(Training tier — Colab.)*

**Lecture**
- Why learned features beat hand-crafted ones; the recognition task family
  (classification → detection → segmentation → pose).
- CNN anatomy: convolution, stride/padding, pooling, activations, batch-norm,
  fully-connected heads; receptive fields.
- Training essentials: datasets & splits, loss, optimiser, epochs, over/under-
  fitting, augmentation; **transfer learning** and why it's the practical default.
- Evaluating classifiers: accuracy, confusion matrix, precision/recall.

**Lab (Colab)**
Fine-tune a small pretrained backbone (e.g. MobileNet/ResNet-18) on a 3–5 class
custom dataset the class photographs (e.g. tools, PPE, fruit). Report accuracy +
confusion matrix. Keep this dataset — Week 9 reuses the collection workflow.

**Deliverable:** Colab notebook + final accuracy + confusion matrix figure.

---

# WEEK 7 — Object detection & the YOLO family

**Outcomes:** explain detection formulation and metrics; run a pretrained YOLO
model and interpret its output. *(CLO3)*

**Lecture**
- Detection vs classification; bounding boxes; anchor-based vs anchor-free.
- The **YOLO** idea (single-shot, grid, one forward pass) and the evolution
  YOLOv5 → v8 → v11; model sizes n/s/m/l/x and the speed/accuracy trade-off.
- Metrics that matter: IoU, precision/recall, **mAP@0.5** and mAP@0.5:0.95; NMS
  and confidence thresholds.
- Post-processing & class filtering (e.g. keep only "person" for surveillance).

**Lab — `code/05_yolo_pretrained.py`**
Run pretrained YOLOv8n on images and a webcam; vary confidence/IoU thresholds and
observe effects; filter to a single class; log inference time per frame on the
training machine (to contrast with Hailo next week).

**Deliverable:** annotated detections + a short note on how threshold changes
traded false positives against misses. *(Quiz 2 covers Wks 6–7.)*

---

# WEEK 8 — Hailo NPU: accelerated inference

**Outcomes:** run a pre-compiled model on the Hailo NPU via picamera2; quantify
the NPU speed-up over the Week-5 CPU baseline. *(CLO4, CLO5)*

**Lecture**
- Why NPUs exist: CNNs are cheap in TOPS but expensive on general CPUs; edge
  accelerators trade flexibility for throughput/Watt.
- The Hailo stack: **HailoRT**, the Python API, the **Model Zoo** (pre-compiled
  `.hef`), and the GStreamer/`hailonet` and picamera2 integration paths.
- The `.hef` format and chip targeting (8 vs 8L vs 10H — a build is chip-specific).
- Pipeline anatomy: camera → NPU inference → CPU post-process/draw; where the CPU
  still does work (pre/post-processing, tracking, drawing).

**Lab — `code/06_hailo_picamera2_detect.py`**
Download a pre-compiled YOLO `.hef` for your chip from the Model Zoo, run live
detection from the Pi camera, and read the achieved FPS. Compare against the
Week-5 CPU FPS table.

**Deliverable:** live-detection screenshot + a CPU-vs-NPU FPS comparison and the
computed speed-up factor. This is the course's "aha" moment — make it explicit.

---

# WEEK 9 — Train → export → compile to `.hef` → deploy (Mid-term project)

**Outcomes:** take a custom-trained model all the way onto the NPU and evaluate
it on-device. *(CLO3, CLO4, CLO5)*

**Lecture**
- The full deployment chain: **train (`.pt`) → export ONNX → Hailo Dataflow
  Compiler (parse → optimise/quantise → compile) → `.hef` → deploy.**
- Quantisation: float32 → int8, calibration data, and the small accuracy cost you
  trade for large speed/memory gains.
- Practical MLOps: keeping training and compilation in **separate Docker
  containers** to avoid dependency conflicts; versioning models.
- Failure modes: unsupported layers, wrong chip target, bad calibration set.

**Lab / Mid-term — `code/07_train_export_compile.sh`**
End-to-end: collect & label a small custom dataset (Roboflow or manual) →
train YOLOv8n (Colab) → export ONNX → compile to `.hef` with the DFC → deploy on
Pi + Hailo → measure mAP-ish qualitative accuracy and FPS on-device.

**Deliverable (graded project):** a working custom detector running on the NPU +
a 2-page report: dataset, training curve, quantisation notes, on-device FPS, and
one thing that went wrong and how you fixed it.

---

# WEEK 10 — TinyML vision on the ESP32-CAM

**Outcomes:** deploy an on-device vision model to a microcontroller and integrate
the ESP32-CAM as a networked camera node. *(CLO4, CLO5)*

**Lecture**
- TinyML / Embedded ML: running inference in the mW range on KB of RAM; what's
  possible (image classification, **FOMO** object detection) and what isn't.
- Edge Impulse workflow: collect → label → DSP block → train → deploy as an
  Arduino library; FOMO's centroid detection and why it fits tiny memory.
- Two roles for the ESP32-CAM: (a) fully standalone TinyML sensor; (b) cheap
  networked camera streaming MJPEG into the Pi/Hailo pipeline.
- Tier comparison: same detection task at MCU vs CPU vs NPU — accuracy, FPS, power.

**Lab — `code/esp32cam/README_esp32cam.md` + `code/08_esp32cam_stream_ingest.py`**
Part A: train a 2–3 class FOMO model in Edge Impulse and run it on the ESP32-CAM.
Part B: flash CameraWebServer and ingest the ESP32-CAM MJPEG stream into OpenCV
on the Pi, then feed it to the Week-8 Hailo detector.

**Deliverable:** short video of on-device FOMO detection + a screenshot of the
ESP32 feed being detected by the Pi+Hailo pipeline. Add a row to your tier table.

---

# WEEK 11 — Tracking, pose & segmentation

**Outcomes:** extend detection to tracking, pose, and segmentation, and add
application logic. *(CLO4, CLO6)*

**Lecture**
- From per-frame detection to **multi-object tracking**: the association problem,
  IoU/Kalman tracking, ByteTrack; stable IDs and counting.
- Pose estimation (keypoints) and instance segmentation on Hailo (available as
  pre-compiled zoo models); choosing task by application need.
- Turning perception into behaviour: ROIs, line-crossing counts, dwell time,
  event triggers/alerts — the logic layer that makes a demo a product.

**Lab**
Add a tracker to your Week-8/9 detector to count unique objects crossing a line,
or estimate pose and trigger an event (e.g. "hand in restricted zone"). Use a
zoo pose/seg `.hef` if your project calls for it.

**Deliverable:** a clip showing stable IDs / counts / an event trigger, plus the
event-logic snippet you wrote.

---

# WEEK 12 — Capstone: an integrated applied CV system

**Outcomes:** design, build, and present a complete offline real-time vision
system on the edge stack. *(CLO5, CLO6)*

**Lecture (short) + studio time**
- Systems view: capture → inference → tracking/logic → output (display, log,
  network, or actuation). Reliability, thermals, and graceful degradation.
- Bridging to robotics (optional extension): publishing detections to ROS 2, or
  driving a gimbal/vehicle from image-based guidance — a natural hook for a
  UAV/UGV follow-on.

**Capstone project — `code/capstone_skeleton.py`**
Teams build one integrated system that uses at least two tiers and includes a
logic layer. Example briefs:
- **Smart camera:** Pi+Hailo person/PPE detector with line-crossing counts and a
  logged event feed.
- **Multi-camera node:** ESP32-CAM(s) streaming into a Pi+Hailo aggregator with
  per-camera detection.
- **Perception-for-robotics:** detect + track a target and output steering
  commands (IBVS-style), demonstrated in sim or on a small rover/drone mock-up.
- **Retail/agri counter:** count/classify objects on a moving background with a
  running tally.

**Deliverable (graded):**
1. Live demo (or recorded video if hardware-bound).
2. 4–6 page report: problem, tier choices + justification (CLO5), architecture
   diagram, results (accuracy + FPS + power notes), limitations, next steps.
3. Code repository (fork of this scaffold) with a working README.

---

## Appendix A — Recommended references (all free/open)

- **UMich EECS 498-007 / 598-005, Deep Learning for Computer Vision** (Justin
  Johnson) — slides, notes, 6 assignments, YouTube lectures.
  https://web.eecs.umich.edu/~justincj/teaching/eecs498/
- **Stanford CS231n** — notes + assignments: https://cs231n.github.io/
- **OpenCV University free courses** (applied OpenCV/DL bootcamps):
  https://opencv.org/university/free-courses/
- **Harvard/Google TinyML open courseware:**
  https://github.com/tinyMLx/courseware/tree/master/edX
- **Raspberry Pi AI docs (Hailo):**
  https://www.raspberrypi.com/documentation/computers/ai.html
- **Hailo RPi examples:** https://github.com/hailo-ai/hailo-apps
- **Ultralytics YOLO docs:** https://docs.ultralytics.com/
- **Edge Impulse docs (ESP32):**
  https://docs.edgeimpulse.com/hardware/boards/espressif-esp32
- Textbook: Szeliski, *Computer Vision: Algorithms and Applications* (2nd ed.,
  free PDF): https://szeliski.org/Book/

## Appendix B — Suggested per-week grading rubric (labs)

| Criterion | Excellent (100) | Adequate (70) | Weak (40) |
|-----------|-----------------|---------------|-----------|
| Correctness | Runs, meets spec | Minor issues | Major gaps |
| Understanding | Notebook explains *why* | Describes *what* | Missing |
| Measurement | Quant. results + interpretation | Numbers only | None |
| Engineering | Clean, reproducible | Works, messy | Not reproducible |

## Appendix C — Mapping to a 12-week HEC/OBE weekly plan

Each week above already carries CLO tags and a deliverable. To produce an
OBE-compliant course file: (1) copy the CLO table and assessment weights into
your template, (2) map each CLO to your PLOs, (3) use Appendix B as the lab
rubric and the Week-9/Week-12 briefs as the project rubrics. Ask for the Word
version if you want this generated as a formal submission pack.
