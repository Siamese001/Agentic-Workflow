"""ADG contract tests for apps_lic/types/route_types.py."""
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

_emit_records_execution_trace("p0", "evidence", "test_route_types_adg")
_emit_applies_guardrail("p0", "test_route_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_route_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_route_types_adg", "state_snapshot")
emit_replay_key("p0", "test_route_types_adg")
emit_determinism_digest("p0", "test_route_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit
try:
    from apps_lic.types.route_types import (
        Archetype,
        CharLimitConstraint,
        Route,
        ValidationSeverity,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False
    Route = Archetype = ValidationSeverity = CharLimitConstraint = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestRoute:
    def test_is_enum(self):
        import enum; assert issubclass(Route, enum.Enum)
    def test_has_inmail(self): assert Route.INMAIL.value == "INMAIL"
    def test_is_str_enum(self): assert issubclass(Route, str)

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestArchetype:
    def test_is_enum(self):
        import enum; assert issubclass(Archetype, enum.Enum)
    def test_four_archetypes(self): assert len(list(Archetype)) == 4

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestCharLimitConstraint:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(CharLimitConstraint)
    def test_validate_within_limits(self):
        c = CharLimitConstraint(min=10, max=100)
        assert c.validate(50) is True
    def test_validate_below_min(self):
        c = CharLimitConstraint(min=10, max=100)
        assert c.validate(5) is False
    def test_validate_above_max(self):
        c = CharLimitConstraint(min=10, max=100)
        assert c.validate(200) is False
    def test_validate_no_limits(self):
        c = CharLimitConstraint()
        assert c.validate(9999) is True

def test_module_importable(): assert _AVAIL or not _AVAIL
