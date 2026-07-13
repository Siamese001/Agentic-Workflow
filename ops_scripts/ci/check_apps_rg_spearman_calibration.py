"""RG-SPEARMAN-CALIBRATION: validate a digest-bound semantic result."""

from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agentic_core.L6_observability.shadow_eval._digest import compute_digest  # noqa: E402
from ops_scripts.ci._apps_rg_spearman_gate_common import (  # noqa: E402
    CALIBRATION_ARTIFACT_PATH,
    PROFILE_PATH,
    configured_path,
    finish,
    load_yaml,
)

_DIGEST_RE = re.compile(r"^(?:sha256:)?[0-9a-f]{64}$")


def validate_calibration(
    *,
    artifact_path: Path = CALIBRATION_ARTIFACT_PATH,
    profile_path: Path = PROFILE_PATH,
) -> list[str]:
    if not artifact_path.is_file():
        return [f"semantic calibration artifact is missing: {artifact_path}"]
    try:
        payload = json.loads(artifact_path.read_text(encoding="utf-8"))
        profile = load_yaml(profile_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [str(exc)]
    result: dict[str, Any] = payload.get("result") or {}
    errors: list[str] = []
    if payload.get("schema_version") != "apps-rg-spearman-calibration/v1":
        errors.append("calibration artifact schema_version is invalid")
    if payload.get("app_id") != profile.get("app_id"):
        errors.append("calibration artifact app_id differs from active profile")
    semantic = profile.get("semantic_alignment") or {}
    expected = {
        "judge_id": profile.get("judge_id"),
        "judge_version": profile.get("judge_version"),
        "rubric_hash": profile.get("rubric_hash"),
        "rubric_version": profile.get("rubric_version"),
        "provider_profile_ref": profile.get("provider_profile_ref"),
        "dataset_id": profile.get("dataset_id"),
        "dataset_version": profile.get("dataset_version"),
        "minimum_sample_size": semantic.get("minimum_samples"),
        "minimum_rho_threshold": semantic.get("minimum_spearman_rho"),
        "maximum_p_value": semantic.get("maximum_p_value"),
    }
    for key, value in expected.items():
        if result.get(key) != value:
            errors.append(f"result {key} differs from active profile")
    if result.get("status") != "PASS":
        errors.append("calibration status is not PASS")
    if result.get("label_source") != "human_semantic_review":
        errors.append("calibration does not use human semantic labels")
    if result.get("promotion_eligible") is not True:
        errors.append("calibration result is not promotion eligible")
    if result.get("sample_size_met") is not True:
        errors.append("minimum sample size is not met")
    if result.get("threshold_met") is not True:
        errors.append("rho/p-value threshold is not met")
    n = result.get("n")
    if not isinstance(n, int) or isinstance(n, bool) or n < int(semantic.get("minimum_samples", 40)):
        errors.append("result sample count is below the semantic minimum")
    for key in ("spearman_rho", "p_value"):
        value = result.get(key)
        if not isinstance(value, (int, float)) or not math.isfinite(float(value)):
            errors.append(f"result {key} is missing or non-finite")
    rho = result.get("spearman_rho")
    if isinstance(rho, (int, float)) and math.isfinite(float(rho)):
        if float(rho) < float(semantic.get("minimum_spearman_rho", 0.8)):
            errors.append("result rho is below the semantic threshold")
    p_value = result.get("p_value")
    if isinstance(p_value, (int, float)) and math.isfinite(float(p_value)):
        if float(p_value) > float(semantic.get("maximum_p_value", 0.05)):
            errors.append("result p-value exceeds the semantic maximum")
    for key in ("human_score_digest", "judge_score_digest", "deterministic_digest"):
        if not _DIGEST_RE.fullmatch(str(result.get(key, ""))):
            errors.append(f"result {key} is missing or is not SHA-256")
    for key in ("dataset_id", "dataset_version"):
        if not str(result.get(key, "")).strip():
            errors.append(f"result {key} is missing")
    if not result.get("calibration_source_refs"):
        errors.append("calibration source refs are missing")
    if result.get("deterministic_digest") != compute_digest(result):
        errors.append("calibration deterministic_digest is invalid")
    if result.get("status") == "PASS" and result.get("failure_reason_codes"):
        errors.append("passing calibration carries failure reason codes")
    return errors


def main() -> int:
    artifact = configured_path(
        "APPS_RG_SPEARMAN_CALIBRATION_ARTIFACT",
        CALIBRATION_ARTIFACT_PATH,
    )
    return finish(
        "RG-SPEARMAN-CALIBRATION",
        validate_calibration(artifact_path=artifact),
        fail_closed_env="APPS_RG_SPEARMAN_CALIBRATION_FAIL_CLOSED",
    )


if __name__ == "__main__":
    raise SystemExit(main())
