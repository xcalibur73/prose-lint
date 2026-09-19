# Changelog

All notable changes to the ProseLint project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-09-19

### Added
- Initial release of ProseLint as the 10th showcase tool in the WebAudits ecosystem.
- Deterministic RuleEngine compiling over 200 regular expressions for AI vocabulary tropes, throat-clearing openers, signposted conclusions, and self-posed rhetorical questions.
- Invariant punctuation verification guaranteeing zero em-dashes and zero en-dashes across analyzed prose.
- ProseAnalyzer computing sentence burstiness (standard deviation of sentence length), Flesch-Kincaid grade level, and passive voice frequency.
- GEOScorer auditing passage citability against Princeton KDD 2024 benchmarks, measuring 134-167 word passage chunks, empirical proof density, and definition header triggers.
- WordPress Gutenberg transpiler (`markdown_to_gutenberg`) converting Markdown to block comments with KSES ampersand entity protection.
- Multi-channel ContentRepurposer generating 60-second ElevenLabs SSML scripts, 5-stage cinematography prompts, Pinterest 2:3 pin bundles, and llms.txt citation summaries.
- Rich terminal output generator with color-coded grades and JSON/Markdown export options.
