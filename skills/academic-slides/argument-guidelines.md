# Argument Guidelines

What a talk says matters more than how it looks: argument first, then evidence, then layout, then polish. A beautiful deck with a muddled argument fails; a plain deck with a clear one works. These guidelines are about making the argument clear to a room that hears it once, at the speaker's pace, and can't scroll back.

## Know the room

Before outlining, settle who is listening, how long the talk is, and the one argument it makes. Specialists want precision; a mixed room needs the intuition before the formalism, and fewer acronyms. An international audience needs plain sentences without idioms. If the user hasn't said, ask or infer from the venue.

**One argument.** A paper holds more than a talk can carry. Choose the part that can be made clearly in the time, and let the rest wait in backup slides or in the paper. Presenting everything means the audience remembers nothing.

## Shape the story

Give the talk a spine the audience can follow, whatever its subject: where it starts, what is at stake, what moves the argument forward, and where it ends up. State the central claim or question early, by the third slide, because everything after it is evidence for it and the audience needs to know what it is evidence for.

Each slide has one job in that argument. A slide doing two things splits the audience's attention; make it two slides. Each slide should make the next one feel like a natural consequence; when a transition needs a long spoken bridge, the order is probably wrong. In talks longer than about fifteen minutes, section slides at the start of each part help the room keep its place.

## Titles carry the argument

A content slide's title is its takeaway, stated as one plain sentence, with the number when there is one: not "Results" but "Ours has the lowest error on three of four test sets". Someone who reads only the titles, in order, should get the whole argument; if they can't, the outline needs work, not the slides. A title that needs more than two lines isn't sharp yet. Structural slides (title, sections, conclusions, references, backup) keep plain labels.

## Evidence, one piece per slide

Each slide shows at most one exhibit (a chart, table, diagram or equation), and the exhibit proves the title. If it doesn't, change one of them.

A slide should make its point even to someone who can't hear the speaker. So mark the finding on the slide: outline the part of the figure that matters, color the focal series, or state the finding in the first remark. Don't leave the audience to search.

Prefer a chart for trends and comparisons, and a table when exact values matter. Show only what the talk will discuss; an exhibit skipped over is noise. Decoration that carries no information (icons, stock photos, logos on content slides) only competes with the evidence.

## Words on slides

Only titles are full sentences. Body text is short, parallel points, one idea each, with articles and filler dropped where the meaning survives. If the audience is reading, they aren't listening: the slide supports the speaker, it doesn't replace them. Detail belongs in the speaker notes or a backup slide.

## What a talk contains

There is no fixed list of parts: a talk contains what this audience needs to follow and judge its argument, and nothing else. Ask of each slide what the room would miss without it. Whatever the subject, the room needs to know early why the question matters and what the claim is, to see the evidence for each step, to hear where the evidence stops, and to leave with two or three takeaways. Everything borrowed is cited, and backup slides answer the likeliest questions.

The title slide is read in the seconds before the talk starts, so it carries only what the audience needs then: what the talk is about and who is giving it. Each extra line (identifiers, long affiliation lists, logos) is something to read instead of listen; it belongs on a later slide, if anywhere.

End on the conclusions, not on "Thank you": the last slide stays up through the questions, and it should give the room something to ask about.

## Time

At most about one content slide per minute, and a plan to finish a minute or two early, since nerves speed delivery and overrunning eats the questions.

## The script

Write what to say in each slide's speaker notes (`add_slide(..., notes=...)`), and the talk can be timed and rehearsed before anyone hears it. Notes are written to be spoken, not read: short sentences, plain words, and a voice the speaker would actually use. They don't repeat the slide, which the room can read for itself; they say what the slide can't, why it matters and how it follows from the last one. Each slide's notes pick up from the one before and hand over to the next, so the talk sounds like one line of thought rather than a list of slides. A slide that needs a long spoken bridge is in the wrong place.

`check.py` estimates the talk's length from the notes; `write_script` puts them in one file for rehearsing. The estimate is a floor: pauses, pointing and questions add to it, so rehearse aloud before trusting it.
