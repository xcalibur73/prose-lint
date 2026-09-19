"""Unit tests for the GEOScorer passage citability evaluator."""

import unittest
from prose_lint.geo_scorer import GEOScorer


class TestGEOScorer(unittest.TestCase):
    def setUp(self):
        self.scorer = GEOScorer()

    def test_proof_counting_and_density(self):
        text = (
            "We upgraded to v1.5.0 and reduced memory usage by 45%. "
            "Server response latency dropped from 350ms to 85ms across 10,000 requests, saving $1,500 monthly."
        )
        result = self.scorer.evaluate(text)
        self.assertGreaterEqual(result.total_empirical_proofs, 5)
        self.assertGreater(result.overall_proof_density, 5.0)

    def test_optimal_chunk_evaluation(self):
        # Create a passage of exactly 145 words (inside 130-175w window)
        words = ["word"] * 145
        passage = " ".join(words)
        result = self.scorer.evaluate(passage)
        self.assertEqual(result.optimal_passages_count, 1)
        self.assertEqual(result.optimal_percentage, 100.0)

    def test_definition_heading_trigger(self):
        text = (
            "## What is Time to First Byte\n\n"
            "Time to First Byte measures the latency between browser request initiation and receiving the initial byte of the HTML response payload from the web server. Under Core Web Vitals standards, an optimal measurement remains under 800ms."
        )
        result = self.scorer.evaluate(text)
        self.assertEqual(result.definition_triggers_detected, 1)
        self.assertGreaterEqual(result.geo_readiness_score, 50.0)

    def test_short_snippets_filtered(self):
        short = "Too short."
        result = self.scorer.evaluate(short)
        self.assertEqual(result.total_passages, 0)


if __name__ == "__main__":
    unittest.main()
