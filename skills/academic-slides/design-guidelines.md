# Design Guidelines

Design here serves one thing: reading. A slide is seen for a minute, from the back of a room, by people also listening to a speaker. Every choice below exists to make the point of a slide land faster, with less effort, and with nothing pulling the eye elsewhere. When a situation isn't covered, ask what helps that reader, and do that.

## The design system

These are fixed by the theme and the helpers. They are deliberately few, because a small, consistent vocabulary is what makes a deck look designed rather than assembled.

**Grid.** The slide is 10 × 5.625 in. Content sits between 0.5 in side margins, on 12 columns with 0.2 in gutters, and between 1.45 in and 4.75 in vertically, on 4 rows with the same gutters (a row holds two lines of body text). Blocks start on a column and span whole columns, and start on a row or a gutter below the block above them. Alignment to a shared grid is what lets separate blocks read as one composition.

**Type.** One typeface, Inter, in one weight, Regular, titles included. Hierarchy comes from size and color, which stay clean on projectors where weights blur together.

| Role | Size |
|---|---|
| Slide titles | 20 pt |
| Subheadings, card headings | 17 pt |
| Body text | 15 pt |
| Tables, footnotes, page numbers | 13 pt |
| Title and section slides | 28 pt |

On this 10 in slide, 15 pt reads like 20 pt on a 13.33 in widescreen slide, the usual minimum for body text. Line spacing is 1.15, with more space between bullets than within them and less before a sub-point. Body text is left-aligned; centering is for things that stand alone (a caption under a centered figure, a single statement).

**Color.** Everything derives from one blue, Paul Tol's #4477AA, the blue of the academic-figure skill's charts, so slides and figures belong together.

| Role | Color | Used for |
|---|---|---|
| Body | gray #6A737C | Running text, quiet enough that emphasis stands out against it |
| Emphasis | dark navy #1B3A7A | Titles, lead-ins, key words, best values, table rules, equations |
| Structure | blue #4477AA | Subheadings, card headings, marks on figures |
| Quiet | gray #8D949B | Footnotes, page numbers |
| Surface | #EDF2F7, #E1EBF4 | Cards and our table row; title and section backgrounds |

Emphasis is color, never weight. An underline may add to it where color alone isn't enough. Words that name a series in a figure may take that series' color.

## Principles

**Hierarchy: one thing first.** Every slide has one point, and the eye should land on what carries it: usually the exhibit, then the title's claim, then the remarks. Size, position and contrast decide where the eye goes, so give them to the thing that matters and take them from everything else. Emphasis works by contrast: a few navy words in gray text stand out; a slide that is half navy has no emphasis at all.

**Reading order.** People read top to bottom, then left to right, and they want to know what to look for before they look. So a description or lead-in goes above its figure, and remarks follow in the order the speaker will point at them. Stacking text above a figure is the natural layout for most slides; it also gives a wide figure the full width.

**Columns only when the content has columns.** One column is the default. Split the width when the content itself is side by side: a tall figure that would shrink under text, parallel items that must read as separate, or two things the audience compares. Splitting text-and-figure just to fill the width makes the eye zigzag and shrinks the figure. When you do split, use proportions the eye reads at once: 1 : 1 (6 + 6), 2 : 1 or 1 : 2 (8 + 4, 4 + 8), three or four equal columns. Odd ratios look like mistakes.

**Proximity and spacing.** Distance tells the audience what belongs together. Things that belong together sit close; separate things sit a clear gap apart. So space always grows outward: lines within a bullet < between bullets < inside a card < between blocks. When the inside of a group is as loose as the gap around it, the grouping disappears.

**Whitespace.** Empty space is not wasted; it is what lets the content be seen. A crowded slide reads as unclear thinking and makes the audience read instead of listen. Nothing runs past the content area, blocks never touch, and a slide with too much on it loses words or becomes two slides. The opposite failure is real too: a slide that is mostly empty, or whose content huddles in one corner, looks unfinished. Fill the content area in balance.

**Consistency.** The audience learns a deck's visual language on the first few slides and then reads by it. If results figures have their description above, all of them do; if a theorem sits on a card, every theorem does. Decide the treatment for each kind of content before building and keep it; vary only when the content is a different kind, never because one slide's text is a little longer.

**Restraint.** Every element on a slide should carry information. No borders, shadows, gradients, icons, clip art or decoration; no boxes where spacing already groups (card-usage-guidelines.md). Figures stay whole at their own proportions. Fewer, quieter elements make the ones that matter visible.

**Honesty.** This is research, not marketing. Results come with their conditions and comparisons; claims are as strong as the evidence. Hero-number slides, superlatives and slogans make researchers trust the work less. Color never carries meaning on its own, so a slide reads in grayscale and for color-blind viewers too.

**Finish.** Small flaws read as carelessness: a single word alone on a line, a title broken mid-phrase, an empty placeholder, two edges almost but not quite aligned. `save()` fixes the first three where it can; the last only careful placement prevents.

## Google Slides

The deck must look the same after Google Slides imports it. That rules out what Google Slides changes or drops: fonts other than Google Fonts (Inter is one), autofit (text never shrinks, so it must fit), Office equations (set them with `add_equation`), native charts (use images), and effects such as gradients, shadows, animations, transitions and embedded media. Hyperlinks and speaker notes survive.

When the user gives their own or an institution's template, it replaces the theme; these principles still apply wherever it doesn't decide.
