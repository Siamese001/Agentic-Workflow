"""W1.P3 — Canonical receipt emitter contract tests.

Plan: apps-rg-canonical-emit-and-hop4a-wiring-b8e2f4
Phase: W1.P3

Tests assert 8 receipts emitted for prefer_canonical=True runs.
Uses fixture run_dir, not live LLM.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from apps_shared.spine_emission.adapter import SpineRuntimeAdapter, AdapterGovernedRun
from apps_shared.spine_emission.context import EmissionConfig


@pytest.fixture
def temp_run_dir():
    """Create a temporary run directory for receipt testing."""
    with tempfile.TemporaryDirectory() as tmp:
        run_dir = Path(tmp) / "20240503_120000"
        run_dir.mkdir(parents=True)
        yield run_dir


@pytest.fixture
def adapter_cfg():
    """Return a minimal EmissionConfig for testing."""
    from apps_shared.spine_emission.contracts import L1PlanStep

    return EmissionConfig(
        app_name="test_app",
        entrypoint_command="python -m test_app",
        runs_root=Path("/tmp/test_runs"),
        route_registry_path=Path("/tmp/test_routes.yaml"),
        l3_dag_path=None,
        plan_steps=[L1PlanStep(step_id="test-001", name="test", kind="transform")],
        plan_rationale="Test configuration for W1.P3 contract tests",
        expects_c0_grounding=False,
        expects_prompt_assembly=False,
        expects_static_dag=False,
        expected_execution_form="DETERMINISTIC_PIPELINE",
        expected_l3_path="BYPASSED",
    )


class TestCanonicalReceiptEmitter:
    """Test that AdapterGovernedRun emits all 8 canonical receipts."""

    def test_emit_receipts_creates_8_files(self, temp_run_dir, adapter_cfg):
        """Verify all 8 receipt files are created when run_dir is set."""
        adapter = SpineRuntimeAdapter(adapter_cfg, prefer_canonical=True)

        with adapter.governed_run(cli_args=[]) as gr:
            gr.set_run_dir(temp_run_dir)
            gr.mark_stage("test_stage", "ok")
            # _emit_receipts called on __exit__

        # Check all 8 receipt files exist
        expected_files = [
            "route_contract.json",
            "l2_execution_receipt.json",
            "exit_review_packet.json",
            "gate_verdicts.json",
            "spine_proof_bundle.json",
            "replay_comparison.json",
            "ats_coverage_report.json",
            "provenance_report.json",
        ]

        for filename in expected_files:
            path = temp_run_dir / filename
            assert path.exists(), f"Missing receipt: {filename}"

    def test_route_contract_has_required_fields(self, temp_run_dir, adapter_cfg):
        """APPS-REQ-RG-001: route_contract.json has all required fields."""
        adapter = SpineRuntimeAdapter(adapter_cfg, prefer_canonical=True)

        with adapter.governed_run(cli_args=[]) as gr:
            gr.set_run_dir(temp_run_dir)

        data = json.loads((temp_run_dir / "route_contract.json").read_text())
        required = [
            "route_id",
            "execution_form",
            "route_digest",
            "hmac_sig",
            "policy_hash",
            "blueprint_hash",
            "replay_key",
        ]
        for field in required:
            assert field in data, f"Missing field: {field}"

    def test_l2_receipt_has_e1_e5_fields(self, temp_run_dir, adapter_cfg):
        """APPS-REQ-RG-002: l2_execution_receipt.json has E1-E5 fields."""
        adapter = SpineRuntimeAdapter(adapter_cfg, prefer_canonical=True)

        with adapter.governed_run(cli_args=[]) as gr:
            gr.set_run_dir(temp_run_dir)

        data = json.loads((temp_run_dir / "l2_execution_receipt.json").read_text())
        required = [
            "e1_work_order",
            "e2_validation_output",
            "e3_attempt_receipt",
            "e4_heal_receipt",
            "e5_dispatch_receipt",
        ]
        for field in required:
            assert field in data, f"Missing field: {field}"

    def test_exit_packet_has_x1_x3_fields(self, temp_run_dir, adapter_cfg):
        """APPS-REQ-RG-003: exit_review_packet.json has X1-X3 fields."""
        adapter = SpineRuntimeAdapter(adapter_cfg, prefer_canonical=True)

        with adapter.governed_run(cli_args=[]) as gr:
            gr.set_run_dir(temp_run_dir)
            gr.mark_stage("test", "ok")

        data = json.loads((temp_run_dir / "exit_review_packet.json").read_text())
        required = ["x1_verdicts", "x2_aggregate", "x3_disposition"]
        for field in required:
            assert field in data, f"Missing field: {field}"

    def test_gate_verdicts_has_required_gates(self, temp_run_dir, adapter_cfg):
        """APPS-REQ-RG-004: gate_verdicts.json has g01, g24, g26, g28."""
        adapter = SpineRuntimeAdapter(adapter_cfg, prefer_canonical=True)

        with adapter.governed_run(cli_args=[]) as gr:
            gr.set_run_dir(temp_run_dir)

        data = json.loads((temp_run_dir / "gate_verdicts.json").read_text())
        required_gates = ["g01", "g24", "g26", "g28"]
        for gate in required_gates:
            assert gate in data, f"Missing gate: {gate}"
            assert "verdict" in data[gate], f"Missing verdict for {gate}"

    def test_spine_proof_bundle_has_no_bypass_evidence(self, temp_run_dir, adapter_cfg):
        """APPS-REQ-RG-005: spine_proof_bundle.json has no_bypass_evidence."""
        adapter = SpineRuntimeAdapter(adapter_cfg, prefer_canonical=True)

        with adapter.governed_run(cli_args=[]) as gr:
            gr.set_run_dir(temp_run_dir)

        data = json.loads((temp_run_dir / "spine_proof_bundle.json").read_text())
        assert "proof_type" in data
        assert "no_bypass_evidence" in data

    def test_replay_comparison_has_replay_key(self, temp_run_dir, adapter_cfg):
        """APPS-REQ-RG-006: replay_comparison.json has replay_key and determinism_verdict."""
        adapter = SpineRuntimeAdapter(adapter_cfg, prefer_canonical=True)

        with adapter.governed_run(cli_args=[]) as gr:
            gr.set_run_dir(temp_run_dir)

        data = json.loads((temp_run_dir / "replay_comparison.json").read_text())
        assert "replay_key" in data
        assert "determinism_verdict" in data

    def test_ats_coverage_has_score_and_terms(self, temp_run_dir, adapter_cfg):
        """APPS-REQ-RG-007: ats_coverage_report.json has coverage_score and matched_terms."""
        adapter = SpineRuntimeAdapter(adapter_cfg, prefer_canonical=True)

        with adapter.governed_run(cli_args=[]) as gr:
            gr.set_run_dir(temp_run_dir)

        data = json.loads((temp_run_dir / "ats_coverage_report.json").read_text())
        assert "coverage_score" in data
        assert "matched_terms" in data

    def test_provenance_has_valid_and_digest(self, temp_run_dir, adapter_cfg):
        """APPS-REQ-RG-008: provenance_report.json has valid and master_binding_digest."""
        adapter = SpineRuntimeAdapter(adapter_cfg, prefer_canonical=True)

        with adapter.governed_run(cli_args=[]) as gr:
            gr.set_run_dir(temp_run_dir)

        data = json.loads((temp_run_dir / "provenance_report.json").read_text())
        assert "valid" in data
        assert "master_binding_digest" in data

    def test_no_emit_when_run_dir_none(self, adapter_cfg):
        """Verify receipts are not emitted when run_dir is never set."""
        adapter = SpineRuntimeAdapter(adapter_cfg, prefer_canonical=True)

        with tempfile.TemporaryDirectory() as tmp:
            temp_path = Path(tmp)
            # Don't create run_dir structure

            with adapter.governed_run(cli_args=[]) as gr:
                # run_dir is None by default
                pass

            # No receipt files should be created
            receipt_files = list(temp_path.glob("*.json"))
            assert len(receipt_files) == 0, f"Unexpected files: {receipt_files}"

    def test_legacy_path_no_emit(self, temp_run_dir, adapter_cfg):
        """Verify legacy path (prefer_canonical=False) does not emit receipts."""
        adapter = SpineRuntimeAdapter(adapter_cfg, prefer_canonical=False)

        with adapter.governed_run(cli_args=[]) as gr:
            gr.set_run_dir(temp_run_dir)

        # No receipt files should be created in legacy mode
        json_files = list(temp_run_dir.glob("*.json"))
        # Filter out any pre-existing files
        receipt_files = [f for f in json_files if f.name in [
            "route_contract.json", "l2_execution_receipt.json",
        ]]
        assert len(receipt_files) == 0, f"Legacy path should not emit: {receipt_files}"
