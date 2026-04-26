"""Pytest coverage for the E2E runtime proof harness.

These tests are the regression net for ``tests/e2e/proof/`` and the six
runner modules. They ensure:

- the reference emitter produces a complete contract chain per 99.3
- every validator (99.3, 99.4, 99.5, 99.6, 99.7, 99.2) flags the expected
  failure modes when an artifact is tampered
- the bundle writer emits the snake-case artifact filenames mandated by 99.1
- the six runner modules invoke cleanly end-to-end
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from tests.e2e.proof.bundle import _artifact_filename, read_bundle
from tests.e2e.proof.contracts import ProofStatus, RouteId, XDisposition
from tests.e2e.proof.harness import emit_run
from tests.e2e.proof.runner import run_scenario
from tests.e2e.proof.scenarios import GOLDEN_PATH_ID, all_scenarios, get
from tests.e2e.proof.validators import (
    validate_contracts,
    validate_groundedness,
    validate_no_bypass,
    validate_replay,
    validate_route_coverage,
    validate_trace,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Reference emitter
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("scenario", all_scenarios(), ids=lambda s: s.scenario_id)
def test_reference_emitter_passes_all_validators(scenario):
    outcome = run_scenario(scenario)
    assert outcome.scenario_status == ProofStatus.PASS, outcome.failures


def test_emitter_is_deterministic_under_same_seed():
    sc = get(GOLDEN_PATH_ID)
    a = emit_run(sc, seed=0)
    b = emit_run(sc, seed=0)
    assert a.contracts == b.contracts
    assert [s.span_id for s in a.spans] == [s.span_id for s in b.spans]
    assert a.replay_inputs == b.replay_inputs


def test_golden_path_emits_full_contract_chain():
    run = emit_run(get(GOLDEN_PATH_ID))
    expected = {
        "ValidatedRequest",
        "L1PlanContract",
        "RouteContract",
        "FinalEvidenceContract",
        "PromptEnvelope",
        "L2ExecutionRequest",
        "SealedL2Artifact",
        "ExitReviewPacket",
        "X3DispositionReceipt",
        "RuntimeExhaustBundle",
    }
    assert expected.issubset(set(run.contracts.keys()))


def test_terminal_ret_routes_skip_c0_pa_and_l2_request():
    for sid in ("RC-R1A", "RC-R1B", "RC-R5", "RC-HITL"):
        run = emit_run(get(sid))
        assert "FinalEvidenceContract" not in run.contracts
        assert "PromptEnvelope" not in run.contracts
        assert "L2ExecutionRequest" not in run.contracts
        # SealedL2Artifact still emitted as the terminal RET packet
        assert "SealedL2Artifact" in run.contracts


def test_uwg_route_emits_commit_chain():
    run = emit_run(get("RC-UWG"))
    assert "CommitRequest" in run.contracts
    assert "UWGCommitReceipt" in run.contracts
    assert run.contracts["X3DispositionReceipt"]["disposition"] == XDisposition.X3C_COMMIT_ELIGIBLE.value


def test_managed_workflow_emits_l3_contract():
    run = emit_run(get("RC-R3R4-MANAGED"))
    assert "L3WorkflowContract" in run.contracts
    assert {s.name for s in run.spans} >= {"l3.workflow.build", "l3.step.dispatch"}


# ---------------------------------------------------------------------------
# Validator failure modes (99.3, 99.4, 99.6, 99.7)
# ---------------------------------------------------------------------------


def test_contracts_validator_detects_missing_evidence_on_grounded_route():
    sc = get(GOLDEN_PATH_ID)
    run = emit_run(sc)
    del run.contracts["FinalEvidenceContract"]
    status, failures = validate_contracts(sc, run)
    assert status == ProofStatus.FAIL
    assert any("FinalEvidenceContract" in f for f in failures)


def test_contracts_validator_detects_broken_lineage():
    sc = get(GOLDEN_PATH_ID)
    run = emit_run(sc)
    run.contracts["RouteContract"]["upstream_ref"] = "tampered"
    status, failures = validate_contracts(sc, run)
    assert status == ProofStatus.FAIL
    assert any("RouteContract.upstream_ref" in f for f in failures)


def test_no_bypass_detects_direct_l4_write():
    sc = get(GOLDEN_PATH_ID)
    run = emit_run(sc)
    run.contracts["SealedL2Artifact"]["direct_l4_write"] = True
    status, failures = validate_no_bypass(sc, run)
    assert status == ProofStatus.FAIL
    assert any("L4 write attempted outside UWG" in f for f in failures)


def test_no_bypass_detects_digest_tamper():
    sc = get(GOLDEN_PATH_ID)
    run = emit_run(sc)
    run.contracts["RouteContract"]["route_id"] = "TAMPERED_ROUTE"
    status, failures = validate_no_bypass(sc, run)
    assert status == ProofStatus.FAIL
    assert any("declared digest does not match recomputed" in f for f in failures)


def test_no_bypass_detects_l6_before_disposition():
    sc = get(GOLDEN_PATH_ID)
    run = emit_run(sc)
    # Swap order: move l6.ingest before exit.disposition
    spans = list(run.spans)
    l6_idx = next(i for i, s in enumerate(spans) if s.name == "l6.ingest")
    disp_idx = next(i for i, s in enumerate(spans) if s.name == "exit.disposition")
    spans[l6_idx], spans[disp_idx] = spans[disp_idx], spans[l6_idx]
    run.spans = spans
    status, failures = validate_no_bypass(sc, run)
    assert status == ProofStatus.FAIL
    assert any("L6 influence before Exit disposition" in f for f in failures)


def test_trace_detects_missing_required_attribute():
    sc = get(GOLDEN_PATH_ID)
    run = emit_run(sc)
    # Strip a required attribute from one span
    run.spans[0].attributes.pop("policy_hash")
    status, failures = validate_trace(sc, run)
    assert status == ProofStatus.FAIL
    assert any("policy_hash" in f for f in failures)


def test_trace_detects_forbidden_span():
    sc = get(GOLDEN_PATH_ID)
    run = emit_run(sc)
    # Inject a forbidden uwg.commit span on a non-commit route
    from tests.e2e.proof.contracts import OTELSpan

    run.spans.append(
        OTELSpan(
            span_id="span-extra",
            parent_span_id=run.spans[-1].span_id,
            name="uwg.commit",
            attributes=dict(run.spans[0].attributes),
        )
    )
    status, failures = validate_trace(sc, run)
    assert status == ProofStatus.FAIL


def test_replay_passes_with_fixed_seed():
    sc = get(GOLDEN_PATH_ID)
    run = emit_run(sc, seed=0)
    status, replay_failures = validate_replay(sc, run)
    assert status == ProofStatus.PASS, replay_failures


def test_groundedness_not_applicable_on_non_grounded_route():
    sc = get("RC-R5")
    run = emit_run(sc)
    status, _ = validate_groundedness(sc, run)
    assert status == ProofStatus.NOT_APPLICABLE


def test_groundedness_fail_when_evidence_stripped():
    sc = get(GOLDEN_PATH_ID)
    run = emit_run(sc)
    del run.contracts["FinalEvidenceContract"]
    status, gnd_failures = validate_groundedness(sc, run)
    assert status == ProofStatus.FAIL
    assert gnd_failures


def test_route_coverage_succeeds_for_full_registry():
    runs = [(sc, emit_run(sc)) for sc in all_scenarios()]
    status, failures = validate_route_coverage(runs)
    assert status == ProofStatus.PASS, failures


def test_route_coverage_fails_when_route_family_absent():
    runs = [(sc, emit_run(sc)) for sc in all_scenarios() if sc.route_id != RouteId.UWG_COMMIT_PATH]
    status, failures = validate_route_coverage(runs)
    assert status == ProofStatus.FAIL
    assert any("UWG_COMMIT_PATH" in f for f in failures)


# ---------------------------------------------------------------------------
# Bundle filename mapping (99.1 verbatim names)
# ---------------------------------------------------------------------------


def test_artifact_filename_matches_99_1_spec():
    assert _artifact_filename("GP-001", "RouteContract") == "gp_001_route_contract.json"
    assert _artifact_filename("GP-001", "FinalEvidenceContract") == "gp_001_final_evidence_contract.json"
    assert _artifact_filename("GP-001", "PromptEnvelope") == "gp_001_prompt_envelope.json"
    assert _artifact_filename("GP-001", "SealedL2Artifact") == "gp_001_sealed_l2_artifact.json"
    assert _artifact_filename("GP-001", "ExitReviewPacket") == "gp_001_exit_review_packet.json"
    assert _artifact_filename("GP-001", "X3DispositionReceipt") == "gp_001_x3_disposition.json"
    assert _artifact_filename("GP-001", "otel_trace") == "gp_001_otel_trace.json"
    assert _artifact_filename("GP-001", "replay_receipt") == "gp_001_replay_receipt.json"
    assert _artifact_filename("GP-001", "no_bypass_receipt") == "gp_001_no_bypass_receipt.json"


# ---------------------------------------------------------------------------
# End-to-end runner invocations (CLI surfaces from 99.8)
# ---------------------------------------------------------------------------


def _run_cli(module: str, args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", module, *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )


@pytest.mark.parametrize(
    "args,bundle_subdir",
    [
        (["--scenario-set", "all"], "all"),
        (["--scenario", GOLDEN_PATH_ID], "gp_001"),
        (["--scenario-set", "routes"], "routes"),
    ],
)
def test_run_agentic_runtime_proof_cli(tmp_path, args, bundle_subdir):
    bundle_dir = tmp_path / bundle_subdir
    result = _run_cli(
        "tests.e2e.run_agentic_runtime_proof",
        [*args, "--emit-proof-bundle", str(bundle_dir), "--strict"],
        REPO_ROOT,
    )
    assert result.returncode == 0, result.stderr + result.stdout
    bundle = read_bundle(bundle_dir)
    assert bundle["acceptance_status"] == "PASS"
    assert bundle["scenarios"]


def test_run_route_coverage_proof_cli(tmp_path):
    bundle_dir = tmp_path / "routes"
    result = _run_cli(
        "tests.e2e.run_route_coverage_proof",
        ["--all-routes", "--emit-proof-bundle", str(bundle_dir), "--strict"],
        REPO_ROOT,
    )
    assert result.returncode == 0, result.stderr + result.stdout
    bundle = read_bundle(bundle_dir)
    assert bundle["acceptance_status"] == "PASS"
    assert {s["scenario_id"] for s in bundle["scenarios"]} >= {"RC-R1A", "RC-R3", "RC-UWG"}


@pytest.mark.parametrize(
    "module",
    [
        "tests.e2e.validate_trace_tree",
        "tests.e2e.validate_replay",
        "tests.e2e.validate_no_bypass",
        "tests.e2e.validate_grounded_output",
    ],
)
def test_validate_axis_runners_pass_on_clean_bundle(tmp_path, module):
    bundle_dir = tmp_path / "all"
    seed_result = _run_cli(
        "tests.e2e.run_agentic_runtime_proof",
        ["--scenario-set", "all", "--emit-proof-bundle", str(bundle_dir), "--strict"],
        REPO_ROOT,
    )
    assert seed_result.returncode == 0, seed_result.stderr

    result = _run_cli(module, ["--proof-bundle", str(bundle_dir), "--strict"], REPO_ROOT)
    assert result.returncode == 0, result.stderr + result.stdout
    assert "[PASS]" in result.stdout


def test_validate_no_bypass_strict_fails_on_violation_injection(tmp_path):
    bundle_dir = tmp_path / "all"
    seed_result = _run_cli(
        "tests.e2e.run_agentic_runtime_proof",
        ["--scenario-set", "golden", "--emit-proof-bundle", str(bundle_dir), "--strict"],
        REPO_ROOT,
    )
    assert seed_result.returncode == 0, seed_result.stderr

    # Tamper the bundle: inject a violation into the no_bypass receipt
    bundle_path = bundle_dir / "bundle.json"
    payload = json.loads(bundle_path.read_text(encoding="utf-8"))
    payload["scenarios"][0]["no_bypass_receipts"][0]["proof_status"] = "FAIL"
    payload["scenarios"][0]["no_bypass_receipts"][0]["violations"].append("synthetic_violation")
    bundle_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    result = _run_cli(
        "tests.e2e.validate_no_bypass",
        ["--proof-bundle", str(bundle_dir), "--strict"],
        REPO_ROOT,
    )
    assert result.returncode == 1, result.stdout + result.stderr
    assert "synthetic_violation" in result.stderr


def test_proof_bundle_contains_99_1_required_artifacts(tmp_path):
    bundle_dir = tmp_path / "gp"
    result = _run_cli(
        "tests.e2e.run_agentic_runtime_proof",
        ["--scenario", GOLDEN_PATH_ID, "--emit-proof-bundle", str(bundle_dir), "--strict"],
        REPO_ROOT,
    )
    assert result.returncode == 0, result.stderr
    s_dir = bundle_dir / "scenarios" / GOLDEN_PATH_ID
    expected = {
        "gp_001_request.json",
        "gp_001_l1_plan.json",
        "gp_001_route_contract.json",
        "gp_001_final_evidence_contract.json",
        "gp_001_prompt_envelope.json",
        "gp_001_sealed_l2_artifact.json",
        "gp_001_exit_review_packet.json",
        "gp_001_x3_disposition.json",
        "gp_001_otel_trace.json",
        "gp_001_replay_receipt.json",
        "gp_001_no_bypass_receipt.json",
    }
    present = {p.name for p in s_dir.iterdir()}
    missing = expected - present
    assert not missing, f"missing 99.1 artifacts: {missing}"


# ---------------------------------------------------------------------------
# Idempotency / determinism across separate processes
# ---------------------------------------------------------------------------


def test_two_independent_runs_produce_identical_bundles(tmp_path):
    a = tmp_path / "a"
    b = tmp_path / "b"
    for d in (a, b):
        result = _run_cli(
            "tests.e2e.run_agentic_runtime_proof",
            ["--scenario-set", "all", "--emit-proof-bundle", str(d), "--strict"],
            REPO_ROOT,
        )
        assert result.returncode == 0, result.stderr

    bundle_a = read_bundle(a)
    bundle_b = read_bundle(b)
    # Drop fields that legitimately differ across runs
    for fld in ("bundle_id", "generated_at"):
        bundle_a.pop(fld, None)
        bundle_b.pop(fld, None)
    bundle_a.pop("digest", None)
    bundle_b.pop("digest", None)

    assert bundle_a == bundle_b
