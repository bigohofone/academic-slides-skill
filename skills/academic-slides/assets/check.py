"""Usage: python check.py deck.pptx

Runs every check in CHECKS on the deck and reports the problems. Exits with 1 if anything is reported.

- check_fit: measures every text box with Inter's real metrics (measure.py) and reports text that
  overflows its box, titles longer than two lines (three on the title slide), table cells that wrap,
  and paragraphs whose last line is a single word that save() couldn't pull back.
- check_grid: reports shapes whose left edge isn't on a grid column start or whose right edge
  isn't on a column end (see box() in slides.py). Arrows (connectors) are exempt; figures only have
  to stay inside the side margins, since they keep their aspect ratio and may be centered.
- check_bounds: reports content shapes that run into the footnote and page-number line, and anything
  that runs past the bottom margin.
- check_shadows: reports shapes with a shadow, or with a style whose effect could add one.
- check_overlap: reports shapes whose boxes overlap (text running into a figure or table). Full-bleed
  backgrounds, arrows and the contents of a card (add_statement) are exempt.

Then it prints how long the speaker notes take to say. No maintained library does this better than counting
words, so it counts words at WORDS_PER_MINUTE, a typical presenting pace (120-150 is the usual range).
"""

import sys

from pptx import Presentation
from pptx.enum.shapes import PP_PLACEHOLDER
from pptx.oxml.ns import qn

from measure import EMU_PER_PT, font, measure
from slides import COLUMN, COLUMNS, GUTTER, LEFT, WIDTH

EMU_PER_IN = 914400
COLUMN_STARTS = [LEFT + c * (COLUMN + GUTTER) for c in range(COLUMNS)]
COLUMN_ENDS = [start + COLUMN for start in COLUMN_STARTS]
GRID_TOLERANCE = 0.01  # in

def check_table_cells(n, shape):
    problems = []
    table = shape.table
    for r, row in enumerate(table.rows):
        for c, cell in enumerate(row.cells):
            if cell.is_spanned:
                continue
            span = cell.span_width if cell.is_merge_origin else 1
            width = (sum(table.columns[k].width for k in range(c, c + span)) - cell.margin_left - cell.margin_right) / EMU_PER_PT
            for p in cell.text_frame.paragraphs:
                need = sum(font(run.font.size.pt if run.font.size else 18, bool(run.font.italic)).getlength(run.text) / 10
                           for run in p.runs)
                if need > width:
                    problems.append(f"slide {n}, {shape.name}: cell ({r}, {c}) \"{cell.text}\" wraps; widen its column")
    return problems

def check_fit(prs):
    problems = []
    for n, slide in enumerate(prs.slides, 1):
        for shape in slide.shapes:
            if shape.has_table:
                problems += check_table_cells(n, shape)
            if not shape.has_text_frame or not shape.text_frame.text.strip():
                continue
            need, box, lines, runts = measure(shape, slide)
            for i in runts:
                text = shape.text_frame.paragraphs[i].text
                problems.append(f"slide {n}, {shape.name}: \"{text}\" ends with one word on its last line; "
                                "reword it (save() already tried tighter spacing)")
            if need > box + 0.01:
                problems.append(f"slide {n}, {shape.name}: text needs {need:.2f} in, box is {box:.2f} in")
            max_lines = 3 if slide.slide_layout.name == "Title" else 2  # a paper's full title may need three
            if shape.is_placeholder and shape.placeholder_format.type == PP_PLACEHOLDER.TITLE and lines > max_lines:
                problems.append(f"slide {n}, {shape.name}: title runs {lines} lines, max {max_lines}")
    return problems

def on_any(edge, edges):
    return any(abs(edge - e) <= GRID_TOLERANCE for e in edges)

def on_card(shape, slide):
    """True for text or an equation placed on a card (add_statement): it follows the card's padding, not the grid."""
    return any(card.name == "Card" and card is not shape and card.left <= shape.left
               and shape.left + shape.width <= card.left + card.width and card.top <= shape.top
               and shape.top + shape.height <= card.top + card.height for card in slide.shapes)

def check_grid(prs):
    problems = []
    slide_width = prs.slide_width / EMU_PER_IN
    for n, slide in enumerate(prs.slides, 1):
        for shape in slide.shapes:
            if shape.element.tag == qn("p:cxnSp") or shape.name == "Highlight" or on_card(shape, slide):
                continue  # arrows run through the gutters; highlights sit on a figure; card contents follow its padding
            left = shape.left / EMU_PER_IN
            right = left + shape.width / EMU_PER_IN
            if abs(left) <= GRID_TOLERANCE and abs(right - slide_width) <= GRID_TOLERANCE:
                continue  # full-bleed
            if not on_any(left, COLUMN_STARTS) and shape.element.tag != qn("p:pic"):
                problems.append(f"slide {n}, {shape.name}: left edge {left:.2f} in is not on a column start")
            if shape.element.tag == qn("p:pic"):
                # A figure keeps its aspect ratio and may be centered in its box: it only has to stay inside the margins.
                if left < LEFT - GRID_TOLERANCE or right > LEFT + WIDTH + GRID_TOLERANCE:
                    problems.append(f"slide {n}, {shape.name}: figure runs outside the side margins")
                continue
            if not on_any(right, COLUMN_ENDS):
                problems.append(f"slide {n}, {shape.name}: right edge {right:.2f} in is not on a column end")
    return problems

BOTTOM_MARGIN = 0.4  # in, the theme's bottom padding
FOOTER_BAND = 0.375  # in, the footnote and page-number line above the bottom margin

def check_bounds(prs):
    problems = []
    bottom_margin = prs.slide_height / EMU_PER_IN - BOTTOM_MARGIN
    footer_top = bottom_margin - FOOTER_BAND
    for n, slide in enumerate(prs.slides, 1):
        for shape in slide.shapes:
            top = shape.top / EMU_PER_IN
            bottom = (shape.top + shape.height) / EMU_PER_IN
            if shape.height >= prs.slide_height:
                continue
            limit = bottom_margin if top >= footer_top - GRID_TOLERANCE else footer_top
            if bottom > limit + GRID_TOLERANCE:
                where = "the bottom margin" if limit == bottom_margin else "the footnote and page-number line"
                problems.append(f"slide {n}, {shape.name}: bottom edge {bottom:.2f} in runs into {where} ({limit:.2f} in)")
    return problems

def check_overlap(prs):
    problems = []
    for n, slide in enumerate(prs.slides, 1):
        shapes = [s for s in slide.shapes
                  if s.element.tag != qn("p:cxnSp") and s.name != "Highlight" and s.height < prs.slide_height
                  and not on_card(s, slide)]
        for i, a in enumerate(shapes):
            for b in shapes[i + 1:]:
                w = min(a.left + a.width, b.left + b.width) - max(a.left, b.left)
                h = min(a.top + a.height, b.top + b.height) - max(a.top, b.top)
                if w > EMU_PER_IN * GRID_TOLERANCE and h > EMU_PER_IN * GRID_TOLERANCE:
                    problems.append(f"slide {n}: {a.name} and {b.name} overlap")
    return problems

def check_shadows(prs):
    """No shape may cast a shadow or carry a style that can give it one."""
    problems = []
    for n, slide in enumerate(prs.slides, 1):
        for shape in slide.shapes:
            el = shape.element
            effect_ref = el.find(f".//{qn('a:effectRef')}")
            if el.find(f".//{qn('a:outerShdw')}") is not None or (effect_ref is not None and effect_ref.get("idx") != "0"):
                problems.append(f"slide {n}, {shape.name}: has a shadow (remove its p:style or effect)")
    return problems

CHECKS = [check_fit, check_grid, check_bounds, check_overlap, check_shadows]

WORDS_PER_MINUTE = 130

def talk_length(prs):
    words = sum(len(slide.notes_slide.notes_text_frame.text.split()) for slide in prs.slides if slide.has_notes_slide)
    if not words:
        return "No speaker notes, so no talk length."
    return f"Speaker notes: {words} words, about {words / WORDS_PER_MINUTE:.1f} min at {WORDS_PER_MINUTE} words/min."

def main(path):
    prs = Presentation(path)
    problems = [problem for check in CHECKS for problem in check(prs)]
    print("\n".join(problems) or "No problems found.")
    print(talk_length(prs))
    return 1 if problems else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
