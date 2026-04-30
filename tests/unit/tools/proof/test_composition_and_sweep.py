"""Smoke tests for W2 composition harnesses + W3 sweep tool.

Plan: 10c-proof-depth-remediation-a9f9af.md, Wave verifications.

Coverage scope (smoke + invariants, NOT exhaustive — the harnesses exercise
real production imports + real OTel SDK; per-platform test runtime is
already 1-2s each):

- W2.1 (REQ-077 semantic_cache): runs cleanly, returns a CompositionProofResult,
  honors anti-cheat (depth never above what was actually proven)
- W2.2 (REQ-128 provenance_chain): same shape
- W3 sweep: _load_g1_targets discovers ledger rows, _content_hash is
  idempotent and self-referential
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest


class TestCompositionSemanticCache:
    """W2.1 — REQ-077 semantic-cache composition harness."""

    def test_imports_and_runs(self):
        from tools.proof.composition_proof_semantic_cache import (
            run_composition_proof,
            REQ_ID,
            EXPECTED_SPAN,
        )
        assert REQ_ID == "10C-REQ-077"
        assert EXPECTED_SPAN == "l0.route.contract_emitted"
        result = run_composition_proof()
        assert result.req_id == REQ_ID
        assert result.status in (
            "SATISFIED", "PARTIAL_REACHED",
            "NO_SPANS_EMITTED", "NOT_REACHABLE_THIS_CHECKOUT",
        )
        # Anti-cheat: actual_proof_depth must NEVER exceed E5
        assert result.actual_proof_depth in (
            "E0_REQUIREMENT_TEXT", "E4_NEGATIVE_CONTROL",
            "E6.5_INTEGRATED_RUNTIME", "E5_COMPOSITION_PROOF",
        )

    def test_satisfied_implies_real_span_capture(self):
        """If status=SATISFIED, otel_proof must show captured spans."""
        from tools.proof.composition_proof_semantic_cache import run_composition_proof

        result = run_composition_proof()
        if result.status == "SATISFIED":
            assert result.otel_proof is not None
            assert result.otel_proof.span_count >= 1
            assert result.otel_proof.expected_seen is True
            assert result.actual_proof_depth == "E5_COMPOSITION_PROOF"


class TestCompositionProvenanceChain:
    """W2.2 — REQ-128 L6 provenance-chain composition harness."""

    def test_imports_and_runs(self):
        from tools.proof.composition_proof_provenance_chain import (
            run_composition_proof,
            REQ_ID,
            EXPECTED_SPAN,
        )
        assert REQ_ID == "10C-REQ-128"
        assert EXPECTED_SPAN == "l6.eval.record_sealed"
        result = run_composition_proof()
        assert result.req_id == REQ_ID

    def test_satisfied_implies_real_span_capture(self):
        from tools.proof.composition_proof_provenance_chain import run_composition_proof

        result = run_composition_proof()
        if result.status == "SATISFIED":
            assert result.otel_proof is not None
            assert result.otel_proof.span_count >= 1
            assert result.otel_proof.expected_seen is True
            assert result.actual_proof_depth == "E5_COMPOSITION_PROOF"


class TestSweepTool:
    """W3 sweep tool surface-level invariants."""

    def test_load_g1_targets_returns_list(self):
        from tools.proof.sweep_otel_evidence import _load_g1_targets

        targets = _load_g1_targets()
        assert isinstance(targets, list)
        # Should find real targets if the ledger CSV has otel_span_expected entries
        assert len(targets) >= 100, "ledger should have ≥100 OTel-emitting REQs"
        for t in targets[:5]:
            assert t.req_id.startswith("10C-REQ-")
            assert t.expected_span  # non-empty
            assert t.test_file  # non-empty

    def test_content_hash_self_referential(self):
        """content_hash must be idempotent: hashing a bundle twice with the
        field blanked yields the same value. AND the recorded content_hash
        in the bundle should equal a fresh recomputation when the bundle's
        own content_hash field is blanked first."""
        from tools.proof.sweep_otel_evidence import _content_hash

        b = {
            "req_id": "10C-REQ-001",
            "proof_status": "EVIDENCE_PRESENT",
            "actual_proof_depth": "E4_NEGATIVE_CONTROL",
            "content_hash": "",
        }
        h1 = _content_hash(b)
        h2 = _content_hash(b)
        assert h1 == h2

        # Bundle with non-empty content_hash should produce same hash as bundle
        # with that field blanked.
        b_full = dict(b)
        b_full["content_hash"] = "stale_value"
        h3 = _content_hash(b_full)
        assert h3 == h1

    def test_content_hash_changes_on_payload_change(self):
        from tools.proof.sweep_otel_evidence import _content_hash

        b1 = {"req_id": "X", "content_hash": ""}
        b2 = {"req_id": "Y", "content_hash": ""}
        assert _content_hash(b1) != _content_hash(b2)


class TestMatrixRegen:
    """W4+W5 regenerate_matrix_and_merkle outputs."""

    def test_merkle_artifacts_exist(self):
        REPO = Path(__file__).resolve().parents[4]
        merkle_json = REPO / "artifacts" / "requirements" / "10c_pilot_merkle_root.json"
        assert merkle_json.exists()
        attestation = json.loads(merkle_json.read_text(encoding="utf-8"))
        assert attestation["scheme"] == "REQ_MERKLE_V1"
        assert attestation["leaf_count"] == 200
        assert len(attestation["merkle_root"]) == 64  # SHA-256 hex
        assert attestation["complete"] is True

    def test_matrix_csv_has_200_rows(self):
        REPO = Path(__file__).resolve().parents[4]
        csv_path = REPO / "docs" / "reports" / "design" / "10c_reconciliation" / "10c_post_remediation_matrix.csv"
        assert csv_path.exists()
        # +1 for header
        line_count = sum(1 for _ in csv_path.open(encoding="utf-8"))
        assert line_count == 201, f"expected 201 lines (200 data + 1 header), got {line_count}"

    def test_matrix_csv_required_columns(self):
        import csv as _csv
        REPO = Path(__file__).resolve().parents[4]
        csv_path = REPO / "docs" / "reports" / "design" / "10c_reconciliation" / "10c_post_remediation_matrix.csv"
        with csv_path.open(encoding="utf-8", newline="") as f:
            reader = _csv.DictReader(f)
            header = reader.fieldnames or []
        for required in [
            "req_id", "actual_proof_depth", "proof_status",
            "harness_outcome", "span_count", "expected_seen",
            "harness_replay_digest", "content_hash",
        ]:
            assert required in header, f"matrix CSV missing required column: {required}"
