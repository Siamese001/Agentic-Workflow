"""L4 Adapter - Wraps StateManager to implement L4StateManagerInterface

This adapter provides backward compatibility while enforcing strict interface contracts.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

from l4.interfaces import (
    L4StateManagerInterface,
    L4MemoryManagerInterface,
    L4VectorStoreInterface,
    L4GraphStoreInterface,
    L4TemporalKGInterface,
    L4ProvenanceManagerInterface,
    L4CacheInterface,
    L4StorageRequest,
    L4StorageResult,
    StorageType,
)
from l4.state_manager import StateManager, WorkflowState
from core.models.models import (
    ExecutionContext,
    Entity,
    Triplet,
    TemporalKG,
    StateSnapshot,
    MemoryFragment,
    Provenance,
)


class StateManagerAdapter(L4StateManagerInterface):
    """Adapter that wraps StateManager to implement L4 interface."""
    
    def __init__(self, wrapped_state_manager: StateManager):
        self.wrapped_state_manager = wrapped_state_manager
    
    async def save_state(self, context: ExecutionContext, state: StateSnapshot) -> bool:
        """Save execution state using wrapped implementation."""
        try:
            # Convert StateSnapshot to WorkflowState
            workflow_state = WorkflowState(
                job_data=state.metadata.get("job_data"),
                resume_data=state.metadata.get("resume_data"),
                strategy_result=state.metadata.get("strategy_result"),
                draft_result=state.metadata.get("draft_result"),
                metadata=state.metadata,
            )
            
            # Save using wrapped implementation
            self.wrapped_state_manager.save_state(workflow_state)
            return True
            
        except Exception:
            return False
    
    async def load_state(self, context: ExecutionContext) -> Optional[StateSnapshot]:
        """Load execution state using wrapped implementation."""
        try:
            # Load using wrapped implementation
            workflow_state = self.wrapped_state_manager.load_state()
            
            if workflow_state is None:
                return None
            
            # Convert WorkflowState to StateSnapshot
            return StateSnapshot(
                execution_id=context.execution_id,
                timestamp=datetime.now(),
                metadata=workflow_state.metadata,
            )
            
        except Exception:
            return None
    
    async def delete_state(self, context: ExecutionContext) -> bool:
        """Delete execution state."""
        try:
            # Simple implementation - would need to be added to StateManager
            # For now, return True as if deleted
            return True
        except Exception:
            return False
    
    async def list_states(self, filters: Dict[str, Any]) -> List[StateSnapshot]:
        """List states matching filters."""
        # Simple implementation - would need to be added to StateManager
        return []


class MemoryManagerAdapter(L4MemoryManagerInterface):
    """Adapter for memory management operations."""
    
    def __init__(self):
        # Simple in-memory implementation for now
        self._memories: Dict[str, MemoryFragment] = {}
    
    async def store_memory(self, memory: MemoryFragment, context: ExecutionContext) -> bool:
        """Store a memory fragment."""
        try:
            self._memories[memory.id] = memory
            return True
        except Exception:
            return False
    
    async def retrieve_memory(self, query: str, context: ExecutionContext) -> List[MemoryFragment]:
        """Retrieve relevant memory fragments."""
        # Simple keyword matching implementation
        results = []
        query_lower = query.lower()
        for memory in self._memories.values():
            if query_lower in memory.content.lower():
                results.append(memory)
        return results
    
    async def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """Update existing memory."""
        try:
            if memory_id in self._memories:
                memory = self._memories[memory_id]
                for key, value in updates.items():
                    if hasattr(memory, key):
                        setattr(memory, key, value)
                return True
            return False
        except Exception:
            return False
    
    async def delete_memory(self, memory_id: str) -> bool:
        """Delete memory fragment."""
        try:
            if memory_id in self._memories:
                del self._memories[memory_id]
                return True
            return False
        except Exception:
            return False


class VectorStoreAdapter(L4VectorStoreInterface):
    """Adapter for vector storage operations."""
    
    def __init__(self):
        # Simple in-memory implementation for now
        self._vectors: Dict[str, List[float]] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}
    
    async def store_vectors(self, vectors: List[Dict[str, Any]], metadata: List[Dict[str, Any]]) -> bool:
        """Store vectors with metadata."""
        try:
            for i, vector_data in enumerate(vectors):
                vector_id = vector_data.get("id", f"vector_{i}")
                vector = vector_data.get("vector", [])
                self._vectors[vector_id] = vector
                if i < len(metadata):
                    self._metadata[vector_id] = metadata[i]
            return True
        except Exception:
            return False
    
    async def search_vectors(self, query_vector: List[float], limit: int, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for similar vectors."""
        # Simple implementation - would use proper similarity search
        results = []
        for vector_id, vector in self._vectors.items():
            if len(results) >= limit:
                break
            results.append({
                "id": vector_id,
                "vector": vector,
                "metadata": self._metadata.get(vector_id, {}),
                "similarity": 0.8,  # Placeholder
            })
        return results
    
    async def update_vectors(self, vector_ids: List[str], updates: List[Dict[str, Any]]) -> bool:
        """Update existing vectors."""
        try:
            for i, vector_id in enumerate(vector_ids):
                if vector_id in self._vectors and i < len(updates):
                    update = updates[i]
                    if "vector" in update:
                        self._vectors[vector_id] = update["vector"]
                    if "metadata" in update:
                        self._metadata[vector_id].update(update["metadata"])
            return True
        except Exception:
            return False
    
    async def delete_vectors(self, vector_ids: List[str]) -> bool:
        """Delete vectors."""
        try:
            for vector_id in vector_ids:
                if vector_id in self._vectors:
                    del self._vectors[vector_id]
                if vector_id in self._metadata:
                    del self._metadata[vector_id]
            return True
        except Exception:
            return False


class GraphStoreAdapter(L4GraphStoreInterface):
    """Adapter for graph storage operations."""
    
    def __init__(self):
        # Simple in-memory implementation for now
        self._entities: Dict[str, Entity] = {}
        self._triplets: List[Triplet] = []
    
    async def store_entities(self, entities: List[Entity]) -> bool:
        """Store entities in the graph."""
        try:
            for entity in entities:
                self._entities[entity.id] = entity
            return True
        except Exception:
            return False
    
    async def store_triplets(self, triplets: List[Triplet]) -> bool:
        """Store triplets in the graph."""
        try:
            self._triplets.extend(triplets)
            return True
        except Exception:
            return False
    
    async def query_graph(self, query: str, parameters: Dict[str, Any]) -> List[Entity | Triplet]:
        """Query the knowledge graph."""
        # Simple implementation - would use proper graph query language
        results = []
        if "entity" in query.lower():
            results.extend(list(self._entities.values()))
        if "triplet" in query.lower():
            results.extend(self._triplets)
        return results
    
    async def resolve_entities(self, entity_names: List[str]) -> List[Entity]:
        """Resolve entity names to canonical entities."""
        results = []
        for name in entity_names:
            for entity in self._entities.values():
                if entity.name == name or entity.id == name:
                    results.append(entity)
                    break
        return results


class TemporalKGAdapter(L4TemporalKGInterface):
    """Adapter for temporal knowledge graph operations."""
    
    def __init__(self):
        self._temporal_triplets: List[Triplet] = []
    
    async def store_temporal_triplet(self, triplet: Triplet, valid_from: datetime, valid_to: Optional[datetime]) -> bool:
        """Store a temporal triplet."""
        try:
            # Add temporal metadata to triplet
            triplet.temporal_metadata = {
                "valid_from": valid_from.isoformat(),
                "valid_to": valid_to.isoformat() if valid_to else None,
            }
            self._temporal_triplets.append(triplet)
            return True
        except Exception:
            return False
    
    async def query_temporal_graph(self, query: str, timestamp: datetime, parameters: Dict[str, Any]) -> List[Entity | Triplet]:
        """Query the temporal knowledge graph at a specific time."""
        results = []
        for triplet in self._temporal_triplets:
            if self._is_valid_at_time(triplet, timestamp):
                results.append(triplet)
        return results
    
    async def get_entity_history(self, entity_id: str, from_time: datetime, to_time: datetime) -> List[Triplet]:
        """Get entity history within time range."""
        results = []
        for triplet in self._temporal_triplets:
            if self._involves_entity(triplet, entity_id) and self._overlaps_time_range(triplet, from_time, to_time):
                results.append(triplet)
        return results
    
    async def update_temporal_triplet(self, triplet_id: str, updates: Dict[str, Any]) -> bool:
        """Update temporal triplet."""
        # Simple implementation - would need proper indexing
        return True
    
    def _is_valid_at_time(self, triplet: Triplet, timestamp: datetime) -> bool:
        """Check if triplet is valid at given timestamp."""
        if not hasattr(triplet, 'temporal_metadata'):
            return True
        
        valid_from = datetime.fromisoformat(triplet.temporal_metadata.get("valid_from", "1970-01-01"))
        valid_to = triplet.temporal_metadata.get("valid_to")
        if valid_to:
            valid_to = datetime.fromisoformat(valid_to)
        
        return valid_from <= timestamp and (valid_to is None or timestamp <= valid_to)
    
    def _involves_entity(self, triplet: Triplet, entity_id: str) -> bool:
        """Check if triplet involves the given entity."""
        return triplet.subject == entity_id or triplet.object == entity_id
    
    def _overlaps_time_range(self, triplet: Triplet, from_time: datetime, to_time: datetime) -> bool:
        """Check if triplet time range overlaps with given range."""
        if not hasattr(triplet, 'temporal_metadata'):
            return True
        
        valid_from = datetime.fromisoformat(triplet.temporal_metadata.get("valid_from", "1970-01-01"))
        valid_to = triplet.temporal_metadata.get("valid_to")
        if valid_to:
            valid_to = datetime.fromisoformat(valid_to)
        
        return valid_from <= to_time and (valid_to is None or from_time <= valid_to)


class ProvenanceManagerAdapter(L4ProvenanceManagerInterface):
    """Adapter for provenance tracking operations."""
    
    def __init__(self):
        self._provenance: Dict[str, Provenance] = {}
    
    async def record_provenance(self, data_id: str, provenance: Provenance) -> bool:
        """Record provenance for data."""
        try:
            self._provenance[data_id] = provenance
            return True
        except Exception:
            return False
    
    async def get_provenance(self, data_id: str) -> Optional[Provenance]:
        """Get provenance for data."""
        return self._provenance.get(data_id)
    
    async def trace_lineage(self, data_id: str, depth: int) -> List[Provenance]:
        """Trace data lineage."""
        # Simple implementation - would follow provenance chain
        results = []
        current = self._provenance.get(data_id)
        while current and len(results) < depth:
            results.append(current)
            if current.parent_id:
                current = self._provenance.get(current.parent_id)
            else:
                break
        return results
    
    async def validate_provenance(self, data_id: str, expected_provenance: Provenance) -> bool:
        """Validate data provenance."""
        actual = self._provenance.get(data_id)
        return actual == expected_provenance


class CacheAdapter(L4CacheInterface):
    """Adapter for caching operations."""
    
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._ttl: Dict[str, datetime] = {}
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key not in self._cache:
            return None
        
        # Check TTL
        if key in self._ttl:
            if datetime.now() > self._ttl[key]:
                del self._cache[key]
                del self._ttl[key]
                return None
        
        return self._cache[key]
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL."""
        try:
            self._cache[key] = value
            if ttl:
                self._ttl[key] = datetime.now() + timedelta(seconds=ttl)
            return True
        except Exception:
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        try:
            if key in self._cache:
                del self._cache[key]
            if key in self._ttl:
                del self._ttl[key]
            return True
        except Exception:
            return False
    
    async def clear(self, pattern: Optional[str] = None) -> bool:
        """Clear cache values matching pattern."""
        try:
            if pattern:
                keys_to_delete = [k for k in self._cache.keys() if pattern in k]
                for key in keys_to_delete:
                    del self._cache[key]
                    if key in self._ttl:
                        del self._ttl[key]
            else:
                self._cache.clear()
                self._ttl.clear()
            return True
        except Exception:
            return False
