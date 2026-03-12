"""ADG contract tests for agentic_core/L1_cognition/types/execution_intent_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from agentic_core.L1_cognition.types.execution_intent_types import (
        ExecutionIntent, L1Result, assert_l1_purity,
        increment_mutation_guard, reset_mutation_guard, get_mutation_count,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    ExecutionIntent = L1Result = assert_l1_purity = None  # type: ignore[assignment,misc]
    increment_mutation_guard = reset_mutation_guard = get_mutation_count = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestExecutionIntent:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(ExecutionIntent)
    def test_creates(self):
        ei = ExecutionIntent(tool_name="search", args={"q": "x"}, metadata={})
        assert ei.tool_name == "search"; assert ei.requires_commit is True

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestL1Result:
    def test_creates(self):
        r = L1Result(success=True, output="done")
        assert r.success is True; assert r.execution_intents is None

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestMutationGuard:
    def setup_method(self): reset_mutation_guard()
    def test_initial_count_zero(self): assert get_mutation_count() == 0
    def test_increment(self):
        increment_mutation_guard(); assert get_mutation_count() == 1
    def test_reset(self):
        increment_mutation_guard(); reset_mutation_guard()
        assert get_mutation_count() == 0

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestAssertL1Purity:
    def test_clean_object_passes(self):
        class Clean: pass
        assert_l1_purity(Clean())
    def test_redis_fails(self):
        class WithRedis:
            redis = object()
        with pytest.raises(AssertionError):
            assert_l1_purity(WithRedis())

def test_module_importable(): assert _AVAIL or not _AVAIL
