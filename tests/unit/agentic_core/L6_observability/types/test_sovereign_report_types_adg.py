"""ADG contract tests for L6_observability/types/sovereign_report_types.py."""
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

_emit_records_execution_trace("p0", "evidence", "test_sovereign_report_types_adg")
_emit_applies_guardrail("p0", "test_sovereign_report_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_sovereign_report_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_sovereign_report_types_adg", "state_snapshot")
emit_replay_key("p0", "test_sovereign_report_types_adg")
emit_determinism_digest("p0", "test_sovereign_report_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
pytestmark = pytest.mark.unit
from agentic_core.L6_observability.types.sovereign_report_types import SovereignReport


class TestSovereignReport:
    def test_creates(self): r = SovereignReport(); assert r.scores == {}
    def test_overall_score_empty(self): r = SovereignReport(); assert r.get_overall_score() == 0.0
    def test_has_builder(self): assert hasattr(SovereignReport, "Builder")
    def test_get_all_issues_empty(self): r = SovereignReport(); assert r.get_all_issues() == []

class TestSovereignReportBuilder:
    def test_builds_report(self):
        b = SovereignReport.Builder()
        r = b.with_dimension("Structural SSOT", 90.0).build()
        assert isinstance(r, SovereignReport)
        assert r.scores["Structural SSOT"] == 90.0
    def test_unknown_dimension_raises(self):
        b = SovereignReport.Builder()
        with pytest.raises(ValueError): b.with_dimension("Unknown Dim", 50.0)
    def test_score_out_of_range_raises(self):
        b = SovereignReport.Builder()
        with pytest.raises(ValueError): b.with_dimension("Structural SSOT", 101.0)
    def test_report_id_set(self):
        r = SovereignReport.Builder().build()
        assert r.report_id.startswith("audit-")
