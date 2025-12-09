"""L4 Interfaces - Memory & State Layer

This module defines abstract interfaces for all L4 memory and state operations.
All L4 implementations must inherit from these interfaces.

Layer: L4 (Memory & State)
Responsibilities:
- State persistence and retrieval
- Memory management
- Data storage operations
- Temporal knowledge graphs
- Entity resolution

Non-responsibilities:
- Planning (L1)
- Tool execution (L2)
- Orchestration (L3)
- Safety/policy decisions (L5)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Sequence, Union
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from core.models.models import (
    ExecutionContext,
    Entity,
    Triplet,
    TemporalKG,
    StateSnapshot,
    MemoryFragment,
    Provenance,
)


class StorageType(Enum):
    """Types of storage backends."""
    VECTOR = "vector"
    GRAPH = "graph"
    DOCUMENT = "document"
    KEY_VALUE = "key_value"
    TEMPORAL = "temporal"


@dataclass
class L4StorageRequest:
    """Input request for L4 storage operations."""
    operation: str
    data: Any
    storage_type: StorageType
    metadata: Optional[Dict[str, Any]] = None
    constraints: Optional[Dict[str, Any]] = None


@dataclass
class L4StorageResult:
    """Output result from L4 storage operations."""
    success: bool
    data: Any
    metadata: Dict[str, Any]
    errors: Optional[List[str]] = None


class L4StateManagerInterface(ABC):
    """Abstract interface for state management operations."""
    
    @abstractmethod
    async def save_state(self, context: ExecutionContext, state: StateSnapshot) -> bool:
        """Save execution state."""
        pass
    
    @abstractmethod
    async def load_state(self, context: ExecutionContext) -> Optional[StateSnapshot]:
        """Load execution state."""
        pass
    
    @abstractmethod
    async def delete_state(self, context: ExecutionContext) -> bool:
        """Delete execution state."""
        pass
    
    @abstractmethod
    async def list_states(self, filters: Dict[str, Any]) -> List[StateSnapshot]:
        """List states matching filters."""
        pass


class L4MemoryManagerInterface(ABC):
    """Interface for memory management operations."""
    
    @abstractmethod
    async def store_memory(self, memory: MemoryFragment, context: ExecutionContext) -> bool:
        """Store a memory fragment."""
        pass
    
    @abstractmethod
    async def retrieve_memory(self, query: str, context: ExecutionContext) -> List[MemoryFragment]:
        """Retrieve relevant memory fragments."""
        pass
    
    @abstractmethod
    async def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """Update existing memory."""
        pass
    
    @abstractmethod
    async def delete_memory(self, memory_id: str) -> bool:
        """Delete memory fragment."""
        pass


class L4VectorStoreInterface(ABC):
    """Interface for vector storage operations."""
    
    @abstractmethod
    async def store_vectors(self, vectors: List[Dict[str, Any]], metadata: List[Dict[str, Any]]) -> bool:
        """Store vectors with metadata."""
        pass
    
    @abstractmethod
    async def search_vectors(self, query_vector: List[float], limit: int, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for similar vectors."""
        pass
    
    @abstractmethod
    async def update_vectors(self, vector_ids: List[str], updates: List[Dict[str, Any]]) -> bool:
        """Update existing vectors."""
        pass
    
    @abstractmethod
    async def delete_vectors(self, vector_ids: List[str]) -> bool:
        """Delete vectors."""
        pass


class L4GraphStoreInterface(ABC):
    """Interface for graph storage operations."""
    
    @abstractmethod
    async def store_entities(self, entities: List[Entity]) -> bool:
        """Store entities in the graph."""
        pass
    
    @abstractmethod
    async def store_triplets(self, triplets: List[Triplet]) -> bool:
        """Store triplets in the graph."""
        pass
    
    @abstractmethod
    async def query_graph(self, query: str, parameters: Dict[str, Any]) -> List[Union[Entity, Triplet]]:
        """Query the knowledge graph."""
        pass
    
    @abstractmethod
    async def resolve_entities(self, entity_names: List[str]) -> List[Entity]:
        """Resolve entity names to canonical entities."""
        pass


class L4TemporalKGInterface(ABC):
    """Interface for temporal knowledge graph operations."""
    
    @abstractmethod
    async def store_temporal_triplet(self, triplet: Triplet, valid_from: datetime, valid_to: Optional[datetime]) -> bool:
        """Store a temporal triplet."""
        pass
    
    @abstractmethod
    async def query_temporal_graph(self, query: str, timestamp: datetime, parameters: Dict[str, Any]) -> List[Union[Entity, Triplet]]:
        """Query the temporal knowledge graph at a specific time."""
        pass
    
    @abstractmethod
    async def get_entity_history(self, entity_id: str, from_time: datetime, to_time: datetime) -> List[Triplet]:
        """Get entity history within time range."""
        pass
    
    @abstractmethod
    async def update_temporal_triplet(self, triplet_id: str, updates: Dict[str, Any]) -> bool:
        """Update temporal triplet."""
        pass


class L4ProvenanceManagerInterface(ABC):
    """Interface for provenance tracking operations."""
    
    @abstractmethod
    async def record_provenance(self, data_id: str, provenance: Provenance) -> bool:
        """Record provenance for data."""
        pass
    
    @abstractmethod
    async def get_provenance(self, data_id: str) -> Optional[Provenance]:
        """Get provenance for data."""
        pass
    
    @abstractmethod
    async def trace_lineage(self, data_id: str, depth: int) -> List[Provenance]:
        """Trace data lineage."""
        pass
    
    @abstractmethod
    async def validate_provenance(self, data_id: str, expected_provenance: Provenance) -> bool:
        """Validate data provenance."""
        pass


class L4CacheInterface(ABC):
    """Interface for caching operations."""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        pass
    
    @abstractmethod
    async def clear(self, pattern: Optional[str] = None) -> bool:
        """Clear cache values matching pattern."""
        pass
