"""Pytest companion for the end-to-end runtime proof harness.

Invokes the harness as a subprocess (so it exercises the same code path a
human operator runs from the CLI), then asserts:

  - Exit code 0
  - JSON bundle is valid
  - Layer-receipt status fields conform to {PASS, FAIL, SKIPPED_VALIDLY,
    NOT_IMPLEMENTED}
  - Layers known to be wired pass: U0 intake, C0 context, Exit Eval
  - Negative control passes (system abstains on blocked route)
  - No fatal_violations are recorded

The harness's verdict (PARTIALLY_PROVEN today) is a property of the runtime,
not of this test. The test only asserts the harness ran and produced an
honest report.
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
HARNESS = ROOT / "scripts" / "proof" / "run_end_to_end_runtime_proof.py"
JSON_BUNDLE = ROOT / "artifacts" / "proof" / "end_to_end_runtime_proof.json"

VALID_STATUSES = {"PASS", "FAIL", "NOT_IMPLEMENTED", "SKIPPED_VALIDLY"}
WIRED_LAYERS_MUST_PASS = ("U0_intake", "C0_context", "exit_eval_control")


@pytest.fixture(scope="module")
def proof_run() -> dict:
    """Invoke the harness once per module and return the JSON bundle."""
    result = subprocess.run(  # noqa: S603 -- intentional, our own harness
        [sys.executable, str(HARNESS)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=120,
        shell=False,
        check=False,
    )
    assert result.returncode == 0, (
        f"Harness exited non-zero: {result.returncode}\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert JSON_BUNDLE.exists(), "Harness did not produce JSON bundle"
    with JSON_BUNDLE.open(encoding="utf-8") as f:
        bundle = json.load(f)
    return bundle


def test_proof_run_metadata(proof_run: dict) -> None:
    pr = proof_run["proof_run"]
    assert pr["request_id"], "request_id missing"
    assert pr["session_id"], "session_id missing"
    assert pr["run_id"], "run_id missing"
    assert pr["trace_root"], "trace_root missing"
    assert pr["return_code"] == 0


def test_layer_statuses_are_valid(proof_run: dict) -> None:
    for layer, receipt in proof_run["layer_receipts"].items():
        status = receipt.get("status")
        assert status in VALID_STATUSES, (
            f"Layer {layer} has invalid status {status!r}"
        )


@pytest.mark.parametrize("layer", WIRED_LAYERS_MUST_PASS)
def test_wired_layers_pass(proof_run: dict, layer: str) -> None:
    receipt = proof_run["layer_receipts"][layer]
    assert receipt["status"] == "PASS", (
        f"Wired layer {layer} did not PASS: {receipt.get('status')} — "
        f"error={receipt.get('error')}"
    )
    assert receipt.get("artifact_path"), (
        f"{layer} produced no artifact path"
    )


def test_negative_control_passes(proof_run: dict) -> None:
    nc = proof_run["negative_controls"][0]
    assert nc["status"] == "PASS", (
        f"Negative control did not pass: {nc.get('actual_behavior')}"
    )


def test_no_fatal_violations(proof_run: dict) -> None:
    assert proof_run["fatal_violations"] == [], (
        f"Fatal violations recorded: {proof_run['fatal_violations']}"
    )


def test_c0_emitted_evidence_contract(proof_run: dict) -> None:
    c0 = proof_run["layer_receipts"]["C0_context"]
    assert c0["evidence_contract_present"]
    assert c0["retrieval_plan_present"]
    assert c0["candidate_evidence_pool_present"]
    assert c0["shaped_evidence_set_present"]
    assert c0["lineage_manifest_present"]


def test_l3_skipped_validly_for_grounded_read(proof_run: dict) -> None:
    l3 = proof_run["layer_receipts"]["L3_orchestration"]
    assert l3["status"] == "SKIPPED_VALIDLY", (
        "L3 should be SKIPPED_VALIDLY for an R3_GROUNDED route"
    )


def test_otel_trace_has_spans(proof_run: dict) -> None:
    otel = proof_run["layer_receipts"]["otel_telemetry"]
    assert otel["span_count"] > 0
    # Every layer that was exercised should have at least one span recorded
    for required in ("U0", "C0", "Exit"):
        assert otel["spans_by_layer"].get(required), (
            f"No spans recorded for {required}"
        )
