# Changelog

All notable changes to the ProseLint project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.1] - 2026-09-24
 
### Fixed
- Fixed false positive in bold-first bullet detection: exempted standard technical documentation lead labels and steps (`Note:`, `Warning:`, `Caution:`, `Important:`, `Tip:`, `Step \d+:`, `Example:`, `Prerequisite:`).

### Added
- Linked documentation and quickstart instructions to the interactive web tool on [webaudits.pro/tools/prose-lint](https://webaudits.pro/tools/prose-lint).

## [1.2.0] - 2026-09-20
 
### Added
- W3C WCAG 2.2 Technique H42/H69 alignment for document title outline integrity:
  - Detected duplicate `H1` headings in `rules.py` with line attribution to prevent topic dilution.
  - Updated `normalize_headings()` in `gutenberg.py` to automatically demote secondary `H1` headings into `H2`.

## [1.1.0] - 2026-09-20

### Added
- Semantic heading hierarchy validation in `rules.py` inspired by `jina-ai/reader`:
  - Detection of skipped heading depths (e.g. H1 directly jumping to H3) violating WCAG accessibility and search outline integrity.
- Automated heading normalization engine in `gutenberg.py`:
  - `normalize_headings()` function smoothing out heading level gaps while preserving title contents.
  - `--normalize-headings` CLI flag to optionally smooth heading hierarchy during Gutenberg transpilation or text repair.

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
