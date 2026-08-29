const fs = require("fs");
const docx = require("docx");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Table, TableRow, TableCell, WidthType, BorderStyle, ShadingType, PageBreak,
  LevelFormat, PageOrientation,
} = docx;

const TEAL = "0E7C86", INK = "0E2233", MUTE = "5B6470", LIME = "4E6E10", LIGHT = "EAF3F5", GOLD = "8A5A00";
const F = "Calibri";

const shd = (f) => ({ type: ShadingType.CLEAR, fill: f, color: "auto" });
const T = (t, o = {}) => new TextRun({ text: t, font: F, size: o.size ?? 21, bold: o.bold, italics: o.it, color: o.color ?? "222222" });
const P = (runs, o = {}) => new Paragraph({ spacing: { after: o.after ?? 100, before: o.before ?? 0, line: o.line ?? 264 },
  alignment: o.align, children: (Array.isArray(runs) ? runs : [T(runs, o)]) });
const H1 = (t) => new Paragraph({ spacing: { before: 240, after: 120 }, keepNext: true,
  border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: TEAL } },
  children: [new TextRun({ text: t, font: F, size: 28, bold: true, color: TEAL })] });
const H2 = (t, c) => new Paragraph({ spacing: { before: 160, after: 60 }, keepNext: true,
  children: [new TextRun({ text: t, font: F, size: 23, bold: true, color: c ?? INK })] });
const bullet = (runs, o = {}) => new Paragraph({ numbering: { reference: "b", level: 0 }, spacing: { after: 50, line: 258 },
  children: Array.isArray(runs) ? runs : [T(runs, o)] });
const cell = (kids, w, o = {}) => new TableCell({ width: { size: w, type: WidthType.DXA }, shading: o.fill ? shd(o.fill) : undefined,
  verticalAlign: o.v, margins: { top: 60, bottom: 60, left: 90, right: 90 },
  children: Array.isArray(kids) ? kids : [kids] });
const tp = (runs, o = {}) => new Paragraph({ spacing: { after: o.after ?? 20, line: 240 }, alignment: o.align, children: runs });
const tt = (t, o = {}) => new TextRun({ text: t, font: F, size: o.size ?? 16, bold: o.bold, italics: o.it, color: o.color ?? "222222" });

// ===================== FRONT MATTER (portrait) =====================
const front = [];
front.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 30 },
  children: [new TextRun({ text: "Intelligent Vision Systems", bold: true, font: F, size: 40, color: TEAL })] }));
front.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 40 },
  children: [new TextRun({ text: "Course Schedule, Raspberry Pi 5 Laboratory Plan & Project Bank", font: F, size: 23, it: true, color: INK })] }));
front.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 160 },
  border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: TEAL } },
  children: [new TextRun({ text: "BSES · 7th Semester · Section A   •   University of Lahore   •   Fall 2026", font: F, size: 18, color: MUTE })] }));

const info = [
  ["Course", "Intelligent Vision Systems (Applied Computer Vision)"],
  ["Program / class", "BSES, 7th Semester, Section A"],
  ["Instructor", "Dr. Muhammad Kazim — Assistant Professor, Department of Intelligent Systems, University of Lahore (muhammad.kazim@is.uol.edu.pk)"],
  ["Semester", "31 August – 14 December 2026 (16 weekly sessions)"],
  ["Meeting", "Mondays, 2:00–5:00 PM  ·  E1-404 Lab  ·  3 hours = 1.5 h theory + 1.5 h laboratory"],
  ["Platform", "Raspberry Pi 5 (+ AI HAT / Hailo, Pi Camera, ESP32-CAM); Python, OpenCV, PyTorch/TensorFlow, Ultralytics YOLO; Google Colab for training"],
  ["Prerequisites", "Python programming; basic linear algebra & probability"],
  ["Texts", "Szeliski, Computer Vision 2e (S) · Gonzalez & Woods, Digital Image Processing 4e (G&W) · Goodfellow et al., Deep Learning"],
];
front.push(new Table({ width: { size: 9500, type: WidthType.DXA }, columnWidths: [2200, 7300],
  rows: info.map(([k, v]) => new TableRow({ children: [
    cell(P([T(k, { bold: true, color: INK })], { after: 0 }), 2200, { fill: LIGHT }),
    cell(P([T(v)], { after: 0 }), 7300) ] })) }));

// CLOs (from course intro)
front.push(H1("Course Learning Outcomes"));
[
  "Explain the fundamentals of image formation, sensing, representation, colour, and processing.",
  "Apply filtering, convolution, frequency-domain analysis, edge detection, and Hough methods.",
  "Detect, describe, and match visual features and estimate geometric transforms robustly.",
  "Apply camera geometry, calibration, stereo vision, and motion estimation for 3-D and dynamic scenes.",
  "Implement classical recognition/detection (e.g. HOG, Haar, SIFT) and evaluate them.",
  "Apply machine and deep learning to image classification, object detection, tracking, and segmentation.",
  "Develop, deploy, and evaluate real-time computer-vision pipelines on embedded hardware (Raspberry Pi 5).",
].forEach((c, i) => front.push(bullet([T("CLO" + (i + 1) + " — ", { bold: true, color: TEAL }), T(c)])));

// Grading
front.push(H1("Assessment & Grading"));
front.push(P([T("Each 3-hour Monday session pairs a "), T("1.5-hour theory lecture", { bold: true }), T(" with a "), T("1.5-hour supervised laboratory", { bold: true }), T(" on the Raspberry Pi 5. Marks are distributed as follows:")]));
const grade = [
  ["Assessment", "Marks", "Coverage"],
  ["Final Exam", "40", "Cumulative; weighted toward recognition, deep learning & embedded deployment (Weeks 10–16)"],
  ["Midterm Exam", "20", "Week 8 — image formation, processing, features, matching & RANSAC (Weeks 1–8)"],
  ["Lab Project (capstone)", "30", "End-to-end vision system deployed on the Raspberry Pi 5 + demo & report"],
  ["Quizzes / Assignments", "10", "Four assignments + periodic quizzes across the semester"],
  ["Total", "100", ""],
];
front.push(new Table({ width: { size: 9500, type: WidthType.DXA }, columnWidths: [2900, 1100, 5500],
  rows: grade.map((r, i) => new TableRow({ children: r.map((c, j) => cell(
    P([T(c, { bold: i === 0 || i === grade.length - 1, color: i === 0 ? "FFFFFF" : (j === 1 ? TEAL : "222222") })],
      { after: 0, align: j === 1 ? AlignmentType.CENTER : undefined }),
    [2900, 1100, 5500][j], { fill: i === 0 ? TEAL : (i === grade.length - 1 ? LIGHT : (i % 2 ? "FFFFFF" : "F4F8F9")) })) })) }));
front.push(P([T("Grading note: ", { bold: true }), T("the Lab Project (30) is the capstone system demonstrated live on target hardware in Week 16; the four assignments and quizzes together carry 10 marks. Weekly lab deliverables are checkpoints toward the capstone and count within lab participation.", { it: true, color: MUTE })], { before: 80 }));

// ===================== SCHEDULE (landscape) =====================
const weeks = [
["1","Mon 31 Aug","L1–L2 — Introduction & Image Formation I","What an intelligent vision system is; acquire → process → analyse → decide → act; edge/embedded constraints; the human visual system; optics & projection: radiometry, lenses, aperture, depth of field, pinhole & thin-lens models, perspective projection, exposure & motion blur.","Lab 1 — Raspberry Pi 5 & Embedded Systems I: OS install, headless SSH/VNC, Python env, GPIO & embedded-vision overview.","Lab 1 out · S 1–2.2"],
["2","Mon 7 Sep","L3–L4 — Image Formation II & Digital Fundamentals","CCD vs CMOS; Bayer CFA & demosaicing; the ISP pipeline; rolling shutter; gain/ISO/read noise; HDR capture. Sampling & quantisation; resolution & bit depth; pixel neighbourhoods/connectivity; distance metrics; colour spaces (RGB, HSV, YCbCr, Lab).","Lab 2 — RPi 5 & Embedded II: install & verify OpenCV 5.0 (note key v4→v5 changes); Pi camera stack (libcamera/picamera2), image & video I/O on the Pi, capture FPS.","Lab 2 out · S 2.3 · G&W 2.4–2.6"],
["3","Mon 14 Sep","L5–L6 — Point Operations & Thresholding","LUTs; gamma/log maps; contrast stretching; histogram equalisation/matching; CLAHE. Global, Otsu, adaptive & Sauvola thresholding; image arithmetic, blending, alpha compositing; bitwise masks; frame differencing.","Lab 3 — CV Fundamentals I: load/save images & videos, drawing functions, basic image operations.","Lab 3 · Assign. 1 out · G&W 3.1–3.3"],
["4","Mon 21 Sep","L7–L8 — Spatial Filtering I & II","Correlation vs convolution; box & Gaussian smoothing; kernel separability; border handling; integral images & O(1) box filters. Sharpening/unsharp masking; Laplacian; gradients (Sobel, Prewitt, Scharr); non-linear filters (median, bilateral, guided).","Lab 4 — CV Fundamentals II: arithmetic & bitwise operations, HSV colour space & colour detection, thresholding.","Lab 4 · Assign. 1 due · G&W 3.4–3.6"],
["5","Mon 28 Sep","L9–L10 — Frequency Domain & Pyramids","1D/2D DFT & FFT; reading a spectrum; the convolution theorem; ideal/Butterworth/Gaussian low-, high- & band-pass; notch filtering; ringing. 2D sampling theorem; aliasing & anti-aliasing; Gaussian & Laplacian pyramids; coarse-to-fine processing.","Lab 5 — CV Fundamentals III: find & draw contours, contour features, background subtraction.","Lab 5 out · G&W 4 · S 3.5"],
["6","Mon 5 Oct","L11–L12 — Restoration & Morphology","Noise models (Gaussian, salt-and-pepper, Poisson, speckle); inverse & Wiener filtering; non-local means; total-variation denoising; PSNR/SSIM. Erosion, dilation, opening, closing; structuring elements; hit-or-miss; connected components; distance transform; skeletonisation.","Lab 6 — Filtering, edges & morphology on the Pi: smoothing/sharpening, Sobel/Canny, morphological pipeline on live video.","Lab 6 · Assign. 2 out · G&W 5, 9"],
["7","Mon 12 Oct","L13–L14 — Edges/Contours & Local Features","Canny in depth; Hough transform for lines & circles; contour tracing; polygon approximation; region descriptors — moments, Hu invariants; shape matching. Harris & Shi–Tomasi corners; scale space; DoG blob detection; FAST; repeatability & invariance.","Lab 7 — Features & matching: corners/keypoints, ORB/SIFT descriptors, feature matching, Hough lines/circles.","Lab 7 · Assign. 2 due · S 7.1–7.3"],
["8","Mon 19 Oct","L15–L16 — Descriptors, Matching & RANSAC","SIFT, SURF, ORB, BRIEF; ratio test & cross-check; brute-force vs FLANN; Hamming distance; why binary descriptors suit embedded targets. 2D transform families; homography by the DLT; robust fitting (RANSAC/MSAC); alignment; panorama stitching & blending.","Lab 8 — Geometry: homography + RANSAC, panorama stitching, camera calibration & undistortion.","MIDTERM (20) · Lab 8 · S 8.1–8.2"],
["9","Mon 26 Oct","L17–L18 — Segmentation I & II","Region growing & split/merge; k-means & mean-shift in colour space; SLIC superpixels; IoU/Dice evaluation. Watershed; graph cuts & GrabCut; active contours (snakes); grouping cues; from hand-designed masks to learned segmentation (bridge to U-Net).","Lab 9 — Build a real-world CV system: plan & architecture, measure object size (2-D), defect-recognition system, database integration.","Lab 9 · Project proposal due · S 7.5"],
["10","Mon 2 Nov","L19–L20 — Calibration & Stereo","Intrinsic/extrinsic parameters; lens distortion models; Zhang's planar calibration; reprojection error; undistortion & rectification. Epipolar geometry; fundamental & essential matrices; rectification; block-matching & SGBM disparity; depth from disparity; RGB-D sensors.","Lab 10 — Calibration, stereo & depth on the Pi.","Lab 10 out · S 11.1–12.1"],
["11","Mon 9 Nov","L21–L22 — Optical Flow & Tracking","Brightness constancy & the aperture problem; Lucas–Kanade & Horn–Schunck; pyramidal KLT tracking; dense flow (Farnebäck). Background subtraction (MOG2, KNN); the Kalman filter; mean-shift/CAMShift; correlation trackers (KCF, CSRT); tracking-by-detection & SORT; MOT metrics.","Lab 11 — Motion & tracking: optical flow, OC-SORT & Strong-SORT tracking, object trajectory & speed estimation, line-crossing counting.","Lab 11 · Assign. 3 out · S 9.3–9.4"],
["12","Mon 16 Nov","L23–L24 — Classical Recognition & Neural Networks","Sliding-window paradigm; HOG + linear SVM (pedestrian detection); Haar cascades (Viola–Jones); bag-of-visual-words & spatial pyramids. Perceptron → MLP; loss functions; back-propagation; SGD, momentum, Adam; over-fitting, regularisation, augmentation; train/val/test discipline.","Lab 12 — Deep learning: image classification (transfer learning) + YOLO object detection on image/video/camera, custom training on Colab, SAHI, pose.","Lab 12 · Assign. 3 due · Goodfellow 6–8"],
["13","Mon 23 Nov","L25–L26 — CNNs, Segmentation Networks & Reading Research Papers","Convolution & pooling; receptive fields; batch norm; LeNet → ResNet → MobileNet → EfficientNet; transfer learning; two-stage (Faster R-CNN) vs one-stage (SSD, YOLO) detection; semantic segmentation (FCN, U-Net, DeepLab); Mask R-CNN; mAP. How to read a research paper and reproduce a model architecture from scratch — method with worked examples.","Lab 13 — Paper Implementation I: U-Net from scratch (PyTorch) — read the paper, build the encoder–decoder with skip connections, train for segmentation (IoU/Dice).","Lab 13 · Assign. 4 out · Ronneberger 2015 · S 5.3"],
["14","Mon 30 Nov","L27–L28 — Edge Vision & the OpenCV 5.0 Deep Dive","Accelerators (GPU, NPU, DSP, FPGA); inference runtimes (TensorRT, TFLite, ONNX Runtime, OpenVINO, Hailo); memory hierarchy, DMA, zero-copy; latency/throughput/power; PTQ vs QAT, INT8/FP16, pruning, distillation, operator fusion. OpenCV 5.0 deep dive: modernised architecture; the new DNN engine; ONNX & modern DL workflows; hardware acceleration (CPU/GPU/AI accelerators); breaking changes & migration from OpenCV 4; performance optimisation.","Lab 14 — Modern deployment on RPi 5: OpenCV 5.0 pipeline migration + CascadeClassifier fix; YOLOv8n ONNX detection with the new DNN engine; export to TFLite/ONNX, run on ONNX Runtime / Hailo, INT8 quantisation, benchmark.","Lab 14 · Assign. 4 due · OpenCV 5 · TinyML"],
["15","Mon 7 Dec","L29–L30 — Vision Transformers, Advanced Topics & Review","Vision transformers & self-supervised learning; multimodal & open-vocabulary models; event cameras; a SLAM overview; ethics, privacy, dataset bias, safety & robustness. Course wrap-up and final-exam review.","Lab 15 — Paper Implementation II: the Transformer (\"Attention Is All You Need\") from scratch (PyTorch) — attention, multi-head, positional encoding, encoder/decoder; bridge to ViT.","Project report due · Vaswani 2017 · S 5.5, 14.x"],
["16","Mon 14 Dec","Capstone Demos & Review","Live demonstration of the capstone vision system on Raspberry Pi 5 target hardware; short talk + Q&A; peer review; final-exam review.","Capstone project demonstrations (Lab Project, 30 marks).","Capstone demos · Final Exam (40, finals week)"],
];

const schedule = [];
schedule.push(new Paragraph({ spacing: { after: 100 }, children: [new TextRun({ text: "16-Week Lecture & Laboratory Schedule", font: F, size: 30, bold: true, color: TEAL })] }));
schedule.push(new Paragraph({ spacing: { after: 120 }, children: [new TextRun({ text: "Each week: 1.5 h theory (lecture) + 1.5 h laboratory on the Raspberry Pi 5. Dates assume a Monday start on 31 Aug 2026 — replace with official academic-calendar dates and insert holiday rows as needed. Reading keys: S = Szeliski 2e, G&W = Gonzalez & Woods 4e.", font: F, size: 16, it: true, color: MUTE })] }));

const cols = [520, 1080, 6500, 5300, 1700];
const head = new TableRow({ tableHeader: true, children:
  ["Wk", "Date", "Lecture & theory topics (1.5 h)", "Laboratory — Raspberry Pi 5 (1.5 h)", "Assessment / reading"]
  .map((h, j) => cell(tp([tt(h, { bold: true, color: "FFFFFF", size: 17 })]), cols[j], { fill: TEAL, v: "center" })) });
const rows = weeks.map((w, i) => {
  const bg = i % 2 ? "FFFFFF" : "F4F8F9";
  const exam = /MIDTERM|Final Exam|Capstone demos/.test(w[5]);
  return new TableRow({ children: [
    cell(tp([tt(w[0], { bold: true, color: INK })], { align: AlignmentType.CENTER }), cols[0], { fill: bg, v: "center" }),
    cell(tp([tt(w[1])]), cols[1], { fill: bg, v: "center" }),
    cell([tp([tt(w[2] + ". ", { bold: true, color: INK })]), tp([tt(w[3])], { after: 0 })], cols[2], { fill: bg }),
    cell(tp([tt(w[4])], { after: 0 }), cols[3], { fill: bg, v: "center" }),
    cell(tp([tt(w[5], { bold: exam, color: exam ? GOLD : MUTE })], { after: 0 }), cols[4], { fill: bg, v: "center" }) ] });
});
schedule.push(new Table({ width: { size: cols.reduce((a, b) => a + b), type: WidthType.DXA }, columnWidths: cols, rows: [head, ...rows] }));

// ===================== LABS + PROJECTS (portrait) =====================
const back = [];
back.push(H1("Laboratory Programme (Raspberry Pi 5)"));
back.push(P([T("All labs run on the Raspberry Pi 5. The first two labs bring up the embedded platform; Labs 3–8 build the classical-vision toolbox; Labs 9–12 build real, deployable systems; "), T("Labs 13 and 15 are research-paper implementation labs", { bold: true }), T(" (U-Net and the Transformer, built from scratch); Lab 14 covers edge deployment — culminating in the capstone. Each lab has an objective, tasks, and a deliverable checked in the session.")]));
back.push(H2("Reading & implementing research papers (method)", TEAL));
back.push(P([T("Two mid-semester labs (after the midterm) teach how to turn a paper into working code. We practise a repeatable, five-step method on two landmark architectures — reading each paper together and building the model from scratch in PyTorch:")], { after: 40 }));
["Skim first — read the abstract, figures and conclusion to grasp the problem and the key idea before touching any equation.",
 "Map the architecture — turn the model figure into a block diagram: inputs, layers, tensor shapes, and how blocks connect.",
 "Extract the maths — write down the core equations (e.g. scaled dot-product attention, the segmentation loss) and exact layer dimensions.",
 "Implement from scratch — build each block in PyTorch, checking tensor shapes at every step against the paper.",
 "Reproduce & verify — train on a small dataset, compare behaviour/metrics to the paper, and note any gaps or simplifications.",
].forEach((x) => back.push(bullet(x)));
back.push(P([T("Target papers: ", { bold: true }), T("(1) Ronneberger et al., \u201CU-Net\u201D (2015) \u2014 Lab 13;  (2) Vaswani et al., \u201CAttention Is All You Need\u201D (2017) \u2014 Lab 15. Each lab produces working code plus a one-page paper summary.")], { before: 40, after: 60 }));
back.push(H2("Featured deep dive \u2014 OpenCV 5.0 (Week 14 / Lab 14)", TEAL));
back.push(P([T("OpenCV has underpinned computer vision for two decades; OpenCV 5.0 brings a modernised architecture, a redesigned DNN engine, first-class ONNX support and stronger hardware acceleration \u2014 with API changes that affect existing code. We cover it directly in Week 14 and use it in the lab:")], { after: 40 }));
["Introduction & architecture \u2014 why OpenCV 5 was introduced and what changed.",
 "Breaking changes & modules \u2014 deprecated APIs, moved modules, compatibility considerations.",
 "The new DNN engine \u2014 ONNX support, modern deep-learning workflows and performance gains.",
 "Data types & hardware \u2014 optimisations for CPUs, GPUs and AI accelerators.",
 "Migration strategies \u2014 upgrading OpenCV 4 applications with recommended best practices.",
 "Live/lab demos \u2014 OpenCV 5 install, pipeline migration, CascadeClassifier fixes, and YOLOv8n ONNX detection.",
].forEach((x) => back.push(bullet(x)));
back.push(P([T("Outcome: ", { bold: true }), T("students can confidently migrate, optimise and modernise production computer-vision pipelines with OpenCV 5.", { it: true, color: MUTE })], { before: 40, after: 60 }));
const labs = [
["1","Raspberry Pi 5 & Embedded Systems I — Setup","Flash Raspberry Pi OS (64-bit); headless SSH & VNC; system update & Python virtual environment; GPIO and basic embedded I/O; overview of embedded-vision constraints (compute, memory, power).","A booted, updated Pi with a working OpenCV/Python environment + a short setup report."],
["2","Raspberry Pi 5 & Embedded Systems II — Camera, I/O & OpenCV 5.0","Install & verify OpenCV 5.0 (note key OpenCV 4→5 changes); connect and configure the Pi camera (libcamera/picamera2); read/write images and video on the Pi; remote development workflow; measure capture FPS and latency.","A live capture application on OpenCV 5.0 + an FPS/latency note."],
["3","CV Fundamentals I — Images, Video & Drawing","Load and save images; load and save videos; drawing functions (lines, shapes, text); basic operations (resize, crop, rotate, ROI).","An image/video I/O utility with on-frame annotations."],
["4","CV Fundamentals II — Colour, Arithmetic & Thresholding","Arithmetic and bitwise operations; masks; the HSV colour space and colour detection; global/Otsu/adaptive threshold operations.","An HSV colour detector + a thresholding app."],
["5","CV Fundamentals III — Contours & Motion","Find and draw contours; contour features (area, perimeter, bounding boxes, polygon approximation); background subtraction and frame differencing.","A contour-based object counter + a motion detector."],
["6","Filtering, Edges & Morphology","Smoothing and sharpening filters; Sobel and Canny edges; morphological operations (open/close); histogram equalisation & CLAHE — all on live Pi video.","A tunable, real-time processing pipeline."],
["7","Features & Matching","Harris/Shi–Tomasi corners; ORB/SIFT descriptors; brute-force & FLANN matching; Hough lines and circles.","A feature-matching + shape-detection application."],
["8","Geometry — Homography, Panorama & Calibration","Estimate a homography with RANSAC; stitch a panorama; calibrate the Pi camera and undistort frames.","A stitched panorama + a saved camera-intrinsics file."],
["9","Build a Real-World CV System","Plan the project and design its architecture; measure the size of an object in 2-D (using calibration); build a defect-recognition system; integrate a database (SQLite/MySQL) to log results.","An end-to-end measuring / defect system logging to a database."],
["10","Stereo & Depth","Stereo calibration; disparity via block-matching/SGBM; build a depth map; (optional) monocular depth estimation.","A depth/disparity map on a real scene."],
["11","Tracking & Analytics","Optical flow / KLT; tracking-by-detection with OC-SORT and Strong-SORT; object trajectory; speed estimation; people/vehicle line-crossing counting.","A tracking + counting + speed application."],
["12","Deep Learning — Classification & YOLO Detection","Classify images with a pretrained model and train a custom classifier by transfer learning (Colab, free GPU); then detect objects on image/video/camera with YOLO, train a custom detector, and try SAHI (small objects) and pose.","A trained custom classifier + a custom YOLO detector running on the Pi."],
["13","Paper Implementation I — U-Net from Scratch","Read \u201CU-Net: Convolutional Networks for Biomedical Image Segmentation\u201D (Ronneberger et al., 2015); understand the contracting/expanding paths and skip connections; implement the full architecture from scratch in PyTorch; train on a small segmentation dataset; evaluate with IoU/Dice and compare against a library U-Net.","A from-scratch U-Net that segments a dataset + a one-page paper summary."],
["14","Modern Deployment with OpenCV 5.0 & Edge Runtimes","OpenCV 5.0 on the Pi: migrate an OpenCV 4 pipeline (deprecated APIs, moved modules), fix a CascadeClassifier call, and run YOLOv8n via ONNX in the new DNN engine with hardware acceleration. Then export to TFLite/ONNX, run on ONNX Runtime / Hailo, apply INT8 quantisation, and benchmark latency, throughput and power vs the CPU baseline.","A migrated OpenCV 5 pipeline + YOLOv8n ONNX detection + a quantised model with a benchmark table."],
["15","Paper Implementation II — Transformer from Scratch","Read \u201CAttention Is All You Need\u201D (Vaswani et al., 2017); implement scaled dot-product attention, multi-head attention, positional encoding and the encoder/decoder blocks from scratch in PyTorch; train on a toy sequence task; connect the mechanism to Vision Transformers (ViT).","A working from-scratch Transformer + a paper summary bridging to ViT."],
];
labs.forEach((l) => {
  back.push(new Paragraph({ spacing: { before: 120, after: 30 }, keepNext: true,
    children: [T("Lab " + l[0] + " — ", { bold: true, color: TEAL, size: 22 }), T(l[1], { bold: true, color: INK, size: 22 })] }));
  back.push(P([T("Tasks: ", { bold: true }), T(l[2])], { after: 20, line: 258 }));
  back.push(P([T("Deliverable: ", { bold: true, color: LIME }), T(l[3], { it: true })], { after: 40, line: 258 }));
});
back.push(new Paragraph({ spacing: { before: 120, after: 30 }, children: [T("Capstone (Week 16) — ", { bold: true, color: TEAL, size: 22 }), T("Deployed vision system on the Raspberry Pi 5", { bold: true, color: INK, size: 22 })] }));
back.push(P([T("Integrate the semester's skills into one complete, real-time system deployed on the Pi; demonstrate live with a short talk, Q&A and peer review. "), T("Assessed as the Lab Project (30 marks).", { bold: true })]));

// Assignments
back.push(H1("Assignment Bank"));
back.push(P([T("Four graded assignments plus periodic quizzes make up the 10-mark Quizzes/Assignments component. Assignments are individual unless stated.")]));
[
["Assignment 1","Image processing","Apply point operations, histogram equalisation/CLAHE and thresholding to a supplied dataset; compare methods quantitatively. (Out Wk 3, due Wk 4.)"],
["Assignment 2","Filtering & features","Implement and compare smoothing/edge filters and a feature matcher (ORB/SIFT); report robustness to noise and rotation. (Out Wk 6, due Wk 7.)"],
["Assignment 3","Motion & tracking","Implement optical flow and a tracking-by-detection pipeline; evaluate with simple MOT metrics on a short clip. (Out Wk 11, due Wk 12.)"],
["Assignment 4","Deep detection","Train a custom YOLO detector on a chosen dataset, report mAP, and write a deployment note for the Raspberry Pi 5. (Out Wk 13, due Wk 14.)"],
].forEach((a) => back.push(bullet([T(a[0] + " — " + a[1] + ": ", { bold: true, color: INK }), T(a[2])])));
back.push(P([T("Quizzes: ", { bold: true }), T("short in-class quizzes at the start of selected sessions test the previous week's theory (best scores counted).", { it: true, color: MUTE })], { before: 60 }));

// Project bank
back.push(H1("Advanced Project Bank"));
back.push(P([T("Students are assigned one advanced project (Lab 15) that grows into the capstone (Lab Project, 30 marks). Every project must run on the Raspberry Pi 5, include a simple GUI or dashboard, and log results. Projects are grouped by theme; each can be scaled up (edge deployment, multi-camera, alerting) for a higher grade.")]));
const groups = [
["Detection, counting & monitoring", "Real-time object detection (YOLOv7/v8/v11/YOLO26) · weapon detection · people entry/exit counting (smart occupancy) · intrusion / zone monitoring · PPE-compliance detection · animal detection · vehicle traffic monitoring · smart parking (slot occupancy)."],
["Recognition & classification", "Face-recognition attendance system · facial-emotion detection · age & gender detection · traffic-sign recognition (EfficientNet) · face-mask detection · driver-distraction classification (ResNet-50)."],
["Tracking & analytics", "Vehicle speed tracking (calibrated) · licence-plate detection + recognition (OCR / VLM) · object trajectory & multi-object tracking (OC-SORT / Strong-SORT) · measure object size in 2-D."],
["Pose, gesture & safety", "Driver-drowsiness detection (EAR/MAR) · human-fitness / exercise-rep tracking (pose) · fall-detection + alert · hand-gesture recognition & control."],
["Systems & IoT integration", "AI accident detection with MQTT alerting · defect-recognition with database logging · Flask/Tkinter dashboards · edge deployment with quantisation & benchmarking."],
];
groups.forEach((g) => back.push(bullet([T(g[0] + ": ", { bold: true, color: TEAL }), T(g[1])])));
back.push(P([T("Challenge tier (bonus): ", { bold: true, color: GOLD }), T("a custom visual-classification feature, video-based detection monitoring, or a full end-to-end custom vision system — designed with the instructor.")], { before: 80 }));

// References
back.push(H1("Reference Materials"));
back.push(H2("Textbooks"));
[["Richard Szeliski", "Computer Vision: Algorithms and Applications, 2e — szeliski.org/Book"],
 ["Gonzalez & Woods", "Digital Image Processing, 4e"],
 ["Goodfellow, Bengio & Courville", "Deep Learning — deeplearningbook.org"],
].forEach(([a, b]) => back.push(bullet([T(a + " — ", { bold: true }), T(b)])));
back.push(H2("Open university courses"));
[["Cornell CS5670", "cs.cornell.edu/courses/cs5670"],
 ["UW CSE455", "courses.cs.washington.edu/courses/cse455"],
 ["UMich EECS 498 — Deep Learning for CV", "web.eecs.umich.edu/~justincj/teaching/eecs498"],
 ["Stanford CS231n", "cs231n.github.io"],
].forEach(([n, u]) => back.push(bullet([T(n + " — "), T(u, { color: TEAL })])));
back.push(H2("Key research papers (implementation labs)"));
[["Vaswani et al. (2017)", "\u201CAttention Is All You Need\u201D — arxiv.org/abs/1706.03762  (Lab 15: Transformer from scratch)"],
 ["Ronneberger et al. (2015)", "\u201CU-Net: Convolutional Networks for Biomedical Image Segmentation\u201D — arxiv.org/abs/1505.04597  (Lab 13: U-Net from scratch)"],
].forEach(([a, b]) => back.push(bullet([T(a + " — ", { bold: true }), T(b)])));
back.push(H2("Tools & platforms"));
[["Ultralytics YOLO (incl. YOLO26)", "docs.ultralytics.com"],
 ["Raspberry Pi AI / Hailo", "raspberrypi.com/documentation/computers/ai.html"],
 ["OpenCV 5.0 (docs & 4\u21925 migration guide)", "docs.opencv.org"],
 ["Roboflow (labelling & datasets)", "roboflow.com"],
 ["Google Colab (free GPU training)", "colab.research.google.com"],
].forEach(([n, u]) => back.push(bullet([T(n + " — "), T(u, { color: TEAL })])));
back.push(P([T("Note: ", { bold: true }), T("dates are illustrative; align them to the official University of Lahore academic calendar and insert public-holiday / mid-term-break rows. Model and tool versions move quickly — reconfirm YOLO26, OpenCV 5.0, Hailo and library versions before each offering.", { it: true, color: MUTE })], { before: 120 }));

// ===================== DOCUMENT =====================
const A4 = { width: 11906, height: 16838 };
const doc = new Document({
  numbering: { config: [{ reference: "b", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
    style: { run: { color: TEAL }, paragraph: { indent: { left: 340, hanging: 200 } } } }] }] },
  styles: { default: { document: { run: { font: F, size: 21 } } } },
  sections: [
    { properties: { page: { size: A4, margin: { top: 1000, bottom: 900, left: 1080, right: 1080 } } }, children: front },
    { properties: { page: { size: { ...A4, orientation: PageOrientation.LANDSCAPE }, margin: { top: 720, bottom: 700, left: 720, right: 720 } } }, children: schedule },
    { properties: { page: { size: A4, margin: { top: 1000, bottom: 900, left: 1080, right: 1080 } } }, children: back },
  ],
});
Packer.toBuffer(doc).then((b) => { fs.writeFileSync("Intelligent_Vision_Systems_Schedule_and_Labs.docx", b); console.log("wrote", b.length); });
