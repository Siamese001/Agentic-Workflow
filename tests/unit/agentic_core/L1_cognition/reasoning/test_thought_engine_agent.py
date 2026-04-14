"""Behavioral tests for thought_engine_agent."""

from __future__ import annotations

import pytest

from agentic_core.thought_engine_agent import ThoughtEngineAgent, validate_thought_engine_agent


def test_default_agent_passes_validation():
    assert validate_thought_engine_agent().name == "thought-engine"


def test_invalid_iteration_budget_raises():
    with pytest.raises(ValueError):
        ThoughtEngineAgent(max_iterations=0).validate()
