"""apps_lic.engines.judges.proof_appropriate_judge — deterministic heuristic (v1).

Plan: .windsurf/plans/apps-lic-deferred-scope-followup-d3f9b2.md W2 D1-P3
Exit rubric dim: proof_appropriate_for_recipient

Scores 0.0–1.0 where 1.0 = proof is well-matched to the recipient context.

Scoring model
-------------
Reads ``run_context`` fields:
  - ``recipient_class``     str  e.g. "EXECUTIVE", "RECRUITER"
  - ``proof_links``         list of proof items in the draft (optional)
  - ``technical_claim_depth_high``  bool (default False)
  - ``output.text``         the draft text

Logic:

1. If recipient_class is RECRUITER or SENIOR_TA:
   - Technical proof is *not required* → return 1.0 unless a strong
     technical claim is detected without proof (score 0.5).
2. If recipient_class is exec/technical (EXECUTIVE, C_LEVEL, CTO, VP_ENG,
   HIRING_MANAGER):
   - If technical_claim_depth_high=True:
     * Proof markers detected in text → 1.0
     * No proof markers → 0.2 (insufficient proof for exec audience)
   - If technical_claim_depth_high=False:
     * Score 0.9 (proof not required, contextually appropriate)
3. Unknown recipient_class → 0.7 (neutral / conservative pass)

Proof markers detected via regex heuristics over draft text:
github.com, linkedin.com, portfolio, project_link, attached, see exhibit,
resume metric patterns (N%, $N, N× improvement), "as demonstrated".
"""

from __future__ import annotations

import re
from typing import Any

from agentic_core.L3_orchestration.exit_eval.v6.app_grader_registry import (
    GRADER_UNKNOWN_SENTINEL,
)

IS_STUB: bool = False
IS_CALIBRATED: bool = True
GRADER_ID: str = "lic::proof_appropriate_judge::v1"

_EXEC_CLASSES: frozenset[str] = frozenset({"EXECUTIVE", "C_LEVEL", "CTO", "VP_ENG", "HIRING_MANAGER"})
_RECRUITER_CLASSES: frozenset[str] = frozenset({"RECRUITER", "SENIOR_TA"})

_PROOF_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"github\.com/\S+", re.I),
    re.compile(r"linkedin\.com/in/\S+", re.I),
    re.compile(r"\b(portfolio|project link|see exhibit|attached|as demonstrated)\b", re.I),
    re.compile(r"\b\d+[%×x]\b"),  # metrics like 40%, 3×
    re.compile(r"\$\d+[KkMm]?\b"),  # dollar figures
    re.compile(r"\b(improved|reduced|increased|shipped|built|deployed|scaled)\b.*\bby\b.*\d", re.I),
]

_STRONG_TECH_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\b(I (built|designed|architected|implemented|shipped|deployed))\b", re.I),
    re.compile(r"\b(at scale|production (system|service|pipeline))\b", re.I),
    re.compile(r"\b(distributed|microservice|ml pipeline|model training|latency)\b", re.I),
]


def _extract_text(ctx: dict[str, Any]) -> str:
    out = ctx.get("output")
    if isinstance(out, dict):
        for key in ("text", "response", "content", "message"):
            v = out.get(key)
            if isinstance(v, str) and v.strip():
                return v
    return ""


def _has_proof(text: str) -> bool:
    return any(p.search(text) for p in _PROOF_PATTERNS)


def _has_strong_tech_claim(text: str) -> bool:
    return any(p.search(text) for p in _STRONG_TECH_PATTERNS)


class ProofAppropriateJudge:
    is_stub: bool = False
    grader_id: str = GRADER_ID

    def grade(self, dim: Any, run_context: dict[str, Any]) -> tuple[Any, list[str]]:
        ctx = run_context or {}
        text = _extract_text(ctx)
        if not text:
            return GRADER_UNKNOWN_SENTINEL, []

        recipient_class = str(ctx.get("recipient_class", "")).upper()
        technical_high = bool(ctx.get("technical_claim_depth_high", False))

        proof_present = _has_proof(text)
        strong_tech = _has_strong_tech_claim(text)

        if recipient_class in _RECRUITER_CLASSES:
            if strong_tech and not proof_present:
                score = 0.5
                reason = "strong_tech_claim_without_proof_for_recruiter"
            else:
                score = 1.0
                reason = "proof_not_required_for_recruiter"
        elif recipient_class in _EXEC_CLASSES:
            if technical_high or strong_tech:
                score = 1.0 if proof_present else 0.2
                reason = "exec_technical_with_proof" if proof_present else "exec_technical_missing_proof"
            else:
                score = 0.9
                reason = "exec_no_technical_claim_proof_not_required"
        else:
            score = 0.7
            reason = "unknown_recipient_class_neutral"

        refs = [
            f"proof_appropriate::v1::recipient_class={recipient_class}",
            f"proof_appropriate::v1::proof_present={proof_present}",
            f"proof_appropriate::v1::technical_high={technical_high}",
            f"proof_appropriate::v1::strong_tech={strong_tech}",
            f"proof_appropriate::v1::reason={reason}",
            f"proof_appropriate::v1::score={score:.2f}",
        ]
        return score, refs


def grade(dim: Any, run_context: dict[str, Any]) -> tuple[Any, list[str]]:
    return ProofAppropriateJudge().grade(dim, run_context)


__all__ = ["ProofAppropriateJudge", "grade", "IS_STUB", "IS_CALIBRATED", "GRADER_ID"]
