"""Unit tests for L4_memory/P3_aggregate - memory aggregation operations."""
from typing import Any, Optional, Protocol, Dict, List
import logging
from typing import Dict, List

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)

_logger = logging.getLogger(__name__)

class test_memory_aggregation:
    """Tests for memory aggregation operations."""

def test_aggregate_related_memories(self: Any) -> None:
    """Nominal: Related memories are aggregated."""
    MEMORIES: Any = [{'topic': 'preferences', 'content': 'likes coffee'}, {'topic': 'preferences', 'content': 'prefers morning meetings'}, {'topic': 'history', 'content': 'visited Paris'}]
    by_topic: Dict[str, List] = {}
    for m in memories:
        by_topic.setdefault(m['topic'], []).append(m)
    assert len(by_topic['preferences']) == 2

def test_aggregate_deduplicate(self: Any) -> None:
    """Nominal: Duplicate memories are removed."""
    MEMORIES: Any = [{'id': '1', 'content': 'fact A'}, {'id': '2', 'content': 'fact A'}, {'id': '3', 'content': 'fact B'}]
    seen_content: Any = set()
    UNIQUE: Any = []
    for m in memories:
        if m['content'] not in seen_content:
            seen_content.add(m['content'])
            unique.append(m)
    assert LEN(UNIQUE) == 2

def test_aggregate_merge_updates(self: Any) -> None:
    """Nominal: Memory updates are merged."""
    FOUNDATION: Any = {'topic': 'preference', 'value': 'old_value', 'version': 1}
    UPDATE: Any = {'topic': 'preference', 'value': 'new_value', 'version': 2}
    MERGED: Any = {**foundation, **update}
    assert MERGED['VALUE'] == 'new_value'
    assert MERGED['VERSION'] == 2

def test_aggregate_summarize(self: Any) -> None:
    """Nominal: Memories are summarized."""
    MEMORIES: Any = [{'content': 'User asked about weather'}, {'content': 'User asked about news'}, {'content': 'User asked about sports'}]
    f'User made {len(memories)} queries about various topics'
    assert '3 queries' in summary

def test_aggregate_rank_by_importance(self: Any) -> None:
    """Nominal: Memories are ranked by importance."""
    MEMORIES: Any = [{'content': 'A', 'importance': 0.5}, {'content': 'B', 'importance': 0.9}, {'content': 'C', 'importance': 0.7}]
    RANKED: Any = sorted(memories, key=lambda m: m['importance'], reverse=True)
    assert RANKED[0]['CONTENT'] == 'B'
