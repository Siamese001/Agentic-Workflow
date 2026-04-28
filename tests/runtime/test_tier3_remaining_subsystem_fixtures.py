"""Tier 3 non-RuntimeGates subsystem batches -- targeted fixture tests.

Static-evidence tests for the 17 non-RuntimeGates Tier 3 rows split across
three subsystem batches:

  Batch 1 -- L0 / L1 / U0 control-boundary rows (7):
    REQ-L0-NO-EXECUTE-001
    REQ-L0-GROUNDED-ACTION-HANDOFF-001
    REQ-U0-OBS-REPLAY-001
    REQ-U0-CHANNEL-VALIDATION-001
    REQ-L1-OBS-OTEL-001
    REQ-L1-PLAN-VALIDATION-SELF-REPAIR-001
    REQ-L1-AMBIGUITY-EVIDENCE-001

  Batch 2 -- C0 / PA / Exit (5):
    REQ-C0-NO-WRITE-001
    REQ-C0-PREFLIGHT-GROUNDING-001
    REQ-C0-GRAPH-RAG-001
    REQ-PA-VALIDATE-SLOT-CONTRACT-001
    REQ-EXIT-X1A-X1F-CHECKS-001

  Batch 3 -- L5 / L6 / UWG / E2E (5):
    REQ-L6-OBS-ANTI-BYPASS-001
    REQ-UWG-AUDIT-REPLAY-CONSISTENCY-001
    REQ-L5-REPLAY-AUDIT-CERT-001
    REQ-L5-EGRESS-PROVIDER-GOV-001
    REQ-E2E-FIXTURES-REPLAY-HARNESS-001

Each parametrized case asserts:

  1. The subsystem reference module exposes the required surface for the
     row (STEP1_REQ_IDS, EXPECTED_FAIL_REASONS, SPAN_NAMES_BY_REQ_ID,
     NEGATIVE_CONTROL_BY_REQ_ID, REQUIRED_ARTIFACT_FIELDS_BY_REQ_ID,
     SCENARIO_KEY_BY_REQ_ID, validate_contract).
  2. The scenario JSON fixture exists and carries step1_req_id,
     expected_fail_reason, gate_result == BLOCKED, evidence_refs,
     blocker_target == REQ_ID, plus every required artifact field.
  3. The replay pair exists, shares its invariant_digest, and matches
     the row's REQ_ID + EFR.
  4. validate_contract(req_id, payload) accepts the scenario fixture.
  5. validate_contract rejects a corrupted-step1_req_id payload (the
     negative control case for the row).

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

_BATCH1_MODULE = "agentic_core.runtime.prove_requirements.tier3_subsystem_refs.l0_l1_u0_refs"
_BATCH2_MODULE = "agentic_core.runtime.prove_requirements.tier3_subsystem_refs.c0_pa_exit_refs"
_BATCH3_MODULE = "agentic_core.runtime.prove_requirements.tier3_subsystem_refs.l5_l6_uwg_e2e_refs"

# (req_id, batch_module_dotted, scenario_key)
_CASES: Tuple[Tuple[str, str, str], ...] = (
    # Batch 1
    ("REQ-L0-NO-EXECUTE-001", _BATCH1_MODULE, "AE_l0_no_execute"),
    ("REQ-L0-GROUNDED-ACTION-HANDOFF-001", _BATCH1_MODULE, "AF_l0_grounded_action_handoff"),
    ("REQ-U0-OBS-REPLAY-001", _BATCH1_MODULE, "AG_u0_obs_replay"),
    ("REQ-U0-CHANNEL-VALIDATION-001", _BATCH1_MODULE, "AH_u0_channel_validation"),
    ("REQ-L1-OBS-OTEL-001", _BATCH1_MODULE, "AI_l1_obs_otel"),
    ("REQ-L1-PLAN-VALIDATION-SELF-REPAIR-001", _BATCH1_MODULE, "AJ_l1_plan_validation_self_repair"),
    ("REQ-L1-AMBIGUITY-EVIDENCE-001", _BATCH1_MODULE, "AK_l1_ambiguity_evidence"),
    # Batch 2
    ("REQ-C0-NO-WRITE-001", _BATCH2_MODULE, "AL_c0_no_write"),
    ("REQ-C0-PREFLIGHT-GROUNDING-001", _BATCH2_MODULE, "AM_c0_preflight_grounding"),
    ("REQ-C0-GRAPH-RAG-001", _BATCH2_MODULE, "AN_c0_graph_rag"),
    ("REQ-PA-VALIDATE-SLOT-CONTRACT-001", _BATCH2_MODULE, "AO_pa_validate_slot_contract"),
    ("REQ-EXIT-X1A-X1F-CHECKS-001", _BATCH2_MODULE, "AP_exit_x1a_x1f_checks"),
    # Batch 3
    ("REQ-L6-OBS-ANTI-BYPASS-001", _BATCH3_MODULE, "AQ_l6_obs_anti_bypass"),
    ("REQ-UWG-AUDIT-REPLAY-CONSISTENCY-001", _BATCH3_MODULE, "AR_uwg_audit_replay_consistency"),
    ("REQ-L5-REPLAY-AUDIT-CERT-001", _BATCH3_MODULE, "AS_l5_replay_audit_cert"),
    ("REQ-L5-EGRESS-PROVIDER-GOV-001", _BATCH3_MODULE, "AT_l5_egress_provider_gov"),
    ("REQ-E2E-FIXTURES-REPLAY-HARNESS-001", _BATCH3_MODULE, "AU_e2e_fixtures_replay_harness"),
)


@pytest.fixture(scope="module", autouse=True)
def _materialize_fixtures() -> None:
    """Materialize the AE..AU fixtures from a clean checkout."""
    _bootstrap.materialize()


def _load(p: Path) -> Mapping[str, Any]:
    assert p.is_file(), f"fixture missing: {p}"
    return json.loads(p.read_text(encoding="utf-8"))


@pytest.mark.parametrize(("req_id", "module_dotted", "scenario_key"), _CASES)
def test_subsystem_module_surface(req_id: str, module_dotted: str, scenario_key: str) -> None:
    mod = importlib.import_module(module_dotted)
    assert req_id in mod.STEP1_REQ_IDS
    assert mod.EXPECTED_FAIL_REASONS[req_id] == _t3.EXPECTED_FAIL_REASONS[req_id]
    assert isinstance(mod.SPAN_NAMES_BY_REQ_ID[req_id], tuple) and mod.SPAN_NAMES_BY_REQ_ID[req_id]
    assert isinstance(mod.NEGATIVE_CONTROL_BY_REQ_ID[req_id], str) and mod.NEGATIVE_CONTROL_BY_REQ_ID[req_id]
    assert isinstance(mod.REQUIRED_ARTIFACT_FIELDS_BY_REQ_ID[req_id], tuple) and mod.REQUIRED_ARTIFACT_FIELDS_BY_REQ_ID[req_id]
    assert mod.SCENARIO_KEY_BY_REQ_ID[req_id] == scenario_key
    assert callable(mod.validate_contract)


@pytest.mark.parametrize(("req_id", "module_dotted", "scenario_key"), _CASES)
def test_scenario_fixture_carries_required_fields(
    req_id: str, module_dotted: str, scenario_key: str
) -> None:
    mod = importlib.import_module(module_dotted)
    payload = _load(_TRACES_DIR / f"scenario_{scenario_key}.json")
    assert payload["step1_req_id"] == req_id
    assert payload["expected_fail_reason"] == mod.EXPECTED_FAIL_REASONS[req_id]
    assert payload["gate_result"] == "BLOCKED"
    assert payload.get("invariant_digest", "").startswith("sha256:")
    assert payload.get("evidence_refs"), "evidence_refs must be non-empty"
    assert payload.get("blocker_target") == req_id
    for field in mod.REQUIRED_ARTIFACT_FIELDS_BY_REQ_ID[req_id]:
        assert field in payload, f"required artifact field missing for {req_id}: {field}"


@pytest.mark.parametrize(("req_id", "module_dotted", "scenario_key"), _CASES)
def test_replay_pair_invariant_digest_matches(
    req_id: str, module_dotted: str, scenario_key: str
) -> None:
    run1 = _load(_REPLAY_DIR / f"replay_{scenario_key}_run_1.json")
    run2 = _load(_REPLAY_DIR / f"replay_{scenario_key}_run_2.json")
    assert run1["step1_req_id"] == req_id
    assert run2["step1_req_id"] == req_id
    mod = importlib.import_module(module_dotted)
    expected_efr = mod.EXPECTED_FAIL_REASONS[req_id]
    assert run1["expected_fail_reason"] == expected_efr
    assert run2["expected_fail_reason"] == expected_efr
    assert run1["invariant_digest"] == run2["invariant_digest"]
    assert run1.get("replay_run_id") and run2.get("replay_run_id")
    assert run1["replay_run_id"] != run2["replay_run_id"]


@pytest.mark.parametrize(("req_id", "module_dotted", "scenario_key"), _CASES)
def test_validate_contract_accepts_scenario(
    req_id: str, module_dotted: str, scenario_key: str
) -> None:
    mod = importlib.import_module(module_dotted)
    payload = _load(_TRACES_DIR / f"scenario_{scenario_key}.json")
    ok, errors = mod.validate_contract(req_id, payload)
    assert ok, f"validate_contract rejected scenario for {req_id}: {errors}"
    assert errors == []


@pytest.mark.parametrize(("req_id", "module_dotted", "scenario_key"), _CASES)
def test_validate_contract_rejects_negative_control(
    req_id: str, module_dotted: str, scenario_key: str
) -> None:
    """Corrupting step1_req_id must produce a contract error -- the
    NEGATIVE_CONTROL_BY_REQ_ID case for this row.
    """
    mod = importlib.import_module(module_dotted)
    payload = dict(_load(_TRACES_DIR / f"scenario_{scenario_key}.json"))
    payload["step1_req_id"] = "REQ-NEGATIVE-CONTROL-CORRUPT-XYZ"
    ok, errors = mod.validate_contract(req_id, payload)
    assert not ok
    assert any("step1_req_id" in e for e in errors)
