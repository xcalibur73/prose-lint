"""Unit tests for ProseLint command-line interface."""

import json
import tempfile
import unittest
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from prose_lint.cli import apply_fixes, main


class TestCLI(unittest.TestCase):
    def test_apply_fixes_replaces_em_dash_and_bold_bullets(self):
        text = (
            "Speed \u2014 that is key.\n"
            "- **Target**: Fix the server.\n"
        )
        fixed = apply_fixes(text)
        self.assertNotIn("\u2014", fixed)
        self.assertIn(" - ", fixed)
        self.assertNotIn("**Target**:", fixed)
        self.assertIn("- Target: Fix the server.", fixed)

    def test_cli_missing_file_error_code(self):
        code = main(["non_existent_file_path_12345.md"])
        self.assertEqual(code, 2)

    def test_cli_clean_file_passes(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as tf:
            tf.write(
                "## Core Performance Diagnostics\n\n"
                "We profiled server response times across 50 geographical edges. "
                "The 95th percentile latency settled at 45ms. "
                "Deploying Redis object cache eliminated database connection stalls."
            )
            temp_path = tf.name

        try:
            code = main([temp_path, "--threshold", "40.0"])
            self.assertEqual(code, 0)
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_cli_json_export(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as tf:
            tf.write("Simple test prose for JSON serialization output.")
            temp_path = tf.name

        save_path = temp_path + ".json"
        try:
            code = main([temp_path, "--output", "json", "--save", save_path, "--threshold", "0.0"])
            self.assertEqual(code, 0)
            self.assertTrue(Path(save_path).is_file())
            data = json.loads(Path(save_path).read_text(encoding="utf-8"))
            self.assertIn("metrics", data)
            self.assertIn("geo_evaluation", data)
        finally:
            Path(temp_path).unlink(missing_ok=True)
            Path(save_path).unlink(missing_ok=True)

    def test_cli_gutenberg_export(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as tf:
            tf.write("## Overview\n\nParagraph text here.")
            temp_path = tf.name

        save_path = temp_path + ".html"
        try:
            code = main([temp_path, "--output", "gutenberg", "--save", save_path])
            self.assertEqual(code, 0)
            content = Path(save_path).read_text(encoding="utf-8")
            self.assertIn("<!-- wp:heading", content)
            self.assertIn("<!-- wp:paragraph", content)
        finally:
            Path(temp_path).unlink(missing_ok=True)
            Path(save_path).unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
