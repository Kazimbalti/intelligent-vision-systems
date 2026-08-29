const fs = require("fs");
const docx = require("docx");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Table, TableRow, TableCell, WidthType, BorderStyle, ShadingType, PageBreak,
  LevelFormat,
} = docx;

const TEAL = "0E7C86", INK = "0E2233", MUTE = "5B6470", LIME = "5C7A12", LIGHT = "EAF3F5";
const FONT = "Calibri";

// ---------- helpers ----------
const H = (text, level) => new Paragraph({ heading: level, spacing: { before: 240, after: 120 },
  children: [new TextRun({ text, font: FONT, color: level === HeadingLevel.HEADING_1 ? TEAL : INK })] });

const P = (runs, opts = {}) => new Paragraph({
  spacing: { after: opts.after ?? 100, before: opts.before ?? 0, line: 276 },
  alignment: opts.align, children: (Array.isArray(runs) ? runs : [runs]).map(r =>
    typeof r === "string" ? new TextRun({ text: r, font: FONT, size: opts.size ?? 21, color: opts.color ?? "222222" }) : r) });

const T = (text, o = {}) => new TextRun({ text, font: FONT, size: o.size ?? 21, bold: o.bold, italics: o.italics, color: o.color ?? "222222" });

const bullet = (text, o = {}) => new Paragraph({ numbering: { reference: o.num ?? "bullets", level: 0 },
  spacing: { after: 60, line: 264 }, children: (Array.isArray(text) ? text : [T(text, o)]) });

const cell = (children, w, shade) => new TableCell({
  width: { size: w, type: WidthType.DXA },
  shading: shade ? { type: ShadingType.CLEAR, fill: shade, color: "auto" } : undefined,
  margins: { top: 80, bottom: 80, left: 120, right: 120 },
  children: Array.isArray(children) ? children : [children] });

// ---------- data: 15 lectures ----------
const parts = [
  ["PART I — Foundations & Classical Vision", [1, 2, 3]],
  ["PART II — Geometry & Multi-View", [4, 5, 6]],
  ["PART III — Deep Learning for Vision", [7, 8, 9]],
  ["PART IV — Detection, Tracking & Recognition", [10, 11, 12, 13]],
  ["PART V — Vision-Based Drone Projects (Capstone Labs)", [14, 15]],
];

const L = {
1: { t: "Introduction & Image Formation",
  th: ["What is computer / intelligent vision; a brief history and the human-vs-machine vision analogy",
       "Image formation: light, lens, sensor, digital images; resolution, colour spaces (RGB/BGR/HSV/grayscale)",
       "The edge-AI stack (ESP32-CAM → Pi 5 CPU → Hailo NPU → drone) and course toolchain; ethics of vision"],
  pr: "Environment setup (Python, OpenCV, Colab); read/convert/annotate images; build an HSV colour-detection app.",
  d: "A working colour detector + a 2×2 image montage (original / gray / HSV / annotated)." },
2: { t: "Image Filtering, Edges & Enhancement",
  th: ["Convolution and linear systems; smoothing (box/Gaussian/median) and sharpening",
       "Gradients and edges: Sobel, Laplacian, Canny; image pyramids and resampling",
       "Histograms, equalisation, CLAHE; thresholding (Otsu/adaptive) and morphology"],
  pr: "Build an interactive processing pipeline (blur → threshold → morphology → Canny) with contour extraction.",
  d: "A tuned pipeline that segments an object under two lighting conditions + a short failure analysis." },
3: { t: "Features, Keypoints & Matching",
  th: ["Corner detection (Harris); scale and rotation invariance",
       "Feature descriptors (SIFT / ORB) and feature matching (brute-force, ratio test)",
       "Line and shape detection with the Hough transform"],
  pr: "Detect and match ORB keypoints between two views; build a line/shape-detection app.",
  d: "A feature-matching visualisation + a working shape/line detector." },
4: { t: "Transformations, Homography & Image Alignment",
  th: ["2D/3D geometric transformations; affine vs projective",
       "Homography and image alignment; RANSAC for robust estimation",
       "Warping, perspective correction and panorama stitching"],
  pr: "Estimate a homography with RANSAC; build a panorama stitcher and a document scanner (perspective warp).",
  d: "A stitched panorama + a working document scanner." },
5: { t: "Cameras, Calibration, Stereo & Depth",
  th: ["Pinhole camera model; intrinsics/extrinsics; lens distortion",
       "Camera calibration (chessboard) and undistortion",
       "Epipolar geometry, stereo & disparity → depth; monocular depth (MiDaS / Depth Pro)"],
  pr: "Calibrate the Pi camera and undistort a live frame; estimate depth (stereo or monocular).",
  d: "A saved intrinsics file + a depth/disparity map on a real scene." },
6: { t: "Motion, Optical Flow & Segmentation",
  th: ["Motion field and optical flow (Lucas–Kanade, Farnebäck); background subtraction",
       "Classical tracking (mean-shift / CamShift / KCF)",
       "Image segmentation & clustering: thresholding, GrabCut, k-means, watershed"],
  pr: "Build an optical-flow motion tracker; a background-subtraction / segmentation app.",
  d: "A motion-tracking clip + a segmentation result on a chosen scene." },
7: { t: "Real-Time & Embedded Capture (Edge Foundations)",
  th: ["The Raspberry Pi camera stack: libcamera → picamera2; sensors (Global Shutter for motion/drones)",
       "The real-time loop; measuring FPS/latency; threading and queues",
       "The ESP32-CAM as a networked camera (MJPEG over Wi-Fi)"],
  pr: "Build a live capture app with an FPS overlay; sweep resolution; ingest the ESP32-CAM stream on the Pi.",
  d: "An FPS-vs-resolution table (the CPU baseline for Lecture 11) + an ESP32 feed screenshot." },
8: { t: "Deep Learning Foundations (PyTorch & TensorFlow)",
  th: ["Perceptron → ANN → backpropagation; activations, loss and cost functions",
       "Optimisers (SGD → Adam), regularisation (dropout, weight init)",
       "CNN building blocks: convolution, pooling, receptive fields; PyTorch vs Keras/TensorFlow"],
  pr: "Train a CNN image classifier on a custom dataset in both PyTorch and TensorFlow/Keras (Colab).",
  d: "Two trained classifiers + accuracy curves and a confusion matrix." },
9: { t: "CNN Architectures, Transfer Learning & Deployment",
  th: ["Architecture lineage: LeNet → AlexNet → VGG → Inception → ResNet → MobileNet → ViT",
       "Transfer learning vs pretrained vs fine-tuning; data augmentation (Albumentations)",
       "Deployment: Gradio, Streamlit and Hugging Face Spaces; simple GUI apps"],
  pr: "Fine-tune a pretrained backbone; wrap it in a Gradio/GUI app and deploy to a Hugging Face Space.",
  d: "A live web demo URL + held-out accuracy." },
10: { t: "Object Detection I — YOLO Family & Custom Training",
  th: ["Detection formulation; boxes, IoU, mAP, NMS; two-stage (R-CNN family) vs one-stage (SSD/YOLO)",
       "YOLO evolution v5 → v8 → 11 → v12 → YOLO26; YOLO-NAS, RF-DETR; zero-shot detection (YOLOE)",
       "Dataset lifecycle: collection, labelling (Roboflow), splitting, augmentation"],
  pr: "Run and compare pretrained YOLO models; train a custom detector (e.g. PPE / pothole).",
  d: "A custom-trained detector + a threshold/mAP analysis note." },
11: { t: "Object Detection II — Edge Acceleration: Hailo NPU & TinyML",
  th: ["Why NPUs exist; HailoRT and the Model Zoo; the .pt → ONNX → Hailo DFC → .hef compile chain",
       "Int8 quantisation and the accuracy/speed trade-off; CPU-vs-NPU benchmarking",
       "TinyML on microcontrollers: Edge Impulse and FOMO on the ESP32-CAM"],
  pr: "Compile and deploy a custom YOLO on Pi + Hailo (benchmark vs CPU); deploy a FOMO model on the ESP32-CAM.",
  d: "An NPU detector at real-time FPS + an on-device ESP32 FOMO demo + a tier-comparison table." },
12: { t: "Tracking, Counting, OCR & Vision AI Agents",
  th: ["The association problem; SORT → DeepSORT → ByteTrack → BoT-SORT; stable IDs",
       "Analytics: line-crossing counts, speed estimation, dwell time, heatmaps, zones",
       "OCR (license plate + PaddleOCR); vision AI agents (LLM-in-the-loop workflows)"],
  pr: "Build a tracking + counting + speed application; add a license-plate detection + OCR pipeline.",
  d: "A tracking/counting demo with in/out counts and speed + an LPR-OCR result." },
13: { t: "Segmentation, Pose & Vision-Language Models",
  th: ["Semantic vs instance segmentation: FCN, U-Net, Mask R-CNN, YOLO-seg; SAM 3 (promptable, 2025)",
       "Pose estimation: OpenPose, YOLO-pose, MediaPipe (hands/face/body)",
       "Vision Transformers recap; CLIP zero-shot & visual search; VLMs (captioning, VQA, OCR); VLA primer"],
  pr: "Run segmentation + a MediaPipe gesture controller; build a CLIP visual search and a VLM VQA demo.",
  d: "A segmentation/pose demo + a working CLIP search and one VQA example." },
14: { t: "Drone Vision Project I — Aerial Perception (Tello + YOLO)",
  th: ["The drone-vision pipeline; DJI Tello SDK, video streaming and control",
       "Aerial detection, tracking and counting; image/world coordinate frames",
       "Flight safety, netted-cage operation and pre-flight checks"],
  pr: "PROJECT: live YOLO detection + tracking + counting from a Tello (e.g. aerial car / house / person counting).",
  d: "A recorded aerial-perception demo + a short project report (pipeline, results, safety)." },
15: { t: "Drone Vision Project II — Autonomous Vision-Guided Drone",
  th: ["Perception → action: closing the loop; visual servoing (keep a target centred)",
       "Colour- and QR-based navigation; obstacle avoidance; PID / deadband control",
       "Runtime safety gates; optional ROS 2 bridge for detections"],
  pr: "PROJECT (capstone): a vision-guided drone — target following / colour-or-QR navigation / obstacle avoidance.",
  d: "Capstone demo + 4–6 page report (problem, architecture, tier justification, results, limitations) + repo." },
};

// ---------- build document body ----------
const body = [];

// Title block
body.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 40 },
  children: [new TextRun({ text: "Applied Computer Vision / Intelligent Vision Systems", bold: true, font: FONT, size: 40, color: TEAL })] }));
body.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 60 },
  children: [new TextRun({ text: "Course Syllabus — Edge, Embedded & Drone Vision", font: FONT, size: 24, italics: true, color: INK })] }));
body.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 }, border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: TEAL } },
  children: [new TextRun({ text: "15 Lectures  •  each 1.5 h theory + 1.5 h practical  •  45 contact hours  •  theory + hands-on projects", font: FONT, size: 18, color: MUTE })] }));

// Course info table
const infoRows = [
  ["Course title", "Applied Computer Vision / Intelligent Vision Systems"],
  ["Level / credits", "BS (final year) or PG introductory · 3 credit hours (2 theory + 1 lab)"],
  ["Structure", "15 lectures × 3 hours = 45 contact hours (1.5 h theory + 1.5 h practical each)"],
  ["Delivery", "Theory lecture + supervised hands-on lab/project every session"],
  ["Prerequisites", "Python programming; basic linear algebra & probability"],
  ["Hardware", "Raspberry Pi 5, Hailo AI HAT, Pi cameras (Module 3 / HQ / Global Shutter), ESP32-CAM, DJI Tello (or equivalent)"],
  ["Software", "Python, OpenCV, PyTorch, TensorFlow/Keras, Ultralytics (YOLO), picamera2, HailoRT, Edge Impulse, Gradio, Roboflow"],
];
body.push(new Table({ width: { size: 9360, type: WidthType.DXA }, columnWidths: [2400, 6960],
  rows: infoRows.map(([k, v]) => new TableRow({ children: [
    cell(P([T(k, { bold: true, color: INK })], { after: 0 }), 2400, LIGHT),
    cell(P([T(v)], { after: 0 }), 6960) ] })) }));

// Description
body.push(H("Course description", HeadingLevel.HEADING_1));
body.push(P([T("This course teaches students to build complete, deployable computer-vision systems — from classical image processing and multi-view geometry to modern deep learning, object detection, tracking, segmentation, and vision-language models — and to run them on real edge hardware. Rather than stopping at model training, every unit pairs 1.5 hours of theory with a 1.5-hour hands-on project, progressing across a four-tier stack (ESP32-CAM microcontroller → Raspberry Pi 5 CPU → Hailo NPU → autonomous drone). The final two labs are vision-based drone projects in which students integrate perception with real-time control. The syllabus synthesises rigorous academic computer-vision curricula (e.g. Cornell CS5670, UW CSE455) with applied, project-driven material (modern YOLO through YOLO26, tracking and analytics, ViT/VLM, TinyML and drone autonomy).")]));

// CLOs
body.push(H("Course Learning Outcomes (CLOs)", HeadingLevel.HEADING_1));
[
  ["CLO1", "Apply classical image-processing, feature and geometry techniques (filtering, edges, features, homography, calibration, stereo, motion) to defined vision tasks."],
  ["CLO2", "Build real-time camera applications across compute tiers and reason about latency, throughput and power."],
  ["CLO3", "Train, fine-tune and evaluate CNN and Transformer models with correct metrics (accuracy, IoU, mAP)."],
  ["CLO4", "Deploy object detection, tracking, counting, segmentation and pose pipelines with application logic."],
  ["CLO5", "Compile and run models on an NPU (Hailo) and a microcontroller (ESP32/TinyML) and quantify the trade-offs."],
  ["CLO6", "Use Vision Transformers, CLIP, VLMs and SAM for zero-shot, search, VQA and segmentation, and explain the VLA idea."],
  ["CLO7", "Integrate perception into an autonomous drone system that turns detections into safe control actions."],
  ["CLO8", "Communicate results through working demos and technical reports and justify all design choices."],
].forEach(([c, t]) => body.push(bullet([T(c + " — ", { bold: true, color: TEAL }), T(t)])));

// Methodology + assessment
body.push(H("Teaching methodology & assessment", HeadingLevel.HEADING_1));
body.push(P([T("Each 3-hour session has two halves: a "), T("1.5-hour theory lecture", { bold: true }), T(" followed by a "), T("1.5-hour supervised practical", { bold: true }), T(" in which students build and measure a working system. Every lecture produces a graded deliverable; two mini-projects and a two-part drone capstone anchor the assessment.")]));
const asmt = [
  ["Component", "Weight", "Maps to"],
  ["Weekly lab deliverables (13)", "26%", "CLO1–CLO6"],
  ["Quizzes (3: classical / deep / edge)", "12%", "CLO1, CLO3, CLO5"],
  ["Mid-term project — custom detector on Hailo NPU (after L11)", "20%", "CLO3–CLO5"],
  ["Drone capstone project + demo (L14–L15)", "32%", "CLO7, CLO8"],
  ["Lab notebook & participation", "10%", "all"],
];
body.push(new Table({ width: { size: 9360, type: WidthType.DXA }, columnWidths: [5460, 1500, 2400],
  rows: asmt.map((r, i) => new TableRow({ children: r.map((c, j) =>
    cell(P([T(c, { bold: i === 0, color: i === 0 ? "FFFFFF" : "222222" })], { after: 0, align: j ? AlignmentType.CENTER : undefined }),
      [5460, 1500, 2400][j], i === 0 ? TEAL : (i % 2 ? "FFFFFF" : LIGHT))) })) }));

// At-a-glance schedule
body.push(new Paragraph({ children: [new PageBreak()] }));
body.push(H("Course schedule at a glance", HeadingLevel.HEADING_1));
const glanceHeader = new TableRow({ tableHeader: true, children: [
  cell(P([T("#", { bold: true, color: "FFFFFF" })], { after: 0, align: AlignmentType.CENTER }), 700, TEAL),
  cell(P([T("Lecture theme (Theory 1.5 h)", { bold: true, color: "FFFFFF" })], { after: 0 }), 4600, TEAL),
  cell(P([T("Practical / Project (1.5 h)", { bold: true, color: "FFFFFF" })], { after: 0 }), 4060, TEAL) ] });
const glanceRows = Object.keys(L).map((k, i) => {
  const l = L[k];
  return new TableRow({ children: [
    cell(P([T(String(k), { bold: true, color: INK })], { after: 0, align: AlignmentType.CENTER }), 700, i % 2 ? "FFFFFF" : LIGHT),
    cell(P([T(l.t)], { after: 0 }), 4600, i % 2 ? "FFFFFF" : LIGHT),
    cell(P([T(l.pr.replace(/^PROJECT.*?: /, "").replace(/^PROJECT.*?\): /, ""))], { after: 0 }), 4060, i % 2 ? "FFFFFF" : LIGHT) ] });
});
body.push(new Table({ width: { size: 9360, type: WidthType.DXA }, columnWidths: [700, 4600, 4060], rows: [glanceHeader, ...glanceRows] }));

// Detailed lectures
body.push(new Paragraph({ children: [new PageBreak()] }));
body.push(H("Detailed lecture & practical plan", HeadingLevel.HEADING_1));
parts.forEach(([pname, nums]) => {
  body.push(new Paragraph({ spacing: { before: 200, after: 80 },
    children: [new TextRun({ text: pname, bold: true, font: FONT, size: 24, color: LIME })] }));
  nums.forEach((n) => {
    const l = L[n];
    body.push(new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 160, after: 80 },
      children: [new TextRun({ text: `Lecture ${n} — ${l.t}`, font: FONT, color: INK })] }));
    body.push(P([T("Theory (1.5 h)", { bold: true, color: TEAL })], { after: 40 }));
    l.th.forEach((x) => body.push(bullet(x)));
    body.push(P([T("Practical (1.5 h)", { bold: true, color: TEAL })], { after: 40, before: 40 }));
    body.push(P([T(l.pr)], { after: 40 }));
    body.push(P([T("Deliverable: ", { bold: true, color: LIME }), T(l.d, { italics: true })], { after: 120 }));
  });
});

// References
body.push(new Paragraph({ children: [new PageBreak()] }));
body.push(H("Reference materials", HeadingLevel.HEADING_1));
body.push(P([T("Core textbook", { bold: true, color: INK })], { after: 40 }));
body.push(bullet("Richard Szeliski, Computer Vision: Algorithms and Applications (2nd ed.) — free PDF: szeliski.org/Book"));
body.push(P([T("University courses (open)", { bold: true, color: INK })], { after: 40, before: 80 }));
[["Cornell CS5670 — Introduction to Computer Vision", "cs.cornell.edu/courses/cs5670"],
 ["University of Washington CSE455 — Computer Vision", "courses.cs.washington.edu/courses/cse455"],
 ["UMich EECS 498/598 — Deep Learning for Computer Vision", "web.eecs.umich.edu/~justincj/teaching/eecs498"],
 ["Stanford CS231n — Convolutional Neural Networks for Visual Recognition", "cs231n.github.io"],
].forEach(([n, u]) => body.push(bullet([T(n + " — ", {}), T(u, { color: TEAL })])));
body.push(P([T("Applied / project-based courses", { bold: true, color: INK })], { after: 40, before: 80 }));
["Complete Computer Vision Bootcamp with PyTorch & TensorFlow (CNN, object detection)",
 "Practical Computer Vision Mastery — 20+ Python & AI projects (OpenCV, YOLO, OCR, GUI)",
 "YOLOv5–YOLO26 & Vision AI Agents — detection, segmentation, tracking, pose",
 "Learn OpenCV — 30 apps with OpenCV, YOLOv8 & YOLO-NAS (tracking, segmentation, pose)",
 "Computer Vision with Vision Transformers & Vision-Language Models (ViT, CLIP, SAM, VLM)",
].forEach((n) => body.push(bullet(n)));
body.push(P([T("Tools & documentation", { bold: true, color: INK })], { after: 40, before: 80 }));
[["Ultralytics YOLO (incl. YOLO26)", "docs.ultralytics.com"],
 ["Raspberry Pi AI / Hailo", "raspberrypi.com/documentation/computers/ai.html"],
 ["Hailo examples", "github.com/hailo-ai/hailo-apps"],
 ["Edge Impulse (ESP32 / FOMO)", "docs.edgeimpulse.com"],
 ["Meta Segment Anything (SAM 3)", "ai.meta.com/sam3"],
 ["MediaPipe", "ai.google.dev/edge/mediapipe/solutions/guide"],
 ["DJI Tello Python SDK (DJITelloPy)", "github.com/damiafuentes/DJITelloPy"],
 ["Roboflow (labelling & datasets)", "roboflow.com"],
].forEach(([n, u]) => body.push(bullet([T(n + " — ", {}), T(u, { color: TEAL })])));

body.push(P([T("Note: ", { bold: true }), T("model versions move quickly — confirm the exact YOLO26 weight names and the current Hailo / picamera2 / SAM releases against official documentation before each offering.", { italics: true, color: MUTE })], { before: 160 }));

// ---------- document ----------
const doc = new Document({
  numbering: { config: [
    { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
      style: { run: { color: TEAL }, paragraph: { indent: { left: 360, hanging: 220 } } } }] }] },
  styles: { default: { document: { run: { font: FONT, size: 21 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONT, size: 30, bold: true, color: TEAL }, paragraph: { spacing: { before: 260, after: 120 } } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONT, size: 25, bold: true, color: INK }, paragraph: { spacing: { before: 160, after: 80 } } } ] },
  sections: [{
    properties: { page: { margin: { top: 1000, bottom: 1000, left: 1080, right: 1080 } } },
    children: body }],
});

Packer.toBuffer(doc).then((buf) => { fs.writeFileSync("Applied_Computer_Vision_Syllabus.docx", buf); console.log("wrote docx", buf.length); });
