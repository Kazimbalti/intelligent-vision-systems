# Lab 5 — Self-Driving Car Vision: Finding Lane Lines

**Intelligent Vision Systems · University of Lahore · Dr. Muhammad Kazim**

Hands-on companion to **Lecture 5 (Part II) — Computer Vision for Self-Driving Cars: Finding Lane Lines**
([slides](https://kazimbalti.github.io/intelligent-vision-systems/lectures/05_SDC_Lane_Finding.html)).
The notebooks follow the lecture step by step and build one complete pipeline:
**colour → region → edges → lines → lanes → video**.

| Part | Notebook | Lecture section | What you build |
|---|---|---|---|
| 5A | `01-color-selection.ipynb` | 2 · Colour selection | RGB thresholds, then a robust HLS white + yellow mask |
| 5B | `02-region-masking.ipynb` | 3 · Region of interest | Triangle mask with `polyfit` + `meshgrid`, then any polygon with `cv2.fillPoly` |
| 5C | `03-canny-edges.ipynb` | 4 · Canny edge detection | Image gradients, Gaussian blur, `cv2.Canny` thresholds |
| 5D | `04-hough-lines.ipynb` | 5 · Hough transform | A Hough accumulator from scratch, then `cv2.HoughLinesP` |
| 5E | `05-lane-finding-project.ipynb` | 6–7 · Pipeline & Assignment 2 | **Assignment 2:** the full lane-finding pipeline on images and videos |
| 5F | `06-bug-hunt.ipynb` | Common pitfalls | **Bug hunt (pairs):** fix 8 planted classic bugs, each with its own check and a scoreboard |
| 5G | `07-leaderboard.ipynb` | Pipeline & Assignment 2 | **Leaderboard:** score your `lane_lines()` on 92 labelled frames and submit to the class leaderboard |

## Learning by doing: checks, bug hunt, leaderboard

* **Auto-checks.** After each quiz in 5A–5D a ✅ cell (from `lab5_checks.py`, downloaded automatically) says whether your
  result is good enough or prints a 💡 hint — never the answer. Pairs can check themselves without waiting for the TA.
* **Bug hunt (5F).** Driver/navigator pairs, swap at every bug: predict → run → fix. First pair to 8/8 shows the TA.
* **Leaderboard (5G).** `leaderboard/` holds 46 clean frames (40 from the two Udacity videos + the 6 test images) and
  46 **hard** copies (night, shadows, haze, noise, glare, faded paint) with labelled lane lines in `ground_truth.json`.
  A lane is correct if its mean horizontal error over the lower image is < 20 px; ranking is overall accuracy, then mean
  error, then speed. The plain lab pipeline scores 95.1 % (clean 100 %, hard 90.2 %); a fixed HLS colour threshold drops
  to 73.9 % — robustness matters. Labels were made with the instructor's reference pipeline and checked by eye.

**Instructor — updating the class leaderboard:** students send the JSON line their notebook prints. Run
`python leaderboard/add_score.py '<that line>'`, then commit and push `leaderboard/leaderboard.json`; the
[Labs page](https://kazimbalti.github.io/intelligent-vision-systems/labs.html#lab-5-leaderboard) shows the new ranking.

## Run it

**Google Colab (recommended):** open a notebook from the
[Labs page](https://kazimbalti.github.io/intelligent-vision-systems/labs.html#lab-5-lane-lines) with its *Open in Colab*
badge and run all cells. Each notebook downloads the images it needs; the project notebook downloads the test videos from
the Udacity project repository.

**Locally / Raspberry Pi 5:**

```bash
python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
jupyter lab
```

Everything runs on a laptop CPU or the Pi 5 (no GPU and no model downloads needed). Tested with OpenCV 5.0; OpenCV 4.x works too.

## Deliverables

* **Lab 5 (5A–5D):** each notebook ends with three **"Your turn"** tasks. Submit the four notebooks with your code,
  outputs and a short written answer to every task.
* **Bug hunt (5F)** and **leaderboard (5G):** in-class activities — show the TA your 8/8 scoreboard and send your
  leaderboard line.
* **Assignment 2 (5E):** the completed `05-lane-finding-project.ipynb` with all outputs, your two output videos
  (`test_videos_output/solidWhiteRight.mp4`, `test_videos_output/solidYellowLeft.mp4`) and the write-up
  (`writeup_template.md`). Out Week 6, due Week 7 — rubric on the
  [Assignments page](https://kazimbalti.github.io/intelligent-vision-systems/assignments/index.html#assignment-2).

## Credits

Adapted and updated from the *Finding Lane Lines* lesson and Project 1 of the **Udacity Self-Driving Car Engineer
Nanodegree**. The test images (`test.jpg`, `exit-ramp.jpg`, `test_images/`) and test videos come from
[udacity/CarND-LaneLines-P1](https://github.com/udacity/CarND-LaneLines-P1) — © 2016–2019 Udacity, Inc., MIT licence
(see `LICENSE-udacity-CarND-LaneLines-P1.txt`).
