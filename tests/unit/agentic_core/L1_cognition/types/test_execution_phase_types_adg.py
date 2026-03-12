"""ADG-driven tests for L1_cognition/types/execution_phase_types.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L1_cognition.types.execution_phase_types import (
    ExecutionContext,
    ExecutionPhase,
)


class TestExecutionPhase:
    def test_is_enum(self):
        import enum
        assert issubclass(ExecutionPhase, enum.Enum)

    def test_think_value(self):
        assert ExecutionPhase.THINK.value == "think"

    def test_act_value(self):
        assert ExecutionPhase.ACT.value == "act"

    def test_all_values_are_strings(self):
        for phase in ExecutionPhase:
            assert isinstance(phase.value, str)


class TestExecutionContext:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ExecutionContext)

    def test_creates_with_defaults(self):
        ctx = ExecutionContext(mission="build a feature")
        assert ctx.mission == "build a feature"
        assert ctx.scene == {}
        assert ctx.history == []
