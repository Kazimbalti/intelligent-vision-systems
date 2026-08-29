# Applied Intelligent Vision Systems
## 14 Lectures + Workshops — Course Handbook

**A hands-on, deployment-first computer-vision course.** Each unit is one
**lecture** (theory) + one **workshop** (build something that runs). The course
takes a student from photons and pixels all the way to a **drone/robot that
sees, decides, and acts** — every model is deployed on real edge hardware.

**Hardware spine:** ESP32-CAM (microcontroller/TinyML) · Raspberry Pi 5 (CPU) ·
**Hailo AI HAT** (NPU) · Pi Camera 3/HQ/Global-Shutter · **Tello / AI drone**
(perception→action). Training happens on a GPU laptop or Google Colab.

**Level:** BS final-year / PG intro · **Duration:** 14 weeks (or a 7-week
double-session intensive) · **Prereqs:** Python, basic linear algebra.

> This handbook synthesises the strongest elements of modern applied-CV
> curricula — OpenCV fundamentals, PyTorch/CNNs, the full YOLO lineage through
> **YOLO26** (NMS-free, edge-first, launched Jan 2026), multi-object tracking &
> analytics, segmentation & pose, Vision Transformers / VLMs / VLA, MediaPipe,
> and drone integration — into one coherent, hardware-grounded program.

---

## Course Learning Outcomes (CLOs)

- **CLO1 — Classical CV:** apply image processing, features, geometry, and
  calibration to solve defined vision tasks. *(Apply)*
- **CLO2 — Real-time systems:** build camera applications on the Pi and reason
  about latency/throughput/power across compute tiers. *(Apply/Evaluate)*
- **CLO3 — Deep learning:** train, fine-tune, and evaluate CNN/Transformer
  models with correct metrics (accuracy, IoU, mAP). *(Analyse)*
- **CLO4 — Detection & analytics:** deploy detection, tracking, counting, and
  segmentation/pose pipelines with application logic. *(Create)*
- **CLO5 — Edge deployment:** compile and run models on an NPU (Hailo) and MCU
  (ESP32), and quantify the speed/power trade-offs. *(Create/Evaluate)*
- **CLO6 — Vision-language:** use ViT/CLIP/VLM/SAM for zero-shot, search, VQA,
  and segmentation tasks, and explain the VLA (vision-language-action) idea.
  *(Understand/Apply)*
- **CLO7 — Integration:** integrate perception into a drone/robot system that
  turns detections into actions. *(Create)*
- **CLO8 — Communication:** ship a demo + technical report and justify every
  design choice. *(Evaluate)*

## Assessment (indicative)

| Component | Weight | Maps to |
|-----------|--------|---------|
| 14 workshop deliverables | 28% | CLO1–CLO7 |
| 3 quizzes (classical / deep / edge) | 12% | CLO1, CLO3, CLO5 |
| Mid project — custom detector on Hailo (after L8/L9) | 20% | CLO3–CLO5 |
| Capstone — drone/robot vision system + demo | 30% | CLO7, CLO8 |
| Lab notebook & participation | 10% | all |

Rubrics in **Appendix A**. Project briefs in **Appendix B**. A curated,
per-lecture resource list is in the companion file **`BEST_MATERIALS.md`**.

---

# PART I — CLASSICAL FOUNDATIONS

## Lecture 1 — Intelligent Vision Systems & the Edge Pipeline
**CLO2, CLO8**

**Lecture.** What "intelligent vision system" means beyond a trained model:
capture → pre-process → inference → post-process → decision → action, under real
constraints (latency, power, thermals, offline operation, privacy). Image
formation in one slide (light → lens → sensor → pixels; rolling vs **global
shutter**, why it matters for drones). The compute-tier ladder used all course:
**MCU (ESP32) → CPU (Pi 5) → NPU (Hailo) → + drone**. Tooling tour. Responsible
vision at the edge.

**Workshop — bring-up & "hello vision".** Complete `SETUP.md`; run the 5-step
smoke test; capture one frame on each tier (Pi camera, Hailo `identify`,
ESP32-CAM web stream). *Deliverable:* notebook page with photos + `hailortcli
identify` output. *(code: `04_picamera2_stream.py`, `08_esp32cam_stream_ingest.py`)*

## Lecture 2 — Image Fundamentals & Classical Processing (OpenCV)
**CLO1**

**Lecture.** Images as NumPy arrays; **BGR vs RGB vs HSV**, grayscale; ROIs and
drawing. Point ops (brightness/contrast, gamma). Filtering: box/Gaussian/median;
**edges** (Sobel, Laplacian, Canny). Histograms, equalisation, **CLAHE** for bad
lighting. Thresholding (global/Otsu/adaptive) and morphology to clean masks.

**Workshop — an interactive processing pipeline + colour detector.** Build a
trackbar pipeline (blur → threshold → morphology → Canny) and an HSV colour
detector; test under two lighting conditions and document what broke.
*Deliverable:* before/after montage + failure note. *(code:
`01_opencv_basics.py`, `02_filters_edges.py`)*

## Lecture 3 — Features, Geometry & Multi-View
**CLO1**

**Lecture.** Contours, shape/size measurement, polygon approximation. Classical
features: Harris, **ORB** keypoints/descriptors, matching. **Warp perspective**
and homography → document scanner, bird's-eye view. **Panorama/stitching**
(brief), HDR (brief). **Camera calibration:** pinhole model, intrinsics,
distortion, chessboard calibration.

**Workshop — calibrate + scan + stitch.** Calibrate your Pi camera
(save intrinsics), build a document scanner via perspective warp, and stitch a
2-image panorama. *Deliverable:* `camera_intrinsics.npz` + scanned page +
panorama. *(code: `03_features.py`)*

## Lecture 4 — Real-Time Capture & Camera Systems
**CLO2**

**Lecture.** The Pi camera stack: libcamera → rpicam-apps → **picamera2**.
Preview/still/video configs; resolution vs FPS vs accuracy; sensor choice
(Module 3 AF, HQ optics, **Global Shutter** for fast motion). The real-time loop,
FPS measurement, threading/queues. The ESP32-CAM as a **networked camera** (MJPEG
over Wi-Fi).

**Workshop — live app + FPS table + ESP32 ingest.** Stream from the Pi camera
with a live FPS overlay; sweep resolutions and record FPS (the **CPU baseline**
for Lecture 8). Ingest the ESP32-CAM stream on the Pi. *Deliverable:*
FPS-vs-resolution table + ESP32 feed screenshot. *(code:
`04_picamera2_stream.py`, `08_esp32cam_stream_ingest.py`)*

---

# PART II — DEEP LEARNING FOR VISION

## Lecture 5 — Deep Learning Foundations (PyTorch)
**CLO3** *(training tier — Colab)*

**Lecture.** Perceptron → ANN → **backpropagation**; activations (sigmoid/tanh/
ReLU/leaky/ELU/softmax) and the vanishing-gradient story; loss vs cost; **gradient
descent optimisers** (SGD, momentum, Adagrad, RMSProp, **Adam**); regularisation
(dropout, weight init). **CNN building blocks:** convolution, padding/stride,
pooling, receptive fields, parameter counting. PyTorch tensors & autograd.

**Workshop — train your first classifier.** In PyTorch, build a custom `Dataset`/
`DataLoader` and train a small CNN on a 3–5 class set you photograph. Report
accuracy + confusion matrix. *Deliverable:* Colab notebook + curves. *(code:
`ml/train_classifier_pytorch.py` — starter in package)*

## Lecture 6 — Image Classification & Transfer Learning + Deployment
**CLO3, CLO8**

**Lecture.** Architecture lineage: **LeNet → AlexNet → VGG → Inception → ResNet →
MobileNet → Vision Transformer**; what each fixed. **Transfer learning vs
pretrained vs fine-tuning** — the practical default. **Data augmentation**
(Albumentations/imgaug). Then **deployment 101:** wrap a model in **Gradio** and
host it free on **Hugging Face Spaces** (also mention Streamlit/Flask).

**Workshop — fine-tune + ship.** Fine-tune a pretrained backbone on your dataset;
build a Gradio demo; deploy it to a Hugging Face Space. *Deliverable:* live Space
URL + accuracy. *(code: `apps/gradio_classifier.py`)*

## Lecture 7 — Object Detection I: Architectures & the YOLO Family
**CLO3, CLO4**

**Lecture.** Detection vs classification; bounding boxes; anchor-based vs
anchor-free. Metrics: **IoU, precision/recall, mAP@0.5 / mAP@0.5:0.95**, NMS.
Two-stage lineage (**R-CNN → Fast → Faster → Mask R-CNN**) vs one-stage (SSD,
**YOLO**). YOLO evolution v5 → v8 → **YOLO11** → v12 → **YOLO26** (NMS-free,
native end-to-end, edge-first). Transformer detectors (**RF-DETR**) and
**zero-shot** detection (**YOLOE**, visual prompting).

**Workshop — run & compare.** Run pretrained YOLO26/YOLO11 on images and webcam;
sweep confidence/IoU; filter to one class; log ms/frame on your training machine
(contrast with Hailo in L8). Try one zero-shot query with YOLOE. *Deliverable:*
annotated detections + threshold trade-off note. *(code: `05_yolo_pretrained.py`)*

## Lecture 8 — Object Detection II: Custom Data + Edge Acceleration (Hailo)
**CLO4, CLO5** — *pairs with the Mid Project*

**Lecture.** Dataset lifecycle: collect → **label with Roboflow** → split →
augment. Training a custom YOLO; reading training curves; aerial datasets
(**VisDrone**). Then the **edge accelerator**: why NPUs exist; **HailoRT**, the
Model Zoo, the **`.hef`** format; the deploy chain **`.pt` → ONNX → Hailo DFC
(parse → optimise/quantise → compile) → `.hef`** on Pi + Hailo; int8
quantisation trade-offs; **CPU-vs-NPU** benchmarking.

**Workshop / Mid Project — custom detector on the NPU.** Label a small custom set
(PPE / pothole / your target), train YOLO, compile to `.hef`, deploy on Pi +
Hailo, and measure on-device FPS vs the L4 CPU baseline. *Deliverable:* working
NPU detector + 2-page report (dataset, curves, quantisation, speed-up). *(code:
`06_hailo_picamera2_detect.py`, `07_train_export_compile.sh`)*

---

# PART III — PERCEPTION AT SCALE

## Lecture 9 — Multi-Object Tracking, Counting & Analytics
**CLO4**

**Lecture.** From per-frame detection to **tracking**: the association problem;
IoU/Kalman; **SORT → DeepSORT → ByteTrack → BoT-SORT**; stable IDs. Turning
tracks into analytics: **line-crossing counts**, entering/leaving, **speed
estimation**, dwell time, heatmaps, ROI/zone logic. Real briefs: traffic
counting, people counter, sports analysis (player/ball tracking), license-plate
+ **OCR** pipeline.

**Workshop — a counting/analytics app.** Add Ultralytics tracking to a detector;
count objects crossing a line (in/out) and estimate speed; render a live tally.
*Deliverable:* clip with stable IDs + in/out counts + speed. *(code:
`09_tracking_counting.py`)*

## Lecture 10 — Segmentation, Pose & Human Interaction
**CLO4, CLO6**

**Lecture.** **Semantic vs instance** segmentation; up/downsampling, transposed
conv, seg losses; **FCN → U-Net → Mask R-CNN → YOLO-seg**; promptable
segmentation with **SAM (Segment Anything)**. **Pose/keypoints:** OpenPose,
YOLO-pose. **MediaPipe** hands/face/pose for fast, CPU-friendly interaction
(gesture control, blink/eye counter, hand-distance → parameter).

**Workshop — segment + control by gesture.** Run YOLO-seg or SAM on your images;
build a **MediaPipe** hand-gesture controller (e.g. pinch → volume/LED, or
hand-distance → a value). *Deliverable:* segmentation output + a working gesture
demo. *(code: `10_mediapipe_gesture.py`)*

## Lecture 11 — TinyML Vision on Microcontrollers (ESP32-CAM & Arduino)
**CLO5**

**Lecture.** Embedded ML: inference in the **mW** range on KB of RAM. **Edge
Impulse** workflow (collect → label → DSP → train → deploy as an Arduino lib);
**FOMO** centroid detection and why it fits tiny memory. The ESP32/Arduino
**vision + sensor** project family (object counter, hand-gesture light, pan-tilt
tracker, ultrasonic/water-level logger, face door-lock, data to MongoDB). Two
roles for the ESP32-CAM: standalone TinyML vs networked camera into the Pi/Hailo
pipeline.

**Workshop — FOMO on-device + a sensor project.** Train a 2–3 class FOMO model in
Edge Impulse and run it on the ESP32-CAM; wire one sensor-integrated behaviour
(e.g. pan-tilt follow or gesture → LED). *Deliverable:* on-device detection video
+ tier comparison row. *(code: `esp32cam/README_esp32cam.md`)*

---

# PART IV — VISION-LANGUAGE & INTEGRATION

## Lecture 12 — Vision Transformers, VLMs & Vision-Language Tasks
**CLO6**

**Lecture.** **ViT**: patches, position, attention (Q/K/V), multi-head, residual/
norm. **CLIP** contrastive alignment → **zero-shot** classification and **visual
search**. **VLMs** for captioning, **VQA**, and describing scenes; **OCR** with a
multimodal model. Applied patterns from industry: satellite/soil classification
with ViT, product background removal with SAM, e-commerce tagging with CLIP,
**CCTV analyst / retail VQA / real-estate description** with a VLM.

**Workshop — CLIP search + VLM VQA.** Build a CLIP visual-search / zero-shot
classifier over your own images; then ask a VLM a question about a scene (VQA) or
generate a caption. *Deliverable:* a working search demo + one VQA example.
*(code: `11_clip_visual_search.py`)*

## Lecture 13 — Vision-Language-Action (VLA): Perception → Behaviour
**CLO6, CLO7**

**Lecture (concept-forward).** From MDP basics (observation, state, action,
transition; open vs closed loop; **three clocks / latency budget**) to the VLA
stack: attaching an **action head** to a VLM; **behaviour cloning**; **diffusion
policies** and **flow matching** (why regression averages two good paths into a
crash); **world models** and imagined rollouts; where **classical robotics**
(kinematics, the Jacobian, a 7 Hz model over a 400 Hz loop) and **runtime safety
gates** stay essential. This is the bridge from "detecting things" to "acting on
them."

**Workshop — closing the loop (sim/mock).** Implement a minimal perception→action
loop: detection → control signal (e.g. keep target centred → yaw command),
demonstrated on the capstone skeleton or in sim. Discuss latency and safety
gates. *Deliverable:* a loop that steers toward a detected target + a latency
note. *(code: `capstone_skeleton.py`, `12_tello_detect.py`)*

## Lecture 14 — Capstone: Drone / Robot-Integrated Intelligent Vision System
**CLO7, CLO8**

**Lecture (short) + studio.** Systems integration: capture → inference →
tracking/logic → **action** (display, log, network, actuate). Drone programming
patterns from the field: **Tello / AI-drone** object detection, **car/house
counting from the air**, **colour/QR-based navigation**, **obstacle avoidance**,
**voice/LLM-with-drone**, helipad landing. Optional **ROS 2** bridge to publish
detections. Reliability, thermals, graceful degradation.

**Capstone project.** Teams build one integrated system using ≥2 tiers with a
logic/action layer. *Deliverables:* live (or recorded) demo; 4–6 page report
(problem, tier justification, architecture, results = accuracy+FPS+power,
limitations); a repo forked from this scaffold. Brief bank in **Appendix B**.
*(code: `capstone_skeleton.py`, `12_tello_detect.py`)*

---

## Appendix A — Rubrics

**Workshop rubric (per lecture).**

| Criterion | Excellent (100) | Adequate (70) | Weak (40) |
|-----------|-----------------|---------------|-----------|
| Correctness | Runs, meets spec | Minor issues | Major gaps |
| Understanding | Notebook explains *why* | Describes *what* | Missing |
| Measurement | Quant. results + interpretation | Numbers only | None |
| Engineering | Clean, reproducible repo | Works but messy | Not reproducible |

**Project rubric (mid & capstone).** Problem framing (15) · Data/method (20) ·
Correct edge deployment & measurement (25) · Integration/action layer (20) ·
Report & demo clarity (20).

## Appendix B — Project brief bank (from the drone/analytics field)

*Analytics:* traffic/vehicle counter with speed · people counter (in/out) ·
PPE/helmet compliance monitor · license-plate detect + OCR · sports (player/ball)
analysis · retail shelf/inventory VQA.
*Edge:* custom YOLO→Hailo detector at 30 FPS · ESP32-CAM FOMO smart sensor ·
ESP32-CAM → Pi/Hailo aggregator.
*Drone/robot:* aerial house/car counter · colour- or QR-guided navigation ·
infinite obstacle course · voice/LLM-activated drone · no-feedback maze · target
follow (IBVS) · helipad landing · symmetrical drone show.

## Appendix C — Tier comparison table (the intellectual payoff)

Students fill this with **their own measurements** and justify a tier choice (CLO5):

| Tier | Model | Input | ~FPS | ~Power | When to use |
|------|-------|-------|------|--------|-------------|
| ESP32-CAM | FOMO | 96×96 | ? | ~mW | always-on, no host, cheapest |
| Pi 5 CPU | YOLO26-n | 640 | ? | ~W | flexible, prototyping |
| Pi 5 + Hailo | YOLO .hef | 640 | ? | ~W+NPU | real-time, offline, production |

## Appendix D — 7-week intensive mapping

Double up: (1+2) (3+4) (5+6) (7+8) (9+10) (11+12) (13+14). Mid project spans the
(7+8) week; capstone runs through the final two weeks.

---

*See `BEST_MATERIALS.md` for the vetted, per-lecture resource list (courses,
docs, repos, datasets). See `README.md` for repo layout and `SETUP.md` for the
full hardware/software setup.*
