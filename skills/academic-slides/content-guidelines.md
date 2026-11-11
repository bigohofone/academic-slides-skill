# Content Guidelines

How the evidence of a talk goes on a slide: figures, tables, equations and citations. Each one is read in seconds from a distance, so each is shaped for that.

## Figures

A figure on a slide is read from across a room, not held at arm's length like a printed page. Figures made for the paper have print-size text and fine detail that disappear on a screen; when you can, use figures made at slide size with text near body size (the academic-figure skill makes them, in this theme's colors). This skill doesn't draw figures itself: use the user's files, and when one is missing, leave its place and tell the user. A figure that only exists in a PDF (a paper, a source deck) is cropped whole with `crop.py`, at 300 dpi so it stays sharp when projected.

Keep figures whole and at their own proportions; stretching or cropping changes what they show. Give the figure the space it needs to be read, and put what to look for above it. In charts, the series the slide is about takes the theme blue and comparisons take grays, so the eye finds it without a legend. Mark the finding on the figure itself, with a dotted outline around the part that matters, rather than leaving the audience to find it.

## Tables

A table is right when exact values matter, such as main results or ablations; for a trend, a chart reads faster. A slide table holds what can be read at a glance, about six columns and eight rows; larger tables keep the rows that make the point and send the full table to a backup slide. `add_table` sets the style: horizontal rules only, the header and the best values in navy, the focal row tinted, numbers right-aligned so digits line up. Give columns room so no cell wraps, put units on the metrics, and say whether lower or higher is better.

## Equations

Display equations are set as in the paper, in a serif, with `add_equation`: the audience recognizes them, and LaTeX handles what plain text can't. Show only the equations the argument needs, and explain the symbols that matter right below, in words. Inline math in text stays in plain Unicode and italics, in the body font. A symbol the body font can't draw well, such as an accented letter, goes into an equation part instead (`add_statement` and `add_equation` both take LaTeX); never switch the body text to another font for it. Emoji in a source deck are the author's content: keep them.

A theorem, lemma, proposition, definition or assumption is a formal statement, different in kind from the talk's own words. It always sits on its card (`add_statement`), the same way every time, so the audience recognizes one at once; what it means goes below the card.

## Citations

Everything borrowed (a claim, a number, a figure) is cited on the slide where it appears, with a superscript mark and the source in the footnote, and listed in full on the References slide. Use the field's citation style, one style throughout. A figure reproduced from a published paper may need the publisher's permission; mention it to the user. Cite only sources the user gave or you read.

## Wording

Define acronyms on first use. Keep bullets parallel and plain, in the words the field uses. A paragraph never ends with a single word alone on its last line; reword it when `save()` can't pull the word back. The narrower the column, the shorter its text must be: a remark in a third or a quarter of the width should fit on one line, and a phrase that wraps there is usually one that can lose a word.
