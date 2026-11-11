"""Text measurement with Inter's real metrics, shared by check.py and slides.save()."""
import copy
import re
from pathlib import Path

from PIL import ImageFont
from pptx.enum.shapes import PP_PLACEHOLDER

ASSETS = Path(__file__).parent
FONT_FILES = {False: ASSETS / "Inter-Regular.ttf", True: ASSETS / "Inter-Italic.ttf"}  # Inter is the only typeface
LINE_EM = (1984 + 494) / 2048  # Inter's ascent + descent, the line height before line spacing
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
P = "{http://schemas.openxmlformats.org/presentationml/2006/main}"
EMU_PER_PT = 12700
RUNT_SPACING = (-25, -50)  # character spacing tried against a runt, in 1/100 pt; more shows
fonts = {}


def font(size, italic=False):
    """Inter at 10x the size, so getlength() / 10 is in points."""
    key = (size, italic)
    if key not in fonts:
        fonts[key] = ImageFont.truetype(str(FONT_FILES[italic]), size * 10)
    return fonts[key]


def style_chain(shape, slide, level=0):
    """lvlNpPr elements that style this shape's text at a paragraph level, nearest first."""
    tag = f"{A}lstStyle/{A}lvl{level + 1}pPr"
    chain = [shape.text_frame._txBody.find(tag)]
    if shape.is_placeholder:
        layout_ph = slide.slide_layout.placeholders.get(idx=shape.placeholder_format.idx)
        if layout_ph is not None:
            chain.append(layout_ph.text_frame._txBody.find(tag))
        is_title = shape.placeholder_format.type in (PP_PLACEHOLDER.TITLE, PP_PLACEHOLDER.CENTER_TITLE)
        styles = slide.slide_layout.slide_master._element.find(f"{P}txStyles")
        style = styles.find(f"{P}titleStyle") if is_title else styles.find(f"{P}bodyStyle")
        chain.append(style.find(f"{A}lvl{level + 1}pPr"))
    return [el for el in chain if el is not None]


def lookup(elements, path, attr, default):
    for el in elements:
        found = el.find(path) if path else el
        if found is not None and found.get(attr) is not None:
            return found.get(attr)
    return default


def inset(shape, slide, attr):
    """A text inset in EMU, following the slide shape -> layout placeholder -> OOXML default chain."""
    bodies = [shape.text_frame._bodyPr]
    if shape.is_placeholder:
        layout_ph = slide.slide_layout.placeholders.get(idx=shape.placeholder_format.idx)
        if layout_ph is not None:
            bodies.append(layout_ph.text_frame._bodyPr)
    for body in bodies:
        if body.get(attr) is not None:
            return int(body.get(attr))
    return 91440 if attr in ("lIns", "rIns") else 45720


def paragraph_style(shape, slide, p):
    pPr = p._p.find(f"{A}pPr")
    chain = ([pPr] if pPr is not None else []) + style_chain(shape, slide, p.level)
    return {"size": int(lookup(chain, f"{A}defRPr", "sz", 1800)) / 100,
            "spacing": int(lookup(chain, f"{A}lnSpc/{A}spcPct", "val", 100000)) / 100000,
            "after": int(lookup(chain, f"{A}spcAft/{A}spcPts", "val", 0)) / 100,
            "before": int(lookup(chain, f"{A}spcBef/{A}spcPts", "val", 0)) / 100,
            "indent": int(lookup(chain, None, "marL", 0)) / EMU_PER_PT}


def wrap(shape, slide, p):
    """Greedy word wrap of one paragraph: (line count, words on the last line, font size)."""
    style = paragraph_style(shape, slide, p)
    width = (shape.width - inset(shape, slide, "lIns") - inset(shape, slide, "rIns")) / EMU_PER_PT - style["indent"]
    size, words = style["size"], []
    runs = {run._r: run for run in p.runs}
    for el in p._p:
        if el.tag == f"{A}br":
            words.append(None)  # a manual line break
        elif el in runs:
            run = runs[el]
            size = run.font.size.pt if run.font.size else size
            f = font(size, bool(run.font.italic))
            spc = int(run.font._rPr.get("spc", 0)) / 100 if run.font._rPr is not None else 0
            for word in run.text.split(" "):
                parts = re.findall(r"[^-]*-|[^-]+", word)  # a line can also break after a hyphen
                for part in parts:
                    space = 0 if part.endswith("-") else f.getlength(" ") / 10 + spc
                    words.append((f.getlength(part) / 10 + spc * len(part), space))
    lines, line, last = 1, 0, 0
    for word in words:
        if word is None or (line and line + word[0] > width):  # the space before a line break takes no room
            lines, line, last = lines + 1, 0, 0
            if word is None:
                continue
        line += word[0] + word[1]
        last += 1
    return lines, last, size


def measure(shape, slide):
    """(height the text needs, height the box has) in inches, the line count, and the paragraphs that end in a runt."""
    height = lines_total = 0
    runts = []
    paragraphs = shape.text_frame.paragraphs
    for i, p in enumerate(paragraphs):
        style = paragraph_style(shape, slide, p)
        lines, last, size = wrap(shape, slide, p)
        lines_total += lines
        if lines > 1 and last == 1:
            runts.append(i)
        height += lines * size * LINE_EM * style["spacing"] + (style["after"] if i < len(paragraphs) - 1 else 0)
        height += style["before"] if i > 0 else 0
    box = (shape.height - inset(shape, slide, "tIns") - inset(shape, slide, "bIns")) / 914400
    return height / 72, box, lines_total, runts


def fix_runts(shape, slide):
    """Where a paragraph's last line holds a single word, tighten the paragraph's character spacing just enough
    (at most 0.5 pt) to pull that word back onto the line above."""
    for p in shape.text_frame.paragraphs:
        lines, last, _ = wrap(shape, slide, p)
        if lines < 2 or last != 1:
            continue
        for spc in RUNT_SPACING:
            for run in p.runs:
                run.font._rPr.set("spc", str(spc))
            if wrap(shape, slide, p)[0] < lines:
                break
        else:
            for run in p.runs:
                run.font._rPr.attrib.pop("spc", None)


BREAK_AFTER = (",", ";", ":", "—")
BREAK_BEFORE = {"and", "but", "or", "from", "with", "while", "than", "because", "when", "where", "which", "that",
                "by", "for", "in", "on", "at", "to", "into", "across", "over", "under", "without", "via", "as"}
WEAK_ENDINGS = {"a", "an", "the", "of", "to", "in", "on", "for", "and", "or", "with", "by", "at", "from", "its", "their"}
BOUND_STARTS = {"of", "'s"}  # never start line 2 with these: they bind to the word before


def balance_title(shape, slide):
    """When a title wraps to two lines, break it at a natural point instead: after a comma, semicolon, colon or
    dash, or before a conjunction or preposition, with both lines fitting and as even as possible; never leaving
    a weak word (a, the, of, ...) at the end of line 1 or a single word on line 2."""
    p = shape.text_frame.paragraphs[0]
    if len(shape.text_frame.paragraphs) != 1 or p._p.find(f"{A}br") is not None:
        return
    lines, _, size = wrap(shape, slide, p)
    if lines != 2:
        return
    f = font(size)
    width = (shape.width - inset(shape, slide, "lIns") - inset(shape, slide, "rIns")) / EMU_PER_PT
    words = p.text.split(" ")
    measure_words = lambda ws: f.getlength(" ".join(ws)) / 10
    best = None
    for k in range(2, len(words) - 1):
        first, second = words[:k], words[k:]
        w1, w2 = measure_words(first), measure_words(second)
        if w1 > width or w2 > width or first[-1].lower() in WEAK_ENDINGS or second[0].lower() in BOUND_STARTS:
            continue
        score = abs(w1 - w2)
        if first[-1].endswith(BREAK_AFTER):
            score -= width * 0.5
        elif second[0].lower() in BREAK_BEFORE:
            score -= width * 0.25
        if best is None or score < best[0]:
            best = (score, k)
    if best is None:
        return
    offset = len(" ".join(words[:best[1]]))  # the space before the second line's first word
    position = 0
    for run in p.runs:
        if position + len(run.text) > offset:
            cut = offset - position
            before, after = run.text[:cut], run.text[cut + 1:]
            run.text = before
            tail = copy.deepcopy(run._r)
            tail.find(f"{A}t").text = after
            br = run._r.makeelement(f"{A}br", {})
            rPr = run._r.find(f"{A}rPr")
            if rPr is not None:
                br.append(copy.deepcopy(rPr))
            run._r.addnext(br)
            br.addnext(tail)
            return
        position += len(run.text)
