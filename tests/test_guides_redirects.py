from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class GuidesRedirectTest(unittest.TestCase):
    def test_old_access_url_redirects_to_guides_catalog(self):
        html = (ROOT / "claude-knopka-za-knopkoy" / "index.html").read_text(encoding="utf-8")
        target = "https://thezhanna-ai.github.io/guides/claude-ai/podklyuchenie-iz-rossii/"
        self.assertIn(f'content="0; url={target}"', html)
        self.assertIn(f'rel="canonical" href="{target}"', html)

    def test_old_profile_url_redirects_to_guides_catalog(self):
        html = (ROOT / "claude-knopka-za-knopkoy" / "o-sebe" / "index.html").read_text(encoding="utf-8")
        target = "https://thezhanna-ai.github.io/guides/claude-ai/kak-rasskazat-o-sebe/"
        self.assertIn(f'content="0; url={target}"', html)
        self.assertIn(f'rel="canonical" href="{target}"', html)


if __name__ == "__main__":
    unittest.main()
