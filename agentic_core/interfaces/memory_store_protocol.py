"""
IMemoryStoreProtocol - Sovereign Protocol for Memory/Vector Store Operations

Zero-Ambiguity Standard: Protocol interface for all memory stores
Category: PROTOCOL (Abstract interface contract)

This protocol defines the contract for any component that stores and retrieves
vector embeddings or memory items. Implementations include InMemoryVectorStore,
PineconeVectorStore, etc.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable


@dataclass
class StoredArtifactRef:
    """Lightweight reference to a stored artifact (no payload)."""

    kind: str
    logical_id: str
    version: int
    path: str
    size_bytes: int

    def __post_init__(self) -> None:
        if not self.kind:
            raise ValueError("kind cannot be empty")
        if not self.logical_id:
            raise ValueError("logical_id cannot be empty")
        if self.version < 0:
            raise ValueError("version must be >= 0")
        if self.size_bytes < 0:
            raise ValueError("size_bytes must be >= 0")


@dataclass
class StoredArtifact:
    """Full artifact with payload, provenance, and metadata."""

    kind: str
    logical_id: str
    payload: dict
    content_type: str
    created_utc: str
    hashes: dict
    metadata: dict

    def __post_init__(self) -> None:
        if not self.kind:
            raise ValueError("kind cannot be empty")
        if not self.logical_id:
            raise ValueError("logical_id cannot be empty")
        if not self.content_type:
            raise ValueError("content_type cannot be empty")
        if not self.created_utc:
            raise ValueError("created_utc cannot be empty")


@runtime_checkable
class IMemoryStoreProtocol(Protocol):
    """
    Protocol defining the memory store contract for sovereign agents.

    Any class implementing this protocol MUST provide:
    - initialize(): Initialize the store
    - upsert(): Insert or update items
    - query(): Query for similar items
    - delete(): Delete items by ID
    """

    async def initialize(self) -> None:
        """
        Initialize the memory store.

        This should set up any connections, create indexes, etc.
        """
        ...

    async def upsert(self, items: list[Any]) -> bool:
        """
        Insert or update memory items.

        Args:
            items: List of memory items to upsert

        Returns:
            True if successful, False otherwise
        """
        ...

    async def query(self, query: Any) -> list[Any]:
        """
        Query for similar memory items.

        Args:
            query: Query object containing vector and filters

        Returns:
            List of matching memory items sorted by relevance
        """
        ...

    async def delete(self, item_ids: list[str]) -> bool:
        """
        Delete memory items by ID.

        Args:
            item_ids: List of item IDs to delete

        Returns:
            True if successful, False otherwise
        """
        ...
