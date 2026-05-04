"""apps_lic.engines.judges.asymmetric_insight_judge — deterministic heuristic (v1).

Plan: .windsurf/plans/apps-lic-deferred-scope-followup-d3f9b2.md W2 D1-P5
Exit rubric dim: asymmetric_insight_present

Scores 0.0–1.0 where 1.0 = strong asymmetric insight detected.

Config-gate discipline
-----------------------
The exit rubric declares this dim as ``required_when: asymmetric_insight_required
== true in lic_plan_rules.yaml``. This judge mirrors that:

  - If ``run_context["asymmetric_insight_required"]`` is False (or absent):
    → return 1.0 (not required; skip gracefully)
  - If True: evaluate insight signal strength against the draft text.

Scoring model (when required)
------------------------------
Asymmetric insight = the sender knows something about the recipient's context
that the recipient has NOT publicly broadcast. Heuristic proxies:

1. **Specificity signal** — references to a specific project, initiative,
   recent announcement, or publication by name. Weighted 0.40.
2. **Counter-narrative signal** — draws a non-obvious connection
   ("most people focus on X, but your work on Y suggests…"). Weighted 0.30.
3. **Non-generic opener** — first sentence is NOT a generic role/title opener.
   Weighted 0.20.
4. **Outreach mode bypass** — if outreach_mode is "cold" for a non-exec
   recipient, insight is not expected; return 1.0 (bypass, same as not required).

All evaluated heuristically over draft text from ``run_context["output"]["text"]``.
"""

from __future__ import annotations

import re
from typing import Any

from agentic_core.L3_orchestration.exit_eval.v6.app_grader_registry import (
    GRADER_UNKNOWN_SENTINEL,
)

IS_STUB: bool = False
IS_CALIBRATED: bool = True
GRADER_ID: str = "lic::asymmetric_insight_judge::v1"

_EXEC_CLASSES: frozenset[str] = frozenset({"EXECUTIVE", "C_LEVEL", "CTO", "VP_ENG"})

_SPECIFICITY_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\b(your (recent|latest|new) (post|article|talk|presentation|announcement|project|initiative|work on))\b", re.I),
    re.compile(r"\b(I (noticed|saw|read|came across|heard about))\b", re.I),
    re.compile(r"\b(your (team|company|org|division|group) (recently|just|has been))\b", re.I),
    re.compile(r"\b(at [A-Z][a-z]+,? (you|your team))\b"),  # named-company specificity
]

_COUNTER_NARRATIVE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\b(most (people|companies|teams|engineers)|unlike (most|others|typical))\b", re.I),
    re.compile(r"\b(while (everyone|most) (is|are|focus(es)?|tends?))\b", re.I),
    re.compile(r"\b(non-?obvious|counter-?intuitive|surprising(ly)?|overlooked)\b", re.I),
]

_GENERIC_OPENER_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"^(hi|hello|dear|good (morning|afternoon|evening))[, ]+\w", re.I),
    re.compile(r"^I (am|'m) (reaching out|writing|contacting)", re.I),
    re.compile(r"^My name is", re.I),
    re.compile(r"^I came across your (profile|background|resume|linkedin)", re.I),
]


def _extract_text(ctx: dict[str, Any]) -> str:
    out = ctx.get("output")
    if isinstance(out, dict):
        for key in ("text", "response", "content", "message"):
            v = out.get(key)
            if isinstance(v, str) and v.strip():
                return v
    return ""


def _score_specificity(text: str) -> float:
    hits = sum(1 for p in _SPECIFICITY_PATTERNS if p.search(text))
    return min(1.0, hits / 2.0)


def _score_counter_narrative(text: str) -> float:
    hits = sum(1 for p in _COUNTER_NARRATIVE_PATTERNS if p.search(text))
    return min(1.0, float(hits))


def _score_non_generic_opener(text: str) -> float:
    first_sentence = text.strip()[:200]
    is_generic = any(p.match(first_sentence) for p in _GENERIC_OPENER_PATTERNS)
    return 0.0 if is_generic else 1.0


def _compute_score(text: str) -> float:
    return (
        0.40 * _score_specificity(text)
        + 0.30 * _score_counter_narrative(text)
        + 0.20 * _score_non_generic_opener(text)
        + 0.10  # base credit for any non-empty draft
    )


class AsymmetricInsightJudge:
    is_stub: bool = False
    grader_id: str = GRADER_ID

    def grade(self, dim: Any, run_context: dict[str, Any]) -> tuple[Any, list[str]]:
        ctx = run_context or {}
        text = _extract_text(ctx)
        if not text:
            return GRADER_UNKNOWN_SENTINEL, []

        asymmetric_required = bool(ctx.get("asymmetric_insight_required", False))
        recipient_class = str(ctx.get("recipient_class", "")).upper()
        outreach_mode = str(ctx.get("outreach_mode", "cold")).lower()

        # Bypass: not required → always pass
        if not asymmetric_required:
            refs = [
                "asymmetric_insight::v1::bypassed=not_required",
                "asymmetric_insight::v1::score=1.00",
            ]
            return 1.0, refs

        # Bypass: cold outreach to non-exec — insight not expected
        if outreach_mode == "cold" and recipient_class not in _EXEC_CLASSES:
            refs = [
                f"asymmetric_insight::v1::bypassed=cold_non_exec_{recipient_class}",
                "asymmetric_insight::v1::score=1.00",
            ]
            return 1.0, refs

        score = max(0.0, min(1.0, _compute_score(text)))
        refs = [
            f"asymmetric_insight::v1::specificity={_score_specificity(text):.2f}",
            f"asymmetric_insight::v1::counter_narrative={_score_counter_narrative(text):.2f}",
            f"asymmetric_insight::v1::non_generic_opener={_score_non_generic_opener(text):.2f}",
            f"asymmetric_insight::v1::recipient_class={recipient_class}",
            f"asymmetric_insight::v1::outreach_mode={outreach_mode}",
            f"asymmetric_insight::v1::score={score:.2f}",
        ]
        return score, refs


def grade(dim: Any, run_context: dict[str, Any]) -> tuple[Any, list[str]]:
    return AsymmetricInsightJudge().grade(dim, run_context)


__all__ = ["AsymmetricInsightJudge", "grade", "IS_STUB", "IS_CALIBRATED", "GRADER_ID"]
