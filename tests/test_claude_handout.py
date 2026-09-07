from html.parser import HTMLParser
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PRIMARY = ROOT / "claude-knopka-za-knopkoy" / "index.html"
SECONDARY = ROOT / "claude-knopka-za-knopkoy" / "o-sebe" / "index.html"


class HeadingParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.h1 = 0

    def handle_starttag(self, tag, attrs):
        if tag == "h1":
            self.h1 += 1


class ClaudeHandoutTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.primary = PRIMARY.read_text(encoding="utf-8")
        cls.secondary = SECONDARY.read_text(encoding="utf-8")

    def test_articles_are_separate_pages(self):
        primary_parser = HeadingParser()
        primary_parser.feed(self.primary)
        secondary_parser = HeadingParser()
        secondary_parser.feed(self.secondary)
        self.assertEqual(primary_parser.h1, 1)
        self.assertEqual(secondary_parser.h1, 1)
        self.assertIn("<title>Как подключить Claude из России</title>", self.primary)
        self.assertIn("<title>Как рассказать Claude о себе</title>", self.secondary)
        self.assertNotIn('id="o-sebe"', self.primary)

    def test_primary_article_uses_approved_structure(self):
        self.assertIn('id="dostup"', self.primary)
        self.assertIn('id="google-account"', self.primary)
        self.assertIn('class="branch-grid"', self.primary)
        self.assertIn("<h3>Выбери страну и сохрани IP</h3>", self.primary)
        self.assertNotIn('class="step-index"', self.primary)

    def test_desktop_toc_geometry_matches_canon(self):
        self.assertIn("grid-template-columns: 210px minmax(0, 720px)", self.primary)
        self.assertIn("gap: 32px", self.primary)
        self.assertIn("width: 260px", self.primary)
        self.assertIn("margin-left: -50px", self.primary)
        self.assertNotIn("padding-left: 50px", self.primary)

    def test_primary_asset_exists(self):
        self.assertTrue((PRIMARY.parent / "assets" / "claude-login-google.png").exists())


if __name__ == "__main__":
    unittest.main()
