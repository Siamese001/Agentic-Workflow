"""apps_lic.engines.judges.brand_voice_judge — PROMOTED (v2 deterministic).

Plan: ``.windsurf/plans/apps-eval-harness-terminal-3c9f81.md`` W2.P1.

PROMOTION HISTORY
=================
- v1 (stub): returned GRADER_UNKNOWN_SENTINEL always.
- **v2 (this plan)**: deterministic heuristic scoring tone/style match
  against an optional ``run_context["brand_voice_profile"]`` (dict with
  ``preferred_lexicon`` list, ``forbidden_lexicon`` list, ``register``
  string of {formal,casual,neutral}). When profile absent, scores on
  a default professional-register heuristic.

Scoring model (v2)
------------------
1. **Preferred lexicon coverage** — fraction of ``preferred_lexicon``
   terms appearing. Weighted 0.30.
2. **Forbidden lexicon cleanliness** — 1.0 iff none of
   ``forbidden_lexicon`` appear; linear penalty per hit. Weighted 0.30.
3. **Register match** — measures formal/casual register via
   contraction + slang density; compares against profile register.
   Weighted 0.25.
4. **Sentence-length variance** — healthy variance scores higher;
   monotone text penalized. Weighted 0.15.
"""

from __future__ import annotations

import re
import statistics
from typing import Any, Mapping

from agentic_core.L3_orchestration.exit_eval.v6.app_grader_registry import (
    GRADER_UNKNOWN_SENTINEL,
)

IS_STUB: bool = False
GRADER_ID: str = "lic::brand_voice_judge::v2"

_CONTRACTION_RE = re.compile(r"\b\w+'\w+\b")
_SLANG_TOKENS: frozenset[str] = frozenset(
    {"gonna", "wanna", "lol", "btw", "fyi", "yeah", "gotta", "kinda"}
)
_FORMAL_HINTS: frozenset[str] = frozenset(
    {"regards", "sincerely", "accordingly", "furthermore", "respectfully"}
)
_WORD = re.compile(r"\b[a-zA-Z]+\b")
_SENTENCE_SPLIT = re.compile(r"[.!?]+\s+")


def _extract_text(ctx: Mapping[str, Any]) -> str:
    out = ctx.get("output") if isinstance(ctx, Mapping) else None
    if isinstance(out, Mapping):
        for key in ("text", "response", "content", "message"):
            v = out.get(key)
            if isinstance(v, str) and v.strip():
                return v
    return ""


def _extract_profile(ctx: Mapping[str, Any]) -> Mapping[str, Any]:
    prof = ctx.get("brand_voice_profile") if isinstance(ctx, Mapping) else None
    return prof if isinstance(prof, Mapping) else {}


def _score_preferred_lexicon(text: str, profile: Mapping[str, Any]) -> float:
    preferred = profile.get("preferred_lexicon") or []
    if not preferred:
        return 0.8  # neutral-score when no profile
    words = {w.lower() for w in _WORD.findall(text)}
    hits = sum(1 for term in preferred if str(term).lower() in words)
    return min(1.0, hits / max(1, len(preferred) // 2))


def _score_forbidden_cleanliness(text: str, profile: Mapping[str, Any]) -> float:
    forbidden = profile.get("forbidden_lexicon") or []
    if not forbidden:
        return 1.0
    lower = text.lower()
    hits = sum(1 for term in forbidden if str(term).lower() in lower)
    return max(0.0, 1.0 - 0.25 * hits)


def _measure_register(text: str) -> str:
    contractions = len(_CONTRACTION_RE.findall(text))
    words = [w.lower() for w in _WORD.findall(text)]
    if not words:
        return "neutral"
    slang = sum(1 for w in words if w in _SLANG_TOKENS)
    formal = sum(1 for w in words if w in _FORMAL_HINTS)
    casual_score = (contractions + slang) / max(1, len(words))
    formal_score = formal / max(1, len(words))
    if formal_score > casual_score and formal_score > 0.01:
        return "formal"
    if casual_score > 0.03:
        return "casual"
    return "neutral"


def _score_register(text: str, profile: Mapping[str, Any]) -> float:
    target = str(profile.get("register", "")).lower() or "neutral"
    observed = _measure_register(text)
    if observed == target:
        return 1.0
    if "neutral" in (observed, target):
        return 0.7
    return 0.3  # formal vs casual mismatch


def _score_length_variance(text: str) -> float:
    parts = [p.strip() for p in _SENTENCE_SPLIT.split(text) if p.strip()]
    if len(parts) < 2:
        return 0.5
    lens = [len(p) for p in parts]
    try:
        stdev = statistics.stdev(lens)
        mean = statistics.mean(lens) or 1
    except statistics.StatisticsError:
        return 0.5
    coeff = stdev / mean
    # Sweet spot coeff-var around 0.3–0.7.
    if 0.3 <= coeff <= 0.7:
        return 1.0
    if coeff < 0.3:
        return max(0.4, coeff / 0.3)
    return max(0.4, 1.0 - (coeff - 0.7) / 1.5)


def _compute_score(text: str, profile: Mapping[str, Any]) -> float:
    return (
        0.30 * _score_preferred_lexicon(text, profile)
        + 0.30 * _score_forbidden_cleanliness(text, profile)
        + 0.25 * _score_register(text, profile)
        + 0.15 * _score_length_variance(text)
    )


class BrandVoiceJudge:
    is_stub: bool = False
    grader_id: str = GRADER_ID

    def grade(self, dim: Any, run_context: dict[str, Any]) -> tuple[Any, list[str]]:
        ctx = run_context or {}
        text = _extract_text(ctx)
        if not text:
            return GRADER_UNKNOWN_SENTINEL, []
        profile = _extract_profile(ctx)
        score = max(0.0, min(1.0, _compute_score(text, profile)))
        refs = [
            f"brand_voice::v2::preferred_lexicon={_score_preferred_lexicon(text, profile):.2f}",
            f"brand_voice::v2::forbidden_clean={_score_forbidden_cleanliness(text, profile):.2f}",
            f"brand_voice::v2::register={_score_register(text, profile):.2f}",
            f"brand_voice::v2::length_variance={_score_length_variance(text):.2f}",
        ]
        return score, refs


def grade(dim: Any, run_context: dict[str, Any]) -> tuple[Any, list[str]]:
    return BrandVoiceJudge().grade(dim, run_context)


__all__ = ["BrandVoiceJudge", "grade", "IS_STUB", "GRADER_ID"]
