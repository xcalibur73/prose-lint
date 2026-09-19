"""ProseLint: Deterministic Editorial Compiler and Quality Gate.

Audits prose for AI lexical markers, cadence burstiness, GEO citability,
WordPress Gutenberg block formatting, and multi-channel content repurposing.
"""

from .analyzer import ProseAnalyzer, ProseMetrics
from .geo_scorer import GEOScorer, GEOResult
from .gutenberg import markdown_to_gutenberg
from .repurposer import ContentRepurposer, RepurposedBundle
from .rules import RuleEngine, Finding

__version__ = "1.0.0"
__all__ = [
    "ProseAnalyzer",
    "ProseMetrics",
    "GEOScorer",
    "GEOResult",
    "markdown_to_gutenberg",
    "ContentRepurposer",
    "RepurposedBundle",
    "RuleEngine",
    "Finding",
    "__version__",
]
