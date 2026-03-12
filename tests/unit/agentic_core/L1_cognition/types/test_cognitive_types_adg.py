"""ADG-driven tests for L1_cognition/types/cognitive_types.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L1_cognition.types.cognitive_types import (
    CognitiveCapability,
    PlanningRequest,
)


class TestCognitiveCapability:
    def test_is_enum(self):
        import enum
        assert issubclass(CognitiveCapability, enum.Enum)

    def test_planning_value(self):
        assert CognitiveCapability.PLANNING.value == "planning"

    def test_reasoning_value(self):
        assert CognitiveCapability.REASONING.value == "reasoning"

    def test_all_values_are_strings(self):
        for cap in CognitiveCapability:
            assert isinstance(cap.value, str)


class TestPlanningRequest:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(PlanningRequest)

    def test_creates_with_defaults(self):
        req = PlanningRequest(Task="build a feature")
        assert req.Task == "build a feature"
        assert req.max_steps == 10
        assert req.reasoning_mode == "react"
        assert req.context == {}

    def test_has_to_dict(self):
        assert hasattr(PlanningRequest, "to_dict")
