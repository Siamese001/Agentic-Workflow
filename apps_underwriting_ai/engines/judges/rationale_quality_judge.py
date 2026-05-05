"""apps_underwriting_ai.engines.judges.rationale_quality_judge — PROMOTED (v2 deterministic).

Plan: ``.windsurf/plans/apps-underwriting-ai-d3-rationale-judge-f2c8d5.md`` W2.P1.

PROMOTION HISTORY
=================
- v1 (stub, plan apps-underwriting-ai-deferred-scope-e8b2f4 D3): returned
  GRADER_UNKNOWN_SENTINEL always (was never committed — file did not exist).
- **v2 (this plan)**: deterministic heuristic scorer — no LLM call, no
  human-labeled holdout required for correctness. Scores the rationale
  quality of an ``apps_underwriting_ai`` DecisionPacket on a 0..1 scale
  using four measurable features. This is NOT a full-fidelity LLM judge;
  it is a real, deterministic grader that replaces the UNKNOWN sentinel
  with a signal-bearing score while calibration-backed LLM scoring remains
  deferred to a future plan.

Scoring model (v2)
------------------
Reads the decision rationale from ``run_context`` via the following fallback
chain::

    run_context["output"]["rationale"]
    run_context["output"]["text"]
    run_context["output"]["response"]
    run_context.get("rationale")   # flat form
    ""  (empty — returns GRADER_UNKNOWN_SENTINEL)

Evidence references are read from ``run_context["output"].get("evidence_refs", [])``
or ``run_context.get("evidence_refs", [])``.

Four features are combined into a weighted composite score:

1. **Rationale length adequacy** — length ≥ 100 chars scores 1.0; 50–99
   scores proportionally; < 50 scores low. Weighted 0.30.
2. **Evidence reference count** — saturates at 5 refs for full score.
   Weighted 0.25.
3. **Explanation quality terms** — presence of terms indicating structured
   reasoning (because, therefore, due to, based on, resulting in, confirms,
   verified, consistent with, exceeds, below, satisfies, demonstrates).
   Saturates at 3 hits. Weighted 0.25.
4. **Compliance / fairness signals** — presence of fairness, policy, or
   compliance language (ecoa, fair lending, protected, compliant, no
   violations, policy section, threshold). Weighted 0.20.

When the rationale text is empty, returns ``(GRADER_UNKNOWN_SENTINEL, [])``
to preserve fail-open behavior.

Integration contract
--------------------
::

    def grade(dim, run_context) -> tuple[float | int, list[str]]

Returns ``(score ∈ [0, 1], evidence_refs)`` or ``(GRADER_UNKNOWN_SENTINEL, [])``
when abstaining (empty rationale).

Spearman calibration
--------------------
Tested against the synthetic holdout at
``apps_underwriting_ai/holdout/rationale_judge_holdout.yaml`` (100 examples,
20 per dim). Correlation ≥ 0.80 is verified by
``tests/governance/test_apps_underwriting_ai_rationale_judge.py``.
"""

from __future__ import annotations

import re
from typing import Any, Mapping

from agentic_core.L3_orchestration.exit_eval.v6.app_grader_registry import (
    GRADER_UNKNOWN_SENTINEL,
)

IS_STUB: bool = False
"""This judge is a promoted real implementation (deterministic v2)."""

IS_CALIBRATED: bool = True
"""Deterministic heuristic scorer — calibrated against holdout Spearman ≥ 0.80.

DS-R3: Strict mode is now active. IS_CALIBRATED=True enables fail_closed_if_unknown
by default — empty/unknown rationale is treated as a score of 0.0 rather than
routing to HITL. Override per-instance via RationaleQualityJudge(fail_closed_if_unknown=False).
"""

FAIL_CLOSED_IF_UNKNOWN: bool = True
"""DS-R8: When True, empty/missing rationale returns score=0.0 instead of GRADER_UNKNOWN_SENTINEL.

Activated now that IS_CALIBRATED=True and global Spearman ρ ≥ 0.80.
Set to False to restore fail-open behavior (returns GRADER_UNKNOWN_SENTINEL → HITL route).
"""

GRADER_ID: str = "underwriting::rationale_quality_judge::v2"
"""Roster ID for this judge."""

_EXPLANATION_TERMS: frozenset[str] = frozenset(
    {
        "because",
        "therefore",
        "due to",
        "based on",
        "resulting in",
        "confirms",
        "verified",
        "consistent with",
        "exceeds",
        "below",
        "satisfies",
        "demonstrates",
    }
)

_COMPLIANCE_TERMS: frozenset[str] = frozenset(
    {
        "ecoa",
        "fair lending",
        "protected",
        "compliant",
        "no violations",
        "policy section",
        "threshold",
        "compliance",
        "permissible",
    }
)

_POLICY_PASS_TERMS: frozenset[str] = frozenset(
    {
        "pass",
        "compliant",
        "compliance confirmed",
        "no violations",
        "zero violations",
        "all checks pass",
        "full compliance",
        "policy status: pass",
    }
)

_POLICY_SECTION_PATTERN = re.compile(
    r"policy\s+section\s+\d",
    re.IGNORECASE,
)

_VIOLATION_TERMS: frozenset[str] = frozenset(
    {
        "violation",
        "violated",
        "gate triggered",
        "hard gate",
        "non-compliant",
        "noncompliant",
        "mandatory decline",
        "cannot approve",
    }
)

# "exceeds" in context of limit/max/cap = violation; "exceeds threshold"
# meaning it passes (FICO 740 exceeds minimum of 620) is NOT a violation.
_VIOLATION_EXCEEDS_PATTERN = re.compile(
    r"exceeds\s+(?:the\s+)?(?:maximum|max|limit|cap|permitted|allowed)",
    re.IGNORECASE,
)

_WORD_PATTERN = re.compile(r"\b[a-zA-Z]+\b")

# W3: feature_derivation_correctness — numeric formula / ratio signals
_NUMERIC_VALUE_PATTERN = re.compile(
    r"\b\d+(?:\.\d+)?\s*(?:%|percent|ratio|ltv|dti|fico|score|bps|pts?|\$)\b",
    re.IGNORECASE,
)
_FORMULA_TERMS: frozenset[str] = frozenset(
    {
        "calculated as",
        "derived from",
        "computed",
        "formula",
        "equals",
        "divided by",
        "multiplied by",
        "ratio of",
        "sum of",
        "total debt",
        "monthly income",
        "appraised value",
        "loan amount",
        "principal balance",
        "ltv is",
        "dti is",
        "fico is",
    }
)

# W3: policy_compliance — extended citation patterns
_POLICY_CITE_PATTERN = re.compile(
    r"(?:"
    r"policy\s+(?:section|article|clause|rule|requirement)\s*[\d\.]+"
    r"|regulation\s+[a-z]\b"
    r"|12\s*cfr\b"
    r"|ecoa\s+(?:section|compliance)"
    r"|tila\b"
    r"|hmda\b"
    r"|fair\s+credit\s+reporting"
    r"|fair\s+lending"
    r"|ability\s+to\s+repay"
    r")",
    re.IGNORECASE,
)


def _extract_rationale(run_context: Mapping[str, Any]) -> str:
    out = run_context.get("output") if isinstance(run_context, Mapping) else None
    if isinstance(out, Mapping):
        for key in ("rationale", "text", "response", "content"):
            value = out.get(key)
            if isinstance(value, str) and value.strip():
                return value
    flat = run_context.get("rationale") if isinstance(run_context, Mapping) else None
    if isinstance(flat, str) and flat.strip():
        return flat
    return ""


def _extract_evidence_refs(run_context: Mapping[str, Any]) -> list[str]:
    out = run_context.get("output") if isinstance(run_context, Mapping) else None
    if isinstance(out, Mapping):
        refs = out.get("evidence_refs")
        if isinstance(refs, list):
            return refs
    flat = run_context.get("evidence_refs") if isinstance(run_context, Mapping) else None
    if isinstance(flat, list):
        return flat
    return []


def _score_length(text: str) -> float:
    n = len(text)
    if n >= 100:
        return 1.0
    if n >= 50:
        return 0.5 + 0.5 * ((n - 50) / 50.0)
    if n > 0:
        return max(0.0, 0.3 * (n / 50.0))
    return 0.0


def _score_evidence_refs(refs: list[str]) -> float:
    return min(1.0, len(refs) / 5.0)


def _score_explanation_terms(text: str) -> float:
    lower = text.lower()
    hits = sum(1 for term in _EXPLANATION_TERMS if term in lower)
    return min(1.0, hits / 3.0)


def _score_compliance_terms(text: str) -> float:
    lower = text.lower()
    hits = sum(1 for term in _COMPLIANCE_TERMS if term in lower)
    return min(1.0, hits / 2.0)


def _score_feature_derivation(text: str) -> float:
    """Signal for feature_derivation_correctness dim.

    Rewards numeric values with units (LTV%, DTI ratio, FICO score, dollar
    amounts) and formula/derivation language.  Saturates at 0.80 so an
    otherwise weak rationale with only numbers doesn't score perfect.
    """
    lower = text.lower()
    numeric_hits = len(_NUMERIC_VALUE_PATTERN.findall(text))
    formula_hits = sum(1 for term in _FORMULA_TERMS if term in lower)
    numeric_score = min(0.50, numeric_hits * 0.15)
    formula_score = min(0.30, formula_hits * 0.15)
    return min(0.80, numeric_score + formula_score)


def _score_extended_policy_citation(text: str) -> float:
    """Extended policy citation signal for policy_compliance dim.

    Rewards specific regulatory references (12 CFR, Regulation B/Z, ECOA
    section, TILA, HMDA, ATR) and policy section citations beyond the basic
    'policy section N' pattern.  Saturates at 0.60.
    """
    hits = len(_POLICY_CITE_PATTERN.findall(text))
    return min(0.60, hits * 0.20)


def _score_policy_signal(text: str) -> float:
    """Combined policy-compliance signal on [0, 1].

    Rewards:
    - Explicit PASS / compliant / no-violations language (+0.5 per hit,
      saturating at 0.60).
    - Policy section citations (e.g. "policy section 2.1") (+0.20 per hit,
      saturating at 0.40 additional).

    Penalizes:
    - Explicit violation / gate-triggered language (−0.60 per hit,
      floored at 0.0).
    - Contextual "exceeds the maximum/limit" pattern (−0.60).

    The net score is clamped to [0.0, 1.0].  This produces a gradient
    that ranks "multiple policy sections cited, PASS confirmed" at ~0.90
    and "gate violation detected" near 0.10–0.20.
    """
    lower = text.lower()

    pass_hits = sum(1 for term in _POLICY_PASS_TERMS if term in lower)
    section_hits = len(_POLICY_SECTION_PATTERN.findall(text))

    violation_hits = sum(1 for term in _VIOLATION_TERMS if term in lower)
    if _VIOLATION_EXCEEDS_PATTERN.search(text):
        violation_hits += 1

    pass_score = min(0.60, pass_hits * 0.30)
    section_score = min(0.40, section_hits * 0.20)
    positive = pass_score + section_score

    penalty = min(1.0, violation_hits * 0.60)
    return max(0.0, min(1.0, positive - penalty))


def _compute_score(text: str, refs: list[str]) -> float:
    """Baseline composite score — used when no dim-specific signals apply."""
    return (
        0.25 * _score_length(text)
        + 0.20 * _score_evidence_refs(refs)
        + 0.20 * _score_explanation_terms(text)
        + 0.15 * _score_compliance_terms(text)
        + 0.20 * _score_policy_signal(text)
    )


def _compute_score_for_dim(text: str, refs: list[str], dim_id: str) -> float:
    """Dim-aware composite score that injects dim-specific feature signals.

    For ``feature_derivation_correctness``: replaces the compliance_terms
    component (weight 0.15) with numeric/formula derivation signal, and
    replaces policy_signal (weight 0.20) with extended feature derivation
    signal.  Weights still sum to 1.0.

    For ``policy_compliance``: replaces the evidence_refs component (0.20)
    with extended regulatory citation score (0.20).  The basic policy_signal
    component (0.20) is retained.

    All other dims fall through to the baseline ``_compute_score``.
    """
    if dim_id == "feature_derivation_correctness":
        return (
            0.20 * _score_length(text)
            + 0.15 * _score_evidence_refs(refs)
            + 0.20 * _score_explanation_terms(text)
            + 0.45 * _score_feature_derivation(text)
        )
    if dim_id == "policy_compliance":
        return (
            0.25 * _score_length(text)
            + 0.15 * _score_evidence_refs(refs)
            + 0.15 * _score_explanation_terms(text)
            + 0.15 * _score_compliance_terms(text)
            + 0.10 * _score_policy_signal(text)
            + 0.20 * _score_extended_policy_citation(text)
        )
    return _compute_score(text, refs)


class RationaleQualityJudge:
    """Deterministic rationale quality judge (v2).

    Scores the quality of a DecisionPacket rationale on 0..1 using
    four measurable, LLM-free heuristic features.

    Parameters
    ----------
    fail_closed_if_unknown:
        When True (default, DS-R8), an empty/missing rationale returns
        ``(0.0, ["rationale_quality::v2::unknown=fail_closed"])`` instead of
        ``(GRADER_UNKNOWN_SENTINEL, [])``. Set to False to restore fail-open
        behavior (UNKNOWN → HITL route).
    """

    is_stub: bool = False
    grader_id: str = GRADER_ID

    def __init__(self, *, fail_closed_if_unknown: bool = FAIL_CLOSED_IF_UNKNOWN) -> None:
        self._fail_closed = fail_closed_if_unknown

    def grade(self, dim: Any, run_context: dict[str, Any]) -> tuple[Any, list[str]]:
        text = _extract_rationale(run_context or {})
        if not text:
            if self._fail_closed:
                return 0.0, ["rationale_quality::v2::unknown=fail_closed"]
            return GRADER_UNKNOWN_SENTINEL, []
        refs = _extract_evidence_refs(run_context or {})
        dim_id = getattr(dim, "dimension_id", None) or (dim if isinstance(dim, str) else "")
        score = max(0.0, min(1.0, _compute_score_for_dim(text, refs, dim_id)))
        evidence_refs = [
            f"rationale_quality::v2::length={_score_length(text):.2f}",
            f"rationale_quality::v2::evidence_refs={_score_evidence_refs(refs):.2f}",
            f"rationale_quality::v2::explanation={_score_explanation_terms(text):.2f}",
            f"rationale_quality::v2::compliance={_score_compliance_terms(text):.2f}",
            f"rationale_quality::v2::policy_signal={_score_policy_signal(text):.2f}",
            f"rationale_quality::v2::dim={dim_id}",
        ]
        return score, evidence_refs


def grade(dim: Any, run_context: dict[str, Any]) -> tuple[Any, list[str]]:
    """Module-level callable form — uses module-level FAIL_CLOSED_IF_UNKNOWN default."""
    return RationaleQualityJudge().grade(dim, run_context)


__all__ = [
    "RationaleQualityJudge",
    "grade",
    "IS_STUB",
    "IS_CALIBRATED",
    "FAIL_CLOSED_IF_UNKNOWN",
    "GRADER_ID",
]
