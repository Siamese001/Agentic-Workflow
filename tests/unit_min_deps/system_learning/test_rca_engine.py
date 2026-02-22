"""Unit tests for system_learning.engines.rca_engine."""

import pytest

from system_learning.engines.rca_engine import RCAAnalysisError, analyze_failures

pytestmark = pytest.mark.unit_min_deps


# Synthetic audit slice fixture
AUDIT_SLICE_FIXTURE = b"""
SyntaxError: invalid syntax
SyntaxError: unexpected EOF
ModuleNotFoundError: No module named 'foo'
ImportError: cannot import name 'bar'
ERROR collecting tests/test_example.py
TimeoutError: operation timed out
SyntaxError: invalid syntax
SourceMutationBlocked: cannot modify protected file
"""


class TestRCAEngine:
    def test_analyze_failures_basic(self):
        """Basic RCA analysis produces expected findings."""
        report = analyze_failures(
            snapshot_id="snap123",
            audit_slice=AUDIT_SLICE_FIXTURE,
            window_start_utc=1700000000,
            window_end_utc=1700003600,
        )

        # Should have findings for multiple categories
        assert len(report.findings) > 0

        # Check that we have expected categories
        categories = {f.category for f in report.findings}
        assert "SYNTAX" in categories
        assert "IMPORT" in categories
        assert "TEST_DISCOVERY" in categories
        assert "TIMEOUT" in categories
        assert "POLICY_BLOCK" in categories

    def test_exact_findings_counts(self):
        """Exact findings match expected categories, signatures, and counts."""
        report = analyze_failures(
            snapshot_id="snap123",
            audit_slice=AUDIT_SLICE_FIXTURE,
            window_start_utc=1700000000,
            window_end_utc=1700003600,
        )

        # Build a dict for easier assertion
        findings_dict = {(f.category, f.signature): f.count for f in report.findings}

        # SYNTAX: 3 occurrences
        assert findings_dict.get(("SYNTAX", "SyntaxError")) == 3

        # IMPORT: 1 ModuleNotFoundError + 1 ImportError
        assert findings_dict.get(("IMPORT", "ModuleNotFoundError")) == 1
        assert findings_dict.get(("IMPORT", "ImportError")) == 1

        # TEST_DISCOVERY: 1 occurrence
        assert findings_dict.get(("TEST_DISCOVERY", "pytest_collection_error")) == 1

        # TIMEOUT: 1 occurrence
        assert findings_dict.get(("TIMEOUT", "TimeoutError")) == 1

        # POLICY_BLOCK: 1 occurrence
        assert findings_dict.get(("POLICY_BLOCK", "SourceMutationBlocked")) == 1

    def test_determinism_same_slice_identical_report_id(self):
        """Same audit_slice produces identical report_id."""
        report1 = analyze_failures(
            snapshot_id="snap123",
            audit_slice=AUDIT_SLICE_FIXTURE,
            window_start_utc=1700000000,
            window_end_utc=1700003600,
        )

        report2 = analyze_failures(
            snapshot_id="snap123",
            audit_slice=AUDIT_SLICE_FIXTURE,
            window_start_utc=1700000000,
            window_end_utc=1700003600,
        )

        assert report1.report_id == report2.report_id
        assert report1.report_hash == report2.report_hash

    def test_invalid_window_rejected(self):
        """Invalid window (start >= end) raises RCAAnalysisError."""
        with pytest.raises(RCAAnalysisError, match="Invalid window"):
            analyze_failures(
                snapshot_id="snap123",
                audit_slice=AUDIT_SLICE_FIXTURE,
                window_start_utc=1700003600,
                window_end_utc=1700000000,  # end < start
            )

    def test_malformed_utf8_rejected(self):
        """Malformed UTF-8 raises RCAAnalysisError."""
        malformed_bytes = b"\xff\xfe invalid utf-8"

        with pytest.raises(RCAAnalysisError, match="Failed to decode"):
            analyze_failures(
                snapshot_id="snap123",
                audit_slice=malformed_bytes,
                window_start_utc=1700000000,
                window_end_utc=1700003600,
            )

    def test_empty_slice_produces_unknown_category(self):
        """Empty audit slice produces UNKNOWN category."""
        report = analyze_failures(
            snapshot_id="snap123",
            audit_slice=b"",
            window_start_utc=1700000000,
            window_end_utc=1700003600,
        )

        # Should have one finding with UNKNOWN category
        assert len(report.findings) == 1
        assert report.findings[0].category == "UNKNOWN"
        assert report.findings[0].signature == "no_patterns_matched"

    def test_no_matching_patterns_produces_unknown(self):
        """Audit slice with no matching patterns produces UNKNOWN."""
        report = analyze_failures(
            snapshot_id="snap123",
            audit_slice=b"some random text\nwith no patterns\n",
            window_start_utc=1700000000,
            window_end_utc=1700003600,
        )

        # Should have one finding with UNKNOWN category
        assert len(report.findings) == 1
        assert report.findings[0].category == "UNKNOWN"


class TestDeterminism:
    def test_analyze_failures_deterministic(self):
        """analyze_failures produces identical results across multiple calls."""
        report1 = analyze_failures(
            snapshot_id="snap123",
            audit_slice=AUDIT_SLICE_FIXTURE,
            window_start_utc=1700000000,
            window_end_utc=1700003600,
        )

        report2 = analyze_failures(
            snapshot_id="snap123",
            audit_slice=AUDIT_SLICE_FIXTURE,
            window_start_utc=1700000000,
            window_end_utc=1700003600,
        )

        report3 = analyze_failures(
            snapshot_id="snap123",
            audit_slice=AUDIT_SLICE_FIXTURE,
            window_start_utc=1700000000,
            window_end_utc=1700003600,
        )

        assert report1.report_id == report2.report_id == report3.report_id
        assert report1.report_hash == report2.report_hash == report3.report_hash
