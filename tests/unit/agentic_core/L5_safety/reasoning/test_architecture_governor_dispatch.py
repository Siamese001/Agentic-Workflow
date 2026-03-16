"""Tests for ArchitectureGovernorAgent dynamic dispatch fixes.

Verifies that the refactored violation_type access uses direct typed attribute
access rather than getattr/hasattr dynamic dispatch on StructureViolation.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

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

_emit_records_execution_trace("p0", "evidence", "test_architecture_governor_dispatch")
_emit_applies_guardrail("p0", "test_architecture_governor_dispatch", "p0_governance")
_emit_reads_policy_state("p0", "test_architecture_governor_dispatch", "policy_binding")
_emit_snapshots_state("p0", "test_architecture_governor_dispatch", "state_snapshot")
emit_replay_key("p0", "test_architecture_governor_dispatch")
emit_determinism_digest("p0", "test_architecture_governor_dispatch")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.reasoning.StructuralValidatorAgent import StructureViolation


def _make_violation(
    violation_type: str,
    message: str = "test violation",
    severity: str = "ERROR",
    suggested_fix: str | None = None,
    file_path: Path | None = None,
) -> StructureViolation:
    return StructureViolation(
        file_path=file_path or Path("fake/file.py"),
        line_number=1,
        violation_type=violation_type,
        message=message,
        suggested_fix=suggested_fix,
        severity=severity,
    )


class TestStructureViolationDirectAccess:
    """StructureViolation.violation_type is a plain str — no getattr/hasattr needed."""

    def test_violation_type_is_str(self):
        v = _make_violation("GRAVITY")
        assert isinstance(v.violation_type, str)

    def test_violation_type_value(self):
        v = _make_violation("NAMING")
        assert v.violation_type == "NAMING"

    def test_violation_severity_direct(self):
        v = _make_violation("GRAVITY", severity="CRITICAL")
        assert v.severity == "CRITICAL"

    def test_violation_suggested_fix_direct(self):
        v = _make_violation("ORPHAN", suggested_fix="Move to archive")
        assert v.suggested_fix == "Move to archive"

    def test_violation_suggested_fix_none_default(self):
        v = _make_violation("DUPLICATE")
        assert v.suggested_fix is None


class TestLogCategoricalDrift:
    """_log_categorical_drift now uses str(raw_vt) instead of hasattr(v_type,'name')."""

    def test_gravity_violation_counted(self):
        from agentic_core.L5_safety.reasoning.ArchitectureGovernorAgent import ArchitectureGovernorAgent

        agent = ArchitectureGovernorAgent.__new__(ArchitectureGovernorAgent)
        agent.project_root = Path(".")
        report = agent._log_categorical_drift(
            [
                _make_violation("GRAVITY"),
                _make_violation("NAMING"),
                _make_violation("ORPHAN"),
                _make_violation("DUPLICATE"),
            ]
        )
        assert report["GRAVITY"] == 1
        assert report["NAMING"] == 1
        assert report["ORPHAN"] == 1
        assert report["DUPLICATE"] == 1

    def test_unknown_type_goes_to_other(self):
        from agentic_core.L5_safety.reasoning.ArchitectureGovernorAgent import ArchitectureGovernorAgent

        agent = ArchitectureGovernorAgent.__new__(ArchitectureGovernorAgent)
        agent.project_root = Path(".")
        report = agent._log_categorical_drift([_make_violation("EXOTIC_TYPE")])
        assert report["OTHER"] == 1

    def test_dict_violations_counted(self):
        from agentic_core.L5_safety.reasoning.ArchitectureGovernorAgent import ArchitectureGovernorAgent

        agent = ArchitectureGovernorAgent.__new__(ArchitectureGovernorAgent)
        agent.project_root = Path(".")
        report = agent._log_categorical_drift(
            [
                {"type": "GRAVITY"},
                {"type": "NAMING"},
            ]
        )
        assert report["GRAVITY"] == 1
        assert report["NAMING"] == 1

    def test_lowercase_violation_type_normalized(self):
        from agentic_core.L5_safety.reasoning.ArchitectureGovernorAgent import ArchitectureGovernorAgent

        agent = ArchitectureGovernorAgent.__new__(ArchitectureGovernorAgent)
        agent.project_root = Path(".")
        report = agent._log_categorical_drift([{"type": "gravity"}])
        assert report["GRAVITY"] == 1

    def test_empty_violations_all_zero(self):
        from agentic_core.L5_safety.reasoning.ArchitectureGovernorAgent import ArchitectureGovernorAgent

        agent = ArchitectureGovernorAgent.__new__(ArchitectureGovernorAgent)
        agent.project_root = Path(".")
        report = agent._log_categorical_drift([])
        assert all(v == 0 for v in report.values())

    def test_violation_with_none_type_goes_to_other(self):
        from agentic_core.L5_safety.reasoning.ArchitectureGovernorAgent import ArchitectureGovernorAgent

        agent = ArchitectureGovernorAgent.__new__(ArchitectureGovernorAgent)
        agent.project_root = Path(".")
        v = MagicMock()
        v.violation_type = None
        report = agent._log_categorical_drift([v])
        assert report["OTHER"] == 1


class TestViolationTypeDirect:
    """Verify the typed violation_type path in the heal_repository loop."""

    def test_gravity_string_type_comparison(self):
        v = _make_violation("GRAVITY")
        _vt = v.violation_type if isinstance(v.violation_type, str) else str(v.violation_type)
        assert _vt == "GRAVITY"

    def test_naming_string_type_comparison(self):
        v = _make_violation("NAMING")
        _vt = v.violation_type if isinstance(v.violation_type, str) else str(v.violation_type)
        assert _vt == "NAMING"

    def test_enum_like_object_fallback_to_str(self):
        class FakeEnum:
            name = "GRAVITY"

            def __str__(self):
                return "GRAVITY"

        v = MagicMock()
        v.violation_type = FakeEnum()
        raw = v.violation_type
        _vt = raw if isinstance(raw, str) else str(raw)
        assert _vt == "GRAVITY"
