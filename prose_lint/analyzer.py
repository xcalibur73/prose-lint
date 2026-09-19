"""Cadence, burstiness, readability, and stylometric analyzer."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class ProseMetrics:
    total_words: int
    total_sentences: int
    total_paragraphs: int
    avg_sentence_length: float
    burstiness_score: float  # Standard deviation of sentence word counts
    cadence_verdict: str     # "High Burstiness (Natural)", "Moderate Variance", "Monotonous (AI Risk)"
    flesch_reading_ease: float
    flesch_kincaid_grade: float
    type_token_ratio: float  # Lexical diversity (0.0 to 1.0)
    passive_voice_count: int
    passive_voice_percentage: float


class ProseAnalyzer:
    """Calculates statistical burstiness, readability grades, and cadence metrics."""

    PASSIVE_VOICE_RE = re.compile(
        r"\b(am|is|are|was|were|be|been|being)\s+([a-z]+ed|[a-z]+en|[a-z]+t)\b",
        re.IGNORECASE,
    )
    SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9])")
    WORD_RE = re.compile(r"\b[a-zA-Z0-9_-]+\b")
    SYLLABLE_VOWEL_RE = re.compile(r"[aeiouy]+", re.IGNORECASE)

    def analyze(self, text: str) -> ProseMetrics:
        """Analyzes text and returns structured stylometric metrics."""
        clean_text = self._strip_markdown(text)
        paragraphs = [p.strip() for p in clean_text.split("\n\n") if p.strip()]
        
        # Sentence segmentation
        raw_sentences = []
        for p in paragraphs:
            split_p = self.SENTENCE_SPLIT_RE.split(p)
            for s in split_p:
                trimmed = s.strip()
                if trimmed and len(trimmed.split()) >= 2:
                    raw_sentences.append(trimmed)

        if not raw_sentences:
            return ProseMetrics(
                total_words=0,
                total_sentences=0,
                total_paragraphs=0,
                avg_sentence_length=0.0,
                burstiness_score=0.0,
                cadence_verdict="Insufficient Content",
                flesch_reading_ease=0.0,
                flesch_kincaid_grade=0.0,
                type_token_ratio=0.0,
                passive_voice_count=0,
                passive_voice_percentage=0.0,
            )

        words = self.WORD_RE.findall(clean_text.lower())
        total_words = len(words)
        total_sentences = len(raw_sentences)
        total_paragraphs = len(paragraphs)

        sentence_lengths = [len(self.WORD_RE.findall(s)) for s in raw_sentences]
        avg_sentence_length = sum(sentence_lengths) / max(total_sentences, 1)

        # Burstiness: Standard Deviation of sentence lengths
        variance = sum((l - avg_sentence_length) ** 2 for l in sentence_lengths) / max(total_sentences, 1)
        burstiness_score = math.sqrt(variance)

        if total_sentences < 4:
            cadence_verdict = "Sample Too Short for Variance"
        elif burstiness_score >= 6.5:
            cadence_verdict = "High Burstiness (Natural Human Rhythm)"
        elif burstiness_score >= 3.8:
            cadence_verdict = "Moderate Variance (Acceptable)"
        else:
            cadence_verdict = "Monotonous Rhythm (Elevated AI Tell)"

        # Syllables and Readability
        total_syllables = sum(self._count_syllables(w) for w in words)
        flesch_ease = self._calc_flesch_reading_ease(total_words, total_sentences, total_syllables)
        fk_grade = self._calc_flesch_kincaid_grade(total_words, total_sentences, total_syllables)

        # Lexical Diversity (Type-Token Ratio)
        unique_words = len(set(words))
        ttr = (unique_words / total_words) if total_words > 0 else 0.0

        # Passive Voice
        passive_matches = len(self.PASSIVE_VOICE_RE.findall(clean_text))
        passive_pct = (passive_matches / total_sentences * 100.0) if total_sentences > 0 else 0.0

        return ProseMetrics(
            total_words=total_words,
            total_sentences=total_sentences,
            total_paragraphs=total_paragraphs,
            avg_sentence_length=round(avg_sentence_length, 1),
            burstiness_score=round(burstiness_score, 2),
            cadence_verdict=cadence_verdict,
            flesch_reading_ease=round(flesch_ease, 1),
            flesch_kincaid_grade=round(fk_grade, 1),
            type_token_ratio=round(ttr, 3),
            passive_voice_count=passive_matches,
            passive_voice_percentage=round(passive_pct, 1),
        )

    def _count_syllables(self, word: str) -> int:
        clean = word.lower()
        if len(clean) <= 3:
            return 1
        matches = self.SYLLABLE_VOWEL_RE.findall(clean)
        count = len(matches)
        if clean.endswith("e") and not clean.endswith("le") and count > 1:
            count -= 1
        return max(count, 1)

    def _calc_flesch_reading_ease(self, words: int, sentences: int, syllables: int) -> float:
        if words == 0 or sentences == 0:
            return 0.0
        score = 206.835 - (1.015 * (words / sentences)) - (84.6 * (syllables / words))
        return max(0.0, min(100.0, score))

    def _calc_flesch_kincaid_grade(self, words: int, sentences: int, syllables: int) -> float:
        if words == 0 or sentences == 0:
            return 0.0
        score = (0.39 * (words / sentences)) + (11.8 * (syllables / words)) - 15.59
        return max(0.0, score)

    def _strip_markdown(self, md: str) -> str:
        # Strip headers, links, formatting
        text = re.sub(r"^#{1,6}\s+", "", md, flags=re.MULTILINE)
        text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
        text = re.sub(r"[*_~`]", "", text)
        text = re.sub(r"<!--[\s\S]*?-->", "", text)
        return text
