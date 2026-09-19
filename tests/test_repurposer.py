"""Unit tests for the multi-channel ContentRepurposer."""

import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from prose_lint.repurposer import ContentRepurposer


class TestContentRepurposer(unittest.TestCase):
    def setUp(self):
        self.repurposer = ContentRepurposer()
        self.sample_text = (
            "# Arch Doorway Dimensions Guide\n\n"
            "Designing an interior archway requires calculating wall thickness and header clearance. "
            "Standard passageway arches measure 36 inches in width and 84 inches in height. "
            "Preserving a minimum 12-inch reveal between the springline and the ceiling maintains visual balance. "
            "For drywall framing, pre-formed arch kits reduce installation labor by 65% compared to manual plywood ribbing.\n\n"
            "Material selection directly impacts acoustic performance and long-term durability. "
            "Solid pine jambs provide greater structural resistance than hollow core composite materials."
        )

    def test_audio_script_generation(self):
        bundle = self.repurposer.transpile(self.sample_text, focus_keyword="Arch Dimensions")
        self.assertGreater(bundle.audio_word_count, 10)
        self.assertIn('<break time="450ms"/>', bundle.audio_ssml_script)

    def test_cinematography_prompts(self):
        bundle = self.repurposer.transpile(self.sample_text, focus_keyword="Arch Dimensions")
        self.assertEqual(len(bundle.cinematography_prompts), 5)
        self.assertIn("Stage 1", bundle.cinematography_prompts[0])
        self.assertIn("Stage 5", bundle.cinematography_prompts[4])

    def test_pinterest_pins_formatting(self):
        bundle = self.repurposer.transpile(self.sample_text, focus_keyword="Arch Dimensions")
        self.assertEqual(len(bundle.pinterest_pins), 3)
        for pin in bundle.pinterest_pins:
            self.assertLessEqual(len(pin.title), 100)
            self.assertLessEqual(len(pin.description), 500)
            self.assertIn("showing", pin.alt_text)

    def test_llms_txt_snippet(self):
        bundle = self.repurposer.transpile(self.sample_text, focus_keyword="Arch Dimensions")
        self.assertIn("## Arch Dimensions", bundle.llms_txt_snippet)
        self.assertIn("Direct Citation Summary:", bundle.llms_txt_snippet)


if __name__ == "__main__":
    unittest.main()
