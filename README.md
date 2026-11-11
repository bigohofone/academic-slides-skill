# academic-slides-skill

A Claude Code skill for research talks: argument, structure and design rules, built with python-pptx from a ready-made Academic theme (`skills/academic-slides/assets/theme.pptx`) as .pptx files that open cleanly in Google Slides. It can also restyle an existing research deck into the theme. Preview: [`docs/academic-slides-theme.pdf`](docs/academic-slides-theme.pdf).

## Install

In Claude Code:

```
/plugin marketplace add bigohofone/academic-slides-skill
/plugin install academic-slides@academic-slides-skill
```

Update with `/plugin marketplace update academic-slides-skill`.

Without the plugin system, copy the skill folder into your skills directory:

```
git clone https://github.com/bigohofone/academic-slides-skill
cp -r academic-slides-skill/skills/academic-slides ~/.claude/skills/
```

For figures in the same colors, see [academic-figure-skill](https://github.com/bigohofone/academic-figure-skill).

## License

MIT, except the bundled Inter fonts (SIL Open Font License, see `skills/academic-slides/assets/Inter-LICENSE.txt`).

Inspired by [academic-pptx-skill](https://github.com/Gabberflast/academic-pptx-skill). The argument guidelines draw on David Hirshleifer's "Best Practices for Academic Presentations" (2026), itself prompted by [David Kasten's post](https://x.com/David_Kasten/status/2027063865742442521), and on Naegle (2021), "Ten simple rules for effective presentation slides", *PLOS Computational Biology*.
