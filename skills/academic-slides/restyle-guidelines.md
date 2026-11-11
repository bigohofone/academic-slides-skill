# Restyle Guidelines

Restyling converts an existing deck (PDF, PPTX, Keynote export) into this theme. The content is the author's: the slides, their order, every title, word, figure, equation and number, and what is grouped with what. The design is yours, and it should be better than the source, not a copy of it: more consistent, more readable, calmer. The design guidelines apply in full; the argument guidelines don't, because the argument is given.

## Keep the content exact

Don't rewrite, shorten, merge, reorder, add or drop anything. Where the author's wording breaks a guideline (a three-line title, a single word left on a line), keep the words and tell the user. Content includes the marks that connect things: an outline around part of a figure, an arrow from a remark to a term. Redraw those in the theme's style (`highlight`, `add_arrow`), and make every one still connect the same two things: an arrow ends on the words or term it points to, not on the empty part of a text box, and bends around other content rather than stopping short. Decoration is not content: logos on every slide, repeated footers, clip art and icons go; the logos may stay on the title slide. To tell the two apart, ask whether the audience would lose anything the author meant them to get. A running section header does carry something, where the talk is; it becomes a section slide at the start of each part rather than a strip on every slide. A PDF of an animated slide often has one page per build step; those pages are one slide shown in stages, so keep its final, complete state once. Don't add anything the source doesn't have, such as a References slide.

## Redesign the layout

Read the whole source first and sort its slides into kinds (a description with a figure, a figure with remarks, equations, a theorem, a results table). Give each kind one treatment and keep to it, so the restyled deck is consistent even where the source wasn't. Design from the content, not from the source's layout: a source that crammed text beside a figure can stack them; a source that stacked them shouldn't be split into columns. Keep the order in which things are read: a lead-in before what it introduces, a caption after its figure. When a figure is too tall to stack, put it on one side and its lead-in and text on the other, so the text still comes first in the column the eye starts.

## Figures never get worse

A restyle must not make anything harder to read. Crop each figure whole from the source (`crop.py` for a PDF) and give it at least the size it had there; the layout makes room for the figure, not the other way round. Rebuild tables with `add_table` when they fit; a table too large to rebuild stays a crop under the same rule. Re-set screenshot equations with `add_equation`, and put theorems and definitions on their cards. If a figure can't keep its size even with the whole content area, use the whole area and tell the user.

## Dense slides become more slides

Source decks are often far too dense, and a style-only restyle can't cut words. When a slide is crowded or overflows, first use the space fully, then set that slide's body one step smaller (13 pt, never less), then split it into consecutive slides under the same title, the later ones marked "(cont.)", keeping every item in order and in its group. Splitting is normal: dense decks often double in length, and the result is better for it. Split evenly, with the same layout on each part, and repeat the slide's subheading or lead-in on each part so every slide stands on its own. A leftover too small for a slide of its own stays with its neighbor; if that would crowd the neighbor, rebalance the split instead. Connectors between blocks that end up on different slides go; the slide order already carries them.

## Finish

Compare every restyled page with its source page at the same size: nothing lost, no figure smaller, every slide of a kind alike. Keep page renders, trial crops and comparison images in a temporary folder and delete it, leaving the deck, its PDF, the build script and the figures it uses. Tell the user which slides were split, which figures couldn't keep their size, which tables stayed crops, and what the checks still report.
