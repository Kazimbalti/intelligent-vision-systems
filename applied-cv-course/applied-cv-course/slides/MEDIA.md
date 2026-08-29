# MEDIA PACK — latest images & videos per lecture

How to use this: the decks already carry (a) original diagrams I generated
(safe to redistribute) and (b) clickable **"▶ Watch (latest)"** links to current
official videos/demos on the Resources slide of each lecture. This file is the
fuller list so you can drop in **licensed** product photos and demo clips
yourself.

**Copyright note.** Product photos, press images, and video frames are owned by
their makers. For internal teaching that's usually fine under fair dealing /
educational use, but if you publish or sell the deck, use official press-kit
images with attribution or CC-licensed images. Do not paste random web images
into a redistributable deck.

**Safe image sources (reusable):**
- Official press/brand kits (attribution as required) — Raspberry Pi, Hailo,
  Ultralytics, Espressif.
- Wikimedia Commons (check each file's licence): https://commons.wikimedia.org
- Unsplash / Pexels (free commercial use): https://unsplash.com · https://pexels.com
- Diagrams: reuse the originals in `slides/figures/` or regenerate via
  `make_figures.py`.

---

## L1 — Intelligent Vision Systems & the Edge Pipeline
- **Video:** Raspberry Pi AI HAT+ 2 setup, object detection & VLM demo — https://www.youtube.com/watch?v=kjkJm15RTE8
- **Images:** Raspberry Pi 5 + AI HAT press images — https://www.raspberrypi.com/products/ · Hailo brand assets — https://hailo.ai/
- **Figure included:** `fig_pipeline.png` (the pipeline).

## L2 — Image Fundamentals & Classical Processing
- **Video/course:** OpenCV University free courses — https://opencv.org/university/free-courses/
- **Images:** OpenCV logo/press — https://opencv.org/ ; sample images ship with OpenCV.

## L3 — Features, Geometry & Multi-View
- **Video/docs:** OpenCV feature matching & calibration — https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html
- **Images:** use your own calibration board photos (from the workshop).

## L4 — Real-Time Capture & Camera Systems
- **Video/examples:** picamera2 examples — https://github.com/raspberrypi/picamera2
- **Images:** Pi Camera Module 3 / HQ / Global Shutter product pages — https://www.raspberrypi.com/products/

## L5 — Deep Learning Foundations
- **Video:** UMich EECS 498 Deep Learning for CV, Lecture 1 — https://www.youtube.com/watch?v=QytpbYkGxKo
- **Figure included:** `fig_conv.png` (convolution / receptive field).

## L6 — Classification, Transfer Learning & Deployment
- **Video/docs:** Gradio — https://www.gradio.app/ ; Hugging Face Spaces — https://huggingface.co/spaces
- **Images:** architecture diagrams — draw your own or cite the original papers.

## L7 — Object Detection I (YOLO family)
- **Video:** Ultralytics YOLO26 — detection/segmentation/pose real-time demo (2026) — https://www.youtube.com/watch?v=F3ej8JG5IeY
- **Also:** Ultralytics Live Session 20 (YOLO26) — https://www.youtube.com/watch?v=ub2xbSlay7g
- **Figure included:** `fig_iou.png` (IoU & mAP).

## L8 — Custom Data + Hailo NPU
- **Video:** RPi 5 + Hailo object detection on the edge (2025) — https://www.youtube.com/watch?v=xiHv7xd1drY
- **Video:** Train YOLO26 on a custom dataset in Colab (2026) — https://www.youtube.com/watch?v=7lZa3Yi2kbo
- **Video:** AI HAT+ 2 (Hailo-10H) setup & demo — https://www.youtube.com/watch?v=kjkJm15RTE8
- **Images:** Hailo AI HAT product/press — https://hailo.ai/

## L9 — Tracking, Counting & Analytics
- **Video:** YOLO26 for video analytics — tracking & counting (2026) — https://www.youtube.com/watch?v=IYKouYLYqX8
- **Docs/GIFs:** Ultralytics solutions (counting, speed, heatmaps) — https://docs.ultralytics.com/solutions/

## L10 — Segmentation, Pose & Interaction
- **Video:** Meta **SAM 3** — unified detection, segmentation & tracking (Nov 2025) — https://www.youtube.com/watch?v=G4OLPDjwncw
- **Video:** MediaPipe hand tracking with OpenCV — https://www.youtube.com/watch?v=RRBXVu5UE-U
- **Live demos (in-browser):** MediaPipe web samples — https://google-ai-edge.github.io/mediapipe-samples-web/
- **Images/GIFs:** SAM project page — https://ai.meta.com/sam3 (and SAM 2 — https://ai.meta.com/research/sam2/)

## L11 — TinyML on ESP32-CAM & Arduino
- **Video:** ESP32-CAM object detection with Edge Impulse FOMO — https://www.youtube.com/watch?v=HDRvZ_BYd08
- **Also (ESP32-S3):** https://www.youtube.com/watch?v=4WepPKM3Vh0
- **Images:** ESP32-CAM board photos — Espressif — https://www.espressif.com/

## L12 — ViT, VLMs & Vision-Language
- **Live demos:** MediaPipe web samples — https://google-ai-edge.github.io/mediapipe-samples-web/
- **Live demos:** Hugging Face image-text-to-text (VLM) — https://huggingface.co/models?pipeline_tag=image-text-to-text
- **Figure included:** `fig_attention.png` (attention Q/K/V).

## L13 — Vision-Language-Action
- **Video/demos:** LeRobot (Hugging Face) — https://github.com/huggingface/lerobot
- **Project page:** Diffusion Policy — https://diffusion-policy.cs.columbia.edu/

## L14 — Capstone: Drone / Robot Integration
- **Video/project:** DJI Tello + YOLOv8 real-time detection — https://github.com/dp-betalock/DJITelloDrone-YOLOv8
- **Project:** Tello instance segmentation (YOLOv8/Detectron2) — https://github.com/dronefreak/dji-tello-object-detection-segmentation
- **Docs:** Ultralytics ROS quickstart — https://docs.ultralytics.com/guides/ros-quickstart/

---

### How to drop an image into a slide (PowerPoint)
Insert → Pictures → This Device, place it, then right-click → Send to Back if it
should sit behind text. Keep a 0.3–0.5" margin. For a video: Insert → Video →
Online Video (paste the YouTube URL) to embed a player, or keep the clickable
link already on the Resources slide.

### Regenerating the diagrams
`python3 make_figures.py` rewrites the PNGs in `figures/` using the course
palette — edit that script to restyle or add new diagrams.
