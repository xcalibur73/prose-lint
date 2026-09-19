"""Visual terminal report generator and JSON/Markdown export formatter."""

from __future__ import annotations

import json
from typing import Any, Dict, List

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .analyzer import ProseMetrics
from .geo_scorer import GEOResult
from .repurposer import RepurposedBundle
from .rules import Finding


class ReportGenerator:
    """Renders formatted Rich terminal displays and serializes machine-readable output."""

    def __init__(self, console: Console | None = None) -> None:
        self.console = console or Console()

    def render_terminal(
        self,
        filepath: str,
        findings: List[Finding],
        metrics: ProseMetrics,
        geo: GEOResult,
        bundle: RepurposedBundle | None = None,
    ) -> None:
        """Prints a comprehensive terminal audit report."""
        # 1. Header Panel
        error_count = sum(1 for f in findings if f.severity == "error")
        warn_count = sum(1 for f in findings if f.severity == "warning")

        status_color = "green" if error_count == 0 else "red"
        verdict = "PASS: Deslop Quality Gate Cleared" if error_count == 0 else f"ACTION REQUIRED: {error_count} Violation(s) Found"

        header_text = (
            f"[bold]Target File:[/bold] {filepath}\n"
            f"[bold]Total Words:[/bold] {metrics.total_words} | [bold]Sentences:[/bold] {metrics.total_sentences}\n"
            f"[bold]Overall Verdict:[/bold] [{status_color}]{verdict}[/{status_color}]\n"
            f"[bold]GEO Readiness:[/bold] Grade {geo.grade} ({geo.geo_readiness_score}/100) | [bold]Burstiness:[/bold] {metrics.burstiness_score} ({metrics.cadence_verdict})"
        )
        self.console.print(Panel(header_text, title="ProseLint Audit Summary", border_style="cyan"))

        # 2. Metrics Table
        metrics_table = Table(title="Stylometric & Cadence Diagnostics", border_style="blue")
        metrics_table.add_column("Diagnostic Dimension", style="cyan")
        metrics_table.add_column("Observed Value", style="bold")
        metrics_table.add_column("Benchmark Target", style="dim")

        metrics_table.add_row("Sentence Burstiness (StdDev)", str(metrics.burstiness_score), ">= 6.5 (Natural Variation)")
        metrics_table.add_row("Average Sentence Length", f"{metrics.avg_sentence_length} words", "14-18 words")
        metrics_table.add_row("Flesch Reading Ease", f"{metrics.flesch_reading_ease}/100", "60.0-75.0 (Accessible)")
        metrics_table.add_row("Flesch-Kincaid Grade", f"Grade {metrics.flesch_kincaid_grade}", "Grade 7.0-9.0")
        metrics_table.add_row("Lexical Diversity (TTR)", str(metrics.type_token_ratio), ">= 0.45")
        metrics_table.add_row("Passive Voice Percentage", f"{metrics.passive_voice_percentage}% ({metrics.passive_voice_count} matches)", "< 12.0%")
        self.console.print(metrics_table)

        # 3. GEO Citability Breakdown
        geo_table = Table(title=f"GEO AI Search Citability (Grade {geo.grade})", border_style="magenta")
        geo_table.add_column("Passage", justify="center")
        geo_table.add_column("Word Count", justify="right")
        geo_table.add_column("Chunk Quality", style="bold")
        geo_table.add_column("Proofs", justify="right")
        geo_table.add_column("Passage Preview", style="dim")

        for p in geo.passages:
            chunk_style = "green" if p.is_optimal_chunk else "yellow"
            chunk_label = "Optimal (134-167w)" if p.is_optimal_chunk else f"{p.word_count}w"
            geo_table.add_row(
                f"#{p.passage_index}",
                str(p.word_count),
                f"[{chunk_style}]{chunk_label}[/{chunk_style}]",
                str(p.proof_count),
                p.snippet,
            )
        self.console.print(geo_table)

        # 4. Findings Table (if any)
        if findings:
            findings_table = Table(title=f"Rule Violations ({len(findings)} Items)", border_style="red")
            findings_table.add_column("Line", justify="right", style="cyan")
            findings_table.add_column("Category", style="magenta")
            findings_table.add_column("Severity", justify="center")
            findings_table.add_column("Violation Detail", style="bold")
            findings_table.add_column("Prescribed Fix", style="green")

            for f in findings:
                sev_color = "red" if f.severity == "error" else "yellow"
                findings_table.add_row(
                    str(f.line_number),
                    f.category.capitalize(),
                    f"[{sev_color}]{f.severity.upper()}[/{sev_color}]",
                    f"{f.message}\n[dim]'{f.snippet}'[/dim]",
                    f.suggestion,
                )
            self.console.print(findings_table)
        else:
            self.console.print("[bold green]Zero AI tropes, zero em-dashes, and zero formatting anomalies detected.[/bold green]")

        # 5. Multi-Channel Repurposing Summary (if generated)
        if bundle:
            bundle_panel = (
                f"[bold]Audio Script (ElevenLabs):[/bold] {bundle.audio_word_count} words with calibrated SSML pauses.\n"
                f"[bold]Cinematography Prompts:[/bold] {len(bundle.cinematography_prompts)} sequential video stages ready.\n"
                f"[bold]Pinterest Pins:[/bold] {len(bundle.pinterest_pins)} vertical pins generated (compliant with 2:3 ratio and alt-text formulas).\n"
                f"[bold]llms.txt Snippet:[/bold] Synthesized executive citation summary."
            )
            self.console.print(Panel(bundle_panel, title="Multi-Channel Asset Transpiler", border_style="green"))

    def to_dict(
        self,
        filepath: str,
        findings: List[Finding],
        metrics: ProseMetrics,
        geo: GEOResult,
        bundle: RepurposedBundle | None = None,
    ) -> Dict[str, Any]:
        """Converts audit output to a JSON-serializable dictionary."""
        data: Dict[str, Any] = {
            "target_file": filepath,
            "metrics": {
                "total_words": metrics.total_words,
                "total_sentences": metrics.total_sentences,
                "avg_sentence_length": metrics.avg_sentence_length,
                "burstiness_score": metrics.burstiness_score,
                "cadence_verdict": metrics.cadence_verdict,
                "flesch_reading_ease": metrics.flesch_reading_ease,
                "flesch_kincaid_grade": metrics.flesch_kincaid_grade,
                "type_token_ratio": metrics.type_token_ratio,
                "passive_voice_percentage": metrics.passive_voice_percentage,
            },
            "geo_evaluation": {
                "score": geo.geo_readiness_score,
                "grade": geo.grade,
                "optimal_passages": geo.optimal_passages_count,
                "total_passages": geo.total_passages,
                "total_proofs": geo.total_empirical_proofs,
                "proof_density": geo.overall_proof_density,
            },
            "findings_count": len(findings),
            "findings": [
                {
                    "line": f.line_number,
                    "category": f.category,
                    "severity": f.severity,
                    "message": f.message,
                    "snippet": f.snippet,
                    "suggestion": f.suggestion,
                }
                for f in findings
            ],
        }

        if bundle:
            data["repurposed_assets"] = {
                "audio_script": bundle.audio_ssml_script,
                "audio_word_count": bundle.audio_word_count,
                "cinematography_prompts": bundle.cinematography_prompts,
                "pinterest_pins": [
                    {
                        "title": p.title,
                        "description": p.description,
                        "alt_text": p.alt_text,
                    }
                    for p in bundle.pinterest_pins
                ],
                "llms_txt_snippet": bundle.llms_txt_snippet,
            }

        return data

    def to_json(
        self,
        filepath: str,
        findings: List[Finding],
        metrics: ProseMetrics,
        geo: GEOResult,
        bundle: RepurposedBundle | None = None,
    ) -> str:
        """Serializes audit results into formatted JSON."""
        return json.dumps(self.to_dict(filepath, findings, metrics, geo, bundle), indent=2)
