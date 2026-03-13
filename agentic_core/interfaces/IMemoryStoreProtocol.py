"""
IMemoryStoreProtocol - Sovereign Protocol for Memory/Vector Store Operations

Zero-Ambiguity Standard: Protocol interface for all memory stores
Category: PROTOCOL (Abstract interface contract)

This protocol defines the contract for any component that stores and retrieves
vector embeddings or memory items. Implementations include InMemoryVectorStore,
PineconeVectorStore, etc.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


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
