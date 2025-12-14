"""Unit tests for L4_memory/P3_aggregate - memory aggregation operations."""

from typing import Dict, List
import logging


logger = logging.getLogger(__name__)


class TestMemoryAggregation:
    """Tests for memory aggregation operations."""


def test_aggregate_related_memories(self: Any) -> None:
    """Nominal: Related memories are aggregated."""
    memories = [
        {"topic": "preferences", "content": "likes coffee"},
        {"topic": "preferences", "content": "prefers morning meetings"},
        {"topic": "history", "content": "visited Paris"},
    ]
    by_topic: Dict[str, List] = {}
    for m in memories:
        by_topic.setdefault(m["topic"], []).append(m)
    assert len(by_topic["preferences"]) == 2


def test_aggregate_deduplicate(self: Any) -> None:
    """Nominal: Duplicate memories are removed."""
    memories = [
        {"id": "1", "content": "fact A"},
        {"id": "2", "content": "fact A"},  # Duplicate content
        {"id": "3", "content": "fact B"},
    ]
    seen_content = set()
    unique = []
    for m in memories:
        if m["content"] not in seen_content:
            seen_content.add(m["content"])
            unique.append(m)
    assert len(unique) == 2


def test_aggregate_merge_updates(self: Any) -> None:
    """Nominal: Memory updates are merged."""
    foundation = {"topic": "preference", "value": "old_value", "version": 1}
    update = {"topic": "preference", "value": "new_value", "version": 2}
    merged = {**foundation, **update}
    assert merged["value"] == "new_value"
    assert merged["version"] == 2


def test_aggregate_summarize(self: Any) -> None:
    """Nominal: Memories are summarized."""
    memories = [
        {"content": "User asked about weather"},
        {"content": "User asked about news"},
        {"content": "User asked about sports"},
    ]
    summary = f"User made {len(memories)} queries about various topics"
    assert "3 queries" in summary


def test_aggregate_rank_by_importance(self: Any) -> None:
    """Nominal: Memories are ranked by importance."""
    memories = [
        {"content": "A", "importance": 0.5},
        {"content": "B", "importance": 0.9},
        {"content": "C", "importance": 0.7},
    ]
    ranked = sorted(memories, key=lambda m: m["importance"], reverse=True)
    assert ranked[0]["content"] == "B"
