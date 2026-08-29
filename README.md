<div align="center">

# 👁️ Intelligent Vision Systems

**A complete, 16-week, project-driven Computer Vision course — classical CV through deep learning, deployed live on the Raspberry&nbsp;Pi&nbsp;5.**

[![Course Website](https://img.shields.io/badge/course%20website-live-2ea44f?style=for-the-badge)](https://kazimbalti.github.io/intelligent-vision-systems/)
[![License: MIT](https://img.shields.io/badge/code%20license-MIT-blue.svg?style=for-the-badge)](LICENSE)
[![Slides: reveal.js](https://img.shields.io/badge/slides-reveal.js-ff5c39?style=for-the-badge)](https://revealjs.com)
[![Platform](https://img.shields.io/badge/platform-Raspberry%20Pi%205-c51a4a?style=for-the-badge)](https://www.raspberrypi.com/products/raspberry-pi-5/)

![Intelligent Vision Systems](images/cv-banner.png)

</div>

Course materials for **Intelligent Vision Systems (Applied Computer Vision)** —
BSES, 7th Semester, Section A, **University of Lahore**, Fall 2026
(31 Aug – 14 Dec 2026, 16 weekly Monday sessions: 1.5&nbsp;h theory + 1.5&nbsp;h
lab). Sixteen lecture decks, fifteen Raspberry&nbsp;Pi&nbsp;5 labs, two
research-paper-from-scratch labs (U-Net, Transformer), an OpenCV&nbsp;5.0 deep
dive, and a capstone vision system demoed on real hardware.

## 🔗 Course Website

**➡️ https://kazimbalti.github.io/intelligent-vision-systems/**

The website is the primary way to browse this course. It has the latest:

- [Syllabus](https://kazimbalti.github.io/intelligent-vision-systems/syllabus.html) — CLOs, textbooks, grading, policies
- [Schedule](https://kazimbalti.github.io/intelligent-vision-systems/schedule.html) — the full 16-week lecture + lab table
- [Labs](https://kazimbalti.github.io/intelligent-vision-systems/labs.html) — 15 labs, capstone rubric, project bank
- [Lectures](https://kazimbalti.github.io/intelligent-vision-systems/lectures/) — 16 interactive reveal.js slide decks
- [Code & Demos](https://kazimbalti.github.io/intelligent-vision-systems/code/) — runnable OpenCV/PyTorch/Hailo/ESP32 samples
- [Assignments](https://kazimbalti.github.io/intelligent-vision-systems/assignments/) — the graded assignment bank
- [Tutorials](https://kazimbalti.github.io/intelligent-vision-systems/tutorials/) — Pi, Git, Python/Conda, VS Code, NumPy, Pydantic

## 📚 About the Course

This course covers both **classical and modern computer vision**, with a
running thread of **real-time deployment on embedded/edge hardware**:

- Image formation, sensing, and digital image fundamentals
- Point operations, spatial & frequency-domain filtering, restoration, morphology
- Edges, contours, local features, descriptors, matching, and RANSAC
- Camera calibration, two-view geometry, and stereo depth
- Optical flow, tracking, and recursive estimation
- Classical recognition (HOG/SVM, Haar), then neural networks and CNNs
- Reading and reproducing research papers from scratch — **U-Net** and the **Transformer**
- Object detection, segmentation, and Vision Transformers / VLMs
- Edge deployment: quantisation, pruning, ONNX/TFLite/Hailo, and an **OpenCV 5.0** deep dive
- A capstone vision system, integrated and demoed live on the **Raspberry Pi 5** (+ AI HAT/Hailo, Pi Camera, ESP32-CAM)

## 🗂️ Repository vs. Course Website

The **course website** (linked above) is the recommended way to browse the
course — syllabus, schedule, labs, and interactive lecture slides.

This **GitHub repository** is the source behind it: every page, every slide
deck, the runnable code samples, and the planning documents the course was
built from. Clone it to get the whole course — slides, code, and labs — in
one place.

## Pages

| File | Purpose |
|------|---------|
| `index.html` | Landing page — course-material cards, About, Course-at-a-glance |
| `syllabus.html` | Description, CLOs, prerequisites, textbooks, grading (40/20/30/10), policies, weekly topic map |
| `schedule.html` | **16-week Monday** lecture+lab table with readings, matching the schedule docx |
| `labs.html` | 15 Raspberry Pi 5 labs + capstone project, paper-implementation labs, OpenCV 5.0 deep dive, milestones, rubric, project bank |
| `lectures/index.html` | Lecture list; `lectures/01_intro.html`…`16_capstone.html` are interactive reveal.js slides, one per week |
| `code/index.html` | Runnable code samples (`code/samples/`, copied from `applied-cv-course/code/`) mapped to labs |
| `assignments/index.html` | The 4-assignment bank (out/due weeks) from the schedule docx |
| `tutorials/` | Tool setup guides (Raspberry Pi, Git, Python/Conda, VS Code, NumPy, Pydantic) — carried over from the source |
| `tas.html` | Instructor contact (Dr. Muhammad Kazim) & TA placeholders |
| `site_libs/` | Bootstrap, reveal.js, search — do not edit |
| `search.json`, `listings.json` | Site search / listing indexes (regenerate if you add pages) |
| `applied-cv-course/` | Source materials this site draws on: handbook, 14-lecture plan, code, syllabus docs — not part of the published site itself |

> **Note:** large binaries (`*.mp4`, `*.pptx`, `*.pdf`) are tracked with
> [Git LFS](https://git-lfs.com/) — run `git lfs install` once before cloning
> so `lectures/assets/01_intro/Projects_demo.mp4`, `lectures/NMD_VAS.pptx`,
> and `lectures/pdf/*.pdf` download correctly.
>
> **GitHub Pages caveat:** Pages serves the raw Git LFS *pointer* file, not
> the real binary, so any `<video>`/`<a>` on the live site can't link to an
> LFS-tracked path directly. The demo video and lecture PDFs instead link to
> the [`media-v1` release](../../releases/tag/media-v1) — if you add another
> large file that needs to play/download from the live site, upload it there
> too (`gh release upload media-v1 <file>`) and link its
> `.../releases/download/media-v1/<file>` URL instead of the repo-relative
> path.

## Editing content

Plain HTML — no build step required to publish.

- **Schedule rows:** edit the matching `<tr>` in `schedule.html`; the *Slides*
  cell links to the matching `lectures/NN_*.html` deck.
- **Lecture materials:** add/edit files under `lectures/` following the
  `01_intro.html`/`02_image.html` reveal.js format, and update the matching
  `lecture-item` block in `lectures/index.html`. New decks (03–16) have no PDF
  export yet — use each deck's built-in PDF export mode (press `e`).
- **Labs / assignments / code:** edit `labs.html`, `assignments/index.html`,
  and `code/index.html` (+ drop new files in `code/samples/`).
- **Dates:** the schedule assumes classes start **Mon 31 Aug 2026**. Replace the
  Date cells with the official University of Lahore academic-calendar dates and
  add holiday rows.
- **Instructor / room:** already filled in from the schedule docx
  (Dr. Muhammad Kazim, E1-404 Lab); TA names are still placeholders in `tas.html`.
- **Banner:** replace `images/cv-banner.png` with your own 3:1-ish image.
- **Nav bar:** the `<ul class="navbar-nav ...">` block is repeated in every
  `.html` file — change all copies together if you add a page.

### Optional: rebuild with Quarto

If you want to regenerate the site properly (auto TOC, search, listings), install
Quarto, create `_quarto.yml` + `.qmd` source files, and run `quarto render`.
The current files are the already-rendered output and work as-is without it.

## Deploy on GitHub Pages

This repo is served straight from the `main` branch root via
**Settings → Pages → Deploy from a branch → `main` / `(root)`** — live at
<https://kazimbalti.github.io/intelligent-vision-systems/>. `.nojekyll` is
included so files are served exactly as written, with no Jekyll processing.

Forking this course? Same two steps: push to your own repo, then flip on
Pages in **Settings**.

## Local preview

```bash
python -m http.server 8000
# open http://localhost:8000
```

## 👤 Instructor

**Dr. Muhammad Kazim**
Assistant Professor, Department of Intelligent Systems
University of Lahore
✉️ [muhammad.kazim@is.uol.edu.pk](mailto:muhammad.kazim@is.uol.edu.pk)

## 🙏 Attribution

- **Site framework and Lectures 01–02** are adapted from the open *Computer
  Vision* course by Kaveh Fathian, Colorado School of Mines —
  <https://ariarobotics.github.io/cv/> (<https://github.com/ariarobotics/cv>),
  reused here for teaching purposes with attribution on the
  [Lectures page](https://kazimbalti.github.io/intelligent-vision-systems/lectures/).
- **Lectures 03–16**, the schedule, labs, assignments, and code samples are
  original materials for this course, built from
  `Intelligent_Vision_Systems_Schedule_and_Labs.docx` and the companion
  `applied-cv-course/` handbook and code.
- Textbooks: Szeliski, *Computer Vision: Algorithms and Applications* 2e ·
  Gonzalez & Woods, *Digital Image Processing* 4e · Goodfellow, Bengio &
  Courville, *Deep Learning*.

## 📄 License

Code samples in [`code/samples/`](code/samples/) are released under the
[MIT License](LICENSE) — use, adapt, and redeploy them freely, attribution
appreciated.

Slides, the schedule, labs, and other course-authored text are provided free
for **educational use** (teaching, self-study, coursework). Please retain
attribution and check the license of any third-party resource (papers,
datasets, images) linked from the site before redistributing it separately.

---

<div align="center">

If this helped you teach or learn computer vision, a ⭐ on this repo helps others find it too.

</div>
