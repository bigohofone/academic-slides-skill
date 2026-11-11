"""Draws the made-up figures for theme.pptx's example slides, in the academic-figure style at slide size.

Run `python theme_example_figures.py`, then `python theme.py`. Needs matplotlib, tol-colors and
https://github.com/bigohofone/academic-figure-skill cloned next to this repo.
"""
import sys
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

HERE = Path(__file__).resolve().parent
FIGURE_STYLE = HERE.parents[3] / "academic-figure-skill" / "skills" / "academic-figure" / "assets"
sys.path.insert(0, str(FIGURE_STYLE))
import paper  # noqa: E402, F401  imported to register Inter and the paper style

DARK, BLUE, TINT, MUTED = "#1B3A7A", "#4477AA", "#EDF2F7", "#818F9C"  # the slide theme's colors
GRAY = "#A8A8A8"
# Slide-size figures: 14 pt text, the box sizes of the theme's picture placeholders.
FIGURE_AND_TEXT = (5.9, 3.15)
FULL_WIDTH = (9.0, 2.75)

plt.style.use(FIGURE_STYLE / "paper.mplstyle")
plt.rcParams.update({"font.size": 14, "axes.labelsize": 14, "axes.titlesize": 14, "xtick.labelsize": 13,
                     "ytick.labelsize": 13, "legend.fontsize": 13, "text.color": DARK, "axes.labelcolor": DARK,
                     "xtick.color": DARK, "ytick.color": DARK, "axes.edgecolor": DARK})


def save(fig, name):
    fig.savefig(HERE / f"theme_example_{name}.png", dpi=200)
    plt.close(fig)


def long_tail():
    rng = np.random.default_rng(1)
    hours = np.sort(np.concatenate([[60000, 9000, 4000, 2500, 1800], rng.lognormal(2.2, 1.6, 95)]))[::-1]
    fig, ax = plt.subplots(figsize=FIGURE_AND_TEXT, layout="constrained")
    ax.bar(np.arange(len(hours)), hours, width=1.0, color=[BLUE if h >= 100 else GRAY for h in hours])
    ax.set_yscale("log")
    ax.axhline(100, color=DARK, linewidth=1, linestyle="--")
    ax.text(len(hours) - 1, 130, "100 h", ha="right", va="bottom")
    ax.set_xlabel("Languages, sorted by labeled hours")
    ax.set_ylabel("Labeled hours")
    ax.set_xticks([])
    save(fig, "long_tail")


def overview():
    fig = plt.figure(figsize=FULL_WIDTH)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 9.0)
    ax.set_ylim(0, 2.75)
    ax.axis("off")

    def panel(x, w, label):
        ax.add_patch(FancyBboxPatch((x, 0.15), w, 2.3, boxstyle="round,pad=0,rounding_size=0.11", fc=TINT, ec="none"))
        ax.text(x + 0.15, 2.3, label, fontsize=14, fontweight="semibold", color=BLUE, va="top")

    def block(x, y, w, text, strong=False):
        ax.add_patch(FancyBboxPatch((x, y), w, 0.62, boxstyle="round,pad=0,rounding_size=0.06",
                                    fc=BLUE if strong else "white", ec=BLUE, lw=1.5))
        ax.text(x + w / 2, y + 0.31, text, ha="center", va="center", fontsize=13, color="white" if strong else DARK)

    def arrow(x0, y0, x1, y1, **kw):
        ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=14, color=DARK, lw=1.5, **kw))

    panel(0.05, 5.85, "Stage 1  Pretrain on unlabeled audio (40 languages)")
    panel(6.05, 2.9, "Stage 2  Fine-tune")
    ax.text(6.2, 1.95, "10 h of labels", fontsize=13, color=MUTED, va="top")
    t = np.linspace(0, 1, 200)
    ax.plot(0.3 + 1.2 * t, 1.31 + 0.25 * np.sin(40 * t) * np.exp(-((t - 0.5) ** 2) / 0.08), color=DARK, lw=1)
    ax.text(0.9, 0.7, "raw audio", ha="center", fontsize=13, color=MUTED)
    block(1.8, 1.0, 1.6, "Masked encoder", strong=True)
    block(4.0, 1.0, 1.7, "k-means targets")
    arrow(1.55, 1.31, 1.8, 1.31)
    arrow(3.4, 1.31, 4.0, 1.31)
    arrow(4.85, 1.0, 2.6, 1.0, connectionstyle="arc3,rad=-0.3")
    ax.text(3.7, 0.3, "re-cluster ×2", ha="center", fontsize=13, color=MUTED)
    block(6.25, 1.0, 1.15, "Encoder")
    block(7.65, 1.0, 1.1, "CTC head")
    arrow(7.4, 1.31, 7.65, 1.31)
    ax.text(8.2, 0.35, "text", ha="center", fontsize=13, color=MUTED)
    arrow(8.2, 1.0, 8.2, 0.65)
    save(fig, "overview")








long_tail()
overview()
print("wrote figures to", HERE)
