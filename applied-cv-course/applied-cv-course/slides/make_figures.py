"""Generate original diagram figures for the lecture decks (safe to embed).
Theme: slate/teal/lime on white. Outputs PNGs to figures/."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch

INK = "#0E2233"; TEAL = "#0E9AA7"; TEALD = "#0B7D88"; LIME = "#A3E635"
MUTE = "#6B7280"; CARD = "#EAF3F5"
os.makedirs("figures", exist_ok=True)
plt.rcParams["font.family"] = "DejaVu Sans"


def box(ax, x, y, w, h, fc, ec="none", r=0.06, lw=0):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                                fc=fc, ec=ec, lw=lw, mutation_aspect=1))


def arrow(ax, x0, y0, x1, y1, c=TEAL, lw=2.4):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>",
                                 mutation_scale=16, color=c, lw=lw))


# ---- 1. Applied-CV pipeline (L1) --------------------------------------
def pipeline():
    fig, ax = plt.subplots(figsize=(11, 3.1), dpi=200)
    ax.set_xlim(0, 11); ax.set_ylim(0, 3.1); ax.axis("off")
    steps = ["Capture", "Pre-process", "Inference", "Post-process", "Decision", "Action"]
    cols = [TEAL, TEALD, INK, TEALD, TEAL, INK]
    w, h, y = 1.55, 1.2, 1.0
    for i, (s, c) in enumerate(zip(steps, cols)):
        x = 0.25 + i * 1.78
        box(ax, x, y, w, h, c, r=0.12)
        ax.text(x + w / 2, y + h / 2, s, ha="center", va="center", color="white",
                fontsize=11.5, fontweight="bold")
        if i < len(steps) - 1:
            arrow(ax, x + w + 0.02, y + h / 2, x + 1.76, y + h / 2, c=LIME if i % 2 else TEAL)
    ax.text(5.5, 0.45, "constraints at every stage:  latency  •  power  •  thermals  •  offline  •  privacy",
            ha="center", fontsize=10.5, color=MUTE, style="italic")
    fig.savefig("figures/fig_pipeline.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ---- 2. Convolution + receptive field (L5) ----------------------------
def conv():
    fig, ax = plt.subplots(figsize=(9, 4.6), dpi=200)
    ax.set_xlim(0, 9); ax.set_ylim(0, 4.6); ax.axis("off")
    # input grid 5x5
    gx, gy, cell = 0.5, 0.7, 0.55
    for r in range(5):
        for c in range(5):
            fc = LIME if (r < 3 and c < 3) else CARD
            ax.add_patch(Rectangle((gx + c * cell, gy + r * cell), cell, cell,
                                   fc=fc, ec="white", lw=2))
    ax.text(gx + 2.5 * cell, gy + 5 * cell + 0.25, "input + 3×3 kernel",
            ha="center", fontsize=11, fontweight="bold", color=INK)
    # kernel outline
    ax.add_patch(Rectangle((gx, gy + 2 * cell), 3 * cell, 3 * cell, fc="none",
                           ec=TEAL, lw=3))
    # arrow to feature map
    arrow(ax, gx + 5 * cell + 0.15, gy + 2.5 * cell, gx + 5 * cell + 1.05, gy + 2.5 * cell, c=INK)
    # output 3x3
    ox = gx + 5 * cell + 1.25
    for r in range(3):
        for c in range(3):
            ax.add_patch(Rectangle((ox + c * cell, gy + 0.9 + r * cell), cell, cell,
                                   fc=TEALD, ec="white", lw=2))
    ax.text(ox + 1.5 * cell, gy + 0.9 + 3 * cell + 0.25, "feature map",
            ha="center", fontsize=11, fontweight="bold", color=INK)
    ax.text(4.5, 0.2, "each output pixel sees a local receptive field; stacking layers grows it",
            ha="center", fontsize=10.5, color=MUTE, style="italic")
    fig.savefig("figures/fig_conv.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ---- 3. IoU + mAP (L7) ------------------------------------------------
def iou():
    fig, ax = plt.subplots(figsize=(9.5, 4.4), dpi=200)
    ax.set_xlim(0, 9.5); ax.set_ylim(0, 4.4); ax.axis("off")
    # two overlapping boxes
    ax.add_patch(Rectangle((0.8, 1.1), 2.6, 2.2, fc="none", ec=TEAL, lw=3.5))
    ax.text(0.8, 3.42, "ground truth", color=TEALD, fontsize=11, fontweight="bold")
    ax.add_patch(Rectangle((2.0, 0.6), 2.6, 2.2, fc="none", ec=LIME, lw=3.5))
    ax.text(3.1, 0.3, "prediction", color="#5c7a12", fontsize=11, fontweight="bold")
    # intersection shaded
    ax.add_patch(Rectangle((2.0, 1.1), 1.4, 1.7, fc=TEAL, alpha=0.25, ec="none"))
    ax.text(2.7, 1.95, "∩", ha="center", va="center", fontsize=20, color=INK, fontweight="bold")
    # formula
    ax.text(6.8, 2.9, "IoU  =", ha="center", fontsize=16, color=INK, fontweight="bold")
    ax.text(8.15, 3.2, "area of overlap", ha="center", fontsize=12.5, color=TEALD)
    ax.plot([7.35, 8.95], [2.95, 2.95], color=INK, lw=1.6)
    ax.text(8.15, 2.62, "area of union", ha="center", fontsize=12.5, color="#5c7a12")
    ax.text(6.9, 1.7, "mAP averages precision/recall\nacross classes and IoU thresholds\n(mAP@0.5, mAP@0.5:0.95)",
            ha="left", fontsize=10.8, color=MUTE, style="italic")
    fig.savefig("figures/fig_iou.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ---- 4. Attention Q/K/V (L12) -----------------------------------------
def attention():
    fig, ax = plt.subplots(figsize=(9.5, 4.2), dpi=200)
    ax.set_xlim(0, 9.5); ax.set_ylim(0, 4.2); ax.axis("off")
    # Q, K, V boxes
    labels = [("Query", TEAL, 0.8), ("Key", TEALD, 4.0), ("Value", INK, 7.2)]
    for name, c, x in labels:
        box(ax, x, 2.3, 1.7, 0.9, c, r=0.12)
        ax.text(x + 0.85, 2.75, name, ha="center", va="center", color="white",
                fontsize=12.5, fontweight="bold")
    # Q.K -> softmax -> weights
    arrow(ax, 2.5, 2.75, 3.9, 2.75, c=MUTE)
    ax.text(3.2, 2.95, "·", ha="center", fontsize=18, color=INK)
    arrow(ax, 4.85, 2.25, 4.85, 1.5, c=MUTE)
    box(ax, 3.7, 0.7, 2.3, 0.8, LIME, r=0.12)
    ax.text(4.85, 1.1, "softmax → weights", ha="center", va="center",
            color=INK, fontsize=11.5, fontweight="bold")
    arrow(ax, 6.05, 1.1, 8.0, 1.1, c=MUTE)
    arrow(ax, 8.05, 2.25, 8.05, 1.5, c=MUTE)
    ax.text(8.05, 0.35, "weighted sum of Values = output", ha="center",
            fontsize=10.8, color=MUTE, style="italic")
    fig.savefig("figures/fig_attention.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


pipeline(); conv(); iou(); attention()
print("figures:", os.listdir("figures"))
