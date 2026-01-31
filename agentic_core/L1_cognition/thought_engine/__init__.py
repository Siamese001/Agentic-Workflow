"""
L1 Cognition Memory module.

Provides memory management capabilities for cognitive agents.
"""

import logging
from typing import Any, Dict, List, Optional  # noqa: F401

logger = logging.getLogger(__name__)


class MemoryStore:
    """Base memory store for agents."""

    def __init__(self):
        self._memories: dict[str, Any] = {}

    def store(self, key: str, value: Any) -> None:
        """Store a memory."""
        self._memories[key] = value

    def retrieve(self, key: str) -> Any | None:
        """Retrieve a memory."""
        return self._memories.get(key)

    def delete(self, key: str) -> None:
        """Delete a memory."""
        if key in self._memories:
            del self._memories[key]

    def list_keys(self) -> list[str]:
        """List all memory keys."""
        return list(self._memories.keys())

    def clear(self) -> None:
        """Clear all memories."""
        self._memories.clear()


class WorkingMemory(MemoryStore):
    """Short-term working memory."""

    pass


class LongTermMemory(MemoryStore):
    """Long-term persistent memory."""

    pass


__all__ = ["MemoryStore", "WorkingMemory", "LongTermMemory"]
