"""A short showcase deck, the example slides in theme.pptx: every helper in slides.py used once in a whole slide,
with the content of one made-up ML talk. Read it for how the helpers compose; it is not a set of layouts to pick
from. theme.py runs it to build theme.pptx, and check.py must pass on it.
"""
from pathlib import Path

from slides import (BLOCK_GAP, CONTENT_TOP, add_bullets, add_cards, add_equation, add_flow, add_image, add_slide,
                    add_statement, add_table, add_text, highlight, rows)

FIG = Path(__file__).parent


def title(prs):
    return add_slide(prs, "Title", "Pretraining on unlabeled speech makes low-resource ASR practical",
                     p1=["ICML 2026 · Oral", "Jane Kim¹, Min Park¹, Alex Lee²   jane.kim@example.edu",
                         "¹ Example University · ² Example Lab"])


def points(prs):
    """One column: bullets with lead-ins in dark navy, sub-points, sources in the footnote."""
    return add_slide(prs, "Title and Content", "Supervised ASR needs labels that most languages don't have", p1=[
        [("Labels are scarce: ", True), ("5 of 100 languages have over 100 h of transcripts¹", False)],
        (1, "Transcribing 1 h of speech takes about 8 h of expert time"),
        [("Audio is not: ", True), ("radio and podcasts exist in every language", False)],
        [("Supervised ASR stalls: ", True), ("over 40% WER with 10 h of labels²", False)],
        (1, "Errors double again on accented and noisy speech")],
        p13=["¹ Author et al. (2024), Venue.   ² Author et al. (2023), Venue."])


def section(prs):
    return add_slide(prs, "Section Header", "Method")


def figure_with_remarks(prs):
    """8 + 4: a chart as the focal point, two short remarks beside it."""
    slide = add_slide(prs, "Title Only", "Only a handful of languages have enough labeled speech",
                      p13=["¹ Author et al. (2024), A census of speech corpora, Venue."])
    add_image(slide, 0, 8, *rows(0, 4), FIG / "theme_example_long_tail.png", valign="middle")
    add_bullets(slide, 8, 4, CONTENT_TOP, None, [
        [("5 of 100", True), (" languages have over 100 h of transcripts¹", False)],
        [("Every language", True), (" has unlabeled audio, from radio to podcasts", False)]])
    return slide


def walkthrough(prs):
    """A diagram across rows 0-2 with the part being explained outlined, three parallel points in 4 + 4 + 4 below."""
    slide = add_slide(prs, "Title Only", "Stage 1 learns from audio alone")
    picture = add_image(slide, 0, 12, *rows(0, 3), FIG / "theme_example_overview.png", valign="middle")
    highlight(slide, picture, 0.0, 0.03, 0.665, 0.97)
    for i, point in enumerate([[("Mask: ", True), ("spans of 10 frames, 8% of starts", False)],
                               [("Predict: ", True), ("each masked frame's cluster", False)],
                               [("Re-cluster: ", True), ("100 MFCC clusters, then 500", False)]]):
        add_bullets(slide, i * 4, 4, rows(3, 1)[0], None, [point])
    return slide


def flow(prs):
    """A process without a figure of its own: steps with arrows, the step the talk is about filled blue."""
    slide = add_slide(prs, "Title Only", "Training runs in four steps, and only the last one uses transcripts")
    top, h = rows(0, 3)
    add_flow(slide, top + (h - 0.9) / 2, ["Raw audio", "Masked encoder", "Discrete targets", "CTC fine-tuning"], key=1)
    add_text(slide, 0, 12, rows(3, 1)[0], None, ["Steps 1 to 3 run once per language family; step 4 per language."],
             align="center")
    return slide


def equation(prs):
    """An equation centered on rows 0-1, what each symbol means below it."""
    slide = add_slide(prs, "Title Only", "The loss predicts the targets of masked frames from their context")
    top, h = rows(0, 2)
    line = add_equation(slide, 0, 12, top, r"L = \sum_{t \in M} -\log p(z_t \mid x_{\setminus M}) + \lambda \|\theta\|^2", 28)
    line.top = int((top + (h - line.height / 914400) / 2) * 914400)
    add_text(slide, 2, 8, rows(2, 1)[0], None, [
        [("M ", True), ("masked frames (8% of starts, spans of 10)", False)],
        [("z", True), ("t", True, "sub"), (" k-means cluster of frame t, from the previous iteration", False)],
        [("λ", True, True), (" weight decay; 0.01 in all runs", False)]], align="center")
    return slide


def theorem(prs):
    """A formal statement on a card, mixing text and an equation; what it means below."""
    slide = add_slide(prs, "Title Only", "Re-clustering cannot make the targets worse")
    card = add_statement(slide, CONTENT_TOP, "Proposition 1", [
        "If the encoder lowers the masked-prediction loss, re-clustering its features never raises it:",
        r"$L(\theta_{k+1}; z^{(k+1)}) \leq L(\theta_k; z^{(k)})$"])
    below = (card[0].top + card[0].height) / 914400 + BLOCK_GAP
    add_bullets(slide, 0, 12, below, None, ["So iterations can only help", "Proof in Appendix B"])
    return slide


def results_table(prs):
    """A table with a grouped header, the best value per column in dark navy and our row tinted."""
    slide = add_slide(prs, "Title Only", "Ours has the lowest WER on three of four test sets",
                      p13=["WER (%), lower is better; best per column in dark navy. CV: Common Voice."])
    add_table(slide, CONTENT_TOP, [
        ["Method", "clean", "other", "CV", "FLEURS"],
        ["Supervised", "8.4", "19.2", "21.7", "24.1"], ["Contrastive [1]", "4.6", "10.8", "17.9", "19.8"],
        ["Masked prediction [2]", "3.9", "9.6", "16.9", "18.7"],
        ["Multilingual fine-tuning [3]", "5.3", "12.4", "16.1", "17.5"], ["Ours", "4.0", "9.1", "15.2", "16.6"]],
        [4, 2, 2, 2, 2], highlight=5, best=[None, "min", "min", "min", "min"],
        groups=[("LibriSpeech", 2), ("", 1), ("", 1)])
    return slide


def contributions(prs):
    """Cards, because the three items are of different kinds (card-usage-guidelines.md)."""
    slide = add_slide(prs, "Title Only", "The paper makes three contributions of different kinds")
    cards = add_cards(slide, CONTENT_TOP, [
        ("Dataset", ["8K hours of unlabeled speech in 40 languages, all of it public"]),
        ("Objective", ["Masked prediction of discrete targets, no negative pairs"]),
        ("Analysis", ["When and why pretraining helps below 10 hours of labels"])])
    below = (cards[0].top + cards[0].height) / 914400 + BLOCK_GAP
    add_text(slide, 0, 12, below, None, ["Code, data and models: example.com/project"], align="center")
    return slide


EXAMPLES = [("Title", title), ("Section", section), ("Points", points), ("Figure with remarks", figure_with_remarks),
            ("Diagram walkthrough", walkthrough), ("Flow", flow), ("Equation", equation), ("Theorem", theorem),
            ("Results table", results_table), ("Contributions", contributions)]
