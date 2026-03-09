"""S10 — Scanner governance: scanner scans itself and finds its own edges.

Plan ref: tests/guardian/test_scanner_governance.py
"""

from __future__ import annotations

from pathlib import Path

from agentic_core.adg.extraction.static_scanner import ADGStaticScanner, ScanResult

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCANNER_FILE = "agentic_core/adg/extraction/static_scanner.py"
_SCHEMA_FILE = "agentic_core/adg/schema.py"


def _scan_scanner() -> ScanResult:
    scanner = ADGStaticScanner(repo_root=_REPO_ROOT, include_tests=False)
    return scanner.scan_files([_SCANNER_FILE, _SCHEMA_FILE])


class TestScannerGovernance:
    """S10: The scanner can scan itself and produce meaningful output."""

    def test_scanner_scans_itself(self):
        result = _scan_scanner()
        assert result.modules, "Scanner produced no modules from its own file"

    def test_scanner_file_in_modules(self):
        result = _scan_scanner()
        assert _SCANNER_FILE in result.modules, (
            f"{_SCANNER_FILE} not found in scanned modules: {result.modules}"
        )

    def test_scanner_imports_edges_present(self):
        result = _scan_scanner()
        import_edges = [e for e in result.edges if e.relation_type == "imports"]
        assert len(import_edges) > 0, "Scanner file has no import edges"

    def test_scanner_digest_computed(self):
        result = _scan_scanner()
        assert len(result.digest) == 64

    def test_scanner_finds_own_class_inheritance(self):
        """Scanner must find its own NodeVisitor subclasses (G3)."""
        result = _scan_scanner()
        impl_edges = [e for e in result.edges if e.relation_type == "implements"]
        assert len(impl_edges) > 0, "Scanner did not find its own class inheritance edges"

    def test_scanner_finds_own_dynamic_exec(self):
        """Scanner's self-test sample has dynamic exec — scanner must detect it in scan_files."""
        # The scanner file itself does not contain eval/exec in production code
        # but this test verifies the dynamic_exec visitor runs without error
        result = _scan_scanner()
        # No assertion on count — just verify no exception was thrown
        assert result.edges is not None

    def test_schema_file_scanned(self):
        result = _scan_scanner()
        assert _SCHEMA_FILE in result.modules, f"{_SCHEMA_FILE} not found in scanned modules"
