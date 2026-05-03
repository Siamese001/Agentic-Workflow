"""apps_rfp.engines.judges.win_theme_alignment_judge — PROMOTED (v2 deterministic).

Plan: ``.windsurf/plans/apps-eval-harness-terminal-3c9f81.md`` W3.P1.

PROMOTION HISTORY
=================
- v1 (stub): returned GRADER_UNKNOWN_SENTINEL always.
- **v2 (this plan)**: deterministic heuristic scoring RFP response
  alignment against declared win themes. Reads
  ``run_context["rfp_context"]["win_themes"]`` (list[str]) and scores
  response text on theme coverage + emphasis + distribution.

Scoring model (v2)
------------------
1. **Theme coverage** — fraction of declared win themes that appear at
   least once in the response. Weighted 0.40.
2. **Theme emphasis** — average occurrence count per covered theme
   (saturates at 3 mentions per theme). Weighted 0.30.
3. **Distribution** — penalizes themes clustered in a single paragraph
   vs distributed across the response. Weighted 0.20.
4. **Response length adequacy** — 1.0 for 300–5000 chars typical of
   RFP responses; penalized outside. Weighted 0.10.

Returns UNKNOWN when output text OR win_themes list is missing.
"""

from __future__ import annotations

import re
from typing import Any, Mapping

from agentic_core.L3_orchestration.exit_eval.v6.app_grader_registry import (
    GRADER_UNKNOWN_SENTINEL,
)

IS_STUB: bool = False
GRADER_ID: str = "rfp::win_theme_alignment_judge::v2"


def _extract_text(ctx: Mapping[str, Any]) -> str:
    out = ctx.get("output") if isinstance(ctx, Mapping) else None
    if isinstance(out, Mapping):
        for key in ("text", "response", "content", "answer"):
            v = out.get(key)
            if isinstance(v, str) and v.strip():
                return v
    return ""


def _extract_themes(ctx: Mapping[str, Any]) -> list[str]:
    rfp_ctx = ctx.get("rfp_context") if isinstance(ctx, Mapping) else None
    if isinstance(rfp_ctx, Mapping):
        themes = rfp_ctx.get("win_themes") or []
        if isinstance(themes, (list, tuple)):
            return [str(t).strip() for t in themes if str(t).strip()]
    return []


def _count_theme(text: str, theme: str) -> int:
    if not theme:
        return 0
    return len(re.findall(re.escape(theme), text, flags=re.IGNORECASE))


def _score_coverage(text: str, themes: list[str]) -> float:
    if not themes:
        return 0.0
    covered = sum(1 for t in themes if _count_theme(text, t) > 0)
    return covered / len(themes)


def _score_emphasis(text: str, themes: list[str]) -> float:
    if not themes:
        return 0.0
    counts = [_count_theme(text, t) for t in themes]
    covered_counts = [c for c in counts if c > 0]
    if not covered_counts:
        return 0.0
    avg = sum(covered_counts) / len(covered_counts)
    return min(1.0, avg / 3.0)


def _score_distribution(text: str, themes: list[str]) -> float:
    if not themes:
        return 0.0
    paragraphs = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    if len(paragraphs) <= 1:
        return 0.5
    theme_paragraph_hits = 0
    for theme in themes:
        hit_paragraphs = sum(1 for p in paragraphs if _count_theme(p, theme) > 0)
        if hit_paragraphs >= 2:
            theme_paragraph_hits += 1
    # Fraction of themes that appear in multiple paragraphs.
    return min(1.0, theme_paragraph_hits / max(1, len(themes) // 2))


def _score_length(text: str) -> float:
    n = len(text)
    if 300 <= n <= 5000:
        return 1.0
    if n < 300:
        return max(0.0, n / 300.0)
    return max(0.3, 1.0 - (n - 5000) / 10000.0)


def _compute_score(text: str, themes: list[str]) -> float:
    return (
        0.40 * _score_coverage(text, themes)
        + 0.30 * _score_emphasis(text, themes)
        + 0.20 * _score_distribution(text, themes)
        + 0.10 * _score_length(text)
    )


class WinThemeAlignmentJudge:
    is_stub: bool = False
    grader_id: str = GRADER_ID

    def grade(self, dim: Any, run_context: dict[str, Any]) -> tuple[Any, list[str]]:
        ctx = run_context or {}
        text = _extract_text(ctx)
        themes = _extract_themes(ctx)
        if not text or not themes:
            return GRADER_UNKNOWN_SENTINEL, []
        score = max(0.0, min(1.0, _compute_score(text, themes)))
        refs = [
            f"win_theme::v2::coverage={_score_coverage(text, themes):.2f}",
            f"win_theme::v2::emphasis={_score_emphasis(text, themes):.2f}",
            f"win_theme::v2::distribution={_score_distribution(text, themes):.2f}",
            f"win_theme::v2::length={_score_length(text):.2f}",
            f"win_theme::v2::themes_declared={len(themes)}",
        ]
        return score, refs


def grade(dim: Any, run_context: dict[str, Any]) -> tuple[Any, list[str]]:
    return WinThemeAlignmentJudge().grade(dim, run_context)


__all__ = ["WinThemeAlignmentJudge", "grade", "IS_STUB", "GRADER_ID"]
