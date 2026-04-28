"""Tier 2 Batch D/E fixture invariants.

Static, deterministic checks. Asserts the four boundary-guard reference
modules, the three Batch D/E OTEL reference modules, the four trace
fixtures (S-V), and the four replay fixture pairs satisfy the contract
declared in TIER2_REMAINING_PROOF_GAPS.md.

This test does NOT execute replay machinery, does NOT emit OTEL spans,
does NOT run a proof harness, does NOT execute boundary-guard runtime
behavior, and does NOT mutate runtime state. It inspects on-disk
metadata and calls only the pure validate_boundary_contract functions.
"""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Mapping

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


# --------------------------------------------------------------------------- #
# Boundary guard modules                                                       #
# --------------------------------------------------------------------------- #

GUARDS: Mapping[str, dict] = {
    "l4_retrieval_surface_guard": {
        "step1_req_id": "REQ-L4-RETRIEVAL-SURFACE-001",
        "expected_fail_reason": "L4_RETRIEVAL_SURFACE_VIOLATION",
        "negative_control_name": "scenario_S_l4_retrieval_surface",
        "good_payload": {
            "retrieval_surface_read_only": True,
            "non_uwg_mutation_attempted": True,
            "rejected": True,
        },
        "bad_payload": {
            "retrieval_surface_read_only": False,
            "non_uwg_mutation_attempted": True,
            "rejected": False,
        },
    },
    "l0_no_retrieval_guard": {
        "step1_req_id": "REQ-L0-NO-RETRIEVAL-001",
        "expected_fail_reason": "L0_RETRIEVAL_BLOCKED",
        "negative_control_name": "scenario_T_l0_no_retrieval",
        "good_payload": {
            "retrieval_attempted": True,
            "rejected": True,
            "retrieval_span_count": 0,
        },
        "bad_payload": {
            "retrieval_attempted": True,
            "rejected": False,
            "retrieval_span_count": 1,
        },
    },
    "l1_no_retrieval_guard": {
        "step1_req_id": "REQ-L1-NO-RETRIEVAL-001",
        "expected_fail_reason": "L1_RETRIEVAL_BLOCKED",
        "negative_control_name": "scenario_U_l1_no_retrieval",
        "good_payload": {
            "retrieval_attempted": True,
            "rejected": True,
            "retrieval_span_count": 0,
        },
        "bad_payload": {
            "retrieval_attempted": True,
            "rejected": False,
            "retrieval_span_count": 2,
        },
    },
    "l1_no_execute_guard": {
        "step1_req_id": "REQ-L1-NO-EXECUTE-001",
        "expected_fail_reason": "L1_EXECUTION_BLOCKED",
        "negative_control_name": "scenario_V_l1_no_execute",
        "good_payload": {
            "execution_attempted": True,
            "rejected": True,
            "tool_invocation_count": 0,
            "model_invocation_count": 0,
        },
        "bad_payload": {
            "execution_attempted": True,
            "rejected": False,
            "tool_invocation_count": 1,
            "model_invocation_count": 0,
        },
    },
}


@pytest.mark.parametrize("guard_name,expected", list(GUARDS.items()))
def test_boundary_guard_metadata(guard_name: str, expected: dict) -> None:
    mod = importlib.import_module(
        f"agentic_core.runtime.prove_requirements.tier2_boundary_guards.{guard_name}"
    )
    assert mod.STEP1_REQ_ID == expected["step1_req_id"]
    assert mod.EXPECTED_FAIL_REASON == expected["expected_fail_reason"]
    assert mod.GUARD_NAME == guard_name
    assert mod.NEGATIVE_CONTROL_NAME == expected["negative_control_name"]
    assert isinstance(mod.FORBIDDEN_CAPABILITIES, tuple) and mod.FORBIDDEN_CAPABILITIES
    assert all(isinstance(c, str) and c for c in mod.FORBIDDEN_CAPABILITIES)
    assert isinstance(mod.ALLOWED_OUTPUTS, tuple) and mod.ALLOWED_OUTPUTS
    assert all(isinstance(o, str) and o for o in mod.ALLOWED_OUTPUTS)
    # Disjoint sets — forbidden vs allowed do not overlap.
    assert set(mod.FORBIDDEN_CAPABILITIES).isdisjoint(set(mod.ALLOWED_OUTPUTS))


@pytest.mark.parametrize("guard_name,expected", list(GUARDS.items()))
def test_boundary_guard_validate_function(guard_name: str, expected: dict) -> None:
    mod = importlib.import_module(
        f"agentic_core.runtime.prove_requirements.tier2_boundary_guards.{guard_name}"
    )
    ok, viols = mod.validate_boundary_contract(expected["good_payload"])
    assert ok is True
    assert viols == []
    bad_ok, bad_viols = mod.validate_boundary_contract(expected["bad_payload"])
    assert bad_ok is False
    assert bad_viols
    # Non-mapping input -> rejected.
    nm_ok, nm_viols = mod.validate_boundary_contract("not a mapping")  # type: ignore[arg-type]
    assert nm_ok is False
    assert nm_viols == ["payload_not_mapping"]


@pytest.mark.parametrize("guard_name", list(GUARDS.keys()))
def test_boundary_guard_module_no_runtime_calls(guard_name: str) -> None:
    forbidden = (
        "subprocess.",
        "requests.",
        "httpx.",
        "open(",
        "os.system",
        "redis",
        "sqlite3.connect",
        "opentelemetry.sdk",
    )
    path = (
        REPO_ROOT
        / "agentic_core"
        / "runtime"
        / "prove_requirements"
        / "tier2_boundary_guards"
        / f"{guard_name}.py"
    )
    text = path.read_text(encoding="utf-8")
    for needle in forbidden:
        assert needle not in text, f"{guard_name}: forbidden token {needle!r}"


# --------------------------------------------------------------------------- #
# OTEL reference modules (L0/L1)                                               #
# --------------------------------------------------------------------------- #

OTEL_REFS: Mapping[str, tuple[str, str]] = {
    "l0_no_retrieval_spans": ("REQ-L0-NO-RETRIEVAL-001", "L0_RETRIEVAL_BLOCKED"),
    "l1_no_retrieval_spans": ("REQ-L1-NO-RETRIEVAL-001", "L1_RETRIEVAL_BLOCKED"),
    "l1_no_execute_spans": ("REQ-L1-NO-EXECUTE-001", "L1_EXECUTION_BLOCKED"),
}


@pytest.mark.parametrize("mod_name,expected", list(OTEL_REFS.items()))
def test_otel_ref_module(mod_name: str, expected: tuple[str, str]) -> None:
    expected_req_id, expected_efr = expected
    mod = importlib.import_module(
        f"agentic_core.runtime.prove_requirements.tier2_otel_refs.{mod_name}"
    )
    assert mod.STEP1_REQ_ID == expected_req_id
    assert mod.EXPECTED_FAIL_REASON == expected_efr
    span_names = mod.SPAN_NAMES
    assert isinstance(span_names, tuple) and span_names
    assert all(isinstance(s, str) and s for s in span_names)
    assert len(set(span_names)) == len(span_names)


@pytest.mark.parametrize("mod_name", list(OTEL_REFS.keys()))
def test_otel_ref_module_emits_no_spans(mod_name: str) -> None:
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
        / f"{mod_name}.py"
    )
    text = path.read_text(encoding="utf-8")
    for needle in forbidden:
        assert needle not in text


# --------------------------------------------------------------------------- #
# Trace / artifact fixtures (dual-purpose: artifact + negative-control)        #
# --------------------------------------------------------------------------- #

TRACE_FIXTURES: Mapping[str, dict] = {
    "S_l4_retrieval_surface": {
        "step1_req_id": "REQ-L4-RETRIEVAL-SURFACE-001",
        "expected_fail_reason": "L4_RETRIEVAL_SURFACE_VIOLATION",
        "specifics": {
            "retrieval_surface_read_only": True,
            "non_uwg_mutation_attempted": True,
            "rejected": True,
        },
    },
    "T_l0_no_retrieval": {
        "step1_req_id": "REQ-L0-NO-RETRIEVAL-001",
        "expected_fail_reason": "L0_RETRIEVAL_BLOCKED",
        "specifics": {
            "retrieval_attempted": True,
            "rejected": True,
            "retrieval_span_count": 0,
        },
    },
    "U_l1_no_retrieval": {
        "step1_req_id": "REQ-L1-NO-RETRIEVAL-001",
        "expected_fail_reason": "L1_RETRIEVAL_BLOCKED",
        "specifics": {
            "retrieval_attempted": True,
            "rejected": True,
            "retrieval_span_count": 0,
        },
    },
    "V_l1_no_execute": {
        "step1_req_id": "REQ-L1-NO-EXECUTE-001",
        "expected_fail_reason": "L1_EXECUTION_BLOCKED",
        "specifics": {
            "execution_attempted": True,
            "rejected": True,
            "tool_invocation_count": 0,
            "model_invocation_count": 0,
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

    for k, v in expected["specifics"].items():
        assert data.get(k) == v, f"{scenario_key}: expected {k}={v!r}, got {data.get(k)!r}"


# --------------------------------------------------------------------------- #
# Replay fixture pairs                                                         #
# --------------------------------------------------------------------------- #

REPLAY_PAIRS: Mapping[str, tuple[str, str]] = {
    "S_l4_retrieval_surface": ("REQ-L4-RETRIEVAL-SURFACE-001", "L4_RETRIEVAL_SURFACE_VIOLATION"),
    "T_l0_no_retrieval": ("REQ-L0-NO-RETRIEVAL-001", "L0_RETRIEVAL_BLOCKED"),
    "U_l1_no_retrieval": ("REQ-L1-NO-RETRIEVAL-001", "L1_RETRIEVAL_BLOCKED"),
    "V_l1_no_execute": ("REQ-L1-NO-EXECUTE-001", "L1_EXECUTION_BLOCKED"),
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


def test_tier2_metadata_wires_batch_d_e_refs() -> None:
    from agentic_core.runtime.prove_requirements import tier2_step1_metadata as t2

    code = t2.CODE_REFERENCES
    validator = t2.VALIDATOR_REFERENCES
    test_ = t2.TEST_REFERENCES
    artifact = t2.ARTIFACT_REFERENCES
    replay = t2.REPLAY_REFERENCES
    otel = t2.OTEL_SPAN_REFERENCES
    negctrl = t2.NEGATIVE_CONTROL_REFERENCES

    targets = {
        "REQ-L4-RETRIEVAL-SURFACE-001": ("l4_retrieval_surface_guard", "S_l4_retrieval_surface"),
        "REQ-L0-NO-RETRIEVAL-001": ("l0_no_retrieval_guard", "T_l0_no_retrieval"),
        "REQ-L1-NO-RETRIEVAL-001": ("l1_no_retrieval_guard", "U_l1_no_retrieval"),
        "REQ-L1-NO-EXECUTE-001": ("l1_no_execute_guard", "V_l1_no_execute"),
    }

    for req_id, (guard, scen) in targets.items():
        # Boundary guard wired as code + validator.
        assert any(f"{guard}.py" in p for p in code[req_id]), f"{req_id} missing code ref"
        assert any(f"{guard}.py" in p for p in validator[req_id]), f"{req_id} missing validator ref"
        # Test ref wired to this fixture file.
        assert any("test_tier2_batch_d_e_fixtures.py" in p for p in test_[req_id])
        # Artifact + replay wiring.
        assert any(f"scenario_{scen}.json" in p for p in artifact[req_id])
        assert any(f"replay_{scen}_run_1.json" in p for p in replay[req_id])
        assert any(f"replay_{scen}_run_2.json" in p for p in replay[req_id])

    # OTEL ref modules (L0/L1 only).
    assert any("l0_no_retrieval_spans.py" in p for p in otel["REQ-L0-NO-RETRIEVAL-001"])
    assert any("l1_no_retrieval_spans.py" in p for p in otel["REQ-L1-NO-RETRIEVAL-001"])
    assert any("l1_no_execute_spans.py" in p for p in otel["REQ-L1-NO-EXECUTE-001"])

    # Negative-control wiring (L0/L1; L4 negctrl pre-existing).
    assert any("scenario_T_l0_no_retrieval.json" in p for p in negctrl["REQ-L0-NO-RETRIEVAL-001"])
    assert any("scenario_U_l1_no_retrieval.json" in p for p in negctrl["REQ-L1-NO-RETRIEVAL-001"])
    assert any("scenario_V_l1_no_execute.json" in p for p in negctrl["REQ-L1-NO-EXECUTE-001"])
