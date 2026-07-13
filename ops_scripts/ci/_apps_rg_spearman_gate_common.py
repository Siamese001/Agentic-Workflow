"""Shared reporting helpers for apps_rg Spearman CI gates."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
PROFILE_PATH = REPO_ROOT / "apps_rg/config/domain_contract/judge_calibration_profile.yaml"
ROSTER_PATH = REPO_ROOT / "apps_rg/config/domain_contract/grader_roster.yaml"
PROVIDERS_PATH = REPO_ROOT / "apps_rg/config/provider_profiles.yaml"
DATASET_PATH = REPO_ROOT / "apps_eval/fixtures/holdout/apps_rg_executive_positioning.v1.jsonl"
CALIBRATION_ARTIFACT_PATH = REPO_ROOT / "artifacts/calibration/apps_rg_executive_positioning.json"
PROMOTION_ARTIFACT_PATH = REPO_ROOT / "artifacts/calibration/apps_rg_approved_baseline.json"


def load_yaml(path: Path) -> Any:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, (dict, list)):
        raise ValueError(f"expected YAML mapping or list in {path}")
    return payload


def configured_path(env_name: str, default: Path) -> Path:
    raw = os.environ.get(env_name, "").strip()
    if not raw:
        return default
    path = Path(raw)
    return path if path.is_absolute() else REPO_ROOT / path


def finish(gate_id: str, errors: list[str], *, fail_closed_env: str) -> int:
    fail_closed = os.environ.get(fail_closed_env, "").strip() == "1"
    if not errors:
        print(f"[{gate_id}] PASS")
        return 0
    posture = "BLOCKING" if fail_closed else "ADVISORY"
    print(f"[{gate_id}] {posture}: {len(errors)} finding(s)")
    for error in errors:
        print(f"  - {error}")
    if not fail_closed:
        print(f"[{gate_id}] set {fail_closed_env}=1 to fail closed")
    return 1 if fail_closed else 0


__all__ = [
    "CALIBRATION_ARTIFACT_PATH",
    "DATASET_PATH",
    "PROFILE_PATH",
    "PROMOTION_ARTIFACT_PATH",
    "PROVIDERS_PATH",
    "REPO_ROOT",
    "ROSTER_PATH",
    "configured_path",
    "finish",
    "load_yaml",
]
