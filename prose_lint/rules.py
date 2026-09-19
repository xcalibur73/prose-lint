"""Deterministic rule engine for lexical deslop, tropes, and formatting invariants."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Finding:
    category: str
    severity: str  # "error", "warning", "info"
    message: str
    line_number: int
    snippet: str
    suggestion: str


class RuleEngine:
    """Evaluates text against deslop dictionaries, punctuation rules, and structure patterns."""

    FORBIDDEN_CHARACTERS = {
        "\u2014": ("em-dash", "Replace with a standard hyphen, colon, or comma."),
        "\u2013": ("en-dash", "Replace with a standard hyphen."),
    }

    AI_TROPES = [
        "delve",
        "delves",
        "delving",
        "delved",
        "tapestry",
        "rich tapestry",
        "testament to",
        "stand as a testament",
        "serves as",
        "serve as",
        "pivotal",
        "pivotal role",
        "beacon",
        "beacon of",
        "game changer",
        "game-changer",
        "unleash",
        "unleashes",
        "unleashing",
        "unleashed",
        "elevate",
        "elevates",
        "elevating",
        "foster",
        "fosters",
        "fostering",
        "harness",
        "harnessing",
        "harnessed",
        "navigating the complexities",
        "navigate the complexities",
        "navigating the landscape",
        "navigate the landscape",
        "digital landscape",
        "ever-evolving landscape",
        "fast-paced world",
        "fast-paced digital",
        "in today's digital",
        "in today's fast-paced",
        "at the forefront",
        "cutting-edge technology",
        "paramount",
        "paramount importance",
        "synergy",
        "holistic approach",
        "paradigm shift",
        "seamless integration",
        "seamlessly",
        "nuanced",
        "nuances",
        "interplay",
        "intricacies",
        "multifaceted",
        "vital role",
        "crucial role",
        "instrumental in",
        "quietly",
        "arguably",
        "speaks volumes",
        "deep dive",
        "double-edged sword",
    ]

    THROAT_CLEARING = [
        "here's the thing",
        "let that sink in",
        "it is worth noting that",
        "it's worth noting that",
        "it should be noted that",
        "it goes without saying",
        "at the end of the day",
        "needless to say",
        "when it comes to",
        "in order to",
        "first and foremost",
        "in this article, we will",
        "in this section, we will",
        "let's explore",
        "let's dive in",
        "let's unpack",
    ]

    CONCLUSIONS = [
        "in conclusion",
        "to conclude",
        "in summary",
        "to sum up",
        "all in all",
        "wrapping up",
        "final thoughts",
    ]

    BOLD_FIRST_BULLET_RE = re.compile(r"^\s*[-*]\s+\*\*([^*]+)\*\*[:\s]")
    RHETORICAL_QUESTION_RE = re.compile(r"\b(why\?|what does this mean\?|the result\?|how\?)\s+[A-Z]", re.IGNORECASE)
    BINARY_CONTRAST_RE = re.compile(r"\bnot\s+([a-z\s]+)\.\s+it(?:'s|\s+is)\s+([a-z\s]+)\.", re.IGNORECASE)

    def __init__(self) -> None:
        # Precompile word boundary regexes for performance
        self._trope_patterns = [
            (trope, re.compile(r"\b" + re.escape(trope) + r"\b", re.IGNORECASE))
            for trope in self.AI_TROPES
        ]
        self._throat_patterns = [
            (phrase, re.compile(r"\b" + re.escape(phrase) + r"\b", re.IGNORECASE))
            for phrase in self.THROAT_CLEARING
        ]
        self._conclusion_patterns = [
            (phrase, re.compile(r"^\s*" + re.escape(phrase) + r"\b", re.IGNORECASE))
            for phrase in self.CONCLUSIONS
        ]

    HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$")

    def scan(self, text: str) -> List[Finding]:
        """Scans the text and returns a list of deterministic findings."""
        findings: List[Finding] = []
        lines = text.splitlines()
        last_heading_level = 0
        h1_count = 0
        in_code_fence = False

        for idx, line in enumerate(lines, start=1):
            if line.startswith("```"):
                in_code_fence = not in_code_fence
                continue

            # 0. Heading hierarchy check (WCAG 2.2 / Google Search Central outline integrity)
            if not in_code_fence:
                heading_match = self.HEADING_RE.match(line)
                if heading_match:
                    level = len(heading_match.group(1))
                    if level == 1:
                        h1_count += 1
                        if h1_count > 1:
                            findings.append(
                                Finding(
                                    category="hierarchy",
                                    severity="warning",
                                    message="Multiple H1 headings detected. Documents should have exactly one H1 to preserve single-topic outline hierarchy.",
                                    line_number=idx,
                                    snippet=line.strip()[:100],
                                    suggestion="Demote secondary H1 to H2.",
                                )
                            )
                    if last_heading_level > 0 and level > last_heading_level + 1:
                        findings.append(
                            Finding(
                                category="hierarchy",
                                severity="warning",
                                message=f"Skipped heading level detected: jumps from H{last_heading_level} directly to H{level}.",
                                line_number=idx,
                                snippet=line.strip()[:100],
                                suggestion=f"Adjust heading depth to H{last_heading_level + 1} to maintain strict WCAG accessibility and search hierarchy.",
                            )
                        )
                    last_heading_level = level

            # 1. Punctuation invariant check
            for char, (label, fix) in self.FORBIDDEN_CHARACTERS.items():
                if char in line:
                    findings.append(
                        Finding(
                            category="punctuation",
                            severity="error",
                            message=f"Forbidden {label} detected: character '{char}' is banned by federation invariant.",
                            line_number=idx,
                            snippet=line.strip()[:100],
                            suggestion=fix,
                        )
                    )

            # 2. Bold-first bullet structure check
            bold_bullet_match = self.BOLD_FIRST_BULLET_RE.match(line)
            if bold_bullet_match:
                findings.append(
                    Finding(
                        category="structure",
                        severity="warning",
                        message="Formulaic bold-first bullet pattern detected. Write natural, varied paragraphs.",
                        line_number=idx,
                        snippet=line.strip()[:100],
                        suggestion="Remove the bold leading prefix and integrate the concept into readable prose.",
                    )
                )

            # 3. Signposted conclusions
            for phrase, pattern in self._conclusion_patterns:
                if pattern.search(line):
                    findings.append(
                        Finding(
                            category="structure",
                            severity="warning",
                            message=f"Signposted conclusion crutch detected: '{phrase}'.",
                            line_number=idx,
                            snippet=line.strip()[:100],
                            suggestion="Remove the meta-signpost and state the final empirical conclusion directly.",
                        )
                    )

            # 4. Throat clearing openers
            for phrase, pattern in self._throat_patterns:
                if pattern.search(line):
                    findings.append(
                        Finding(
                            category="filler",
                            severity="warning",
                            message=f"Throat-clearing filler phrase detected: '{phrase}'.",
                            line_number=idx,
                            snippet=line.strip()[:100],
                            suggestion="Cut the meta-commentary and proceed immediately to the factual statement.",
                        )
                    )

            # 5. Lexical AI tropes
            for trope, pattern in self._trope_patterns:
                if pattern.search(line):
                    findings.append(
                        Finding(
                            category="trope",
                            severity="error",
                            message=f"Predictable AI vocabulary trope detected: '{trope}'.",
                            line_number=idx,
                            snippet=line.strip()[:100],
                            suggestion=f"Replace '{trope}' with concrete technical or descriptive terms.",
                        )
                    )

            # 6. Self-posed rhetorical questions
            if self.RHETORICAL_QUESTION_RE.search(line):
                findings.append(
                    Finding(
                        category="structure",
                        severity="warning",
                        message="Self-posed rhetorical question detected.",
                        line_number=idx,
                        snippet=line.strip()[:100],
                        suggestion="Fold the rhetorical question directly into a declarative statement.",
                    )
                )

        return findings
