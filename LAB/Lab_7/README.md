# Lab 7 — Reading & Implementing Research Papers

**Intelligent Vision Systems · University of Lahore · Dr. Muhammad Kazim**

Hands-on companion to **Lecture 7 — Reading & Implementing Research Papers**
([slides](https://kazimbalti.github.io/intelligent-vision-systems/lectures/07_Paper_Implementation.html),
[setup guide for Colab & Antigravity](https://kazimbalti.github.io/intelligent-vision-systems/tutorials/09_paper_implementation_setup.html)).
You read four landmark papers and build each model from scratch in PyTorch, testing every block against the paper
and against PyTorch's own implementation. Every notebook runs on a **free Colab CPU in a few minutes** (a GPU only makes it faster).

| Part | Notebook | Paper | What you build | ✅ The check you must pass |
|---|---|---|---|---|
| 7A | `01-pytorch-for-papers.ipynb` | — | Tensors (B, C, H, W), conv arithmetic, reshape vs permute, `nn.Module`, the 5-line training loop, `trace_shapes` | two-moons accuracy ≥ 95 % |
| 7B | `02-attention-from-scratch.ipynb` | Vaswani et al. 2017, §3.2 | Stable softmax, scaled dot-product attention, masks, why ÷√d_k, multi-head attention | identical to `F.scaled_dot_product_attention` and `nn.MultiheadAttention` |
| 7C | `03-transformer-reverse-sequence.ipynb` | Vaswani et al. 2017, Fig. 1 | Positional encoding, LayerNorm, FFN, encoder & decoder layers, the full Transformer, greedy decoding | ≥ 95 % of sequences reversed (we get 98.8 %) |
| 7D | `04-unet-from-paper.ipynb` | Ronneberger et al. 2015 | Paper-exact U-Net (572 → 388, 31 030 658 params), modern U-Net, synthetic shapes dataset, Dice, skip-connection ablation | mean Dice ≥ 0.85 (we get 0.94) |
| 7E | `05-resnet-from-paper.ipynb` | He et al. 2016 | Residual block, ResNet-18/34/50 (exact torchvision counts), official weights loaded into your code, Figure 1 reproduced | `load_state_dict(strict=True)` works |
| 7F | `06-vit-from-paper.ipynb` | Dosovitskiy et al. 2021 | Patchify, patch embedding = strided conv, [class] token, ViT-B/16 (86 567 656 params), tiny ViT on digits, ablations | test accuracy ≥ 90 % (we get 98.6 %) |
| 7G | `07-paper-bug-hunt.ipynb` | all four | **Bug hunt (pairs):** 8 silent bugs from real code | scoreboard 8/8 |
| 7H | `08-implement-your-own-paper.ipynb` | Hu et al. 2018 (SE-Net) + yours | The 7-step recipe on a worked example, then a blank template for **your** paper | — |
| 7I | `09-paper-math-workbook.ipynb` | all five | 20 pencil-first exercises for the [Paper ↔ Code handbook](https://kazimbalti.github.io/intelligent-vision-systems/tutorials/10_paper_code_side_by_side.html): attention by hand, √d_k, PE, LayerNorm, U-Net sizes, ViT/ResNet counts | every answer = PyTorch's value |

`lab7_checks.py` holds the ✅/💡 auto-checks and helpers (`trace_shapes`, `count_params`, `overfit_one_batch`,
`make_shapes_dataset`, `load_digits_tensors`, `make_reverse_batch`). The notebooks download it automatically.

## Run in Google Colab (easiest)

Click a notebook on the [labs page](https://kazimbalti.github.io/intelligent-vision-systems/labs.html#lab-7-papers) →
**Open in Colab** → *File → Save a copy in Drive* → *Runtime → Run all*. Optional: *Runtime → Change runtime type → T4 GPU*.

## Run locally in Google Antigravity or VS Code

```bash
git clone https://github.com/Kazimbalti/intelligent-vision-systems
cd intelligent-vision-systems/LAB/Lab_7
python -m venv .venv
.venv\Scripts\activate            # Windows   (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
```
Open the folder in Antigravity (*File → Open Folder*), open a notebook, **Select Kernel → .venv**.
This folder contains `AGENTS.md` and `.agents/rules/paper-tutor.md`: they ask Antigravity's agent (and other coding agents) to
act as a **tutor** in this lab — explain, give hints, review — instead of writing your TODOs.

## Project 1: implement one new paper (individual, 2 weeks)

Implement one paper we did not build in the labs (★☆☆ or ★★☆ from the lecture's menu, or your own with approval),
test it, and check whether its main claim holds at small scale. Start from `08-implement-your-own-paper.ipynb` (Lab 7H).

| Step | Days |
|---|---|
| 1 · Choose a paper, get it approved | 1–2 |
| 2 · Read it: paper card, shape table, key equations | 2–3 |
| 3 · Build & test: shape, hand-example and parameter tests, overfit one batch | 4–8 |
| 4 · Experiment: the main claim + one ablation, 3 seeds | 9–12 |
| 5 · 2-page report with an AI-use declaration + 3-minute viva | 13–14 |

Marks: paper card + shape table 20 %, implementation + tests 30 %, experiment + ablation 25 %, honest report 15 %,
clean code 10 %. Details: [labs page](https://kazimbalti.github.io/intelligent-vision-systems/labs.html#lab-7-project-1).

## Deliverables

* **7A–7F:** every ✅ check passing and the **"Your turn"** questions answered in the notebook.
* **7G:** the 8/8 scoreboard and one line per bug (what · how found · which habit would have caught it).
* **Project 1:** one GitHub repo (model.py, test_model.py, paper.ipynb, report.pdf), submitted as your teacher announces.

## Papers and credits

* A. Vaswani et al., *Attention Is All You Need*, NeurIPS 2017 — [arXiv:1706.03762](https://arxiv.org/abs/1706.03762)
* O. Ronneberger, P. Fischer, T. Brox, *U-Net*, MICCAI 2015 — [arXiv:1505.04597](https://arxiv.org/abs/1505.04597)
* K. He, X. Zhang, S. Ren, J. Sun, *Deep Residual Learning for Image Recognition*, CVPR 2016 — [arXiv:1512.03385](https://arxiv.org/abs/1512.03385)
* A. Dosovitskiy et al., *An Image is Worth 16x16 Words*, ICLR 2021 — [arXiv:2010.11929](https://arxiv.org/abs/2010.11929)
* J. Hu, L. Shen, G. Sun, *Squeeze-and-Excitation Networks*, CVPR 2018 — [arXiv:1709.01507](https://arxiv.org/abs/1709.01507)
* S. Keshav, [*How to Read a Paper*](https://web.stanford.edu/class/ee384m/Handouts/HowtoReadPaper.pdf), ACM SIGCOMM CCR 2007
* Data: scikit-learn's bundled digits and sample photos (china.jpg, flower.jpg: CC BY 2.0, Flickr users danielbuechele and vultilion);
  all other data is generated in the notebooks. Pretrained weights in 7E come from torchvision.
* Further reading: [The Annotated Transformer](https://nlp.seas.harvard.edu/annotated-transformer/),
  [labml.ai annotated implementations](https://nn.labml.ai/), [d2l.ai](https://d2l.ai/),
  [niconielsen32/101-transformers](https://github.com/niconielsen32/101-transformers).
