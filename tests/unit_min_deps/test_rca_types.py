"""Unit tests for system_learning.types.rca_types."""

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
from system_learning.types.rca_types import (
    RCAFinding,
    canonical_bytes,
    compute_report_hash,
    create_rca_report,
)

_emit_records_execution_trace("p0", "evidence", "test_rca_types")
_emit_applies_guardrail("p0", "test_rca_types", "p0_governance")
_emit_reads_policy_state("p0", "test_rca_types", "policy_binding")
_emit_snapshots_state("p0", "test_rca_types", "state_snapshot")
emit_replay_key("p0", "test_rca_types")
emit_determinism_digest("p0", "test_rca_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit_min_deps


class TestRCATypes:
    def test_deterministic_hash_stability(self):
        """Same inputs produce identical report_hash across two constructions."""
        findings = (
            RCAFinding(
                category="SYNTAX",
                signature="SyntaxError",
                count=5,
                evidence_hash="abc123",
            ),
            RCAFinding(
                category="IMPORT",
                signature="ModuleNotFoundError",
                count=2,
                evidence_hash="def456",
            ),
        )

        report1 = create_rca_report(
            snapshot_id="snap123",
            window_start_utc=1700000000,
            window_end_utc=1700003600,
            findings=findings,
        )

        report2 = create_rca_report(
            snapshot_id="snap123",
            window_start_utc=1700000000,
            window_end_utc=1700003600,
            findings=findings,
        )

        assert report1.report_hash == report2.report_hash
        assert report1.report_id == report2.report_id
        assert report1.report_id == report1.report_hash

    def test_findings_ordering_canonical(self):
        """Findings are sorted deterministically by (category, signature)."""
        # Create findings in non-canonical order
        findings = (
            RCAFinding(
                category="SYNTAX",
                signature="SyntaxError",
                count=5,
                evidence_hash="abc123",
            ),
            RCAFinding(
                category="IMPORT",
                signature="ModuleNotFoundError",
                count=2,
                evidence_hash="def456",
            ),
        )

        report = create_rca_report(
            snapshot_id="snap123",
            window_start_utc=1700000000,
            window_end_utc=1700003600,
            findings=findings,
        )

        # Canonical bytes should sort findings
        canonical = canonical_bytes(report)

        # IMPORT should come before SYNTAX alphabetically
        assert b"IMPORT" in canonical
        assert b"SYNTAX" in canonical
        assert canonical.index(b"IMPORT") < canonical.index(b"SYNTAX")

    def test_changing_evidence_changes_hash(self):
        """Changing one byte in evidence changes report_hash."""
        findings1 = (
            RCAFinding(
                category="SYNTAX",
                signature="SyntaxError",
                count=5,
                evidence_hash="abc123",
            ),
        )

        findings2 = (
            RCAFinding(
                category="SYNTAX",
                signature="SyntaxError",
                count=5,
                evidence_hash="abc124",  # Changed last byte
            ),
        )

        report1 = create_rca_report(
            snapshot_id="snap123",
            window_start_utc=1700000000,
            window_end_utc=1700003600,
            findings=findings1,
        )

        report2 = create_rca_report(
            snapshot_id="snap123",
            window_start_utc=1700000000,
            window_end_utc=1700003600,
            findings=findings2,
        )

        assert report1.report_hash != report2.report_hash

    def test_report_id_equals_report_hash(self):
        """report_id is always equal to report_hash."""
        findings = (
            RCAFinding(
                category="TIMEOUT",
                signature="TimeoutError",
                count=1,
                evidence_hash="xyz789",
            ),
        )

        report = create_rca_report(
            snapshot_id="snap456",
            window_start_utc=1700000000,
            window_end_utc=1700003600,
            findings=findings,
        )

        assert report.report_id == report.report_hash


class TestDeterminism:
    def test_canonical_bytes_deterministic(self):
        """canonical_bytes produces identical output for same report."""
        findings = (
            RCAFinding(
                category="SYNTAX",
                signature="SyntaxError",
                count=5,
                evidence_hash="abc123",
            ),
            RCAFinding(
                category="IMPORT",
                signature="ModuleNotFoundError",
                count=2,
                evidence_hash="def456",
            ),
        )

        report = create_rca_report(
            snapshot_id="snap123",
            window_start_utc=1700000000,
            window_end_utc=1700003600,
            findings=findings,
        )

        canonical1 = canonical_bytes(report)
        canonical2 = canonical_bytes(report)
        canonical3 = canonical_bytes(report)

        assert canonical1 == canonical2 == canonical3

    def test_compute_report_hash_deterministic(self):
        """compute_report_hash produces identical output for same report."""
        findings = (
            RCAFinding(
                category="SYNTAX",
                signature="SyntaxError",
                count=5,
                evidence_hash="abc123",
            ),
        )

        report = create_rca_report(
            snapshot_id="snap123",
            window_start_utc=1700000000,
            window_end_utc=1700003600,
            findings=findings,
        )

        hash1 = compute_report_hash(report)
        hash2 = compute_report_hash(report)
        hash3 = compute_report_hash(report)

        assert hash1 == hash2 == hash3
