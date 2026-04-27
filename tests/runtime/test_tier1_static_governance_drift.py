"""Targeted Tier 1 fixture validation for REQ-L5-STATIC-GOV-DRIFT-001.

Validates ONLY the metadata shape and integrity of the static-governance-drift
fixture artifact and its deterministic replay pair. Does NOT execute any
runtime governance-drift detector, OTEL exporter, or proof harness.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PROOF = REPO_ROOT / "artifacts" / "runtime" / "requirements_proof"
ARTIFACT = PROOF / "traces" / "scenario_I_static_governance_drift.json"
REPLAY_1 = PROOF / "replay" / "replay_I_static_governance_drift_run_1.json"
REPLAY_2 = PROOF / "replay" / "replay_I_static_governance_drift_run_2.json"

REQ_ID = "REQ-L5-STATIC-GOV-DRIFT-001"
EFR = "STATIC_GOVERNANCE_DRIFT_DETECTED"


def _load(path: Path) -> dict:
    assert path.exists(), f"Fixture missing: {path}"
    payload: dict = json.loads(path.read_text(encoding="utf-8"))
    return payload


def test_artifact_exists_and_matches_requirement() -> None:
    payload = _load(ARTIFACT)
    assert payload["step1_req_id"] == REQ_ID
    assert payload["expected_fail_reason"] == EFR
    assert payload["drift_detected"] is True
    assert payload["gate_result"] == "BLOCKED"


def test_replay_pair_exists() -> None:
    assert REPLAY_1.exists()
    assert REPLAY_2.exists()


def test_replay_pair_matches_requirement() -> None:
    r1 = _load(REPLAY_1)
    r2 = _load(REPLAY_2)
    assert r1["step1_req_id"] == REQ_ID
    assert r2["step1_req_id"] == REQ_ID


def test_replay_pair_invariant_digest_matches() -> None:
    a = _load(ARTIFACT)
    r1 = _load(REPLAY_1)
    r2 = _load(REPLAY_2)
    assert a["invariant_digest"] == r1["invariant_digest"] == r2["invariant_digest"]
    assert r1["replay_run_id"] != r2["replay_run_id"]


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
