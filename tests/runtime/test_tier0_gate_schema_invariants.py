"""Tier 0 gate-schema invariant validators.

Narrowly scoped tests for two Tier 0 requirements:

  - ``REQ-GATE-SCHEMA-UNKNOWN-NOT-PASS-001`` — UNKNOWN GateVerdict MUST NOT
    be aggregated as PASS.
  - ``REQ-GATE-SCHEMA-NA-REQUIRES-REASON-001`` — NOT_APPLICABLE GateVerdict
    MUST carry a non-empty ``na_reason``; missing reason is a schema
    violation that MUST be rejected.

These tests validate the static fixture artifacts and replay bundles only.
They do not start runtime services, do not execute live gates, and do not
invoke proof harnesses, OTEL exporters, or full replay machinery.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

_PROOF_BASE = Path("artifacts/runtime/requirements_proof")
_TRACES = _PROOF_BASE / "traces"
_REPLAY = _PROOF_BASE / "replay"


# ----- REQ-GATE-SCHEMA-UNKNOWN-NOT-PASS-001 --------------------------------


def test_scenario_F_unknown_gate_never_treated_as_pass() -> None:
    payload = json.loads(
        (_TRACES / "scenario_F_gate_schema_unknown_not_pass.json").read_text(encoding="utf-8")
    )
    assert payload["step1_req_id"] == "REQ-GATE-SCHEMA-UNKNOWN-NOT-PASS-001"
    assert payload["expected_fail_reason"] == "UNKNOWN_GATE_RESULT_NOT_PASS"
    assert payload["x2_aggregate"]["any_unknown"] is True
    assert payload["x2_aggregate"]["any_unknown_treated_as_pass"] is False
    for d in payload["gate_decisions"]:
        if d["verdict"] == "UNKNOWN":
            assert d["treated_as_pass"] is False, f"UNKNOWN must not be treated_as_pass: {d}"


@pytest.mark.parametrize(
    "fname",
    [
        "replay_F_gate_schema_unknown_not_pass_run_1.json",
        "replay_F_gate_schema_unknown_not_pass_run_2.json",
    ],
)
def test_replay_F_carries_required_fields(fname: str) -> None:
    payload = json.loads((_REPLAY / fname).read_text(encoding="utf-8"))
    assert payload["step1_req_id"] == "REQ-GATE-SCHEMA-UNKNOWN-NOT-PASS-001"
    assert payload["expected_fail_reason"] == "UNKNOWN_GATE_RESULT_NOT_PASS"
    assert payload["invariant_digest"].startswith("sha256:")
    assert payload["route_id"]
    assert payload["exit_disposition"]
    assert payload["gate_verdicts_summary"]["UNKNOWN_treated_as_pass_count"] == 0


def test_replay_F_pair_digest_is_stable() -> None:
    p1 = json.loads(
        (_REPLAY / "replay_F_gate_schema_unknown_not_pass_run_1.json").read_text(encoding="utf-8")
    )
    p2 = json.loads(
        (_REPLAY / "replay_F_gate_schema_unknown_not_pass_run_2.json").read_text(encoding="utf-8")
    )
    assert p1["invariant_digest"] == p2["invariant_digest"]
    assert p1["route_id"] == p2["route_id"]
    assert p1["exit_disposition"] == p2["exit_disposition"]


# ----- REQ-GATE-SCHEMA-NA-REQUIRES-REASON-001 ------------------------------


def test_scenario_G_na_without_reason_is_rejected() -> None:
    payload = json.loads(
        (_TRACES / "scenario_G_gate_schema_na_requires_reason.json").read_text(encoding="utf-8")
    )
    assert payload["step1_req_id"] == "REQ-GATE-SCHEMA-NA-REQUIRES-REASON-001"
    assert payload["expected_fail_reason"] == "NOT_APPLICABLE_REASON_MISSING"
    saw_missing = False
    for d in payload["gate_decisions"]:
        if d["verdict"] == "NOT_APPLICABLE":
            if d.get("na_reason"):
                assert d["valid"] is True
            else:
                assert d["valid"] is False, f"NA without na_reason must be invalid: {d}"
                assert "schema_violation" in d.get("rejection_reason", "")
                saw_missing = True
    assert saw_missing, "fixture must include at least one NA-without-reason case"


@pytest.mark.parametrize(
    "fname",
    [
        "replay_G_gate_schema_na_requires_reason_run_1.json",
        "replay_G_gate_schema_na_requires_reason_run_2.json",
    ],
)
def test_replay_G_carries_required_fields(fname: str) -> None:
    payload = json.loads((_REPLAY / fname).read_text(encoding="utf-8"))
    assert payload["step1_req_id"] == "REQ-GATE-SCHEMA-NA-REQUIRES-REASON-001"
    assert payload["expected_fail_reason"] == "NOT_APPLICABLE_REASON_MISSING"
    assert payload["invariant_digest"].startswith("sha256:")
    assert payload["route_id"]
    assert payload["exit_disposition"]
    summary = payload["gate_verdicts_summary"]
    assert summary["NOT_APPLICABLE_without_reason_count"] >= 1
    assert summary["rejected_for_missing_reason_count"] == summary["NOT_APPLICABLE_without_reason_count"]


def test_replay_G_pair_digest_is_stable() -> None:
    p1 = json.loads(
        (_REPLAY / "replay_G_gate_schema_na_requires_reason_run_1.json").read_text(encoding="utf-8")
    )
    p2 = json.loads(
        (_REPLAY / "replay_G_gate_schema_na_requires_reason_run_2.json").read_text(encoding="utf-8")
    )
    assert p1["invariant_digest"] == p2["invariant_digest"]
    assert p1["route_id"] == p2["route_id"]
    assert p1["exit_disposition"] == p2["exit_disposition"]
