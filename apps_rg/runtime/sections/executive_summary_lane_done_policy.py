"""Executive summary lane \"done\" policy — operator exit, regen, artifact flags.

Single SSOT for acceptance scenarios: frozen L2 output + judge scores must map to
the written operator contract (draft vs certified, judge regen trigger, CLI exit).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from apps_rg.runtime.sections.executive_summary_judge_remediation import (
    evaluate_judge_remediation_trigger,
)
from apps_rg.runtime.sections.executive_summary_operator_disposition import (
    compute_executive_summary_operator_disposition,
)
from apps_rg.runtime.sections.executive_summary_repair_policy import (
    judge_regeneration_enabled,
)

_PRODUCT_QUALITY_PASS = "PASS"
_RUNTIME_REAL_LLM = "REAL_LLM"
_X3_SOFT_FAIL = "X3_REVIEW_JUDGE_SOFT_FAIL"
_X3_ALLOW = "X3_ALLOW"


@dataclass(frozen=True)
class ExecutiveSummaryLaneDonePolicy:
    draft_ready: bool
    certified: bool
    process_exit_code: int
    operator_status: str
    disposition_tier: str
    proof_eligible: bool
    judge_regen_triggered: bool
    judge_regen_trigger_mode: str | None
    judge_regen_skip_reason: str | None
    soft_judge_only_rescore_eligible: bool
    artifact_flags: dict[str, Any]


def _operator_status(*, draft_ready: bool, certified: bool) -> str:
    if certified:
        return "CERTIFIED"
    if draft_ready:
        return "DRAFT_READY"
    return "NOT_READY"


def _soft_judge_only_rescore_eligible(
    *,
    judge_regen_triggered: bool,
    trigger_receipt: dict[str, Any],
    x1d_judges: list[dict[str, Any]],
) -> bool:
    """Deprecated path: any judge below floor triggers Qwen regen (no rescore-only shortcut)."""
    del judge_regen_triggered, trigger_receipt, x1d_judges
    return False


def compute_executive_summary_lane_done_policy(
    *,
    l2_output: dict[str, Any],
    x3_disposition: dict[str, Any],
    x1d_judges: list[dict[str, Any]],
    manifest: dict[str, Any] | None = None,
    cli_path_pass: bool = True,
    fault: str = "",
    judge_regen_enabled: bool | None = None,
) -> ExecutiveSummaryLaneDonePolicy:
    """Derive lane done semantics from frozen L2 + judge artifacts (no live LLM)."""
    manifest = dict(manifest or {})
    rgs = str(l2_output.get("runtime_generation_status") or manifest.get("runtime_generation_status") or _RUNTIME_REAL_LLM)
    if rgs:
        manifest.setdefault("runtime_generation_status", rgs)

    op = compute_executive_summary_operator_disposition(
        artifact_dir=None,
        x3_loaded=x3_disposition,
        manifest_loaded=manifest,
        cli_path_pass=cli_path_pass,
        fault=fault,
    )
    x2_passed = str(x3_disposition.get("product_quality_status") or _PRODUCT_QUALITY_PASS) == _PRODUCT_QUALITY_PASS
    regen_enabled = judge_regeneration_enabled() if judge_regen_enabled is None else judge_regen_enabled

    triggered, trigger_receipt = evaluate_judge_remediation_trigger(
        x1d_judges,
        runtime_generation_status=rgs,
        x2_passed=x2_passed,
    )
    judge_regen_triggered = bool(triggered and regen_enabled and rgs == _RUNTIME_REAL_LLM and x2_passed)
    skip_reason = None if judge_regen_triggered else str(trigger_receipt.get("reason") or "")

    proof_eligible = bool(op.certified and manifest.get("proof_eligible", op.certified))
    operator_status = _operator_status(draft_ready=op.draft_ready, certified=op.certified)

    artifact_flags = {
        "runtime_generation_status": rgs,
        "product_quality_status": op.product_quality_status,
        "x3_code": op.x3_code,
        "x3_pass": bool(x3_disposition.get("pass")),
        "model_backed_pass_count": trigger_receipt.get("model_backed_pass_count"),
        "soft_fail_count": trigger_receipt.get("soft_fail_count"),
        "judge_regen_enabled": regen_enabled,
        "judge_remediation_trigger": trigger_receipt,
        "post_x2_judge_refresh_rescore_only": not regen_enabled,
        "expected_nonzero_exit": op.expected_nonzero_exit,
    }

    return ExecutiveSummaryLaneDonePolicy(
        draft_ready=op.draft_ready,
        certified=op.certified,
        process_exit_code=op.process_exit_code,
        operator_status=operator_status,
        disposition_tier=op.disposition_tier,
        proof_eligible=proof_eligible,
        judge_regen_triggered=judge_regen_triggered,
        judge_regen_trigger_mode=(
            str(trigger_receipt.get("trigger_mode")) if judge_regen_triggered else None
        ),
        judge_regen_skip_reason=skip_reason or None,
        soft_judge_only_rescore_eligible=_soft_judge_only_rescore_eligible(
            judge_regen_triggered=judge_regen_triggered,
            trigger_receipt=trigger_receipt,
            x1d_judges=x1d_judges,
        ),
        artifact_flags=artifact_flags,
    )


def x3_disposition_for_judges(
    *,
    x3_code: str,
    x3_pass: bool,
    product_quality_status: str = _PRODUCT_QUALITY_PASS,
) -> dict[str, Any]:
    return {
        "x3_code": x3_code,
        "pass": x3_pass,
        "product_quality_status": product_quality_status,
    }


__all__ = [
    "ExecutiveSummaryLaneDonePolicy",
    "compute_executive_summary_lane_done_policy",
    "x3_disposition_for_judges",
    "_X3_ALLOW",
    "_X3_SOFT_FAIL",
]
