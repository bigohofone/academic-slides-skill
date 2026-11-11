"""Building blocks for decks made from theme.pptx: the grid, text, figures, cards, tables and flows. Each helper
applies the design system (design-guidelines.md), so a slide composed from them stays on the grid and in the type scale.

    import sys; sys.path.insert(0, "{skill-dir}/assets")
    from slides import new_deck, add_slide, add_bullets, add_image, rows, save

    prs = new_deck()
    slide = add_slide(prs, "Title Only", "A finding in one sentence")
    add_bullets(slide, 0, 4, *rows(0, 4), [[("Lead-in: ", True), ("the point", False)], (1, "a sub-point")])
    add_image(slide, 4, 8, *rows(0, 4), "figures/result.png", valign="middle")
    save(prs, "talk.pptx")

Text arguments: a paragraph is a str, a list of runs, or (level, str or runs) for a sub-point (level 1 or 2).
A run is (text, style...) where each style is True or "strong" (emphasis: dark navy instead of the gray body
color), "accent" (the theme blue), "underline" (with emphasis, sparingly), "italic", "super" or "sub" (Inter has few Unicode superscripts, e.g. no ᵀ),
or a hex color like "#EE6677" (to name a figure's series in its own color). There is one weight, Inter Regular:
emphasis is color, never weight.
"""
import tempfile
from pathlib import Path

from PIL import ImageFont
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_LINE_DASH_STYLE, MSO_THEME_COLOR
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

from measure import balance_title, fix_runts, measure

ASSETS = Path(__file__).parent
THEME = ASSETS / "theme.pptx"

# Colors not in the theme's color scheme (body text, the theme blue and the backgrounds are; see theme.py).
STRONG = "1B3A7A"  # dark navy: titles, emphasis, table rules and lines, equations
CARD_FILL = "EDF2F7"  # the light tint of cards and flow steps

# Grid: the 9 in between the 0.5 in side margins is 12 columns with 0.2 in gutters, and the content height
# (1.45 in to 4.75 in) is 4 rows with the same gutters. Every block starts on a column and a row.
LEFT, WIDTH = 0.5, 9.0
COLUMNS, GUTTER = 12, 0.2
COLUMN = (WIDTH - (COLUMNS - 1) * GUTTER) / COLUMNS
CONTENT_TOP, CONTENT_BOTTOM, BLOCK_GAP = 1.45, 4.75, GUTTER
CONTENT_H = CONTENT_BOTTOM - CONTENT_TOP
ROWS = 4
ROW = (CONTENT_H - (ROWS - 1) * BLOCK_GAP) / ROWS

# Text: line spacing 1.15; 10 pt before a top-level paragraph, 4 pt before a sub-point; bullets by level.
LINE_SPACING = 1.15
PARAGRAPH_GAP_PT, SUB_GAP_PT = 10, 4
BULLETS = "•–◦"
INTER_LINE = (1984 + 494) / 2048 * LINE_SPACING  # Inter's line pitch, in em

# Cards: 8 pt corners, no border; padding 0.15 in < the 0.2 in gutter between cards. A text line's box starts
# 0.45 em above its capitals (measured for Inter at 1.15 spacing), so the top inset is trimmed by that much to
# make the visible gap above the text equal the others.
CARD_RADIUS = 8 / 72
CARD_PADDING = 0.15
CARD_HEADING_PT, CARD_BODY_PT = 17, 15
CARD_HEADING_GAP_PT, CARD_ITEM_GAP_PT = 4, 6
CAP_OFFSET_EM = 0.45

# Tables: 13 pt text; rules above, under the header and below, dark navy; no vertical lines.
TABLE_PT = 13
CELL_PADDING = 0.08  # in, left and right inside a cell; none on the table's outer edges
CELL_LINES = ["lnL", "lnR", "lnT", "lnB", "lnTlToBr", "lnBlToTr", "cell3D", "noFill", "solidFill", "gradFill",
              "blipFill", "pattFill", "grpFill", "headers", "extLst"]  # the order OOXML requires inside a:tcPr

ALIGN = {"left": PP_ALIGN.LEFT, "center": PP_ALIGN.CENTER, "right": PP_ALIGN.RIGHT}


# Grid

def box(first_column, span, y, h):
    """(x, y, w, h) in inches for a box that starts at a grid column (0-11) and spans `span` columns."""
    return LEFT + first_column * (COLUMN + GUTTER), y, span * COLUMN + (span - 1) * GUTTER, h


def rows(first_row, span):
    """(y, h) in inches for a block that starts at a grid row (0-3) and spans `span` rows."""
    return CONTENT_TOP + first_row * (ROW + BLOCK_GAP), span * ROW + (span - 1) * BLOCK_GAP


def next_row(bottom):
    """The first grid row that starts at least a gutter below `bottom` (inches); ROWS when none is left."""
    return next((r for r in range(ROWS) if rows(r, 1)[0] >= bottom + BLOCK_GAP - 0.01), ROWS)


def center_vertically(shapes):
    """Move a group of shapes, keeping their spacing, so the group sits in the vertical middle of the content area."""
    top = min(s.top for s in shapes)
    bottom = max(s.top + s.height for s in shapes)
    shift = int(Inches(CONTENT_TOP) + (Inches(CONTENT_H) - (bottom - top)) / 2) - top
    for s in shapes:
        s.top += shift
    return shapes


def resize(shape, first_column, span, y, h):
    """Move and resize a shape (e.g. a placeholder) onto the grid. Sets all four values: setting only some of a
    placeholder's size makes python-pptx write 0 for the others."""
    x, y, w, h = box(first_column, span, y, h)
    shape.left, shape.top, shape.width, shape.height = Inches(x), Inches(y), Inches(w), Inches(h)
    return shape


# Deck

def new_deck():
    """The theme without its example slides."""
    prs = Presentation(THEME)
    for sld_id in list(prs.slides._sldIdLst):
        prs.part.drop_rel(sld_id.rId)
        prs.slides._sldIdLst.remove(sld_id)
    return prs


def fill(shape, paragraphs):
    """Write paragraphs (see the module docstring) into a shape's text frame."""
    tf = shape.text_frame
    for i, para in enumerate(paragraphs):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        if isinstance(para, tuple) and isinstance(para[0], int):
            p.level, para = para
        for text, *styles in [(para,)] if isinstance(para, str) else para:
            run = p.add_run()
            run.text = text
            names = {("strong" if k == 0 else "accent") if style is True else style
                     for k, style in enumerate(styles) if style}
            colors = [name for name in names if name.startswith("#")]
            if "italic" in names:
                run.font.italic = True
            if "underline" in names:
                run.font.underline = True
            if "super" in names or "sub" in names:
                run.font._rPr.set("baseline", "30000" if "super" in names else "-25000")
            if colors:
                run.font.color.rgb = RGBColor.from_string(colors[0][1:])
            elif "accent" in names:
                run.font.color.theme_color = MSO_THEME_COLOR.ACCENT_1
            elif "strong" in names:
                run.font.color.rgb = RGBColor.from_string(STRONG)


def add_slide(prs, layout_name, title, notes=None, **placeholders):
    """A slide on a theme layout. title: a str or runs. notes: what the speaker says on it. placeholders:
    p<idx>=paragraphs, e.g. p1=[...], p13=["footnote"]."""
    layout = next(layout for layout in prs.slide_layouts if layout.name == layout_name)
    slide = prs.slides.add_slide(layout)
    if isinstance(title, str):
        slide.shapes.title.text = title
    else:
        fill(slide.shapes.title, [title])
    for key, paragraphs in placeholders.items():
        fill(slide.placeholders[int(key[1:])], paragraphs)
    if notes:
        slide.notes_slide.notes_text_frame.text = notes
    return slide


def tidy(prs):
    """Delete empty placeholders (their prompt text shows in the editor), drop the gap above each text's first
    paragraph, break two-line titles at a natural point, and pull single-word last lines back with at most 0.5 pt
    tighter spacing."""
    for slide in prs.slides:
        for ph in list(slide.placeholders):
            if ph.has_text_frame and not ph.text_frame.text:
                ph.element.getparent().remove(ph.element)
        for shape in slide.shapes:
            if shape.has_text_frame:
                shape.text_frame.paragraphs[0].space_before = Pt(0)
                fix_runts(shape, slide)
        title = slide.shapes.title
        if title is not None and title.has_text_frame and title.text_frame.text:
            balance_title(title, slide)


def save(prs, path):
    tidy(prs)
    prs.save(path)


def write_script(prs, path):
    """Every slide's title and speaker notes in one Markdown file, in slide order, for rehearsing."""
    parts = ["# Script\n"]
    for n, slide in enumerate(prs.slides, 1):
        title = slide.shapes.title.text_frame.text.replace("\v", " ") if slide.shapes.title else ""
        notes = slide.notes_slide.notes_text_frame.text if slide.has_notes_slide else ""
        parts.append(f"## {n}. {title}\n\n{notes}\n")
    Path(path).write_text("\n".join(parts))


# Text

def add_text(slide, first_column, span, y, h, paragraphs, size=15, align="left", color=MSO_THEME_COLOR.TEXT_1):
    """Free text on the grid, for content no placeholder holds (captions, an equation's terms, a big number).
    h=None fits the height to the text, so the next block can start right under it."""
    auto_height = h is None
    x, y, w, h = box(first_column, span, y, h or 1)
    shape = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = shape.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    fill(shape, paragraphs)
    for i, p in enumerate(tf.paragraphs):
        p.alignment = ALIGN[align]
        p.line_spacing = LINE_SPACING
        p.space_before = Pt(0 if i == 0 else PARAGRAPH_GAP_PT if p.level == 0 else SUB_GAP_PT)
        for run in p.runs:
            run.font.size = Pt(size)
            if run.font.color.type is None:
                run.font.color.theme_color = color
    if auto_height:
        fix_runts(shape, slide)
        shape.height = Inches(measure(shape, slide)[0] + 0.02)
    return shape


def add_bullets(slide, first_column, span, y, h, paragraphs, size=15):
    """Bulleted text anywhere on the grid, bullets by level (• – ◦). h=None fits the height to the text."""
    shape = add_text(slide, first_column, span, y, h or 1, paragraphs, size)
    for p in shape.text_frame.paragraphs:
        pPr = p._p.get_or_add_pPr()
        pPr.set("marL", str(Inches(0.25) * (p.level + 1)))
        pPr.set("indent", str(-Inches(0.25)))
        pPr.append(pPr.makeelement(qn("a:buFont"), {"typeface": "Arial"}))
        pPr.append(pPr.makeelement(qn("a:buChar"), {"char": BULLETS[min(p.level, 2)]}))
    if h is None:
        fix_runts(shape, slide)
        shape.height = Inches(measure(shape, slide)[0] + 0.02)
    return shape


def numbered(shape):
    """Number a placeholder's paragraphs 1., 2., 3. instead of bullets (outlines, algorithm steps)."""
    for p in shape.text_frame.paragraphs:
        pPr = p._p.get_or_add_pPr()
        for old in pPr.findall(qn("a:buChar")) + pPr.findall(qn("a:buNone")):
            pPr.remove(old)
        pPr.append(pPr.makeelement(qn("a:buAutoNum"), {"type": "arabicPeriod"}))
    return shape


def plain(shape):
    """Plain paragraphs, no bullets and no indent, in a placeholder that has bullets by default."""
    for p in shape.text_frame.paragraphs:
        pPr = p._p.get_or_add_pPr()
        for old in pPr.findall(qn("a:buChar")) + pPr.findall(qn("a:buAutoNum")):
            pPr.remove(old)
        pPr.set("marL", "0")
        pPr.set("indent", "0")
        pPr.append(pPr.makeelement(qn("a:buNone"), {}))
    return shape


def align(shape, how):
    """Align every paragraph of a shape: "left", "center" or "right"."""
    for p in shape.text_frame.paragraphs:
        p.alignment = ALIGN[how]
    return shape


# Figures

def figure(slide, idx, path, align="center", valign="top"):
    """An image in a picture placeholder, whole: aspect ratio kept, no crop, centered across the placeholder
    (align="left" for its left edge), at its top (valign="middle" to center it vertically too)."""
    ph = slide.placeholders[idx]
    x, y, w, h = ph.left, ph.top, ph.width, ph.height
    pic = ph.insert_picture(str(path))
    pic.crop_left = pic.crop_right = pic.crop_top = pic.crop_bottom = 0
    iw, ih = pic.image.size
    scale = min(w / iw, h / ih)
    pic.width, pic.height = int(iw * scale), int(ih * scale)
    pic.left = x + ((w - pic.width) // 2 if align == "center" else 0)
    pic.top = y + ((h - pic.height) // 2 if valign == "middle" else 0)


def add_image(slide, first_column, span, y, h, path, align="center", valign="top"):
    """An image in a grid box, whole and at its own aspect ratio, centered across the box (align="left" for its
    left edge), at its top (valign="middle" to center it vertically too)."""
    x, y, w, h = box(first_column, span, y, h)
    pic = slide.shapes.add_picture(str(path), Inches(x), Inches(y))
    scale = min(Inches(w) / pic.width, Inches(h) / pic.height)
    pic.width, pic.height = int(pic.width * scale), int(pic.height * scale)
    if align == "center":
        pic.left = Inches(x) + (Inches(w) - pic.width) // 2
    if valign == "middle":
        pic.top = Inches(y) + (Inches(h) - pic.height) // 2
    return pic


def highlight(slide, picture, left, top, right, bottom):
    """A dotted outline in the theme blue around part of a figure, given as fractions of the picture (0 to 1), to walk
    through a diagram one part per slide. The only shape allowed off the grid and on top of a figure."""
    x0 = picture.left + int(picture.width * left)
    y0 = picture.top + int(picture.height * top)
    outline = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x0, y0, int(picture.width * (right - left)),
                                     int(picture.height * (bottom - top)))
    outline.name = "Highlight"
    outline.adjustments[0] = 0.08
    outline._element.remove(outline._element.find(qn("p:style")))
    outline.fill.background()
    outline.line.color.theme_color = MSO_THEME_COLOR.ACCENT_1
    outline.line.width = Pt(2)
    outline.line.dash_style = MSO_LINE_DASH_STYLE.ROUND_DOT
    return outline


def add_equation(slide, first_column, span, y, tex, size=24, align="center"):
    """A LaTeX equation (matplotlib mathtext in Computer Modern, the serif of LaTeX papers, dark navy) as an image
    at its natural size for `size` pt, from y, centered in its columns by default. For anything Unicode text can't
    set: stacked sub- and superscripts, sums with limits, fractions, \\mathbb, \\mathcal, \\left( \\right).
    mathtext is a subset of LaTeX: no environments (cases, align, matrix); write a case split as two equations."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    with plt.rc_context({"mathtext.fontset": "cm"}):
        fig = plt.figure(figsize=(0.01, 0.01))
        fig.text(0, 0, f"${tex}$", fontsize=size, color=f"#{STRONG}")
        path = Path(tempfile.mkdtemp()) / "equation.png"
        fig.savefig(path, dpi=300, bbox_inches="tight", pad_inches=0.02, transparent=True)
        plt.close(fig)
    x, y, w, _ = box(first_column, span, y, 0)
    pic = slide.shapes.add_picture(str(path), Inches(x), Inches(y))
    natural_w, natural_h = pic.image.size[0] / 300, pic.image.size[1] / 300
    scale = min(1, w / natural_w)
    pic.width, pic.height = Inches(natural_w * scale), Inches(natural_h * scale)
    if align == "center":
        pic.left = Inches(x) + (Inches(w) - pic.width) // 2
    return pic


# Cards

def card_corner(w, h):
    """roundRect's adj value that gives CARD_RADIUS corners on a w x h shape (adj is a share of the shorter side)."""
    return CARD_RADIUS / min(w, h)


def card_paragraphs(heading, body):
    """(text, is_heading, size_pt) for a card's heading and body lines."""
    return ([(heading, True, CARD_HEADING_PT)] if heading else []) + [(line, False, CARD_BODY_PT) for line in body]


def card_insets(paragraphs):
    """(top, bottom) insets in inches that make the visible gaps above and below the text equal CARD_PADDING."""
    return CARD_PADDING - CAP_OFFSET_EM * paragraphs[0][2] / 72, CARD_PADDING


def text_height(paragraphs, width):
    """Height in inches of a card's paragraphs wrapped to `width` inches in Inter, with their gaps."""
    total = 0
    for text, _, size in paragraphs:
        font = ImageFont.truetype(str(ASSETS / "Inter-Regular.ttf"), size * 10)
        lines, line = 1, 0
        for word in text.split(" "):
            w = font.getlength(word + " ") / 10 / 72
            if line and line + w > width:
                lines, line = lines + 1, 0
            line += w
        total += lines * size * INTER_LINE / 72
    gaps = [CARD_HEADING_GAP_PT if i == 1 and paragraphs[0][1] else CARD_ITEM_GAP_PT for i in range(1, len(paragraphs))]
    return total + sum(gaps) / 72


def add_card(slide, first_column, span, y, heading=None, body=(), h=None):
    """A card on the grid: a 17 pt heading in the theme blue over 15 pt body lines, its height fitted to the text
    (or `h`). Only when card-usage-guidelines.md calls for a card; never nest cards. For a group, use add_cards."""
    w = box(first_column, span, y, 0)[2]
    paragraphs = card_paragraphs(heading, body)
    top_inset, bottom_inset = card_insets(paragraphs) if paragraphs else (CARD_PADDING, CARD_PADDING)
    if h is None:
        h = text_height(paragraphs, w - 2 * CARD_PADDING) + top_inset + bottom_inset
    x, y, w, h = box(first_column, span, y, h)
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    card.adjustments[0] = card_corner(w, h)
    card.fill.solid()
    card.fill.fore_color.rgb = RGBColor.from_string(CARD_FILL)
    card.line.fill.background()
    card.name = "Card"
    card._element.remove(card._element.find(qn("p:style")))  # the default style brings a shadow and white text
    tf = card.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.TOP
    tf.margin_left = tf.margin_right = Inches(CARD_PADDING)
    tf.margin_top, tf.margin_bottom = Inches(top_inset), Inches(bottom_inset)
    for i, (text, is_heading, size) in enumerate(paragraphs):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.line_spacing = LINE_SPACING
        p.space_before = Pt(0 if i == 0 else CARD_HEADING_GAP_PT if i == 1 and heading else CARD_ITEM_GAP_PT)
        run = p.add_run()
        run.text = text
        run.font.size = Pt(size)
        run.font.color.theme_color = MSO_THEME_COLOR.ACCENT_1 if is_heading else MSO_THEME_COLOR.TEXT_1
    return card


def add_cards(slide, y, items):
    """2 to 4 cards side by side across the 12 columns, equal widths, one height that fits the tallest.
    items: [(heading, [body lines]), ...]."""
    span = COLUMNS // len(items)
    inner = box(0, span, y, 0)[2] - 2 * CARD_PADDING
    h = max(text_height(card_paragraphs(heading, body), inner) + sum(card_insets(card_paragraphs(heading, body)))
            for heading, body in items)
    return [add_card(slide, i * span, span, y, heading, body, h) for i, (heading, body) in enumerate(items)]


def add_statement(slide, y, label, parts, first_column=0, span=12, equation_pt=20):
    """A formal statement (theorem, lemma, proposition, definition, assumption) on a card: the label as a 17 pt
    heading in the theme blue, then its parts stacked in order, each a paragraph (str or runs) or an equation
    written "$...$" (LaTeX, centered). The card's height fits its parts. Returns [card, *contents], so
    center_vertically() can move the whole group."""
    x, _, w, _ = box(first_column, span, y, 0)
    card = add_card(slide, first_column, span, y, h=1)
    shapes = [card]
    cursor = y + CARD_PADDING - CAP_OFFSET_EM * CARD_HEADING_PT / 72
    for i, part in enumerate([[(label, True, True)]] + list(parts)):
        if i:
            cursor += (CARD_HEADING_GAP_PT if i == 1 else CARD_ITEM_GAP_PT) / 72
        if isinstance(part, str) and part.startswith("$") and part.endswith("$"):
            shape = add_equation(slide, first_column, span, cursor, part[1:-1], equation_pt)
        else:
            shape = add_text(slide, first_column, span, cursor, 1, [part], CARD_HEADING_PT if i == 0 else CARD_BODY_PT)
            shape.left, shape.width = Inches(x + CARD_PADDING), Inches(w - 2 * CARD_PADDING)
            fix_runts(shape, slide)
            shape.height = Inches(measure(shape, slide)[0])
        cursor = (shape.top + shape.height) / 914400
        shapes.append(shape)
    card.height = Inches(cursor + CARD_PADDING - y)
    card.adjustments[0] = card_corner(w, card.height / 914400)
    return shapes


# Tables

def set_cell_line(cell, side, width_pt):
    """A dark navy rule on one side of a table cell ("lnT" or "lnB")."""
    tcPr = cell._tc.get_or_add_tcPr()
    old = tcPr.find(qn(f"a:{side}"))
    if old is not None:
        tcPr.remove(old)
    line = tcPr.makeelement(qn(f"a:{side}"), {"w": str(int(width_pt * 12700)), "cap": "flat", "cmpd": "sng"})
    solid = line.makeelement(qn("a:solidFill"), {})
    solid.append(solid.makeelement(qn("a:srgbClr"), {"val": STRONG}))
    line.append(solid)
    later = [child for child in tcPr if CELL_LINES.index(child.tag.split("}")[1]) > CELL_LINES.index(side)]
    later[0].addprevious(line) if later else tcPr.append(line)


def add_table(slide, y, rows, spans, highlight=None, best=None, align=None, row_h=0.34, first_column=0,
              groups=None, best_groups=None):
    """A table on the grid, its text fixed at 13 pt. rows[0] is the header; spans gives each column's share of grid columns (their sum is
    the table's width: 12 for full width, 6 or 8 beside text), from first_column.
    The header is dark navy; the highlighted row (ours) gets the card tint only, so dark navy in the body always
    means best. best: per column "min", "max" or None, the best value set in dark navy; best_groups: [(first,
    last), ...] 1-based data rows, to find the best within each group (e.g. per setting) instead of the column.
    groups: [(label, n), ...] over the columns after the first adds a header row above, each label spanning its
    n columns ("" for none). align: per column "left", "center" or "right"; by default the first column is left,
    number columns right, mark columns (✓, ✗) centered."""
    head = 2 if groups else 1
    if groups:
        rows = [[""] + [label if k == 0 else "" for label, n in groups for k in range(n)]] + list(rows)
        highlight = highlight + 1 if highlight is not None else None
    x, y, w, h = box(first_column, sum(spans), y, row_h * len(rows))
    frame = slide.shapes.add_table(len(rows), len(spans), Inches(x), Inches(y), Inches(w), Inches(h))
    table = frame.table
    table._tbl.tblPr.find(qn("a:tableStyleId")).text = "{2D5ABB26-0587-4C30-8999-92F81FD0307C}"  # No Style, No Grid
    table.first_row = table.horz_banding = False
    for c, span in enumerate(spans):
        table.columns[c].width = int(Inches(w) * span / sum(spans))
    numeric = [any(ch.isdigit() for row in rows[head:] for ch in str(row[c])) for c in range(len(spans))]
    aligns = align or ["left"] + ["right" if numeric[c] else "center" for c in range(1, len(spans))]
    best_cells = set()
    for first, last in best_groups or [(1, len(rows) - head)]:
        for c, rule in enumerate(best or []):
            if rule:
                values = [(float(rows[r][c]), r) for r in range(first + head - 1, last + head)]
                target = (min if rule == "min" else max)(v for v, _ in values)
                best_cells |= {(r, c) for v, r in values if v == target}
    last_row, last_col = len(rows) - 1, len(spans) - 1
    for r, row in enumerate(rows):
        table.rows[r].height = Inches(row_h)
        for c, value in enumerate(row):
            cell = table.cell(r, c)
            cell.margin_left = Inches(CELL_PADDING if c > 0 else 0)
            cell.margin_right = Inches(CELL_PADDING if c < last_col else 0)
            cell.margin_top = cell.margin_bottom = 0
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            strong = r < head or (r, c) in best_cells
            fill(cell, [[(str(value), strong)]])
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER if r == 0 and groups else ALIGN[aligns[c]]
            if p.runs:
                p.runs[0].font.size = Pt(TABLE_PT)
                if not strong:
                    p.runs[0].font.color.theme_color = MSO_THEME_COLOR.TEXT_1
            if r == highlight:
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor.from_string(CARD_FILL)
            if r == 0:
                set_cell_line(cell, "lnT", 1.25)
            if groups and r == 0 and c > 0 and value:
                set_cell_line(cell, "lnB", 0.5)
            if r == head - 1:
                set_cell_line(cell, "lnB", 0.75)
            if r == head:
                set_cell_line(cell, "lnT", 0.75)
            if r == last_row:
                set_cell_line(cell, "lnB", 1.25)
    if groups:
        c = 1
        for label, n in groups:
            if n > 1:
                table.cell(0, c).merge(table.cell(0, c + n - 1))
            c += n
    return frame


# Flow

def add_flow(slide, y, steps, h=0.9, key=None):
    """2 to 4 steps left to right across the 12 columns, an arrow in each gutter, drawn like the cards: rounded
    tinted boxes without borders, the step at index `key` filled with the theme blue. A step is a str or runs
    (emphasis runs show in dark navy); raise h for steps of three lines or more."""
    span = COLUMNS // len(steps)
    shapes = []
    for i, step in enumerate(steps):
        x, _, w, _ = box(i * span, span, y, h)
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
        shape.adjustments[0] = card_corner(w, h)
        shape._element.remove(shape._element.find(qn("p:style")))
        shape.fill.solid()
        if i == key:
            shape.fill.fore_color.theme_color = MSO_THEME_COLOR.ACCENT_1
        else:
            shape.fill.fore_color.rgb = RGBColor.from_string(CARD_FILL)
        shape.line.fill.background()
        tf = shape.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = Inches(CARD_PADDING)
        fill(shape, [step])
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        p.line_spacing = LINE_SPACING
        for run in p.runs:
            run.font.size = Pt(15)
            if i == key:
                run.font.color.rgb = RGBColor.from_string("FFFFFF")
            elif run.font.color.type is None:
                run.font.color.theme_color = MSO_THEME_COLOR.TEXT_1
        if shapes:
            middle = shape.top + shape.height // 2
            add_arrow(slide, shapes[-1].left + shapes[-1].width, middle, shape.left, middle)
        shapes.append(shape)
    return shapes


def add_arrow(slide, x0, y0, x1, y1):
    """A dark navy arrow from (x0, y0) to (x1, y1), in EMU, without the default style's shadow: to join two
    figures or blocks, usually across a gutter."""
    arrow = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, x0, y0, x1, y1)
    arrow._element.remove(arrow._element.find(qn("p:style")))
    arrow.line.color.rgb = RGBColor.from_string(STRONG)
    arrow.line.width = Pt(1.5)
    ln = arrow.line._get_or_add_ln()
    ln.append(ln.makeelement(qn("a:tailEnd"), {"type": "triangle"}))
    return arrow
