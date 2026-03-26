"""ADG-driven tests for L1_cognition/types/capability_types.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: from agentic_core.L1_cognition.types.capability_types import (
    AgentCapability,
    AgentStatus,
)


class TestAgentCapability:
    def test_is_enum(self):
        from agentic_core.L1_cognition.types.capability_types import (
        import enum
        assert issubclass(AgentCapability, enum.Enum)

    def test_reasoning_value(self):
        assert AgentCapability.REASONING.value == "reasoning"

    def test_planning_value(self):
        assert AgentCapability.PLANNING.value == "planning"

    def test_all_values_are_strings(self):
        for cap in AgentCapability:
            assert isinstance(cap.value, str)


class TestAgentStatus:
    def test_is_enum(self):
        import enum
        assert issubclass(AgentStatus, enum.Enum)

    def test_active_value(self):
        assert AgentStatus.ACTIVE.value == "active"

    def test_error_value(self):
        assert AgentStatus.ERROR.value == "error"
