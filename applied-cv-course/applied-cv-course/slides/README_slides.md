# Lecture slide decks (14)

One editable PowerPoint deck per lecture, matching the 14-lecture handbook.

| # | File | Lecture |
|---|------|---------|
| 1 | Lecture_01_Intro_Edge_Pipeline.pptx | Intelligent Vision Systems & the Edge Pipeline |
| 2 | Lecture_02_Image_Fundamentals_OpenCV.pptx | Image Fundamentals & Classical Processing |
| 3 | Lecture_03_Features_Geometry_MultiView.pptx | Features, Geometry & Multi-View |
| 4 | Lecture_04_RealTime_Capture_picamera2.pptx | Real-Time Capture & Camera Systems |
| 5 | Lecture_05_Deep_Learning_Foundations.pptx | Deep Learning Foundations for Vision |
| 6 | Lecture_06_Classification_Transfer_Deploy.pptx | Classification, Transfer Learning & Deployment |
| 7 | Lecture_07_Detection_I_YOLO_Family.pptx | Object Detection I — Architectures & YOLO |
| 8 | Lecture_08_Detection_II_Custom_Hailo.pptx | Object Detection II — Custom Data + Hailo NPU |
| 9 | Lecture_09_Tracking_Counting_Analytics.pptx | Tracking, Counting & Analytics |
| 10 | Lecture_10_Segmentation_Pose_Interaction.pptx | Segmentation, Pose & Human Interaction |
| 11 | Lecture_11_TinyML_ESP32_Arduino.pptx | TinyML Vision on Microcontrollers |
| 12 | Lecture_12_ViT_VLM_VisionLanguage.pptx | Vision Transformers, VLMs & Vision-Language |
| 13 | Lecture_13_Vision_Language_Action.pptx | Vision-Language-Action: Perception → Behaviour |
| 14 | Lecture_14_Capstone_Drone_Robot_Integration.pptx | Capstone — Drone/Robot-Integrated Vision |

## Deck structure (every lecture)
Title → Learning outcomes (CLO-tagged) → Roadmap → 4–5 content/diagram slides
→ Workshop (task + deliverable + code file) → Key takeaways → Materials.
**Speaker notes are on every slide** (open the Notes pane in PowerPoint).

## Design
- Theme: edge-AI — deep slate + teal, lime "detection-box" accent.
- Safe fonts (Calibri body, Century Schoolbook headers) so they render
  everywhere without substitution.
- Motif: numbered circles + rounded cards; varied layouts (two-column,
  process flow, stat callouts, the tier ladder).

## Rebrand / edit
- Content lives in `content.js`; layout/theme in `build_decks.js`.
- To rebrand (e.g. University of Lahore colours), edit the palette constants at
  the top of `build_decks.js` (INK / TEAL / LIME) and re-run:
  ```bash
  node build_decks.js
  ```
- To edit wording, change `content.js` and re-run — no need to touch layouts.
- Requires Node with `pptxgenjs` available.
