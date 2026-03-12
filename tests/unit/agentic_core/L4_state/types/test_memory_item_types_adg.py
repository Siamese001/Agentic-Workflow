"""ADG-driven tests for agentic_core/L4_state/types/memory_item_types.py — fan_in=3.

Contract tests: MemoryItem and MemoryQuery pydantic models.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L4_state.types.memory_item_types import MemoryItem, MemoryQuery


class TestMemoryItemImport:
    def test_classes_importable(self):
        assert callable(MemoryItem)
        assert callable(MemoryQuery)


class TestMemoryItem:
    def test_valid_creation(self):
        item = MemoryItem(
            content="test memory",
            embedding=[0.1, 0.2, 0.3],
            metadata={"tag": "test"},
        )
        assert item.content == "test memory"
        assert item.embedding == [0.1, 0.2, 0.3]

    def test_empty_content_raises(self):
        with pytest.raises(Exception):
            MemoryItem(content="", embedding=[0.1], metadata={})

    def test_empty_embedding_raises(self):
        with pytest.raises(Exception):
            MemoryItem(content="test", embedding=[], metadata={})

    def test_default_metadata(self):
        item = MemoryItem(content="test", embedding=[0.1, 0.2])
        assert isinstance(item.metadata, dict)

    def test_score_defaults_to_none(self):
        item = MemoryItem(content="test", embedding=[0.1])
        assert item.score is None

    def test_score_can_be_set(self):
        item = MemoryItem(content="test", embedding=[0.1], score=0.95)
        assert item.score == pytest.approx(0.95)

    def test_metadata_accepts_any_values(self):
        item = MemoryItem(
            content="test",
            embedding=[0.1],
            metadata={"key": "value", "num": 42, "flag": True},
        )
        assert item.metadata["num"] == 42


class TestMemoryQuery:
    def test_valid_creation(self):
        query = MemoryQuery(vector=[0.1, 0.2, 0.3])
        assert query.vector == [0.1, 0.2, 0.3]

    def test_default_top_k(self):
        query = MemoryQuery(vector=[0.1])
        assert query.top_k == 5

    def test_custom_top_k(self):
        query = MemoryQuery(vector=[0.1], top_k=10)
        assert query.top_k == 10

    def test_top_k_minimum_1(self):
        with pytest.raises(Exception):
            MemoryQuery(vector=[0.1], top_k=0)

    def test_top_k_maximum_100(self):
        with pytest.raises(Exception):
            MemoryQuery(vector=[0.1], top_k=101)

    def test_filter_metadata_defaults_to_none(self):
        query = MemoryQuery(vector=[0.1])
        assert query.filter_metadata is None

    def test_filter_metadata_can_be_set(self):
        query = MemoryQuery(vector=[0.1], filter_metadata={"tag": "important"})
        assert query.filter_metadata == {"tag": "important"}
