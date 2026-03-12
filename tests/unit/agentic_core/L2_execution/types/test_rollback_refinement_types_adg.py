"""ADG-driven tests for L2_execution/types/rollback_refinement_types.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.types.rollback_refinement_types import RollbackStrategyId


class TestRollbackStrategyId:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(RollbackStrategyId)

    def test_is_frozen(self):
        sid = RollbackStrategyId(name="strategy_a")
        with pytest.raises((AttributeError, TypeError)):
            sid.name = "other"

    def test_creates(self):
        sid = RollbackStrategyId(name="retry_last_good")
        assert sid.name == "retry_last_good"

    def test_canonical_bytes_returns_bytes(self):
        sid = RollbackStrategyId(name="s1")
        result = sid.canonical_bytes()
        assert isinstance(result, bytes)

    def test_content_hash_is_hex_string(self):
        sid = RollbackStrategyId(name="s1")
        h = sid.content_hash()
        assert isinstance(h, str)
        assert len(h) == 64
