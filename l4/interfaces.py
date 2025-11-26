"""
L4 interfaces for resume job alignment memory and state management.

Defines abstract interfaces for resume enhancement state operations.
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
    """Storage backend types for resume workflow job alignment."""
    VECTOR = "vector"
    GRAPH = "graph"
    DOCUMENT = "document"
    KEY_VALUE = "key_value"
    TEMPORAL = "temporal"


@dataclass
class L4StorageRequest:
    """Input request for resume job alignment storage operations."""
    operation: str
    data: Any
    storage_type: StorageType
    metadata: Optional[Dict[str, Any]] = None
    constraints: Optional[Dict[str, Any]] = None


@dataclass
class L4StorageResult:
    """Output result from resume job alignment storage operations."""
    success: bool
    data: Any
    metadata: Dict[str, Any]
    errors: Optional[List[str]] = None


class L4StateManagerInterface(ABC):
    """Abstract interface for resume job alignment state management."""
    
    @abstractmethod
    async def save_state(self, context: ExecutionContext, state: StateSnapshot) -> bool:
        """Saves resume workflow execution state for job alignment."""
        pass
    
    @abstractmethod
    async def load_state(self, context: ExecutionContext) -> Optional[StateSnapshot]:
        """Loads resume workflow execution state for job alignment."""
        pass
    
    @abstractmethod
    async def delete_state(self, context: ExecutionContext) -> bool:
        """Deletes resume workflow execution state for job alignment."""
        pass
    
    @abstractmethod
    async def list_states(self, filters: Dict[str, Any]) -> List[StateSnapshot]:
        """Lists resume workflow states matching job alignment filters."""
        pass


class L4MemoryManagerInterface(ABC):
    """Interface for resume workflow memory management operations."""
    
    @abstractmethod
    async def store_memory(self, memory: MemoryFragment, context: ExecutionContext) -> bool:
        """Stores resume workflow memory fragment for job alignment."""
        pass
    
    @abstractmethod
    async def retrieve_memory(self, query: str, context: ExecutionContext) -> List[MemoryFragment]:
        """Retrieves resume workflow memory fragments for job alignment."""
        pass
    
    @abstractmethod
    async def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """Updates existing resume workflow memory for job alignment."""
        pass
    
    @abstractmethod
    async def delete_memory(self, memory_id: str) -> bool:
        """Deletes resume workflow memory fragment for job alignment."""
        pass


class L4VectorStoreInterface(ABC):
    """Interface for resume workflow vector storage operations."""
    
    @abstractmethod
    async def store_vectors(self, vectors: List[Dict[str, Any]], metadata: List[Dict[str, Any]]) -> bool:
        """Stores resume workflow vectors with job alignment metadata."""
        pass
    
    @abstractmethod
    async def search_vectors(self, query_vector: List[float], limit: int, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Searches resume workflow vectors for job alignment similarity."""
        pass
    
    @abstractmethod
    async def update_vectors(self, vector_ids: List[str], updates: List[Dict[str, Any]]) -> bool:
        """Updates existing resume workflow vectors for job alignment."""
        pass
    
    @abstractmethod
    async def delete_vectors(self, vector_ids: List[str]) -> bool:
        """Deletes resume workflow vectors for job alignment processing."""
        pass


class L4GraphStoreInterface(ABC):
    """Interface for resume workflow graph storage operations."""
    
    @abstractmethod
    async def store_entities(self, entities: List[Entity]) -> bool:
        """Stores resume workflow entities for job alignment graph."""
        pass
    
    @abstractmethod
    async def store_triplets(self, triplets: List[Triplet]) -> bool:
        """Stores resume workflow triplets for job alignment graph."""
        pass
    
    @abstractmethod
    async def query_graph(self, query: str, parameters: Dict[str, Any]) -> List[Union[Entity, Triplet]]:
        """Queries resume workflow knowledge graph for job alignment."""
        pass
    
    @abstractmethod
    async def resolve_entities(self, entity_names: List[str]) -> List[Entity]:
        """Resolves resume workflow entities for job alignment processing."""
        pass


class L4TemporalKGInterface(ABC):
    """Interface for resume workflow temporal knowledge graph operations."""
    
    @abstractmethod
    async def store_temporal_triplet(self, triplet: Triplet, valid_from: datetime, valid_to: Optional[datetime]) -> bool:
        """Stores resume workflow temporal triplet for job alignment."""
        pass
    
    @abstractmethod
    async def query_temporal_graph(self, query: str, timestamp: datetime, parameters: Dict[str, Any]) -> List[Union[Entity, Triplet]]:
        """Queries resume workflow temporal graph for job alignment."""
        pass
    
    @abstractmethod
    async def get_entity_history(self, entity_id: str, from_time: datetime, to_time: datetime) -> List[Triplet]:
        """Gets resume workflow entity history for job alignment."""
        pass
    
    @abstractmethod
    async def update_temporal_triplet(self, triplet_id: str, updates: Dict[str, Any]) -> bool:
        """Updates resume workflow temporal triplet for job alignment."""
        pass


class L4ProvenanceManagerInterface(ABC):
    """Interface for resume workflow provenance tracking operations."""
    
    @abstractmethod
    async def record_provenance(self, data_id: str, provenance: Provenance) -> bool:
        """Records resume workflow provenance for job alignment data."""
        pass
    
    @abstractmethod
    async def get_provenance(self, data_id: str) -> Optional[Provenance]:
        """Gets resume workflow provenance for job alignment data."""
        pass
    
    @abstractmethod
    async def trace_lineage(self, data_id: str, depth: int) -> List[Provenance]:
        """Traces resume workflow data lineage for job alignment."""
        pass
    
    @abstractmethod
    async def validate_provenance(self, data_id: str, expected_provenance: Provenance) -> bool:
        """Validates resume workflow data provenance for job alignment."""
        pass


class L4CacheInterface(ABC):
    """Interface for resume workflow caching operations."""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Gets resume workflow value from cache for job alignment."""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Sets resume workflow value in cache for job alignment."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Deletes resume workflow value from cache for job alignment."""
        pass
    
    @abstractmethod
    async def clear(self, pattern: Optional[str] = None) -> bool:
        """Clears resume workflow cache values for job alignment."""
        pass
