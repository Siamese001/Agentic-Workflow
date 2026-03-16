"""ADG-driven tests for L5_safety/validators/report_location_validator.py — fan_in=1."""
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

_emit_records_execution_trace("p0", "evidence", "test_report_location_validator_adg")
_emit_applies_guardrail("p0", "test_report_location_validator_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_report_location_validator_adg", "policy_binding")
_emit_snapshots_state("p0", "test_report_location_validator_adg", "state_snapshot")
emit_replay_key("p0", "test_report_location_validator_adg")
emit_determinism_digest("p0", "test_report_location_validator_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.validators.report_location_validator import (
    REPORT_FILE_PATTERNS,
    SSOT_REPORTS_DIR,
)


class TestConstants:
    def test_ssot_reports_dir_value(self):
        assert SSOT_REPORTS_DIR == "docs/reports"

    def test_report_file_patterns_tuple(self):
        assert isinstance(REPORT_FILE_PATTERNS, tuple)
        assert len(REPORT_FILE_PATTERNS) > 0

    def test_md_pattern_present(self):
        assert any("md" in p for p in REPORT_FILE_PATTERNS)

    def test_rca_pattern_present(self):
        assert any("RCA" in p for p in REPORT_FILE_PATTERNS)


class TestReportLocationValidator:
    def test_importable(self):
        from agentic_core.L5_safety.validators.report_location_validator import (
            ReportLocationValidator,
        )
        assert callable(ReportLocationValidator)

    def test_creates(self, tmp_path):
        from agentic_core.L5_safety.validators.report_location_validator import (
            ReportLocationValidator,
        )
        validator = ReportLocationValidator(project_root=tmp_path)
        assert validator is not None
