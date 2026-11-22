# Paper reading worksheet (one page per paper)

*Intelligent Vision Systems · Lecture 7 · fill it by hand or in a markdown cell. Your own words, never copied.*

## Pass 1 (10 minutes): title, abstract, introduction, headings, all figures, conclusion

| | |
|---|---|
| Title · authors · venue · year | |
| Links (arXiv · PDF · official code) | |
| **C**ategory: what kind of paper? (new architecture / new loss / dataset / analysis / application) | |
| **C**ontext: which 1–3 earlier papers does it build on? | |
| **C**ontributions: what is new? (≤ 3 bullets) | |
| **C**orrectness: do the assumptions look reasonable? | |
| **C**larity: is it well written? Which part was hard? | |
| The key idea in **one sentence** | |
| Decision: read further / implement / skip? Why? | |

## Pass 2 (≈ 1 hour): method, architecture figure, main table

1. **Input → output** (with shapes, e.g. `(B, 1, 572, 572) → (B, 2, 388, 388)`):
2. **Draw the architecture figure** yourself (boxes and arrows), and write the tensor shape on every arrow.
3. **Shape table**

   | Block / layer | Output shape | Parameters (if you can count them) |
   |---|---|---|
   | | | |

4. **Core equations** — copy each one, then explain every symbol and its shape in words:

   | Eq. | Copied from the paper | In my words (+ shapes) | PyTorch line |
   |---|---|---|---|
   | | | | |

5. **Training details** (optimiser, learning rate + schedule, batch size, epochs, loss, augmentation, hardware):
6. **Main result** (table/figure number, metric, number, baseline):
7. **Ablation** — which part of the method matters most, and by how much?
8. **Words and references I did not understand** (look up 1–2 of them, not all):

## Before you code (pass 3 = implementing)

- [ ] I can explain the key idea to a friend in 2 minutes without the paper.
- [ ] Every box in the figure maps to one class or function in my plan.
- [ ] I know which test I will use for each block (shape · hand-computed value · parameter count · reference implementation).
- [ ] I chose a **small** experiment that still tests the paper's main claim, and one **ablation**.
- [ ] I know what compute/data I need, and it fits in Colab.

*Method after S. Keshav, "How to Read a Paper", ACM SIGCOMM CCR 37(3), 2007.*
