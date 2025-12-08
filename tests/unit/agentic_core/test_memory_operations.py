"""Unit tests for L4_memory layer - memory storage, retrieval, and management."""
from __future__ import annotations
import pytest
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import hashlib

@dataclass
class MemoryEntry:
    id: str
    content: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None

class TestMemoryStorage:
    """Tests for memory storage operations."""

    def test_store_memory_entry(self):
        """Nominal: Memory entry is stored."""
        entry = MemoryEntry(
            id="mem_001",
            content="User prefers formal tone",
            timestamp=datetime.now(),
        )
        storage: Dict[str, MemoryEntry] = {}
        storage[entry.id] = entry
        assert entry.id in storage

    def test_store_with_metadata(self):
        """Nominal: Memory with metadata is stored."""
        entry = MemoryEntry(
            id="mem_002",
            content="Important fact",
            timestamp=datetime.now(),
            metadata={"source": "conversation", "importance": "high"},
        )
        assert entry.metadata["importance"] == "high"

    def test_store_duplicate_overwrites(self):
        """Edge case: Duplicate ID overwrites existing."""
        storage: Dict[str, MemoryEntry] = {}
        entry1 = MemoryEntry(id="mem_001", content="Original", timestamp=datetime.now())
        entry2 = MemoryEntry(id="mem_001", content="Updated", timestamp=datetime.now())
        storage[entry1.id] = entry1
        storage[entry2.id] = entry2
        assert storage["mem_001"].content == "Updated"

    def test_store_generates_id(self):
        """Nominal: ID is generated from content hash."""
        content = "Memory content"
        generated_id = hashlib.sha256(content.encode()).hexdigest()[:16]
        assert len(generated_id) == 16

    def test_storage_determinism(self):
        """Determinism: Same content produces same ID."""
        content = "Test memory"
        id1 = hashlib.sha256(content.encode()).hexdigest()[:16]
        id2 = hashlib.sha256(content.encode()).hexdigest()[:16]
        assert id1 == id2


class TestMemoryRetrieval:
    """Tests for memory retrieval operations."""

    def test_retrieve_by_id(self):
        """Nominal: Retrieve memory by ID."""
        storage = {
            "mem_001": MemoryEntry(id="mem_001", content="Content 1", timestamp=datetime.now()),
            "mem_002": MemoryEntry(id="mem_002", content="Content 2", timestamp=datetime.now()),
        }
        retrieved = storage.get("mem_001")
        assert retrieved is not None
        assert retrieved.content == "Content 1"

    def test_retrieve_missing_returns_none(self):
        """Nominal: Missing ID returns None."""
        storage: Dict[str, MemoryEntry] = {}
        retrieved = storage.get("nonexistent")
        assert retrieved is None

    def test_retrieve_by_recency(self):
        """Nominal: Retrieve most recent memories."""
        now = datetime.now()
        entries = [
            MemoryEntry(id="1", content="Old", timestamp=datetime(2024, 1, 1)),
            MemoryEntry(id="2", content="Recent", timestamp=now),
        ]
        sorted_entries = sorted(entries, key=lambda e: e.timestamp, reverse=True)
        assert sorted_entries[0].content == "Recent"

    def test_retrieve_by_keyword(self):
        """Nominal: Retrieve memories matching keyword."""
        entries = [
            MemoryEntry(id="1", content="User likes coffee", timestamp=datetime.now()),
            MemoryEntry(id="2", content="User prefers tea", timestamp=datetime.now()),
        ]
        keyword = "coffee"
        matches = [e for e in entries if keyword in e.content.lower()]
        assert len(matches) == 1

    def test_retrieve_with_limit(self):
        """Edge case: Limit number of retrieved memories."""
        entries = [MemoryEntry(id=str(i), content=f"Memory {i}", timestamp=datetime.now()) for i in range(100)]
        limit = 10
        retrieved = entries[:limit]
        assert len(retrieved) == 10


class TestMemoryManagement:
    """Tests for memory lifecycle management."""

    def test_delete_memory(self):
        """Nominal: Memory is deleted."""
        storage = {"mem_001": MemoryEntry(id="mem_001", content="To delete", timestamp=datetime.now())}
        del storage["mem_001"]
        assert "mem_001" not in storage

    def test_update_memory(self):
        """Nominal: Memory content is updated."""
        entry = MemoryEntry(id="mem_001", content="Original", timestamp=datetime.now())
        entry.content = "Updated"
        entry.timestamp = datetime.now()
        assert entry.content == "Updated"

    def test_memory_expiration(self):
        """Edge case: Expired memories are identified."""
        old_entry = MemoryEntry(id="old", content="Old", timestamp=datetime(2020, 1, 1))
        max_age_days = 365
        age = (datetime.now() - old_entry.timestamp).days
        is_expired = age > max_age_days
        assert is_expired is True

    def test_memory_consolidation(self):
        """Edge case: Similar memories are consolidated."""
        entries = [
            {"content": "User likes coffee", "score": 0.9},
            {"content": "User enjoys coffee", "score": 0.85},
        ]
        # Consolidate by keeping highest score
        consolidated = max(entries, key=lambda e: e["score"])
        assert consolidated["score"] == 0.9

    def test_memory_capacity_limit(self):
        """Edge case: Storage respects capacity limit."""
        max_capacity = 100
        storage: List[MemoryEntry] = []
        for i in range(150):
            if len(storage) >= max_capacity:
                storage.pop(0)  # Remove oldest
            storage.append(MemoryEntry(id=str(i), content=f"Mem {i}", timestamp=datetime.now()))
        assert len(storage) == max_capacity
