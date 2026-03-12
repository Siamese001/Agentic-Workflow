"""ADG-driven tests for L1_cognition/engines/perception_engine.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L1_cognition.engines.perception_engine import PerceptionNode


class TestPerceptionNode:
    def test_creates(self):
        node = PerceptionNode()
        assert node.inputs_processed == 0
        assert node.cache == {}

    def test_has_process(self):
        assert hasattr(PerceptionNode, "process")

    def test_process_returns_dict(self):
        node = PerceptionNode()
        result = node.process(
            raw_input={"text": "hello"},
            context={"session_id": "s-1"},
        )
        assert isinstance(result, dict)
