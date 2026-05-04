"""apps_lic.engines.judges.ask_friction_judge — deterministic heuristic (v1).

Plan: .windsurf/plans/apps-lic-deferred-scope-followup-d3f9b2.md W2 D1-P1
Exit rubric dim: ask_friction_score

Scores 0.0–1.0 where **lower is better** (lower friction = easier ask).
The rubric's fail_closed_when threshold is score > 0.5, so this judge
targets the complement: a high judge score means HIGH friction (bad).

Scoring model
-------------
Four friction signals weighted additively:

1. **Commitment demand** — verb phrases that demand high-commitment actions
   (e.g. "hire me", "offer me", "give me"). Weighted 0.35.
2. **Implicit assumption burden** — text that assumes the recipient has
   time/context without establishing it ("you must know", "as you can see",
   "obviously"). Weighted 0.25.
3. **Multi-ask count** — number of distinct asks/questions in the draft.
   Single ask = 0 friction; each additional ask adds friction. Weighted 0.20.
4. **Length friction for executive channel** — very long drafts impose
   reading friction on senior execs. Weighted 0.20.

Caller passes recipient_class via run_context to modulate the length
sensitivity. Missing run_context → conservative (non-exec) scoring.
"""

from __future__ import annotations

import re
from typing import Any, Mapping

from agentic_core.L3_orchestration.exit_eval.v6.app_grader_registry import (
    GRADER_UNKNOWN_SENTINEL,
)

IS_STUB: bool = False
IS_CALIBRATED: bool = True
GRADER_ID: str = "lic::ask_friction_judge::v1"

_COMMITMENT_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\b(hire me|offer me|give me|provide me|grant me|guarantee)\b", re.I),
    re.compile(r"\b(you (must|have to|need to|should) (call|meet|respond|reply|decide))\b", re.I),
    re.compile(r"\b(immediately|right away|today|urgent(ly)?)\b", re.I),
]

_ASSUMPTION_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\b(you must know|as you (can |well )?see|obviously|clearly you|everyone knows)\b", re.I),
    re.compile(r"\b(you('re| are) (already |well )?aware)\b", re.I),
    re.compile(r"\b(no doubt|of course|needless to say)\b", re.I),
]

_EXEC_CLASSES: frozenset[str] = frozenset({"EXECUTIVE", "C_LEVEL", "CTO", "VP_ENG"})


def _extract_text(ctx: Mapping[str, Any]) -> str:
    out = ctx.get("output") if isinstance(ctx, Mapping) else None
    if isinstance(out, Mapping):
        for key in ("text", "response", "content", "message"):
            v = out.get(key)
            if isinstance(v, str) and v.strip():
                return v
    return ""


def _score_commitment(text: str) -> float:
    hits = sum(1 for p in _COMMITMENT_PATTERNS if p.search(text))
    return min(1.0, hits / len(_COMMITMENT_PATTERNS))


def _score_assumption(text: str) -> float:
    hits = sum(1 for p in _ASSUMPTION_PATTERNS if p.search(text))
    return min(1.0, hits / max(1, len(_ASSUMPTION_PATTERNS)))


def _score_multi_ask(text: str) -> float:
    questions = text.count("?")
    ask_markers = len(re.findall(r"\b(please|kindly|could you|would you|can you)\b", text, re.I))
    total = max(questions, ask_markers)
    if total <= 1:
        return 0.0
    return min(1.0, (total - 1) * 0.25)


def _score_length_exec(text: str, is_exec: bool) -> float:
    if not is_exec:
        return 0.0
    n = len(text)
    if n <= 300:
        return 0.0
    if n <= 600:
        return (n - 300) / 300.0 * 0.5
    return min(1.0, 0.5 + (n - 600) / 800.0)


def _compute_score(text: str, is_exec: bool) -> float:
    return (
        0.35 * _score_commitment(text)
        + 0.25 * _score_assumption(text)
        + 0.20 * _score_multi_ask(text)
        + 0.20 * _score_length_exec(text, is_exec)
    )


class AskFrictionJudge:
    is_stub: bool = False
    grader_id: str = GRADER_ID

    def grade(self, dim: Any, run_context: dict[str, Any]) -> tuple[Any, list[str]]:
        ctx = run_context or {}
        text = _extract_text(ctx)
        if not text:
            return GRADER_UNKNOWN_SENTINEL, []
        recipient_class = str(ctx.get("recipient_class", "")).upper()
        is_exec = recipient_class in _EXEC_CLASSES
        score = max(0.0, min(1.0, _compute_score(text, is_exec)))
        refs = [
            f"ask_friction::v1::commitment={_score_commitment(text):.2f}",
            f"ask_friction::v1::assumption={_score_assumption(text):.2f}",
            f"ask_friction::v1::multi_ask={_score_multi_ask(text):.2f}",
            f"ask_friction::v1::length_exec={_score_length_exec(text, is_exec):.2f}",
            f"ask_friction::v1::is_exec={is_exec}",
        ]
        return score, refs


def grade(dim: Any, run_context: dict[str, Any]) -> tuple[Any, list[str]]:
    return AskFrictionJudge().grade(dim, run_context)


__all__ = ["AskFrictionJudge", "grade", "IS_STUB", "IS_CALIBRATED", "GRADER_ID"]
