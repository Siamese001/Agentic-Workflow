"""Boundary fault injection matrix — R-99.9 sign-off test suite.

Implements the 99.9 spec: for every fault class a layer could use to bypass its
authority boundary, inject the fault and prove the owning validator catches it.
Emits a ``BoundaryFaultProofBundle`` to ``artifacts/e2e/boundary_faults/proof_bundle.json``
on a clean pytest run so the matrix in
``docs/reference/99_End_to_End_Runtime_Proof_and_Acceptance/README.md`` can cite
a real artifact path.

Fault classes covered (from 99.9 §FAULT CLASSES):
  - L1 attempts route authority
  - L0 attempts retrieval
  - C0 attempts answer generation
  - Prompt Assembly attempts retrieval
  - L2 attempts direct L4 write
  - L2 emits CommitRequest directly (non-UWG path)
  - E4 repair mutates policy_hash
  - HITL bypass of L5 re-clearance
  - Exit cites uncommitted artifact as committed
  - UWG accepts CommitRequest with empty state_diff
  - L6 mutates current run (span before Exit disposition)
  - Runtime Gate UNKNOWN treated as PASS
  - Missing OTEL span still claims proof
  - Replay digest mismatch still progresses
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import pytest

from tests.e2e.proof.bundle import read_bundle
from tests.e2e.proof.contracts import OTELSpan, ProofStatus, XDisposition
from tests.e2e.proof.harness import emit_run
from tests.e2e.proof.scenarios import GOLDEN_PATH_ID, get
from tests.e2e.proof.validators import (
    validate_contracts,
    validate_groundedness,
    validate_no_bypass,
    validate_replay,
    validate_trace,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
BOUNDARY_FAULT_DIR = REPO_ROOT / "artifacts" / "e2e" / "boundary_faults"


# ---------------------------------------------------------------------------
# Fault scenario schema (per 99.9 BoundaryFaultScenario shape)
# ---------------------------------------------------------------------------


@dataclass
class BoundaryFault:
    scenario_id: str
    fault_class: str
    target_layer: str
    base_scenario_id: str
    mutate: Callable[[Any], None]
    expected_validator: str
    expected_reason_substring: str
    expected_no_write: bool = True


def _mutate_l1_grabs_route_authority(run: Any) -> None:
    run.contracts["L1PlanContract"]["route_id_forced"] = "R3_SIMPLE_GROUNDED_READ"


def _mutate_l0_attempts_retrieval(run: Any) -> None:
    run.contracts["RouteContract"]["fetched_evidence_refs"] = ["ev-1"]


def _mutate_c0_answer_generation(run: Any) -> None:
    run.contracts["FinalEvidenceContract"]["final_answer_text"] = "42."


def _mutate_pa_retrieval_outside_c0(run: Any) -> None:
    c0_evidence = run.contracts["FinalEvidenceContract"]["digest"]
    run.contracts["PromptEnvelope"]["upstream_evidence_ref"] = "blake2b:forged00000000000000000000"
    run.contracts["PromptEnvelope"]["__forged_from"] = c0_evidence


def _mutate_l2_direct_l4_write(run: Any) -> None:
    run.contracts["SealedL2Artifact"]["direct_l4_write"] = True


def _mutate_l2_emits_commit_on_non_uwg(run: Any) -> None:
    run.contracts["CommitRequest"] = {
        "contract_type": "CommitRequest",
        "digest": "blake2b:ghostcommit00000000000000000000",
        "upstream_ref": run.contracts["X3DispositionReceipt"]["digest"],
        "state_diff": {"k": "v"},
        "root": dict(run.contracts["X3DispositionReceipt"]["root"]),
    }


def _mutate_e4_policy_drift(run: Any) -> None:
    run.contracts["SealedL2Artifact"]["root"]["policy_hash"] = "policy:tampered"


def _mutate_hitl_bypass_reclearance(run: Any) -> None:
    run.contracts["SealedL2Artifact"]["direct_l4_write"] = True


def _mutate_exit_cites_uncommitted_as_committed(run: Any) -> None:
    run.contracts["X3DispositionReceipt"]["disposition"] = XDisposition.X3C_COMMIT_ELIGIBLE.value


def _mutate_uwg_accepts_empty_state_diff(run: Any) -> None:
    run.contracts["CommitRequest"]["state_diff"] = {}


def _mutate_l6_mutates_current_run(run: Any) -> None:
    spans = list(run.spans)
    l6_idx = next(i for i, s in enumerate(spans) if s.name == "l6.ingest")
    disp_idx = next(i for i, s in enumerate(spans) if s.name == "exit.disposition")
    spans[l6_idx], spans[disp_idx] = spans[disp_idx], spans[l6_idx]
    run.spans = spans


def _mutate_gate_unknown_as_pass(run: Any) -> None:
    run.contracts["ExitReviewPacket"]["gate_verdicts"] = [{"gate": "X1", "status": "UNKNOWN"}]


def _mutate_missing_otel_span(run: Any) -> None:
    run.spans = [s for s in run.spans if s.name != "exit.disposition"]


def _mutate_replay_digest_drift(run: Any) -> None:
    run.replay_inputs["route_digest"] = "blake2b:drifted0000000000000000000000"


FAULT_MATRIX: list[BoundaryFault] = [
    BoundaryFault(
        scenario_id="BF-01-L1-ROUTE-AUTHORITY",
        fault_class="L1_attempts_route_authority",
        target_layer="L1",
        base_scenario_id=GOLDEN_PATH_ID,
        mutate=_mutate_l1_grabs_route_authority,
        expected_validator="no_bypass",
        expected_reason_substring="tamper detected",
    ),
    BoundaryFault(
        scenario_id="BF-02-L0-RETRIEVAL",
        fault_class="L0_attempts_retrieval",
        target_layer="L0",
        base_scenario_id=GOLDEN_PATH_ID,
        mutate=_mutate_l0_attempts_retrieval,
        expected_validator="no_bypass",
        expected_reason_substring="tamper detected",
    ),
    BoundaryFault(
        scenario_id="BF-03-C0-ANSWER-GENERATION",
        fault_class="C0_attempts_answer_generation",
        target_layer="C0",
        base_scenario_id=GOLDEN_PATH_ID,
        mutate=_mutate_c0_answer_generation,
        expected_validator="no_bypass",
        expected_reason_substring="tamper detected",
    ),
    BoundaryFault(
        scenario_id="BF-04-PA-RETRIEVAL-OUTSIDE-C0",
        fault_class="PA_attempts_retrieval",
        target_layer="PromptAssembly",
        base_scenario_id=GOLDEN_PATH_ID,
        mutate=_mutate_pa_retrieval_outside_c0,
        expected_validator="groundedness",
        expected_reason_substring="upstream_evidence_ref does not match",
    ),
    BoundaryFault(
        scenario_id="BF-05-L2-DIRECT-L4-WRITE",
        fault_class="L2_attempts_direct_L4_write",
        target_layer="L2",
        base_scenario_id=GOLDEN_PATH_ID,
        mutate=_mutate_l2_direct_l4_write,
        expected_validator="no_bypass",
        expected_reason_substring="L4 write attempted outside UWG",
    ),
    BoundaryFault(
        scenario_id="BF-06-L2-EMITS-COMMIT-NON-UWG",
        fault_class="L2_emits_CommitRequest_directly",
        target_layer="L2",
        base_scenario_id=GOLDEN_PATH_ID,
        mutate=_mutate_l2_emits_commit_on_non_uwg,
        expected_validator="no_bypass",
        expected_reason_substring="CommitRequest emitted without X3C_COMMIT_ELIGIBLE",
    ),
    BoundaryFault(
        scenario_id="BF-07-E4-POLICY-DRIFT",
        fault_class="E4_mutates_policy_hash",
        target_layer="L2",
        base_scenario_id=GOLDEN_PATH_ID,
        mutate=_mutate_e4_policy_drift,
        expected_validator="no_bypass",
        expected_reason_substring="tamper detected",
    ),
    BoundaryFault(
        scenario_id="BF-08-HITL-BYPASS-RECLEARANCE",
        fault_class="HITL_bypass_of_L5_reclearance",
        target_layer="HITL",
        base_scenario_id="RC-HITL",
        mutate=_mutate_hitl_bypass_reclearance,
        expected_validator="no_bypass",
        expected_reason_substring="L4 write attempted outside UWG",
    ),
    BoundaryFault(
        scenario_id="BF-09-EXIT-CITES-UNCOMMITTED",
        fault_class="Exit_cites_uncommitted_as_committed",
        target_layer="Exit",
        base_scenario_id=GOLDEN_PATH_ID,
        mutate=_mutate_exit_cites_uncommitted_as_committed,
        expected_validator="no_bypass",
        expected_reason_substring="tamper detected",
    ),
    BoundaryFault(
        scenario_id="BF-10-UWG-EMPTY-STATE-DIFF",
        fault_class="UWG_accepts_empty_state_diff",
        target_layer="UWG",
        base_scenario_id="RC-UWG",
        mutate=_mutate_uwg_accepts_empty_state_diff,
        expected_validator="no_bypass",
        expected_reason_substring="empty/missing state_diff",
    ),
    BoundaryFault(
        scenario_id="BF-11-L6-MUTATES-CURRENT-RUN",
        fault_class="L6_mutates_current_run",
        target_layer="L6",
        base_scenario_id=GOLDEN_PATH_ID,
        mutate=_mutate_l6_mutates_current_run,
        expected_validator="no_bypass",
        expected_reason_substring="L6 influence before Exit disposition",
    ),
    BoundaryFault(
        scenario_id="BF-12-GATE-UNKNOWN-AS-PASS",
        fault_class="Gate_UNKNOWN_treated_as_PASS",
        target_layer="00C_gates",
        base_scenario_id=GOLDEN_PATH_ID,
        mutate=_mutate_gate_unknown_as_pass,
        expected_validator="no_bypass",
        expected_reason_substring="tamper detected",
    ),
    BoundaryFault(
        scenario_id="BF-13-MISSING-OTEL-SPAN",
        fault_class="Missing_OTEL_span_still_claims_proof",
        target_layer="otel",
        base_scenario_id=GOLDEN_PATH_ID,
        mutate=_mutate_missing_otel_span,
        expected_validator="trace",
        expected_reason_substring="exit.disposition",
    ),
    BoundaryFault(
        scenario_id="BF-14-REPLAY-DIGEST-DRIFT",
        fault_class="Replay_digest_mismatch_still_progresses",
        target_layer="replay",
        base_scenario_id=GOLDEN_PATH_ID,
        mutate=_mutate_replay_digest_drift,
        expected_validator="replay",
        expected_reason_substring="route_digest mismatch",
    ),
]


# ---------------------------------------------------------------------------
# Per-fault assertion — every fault must be caught by its expected validator
# ---------------------------------------------------------------------------


_VALIDATORS: dict[str, Callable[[Any, Any], tuple[ProofStatus, list[str]]]] = {
    "contracts": validate_contracts,
    "trace": validate_trace,
    "replay": validate_replay,
    "no_bypass": validate_no_bypass,
    "groundedness": validate_groundedness,
}


@pytest.mark.parametrize("fault", FAULT_MATRIX, ids=lambda f: f.scenario_id)
def test_boundary_fault_is_blocked(fault: BoundaryFault) -> None:
    scenario = get(fault.base_scenario_id)
    run = emit_run(scenario)
    fault.mutate(run)

    validator = _VALIDATORS[fault.expected_validator]
    status, failures = validator(scenario, run)

    assert status == ProofStatus.FAIL, (
        f"{fault.scenario_id}: {fault.expected_validator} validator did NOT flag the fault"
    )
    assert any(fault.expected_reason_substring in msg for msg in failures), (
        f"{fault.scenario_id}: expected reason substring "
        f"{fault.expected_reason_substring!r} not found in {failures}"
    )


# ---------------------------------------------------------------------------
# BoundaryFaultProofBundle emission — writes artifacts/e2e/boundary_faults/proof_bundle.json
# ---------------------------------------------------------------------------


def _emit_boundary_fault_bundle(tmp_path: Path | None = None) -> Path:
    out_dir = tmp_path if tmp_path is not None else BOUNDARY_FAULT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    scenarios_run: list[dict[str, Any]] = []
    pass_count = 0
    fail_count = 0
    blocked_write_attempts: list[str] = []
    blocked_authority_expansions: list[str] = []
    missing_expected_blocks: list[str] = []
    trace_coverage_map: dict[str, list[str]] = {}
    replay_comparison_refs: list[str] = []

    for fault in FAULT_MATRIX:
        scenario = get(fault.base_scenario_id)
        run = emit_run(scenario)
        fault.mutate(run)
        validator = _VALIDATORS[fault.expected_validator]
        status, failures = validator(scenario, run)
        blocked = status == ProofStatus.FAIL and any(
            fault.expected_reason_substring in m for m in failures
        )
        if blocked:
            pass_count += 1
        else:
            fail_count += 1
            missing_expected_blocks.append(fault.scenario_id)

        if "L4 write" in fault.expected_reason_substring or "direct_l4_write" in fault.fault_class:
            blocked_write_attempts.append(fault.scenario_id)
        if fault.target_layer in {"L1", "L0", "C0", "PromptAssembly"}:
            blocked_authority_expansions.append(fault.scenario_id)
        if fault.expected_validator == "trace":
            trace_coverage_map[fault.scenario_id] = [s.name for s in run.spans]
        if fault.expected_validator == "replay":
            replay_comparison_refs.append(fault.scenario_id)

        scenarios_run.append(
            {
                "scenario_id": fault.scenario_id,
                "fault_class": fault.fault_class,
                "target_layer": fault.target_layer,
                "base_scenario_id": fault.base_scenario_id,
                "expected_validator": fault.expected_validator,
                "expected_reason_substring": fault.expected_reason_substring,
                "blocked": blocked,
                "actual_status": status.value,
                "actual_failures": failures,
            }
        )

    bundle: dict[str, Any] = {
        "proof_bundle_id": "boundary-fault-matrix-v1",
        "scenarios_run": scenarios_run,
        "pass_count": pass_count,
        "fail_count": fail_count,
        "blocked_write_attempts": blocked_write_attempts,
        "blocked_authority_expansions": blocked_authority_expansions,
        "missing_expected_blocks": missing_expected_blocks,
        "trace_coverage_map": trace_coverage_map,
        "replay_comparison_refs": replay_comparison_refs,
    }
    body = json.dumps(bundle, indent=2, sort_keys=True).encode("utf-8")
    deterministic_digest = "blake2b:" + hashlib.blake2b(body, digest_size=16).hexdigest()
    bundle["deterministic_digest"] = deterministic_digest
    out_path = out_dir / "proof_bundle.json"
    out_path.write_text(json.dumps(bundle, indent=2, sort_keys=True), encoding="utf-8")
    return out_path


def test_boundary_fault_matrix_covers_all_layers() -> None:
    layers = {f.target_layer for f in FAULT_MATRIX}
    # Every authority boundary listed in 99.6 must have at least one fault:
    required_layers = {"L1", "L0", "C0", "PromptAssembly", "L2", "HITL", "Exit", "UWG", "L6", "00C_gates", "otel", "replay"}
    missing = required_layers - layers
    assert not missing, f"fault matrix missing coverage for layers: {missing}"


def test_each_fault_has_expected_blocking_layer() -> None:
    for fault in FAULT_MATRIX:
        assert fault.expected_validator in _VALIDATORS, (
            f"{fault.scenario_id}: unknown validator {fault.expected_validator}"
        )


def test_boundary_fault_bundle_is_emitted_and_complete(tmp_path: Path) -> None:
    out_path = _emit_boundary_fault_bundle(tmp_path)
    assert out_path.exists(), "proof_bundle.json not emitted"
    payload = json.loads(out_path.read_text(encoding="utf-8"))
    assert payload["pass_count"] == len(FAULT_MATRIX), (
        f"not every fault was blocked: missing={payload['missing_expected_blocks']}"
    )
    assert payload["fail_count"] == 0
    assert payload["deterministic_digest"].startswith("blake2b:")
    # Every 99.9 required field must be present
    required_keys = {
        "proof_bundle_id",
        "scenarios_run",
        "pass_count",
        "fail_count",
        "blocked_write_attempts",
        "blocked_authority_expansions",
        "missing_expected_blocks",
        "trace_coverage_map",
        "replay_comparison_refs",
        "deterministic_digest",
    }
    assert required_keys.issubset(payload.keys()), f"missing keys: {required_keys - payload.keys()}"


def test_boundary_fault_bundle_is_deterministic(tmp_path: Path) -> None:
    a = _emit_boundary_fault_bundle(tmp_path / "a")
    b = _emit_boundary_fault_bundle(tmp_path / "b")
    payload_a = json.loads(a.read_text(encoding="utf-8"))
    payload_b = json.loads(b.read_text(encoding="utf-8"))
    assert payload_a["deterministic_digest"] == payload_b["deterministic_digest"]


def test_boundary_fault_bundle_lives_on_disk_after_session() -> None:
    """Session-scoped emission — writes the canonical bundle the README matrix cites."""
    out_path = _emit_boundary_fault_bundle()
    assert out_path.exists()
    assert out_path.parent == BOUNDARY_FAULT_DIR


def test_no_fault_creates_l4_commit_without_uwg() -> None:
    """99.9 TEST REQUIREMENT: test_no_fault_can_create_l4_commit_without_uwg."""
    for fault in FAULT_MATRIX:
        scenario = get(fault.base_scenario_id)
        run = emit_run(scenario)
        fault.mutate(run)
        uwg_receipt = run.contracts.get("UWGCommitReceipt")
        is_uwg_route = scenario.route_id.name == "UWG_COMMIT_PATH"
        if uwg_receipt is not None and not is_uwg_route:
            pytest.fail(f"{fault.scenario_id}: UWGCommitReceipt emitted on non-UWG route")


def test_no_fault_skips_exit_disposition() -> None:
    """99.9 TEST REQUIREMENT: test_no_fault_can_skip_exit_disposition."""
    for fault in FAULT_MATRIX:
        scenario = get(fault.base_scenario_id)
        run = emit_run(scenario)
        fault.mutate(run)
        # Missing-OTEL fault legitimately removes the exit.disposition SPAN but
        # the X3DispositionReceipt contract must still be emitted (contract is
        # the authority of record; span is the observation).
        assert "X3DispositionReceipt" in run.contracts, (
            f"{fault.scenario_id}: X3DispositionReceipt missing from contract chain"
        )
