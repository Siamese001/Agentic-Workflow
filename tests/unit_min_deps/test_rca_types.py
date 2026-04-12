"""Unit tests for system_learning.types.rca_types."""


class TestRCATypes:
    def test_deterministic_hash_stability(self):
        """Same inputs produce identical report_hash across two constructions."""

    def test_findings_ordering_canonical(self):
        """Findings are sorted deterministically by (category, signature)."""

    def test_changing_evidence_changes_hash(self):
        """Changing one byte in evidence changes report_hash."""

    def test_report_id_equals_report_hash(self):
        """report_id is always equal to report_hash."""


class TestDeterminism:
    def test_canonical_bytes_deterministic(self):
        """canonical_bytes produces identical output for same report."""

    def test_compute_report_hash_deterministic(self):
        """compute_report_hash produces identical output for same report."""
