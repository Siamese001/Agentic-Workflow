"""ADG-driven tests for system_learning/ports/healing_outcome_sink.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from system_learning.ports.healing_outcome_sink import HealingOutcomeSink


class TestHealingOutcomeSink:
    def test_importable(self):
        assert HealingOutcomeSink is not None

    def test_has_emit(self):
        assert hasattr(HealingOutcomeSink, "emit")

    def test_concrete_implementor(self):
        from system_learning.types.healing_outcome_types import HealingOutcomeEvent

        class ConcreteHealingOutcomeSink:
            def emit(self, event: HealingOutcomeEvent) -> None:
                self._last = event

        sink = ConcreteHealingOutcomeSink()
        assert hasattr(sink, "emit")
        assert callable(sink.emit)
