"""Command-line interface for ProseLint."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rich.console import Console

from . import __version__
from .analyzer import ProseAnalyzer
from .geo_scorer import GEOScorer
from .gutenberg import markdown_to_gutenberg, normalize_headings
from .repurposer import ContentRepurposer
from .report_generator import ReportGenerator
from .rules import RuleEngine


def build_parser() -> argparse.ArgumentParser:
    """Builds the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="prose-lint",
        description="ProseLint: Deterministic Editorial Compiler and Quality Gate",
        epilog="Examples:\n  prose-lint article.md\n  prose-lint article.md --output json --save report.json\n  prose-lint article.md --output gutenberg --save post.html\n  prose-lint article.md --repurpose",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "file",
        nargs="?",
        type=str,
        help="Path to Markdown or text file to audit.",
    )
    parser.add_argument(
        "--output",
        "-o",
        choices=["terminal", "json", "markdown", "gutenberg"],
        default="terminal",
        help="Report or transpilation output format (default: terminal).",
    )
    parser.add_argument(
        "--repurpose",
        action="store_true",
        help="Transpile draft into video prompts, ElevenLabs script, Pinterest pins, and llms.txt snippet.",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=65.0,
        help="Minimum GEO citability score required to pass (default: 65.0).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors and exit with non-zero status if any warning is flagged.",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically apply deterministic fixes (replace em-dashes, clean bold-first bullets).",
    )
    parser.add_argument(
        "--normalize-headings",
        action="store_true",
        help="Automatically normalize skipped heading levels (e.g. H1 to H3 -> H2) during processing.",
    )
    parser.add_argument(
        "--save",
        type=str,
        help="File path to save output report or transpiled content.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"prose-lint {__version__}",
        help="Show program's version number and exit.",
    )
    return parser


def apply_fixes(text: str) -> str:
    """Applies deterministic text fixes to eliminate simple invariant violations."""
    # Replace em-dashes and en-dashes
    cleaned = text.replace("\u2014", " - ").replace("\u2013", "-")
    # Clean up double spaces
    import re
    cleaned = re.sub(r" +", " ", cleaned)
    # Convert bold-first list leads (- **Topic**: text -> - Topic: text)
    cleaned = re.sub(r"^(\s*[-*]\s+)\*\*([^*]+)\*\*:\s*", r"\1\2: ", cleaned, flags=re.MULTILINE)
    return cleaned


def main(argv: list[str] | None = None) -> int:
    """Main CLI entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.file:
        parser.print_help()
        return 0

    path = Path(args.file)
    if not path.is_file():
        Console(stderr=True).print(f"[bold red]Error:[/bold red] Target file not found: {args.file}")
        return 2

    try:
        content = path.read_text(encoding="utf-8")
    except Exception as err:
        Console(stderr=True).print(f"[bold red]Error:[/bold red] Failed to read file: {err}")
        return 2

    if args.fix:
        content = apply_fixes(content)
        if args.normalize_headings:
            content = normalize_headings(content)
        if args.save:
            Path(args.save).write_text(content, encoding="utf-8")
            Console().print(f"[bold green]Success:[/bold green] Applied deterministic fixes and saved to {args.save}")
        else:
            path.write_text(content, encoding="utf-8")
            Console().print(f"[bold green]Success:[/bold green] Applied deterministic fixes in-place to {args.file}")

    # Output format: Gutenberg transpilation
    if args.output == "gutenberg":
        gutenberg_markup = markdown_to_gutenberg(content, normalize_heading_hierarchy=args.normalize_headings)
        if args.save:
            Path(args.save).write_text(gutenberg_markup, encoding="utf-8")
            Console().print(f"[bold green]Success:[/bold green] Saved Gutenberg block markup to {args.save}")
        else:
            print(gutenberg_markup)
        return 0

    # Execute full analysis suite
    rule_engine = RuleEngine()
    analyzer = ProseAnalyzer()
    geo_scorer = GEOScorer()

    findings = rule_engine.scan(content)
    metrics = analyzer.analyze(content)
    geo_result = geo_scorer.evaluate(content)

    bundle = None
    if args.repurpose:
        repurposer = ContentRepurposer()
        bundle = repurposer.transpile(content)

    report_gen = ReportGenerator()

    if args.output == "json":
        json_output = report_gen.to_json(str(path), findings, metrics, geo_result, bundle)
        if args.save:
            Path(args.save).write_text(json_output, encoding="utf-8")
            Console().print(f"[bold green]Saved JSON report to {args.save}[/bold green]")
        else:
            print(json_output)
    elif args.output == "terminal":
        report_gen.render_terminal(str(path), findings, metrics, geo_result, bundle)
        if args.save:
            # Also save JSON if save flag specified in terminal mode
            json_output = report_gen.to_json(str(path), findings, metrics, geo_result, bundle)
            Path(args.save).write_text(json_output, encoding="utf-8")
            Console().print(f"[bold green]Saved report to {args.save}[/bold green]")
    elif args.output == "markdown":
        json_dict = report_gen.to_dict(str(path), findings, metrics, geo_result, bundle)
        md_lines = [
            f"# ProseLint Audit: {path.name}\n",
            f"- Words: {metrics.total_words}",
            f"- Burstiness Score: {metrics.burstiness_score} ({metrics.cadence_verdict})",
            f"- GEO Citability: Grade {geo_result.grade} ({geo_result.geo_readiness_score}/100)",
            f"- Violations: {len(findings)}\n",
            "## Rule Violations\n",
        ]
        for f in findings:
            md_lines.append(f"- Line {f.line_number} [{f.severity.upper()}]: {f.message} (Suggestion: {f.suggestion})")
        md_content = "\n".join(md_lines)
        if args.save:
            Path(args.save).write_text(md_content, encoding="utf-8")
            Console().print(f"[bold green]Saved Markdown report to {args.save}[/bold green]")
        else:
            print(md_content)

    # Exit code determination
    error_count = sum(1 for f in findings if f.severity == "error")
    warning_count = sum(1 for f in findings if f.severity == "warning")

    if error_count > 0:
        return 1
    if args.strict and warning_count > 0:
        return 1
    if geo_result.geo_readiness_score < args.threshold:
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
