"""ADG-driven tests for L1_cognition/engines/CognitiveNode.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L1_cognition.engines.CognitiveNode import CognitiveResult


class TestCognitiveResult:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(CognitiveResult)

    def test_creates_with_required_fields(self):
        result = CognitiveResult(output="done", thought_type="reasoning")
        assert result.output == "done"
        assert result.thought_type == "reasoning"
        assert result.success is True
        assert result.latency_ms == 0.0
        assert result.plan == {}
        assert result.memory_used == []
