"""Usage: python aesthetics.py deck.pptx

Layout metrics measured on the rendered slides, after AeSlides (Pan et al., 2026, "Incentivizing Aesthetic Layout
in LLM-Based Slide Generation via Verifiable Rewards", arXiv 2604.22840). Renders the deck with LibreOffice and
the bundled Inter, prints one line per slide, and flags the ones outside the thresholds; exits with 1 if any is
flagged. Overlap and overflow are check.py's job. It also saves a contact sheet, every slide small on one image, and
prints where.

Everything is measured on real pixels, not shape boxes: a pixel is ink when it is darker than INK_LEVEL (the
slides are white), and ink is grown by a few pixels so the letters of a line merge into one region while the
white inside and around a figure stays blank. Only the content area counts: below the title and above the
footnote line (1.45 in to 4.85 in), so the title doesn't weigh on every slide. Title and section slides are
skipped. Slides are rendered 1280 px wide, as in AeSlides.

- fill: the share of the content area covered by ink grown by GROW px (about the gap between letters and lines,
  so a block of text reads as one region). Over CROWDED the slide is crowded. Calibrated on real talks:
  well-spaced slides measure 0.14-0.40, slides too dense to read 0.47-0.56. A slide of large dense charts can
  pass the limit too; look at it before splitting.
- whitespace: AeSlides' excessive-whitespace measure, the share of the content area with no ink anywhere in the
  201 x 151 px window around it, so only large empty regions count. Over EMPTY, half the content area is empty.
- balance: AeSlides' visual imbalance, the distance of the centroid of the inked area from the middle of the
  content area, in tolerances of X_TOL of the width and Y_TOL of the height; a sideways lean counts more than a
  vertical one. Over 1 the slide leans to one side. The tolerances are wider than AeSlides' (0.05, 0.15) because
  body text here is left-aligned and starts at the top.
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import pymupdf
from PIL import Image
from pptx import Presentation

ASSETS = Path(__file__).parent
WIDTH = 1280  # px, the width AeSlides renders at
INK_LEVEL = 235  # gray level under which a pixel is ink
GROW = 13  # px
WHITESPACE_WINDOW = (201, 151)  # px, width x height
X_TOL, Y_TOL = 0.2, 0.35
CROWDED, EMPTY = 0.45, 0.5
CONTENT = (0.5, 1.45, 9.5, 4.85)  # in: left, top, right, bottom
SKIPPED_LAYOUTS = ("Title", "Section Header")


def render(path):
    """The deck as a PDF, rendered by LibreOffice with the bundled Inter."""
    out = Path(tempfile.mkdtemp())
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(out), str(path)], check=True,
                   capture_output=True, env={**os.environ, "FONTCONFIG_FILE": str(ASSETS / "fonts.conf")})
    return out / (Path(path).stem + ".pdf")


def box_mean(a, w, h):
    """Mean over a w x h window around each pixel, from an integral image (edges padded by reflection)."""
    padded = np.pad(a, ((h // 2 + 1, h // 2), (w // 2 + 1, w // 2)), mode="reflect")
    s = padded.cumsum(0).cumsum(1)
    return (s[h:, w:] - s[:-h, w:] - s[h:, :-w] + s[:-h, :-w]) / (w * h)


def metrics(page, ppi):
    """(fill, whitespace, balance) of one slide."""
    pix = page.get_pixmap(matrix=pymupdf.Matrix(WIDTH / page.rect.width, WIDTH / page.rect.width))
    gray = np.asarray(Image.frombytes("RGB", (pix.width, pix.height), pix.samples).convert("L"), dtype=float)
    ink = (gray < INK_LEVEL).astype(float)
    left, top, right, bottom = (int(v * ppi) for v in CONTENT)
    inked = (box_mean(ink, GROW, GROW) > 0)[top:bottom, left:right]
    fill = float(inked.mean())
    whitespace = float((box_mean(ink, *WHITESPACE_WINDOW)[top:bottom, left:right] == 0).mean())
    if not inked.any():
        return fill, whitespace, 0.0
    ys, xs = np.nonzero(inked)
    x, y = xs.mean() / inked.shape[1], ys.mean() / inked.shape[0]
    return fill, whitespace, float(np.hypot((x - 0.5) / X_TOL, (y - 0.5) / Y_TOL))


def contact_sheet(pdf, columns=4, width=480):
    """Every page of the PDF, small, on one image beside it, numbered by position."""
    pages = []
    for page in pymupdf.open(pdf):
        pix = page.get_pixmap(matrix=pymupdf.Matrix(width / page.rect.width, width / page.rect.width))
        pages.append(Image.frombytes("RGB", (pix.width, pix.height), pix.samples))
    w, h = pages[0].size
    gap = 8
    sheet = Image.new("RGB", (columns * (w + gap) + gap, -(-len(pages) // columns) * (h + gap) + gap), "#9AA0A6")
    for i, image in enumerate(pages):
        sheet.paste(image, (gap + i % columns * (w + gap), gap + i // columns * (h + gap)))
    out = pdf.with_name(pdf.stem + "-sheet.png")
    sheet.save(out)
    return out


def main(path):
    prs = Presentation(path)
    ppi = WIDTH / (prs.slide_width / 914400)
    flagged = False
    pdf = render(path)
    print(f"contact sheet: {contact_sheet(pdf)}")
    for n, (slide, page) in enumerate(zip(prs.slides, pymupdf.open(pdf)), 1):
        if slide.slide_layout.name in SKIPPED_LAYOUTS:
            continue
        fill, whitespace, balance = metrics(page, ppi)
        notes = []
        if fill > CROWDED:
            notes.append("crowded: cut words, give it more space, or split it")
        if whitespace > EMPTY:
            notes.append("mostly empty: enlarge the exhibit, or merge it with a neighbor")
        if balance > 1:
            notes.append("leans to one side: rebalance the columns")
        flagged |= bool(notes)
        line = f"slide {n}: fill {fill:.2f}, whitespace {whitespace:.2f}, balance {balance:.2f}"
        print(line + ("  <- " + "; ".join(notes) if notes else ""))
    return 1 if flagged else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
