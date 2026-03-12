"""ADG-driven tests for L1_cognition/config/react_config.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L1_cognition.config.react_config import (
    ReasoningMode,
    ReActStep,
)


class TestReasoningMode:
    def test_is_enum(self):
        import enum
        assert issubclass(ReasoningMode, enum.Enum)

    def test_react_value(self):
        assert ReasoningMode.REACT.value == "react"

    def test_chain_of_thought_value(self):
        assert ReasoningMode.CHAIN_OF_THOUGHT.value == "cot"

    def test_all_values_are_strings(self):
        for mode in ReasoningMode:
            assert isinstance(mode.value, str)


class TestReActStep:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ReActStep)

    def test_creates(self):
        step = ReActStep(step_number=1, thought="analyze this", action="search")
        assert step.step_number == 1
        assert step.thought == "analyze this"
        assert step.action == "search"
        assert step.observation == ""
