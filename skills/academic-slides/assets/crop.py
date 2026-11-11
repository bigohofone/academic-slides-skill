"""Usage: python crop.py paper.pdf PAGE "Figure 2" out.png
       python crop.py paper.pdf PAGE --box x0,y0,x1,y1 out.png

Crops a figure from a PDF at 300 dpi, so it stays sharp when projected. With a caption, it finds the figure above
that caption on the page (1-based): the vector drawings and images between the caption and the nearest paragraph of
running text above it, with their axis labels and legends. With --box, it crops that region, in points from the
page's top left. Always look at the result: a caption below a figure is the common case, not the only one.
"""
import re
import sys

import pymupdf

DPI = 300
PARAGRAPH_CHARS = 120  # a text block longer than this is running text, not a label inside the figure
MARGIN = 3  # pt around the figure


def figure_box(page, caption):
    blocks = page.get_text("blocks")
    cap = next(b for b in blocks if " ".join(b[4].split()).startswith(caption))
    cap_left, cap_top, cap_right = cap[0], cap[1], cap[2]
    paragraphs_above = [b for b in blocks if b[3] <= cap_top - 2 and b[2] > cap_left and b[0] < cap_right
                        and len(b[4]) > PARAGRAPH_CHARS and not re.match(r"(Figure|Fig\.|Table)", b[4])]
    top = max((b[3] for b in paragraphs_above), default=0)
    marks = [d["rect"] for d in page.get_drawings()] + [pymupdf.Rect(i["bbox"]) for i in page.get_image_info()]
    marks = [r for r in marks if r.y0 >= top - 1 and r.y1 <= cap_top + 1 and r.x1 > cap_left - 5
             and r.x0 < cap_right + 5 and r.width < page.rect.width * 0.95]
    box = pymupdf.Rect(marks[0])
    for r in marks[1:]:
        box |= r
    for b in blocks:  # labels and legends that sit just outside the drawn marks
        r = pymupdf.Rect(b[:4])
        if r.y0 >= top - 1 and r.y1 <= cap_top + 1 and r.intersects(box + (-20, -20, 20, 20)) and len(b[4]) < PARAGRAPH_CHARS:
            box |= r
    box += (-MARGIN, -MARGIN, MARGIN, MARGIN)
    box.y1 = min(box.y1, cap_top - 1)  # never into the caption
    return box


def crop(pdf, page_number, out, caption=None, box=None):
    page = pymupdf.open(pdf)[page_number - 1]
    clip = pymupdf.Rect(box) if box else figure_box(page, caption)
    page.get_pixmap(dpi=DPI, clip=clip).save(out)
    return tuple(round(v) for v in clip)


if __name__ == "__main__":
    pdf, page_number, how, *rest = sys.argv[1:]
    if how == "--box":
        print(crop(pdf, int(page_number), rest[1], box=[float(v) for v in rest[0].split(",")]))
    else:
        print(crop(pdf, int(page_number), rest[0], caption=how))
