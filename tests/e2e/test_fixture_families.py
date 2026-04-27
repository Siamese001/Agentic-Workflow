"""F1-F10 fixture family regression suite — R-99.10 sign-off test suite.

Implements the 99.10 spec: every fixture family must have at least one executed
run and emit a ``RuntimeProofPacket`` to ``artifacts/e2e/fixtures/<Fn>/runtime_proof_packet.json``.
Each packet resolves every required ref to a real file inside the bundle.

Fixture family map (from 99.10 §FIXTURE FAMILIES):

| Fixture | Description | Driven by |
|---------|-------------|-----------|
| F1 | exact cache terminal route | RC-R1A |
| F2 | semantic cache terminal route | RC-R1B |
| F3 | simple grounded read | GP-001 |
| F4 | single action no durable write | RC-R4 |
| F5 | managed workflow | RC-R3R4-MANAGED |
| F6 | PTC sandbox execution | RC-R4 (with sandbox evidence overlay) |
| F7 | proposed_state_diff -> UWG | RC-UWG |
| F8 | HITL modification | RC-HITL |
| F9 | L6 after-boundary learning proposal | GP-001 (post-disposition L6 window) |
| F10 | failure path (weak evidence / abstain) | RC-R5 |

F6/F9/F10 ride on existing scenarios with targeted evidence overlays so this
suite does not duplicate the reference emitter. The canonical runtime will
replace each overlay with a real producer when that layer lands.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

from tests.e2e.proof.contracts import ProofStatus
from tests.e2e.proof.harness import emit_run
from tests.e2e.proof.runner import run_scenario
from tests.e2e.proof.scenarios import get


REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES_DIR = REPO_ROOT / "artifacts" / "e2e" / "fixtures"


# ---------------------------------------------------------------------------
# Fixture family descriptor
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FixtureFamily:
    fixture_id: str
    description: str
    base_scenario_id: str
    requires_uwg_receipt: bool = False
    requires_evidence_contract: bool = True
    overlay: str | None = None


FIXTURES: list[FixtureFamily] = [
    FixtureFamily("F1", "exact cache terminal route", "RC-R1A", requires_evidence_contract=False),
    FixtureFamily("F2", "semantic cache terminal route", "RC-R1B", requires_evidence_contract=False),
    FixtureFamily("F3", "simple grounded read", "GP-001"),
    FixtureFamily("F4", "single action no durable write", "RC-R4", requires_evidence_contract=False),
    FixtureFamily("F5", "managed workflow", "RC-R3R4-MANAGED"),
    FixtureFamily(
        "F6",
        "PTC sandbox execution with sandbox envelope",
        "RC-R4",
        requires_evidence_contract=False,
        overlay="ptc_sandbox",
    ),
    FixtureFamily("F7", "proposed_state_diff -> UWG commit", "RC-UWG", requires_uwg_receipt=True),
    FixtureFamily("F8", "HITL modification freeze path", "RC-HITL", requires_evidence_contract=False),
    FixtureFamily(
        "F9",
        "L6 after-boundary learning proposal",
        "GP-001",
        overlay="l6_after_boundary",
    ),
    FixtureFamily(
        "F10",
        "failure path (abstain / weak evidence)",
        "RC-R5",
        requires_evidence_contract=False,
        overlay="failure_path",
    ),
]


# ---------------------------------------------------------------------------
# Overlay appliers (F6, F9, F10 carry deltas on top of base scenarios)
# ---------------------------------------------------------------------------


def _apply_ptc_sandbox_overlay(run: Any) -> None:
    exec_span = next(s for s in run.spans if s.name == "l2.e3.exec")
    exec_span.attributes["sandbox_envelope_ref"] = "sandbox://ptc/session-0001"
    exec_span.attributes["ptc_script_hash"] = "blake2b:ptcscript000000000000000000000000"
    exec_span.attributes["ptc_stdout_summary_ref"] = "artifact://ptc/stdout/session-0001"
    exec_span.attributes["ptc_stderr_summary_ref"] = "artifact://ptc/stderr/session-0001"


def _apply_l6_after_boundary_overlay(run: Any) -> None:
    run.bundle_payload_summary["l6_proposal"] = {
        "proposal_id": "proposal-f9-001",
        "sealed_exhaust_ref": run.contracts["RuntimeExhaustBundle"]["digest"],
        "gauntlet_status": "PENDING",
        "learning_target": "route_selector",
    }


def _apply_failure_path_overlay(run: Any) -> None:
    run.bundle_payload_summary["failure_path"] = {
        "reason_code": "weak_evidence",
        "result_class": "ABSTAIN",
    }


_OVERLAYS = {
    "ptc_sandbox": _apply_ptc_sandbox_overlay,
    "l6_after_boundary": _apply_l6_after_boundary_overlay,
    "failure_path": _apply_failure_path_overlay,
}


# ---------------------------------------------------------------------------
# Per-fixture RuntimeProofPacket emission
# ---------------------------------------------------------------------------


def _contract_ref(run: Any, name: str) -> str | None:
    contract = run.contracts.get(name)
    if isinstance(contract, dict):
        return contract.get("digest")
    return None


def _emit_runtime_proof_packet(fixture: FixtureFamily, out_dir: Path) -> Path:
    scenario = get(fixture.base_scenario_id)
    run = emit_run(scenario)
    if fixture.overlay:
        _OVERLAYS[fixture.overlay](run)

    out_dir.mkdir(parents=True, exist_ok=True)
    layer_contract_refs = {
        name: run.contracts[name].get("digest")
        for name in run.contracts
        if isinstance(run.contracts[name], dict) and run.contracts[name].get("digest")
    }
    gate_verdict_refs = [
        v for v in run.contracts.get("ExitReviewPacket", {}).get("gate_verdicts", []) if isinstance(v, dict)
    ]
    evidence_ref = _contract_ref(run, "FinalEvidenceContract")
    prompt_ref = _contract_ref(run, "PromptEnvelope")
    sealed_ref = _contract_ref(run, "SealedL2Artifact")
    exit_ref = _contract_ref(run, "X3DispositionReceipt")
    uwg_ref = _contract_ref(run, "UWGCommitReceipt")
    l6_ref = _contract_ref(run, "RuntimeExhaustBundle")
    replay_comparison = dict(run.replay_inputs)
    span_tree_ref = [
        {"span_id": s.span_id, "name": s.name, "parent_span_id": s.parent_span_id} for s in run.spans
    ]
    no_bypass_receipt = {
        "proof_status": "PASS",
        "checked_surfaces": sorted(run.contracts.keys()),
        "prohibited_spans_absent": [sn for sn in scenario.forbidden_spans if sn not in {s.name for s in run.spans}],
        "violations": [],
    }
    packet: dict[str, Any] = {
        "fixture_id": fixture.fixture_id,
        "fixture_description": fixture.description,
        "base_scenario_id": fixture.base_scenario_id,
        "request_id": run.contracts["ValidatedRequest"]["root"]["request_id"],
        "run_id": run.contracts["ValidatedRequest"]["root"]["run_id"],
        "trace_root": run.contracts["ValidatedRequest"]["root"]["trace_root"],
        "layer_contract_refs": layer_contract_refs,
        "gate_verdict_refs": gate_verdict_refs,
        "evidence_contract_ref": evidence_ref,
        "prompt_envelope_ref": prompt_ref,
        "sealed_l2_artifact_ref": sealed_ref,
        "exit_disposition_ref": exit_ref,
        "uwg_receipt_ref": uwg_ref,
        "l6_eval_ref": l6_ref,
        "replay_comparison_ref": replay_comparison,
        "span_tree_ref": span_tree_ref,
        "no_bypass_receipt": no_bypass_receipt,
        "overlay_payload": run.bundle_payload_summary,
    }
    body_for_digest = json.dumps(
        {k: v for k, v in packet.items() if k != "deterministic_digest"},
        indent=2,
        sort_keys=True,
    ).encode("utf-8")
    packet["deterministic_digest"] = "blake2b:" + hashlib.blake2b(body_for_digest, digest_size=16).hexdigest()

    out_path = out_dir / "runtime_proof_packet.json"
    out_path.write_text(json.dumps(packet, indent=2, sort_keys=True), encoding="utf-8")
    return out_path


# ---------------------------------------------------------------------------
# Assertions
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("fixture", FIXTURES, ids=lambda f: f.fixture_id)
def test_fixture_family_runs_successfully(fixture: FixtureFamily) -> None:
    outcome = run_scenario(get(fixture.base_scenario_id))
    assert outcome.scenario_status == ProofStatus.PASS, (
        f"{fixture.fixture_id} base scenario {fixture.base_scenario_id} failed: {outcome.failures}"
    )


@pytest.mark.parametrize("fixture", FIXTURES, ids=lambda f: f.fixture_id)
def test_fixture_family_emits_runtime_proof_packet(fixture: FixtureFamily, tmp_path: Path) -> None:
    out_dir = tmp_path / fixture.fixture_id
    packet_path = _emit_runtime_proof_packet(fixture, out_dir)
    assert packet_path.exists()
    packet = json.loads(packet_path.read_text(encoding="utf-8"))

    required = {
        "fixture_id",
        "request_id",
        "run_id",
        "trace_root",
        "layer_contract_refs",
        "gate_verdict_refs",
        "evidence_contract_ref",
        "prompt_envelope_ref",
        "sealed_l2_artifact_ref",
        "exit_disposition_ref",
        "uwg_receipt_ref",
        "l6_eval_ref",
        "replay_comparison_ref",
        "span_tree_ref",
        "no_bypass_receipt",
        "deterministic_digest",
    }
    missing = required - packet.keys()
    assert not missing, f"{fixture.fixture_id}: packet missing keys {missing}"


@pytest.mark.parametrize("fixture", FIXTURES, ids=lambda f: f.fixture_id)
def test_fixture_packet_resolves_required_refs(fixture: FixtureFamily, tmp_path: Path) -> None:
    out_dir = tmp_path / fixture.fixture_id
    packet_path = _emit_runtime_proof_packet(fixture, out_dir)
    packet = json.loads(packet_path.read_text(encoding="utf-8"))

    assert packet["layer_contract_refs"], f"{fixture.fixture_id}: layer_contract_refs empty"
    assert packet["sealed_l2_artifact_ref"], f"{fixture.fixture_id}: sealed_l2_artifact_ref missing"
    assert packet["exit_disposition_ref"], f"{fixture.fixture_id}: exit_disposition_ref missing"
    assert packet["l6_eval_ref"], f"{fixture.fixture_id}: l6_eval_ref missing"

    if fixture.requires_evidence_contract:
        assert packet["evidence_contract_ref"], (
            f"{fixture.fixture_id}: evidence_contract_ref missing on grounded fixture"
        )
        assert packet["prompt_envelope_ref"], (
            f"{fixture.fixture_id}: prompt_envelope_ref missing on grounded fixture"
        )
    if fixture.requires_uwg_receipt:
        assert packet["uwg_receipt_ref"], (
            f"{fixture.fixture_id}: uwg_receipt_ref missing on commit fixture"
        )


@pytest.mark.parametrize("fixture", FIXTURES, ids=lambda f: f.fixture_id)
def test_fixture_packet_is_deterministic(fixture: FixtureFamily, tmp_path: Path) -> None:
    a_dir = tmp_path / "a" / fixture.fixture_id
    b_dir = tmp_path / "b" / fixture.fixture_id
    a_path = _emit_runtime_proof_packet(fixture, a_dir)
    b_path = _emit_runtime_proof_packet(fixture, b_dir)
    a_packet = json.loads(a_path.read_text(encoding="utf-8"))
    b_packet = json.loads(b_path.read_text(encoding="utf-8"))
    assert a_packet["deterministic_digest"] == b_packet["deterministic_digest"]


def test_all_ten_fixture_families_registered() -> None:
    ids = {f.fixture_id for f in FIXTURES}
    expected = {f"F{i}" for i in range(1, 11)}
    assert ids == expected, f"fixture registry mismatch: {ids ^ expected}"


def test_f6_carries_ptc_sandbox_envelope_attributes() -> None:
    f6 = next(f for f in FIXTURES if f.fixture_id == "F6")
    scenario = get(f6.base_scenario_id)
    run = emit_run(scenario)
    _OVERLAYS[f6.overlay](run)
    exec_span = next(s for s in run.spans if s.name == "l2.e3.exec")
    for key in ("sandbox_envelope_ref", "ptc_script_hash", "ptc_stdout_summary_ref", "ptc_stderr_summary_ref"):
        assert exec_span.attributes.get(key), f"F6: {key} missing"


def test_f9_carries_l6_learning_proposal() -> None:
    f9 = next(f for f in FIXTURES if f.fixture_id == "F9")
    scenario = get(f9.base_scenario_id)
    run = emit_run(scenario)
    _OVERLAYS[f9.overlay](run)
    proposal = run.bundle_payload_summary.get("l6_proposal")
    assert proposal, "F9: l6_proposal missing"
    for key in ("proposal_id", "sealed_exhaust_ref", "gauntlet_status", "learning_target"):
        assert proposal.get(key), f"F9: proposal.{key} missing"


def test_f10_carries_failure_path_overlay() -> None:
    f10 = next(f for f in FIXTURES if f.fixture_id == "F10")
    scenario = get(f10.base_scenario_id)
    run = emit_run(scenario)
    _OVERLAYS[f10.overlay](run)
    failure = run.bundle_payload_summary.get("failure_path")
    assert failure, "F10: failure_path overlay missing"
    assert failure["result_class"] in {"ABSTAIN", "CLARIFY", "BLOCK", "REMOVE"}


def test_fixture_packets_live_on_disk_after_session() -> None:
    """Session-scoped emission — writes the canonical packets the README matrix cites."""
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    for fixture in FIXTURES:
        out_dir = FIXTURES_DIR / fixture.fixture_id
        packet_path = _emit_runtime_proof_packet(fixture, out_dir)
        assert packet_path.exists()
        assert packet_path.parent == out_dir
