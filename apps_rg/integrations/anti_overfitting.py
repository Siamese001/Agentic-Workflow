"""Anti-overfitting hard-gate primitives.

Three primitives matching the rubric in apps_eval/config/rubrics/narrative_judge.yaml:
  - mirror_density: combined JD+company term token-density bounds
  - buzzword_soup: cap on configured buzzwords per bullet
  - adjacent_repetition: no two consecutive bullets in the same role lead with the same mirror term
  - filler_intensifiers: forbidden words/phrases reject the candidate

Plan: .windsurf/plans/apps-rg-narrative-and-company-research-e3f8c1.md (P3.3).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable, List, Optional, Sequence, Set

DEFAULT_BUZZWORDS: Sequence[str] = (
    "AI",
    "transformation",
    "agentic",
    "enterprise",
    "Fortune",
    "strategic",
    "C-suite",
    "cloud",
    "digital",
    "innovation",
)
DEFAULT_FILLER: Sequence[str] = (
    "leading",
    "world-class",
    "cutting-edge",
    "mission-critical",
    "next-generation",
    "best-in-class",
    "leverage",
    "synergy",
    "enabled",
    "unified",
    "robust",
    "comprehensive",
    "holistic",
)


@dataclass
class GateResult:
    gate_id: str
    passed: bool
    detail: str = ""

    def as_dict(self) -> dict:
        return {"gate_id": self.gate_id, "passed": self.passed, "detail": self.detail}


@dataclass
class AntiOverfittingConfig:
    buzzwords: Sequence[str] = field(default_factory=lambda: list(DEFAULT_BUZZWORDS))
    max_buzzwords: int = 3
    filler: Sequence[str] = field(default_factory=lambda: list(DEFAULT_FILLER))
    mirror_min: float = 0.08
    mirror_max: float = 0.22
    # Length-aware calibration (2026-05-01) ΓÇö short texts can't realistically
    # hit a fixed 0.08 density without keyword stuffing; long texts should
    # still clear a meaningful floor. When `adaptive_mirror=True`, mirror_min
    # scales with word count:
    #   n <  30 words  -> floor = 0.04  (single mirror term usually qualifies)
    #   n <  80 words  -> floor = 0.06
    #   n >= 80 words  -> floor = mirror_min (0.08)
    # mirror_max always applies as-is ΓÇö the anti-overfit ceiling doesn't need
    # length scaling because stuffing is equally bad at any length.
    adaptive_mirror: bool = True
    # Per-section buzzword overrides ΓÇö keyed by section_id to let exec_summary
    # tolerate more buzzwords than a single bullet. When unset for a section,
    # max_buzzwords applies. Empty-string key is the global default.
    max_buzzwords_by_section: dict = field(
        default_factory=lambda: {
            "hop_4a_headline": 2,
            "hop_4b_exec_summary": 5,
            "hop_4c_competencies": 4,
        }
    )


def _word_re(term: str) -> re.Pattern:
    # Word-boundary, case-insensitive, supports hyphenated phrases.
    escaped = re.escape(term.strip())
    return re.compile(rf"(?<![\w-]){escaped}(?![\w-])", re.IGNORECASE)


def count_buzzwords(text: str, buzzwords: Iterable[str] = DEFAULT_BUZZWORDS) -> int:
    if not text:
        return 0
    total = 0
    for term in buzzwords:
        total += len(_word_re(term).findall(text))
    return total


def filler_hits(text: str, filler: Iterable[str] = DEFAULT_FILLER) -> List[str]:
    hits: List[str] = []
    for term in filler:
        if _word_re(term).search(text or ""):
            hits.append(term)
    return hits


def mirror_density(text: str, mirror_terms: Iterable[str]) -> float:
    text = text or ""
    if not text.strip():
        return 0.0
    tokens = re.findall(r"[\w-]+", text.lower())
    n = max(1, len(tokens))
    matched = 0
    for term in mirror_terms:
        for m in _word_re(term).findall(text):
            matched += len(re.findall(r"[\w-]+", m.lower()))
    return min(1.0, matched / n)


def gate_buzzword_soup(
    text: str,
    cfg: AntiOverfittingConfig,
    *,
    section_id: str = "",
) -> GateResult:
    """Pass if buzzword count is under the per-section cap (or global fallback)."""
    n = count_buzzwords(text, cfg.buzzwords)
    cap = cfg.max_buzzwords_by_section.get(section_id, cfg.max_buzzwords)
    if n > cap:
        return GateResult(
            "buzzword_soup",
            False,
            f"buzzword_count={n} > max={cap} (section={section_id or 'default'})",
        )
    return GateResult("buzzword_soup", True, f"buzzword_count={n} (cap={cap})")


def gate_filler_intensifiers(text: str, cfg: AntiOverfittingConfig) -> GateResult:
    hits = filler_hits(text, cfg.filler)
    if hits:
        return GateResult("filler_intensifiers", False, f"hits={hits}")
    return GateResult("filler_intensifiers", True, "no filler detected")


def _adaptive_min(text: str, cfg: AntiOverfittingConfig) -> float:
    if not cfg.adaptive_mirror:
        return cfg.mirror_min
    n = len(re.findall(r"[\w-]+", text or ""))
    if n < 30:
        return min(0.04, cfg.mirror_min)
    if n < 80:
        return min(0.06, cfg.mirror_min)
    return cfg.mirror_min


def gate_mirror_density(
    text: str, mirror_terms: Iterable[str], cfg: AntiOverfittingConfig
) -> GateResult:
    d = mirror_density(text, mirror_terms)
    effective_min = _adaptive_min(text, cfg)
    if d < effective_min:
        return GateResult(
            "mirror_density",
            False,
            f"density={d:.4f} < min={effective_min:.4f} (adaptive={cfg.adaptive_mirror})",
        )
    if d > cfg.mirror_max:
        return GateResult(
            "mirror_density",
            False,
            f"density={d:.4f} > max={cfg.mirror_max}",
        )
    return GateResult("mirror_density", True, f"density={d:.4f} (min={effective_min:.4f})")


def gate_adjacent_repetition(
    bullets: Sequence[str],
    mirror_terms: Iterable[str],
) -> GateResult:
    """Detect consecutive bullets that share their leading mirror term."""
    mirror_list = [t for t in mirror_terms if t]
    last_lead: Optional[str] = None
    for i, text in enumerate(bullets):
        lead = _leading_mirror(text, mirror_list)
        if lead and last_lead and lead.lower() == last_lead.lower():
            return GateResult(
                "adjacent_repetition",
                False,
                f"bullet_{i} and bullet_{i - 1} both lead with '{lead}'",
            )
        last_lead = lead
    return GateResult("adjacent_repetition", True, "no adjacent leading-term repeats")


def _leading_mirror(text: str, mirror_terms: Sequence[str]) -> Optional[str]:
    if not text:
        return None
    head = text.strip().split()[:3]
    head_blob = " ".join(head)
    for term in mirror_terms:
        if _word_re(term).search(head_blob):
            return term
    return None


def evaluate_text(
    text: str,
    *,
    mirror_terms: Iterable[str],
    cfg: Optional[AntiOverfittingConfig] = None,
) -> List[GateResult]:
    cfg = cfg or AntiOverfittingConfig()
    return [
        gate_buzzword_soup(text, cfg),
        gate_filler_intensifiers(text, cfg),
        gate_mirror_density(text, mirror_terms, cfg),
    ]


__all__ = [
    "AntiOverfittingConfig",
    "DEFAULT_BUZZWORDS",
    "DEFAULT_FILLER",
    "GateResult",
    "count_buzzwords",
    "evaluate_text",
    "filler_hits",
    "gate_adjacent_repetition",
    "gate_buzzword_soup",
    "gate_filler_intensifiers",
    "gate_mirror_density",
    "mirror_density",
]
