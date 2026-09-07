from html.parser import HTMLParser
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2] / "claude-knopka-za-knopkoy" / "o-sebe"
HTML = ROOT / "index.html"


class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.hrefs = []
        self.images = []
        self.h1 = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if tag == "a" and "href" in attrs:
            self.hrefs.append(attrs["href"])
        if tag == "img":
            self.images.append(attrs)
        if tag == "h1":
            self.h1 += 1


class ArticleContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = HTML.read_text(encoding="utf-8")
        cls.parser = Parser()
        cls.parser.feed(cls.source)

    def test_is_standalone_article(self):
        self.assertEqual(self.parser.h1, 1)
        self.assertIn("<title>Как рассказать Claude о себе</title>", self.source)
        self.assertIn('meta name="robots" content="noindex, nofollow"', self.source)
        self.assertNotIn('class="step-index"', self.source)

    def test_beginner_explanation_is_clear(self):
        self.assertIn("чтобы Claude помнил, кто ты, чем занимаешься", self.source)
        self.assertIn("приводить примеры из твоей области", self.source)
        self.assertIn("не придётся каждый раз заново объяснять свой контекст", self.source)
        self.assertIn("который тебе легче читать", self.source)

    def test_current_ui_and_examples_are_shown(self):
        for label in (
            "What should Claude call you?",
            "What best describes your work?",
            "Instructions for Claude",
            "Appearance",
            "Chat font",
            "Generate memory from chats",
            "Include sensitive topics in memory",
            "Start import",
        ):
            self.assertIn(label, self.source)
        self.assertIn("Я психолог", self.source)
        self.assertIn("онлайн-клуб для подростков", self.source)
        self.assertEqual(self.source.count('class="annotation memory-'), 4)

    def test_images_exist(self):
        expected = {"assets/claude-general-example.png", "assets/claude-memory.png"}
        self.assertEqual({image["src"] for image in self.parser.images}, expected)
        for src in expected:
            self.assertTrue((ROOT / src).exists())

    def test_canon_colors_and_compact_cards(self):
        self.assertIn("--info: #E2E8E9", self.source)
        self.assertIn("--info-line: #BBC7CA", self.source)
        self.assertIn("padding: 11px 18px", self.source)
        self.assertNotIn("#EEF2EE", self.source)
        self.assertNotIn("#CFD8D1", self.source)

    def test_buttons_are_orange_and_pressable(self):
        self.assertIn(".copy-button", self.source)
        self.assertIn("background: var(--accent)", self.source)
        self.assertIn(".copy-button:active", self.source)
        self.assertIn("translateY(2px)", self.source)
        self.assertIn('data-copy-target="instructions-template"', self.source)

    def test_toc_uses_current_canon_and_fast_activation(self):
        self.assertIn("grid-template-columns: 210px minmax(0, 720px)", self.source)
        self.assertIn("width: 260px", self.source)
        self.assertIn("margin-left: -50px", self.source)
        self.assertNotIn("padding-left: 50px", self.source)
        self.assertIn("window.innerHeight - 24", self.source)
        self.assertNotIn("Math.min(220", self.source)

    def test_internal_links_resolve(self):
        for href in self.parser.hrefs:
            if href.startswith("#"):
                self.assertIn(href[1:], self.parser.ids)

    def test_only_ordinary_hyphens_are_used(self):
        self.assertIsNone(re.search("[—–]", self.source))

    def test_final_cta_differs_from_first_article(self):
        self.assertIn("Собери свою систему работы с ИИ", self.source)
        self.assertIn("Настроить ИИ под свой проект", self.source)
        self.assertNotIn("От чата Claude.ai к Claude Code", self.source)


if __name__ == "__main__":
    unittest.main()
