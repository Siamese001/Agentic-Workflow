"""Tier 3 Runtime Gates cluster — targeted fixture tests.

Static-evidence tests for the 8 Runtime Gates rows in Tier 3:

  - REQ-GATE-G01-G05-INGRESS-001
  - REQ-GATE-G06-G10-HITL-ROUTE-001
  - REQ-GATE-G11-G15-TOOL-MODEL-001
  - REQ-GATE-G16-G20-MEMORY-WORKFLOW-001
  - REQ-GATE-G21-G24-OUTPUT-REPLAY-001
  - REQ-GATE-G25-G29-EXIT-WRITE-001
  - REQ-GATE-NO-OVERLAP-WITH-EXIT-001
  - REQ-GATE-NO-OVERLAP-WITH-L5-001

Each parametrized case asserts:

  1. The static reference module exposes the required surface
     (STEP1_REQ_ID, EXPECTED_FAIL_REASON, GATE_FAMILY/RANGE, GATE_IDS,
     SPAN_NAMES, NEGATIVE_CONTROL_NAME, REQUIRED_ARTIFACT_FIELDS,
     validate_gate_contract).
  2. The scenario JSON fixture exists, parses, and carries the required
     artifact fields, step1_req_id, expected_fail_reason, gate_result.
  3. The two replay JSON fixtures exist, share an invariant_digest, and
     match the row's step1_req_id and expected_fail_reason.
  4. The reference module's validate_gate_contract() accepts the
     scenario payload (returns True with no errors).
  5. validate_gate_contract() rejects an obvious negative control
     (corrupted step1_req_id) with errors.

No runtime services are called. No tool is executed. No OTEL span is
emitted. No replay machinery is run. Pure deterministic JSON + module
introspection.
"""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Any, Mapping, Tuple

import pytest

from agentic_core.runtime.prove_requirements import (
    tier3_step1_metadata as _t3,
    tier_fixture_bootstrap as _bootstrap,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
_TRACES_DIR = REPO_ROOT / "artifacts" / "runtime" / "requirements_proof" / "traces"
_REPLAY_DIR = REPO_ROOT / "artifacts" / "runtime" / "requirements_proof" / "replay"

# (req_id, ref_module_dotted, scenario_key)
_CASES: Tuple[Tuple[str, str, str], ...] = (
    (
        "REQ-GATE-G01-G05-INGRESS-001",
        "agentic_core.runtime.prove_requirements.tier3_runtime_gate_refs.g01_g05_ingress_refs",
        "W_gate_g01_g05_ingress",
    ),
    (
        "REQ-GATE-G06-G10-HITL-ROUTE-001",
        "agentic_core.runtime.prove_requirements.tier3_runtime_gate_refs.g06_g10_hitl_route_refs",
        "X_gate_g06_g10_hitl_route",
    ),
    (
        "REQ-GATE-G11-G15-TOOL-MODEL-001",
        "agentic_core.runtime.prove_requirements.tier3_runtime_gate_refs.g11_g15_tool_model_refs",
        "Y_gate_g11_g15_tool_model",
    ),
    (
        "REQ-GATE-G16-G20-MEMORY-WORKFLOW-001",
        "agentic_core.runtime.prove_requirements.tier3_runtime_gate_refs.g16_g20_memory_workflow_refs",
        "Z_gate_g16_g20_memory_workflow",
    ),
    (
        "REQ-GATE-G21-G24-OUTPUT-REPLAY-001",
        "agentic_core.runtime.prove_requirements.tier3_runtime_gate_refs.g21_g24_output_replay_refs",
        "AA_gate_g21_g24_output_replay",
    ),
    (
        "REQ-GATE-G25-G29-EXIT-WRITE-001",
        "agentic_core.runtime.prove_requirements.tier3_runtime_gate_refs.g25_g29_exit_write_refs",
        "AB_gate_g25_g29_exit_write",
    ),
    (
        "REQ-GATE-NO-OVERLAP-WITH-EXIT-001",
        "agentic_core.runtime.prove_requirements.tier3_runtime_gate_refs.gate_no_overlap_exit_refs",
        "AC_gate_no_overlap_exit",
    ),
    (
        "REQ-GATE-NO-OVERLAP-WITH-L5-001",
        "agentic_core.runtime.prove_requirements.tier3_runtime_gate_refs.gate_no_overlap_l5_refs",
        "AD_gate_no_overlap_l5",
    ),
)


@pytest.fixture(scope="module", autouse=True)
def _materialize_fixtures() -> None:
    """Materialize the W..AD fixtures from a clean checkout."""
    _bootstrap.materialize()


def _load(p: Path) -> Mapping[str, Any]:
    assert p.is_file(), f"fixture missing: {p}"
    return json.loads(p.read_text(encoding="utf-8"))


@pytest.mark.parametrize(("req_id", "module_dotted", "scenario_key"), _CASES)
def test_reference_module_surface(req_id: str, module_dotted: str, scenario_key: str) -> None:
    mod = importlib.import_module(module_dotted)
    assert mod.STEP1_REQ_ID == req_id
    # EXPECTED_FAIL_REASON must match the metadata module's seed.
    assert mod.EXPECTED_FAIL_REASON == _t3.EXPECTED_FAIL_REASONS[req_id]
    assert isinstance(mod.GATE_FAMILY, str) and mod.GATE_FAMILY
    assert isinstance(mod.GATE_RANGE, str) and mod.GATE_RANGE
    assert isinstance(mod.GATE_IDS, tuple) and mod.GATE_IDS
    assert isinstance(mod.SPAN_NAMES, tuple) and mod.SPAN_NAMES
    assert isinstance(mod.NEGATIVE_CONTROL_NAME, str) and mod.NEGATIVE_CONTROL_NAME
    assert isinstance(mod.REQUIRED_ARTIFACT_FIELDS, tuple) and mod.REQUIRED_ARTIFACT_FIELDS
    assert callable(mod.validate_gate_contract)
    assert mod.SCENARIO_KEY == scenario_key


@pytest.mark.parametrize(("req_id", "module_dotted", "scenario_key"), _CASES)
def test_scenario_fixture_carries_required_fields(
    req_id: str, module_dotted: str, scenario_key: str
) -> None:
    mod = importlib.import_module(module_dotted)
    payload = _load(_TRACES_DIR / f"scenario_{scenario_key}.json")
    assert payload["step1_req_id"] == req_id
    assert payload["expected_fail_reason"] == mod.EXPECTED_FAIL_REASON
    assert payload["gate_result"] == "BLOCKED"
    assert payload.get("invariant_digest", "").startswith("sha256:")
    assert payload.get("evidence_refs"), "evidence_refs must be non-empty"
    # Either gate_family or gate_range must be present.
    assert payload.get("gate_family") or payload.get("gate_range")
    # blocker_target must match the row.
    assert payload.get("blocker_target") == req_id
    # Every REQUIRED_ARTIFACT_FIELDS entry must be present in the payload.
    for field in mod.REQUIRED_ARTIFACT_FIELDS:
        assert field in payload, f"required artifact field missing: {field}"


@pytest.mark.parametrize(("req_id", "module_dotted", "scenario_key"), _CASES)
def test_replay_pair_invariant_digest_matches(
    req_id: str, module_dotted: str, scenario_key: str
) -> None:
    run1 = _load(_REPLAY_DIR / f"replay_{scenario_key}_run_1.json")
    run2 = _load(_REPLAY_DIR / f"replay_{scenario_key}_run_2.json")
    assert run1["step1_req_id"] == req_id
    assert run2["step1_req_id"] == req_id
    mod = importlib.import_module(module_dotted)
    assert run1["expected_fail_reason"] == mod.EXPECTED_FAIL_REASON
    assert run2["expected_fail_reason"] == mod.EXPECTED_FAIL_REASON
    assert run1["invariant_digest"] == run2["invariant_digest"]
    assert run1.get("replay_run_id") and run2.get("replay_run_id")
    assert run1["replay_run_id"] != run2["replay_run_id"]


@pytest.mark.parametrize(("req_id", "module_dotted", "scenario_key"), _CASES)
def test_validate_gate_contract_accepts_scenario(
    req_id: str, module_dotted: str, scenario_key: str
) -> None:
    mod = importlib.import_module(module_dotted)
    payload = _load(_TRACES_DIR / f"scenario_{scenario_key}.json")
    ok, errors = mod.validate_gate_contract(payload)
    assert ok, f"validate_gate_contract rejected fixture: {errors}"
    assert errors == []


@pytest.mark.parametrize(("req_id", "module_dotted", "scenario_key"), _CASES)
def test_validate_gate_contract_rejects_negative_control(
    req_id: str, module_dotted: str, scenario_key: str
) -> None:
    """Corrupting step1_req_id must produce a contract error — the
    NEGATIVE_CONTROL_NAME case for this gate band.
    """
    mod = importlib.import_module(module_dotted)
    payload = dict(_load(_TRACES_DIR / f"scenario_{scenario_key}.json"))
    payload["step1_req_id"] = "REQ-NEGATIVE-CONTROL-CORRUPT-XYZ"
    ok, errors = mod.validate_gate_contract(payload)
    assert not ok
    assert any("step1_req_id" in e for e in errors)
