"""ADG contract tests for L4_state/types/context_priority_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
from agentic_core.L4_state.types.context_priority_types import ContextPriority, ContextType, ContextChunk

class TestContextPriority:
    def test_is_enum(self):
        import enum; assert issubclass(ContextPriority, enum.Enum)
    def test_has_critical(self):
        assert ContextPriority.CRITICAL.value == "critical"

class TestContextType:
    def test_is_enum(self):
        import enum; assert issubclass(ContextType, enum.Enum)

class TestContextChunk:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(ContextChunk)
    def test_creates(self):
        c = ContextChunk(id="c1", content="hello", chunk_type=ContextType.EXAMPLE,
                         priority=ContextPriority.LOW, token_count=5)
        assert c.id == "c1"
        assert c.token_count == 5
