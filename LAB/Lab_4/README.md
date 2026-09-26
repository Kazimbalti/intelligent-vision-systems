# Lab 4 — Computer Vision in Practice

**Intelligent Vision Systems · University of Lahore · Dr. Muhammad Kazim**

Hands-on companion to **Lecture 4 — Computer Vision: How computers see the world around us**
([slides](https://kazimbalti.github.io/intelligent-vision-systems/lectures/04_Computer_Vision.html)).
Each notebook is one of the lecture's **▶ DEMO** slides, climbing the same ladder:
pixels → classify → detect → segment → understand. All five use the same photo, `demo.jpg`.

| Part | Notebook | Lecture 4 section (demo slide) | Model |
|---|---|---|---|
| 4A | `02-image-as-numbers.ipynb` | 2 · How Images Are Represented (17) | OpenCV + NumPy |
| 4B | `03-image-classification.ipynb` | 3 · Image Classification (25) | ResNet-50 (ImageNet) |
| 4C | `04-object-detection.ipynb` | 4 · Object Detection (32) | RF-DETR Small (COCO) |
| 4D | `05-object-segmentation.ipynb` | 5 · Object Segmentation (39) | RF-DETR Seg Small (COCO) |
| 4E | `06-image-understanding.ipynb` | 6 · Image Understanding (46) | SmolVLM2-500M |

## Run it

**Google Colab (recommended, free GPU):** open a notebook from the
[Labs page](https://kazimbalti.github.io/intelligent-vision-systems/labs.html#lab-4-demos) with its *Open in Colab*
badge, uncomment the `!pip install` line in the first code cell, and run all cells. The notebook downloads `demo.jpg` itself.

**Locally / Raspberry Pi 5:**

```bash
python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
jupyter lab
```

The first run downloads model weights (ResNet-50 ≈ 100 MB, RF-DETR ≈ 100–150 MB each, SmolVLM2 ≈ 1 GB).
4A runs anywhere. 4B–4D run on a laptop CPU or the Pi 5 in a few seconds per image. 4E is
slow on the Pi (use Colab or a laptop).

## Deliverable

Each notebook ends with a **"Your turn"** section of three tasks. Submit the five notebooks with your code,
outputs and a short written answer to every task.
