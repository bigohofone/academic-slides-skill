import re
import sys
from pathlib import Path

from pptx import Presentation

ASSETS = Path(__file__).parent / "skills/academic-slides/assets"
sys.path.insert(0, str(ASSETS))
import slides
from check import CHECKS

THEME = Presentation(ASSETS / "theme.pptx")


def test_theme_passes_every_check():
    assert [problem for check in CHECKS for problem in check(THEME)] == []


def test_showcase_uses_every_add_helper():
    showcase = (ASSETS / "examples.py").read_text()
    helpers = [name for name in dir(slides) if name.startswith("add_") and name not in ("add_card", "add_arrow")]
    assert [name for name in helpers if not re.search(rf"\b{name}\(", showcase)] == []
