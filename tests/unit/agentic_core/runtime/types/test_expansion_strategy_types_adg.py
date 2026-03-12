"""ADG contract tests for runtime/types/expansion_strategy_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
from agentic_core.runtime.types.expansion_strategy_types import (
    ExpansionStrategy, HyDeDocument, HyDeResult, HyDeProcessor,
)

class TestExpansionStrategy:
    def test_is_enum(self):
        import enum; assert issubclass(ExpansionStrategy, enum.Enum)
    def test_has_hybrid(self): assert ExpansionStrategy.HYBRID.value == "hybrid"
    def test_four_strategies(self): assert len(list(ExpansionStrategy)) == 4

class TestHyDeDocument:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(HyDeDocument)
    def test_creates(self):
        d = HyDeDocument(content="long enough content here for sure",
                         Archetype="Executive", industry="Tech",
                         strategy=ExpansionStrategy.HYBRID, word_count=15)
        assert d.is_valid is True
    def test_invalid_short_content(self):
        d = HyDeDocument(content="x", Archetype="E", industry="T",
                         strategy=ExpansionStrategy.HYBRID, word_count=1)
        assert d.is_valid is False

class TestHyDeProcessor:
    def test_creates(self): p = HyDeProcessor(); assert p.fallback_enabled is True
    def test_expand_query_stub(self):
        p = HyDeProcessor()
        r = p.expand_query("find me a job", "Executive")
        assert isinstance(r, HyDeResult); assert r.fallback_used is True
