# BEST MATERIALS — vetted resources per lecture

Free/open unless noted. Verify version-specific pages before a live class;
edge-hardware software (HailoRT, picamera2, Edge Impulse) moves fast.

## Backbone references (whole course)
- **UMich EECS 498/598 — Deep Learning for Computer Vision** (Justin Johnson):
  slides, notes, 6 assignments, full video lectures.
  https://web.eecs.umich.edu/~justincj/teaching/eecs498/
- **Stanford CS231n** — notes + assignments: https://cs231n.github.io/
- **OpenCV University free courses / bootcamp** (applied):
  https://opencv.org/university/free-courses/
- **Szeliski, *Computer Vision: Algorithms and Applications*** (free PDF):
  https://szeliski.org/Book/
- **Ultralytics YOLO docs** (detection/seg/pose/track/export):
  https://docs.ultralytics.com/
- **Roboflow** (labelling + datasets + guides): https://roboflow.com/ ·
  https://blog.roboflow.com/

## L1 — Intelligent vision systems & the edge pipeline
- Raspberry Pi AI docs (Hailo): https://www.raspberrypi.com/documentation/computers/ai.html
- Raspberry Pi AI HAT+ hardware: https://www.raspberrypi.com/documentation/accessories/ai-hat-plus.html

## L2 — Image fundamentals & classical processing
- OpenCV Python tutorials (official): https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html
- OpenCV University free OpenCV course: https://opencv.org/university/free-opencv-course/

## L3 — Features, geometry & multi-view
- OpenCV feature matching & homography docs (in the tutorials above).
- Camera calibration (OpenCV): https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html

## L4 — Real-time capture & camera systems
- picamera2 manual + examples: https://github.com/raspberrypi/picamera2
- rpicam-apps / libcamera: https://www.raspberrypi.com/documentation/computers/camera_software.html

## L5 — Deep learning foundations (PyTorch)
- PyTorch "Learn the Basics": https://pytorch.org/tutorials/beginner/basics/intro.html
- 3Blue1Brown Neural Networks (intuition): https://www.3blue1brown.com/topics/neural-networks

## L6 — Classification, transfer learning & deployment
- torchvision models & transfer-learning tutorial:
  https://pytorch.org/tutorials/beginner/transfer_learning_tutorial.html
- Albumentations: https://albumentations.ai/
- Gradio: https://www.gradio.app/ · Hugging Face Spaces: https://huggingface.co/spaces

## L7 — Object detection I (architectures & YOLO family)
- YOLO26 launch + docs: https://www.ultralytics.com/blog/ultralytics-yolo26-the-new-standard-for-edge-first-vision-ai
- YOLO evolution survey (YOLO26/11/v8/v5): https://arxiv.org/abs/2510.09653
- RF-DETR: https://github.com/roboflow/rf-detr
- YOLOE (zero-shot / prompting) docs: https://docs.ultralytics.com/models/yoloe/

## L8 — Custom data + Hailo edge acceleration
- Roboflow labelling guide: https://blog.roboflow.com/how-to-label-data/
- Hailo RPi examples (maintained): https://github.com/hailo-ai/hailo-apps
- Hailo RPi5 examples (reference): https://github.com/hailo-ai/hailo-rpi5-examples
- Seeed wiki — YOLOv8n on Pi5 AI Kit (train→deploy):
  https://wiki.seeedstudio.com/tutorial_of_ai_kit_with_raspberrypi5_about_yolov8n_object_detection/
- Core Electronics — custom Python on the AI HAT+:
  https://core-electronics.com.au/guides/yolo-object-detection-on-the-raspberry-pi-ai-hat-writing-custom-python/
- VisDrone dataset: https://github.com/VisDrone/VisDrone-Dataset

## L9 — Tracking, counting & analytics
- Ultralytics tracking (ByteTrack/BoT-SORT): https://docs.ultralytics.com/modes/track/
- Ultralytics solutions (counting, speed, heatmaps): https://docs.ultralytics.com/solutions/
- ByteTrack paper/repo: https://github.com/ifzhang/ByteTrack

## L10 — Segmentation, pose & interaction
- Segment Anything (SAM): https://github.com/facebookresearch/segment-anything
- U-Net paper: https://arxiv.org/abs/1505.04597
- YOLO segmentation/pose docs: https://docs.ultralytics.com/tasks/
- MediaPipe (hands/face/pose): https://ai.google.dev/edge/mediapipe/solutions/guide

## L11 — TinyML on ESP32-CAM & Arduino
- Edge Impulse ESP32 docs: https://docs.edgeimpulse.com/hardware/boards/espressif-esp32
- FOMO on ESP32-CAM tutorial:
  https://www.makerguides.com/train-an-object-detection-model-with-edge-impulse-for-esp32-cam/
- Harvard/Google TinyML open courseware:
  https://github.com/tinyMLx/courseware/tree/master/edX

## L12 — Vision Transformers, VLMs & vision-language tasks
- ViT paper ("An Image is Worth 16×16 Words"): https://arxiv.org/abs/2010.11929
- CLIP: https://github.com/openai/CLIP · OpenCLIP: https://github.com/mlfoundations/open_clip
- Hugging Face vision-language models hub: https://huggingface.co/models?pipeline_tag=image-text-to-text
- Roboflow VLM guides: https://blog.roboflow.com/tag/multimodal/

## L13 — Vision-Language-Action (VLA)
- LeRobot (Hugging Face robotics / policies): https://github.com/huggingface/lerobot
- Diffusion Policy: https://diffusion-policy.cs.columbia.edu/
- Survey: "Vision-Language-Action Models" (search arXiv for the latest VLA survey)

## L14 — Drone/robot integration & capstone
- DJITelloPy (Tello Python SDK): https://github.com/damiafuentes/DJITelloPy
- ROS 2 docs: https://docs.ros.org/ · vision_msgs for detections:
  https://github.com/ros-perception/vision_msgs
- Ultralytics + ROS guide: https://docs.ultralytics.com/guides/ros-quickstart/

---

## How the uploaded reference courses map here
- *Big DL/CV course (Python→DL→OpenCV→PyTorch→architectures→detection→seg→deploy)*
  → L2, L5, L6, L7, L10, plus the Gradio/HF deployment in L6.
- *Modern YOLO course (YOLO26/v12/11/v8/v5, tracking, counting, OCR, aerial)*
  → L7, L8, L9.
- *OpenCV bootcamps (features, panorama, HDR, tracking, MediaPipe, depth, sports)*
  → L2, L3, L9, L10.
- *ViT & VLM applied course (ViT, SAM, CLIP, VQA, CCTV/retail/real-estate)*
  → L12.
- *VLA / robot-learning course (MDP, attention, diffusion policies, world models)*
  → L13.
- *Arduino GUI / ESP32 project course (object counter, gesture, pan-tilt, door lock)*
  → L11.
- *Drone programming courses (face/body/hand, AI drone, Tello, educator projects)*
  → L13, L14 + Appendix B brief bank.
