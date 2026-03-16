"""ADG-driven tests for adg/analysis/impact.py — fan_in=1."""
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

_emit_records_execution_trace("p0", "evidence", "test_impact_adg")
_emit_applies_guardrail("p0", "test_impact_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_impact_adg", "policy_binding")
_emit_snapshots_state("p0", "test_impact_adg", "state_snapshot")
emit_replay_key("p0", "test_impact_adg")
emit_determinism_digest("p0", "test_impact_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.adg.analysis.impact import _EXECUTION_RELATIONS, ImpactReport


class TestExecutionRelations:
    def test_is_frozenset(self):
        assert isinstance(_EXECUTION_RELATIONS, frozenset)

    def test_contains_imports(self):
        assert "imports" in _EXECUTION_RELATIONS

    def test_contains_calls(self):
        assert "calls" in _EXECUTION_RELATIONS


class TestImpactReport:
    def test_creates_with_defaults(self):
        report = ImpactReport()
        assert report is not None

    def test_changed_modules_default_empty(self):
        report = ImpactReport()
        assert report.changed_modules == []

    def test_impacted_modules_default_empty(self):
        report = ImpactReport()
        assert report.impacted_modules == []

    def test_risk_score_default_zero(self):
        report = ImpactReport()
        assert report.risk_score == pytest.approx(0.0)

    def test_risk_label_default_low(self):
        report = ImpactReport()
        assert report.risk_label == "LOW"

    def test_covering_tests_default_empty(self):
        report = ImpactReport()
        assert report.covering_tests == []

    def test_with_changed_modules(self):
        report = ImpactReport(changed_modules=["foo.py", "bar.py"])
        assert len(report.changed_modules) == 2
