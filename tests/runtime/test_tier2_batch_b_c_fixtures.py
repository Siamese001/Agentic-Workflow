"""Tier 2 Batch B/C fixture invariants.

Static, deterministic checks. Asserts the L3->L2 OTEL reference module,
the six trace fixtures (M-R), and the six replay fixture pairs created
for Batch B/C satisfy the contract declared in
TIER2_REMAINING_PROOF_GAPS.md.

This test does NOT execute replay machinery, does NOT emit OTEL spans,
does NOT run a proof harness, and does NOT mutate runtime state. It
inspects on-disk metadata only.
"""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Mapping

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


# --------------------------------------------------------------------------- #
# OTEL reference module — REQ-L3-L2-STEP-HANDOFF-001                           #
# --------------------------------------------------------------------------- #


def test_l3_l2_step_handoff_otel_ref_module() -> None:
    mod = importlib.import_module(
        "agentic_core.runtime.prove_requirements.tier2_otel_refs.l3_l2_step_handoff_spans"
    )
    assert mod.STEP1_REQ_ID == "REQ-L3-L2-STEP-HANDOFF-001"
    assert mod.EXPECTED_FAIL_REASON == "L3_L2_HANDOFF_CHECKPOINT_MISSING"
    span_names = mod.SPAN_NAMES
    assert isinstance(span_names, tuple) and span_names
    assert all(isinstance(s, str) and s for s in span_names)
    assert len(set(span_names)) == len(span_names)


def test_l3_l2_step_handoff_module_emits_no_spans() -> None:
    forbidden = (
        "opentelemetry.sdk",
        "trace.get_tracer(",
        "tracer.start_as_current_span",
        "tracer.start_span",
        ".set_attribute(",
        ".add_event(",
        ".end()",
    )
    path = (
        REPO_ROOT
        / "agentic_core"
        / "runtime"
        / "prove_requirements"
        / "tier2_otel_refs"
        / "l3_l2_step_handoff_spans.py"
    )
    text = path.read_text(encoding="utf-8")
    for needle in forbidden:
        assert needle not in text


# --------------------------------------------------------------------------- #
# Trace / artifact fixtures (dual-purpose: artifact + negative-control)        #
# --------------------------------------------------------------------------- #

TRACE_FIXTURES: Mapping[str, dict] = {
    "M_c0_no_execute": {
        "step1_req_id": "REQ-C0-NO-EXECUTE-001",
        "expected_fail_reason": "C0_EXECUTION_BLOCKED",
        "specifics": {
            "tool_invocation_count": 0,
            "model_invocation_count": 0,
            "c0_final_answer_emitted": False,
        },
    },
    "N_l5_hitl_reclearance": {
        "step1_req_id": "REQ-L5-HITL-RECLEARANCE-001",
        "expected_fail_reason": "HITL_RECLEARANCE_REQUIRED",
        "specifics": {
            "reclearance_required": True,
            "reclearance_present": False,
            "rejected": True,
        },
    },
    "O_l3_l2_step_handoff": {
        "step1_req_id": "REQ-L3-L2-STEP-HANDOFF-001",
        "expected_fail_reason": "L3_L2_HANDOFF_CHECKPOINT_MISSING",
        "specifics": {
            "checkpoint_required": True,
            "checkpoint_present": False,
            "resume_aborted": True,
        },
    },
    "P_l4_cache_state": {
        "step1_req_id": "REQ-L4-CACHE-STATE-001",
        "expected_fail_reason": "L4_CACHE_STATE_VIOLATION",
        "specifics": {
            "ad_hoc_invalidation_attempted": True,
            "rejected": True,
        },
    },
    "Q_l5_risk_tier_bands": {
        "step1_req_id": "REQ-L5-RISK-TIER-BANDS-001",
        "expected_fail_reason": "L5_RISK_TIER_POLICY_MISMATCH",
        "specifics": {
            "ad_hoc_score_attempted": True,
            "rejected": True,
        },
    },
    "R_u0_origin_trust_injection": {
        "step1_req_id": "REQ-U0-ORIGIN-TRUST-INJECTION-001",
        "expected_fail_reason": "ORIGIN_TRUST_LABEL_MISSING",
        "specifics": {
            "trust_label_present": False,
            "quarantined_or_rejected": True,
        },
    },
}


@pytest.mark.parametrize("scenario_key,expected", list(TRACE_FIXTURES.items()))
def test_trace_fixture_invariants(scenario_key: str, expected: dict) -> None:
    path = (
        REPO_ROOT
        / "artifacts"
        / "runtime"
        / "requirements_proof"
        / "traces"
        / f"scenario_{scenario_key}.json"
    )
    assert path.is_file(), f"missing trace fixture: {path}"
    data = json.loads(path.read_text(encoding="utf-8"))

    # Required base fields.
    for field in (
        "step1_req_id",
        "scenario_id",
        "expected_fail_reason",
        "invariant_digest",
        "gate_result",
        "evidence_refs",
        "blocker_target",
    ):
        assert field in data, f"missing field {field} in scenario_{scenario_key}.json"

    assert data["step1_req_id"] == expected["step1_req_id"]
    assert data["expected_fail_reason"] == expected["expected_fail_reason"]
    assert data["scenario_id"] == f"scenario_{scenario_key}"
    assert data["gate_result"] == "BLOCKED"
    assert data["blocker_target"] == expected["step1_req_id"]
    assert data["invariant_digest"].startswith("sha256:")

    evidence_refs = data["evidence_refs"]
    assert isinstance(evidence_refs, list) and evidence_refs
    assert all(isinstance(r, str) and r for r in evidence_refs)

    # Requirement-specific demonstration fields.
    for k, v in expected["specifics"].items():
        assert data.get(k) == v, f"{scenario_key}: expected {k}={v!r}, got {data.get(k)!r}"


# --------------------------------------------------------------------------- #
# Replay fixture pairs                                                         #
# --------------------------------------------------------------------------- #

REPLAY_PAIRS: Mapping[str, tuple[str, str]] = {
    "M_c0_no_execute": ("REQ-C0-NO-EXECUTE-001", "C0_EXECUTION_BLOCKED"),
    "N_l5_hitl_reclearance": ("REQ-L5-HITL-RECLEARANCE-001", "HITL_RECLEARANCE_REQUIRED"),
    "O_l3_l2_step_handoff": ("REQ-L3-L2-STEP-HANDOFF-001", "L3_L2_HANDOFF_CHECKPOINT_MISSING"),
    "P_l4_cache_state": ("REQ-L4-CACHE-STATE-001", "L4_CACHE_STATE_VIOLATION"),
    "Q_l5_risk_tier_bands": ("REQ-L5-RISK-TIER-BANDS-001", "L5_RISK_TIER_POLICY_MISMATCH"),
    "R_u0_origin_trust_injection": (
        "REQ-U0-ORIGIN-TRUST-INJECTION-001",
        "ORIGIN_TRUST_LABEL_MISSING",
    ),
}


@pytest.mark.parametrize("scenario_key,expected", list(REPLAY_PAIRS.items()))
def test_replay_pair_invariants(scenario_key: str, expected: tuple[str, str]) -> None:
    expected_req_id, expected_efr = expected
    base = REPO_ROOT / "artifacts" / "runtime" / "requirements_proof" / "replay"
    run_1 = base / f"replay_{scenario_key}_run_1.json"
    run_2 = base / f"replay_{scenario_key}_run_2.json"

    assert run_1.is_file() and run_2.is_file()

    d1 = json.loads(run_1.read_text(encoding="utf-8"))
    d2 = json.loads(run_2.read_text(encoding="utf-8"))

    for d, idx in ((d1, 1), (d2, 2)):
        for field in (
            "step1_req_id",
            "scenario_id",
            "expected_fail_reason",
            "invariant_digest",
            "replay_run_id",
        ):
            assert field in d, f"missing field {field} in run_{idx} for {scenario_key}"
        assert d["step1_req_id"] == expected_req_id
        assert d["scenario_id"] == f"scenario_{scenario_key}"
        assert d["expected_fail_reason"] == expected_efr
        assert d["replay_run_index"] == idx
        assert d["invariant_digest"].startswith("sha256:")

    assert d1["invariant_digest"] == d2["invariant_digest"]
    assert d1["replay_run_id"] != d2["replay_run_id"]


# --------------------------------------------------------------------------- #
# Tier 2 mapping wiring                                                        #
# --------------------------------------------------------------------------- #


def test_tier2_metadata_wires_batch_b_c_refs() -> None:
    from agentic_core.runtime.prove_requirements import tier2_step1_metadata as t2

    artifact = t2.ARTIFACT_REFERENCES
    replay = t2.REPLAY_REFERENCES
    negctrl = t2.NEGATIVE_CONTROL_REFERENCES
    otel = t2.OTEL_SPAN_REFERENCES

    # Artifact wiring (M, P, Q, R).
    assert any("scenario_M_c0_no_execute.json" in p for p in artifact["REQ-C0-NO-EXECUTE-001"])
    assert any("scenario_P_l4_cache_state.json" in p for p in artifact["REQ-L4-CACHE-STATE-001"])
    assert any("scenario_Q_l5_risk_tier_bands.json" in p for p in artifact["REQ-L5-RISK-TIER-BANDS-001"])
    assert any(
        "scenario_R_u0_origin_trust_injection.json" in p
        for p in artifact["REQ-U0-ORIGIN-TRUST-INJECTION-001"]
    )

    # Negative-control wiring (N, O, P, Q, R).
    assert any(
        "scenario_N_l5_hitl_reclearance.json" in p
        for p in negctrl["REQ-L5-HITL-RECLEARANCE-001"]
    )
    assert any(
        "scenario_O_l3_l2_step_handoff.json" in p for p in negctrl["REQ-L3-L2-STEP-HANDOFF-001"]
    )
    assert any("scenario_P_l4_cache_state.json" in p for p in negctrl["REQ-L4-CACHE-STATE-001"])
    assert any(
        "scenario_Q_l5_risk_tier_bands.json" in p for p in negctrl["REQ-L5-RISK-TIER-BANDS-001"]
    )
    assert any(
        "scenario_R_u0_origin_trust_injection.json" in p
        for p in negctrl["REQ-U0-ORIGIN-TRUST-INJECTION-001"]
    )

    # Replay-pair wiring (M, N, O, P, Q, R).
    assert any("replay_M_c0_no_execute_run_1.json" in p for p in replay["REQ-C0-NO-EXECUTE-001"])
    assert any("replay_M_c0_no_execute_run_2.json" in p for p in replay["REQ-C0-NO-EXECUTE-001"])
    assert any(
        "replay_N_l5_hitl_reclearance_run_1.json" in p
        for p in replay["REQ-L5-HITL-RECLEARANCE-001"]
    )
    assert any(
        "replay_O_l3_l2_step_handoff_run_1.json" in p for p in replay["REQ-L3-L2-STEP-HANDOFF-001"]
    )
    assert any("replay_P_l4_cache_state_run_1.json" in p for p in replay["REQ-L4-CACHE-STATE-001"])
    assert any(
        "replay_Q_l5_risk_tier_bands_run_1.json" in p for p in replay["REQ-L5-RISK-TIER-BANDS-001"]
    )
    assert any(
        "replay_R_u0_origin_trust_injection_run_1.json" in p
        for p in replay["REQ-U0-ORIGIN-TRUST-INJECTION-001"]
    )

    # OTEL wiring (L3->L2 step handoff).
    assert any(
        "l3_l2_step_handoff_spans.py" in p for p in otel["REQ-L3-L2-STEP-HANDOFF-001"]
    )
