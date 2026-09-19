"""Generative Engine Optimization (GEO) passage citability and proof density evaluator."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class PassageScore:
    passage_index: int
    word_count: int
    is_optimal_chunk: bool  # 134-167 words
    proof_count: int
    proof_density_ratio: float  # proofs per 100 words
    snippet: str
    feedback: str


@dataclass(frozen=True)
class GEOResult:
    total_passages: int
    optimal_passages_count: int
    optimal_percentage: float
    total_empirical_proofs: int
    overall_proof_density: float
    definition_triggers_detected: int
    geo_readiness_score: float  # 0 to 100
    grade: str                  # A, B, C, F
    passages: List[PassageScore]


class GEOScorer:
    """Audits content for AI answer engine citability, empirical proof density, and definition blocks."""

    OPTIMAL_MIN_WORDS = 130
    OPTIMAL_MAX_WORDS = 175

    # Patterns for quantitative proof: percentages, metrics, benchmarks, currency, versions
    PROOF_PATTERNS = [
        re.compile(r"\b\d+(?:\.\d+)?%"),                                       # 84%, 12.5%
        re.compile(r"\b\d+(?:\.\d+)?\s*(?:ms|s|kb|mb|gb|px|rem|em|vw|vh)\b", re.IGNORECASE), # 420ms, 100kb, 16px
        re.compile(r"\$\d+(?:,\d{3})*(?:\.\d+)?"),                             # $1,200, $50
        re.compile(r"\bv\d+\.\d+(?:\.\d+)?\b", re.IGNORECASE),                 # v1.5.0, v2.1
        re.compile(r"\b\d+(?:,\d{3})+\b"),                                     # 10,000
    ]

    DEFINITION_HEADING_RE = re.compile(
        r"^#{2,3}\s+(?:what\s+is|why\s+is|how\s+does|definition\s+of|what\s+are)\b",
        re.IGNORECASE | re.MULTILINE,
    )

    def evaluate(self, text: str) -> GEOResult:
        """Evaluates text against GEO passage guidelines and returns a GEOResult."""
        # Split into conceptual sections by double newline or headers
        sections = [s.strip() for s in re.split(r"\n\s*\n|(?=^#{2,4}\s+)", text, flags=re.MULTILINE) if s.strip()]
        
        # Clean markdown headers from passage word count
        passage_scores: List[PassageScore] = []
        total_proofs = 0
        optimal_count = 0
        total_words = 0

        for idx, sec in enumerate(sections, start=1):
            clean_sec = re.sub(r"^#{1,6}\s+.*$", "", sec, flags=re.MULTILINE).strip()
            words = clean_sec.split()
            w_count = len(words)
            if w_count < 10:
                continue

            total_words += w_count
            is_optimal = self.OPTIMAL_MIN_WORDS <= w_count <= self.OPTIMAL_MAX_WORDS
            if is_optimal:
                optimal_count += 1

            # Count empirical proof markers
            sec_proofs = 0
            for pat in self.PROOF_PATTERNS:
                sec_proofs += len(pat.findall(clean_sec))

            total_proofs += sec_proofs
            proof_density = (sec_proofs / w_count * 100.0) if w_count > 0 else 0.0

            if is_optimal:
                feedback = "Optimal 134-167w citation passage chunk."
            elif w_count < self.OPTIMAL_MIN_WORDS:
                feedback = f"Sub-optimal length ({w_count}w): Expand context to provide complete self-contained answer."
            else:
                feedback = f"Passage exceeds optimal chunking ({w_count}w): Split into focused topic blocks."

            snippet = " ".join(words[:18]) + ("..." if w_count > 18 else "")
            passage_scores.append(
                PassageScore(
                    passage_index=idx,
                    word_count=w_count,
                    is_optimal_chunk=is_optimal,
                    proof_count=sec_proofs,
                    proof_density_ratio=round(proof_density, 2),
                    snippet=snippet,
                    feedback=feedback,
                )
            )

        total_passages = len(passage_scores)
        optimal_pct = (optimal_count / total_passages * 100.0) if total_passages > 0 else 0.0
        overall_density = (total_proofs / total_words * 100.0) if total_words > 0 else 0.0

        # Check for definition headings
        def_matches = len(self.DEFINITION_HEADING_RE.findall(text))

        # Calculate weighted GEO score (0-100)
        # 45% Proof Density (target: 2.0+ proofs per 100w = 45/45)
        proof_score = min(45.0, (overall_density / 2.0) * 45.0)
        # 40% Optimal Chunking (target: 70%+ optimal passages = 40/40)
        chunk_score = min(40.0, (optimal_pct / 70.0) * 40.0)
        # 15% Definition Triggers (at least 1 definition header = 15/15)
        def_score = 15.0 if def_matches > 0 else 5.0

        geo_score = round(proof_score + chunk_score + def_score, 1)

        if geo_score >= 85.0:
            grade = "A"
        elif geo_score >= 70.0:
            grade = "B"
        elif geo_score >= 55.0:
            grade = "C"
        else:
            grade = "F"

        return GEOResult(
            total_passages=total_passages,
            optimal_passages_count=optimal_count,
            optimal_percentage=round(optimal_pct, 1),
            total_empirical_proofs=total_proofs,
            overall_proof_density=round(overall_density, 2),
            definition_triggers_detected=def_matches,
            geo_readiness_score=geo_score,
            grade=grade,
            passages=passage_scores,
        )
