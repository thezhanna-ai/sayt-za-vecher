from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "claude-knopka-za-knopkoy" / "index.html"


class ClaudeHandoutTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = HTML.read_text(encoding="utf-8")

    def test_second_handout_has_permanent_entry_point(self):
        self.assertIn('id="o-sebe"', self.html)
        self.assertIn('id="import-chatgpt"', self.html)
        self.assertIn("Как рассказать Claude о себе", self.html)
        self.assertNotIn("Раздел 02", self.html)

    def test_current_claude_controls_are_named(self):
        for label in (
            "What should Claude call you?",
            "What best describes your work?",
            "Instructions for Claude",
            "Appearance",
            "Chat font",
            "Generate memory from chats",
            "Start import",
        ):
            self.assertIn(label, self.html)

    def test_real_settings_screenshots_are_used(self):
        self.assertIn("assets/claude-settings-general.png", self.html)
        self.assertIn("assets/claude-settings-memory.png", self.html)

    def test_desktop_toc_geometry_matches_canon(self):
        self.assertIn("grid-template-columns: 210px minmax(0, 720px)", self.html)
        self.assertIn("gap: 32px", self.html)
        self.assertIn("width: 260px", self.html)
        self.assertIn("margin-left: -50px", self.html)

    def test_copyable_instructions_are_present(self):
        self.assertIn('id="instructions-template"', self.html)
        self.assertIn('data-copy-target="instructions-template"', self.html)
        self.assertIn("Кто я", self.html)

    def test_only_official_sources_describe_claude_settings(self):
        self.assertIn("10185728-understanding-claude-s-personalization-features", self.html)
        self.assertIn("11817273-use-claude-s-chat-search-and-memory", self.html)
        self.assertIn("12123587-import-and-export-your-memory-from-claude", self.html)


if __name__ == "__main__":
    unittest.main()
