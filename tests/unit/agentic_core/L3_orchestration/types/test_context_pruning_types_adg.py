"""ADG contract tests for L3_orchestration/types/context_pruning_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
from agentic_core.L3_orchestration.types.context_pruning_types import (
    CRITICAL_DNA_KEYS, PruningMetrics, PruningResult, ContextPruningStrategy,
)

class TestCriticalDnaKeys:
    def test_is_frozenset(self): assert isinstance(CRITICAL_DNA_KEYS, frozenset)
    def test_contains_original_goal(self): assert "original_goal" in CRITICAL_DNA_KEYS

class TestPruningMetrics:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(PruningMetrics)
    def test_defaults_zero(self): m = PruningMetrics(); assert m.total_prunes == 0

class TestContextPruningStrategy:
    def test_creates(self): s = ContextPruningStrategy(); assert s is not None
    def test_no_prune_needed(self):
        s = ContextPruningStrategy()
        assert s.should_prune({"a": 1}) is False
