"""Unit tests for the ProseAnalyzer cadence and burstiness engine."""

import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from prose_lint.analyzer import ProseAnalyzer


class TestProseAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = ProseAnalyzer()

    def test_empty_text_handling(self):
        metrics = self.analyzer.analyze("")
        self.assertEqual(metrics.total_words, 0)
        self.assertEqual(metrics.total_sentences, 0)
        self.assertEqual(metrics.burstiness_score, 0.0)

    def test_high_burstiness_human_writing(self):
        # Mix very short and very long sentences
        text = (
            "We shipped today. "
            "Our team spent forty-two days rewriting the database connection layer to eliminate connection pool exhaustion under sudden traffic spikes. "
            "Latency fell immediately. "
            "Across our three distributed clusters, average query execution times dropped from 240 milliseconds down to 18 milliseconds without requiring database hardware upgrades."
        )
        metrics = self.analyzer.analyze(text)
        self.assertGreaterEqual(metrics.burstiness_score, 6.0)
        self.assertIn("Human", metrics.cadence_verdict)

    def test_monotonous_cadence_detection(self):
        # Equal length sentences (every sentence exactly 7 words)
        text = (
            "The system processes queries with high speed. "
            "Our servers handle requests across all regions. "
            "Each worker thread executes tasks without delay. "
            "The database stores records inside memory cache. "
            "New records arrive every ten whole seconds."
        )
        metrics = self.analyzer.analyze(text)
        self.assertLess(metrics.burstiness_score, 3.5)
        self.assertIn("Monotonous", metrics.cadence_verdict)

    def test_readability_and_diversity(self):
        text = "Simple tools solve difficult problems quickly and reliably for software engineers."
        metrics = self.analyzer.analyze(text)
        self.assertGreater(metrics.total_words, 5)
        self.assertGreater(metrics.type_token_ratio, 0.5)

    def test_passive_voice_detection(self):
        text = (
            "The experiment was conducted by our team. "
            "The results were analyzed over five weeks. "
            "A final deployment was completed successfully."
        )
        metrics = self.analyzer.analyze(text)
        self.assertGreaterEqual(metrics.passive_voice_count, 3)
        self.assertGreater(metrics.passive_voice_percentage, 50.0)


if __name__ == "__main__":
    unittest.main()
