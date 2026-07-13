"""apps_rg binding from an approved L6 promotion to an L4 baseline proposal."""

from __future__ import annotations

from typing import Any

from agentic_core.L4_state.contracts.app_domain import (
    ApprovedJudgeCalibrationBaseline,
)
from agentic_core.L4_state.contracts.records import stamp_digest

APPS_RG_EXEC_POSITIONING_CALIBRATION_IDENTITY = {
    "app_id": "apps_rg",
    "task_class": "resume_generation",
    "judge_id": "rg::executive_positioning_judge::v1",
    "judge_version": "v1",
    "rubric_hash": ("e3cec96dfac21b61056f4f5d1d150fa769e3242a5e4b93c4c907afe8b731fdb1"),
    "rubric_version": "1.0.0",
    "provider_profile_ref": "local_qwen_generator",
    "dataset_id": "apps_rg_executive_positioning",
    "dataset_version": "v1",
}


def build_apps_rg_judge_calibration_baseline(
    calibration_result: Any,
    promotion_result: Any,
    *,
    approved_at: str,
    expires_at: str,
    approved_use: str = "ALLOW_ADVISORY_ONLY",
) -> ApprovedJudgeCalibrationBaseline:
    """Build a future-run baseline only after 6D has bound a UWG receipt."""
    if getattr(calibration_result, "status", "") != "PASS":
        raise ValueError("calibration result must pass before baseline construction")
    if not bool(getattr(calibration_result, "promotion_eligible", False)):
        raise ValueError("calibration result is not promotion eligible")
    if getattr(promotion_result, "approval_decision", "") != "APPROVE":
        raise ValueError("6D promotion must be approved")
    promotion = getattr(promotion_result, "promotion", None)
    activation = getattr(promotion_result, "activation", None)
    if promotion is None or activation is None:
        raise ValueError("approved promotion and activation receipts are required")
    if not str(getattr(promotion, "uwg_receipt_id", "") or ""):
        raise ValueError("promotion must carry a bound UWG receipt")
    if getattr(activation, "promotion_packet_id", "") != getattr(
        promotion, "promotion_packet_id", ""
    ) or getattr(activation, "uwg_receipt_id", "") != getattr(promotion, "uwg_receipt_id", ""):
        raise ValueError("activation receipt does not bind the approved promotion")
    if not bool(getattr(activation, "no_current_run_mutation_assertion", False)):
        raise ValueError("activation must preserve the completed run")
    if getattr(activation, "activate_at", "") != "NEXT_RUN_START":
        raise ValueError("calibration baseline activation must be future-run only")
    rho = getattr(calibration_result, "spearman_rho", None)
    p_value = getattr(calibration_result, "p_value", None)
    if rho is None or p_value is None:
        raise ValueError("calibration rho and p-value are required")
    result_digest = str(getattr(calibration_result, "deterministic_digest", "") or "")
    if not result_digest:
        raise ValueError("calibration result must be digest-bound")
    mismatches = [
        key
        for key, expected in APPS_RG_EXEC_POSITIONING_CALIBRATION_IDENTITY.items()
        if key not in {"app_id", "task_class"} and str(getattr(calibration_result, key, "") or "") != expected
    ]
    if mismatches:
        raise ValueError("calibration identity differs from apps_rg runtime: " + ",".join(mismatches))
    return stamp_digest(
        ApprovedJudgeCalibrationBaseline(
            baseline_id=f"baseline::apps_rg::executive-positioning::{result_digest[:20]}",
            app_id="apps_rg",
            task_class="resume_generation",
            status="active",
            judge_id=str(calibration_result.judge_id),
            judge_version=str(calibration_result.judge_version),
            rubric_hash=str(calibration_result.rubric_hash),
            rubric_version=str(calibration_result.rubric_version),
            provider_profile_ref=str(calibration_result.provider_profile_ref),
            dataset_id=str(calibration_result.dataset_id),
            dataset_version=str(calibration_result.dataset_version),
            n=int(calibration_result.n),
            spearman_rho=float(rho),
            p_value=float(p_value),
            threshold=float(calibration_result.minimum_rho_threshold),
            approved_use=approved_use,
            approved_at=approved_at,
            expires_at=expires_at,
            promotion_receipt_ref=str(activation.activation_receipt_id),
            uwg_receipt_ref=str(promotion.uwg_receipt_id),
            source_app_config_ref=("apps_rg/config/domain_contract/judge_calibration_profile.yaml"),
            audit_refs=tuple(
                ref
                for ref in (
                    str(getattr(promotion, "gauntlet_receipt", "") or ""),
                    str(getattr(promotion, "approval_decision_id", "") or ""),
                )
                if ref
            ),
            lineage_refs=tuple(
                ref
                for ref in (
                    str(calibration_result.calibration_id),
                    result_digest,
                    str(promotion.promotion_packet_id),
                    str(getattr(promotion, "deterministic_digest", "") or ""),
                )
                if ref
            ),
        )
    )


__all__ = [
    "APPS_RG_EXEC_POSITIONING_CALIBRATION_IDENTITY",
    "build_apps_rg_judge_calibration_baseline",
]
