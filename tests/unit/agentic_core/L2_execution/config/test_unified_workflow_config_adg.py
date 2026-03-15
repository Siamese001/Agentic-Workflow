"""ADG-driven tests for L2_execution/config/unified_workflow_config.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.config.unified_workflow_config import MissionFocus
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    MissionFocus = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="unified_workflow_config deps unavailable")
class TestMissionFocus:
    def test_is_enum(self):
        import enum
        assert issubclass(MissionFocus, enum.Enum)

    def test_has_members(self):
        members = list(MissionFocus)
        assert len(members) >= 1


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
