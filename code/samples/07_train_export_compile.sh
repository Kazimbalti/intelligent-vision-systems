#!/usr/bin/env bash
# Week 9 - Full deployment chain: train -> ONNX -> Hailo .hef -> deploy.
#
# This is a REFERENCE / RUNBOOK, not a one-click script. The Hailo Dataflow
# Compiler (DFC) commands vary by DFC / model-zoo version and require the Hailo
# Developer Zone download + a Docker environment. Run the TRAIN step on a GPU
# machine or Colab; run the COMPILE step in the Hailo Docker container; run the
# DEPLOY step on the Raspberry Pi.
#
# Golden rule: keep TRAINING and COMPILATION in separate containers/venvs.
# They have conflicting numpy/torch requirements.
set -e

# ----------------------------------------------------------------------------
# STEP 1 - TRAIN (GPU machine / Colab)   [pip install ultralytics]
# ----------------------------------------------------------------------------
# Prepare a YOLO-format dataset (Roboflow export or manual) with data.yaml.
yolo detect train \
    data=datasets/mydata/data.yaml \
    model=yolov8n.pt \
    epochs=100 imgsz=640 batch=16 \
    name=custom_yolov8n
# Best weights land in runs/detect/custom_yolov8n/weights/best.pt

# ----------------------------------------------------------------------------
# STEP 2 - EXPORT TO ONNX (same machine)
# ----------------------------------------------------------------------------
# opset 11 is a safe, widely-supported target for the Hailo parser.
yolo export \
    model=runs/detect/custom_yolov8n/weights/best.pt \
    format=onnx opset=11 imgsz=640
# -> runs/detect/custom_yolov8n/weights/best.onnx

# ----------------------------------------------------------------------------
# STEP 3 - COMPILE ONNX -> .hef  (Hailo DFC Docker container)
# ----------------------------------------------------------------------------
# Set --hw-arch to YOUR chip: hailo8, hailo8l, or hailo10h.
# The 'optimize' step quantises to int8 and needs a small calibration set
# (a folder of ~64-256 representative images from your dataset).
HW_ARCH=hailo8l
CALIB_DIR=datasets/mydata/calib

# 3a. Parse ONNX to Hailo Archive (.har)
hailo parser onnx best.onnx --hw-arch ${HW_ARCH} --har-path best.har

# 3b. Optimize/quantize using calibration images
hailo optimize best.har \
    --hw-arch ${HW_ARCH} \
    --calib-set-path ${CALIB_DIR} \
    --output-har-path best_optimized.har

# 3c. Compile to a deployable .hef
hailo compiler best_optimized.har \
    --hw-arch ${HW_ARCH} \
    --output-dir ./
# -> best.hef   (copy this to the Raspberry Pi)

# NOTE: the hailomz (model-zoo) wrapper can do 3a-3c in one command for
# supported architectures, e.g.:
#   hailomz compile yolov8n --hw-arch hailo8l --ckpt best.onnx \
#       --calib-path ${CALIB_DIR} --classes <N>
# Check `hailomz --help` for your version.

# ----------------------------------------------------------------------------
# STEP 4 - DEPLOY (Raspberry Pi + Hailo)
# ----------------------------------------------------------------------------
# Copy best.hef and a labels file to the Pi, then:
#   python 06_hailo_picamera2_detect.py --hef best.hef --labels mydata.txt --conf 0.4
echo "Done. Deploy best.hef on the Pi with 06_hailo_picamera2_detect.py"
