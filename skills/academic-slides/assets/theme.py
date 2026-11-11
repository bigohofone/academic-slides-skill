"""Builds theme.pptx: the Academic theme (colors, fonts, master, slide layouts, and one example slide per layout) that every deck starts from.

Run `python theme.py` after changing anything below, and commit the new theme.pptx.
"""
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.oxml import parse_xml
from pptx.util import Inches

from examples import EXAMPLES
from slides import CARD_FILL, CARD_PADDING, CONTENT_H, CONTENT_TOP, box, card_corner, rows, tidy

OUT = Path(__file__).parent / "theme.pptx"

# Every color is built from one blue: Paul Tol's "bright" blue, the blue of the academic-figure skill's charts.
BLUE = "4477AA"  # structure: subheadings, card headings, outlines on figures
STRONG = "1B3A7A"  # titles, emphasis and table lines: dark navy
TEXT = "6A737C"  # body text: a light, low-saturation gray (a trace of the blue), so the dark navy marks emphasis
MUTED = "8D949B"  # footnotes and page numbers, lighter than the body
ACCENT = BLUE
ACCENT2 = "729ECA"
CARD = CARD_FILL
SKY = "E1EBF4"  # title and section slide background
BG = "FFFFFF"
HEAD_FONT = "Inter"  # one weight everywhere: Inter Regular; emphasis is color, never weight
BODY_FONT = "Inter"
LINE = 115000  # line spacing 1.15
BULLETS = "•–◦"  # bullet mark by indent level

NS = 'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
P = "{http://schemas.openxmlformats.org/presentationml/2006/main}"


def emu(inches):
    return int(Inches(inches))


def level_style(size, color=None, bullet=False, align="l", gap=10):
    bu = '<a:buFont typeface="Arial"/><a:buChar char="•"/>' if bullet else "<a:buNone/>"
    indent = f'marL="{emu(0.25)}" indent="{-emu(0.25)}"' if bullet else 'marL="0" indent="0"'
    fill = f'<a:solidFill><a:srgbClr val="{color}"/></a:solidFill>' if color else ""
    return (f'<a:lvl1pPr {indent} algn="{align}"><a:lnSpc><a:spcPct val="{LINE}"/></a:lnSpc>'
            f'<a:spcBef><a:spcPts val="{gap * 100}"/></a:spcBef><a:spcAft><a:spcPts val="0"/></a:spcAft>{bu}'
            f'<a:defRPr sz="{size * 100}" b="0">{fill}</a:defRPr></a:lvl1pPr>')


def placeholder(shape_id, name, ph, box, prompt, style, anchor="t", inset=0):
    x, y, w, h = (emu(v) for v in box)
    return (f'<p:sp {NS}><p:nvSpPr><p:cNvPr id="{shape_id}" name="{name}"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>'
            f'<p:nvPr>{ph}</p:nvPr></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr>'
            f'<p:txBody><a:bodyPr wrap="square" lIns="{emu(inset)}" tIns="{emu(inset)}" rIns="{emu(inset)}" bIns="{emu(inset)}" anchor="{anchor}"><a:noAutofit/></a:bodyPr>'
            f'<a:lstStyle>{style}</a:lstStyle><a:p><a:r><a:rPr lang="en-US"/><a:t>{prompt}</a:t></a:r></a:p></p:txBody></p:sp>')


def card(shape_id, rect):
    x, y, w, h = (emu(v) for v in rect)
    corner = int(card_corner(rect[2], rect[3]) * 100000)
    return (f'<p:sp {NS}><p:nvSpPr><p:cNvPr id="{shape_id}" name="Card"/><p:cNvSpPr/><p:nvPr userDrawn="1"/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm><a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val {corner}"/></a:avLst></a:prstGeom>'
            f'<a:solidFill><a:srgbClr val="{CARD}"/></a:solidFill><a:ln><a:noFill/></a:ln></p:spPr></p:sp>')


# Same padding on every slide: 0.5 in left and right, 0.4 in top and bottom. The 12-column grid (box) is in slides.py.
TOP, BOTTOM = 0.4, 5.625 - 0.4


TITLE_BOX = box(0, 12, TOP, 1.0)
FOOTNOTE_BOX = box(0, 10, BOTTOM - 0.375, 0.375)
PAGE_NUMBER_BOX = box(10, 2, BOTTOM - 0.375, 0.375)


def title(prompt="Story title: one sentence, at most two lines"):
    return placeholder(2, "Title", '<p:ph type="title"/>', TITLE_BOX, prompt, "")


def body(idx, box, prompt, anchor="t", inset=0, **style):
    return placeholder(10 + idx, f"Body {idx}", f'<p:ph type="body" idx="{idx}"/>', box, prompt, level_style(**style) if style else "", anchor, inset)


def header(idx, box, prompt):
    return body(idx, box, prompt, size=17, color=ACCENT, gap=0)


def footnote():
    return body(13, FOOTNOTE_BOX, "Footnote or source", size=13, color=MUTED, gap=0)


def picture(idx, box):
    return placeholder(10 + idx, f"Figure {idx}", f'<p:ph type="pic" idx="{idx}"/>', box, "Figure", "")


def big_title(box, size, prompt, color, anchor="t"):
    return placeholder(2, "Title", '<p:ph type="title"/>', box, prompt, level_style(size, color=color, gap=0), anchor)


def page_number():
    x, y, w, h = (emu(v) for v in PAGE_NUMBER_BOX)
    return (f'<p:sp {NS}><p:nvSpPr><p:cNvPr id="30" name="Page number"/><p:cNvSpPr txBox="1"/><p:nvPr userDrawn="1"/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr>'
            f'<p:txBody><a:bodyPr wrap="square" lIns="0" tIns="0" rIns="0" bIns="0" anchor="t"><a:noAutofit/></a:bodyPr><a:lstStyle/>'
            f'<a:p><a:pPr algn="r"/><a:fld id="{{B6F15528-21DE-4FAA-801E-634DDDAF4B2B}}" type="slidenum">'
            f'<a:rPr lang="en-US" sz="1300" b="0"><a:solidFill><a:srgbClr val="{MUTED}"/></a:solidFill><a:latin typeface="{BODY_FONT}"/></a:rPr>'
            f'<a:t>‹#›</a:t></a:fld></a:p></p:txBody></p:sp>')


LAYOUTS = [
    ("Title", SKY, [
        big_title(box(0, 12, 0.9, 2.2), 28, "Talk title: the claim or question", STRONG),
        body(1, box(0, 10, 3.2, FOOTNOTE_BOX[1] - 3.2), "Venue · date, then authors, then affiliations: one per line", size=15, color=TEXT, gap=6),
    ]),
    ("Title and Content", None, [
        title(),
        body(1, box(0, 12, CONTENT_TOP, CONTENT_H), "Bullets: a lead-in in dark navy, then the point"),
        footnote(),
    ]),
    ("Statement", None, [
        title(),
        card(20, box(0, 12, *rows(0, 2))),
        body(1, box(0, 12, *rows(0, 2)), "The research question, in one or two sentences", anchor="ctr", inset=CARD_PADDING, size=17, align="ctr", gap=0),
        body(2, box(0, 12, *rows(2, 1)), "Contribution", size=15),
        footnote(),
    ]),
    ("Two Content", None, [
        title(),
        header(1, box(0, 6, CONTENT_TOP, 0.45), "Left header"),
        body(2, box(0, 6, CONTENT_TOP + 0.55, CONTENT_H - 0.55), "Left bullets"),
        header(3, box(6, 6, CONTENT_TOP, 0.45), "Right header"),
        body(4, box(6, 6, CONTENT_TOP + 0.55, CONTENT_H - 0.55), "Right bullets"),
        footnote(),
    ]),
    ("Figure and Text", None, [
        title(),
        picture(1, box(0, 8, CONTENT_TOP, CONTENT_H)),
        body(2, box(8, 4, CONTENT_TOP, CONTENT_H), "Two or three points the figure can't show", size=15, bullet=True),
        footnote(),
    ]),
    ("Figure", None, [
        title(),
        picture(1, box(0, 12, *rows(0, 3))),
        body(2, box(0, 12, *rows(3, 1)), "Caption: what the figure shows", size=15, gap=0),
        footnote(),
    ]),
    ("Section Header", SKY, [
        big_title(box(0, 12, TOP, FOOTNOTE_BOX[1] - TOP), 28, "Section name", STRONG, anchor="ctr"),
    ]),
    ("References", None, [
        title("References"),
        body(1, box(0, 12, CONTENT_TOP, CONTENT_H), "One reference per paragraph, one citation style", size=15),
    ]),
    ("Title Only", None, [title(), footnote()]),
    ("Blank", None, []),
]


def set_theme(master):
    theme = master.part.part_related_by(RT.THEME)
    root = etree.fromstring(theme.blob)
    root.set("name", "Academic")
    scheme = root.find(f".//{A}clrScheme")
    scheme.set("name", "Academic")
    colors = {"dk1": TEXT, "lt1": "FFFFFF", "dk2": STRONG, "lt2": CARD, "accent1": ACCENT, "accent2": ACCENT2,
              "accent3": MUTED, "accent4": SKY, "accent5": "8C8C8C", "accent6": "BFBFBF", "hlink": ACCENT, "folHlink": MUTED}
    for el in scheme:
        el.clear()
        etree.SubElement(el, f"{A}srgbClr", val=colors[etree.QName(el).localname])
    for style in root.iter(f"{A}effectStyle"):  # no shadows, glows or 3D anywhere, even on shapes added later
        for child in list(style):
            style.remove(child)
        etree.SubElement(style, f"{A}effectLst")
    fonts = root.find(f".//{A}fontScheme")
    fonts.set("name", "Academic")
    for part, face in (("majorFont", HEAD_FONT), ("minorFont", BODY_FONT)):
        for script in ("latin", "ea", "cs"):  # symbols like ✓ ✗ — count as ea/cs text in some renderers
            fonts.find(f"{A}{part}/{A}{script}").set("typeface", face)
    theme._blob = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def set_background(element, color):
    c_sld = element.find(f"{P}cSld")
    old = c_sld.find(f"{P}bg")
    if old is not None:
        c_sld.remove(old)
    c_sld.insert(0, parse_xml(f'<p:bg {NS}><p:bgPr><a:solidFill><a:srgbClr val="{color}"/></a:solidFill><a:effectLst/></p:bgPr></p:bg>'))


def set_shapes(element, shapes):
    tree = element.find(f"{P}cSld/{P}spTree")
    for sp in tree.findall(f"{P}sp"):
        tree.remove(sp)
    for xml in shapes:
        tree.append(parse_xml(xml))


def set_master(master):
    set_background(master._element, BG)
    set_shapes(master._element, [title(), body(1, box(0, 12, CONTENT_TOP, CONTENT_H), "Body"), page_number()])
    styles = master._element.find(f"{P}txStyles")
    styles.find(f"{P}titleStyle").clear()
    styles.find(f"{P}titleStyle").append(parse_xml(
        f'<a:lvl1pPr {NS} algn="l"><a:lnSpc><a:spcPct val="{LINE}"/></a:lnSpc><a:spcBef><a:spcPts val="0"/></a:spcBef><a:buNone/>'
        f'<a:defRPr sz="2000" b="0"><a:solidFill><a:srgbClr val="{STRONG}"/></a:solidFill><a:latin typeface="+mj-lt"/></a:defRPr></a:lvl1pPr>'))
    body_style = styles.find(f"{P}bodyStyle")
    body_style.clear()
    for level in range(1, 4):
        margin = emu(0.25 * level)
        body_style.append(parse_xml(
            f'<a:lvl{level}pPr {NS} marL="{margin}" indent="{-emu(0.25)}" algn="l"><a:lnSpc><a:spcPct val="{LINE}"/></a:lnSpc>'
            f'<a:spcBef><a:spcPts val="{1000 if level == 1 else 400}"/></a:spcBef><a:spcAft><a:spcPts val="0"/></a:spcAft><a:buFont typeface="Arial"/><a:buChar char="{BULLETS[level - 1]}"/>'
            f'<a:defRPr sz="1500"><a:solidFill><a:schemeClr val="tx1"/></a:solidFill><a:latin typeface="+mn-lt"/></a:defRPr></a:lvl{level}pPr>'))


prs = Presentation()
prs.slide_width = Inches(10)
prs.slide_height = Inches(5.625)
master = prs.slide_master
set_theme(master)
set_master(master)

layouts = list(prs.slide_layouts)
for layout, (name, bg, shapes) in zip(layouts, LAYOUTS):
    element = layout._element
    element.attrib.pop("type", None)
    element.find(f"{P}cSld").set("name", name)
    if bg:
        set_background(element, bg)
    set_shapes(element, shapes)
for layout in layouts[len(LAYOUTS):]:
    prs.slide_layouts.remove(layout)


# Example slides: the showcase in examples.py, each slide's speaker notes naming it. slides.new_deck() drops them.
for name, build in EXAMPLES:
    slide = build(prs)
    notes = slide.notes_slide.notes_text_frame
    notes.text = f"Showcase: {name}" + ("\n" + notes.text if notes.text else "")

tidy(prs)
for part in prs.part.package.iter_parts():  # the notes master brings its own theme, with shadows; strip it too
    if str(part.partname).startswith("/ppt/theme/"):
        root = part._element if hasattr(part, "_element") else etree.fromstring(part.blob)
        for style in root.iter(f"{A}effectStyle"):
            for child in list(style):
                style.remove(child)
            etree.SubElement(style, f"{A}effectLst")
        if not hasattr(part, "_element"):
            part._blob = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
prs.save(OUT)
print("wrote", OUT)
