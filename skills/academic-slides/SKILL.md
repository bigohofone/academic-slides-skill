---
name: academic-slides
description: "Builds research talks as .pptx decks that open cleanly in Google Slides, from a ready-made Academic theme with python-pptx. Use it for any talk about research, such as a paper at a conference, a seminar, a thesis or dissertation defense, a group meeting, or a guest lecture; whenever the user asks for slides about a paper, study, dataset or thesis; and to restyle an existing research deck into the theme."
---

# Academic Slides

A research talk is an argument made out loud to a room that sees each slide for about a minute. A good slide lets that room get its point at a glance while still listening to the speaker: one claim, the evidence for it, nothing competing. Everything in this skill follows from that. Design each slide yourself with that reader in mind; the theme, the helpers and the checks get the mechanics right so your attention can go to judgment.

## What to read

- [argument-guidelines.md](argument-guidelines.md): what the talk says, in what order, and how each slide earns its place. For a new talk.
- [design-guidelines.md](design-guidelines.md): how a slide looks: the design system (grid, type, color) and the principles of good layout. Always.
- [content-guidelines.md](content-guidelines.md): figures, tables, equations and citations. Always.
- [card-usage-guidelines.md](card-usage-guidelines.md): when grouping needs a card, and when it doesn't. Before drawing any box.
- [restyle-guidelines.md](restyle-guidelines.md): converting an existing deck, where the content is the author's and only the design is yours.

Read them for the reasoning, not as rules to look up: when a case isn't covered, the reasoning tells you what to do. When they pull in different directions, what the user asked comes first, then what the audience can read.

## Workflow

1. **Argument** (new talks). Settle the audience, the time and the one argument. Write the outline as action titles, one per slide, and read the titles alone: they should tell the whole story. Agree on it with the user when the deck is long or the content complex. For a restyle the argument is given; read the whole source deck instead.
2. **Layout plan.** Before building, decide how each kind of content in this deck will look (a figure with its description, a results table, a theorem, a comparison) and keep to it, so the audience learns the deck's visual language once.
3. **Build** with the helpers below, in one Python script in the user's project.
4. **Check** with the tools, then look at every rendered page as the audience would, and fix what reads badly.
5. **Hand over** with what the user needs to know.

## Building

```python
import sys; sys.path.insert(0, "{skill-dir}/assets")
from slides import new_deck, add_slide, add_text, add_image, rows, next_row, save, write_script, CONTENT_BOTTOM

prs = new_deck()  # theme.pptx without its example slides
add_slide(prs, "Title", "Early childhood programs raise adult earnings",
          p1=["SOLE · May 2025", "Jane Smith¹, John Doe²", "¹ University of X · ² Lab Y"])

slide = add_slide(prs, "Title Only", "Program children earn 18% more by age 35", p13=["Source: SSA earnings records."])
lead = add_text(slide, 0, 12, rows(0, 1)[0], None, [[("Earnings at 35, ", False), ("program", True), (" vs control", False)]])
top = rows(next_row((lead.top + lead.height) / 914400), 1)[0]
add_image(slide, 0, 12, top, CONTENT_BOTTOM - top, "figures/earnings.png")
add_slide(prs, "Section Header", "Results", notes="So what did the program change? Start with earnings.")

save(prs, "talk.pptx")  # removes empty placeholders, balances titles, fixes single-word last lines
write_script(prs, "script.md")  # every slide's title and notes, for rehearsing
```

`{skill-dir}` is this skill's base directory. Positions are grid columns (0–11) and rows (0–3): `box(first_column, span, y, h)`, `rows(first_row, span)`, `next_row(bottom)`.

**Layouts** for `add_slide(prs, layout, title, notes=..., p<idx>=...)`, where `notes` is what to say and `p13` is the footnote: Title, Section Header, Title and Content, Two Content, Figure and Text, Figure, Statement, References, Title Only (compose the rest with helpers), Blank.

**Helpers** in `assets/slides.py`; each docstring says what it does and takes:

| Helper | For |
|---|---|
| `add_text`, `add_bullets` | Text in grid columns; `h=None` fits the box to the text |
| `add_image`, `figure` | A figure, whole and centered |
| `add_table` | A table in the theme's style |
| `add_equation` | A display equation, LaTeX set in the serif of papers |
| `add_statement` | A theorem, lemma or definition on its card |
| `add_cards` | A row of cards, when grouping needs them |
| `add_flow`, `add_arrow` | A process in steps; an arrow joining two blocks |
| `highlight` | A dotted outline marking part of a figure |
| `center_vertically`, `numbered`, `plain`, `align`, `resize` | Adjustments |

**Text** is a list of paragraphs. A paragraph is a str, a list of runs, or `(level, ...)` for a sub-point; a run is `(text, style...)`: `True` for emphasis, `True, True` or `"accent"` for the theme blue, `"underline"`, `"italic"`, `"super"`, `"sub"`, or `"#RRGGBB"` for words that name a figure's series.

**Figures from a PDF:** `python {skill-dir}/assets/crop.py paper.pdf 3 "Figure 2" figures/fig2.png` finds the figure above that caption on page 3 and crops it at 300 dpi; `--box x0,y0,x1,y1` (in points) crops a region by hand when the caption doesn't anchor it. Look at every crop.

**Showcase:** `assets/examples.py` builds the example slides in `theme.pptx`, every helper used once in a whole slide. Read it to see how the pieces compose, not as layouts to copy. To change the theme itself, edit `assets/theme.py` and run it.

## Checking

- `python {skill-dir}/assets/check.py deck.pptx` measures text with the font's real metrics: overflow, long titles, wrapping table cells, single words on a last line, and shapes off the grid, overlapping or past the margin. It also estimates the talk's length from the speaker notes.
- `python {skill-dir}/assets/aesthetics.py deck.pptx` renders the deck and measures each slide on its pixels, after AeSlides: how crowded it is, how much of it is empty, whether it leans to one side. It also saves a contact sheet of every slide, to see the deck at once and spot slides that don't look like their siblings.
- `FONTCONFIG_FILE={skill-dir}/assets/fonts.conf soffice --headless --convert-to pdf deck.pptx` renders it with the bundled Inter. Look at every page as someone in the room would: where does the eye land first, is that the point, does anything compete with it, does the slide look like its siblings?

The tools catch mechanics; only looking tells you whether a slide communicates. Before handing over, read the titles alone once more, and make sure every borrowed claim and figure is cited and the deck ends on its conclusions.

## Hand-over

Tell the user how to open the deck in Google Slides (upload the .pptx to Drive, then File → Save as Google Slides; Keynote and PowerPoint need Inter installed from `{skill-dir}/assets/`), which figures are missing, what the checks still report and why it stays, and for a restyle which slides were split. Suggest rehearsing aloud to time.
