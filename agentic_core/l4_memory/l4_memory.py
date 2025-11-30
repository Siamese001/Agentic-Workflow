"""L4 Memory/State Engine - Robust Implementation

Provides memory management, state persistence, and RAG capabilities
for both resume and outreach workflows with robust data handling.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import logging
from datetime import datetime
import json

# Re-export robust implementations from engines
from agentic_core.resume_engine.l4_memory_state.memory.rg_state_manager import (
    ResumeStateManager,
)  # noqa: F401
from agentic_core.resume_engine.l4_memory_state.rag.rg_rag_engine import (
    ResumeRAGEngine,
)  # noqa: F401
from agentic_core.outreach_engine.l4_memory_state.memory.lic_memory import (
    OutreachMemoryManager,
)  # noqa: F401
from agentic_core.outreach_engine.l4_memory_state.rag.lic_rag_policies import (
    get_rag_policy,
)  # noqa: F401

class MemoryType(str, Enum):
    """Types of memory storage."""
    EPISODIC = "episodic"  # Individual interactions/experiences
    SEMANTIC = "semantic"  # General knowledge and facts
    PROCEDURAL = "procedural"  # Workflow processes and patterns
    WORKING = "working"  # Temporary session state

class StorageBackend(str, Enum):
    """Storage backend options."""
    MEMORY = "memory"
    FILE = "file"
    DATABASE = "database"
    VECTOR_DB = "vector_db"

@dataclass
class MemoryEntry:
    """Individual memory entry."""
    entry_id: str
    memory_type: MemoryType
    content: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    access_count: int = 0
    last_accessed: Optional[datetime] = None

@dataclass
class RetrievalQuery:
    """Query for memory retrieval."""
    query_type: MemoryType
    query_text: str
    filters: Dict[str, Any] = field(default_factory=dict)
    limit: int = 10
    similarity_threshold: float = 0.7

@dataclass
class RetrievalResult:
    """Result of memory retrieval."""
    entries: List[MemoryEntry]
    total_found: int
    query_time_ms: int
    metadata: Dict[str, Any] = field(default_factory=dict)

class MemoryManager:
    """
    Robust memory management system supporting multiple storage backends
    and retrieval strategies for both resume and outreach workflows.
    """

    def __init__(
        self,
        backend: StorageBackend = StorageBackend.MEMORY,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.backend = backend
        self.config = config or {}
        self.logger = logging.getLogger(__name__)

        # Initialize specialized memory managers
        self.resume_state_manager = ResumeStateManager()
        self.outreach_memory_manager = OutreachMemoryManager()
        self.resume_rag_engine = ResumeRAGEngine()

        # In-memory storage for other types
        self._memory_store: Dict[str, MemoryEntry] = {}
        self._type_index: Dict[MemoryType, List[str]] = {
            memory_type: [] for memory_type in MemoryType
        }

        # Performance tracking
        self._access_stats: Dict[str, Dict[str, Any]] = {}

    async def store_memory(
        self,
        entry: MemoryEntry,
        workflow_type: Optional[str] = None
    ) -> str:
        """
        Store a memory entry with appropriate backend.
        
        Args:
            entry: Memory entry to store
            workflow_type: Optional workflow type for specialized handling
            
        Returns:
            Entry ID of stored memory
        """
        try:
            if workflow_type == "resume" and entry.memory_type == MemoryType.SEMANTIC:
                # Use resume state manager for resume-related semantic memory
                result = await self.resume_state_manager.store_state(entry.entry_id, entry.content)
                entry_id = result.get("id", entry.entry_id)
            elif workflow_type == "outreach" and entry.memory_type == MemoryType.SEMANTIC:
                # Use outreach memory manager for outreach-related semantic memory
                result = await self.outreach_memory_manager.store_memory(entry.entry_id, entry.content)
                entry_id = result.get("id", entry.entry_id)
            else:
                # Use generic storage
                entry_id = entry.entry_id
                self._memory_store[entry_id] = entry
                self._type_index[entry.memory_type].append(entry_id)

            # Update access statistics
            self._update_access_stats(entry_id, "store")

            self.logger.debug(f"Stored memory entry {entry_id} of type {entry.memory_type}")
            return entry_id

        except Exception as e:
            self.logger.error(f"Failed to store memory entry: {e}")
            raise

    async def retrieve_memory(
        self,
        query: RetrievalQuery,
        workflow_type: Optional[str] = None
    ) -> RetrievalResult:
        """
        Retrieve memory entries based on query.
        
        Args:
            query: Retrieval query parameters
            workflow_type: Optional workflow type for specialized handling
            
        Returns:
            Retrieval results with matching entries
        """
        start_time = asyncio.get_event_loop().time()

        try:
            if workflow_type == "resume" and query.query_type == MemoryType.SEMANTIC:
                # Use resume RAG engine for semantic resume queries
                rag_policy = get_rag_policy("resume")
                results = await self.resume_rag_engine.query(
                    query.query_text,
                    policy=rag_policy,
                    limit=query.limit
                )
                entries = [
                    MemoryEntry(
                        entry_id=result.get("id", ""),
                        memory_type=MemoryType.SEMANTIC,
                        content=result.get("content", {}),
                        metadata=result.get("metadata", {})
                    )
                    for result in results
                ]

            elif workflow_type == "outreach" and query.query_type == MemoryType.SEMANTIC:
                # Use outreach memory manager for semantic outreach queries
                results = await self.outreach_memory_manager.retrieve_memories(
                    query.query_text,
                    filters=query.filters,
                    limit=query.limit
                )
                entries = [
                    MemoryEntry(
                        entry_id=result.get("id", ""),
                        memory_type=MemoryType.SEMANTIC,
                        content=result.get("content", {}),
                        metadata=result.get("metadata", {})
                    )
                    for result in results
                ]

            else:
                # Use generic retrieval
                entries = await self._generic_retrieve(query)

            # Filter by similarity threshold and apply filters
            filtered_entries = []
            for entry in entries:
                # Update access count and timestamp
                entry.access_count += 1
                entry.last_accessed = datetime.now()

                # Apply filters
                if self._matches_filters(entry, query.filters):
                    filtered_entries.append(entry)

            query_time = int((asyncio.get_event_loop().time() - start_time) * 1000)

            result = RetrievalResult(
                entries=filtered_entries[:query.limit],
                total_found=len(filtered_entries),
                query_time_ms=query_time,
                metadata={"query_type": query.query_type, "workflow_type": workflow_type}
            )

            self.logger.debug(f"Retrieved {len(result.entries)} entries in {query_time}ms")
            return result

        except Exception as e:
            query_time = int((asyncio.get_event_loop().time() - start_time) * 1000)
            self.logger.error(f"Memory retrieval failed: {e}")

            return RetrievalResult(
                entries=[],
                total_found=0,
                query_time_ms=query_time,
                metadata={"error": str(e)}
            )

    async def _generic_retrieve(self, query: RetrievalQuery) -> List[MemoryEntry]:
        """Generic retrieval implementation for in-memory storage."""
        entry_ids = self._type_index.get(query.query_type, [])
        entries = []

        for entry_id in entry_ids:
            if entry_id in self._memory_store:
                entry = self._memory_store[entry_id]

                # Simple text matching (can be enhanced with vector similarity)
                if self._text_matches(query.query_text, entry.content):
                    entries.append(entry)

        return entries

    def _text_matches(self, query_text: str, content: Dict[str, Any]) -> bool:
        """Simple text matching for content."""
        query_lower = query_text.lower()
        content_text = json.dumps(content).lower()
        return query_lower in content_text

    def _matches_filters(self, entry: MemoryEntry, filters: Dict[str, Any]) -> bool:
        """Check if entry matches all filters."""
        for key, value in filters.items():
            if key not in entry.metadata:
                return False
            if entry.metadata[key] != value:
                return False
        return True

    async def delete_memory(self, entry_id: str) -> bool:
        """Delete a memory entry."""
        try:
            if entry_id in self._memory_store:
                entry = self._memory_store[entry_id]
                self._type_index[entry.memory_type].remove(entry_id)
                del self._memory_store[entry_id]

                # Clean up access stats
                self._access_stats.pop(entry_id, None)

                self.logger.debug(f"Deleted memory entry {entry_id}")
                return True
            return False

        except Exception as e:
            self.logger.error(f"Failed to delete memory entry {entry_id}: {e}")
            return False

    async def cleanup_expired(self) -> int:
        """Clean up expired memory entries."""
        now = datetime.now()
        expired_ids = []

        for entry_id, entry in self._memory_store.items():
            if entry.expires_at and entry.expires_at < now:
                expired_ids.append(entry_id)

        for entry_id in expired_ids:
            await self.delete_memory(entry_id)

        self.logger.info(f"Cleaned up {len(expired_ids)} expired memory entries")
        return len(expired_ids)

    def _update_access_stats(self, entry_id: str, operation: str) -> None:
        """Update access statistics for monitoring."""
        if entry_id not in self._access_stats:
            self._access_stats[entry_id] = {
                "created": datetime.now(),
                "access_count": 0,
                "last_access": None,
                "operations": []
            }

        stats = self._access_stats[entry_id]
        stats["operations"].append({
            "operation": operation,
            "timestamp": datetime.now()
        })
        stats["last_access"] = datetime.now()

        if operation == "retrieve":
            stats["access_count"] += 1

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory storage statistics."""
        total_entries = len(self._memory_store)
        type_counts = {
            memory_type: len(entry_ids)
            for memory_type, entry_ids in self._type_index.items()
        }

        return {
            "total_entries": total_entries,
            "type_distribution": type_counts,
            "backend": self.backend,
            "access_stats": len(self._access_stats)
        }

# Global memory manager instance
_global_memory_manager: Optional[MemoryManager] = None

def get_memory_manager(
    backend: StorageBackend = StorageBackend.MEMORY,
    config: Optional[Dict[str, Any]] = None
) -> MemoryManager:
    """Get the global memory manager instance."""
    global _global_memory_manager
    if _global_memory_manager is None:
        _global_memory_manager = MemoryManager(backend, config)
    return _global_memory_manager

def reset_memory_manager() -> None:
    """Reset the global memory manager instance (for testing)."""
    global _global_memory_manager
    _global_memory_manager = None

__all__ = [
    "MemoryType",
    "StorageBackend",
    "MemoryEntry",
    "RetrievalQuery",
    "RetrievalResult",
    "MemoryManager",
    "get_memory_manager",
    "reset_memory_manager",
]
