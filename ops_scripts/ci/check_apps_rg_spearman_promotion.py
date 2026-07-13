"""RG-SPEARMAN-PROMOTION: validate an approved future-run L4 baseline."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agentic_core.L4_state.contracts.app_domain import (  # noqa: E402
    APPROVED_JUDGE_USE_VOCAB,
    ApprovedJudgeCalibrationBaseline,
)
from agentic_core.L4_state.contracts.records import stamp_digest  # noqa: E402
from ops_scripts.ci._apps_rg_spearman_gate_common import (  # noqa: E402
    PROFILE_PATH,
    PROMOTION_ARTIFACT_PATH,
    configured_path,
    finish,
    load_yaml,
)


def validate_promotion(
    *,
    artifact_path: Path = PROMOTION_ARTIFACT_PATH,
    profile_path: Path = PROFILE_PATH,
) -> list[str]:
    if not artifact_path.is_file():
        return [f"approved calibration baseline is missing: {artifact_path}"]
    try:
        payload = json.loads(artifact_path.read_text(encoding="utf-8"))
        profile = load_yaml(profile_path)
        baseline_payload: dict[str, Any] = payload.get("baseline") or payload
        baseline = ApprovedJudgeCalibrationBaseline(**baseline_payload)
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        return [f"invalid promotion artifact: {exc}"]
    errors: list[str] = []
    semantic = profile.get("semantic_alignment") or {}
    expected = {
        "app_id": profile.get("app_id"),
        "task_class": profile.get("task_class"),
        "judge_id": profile.get("judge_id"),
        "judge_version": profile.get("judge_version"),
        "rubric_hash": profile.get("rubric_hash"),
        "rubric_version": profile.get("rubric_version"),
        "provider_profile_ref": profile.get("provider_profile_ref"),
    }
    for key, value in expected.items():
        if getattr(baseline, key) != value:
            errors.append(f"baseline {key} differs from active profile")
    if baseline.status != "active":
        errors.append("baseline is not active")
    if baseline.created_by_surface != "UWG":
        errors.append("baseline was not created by UWG")
    if not baseline.uwg_receipt_ref or not baseline.promotion_receipt_ref:
        errors.append("baseline lacks UWG or promotion receipt")
    if baseline.n < int(semantic.get("minimum_samples", 40)):
        errors.append("baseline sample count is below the semantic minimum")
    if baseline.spearman_rho < float(semantic.get("minimum_spearman_rho", 0.8)):
        errors.append("baseline rho is below the semantic threshold")
    if baseline.p_value > float(semantic.get("maximum_p_value", 0.05)):
        errors.append("baseline p-value exceeds the semantic maximum")
    if baseline.approved_use not in APPROVED_JUDGE_USE_VOCAB:
        errors.append("baseline approved_use is unbounded")
    try:
        approved = datetime.fromisoformat(baseline.approved_at)
        expires = datetime.fromisoformat(baseline.expires_at)
        now = datetime.now(timezone.utc)
        if approved > now:
            errors.append("baseline approval timestamp is in the future")
        if expires <= now:
            errors.append("baseline is expired")
    except ValueError:
        errors.append("baseline expires_at is invalid")
    expected_digest = stamp_digest(
        ApprovedJudgeCalibrationBaseline(**{**baseline_payload, "deterministic_digest": ""})
    ).deterministic_digest
    if baseline.deterministic_digest != expected_digest:
        errors.append("baseline deterministic_digest is invalid")
    return errors


def main() -> int:
    artifact = configured_path(
        "APPS_RG_SPEARMAN_PROMOTION_ARTIFACT",
        PROMOTION_ARTIFACT_PATH,
    )
    return finish(
        "RG-SPEARMAN-PROMOTION",
        validate_promotion(artifact_path=artifact),
        fail_closed_env="APPS_RG_SPEARMAN_PROMOTION_FAIL_CLOSED",
    )


if __name__ == "__main__":
    raise SystemExit(main())
