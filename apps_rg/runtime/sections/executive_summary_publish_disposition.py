"""Publish disposition SSOT for executive_summary pool handoff (certified vs best_effort)."""

from __future__ import annotations

import os
from typing import Any

from apps_rg.runtime.sections.executive_summary_judge_remediation import (
    all_model_backed_judges_pass,
    _is_model_backed_soft_fail,
    _normalize_judge_list,
)


def best_effort_publish_allowed_from_env() -> bool:
    raw = os.environ.get("APPS_RG_EXEC_SUMMARY_BEST_EFFORT_PUBLISH_ALLOWED", "").strip().lower()
    return raw in ("1", "true", "yes", "on")


def blocking_judge_ids(x1d_judges: list[dict[str, Any]]) -> list[str]:
    out: list[str] = []
    for judge in _normalize_judge_list(x1d_judges):
        if judge.get("evaluator_mode") != "MODEL_BACKED":
            continue
        if _is_model_backed_soft_fail(judge) or judge.get("decisive_failure"):
            pk = str(judge.get("provider_key") or judge.get("judge_id") or "").strip()
            if pk:
                out.append(pk)
    return sorted(set(out))


def resolve_publish_disposition(
    x1d_judges: list[dict[str, Any]],
    *,
    best_effort_publish_allowed: bool,
    published_from_pool: bool,
) -> dict[str, Any]:
    """Classify published snapshot for proof/Exit consequences."""
    judges_pass = all_model_backed_judges_pass(x1d_judges)
    blocking = blocking_judge_ids(x1d_judges)
    if judges_pass:
        return {
            "schema": "executive_summary_publish_disposition_v1",
            "publish_disposition": "certified",
            "x1d_certified": True,
            "proof_eligible": True,
            "judge_certified": True,
            "blocking_judge_ids": [],
            "best_effort_publish_allowed": bool(best_effort_publish_allowed),
            "published_from_pool": bool(published_from_pool),
            "x3_certification_note": "eligible_for_allow_when_x2_and_x3_allow",
        }
    if published_from_pool and best_effort_publish_allowed:
        return {
            "schema": "executive_summary_publish_disposition_v1",
            "publish_disposition": "best_effort",
            "x1d_certified": False,
            "proof_eligible": False,
            "judge_certified": False,
            "blocking_judge_ids": blocking,
            "best_effort_publish_allowed": True,
            "published_from_pool": True,
            "x3_certification_note": "non_certified_review_only",
        }
    return {
        "schema": "executive_summary_publish_disposition_v1",
        "publish_disposition": "judge_certification_required",
        "x1d_certified": False,
        "proof_eligible": False,
        "judge_certified": False,
        "blocking_judge_ids": blocking,
        "best_effort_publish_allowed": bool(best_effort_publish_allowed),
        "published_from_pool": bool(published_from_pool),
        "x3_certification_note": "pool_publish_blocked_without_best_effort_flag",
    }


def apply_publish_disposition_to_proof_bundle(
    bundle: dict[str, Any],
    disposition: dict[str, Any],
) -> dict[str, Any]:
    """Override proof surfaces when publish is best_effort or judge-blocked."""
    out = dict(bundle)
    pub = str(disposition.get("publish_disposition") or "")
    if pub == "certified":
        out["publish_disposition"] = pub
        out["x1d_certified"] = True
        return out
    out["publish_disposition"] = pub
    out["x1d_certified"] = False
    out["proof_eligible"] = False
    out["judge_proof_eligible"] = False
    out["provider_proof_eligible"] = False
    out["runtime_certification"] = "NON_CERTIFIED_PUBLISH"
    note = str(disposition.get("x3_certification_note") or "")
    blocking = disposition.get("blocking_judge_ids") or []
    if blocking:
        note = f"{note}; blocking_judges={','.join(blocking)}".strip("; ")
    prior = str(out.get("proof_closeout_note") or "").strip()
    suffix = f"publish_disposition={pub}"
    if note:
        suffix = f"{suffix}; {note}"
    out["proof_closeout_note"] = f"{prior}; {suffix}".strip("; ") if prior else suffix
    return out


def apply_publish_disposition_to_x3_dict(
    x3_data: dict[str, Any],
    disposition: dict[str, Any],
) -> dict[str, Any]:
    """Ensure best_effort publish cannot present as X3_ALLOW / certified."""
    out = dict(x3_data)
    pub = str(disposition.get("publish_disposition") or "")
    out["publish_disposition"] = pub
    out["x1d_certified"] = disposition.get("x1d_certified", False)
    out["blocking_judge_ids"] = list(disposition.get("blocking_judge_ids") or [])
    if pub == "certified":
        return out
    if pub == "best_effort":
        out["pass"] = False
        if str(out.get("x3_code") or "") == "X3_ALLOW":
            out["x3_code"] = "X3_REVIEW_PUBLISH_BEST_EFFORT"
        elif not str(out.get("x3_code") or "").startswith("X3_REVIEW"):
            out["x3_code"] = "X3_REVIEW_JUDGE_SOFT_FAIL"
        review = str(out.get("review_reason") or "").strip()
        extra = "Published best_effort snapshot; not X1D-certified (set APPS_RG_EXEC_SUMMARY_BEST_EFFORT_PUBLISH_ALLOWED=1)."
        out["review_reason"] = f"{review}; {extra}".strip("; ") if review else extra
    elif pub == "judge_certification_required":
        out["pass"] = False
        if str(out.get("x3_code") or "") == "X3_ALLOW":
            out["x3_code"] = "X3_REVIEW_PUBLISH_NOT_CERTIFIED"
    return out


__all__ = [
    "apply_publish_disposition_to_proof_bundle",
    "apply_publish_disposition_to_x3_dict",
    "best_effort_publish_allowed_from_env",
    "blocking_judge_ids",
    "resolve_publish_disposition",
]
