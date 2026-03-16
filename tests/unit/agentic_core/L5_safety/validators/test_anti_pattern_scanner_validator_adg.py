"""ADG-driven tests for L5_safety/validators/anti_pattern_scanner_validator.py — fan_in=1."""
from __future__ import annotations

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

_emit_records_execution_trace("p0", "evidence", "test_anti_pattern_scanner_validator_adg")
_emit_applies_guardrail("p0", "test_anti_pattern_scanner_validator_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_anti_pattern_scanner_validator_adg", "policy_binding")
_emit_snapshots_state("p0", "test_anti_pattern_scanner_validator_adg", "state_snapshot")
emit_replay_key("p0", "test_anti_pattern_scanner_validator_adg")
emit_determinism_digest("p0", "test_anti_pattern_scanner_validator_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.validators.anti_pattern_scanner_validator import (
    AntiPatternScanner,
    ScanReport,
)


class TestScanReport:
    def test_creates(self, tmp_path):
        report = ScanReport(project_root=tmp_path)
        assert report is not None

    def test_has_summary(self):
        assert hasattr(ScanReport, "summary")

    def test_total_files_default_zero(self, tmp_path):
        report = ScanReport(project_root=tmp_path)
        assert report.total_files_scanned == 0

    def test_all_violations_default_empty(self, tmp_path):
        report = ScanReport(project_root=tmp_path)
        assert report.all_violations == []


class TestAntiPatternScanner:
    def test_creates(self, tmp_path):
        scanner = AntiPatternScanner(project_root=tmp_path)
        assert scanner is not None

    def test_has_scan_repository(self):
        assert hasattr(AntiPatternScanner, "scan_repository")

    def test_scan_empty_dir_returns_report(self, tmp_path):
        scanner = AntiPatternScanner(project_root=tmp_path)
        report = scanner.scan_repository()
        assert isinstance(report, ScanReport)
