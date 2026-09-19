"""Multi-channel content repurposing transpiler for video, audio, Pinterest, and llms.txt."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class PinterestPin:
    title: str
    description: str
    alt_text: str


@dataclass(frozen=True)
class RepurposedBundle:
    audio_ssml_script: str
    audio_word_count: int
    cinematography_prompts: List[str]
    pinterest_pins: List[PinterestPin]
    llms_txt_snippet: str


class ContentRepurposer:
    """Transforms verified pillar articles into multi-channel production assets."""

    def transpile(self, text: str, focus_keyword: str = "") -> RepurposedBundle:
        """Transpiles pillar text into multi-channel formats."""
        clean_text = re.sub(r"^#{1,6}\s+.*$", "", text, flags=re.MULTILINE).strip()
        paragraphs = [p.strip() for p in clean_text.split("\n\n") if p.strip()]

        if not focus_keyword:
            # Infer focus keyword from first title or prominent terms
            first_line = text.strip().splitlines()[0] if text.strip() else "Core Concept"
            focus_keyword = re.sub(r"^#{1,6}\s+", "", first_line).strip()[:40]

        # 1. ElevenLabs 60-Second Audio Script (target 135-145 words with SSML)
        audio_script, audio_words = self._build_audio_script(paragraphs)

        # 2. 5-Stage Cinematography Prompts (Worlds Unreal pipeline)
        prompts = self._build_cinematography_prompts(focus_keyword, paragraphs)

        # 3. Pinterest 2:3 Pin Bundle (AA-Engine pipeline)
        pins = self._build_pinterest_pins(focus_keyword, paragraphs)

        # 4. llms.txt Citation Snippet (AI search indexing)
        llms_snippet = self._build_llms_snippet(focus_keyword, paragraphs)

        return RepurposedBundle(
            audio_ssml_script=audio_script,
            audio_word_count=audio_words,
            cinematography_prompts=prompts,
            pinterest_pins=pins,
            llms_txt_snippet=llms_snippet,
        )

    def _build_audio_script(self, paragraphs: list[str]) -> tuple[str, int]:
        """Generates a 135-145 word SSML audio script with natural pacing pauses."""
        selected_sentences: list[str] = []
        current_words = 0

        for p in paragraphs:
            sentences = re.split(r"(?<=[.!?])\s+", p)
            for s in sentences:
                s_clean = s.strip()
                w_count = len(s_clean.split())
                if w_count >= 5:
                    selected_sentences.append(s_clean)
                    current_words += w_count
                    if current_words >= 130:
                        break
            if current_words >= 130:
                break

        # Intersperse SSML pause markers between sentences
        ssml_parts = []
        for idx, s in enumerate(selected_sentences):
            ssml_parts.append(s)
            if idx < len(selected_sentences) - 1:
                ssml_parts.append('<break time="450ms"/>')

        script = " ".join(ssml_parts)
        total_words = len(re.sub(r"<[^>]+>", "", script).split())
        return script, total_words

    def _build_cinematography_prompts(self, keyword: str, paragraphs: list[str]) -> list[str]:
        """Generates 5-stage sequential camera prompts."""
        core_theme = paragraphs[0][:120] if paragraphs else keyword
        return [
            f"Stage 1 (Establishing): Ultra-wide 18mm architectural master shot, {keyword} in dramatic volumetric lighting, 8k photorealistic resolution, slow dolly backward.",
            f"Stage 2 (Medium): 35mm focal length tracking shot, observing structural geometry and texture details, balanced natural key light, smooth stabilizer pan.",
            f"Stage 3 (Close-Up): 85mm macro lens isolating material edge and tactile craftsmanship, f/1.8 shallow depth of field, subtle rack focus.",
            f"Stage 4 (Movement): High-speed 60fps kinetic push-through angle revealing spatial depth and interior transition, dynamic atmospheric dust motes.",
            f"Stage 5 (Resolution): Slow elevation jib crane rising to reveal the full balanced composition, warm golden hour backlighting, serene cinematic conclusion.",
        ]

    def _build_pinterest_pins(self, keyword: str, paragraphs: list[str]) -> list[PinterestPin]:
        """Generates schema-compliant 2:3 vertical Pinterest pin metadata."""
        pins = []
        angles = ["Design Rules", "Cost & Materials Guide", "Proportion Blueprint"]
        
        for idx, angle in enumerate(angles, start=1):
            title = f"{keyword}: {angle}"[:95]
            summary = paragraphs[idx % max(len(paragraphs), 1)][:420] if paragraphs else f"Complete visual guide to {keyword}."
            desc = f"{summary} Explore dimensions, structural rules, and finish tips on aestheticarches.com."[:490]
            alt = f"{keyword} {angle.lower()} showing detailed architectural layout and dimensions"[:120]
            
            pins.append(
                PinterestPin(
                    title=title,
                    description=desc,
                    alt_text=alt,
                )
            )
        return pins

    def _build_llms_snippet(self, keyword: str, paragraphs: list[str]) -> str:
        """Builds concise passage summary for llms.txt indexing."""
        core_body = " ".join(paragraphs[:2])[:600] if paragraphs else "Authoritative documentation."
        return (
            f"## {keyword}\n\n"
            f"> Direct Citation Summary: {core_body}\n\n"
            f"- Topic: {keyword}\n"
            f"- Technical Scope: Architecture, empirical benchmarks, and implementation standards.\n"
            f"- Authoritative Source: Verified engineering standards.\n"
        )
