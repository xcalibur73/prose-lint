"""Unit tests for the deslop RuleEngine."""

import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from prose_lint.rules import RuleEngine


class TestRuleEngine(unittest.TestCase):
    def setUp(self):
        self.engine = RuleEngine()

    def test_clean_text_passes_with_zero_findings(self):
        clean = (
            "We measured time to first byte across 50 regional server locations.\n"
            "Cache hits responded in 42ms while unprimed queries completed in 180ms.\n"
            "The direct solution requires configuring Redis object cache on port 6379."
        )
        findings = self.engine.scan(clean)
        self.assertEqual(len(findings), 0)

    def test_detects_forbidden_em_dash(self):
        text = "This optimization \u2014 although controversial \u2014 yielded immediate results."
        findings = self.engine.scan(text)
        punctuation_errors = [f for f in findings if f.category == "punctuation"]
        self.assertGreaterEqual(len(punctuation_errors), 1)
        self.assertEqual(punctuation_errors[0].severity, "error")

    def test_detects_forbidden_en_dash(self):
        text = "Check the range 10\u201320."
        findings = self.engine.scan(text)
        punctuation_errors = [f for f in findings if f.category == "punctuation"]
        self.assertEqual(len(punctuation_errors), 1)

    def test_detects_ai_tropes(self):
        text = (
            "In today's fast-paced digital landscape, it is pivotal to delve into the rich tapestry.\n"
            "This serves as a testament to modern engineering, acting as a beacon of hope."
        )
        findings = self.engine.scan(text)
        tropes = [f for f in findings if f.category == "trope"]
        self.assertGreaterEqual(len(tropes), 4)

    def test_detects_throat_clearing(self):
        text = "Here's the thing: you must test server latency under peak traffic."
        findings = self.engine.scan(text)
        fillers = [f for f in findings if f.category == "filler"]
        self.assertEqual(len(fillers), 1)

    def test_detects_bold_first_bullets(self):
        text = (
            "- **Performance**: We profiled the memory usage.\n"
            "- **Reliability**: All tests passed."
        )
        findings = self.engine.scan(text)
        structure_warnings = [f for f in findings if f.category == "structure"]
        self.assertEqual(len(structure_warnings), 2)

    def test_detects_signposted_conclusions(self):
        text = "In conclusion, the architecture satisfies all service level objectives."
        findings = self.engine.scan(text)
        conclusions = [f for f in findings if "conclusion" in f.message.lower()]
        self.assertEqual(len(conclusions), 1)

    def test_detects_rhetorical_questions(self):
        text = "Why? Because cache invalidation remains a difficult problem in distributed systems."
        findings = self.engine.scan(text)
        rhetorical = [f for f in findings if "rhetorical" in f.message.lower()]
        self.assertEqual(len(rhetorical), 1)

    def test_ignores_standard_hyphen_in_compound_words(self):
        text = "This is a real-time, high-performance, well-architected pipeline."
        findings = self.engine.scan(text)
        punct = [f for f in findings if f.category == "punctuation"]
        self.assertEqual(len(punct), 0)

    def test_detects_multiple_dash_violations_on_different_lines(self):
        text = "Line one \u2014 first.\nLine two \u2013 second."
        findings = self.engine.scan(text)
        punct = [f for f in findings if f.category == "punctuation"]
        self.assertEqual(len(punct), 2)
        self.assertEqual(punct[0].line_number, 1)
        self.assertEqual(punct[1].line_number, 2)

    def test_detects_skipped_heading_hierarchy(self):
        text = "# Main Title\n\n### Subtitle with skipped H2\n\nParagraph text."
        findings = self.engine.scan(text)
        hierarchy = [f for f in findings if f.category == "hierarchy"]
        self.assertEqual(len(hierarchy), 1)
        self.assertIn("jumps from H1 directly to H3", hierarchy[0].message)

    def test_detects_multiple_h1_headings(self):
        text = "# Primary Document Title\n\nIntroduction.\n\n# Secondary Document Title\n\nBody content."
        findings = self.engine.scan(text)
        h1_findings = [f for f in findings if f.category == "hierarchy" and "Multiple H1" in f.message]
        self.assertEqual(len(h1_findings), 1)
        self.assertEqual(h1_findings[0].line_number, 5)

    def test_standard_lead_labels_false_positive_suppression(self):
        text = (
            "- **Note:** Ensure port 443 is open on the ingress controller.\n"
            "- **Warning:** Do not commit database credentials to git.\n"
            "- **Step 1:** Download the configuration manifest.\n"
            "- **Tip:** Leverage Redis caching for frequent queries."
        )
        findings = self.engine.scan(text)
        structure_warnings = [f for f in findings if f.category == "structure"]
        self.assertEqual(len(structure_warnings), 0)


if __name__ == "__main__":
    unittest.main()
