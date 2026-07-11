"""Pinned baseline validation shared by fresh E2E runtime and launcher."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

BASELINE_SCHEMA_VERSION = "apps_rg.e2e_baseline.v1"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_pinned_baseline(repo_root: Path, baseline_ref: Path) -> dict[str, str]:
    ref = baseline_ref if baseline_ref.is_absolute() else repo_root / baseline_ref
    try:
        payload = json.loads(ref.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"PINNED_BASELINE_UNREADABLE:{ref}:{exc}") from exc
    if not isinstance(payload, dict) or payload.get("schema_version") != BASELINE_SCHEMA_VERSION:
        raise RuntimeError(f"PINNED_BASELINE_SCHEMA_INVALID:{ref}")
    run_dir_text = str(payload.get("baseline_run_dir") or "").strip()
    expected_digest = str(payload.get("mandatory_output_sha256") or "").strip().lower()
    git_commit = str(payload.get("git_commit") or "").strip().lower()
    baseline_id = str(payload.get("baseline_id") or "").strip()
    target_company = str(payload.get("target_company") or "").strip()
    target_role = str(payload.get("target_role") or "").strip()
    expected_exit = str(payload.get("expected_exit_status") or "").strip().lower()
    expected_authorized = payload.get("expected_outcome_authorized")
    expected_x3 = str(payload.get("expected_x3_disposition") or "").strip()
    if not (
        run_dir_text
        and baseline_id
        and target_company
        and target_role
        and re.fullmatch(r"[0-9a-f]{40}", git_commit)
        and re.fullmatch(r"[0-9a-f]{64}", expected_digest)
        and expected_exit == "success"
        and expected_authorized is True
        and expected_x3
    ):
        raise RuntimeError(f"PINNED_BASELINE_IDENTITY_INVALID:{ref}")
    run_dir = (repo_root / run_dir_text).resolve()
    mandatory = run_dir / "APPS_RG_MANDATORY_RUN_OUTPUT.json"
    if not mandatory.is_file():
        raise RuntimeError(f"PINNED_BASELINE_ARTIFACT_MISSING:{mandatory}")
    observed_digest = _sha256(mandatory)
    if observed_digest != expected_digest:
        raise RuntimeError(
            f"PINNED_BASELINE_DIGEST_MISMATCH:expected={expected_digest}:observed={observed_digest}"
        )
    try:
        mandatory_payload = json.loads(mandatory.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"PINNED_BASELINE_MANDATORY_INVALID:{mandatory}:{exc}") from exc
    summary = (
        mandatory_payload.get("result_summary")
        if isinstance(mandatory_payload, dict) and isinstance(mandatory_payload.get("result_summary"), dict)
        else {}
    )
    observed_exit = str(summary.get("exit_status") or "").lower()
    observed_authorized = summary.get("outcome_authorized") is True
    observed_x3 = str(summary.get("x3_disposition") or "")
    if not (
        observed_exit == expected_exit
        and observed_authorized is expected_authorized
        and observed_x3 == expected_x3
    ):
        raise RuntimeError(
            "PINNED_BASELINE_EXPECTATION_MISMATCH:"
            f"exit={observed_exit}:authorized={observed_authorized}:x3={observed_x3}"
        )
    return {
        "baseline_id": baseline_id,
        "baseline_ref": str(ref.resolve()),
        "baseline_run_dir": str(run_dir),
        "mandatory_output_sha256": observed_digest,
        "git_commit": git_commit,
        "target_company": target_company,
        "target_role": target_role,
    }


__all__ = ["BASELINE_SCHEMA_VERSION", "validate_pinned_baseline"]
