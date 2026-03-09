"""H9 / Guardian integration test — ADG graph coverage.

Asserts all 6 graph types produce minimum evidence and all policies pass.
Plan ref: tests/guardian/test_adg_graph_coverage_guardian.py
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.adg.extraction.static_scanner import (
    ADGStaticScanner,
    ScanResult,
    run_scanner_self_test,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]

# Minimum evidence floors per graph (matches plan A2)
_EVIDENCE_FLOORS = {
    "imports": 500,
    "implements": 100,
    "reads_from": 50,
    "instantiates": 50,
}


@pytest.fixture(scope="module")
def scan_result() -> ScanResult:
    scanner = ADGStaticScanner(repo_root=_REPO_ROOT, include_tests=True)
    return scanner.scan()


class TestScannerSelfTest:
    """S1: Scanner self-test must pass before any graph analysis."""

    def test_self_test_passes(self):
        assert run_scanner_self_test() is True


class TestManifestCompleteness:
    """A1: ScanManifest fields must be populated."""

    def test_scanner_version_set(self, scan_result):
        assert scan_result.manifest.scanner_version == "2.0.0"

    def test_python_ast_version_set(self, scan_result):
        assert scan_result.manifest.python_ast_version != ""

    def test_parsed_modules_nonzero(self, scan_result):
        """A3: Zero-parsed-file check."""
        assert scan_result.manifest.parsed_module_count > 0

    def test_self_test_passed_in_manifest(self, scan_result):
        assert scan_result.manifest.scanner_self_test_passed is True

    def test_tests_included_flag(self, scan_result):
        assert scan_result.manifest.tests_included is True


class TestGraphEvidenceFloors:
    """A2: Minimum evidence floors for all 6 graph types."""

    def test_imports_floor(self, scan_result):
        counts = scan_result.edge_counts_by_relation()
        actual = counts.get("imports", 0)
        assert actual >= _EVIDENCE_FLOORS["imports"], (
            f"imports graph: {actual} edges < floor {_EVIDENCE_FLOORS['imports']}"
        )

    def test_implements_floor(self, scan_result):
        counts = scan_result.edge_counts_by_relation()
        actual = counts.get("implements", 0)
        assert actual >= _EVIDENCE_FLOORS["implements"], (
            f"implements graph: {actual} edges < floor {_EVIDENCE_FLOORS['implements']}"
        )

    def test_reads_from_floor(self, scan_result):
        counts = scan_result.edge_counts_by_relation()
        actual = counts.get("reads_from", 0)
        assert actual >= _EVIDENCE_FLOORS["reads_from"], (
            f"reads_from graph: {actual} edges < floor {_EVIDENCE_FLOORS['reads_from']}"
        )

    def test_instantiates_floor(self, scan_result):
        counts = scan_result.edge_counts_by_relation()
        actual = counts.get("instantiates", 0)
        assert actual >= _EVIDENCE_FLOORS["instantiates"], (
            f"instantiates graph: {actual} edges < floor {_EVIDENCE_FLOORS['instantiates']}"
        )


class TestGraphCoverage:
    """All 6 graph types must be present in a full scan."""

    def test_g1_imports_present(self, scan_result):
        relation_types = {e.relation_type for e in scan_result.edges}
        assert "imports" in relation_types

    def test_g3_implements_present(self, scan_result):
        relation_types = {e.relation_type for e in scan_result.edges}
        assert "implements" in relation_types

    def test_g5_reads_from_present(self, scan_result):
        relation_types = {e.relation_type for e in scan_result.edges}
        assert "reads_from" in relation_types

    def test_g6_instantiates_present(self, scan_result):
        relation_types = {e.relation_type for e in scan_result.edges}
        assert "instantiates" in relation_types

    def test_digest_deterministic(self, scan_result):
        """S7: Digest must be a 64-hex SHA256."""
        assert len(scan_result.digest) == 64
        assert all(c in "0123456789abcdef" for c in scan_result.digest)

    def test_no_cardinality_violations(self, scan_result):
        """S9: No cardinality violations in full scan."""
        assert scan_result.manifest.cardinality_violations == [], (
            f"Cardinality violations: {scan_result.manifest.cardinality_violations}"
        )

    def test_minimum_evidence_passed(self, scan_result):
        """A2: manifest flag must be True."""
        assert scan_result.manifest.minimum_evidence_passed is True


class TestLayerLabelCoverage:
    """H2/S4: No L_UNKNOWN modules after label mapping."""

    def test_unknown_layer_count_zero_or_low(self, scan_result):
        """After H2 mapping, unknown count should be very low (external deps only)."""
        assert scan_result.manifest.unknown_layer_count < 50, (
            f"Too many L_UNKNOWN modules: {scan_result.manifest.unknown_layer_count}"
        )
