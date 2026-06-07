"""apps_lic.engines.judges.personalization_judge — deterministic heuristic (v1).

Plan: docs/archive/windsurf/legacy-tree/plans/apps-lic-deferred-scope-followup-d3f9b2.md W2 D1-P4
Exit rubric dim: personalization_mode_appropriate

Scores 0.0–1.0 where 1.0 = personalization level is well-matched to the
recipient_class + outreach_mode combination.

Scoring model
-------------
Reads from ``run_context``:
  - ``personalization_mode``  str  one of: none/company/role/recipient/relationship/asymmetric
  - ``recipient_class``       str
  - ``outreach_mode``         str  one of: cold/warm/referral/follow_up

Calibration table (cold vs warm axis matters most):

  Cold outreach:
    - RECRUITER/SENIOR_TA:  "company" or "role" → 1.0; "none" → 0.6; "recipient/relationship" → 0.7
    - Exec (EXECUTIVE etc): "company" or "recipient" → 1.0; "none" → 0.3; "role" → 0.7
    - HIRING_MANAGER:       "role" or "company" → 1.0; others contextual
  Warm/referral outreach:
    - Any class:            "recipient" or "relationship" → 1.0; "none" → 0.4
    - RECRUITER warm:       "role" → 0.9; "recipient" → 1.0
  Asymmetric mode:
    - Always 1.0 for exec classes; 0.7 for non-exec (asymmetric insight not
      typically warranted for recruiter cold).

Unknown combinations default to 0.75 (neutral pass).
"""

from __future__ import annotations

from typing import Any

from agentic_core.L3_orchestration.exit_eval.v6.app_grader_registry import (
    GRADER_UNKNOWN_SENTINEL,
)

IS_STUB: bool = False
IS_CALIBRATED: bool = True
GRADER_ID: str = "lic::personalization_judge::v1"

_EXEC_CLASSES: frozenset[str] = frozenset({"EXECUTIVE", "C_LEVEL", "CTO", "VP_ENG"})
_RECRUITER_CLASSES: frozenset[str] = frozenset({"RECRUITER", "SENIOR_TA"})
_WARM_MODES: frozenset[str] = frozenset({"warm", "referral", "warm_referral", "follow_up"})

# score_table[(outreach_mode_is_warm, recipient_bucket, personalization_mode)] = score
_SCORE_TABLE: dict[tuple[bool, str, str], float] = {
    # --- cold ---
    (False, "recruiter", "none"):         0.6,
    (False, "recruiter", "company"):      1.0,
    (False, "recruiter", "role"):         1.0,
    (False, "recruiter", "recipient"):    0.7,
    (False, "recruiter", "relationship"): 0.7,
    (False, "recruiter", "asymmetric"):   0.7,
    (False, "exec",      "none"):         0.3,
    (False, "exec",      "company"):      1.0,
    (False, "exec",      "role"):         0.7,
    (False, "exec",      "recipient"):    1.0,
    (False, "exec",      "relationship"): 0.8,
    (False, "exec",      "asymmetric"):   1.0,
    (False, "hiring",    "none"):         0.5,
    (False, "hiring",    "company"):      1.0,
    (False, "hiring",    "role"):         1.0,
    (False, "hiring",    "recipient"):    0.8,
    (False, "hiring",    "relationship"): 0.8,
    (False, "hiring",    "asymmetric"):   0.9,
    # --- warm / referral ---
    (True,  "recruiter", "none"):         0.4,
    (True,  "recruiter", "company"):      0.8,
    (True,  "recruiter", "role"):         0.9,
    (True,  "recruiter", "recipient"):    1.0,
    (True,  "recruiter", "relationship"): 1.0,
    (True,  "recruiter", "asymmetric"):   0.8,
    (True,  "exec",      "none"):         0.3,
    (True,  "exec",      "company"):      0.8,
    (True,  "exec",      "role"):         0.7,
    (True,  "exec",      "recipient"):    1.0,
    (True,  "exec",      "relationship"): 1.0,
    (True,  "exec",      "asymmetric"):   1.0,
    (True,  "hiring",    "none"):         0.4,
    (True,  "hiring",    "company"):      0.8,
    (True,  "hiring",    "role"):         1.0,
    (True,  "hiring",    "recipient"):    1.0,
    (True,  "hiring",    "relationship"): 1.0,
    (True,  "hiring",    "asymmetric"):   0.9,
}


def _recipient_bucket(recipient_class: str) -> str:
    if recipient_class in _RECRUITER_CLASSES:
        return "recruiter"
    if recipient_class in _EXEC_CLASSES:
        return "exec"
    if recipient_class == "HIRING_MANAGER":
        return "hiring"
    return "other"


def _extract_text(ctx: dict[str, Any]) -> str:
    out = ctx.get("output")
    if isinstance(out, dict):
        for key in ("text", "response", "content", "message"):
            v = out.get(key)
            if isinstance(v, str) and v.strip():
                return v
    return ""


class PersonalizationJudge:
    is_stub: bool = False
    grader_id: str = GRADER_ID

    def grade(self, dim: Any, run_context: dict[str, Any]) -> tuple[Any, list[str]]:
        ctx = run_context or {}
        text = _extract_text(ctx)
        if not text:
            return GRADER_UNKNOWN_SENTINEL, []

        p_mode = str(ctx.get("personalization_mode", "")).lower().strip()
        recipient_class = str(ctx.get("recipient_class", "")).upper()
        outreach_mode = str(ctx.get("outreach_mode", "cold")).lower().strip()

        is_warm = outreach_mode in _WARM_MODES
        bucket = _recipient_bucket(recipient_class)

        key = (is_warm, bucket, p_mode)
        if bucket == "other":
            score = 0.75
            reason = "unknown_recipient_class_neutral"
        elif p_mode == "":
            score = 0.5
            reason = "personalization_mode_not_set"
        else:
            score = _SCORE_TABLE.get(key, 0.75)
            reason = f"table_lookup_{key}"

        refs = [
            f"personalization::v1::recipient_class={recipient_class}",
            f"personalization::v1::outreach_mode={outreach_mode}",
            f"personalization::v1::p_mode={p_mode}",
            f"personalization::v1::is_warm={is_warm}",
            f"personalization::v1::bucket={bucket}",
            f"personalization::v1::reason={reason}",
            f"personalization::v1::score={score:.2f}",
        ]
        return score, refs


def grade(dim: Any, run_context: dict[str, Any]) -> tuple[Any, list[str]]:
    return PersonalizationJudge().grade(dim, run_context)


__all__ = ["PersonalizationJudge", "grade", "IS_STUB", "IS_CALIBRATED", "GRADER_ID"]
