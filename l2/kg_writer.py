"""
L2 KG Writer - Mirrors temporal graph data to Neo4j

Writes entities, relations, and events to Neo4jGraphStore while preserving
existing SQLite/NetworkX behavior for backward compatibility.

Layer: L2 (Execution)
"""

from __future__ import annotations

from typing import List, Optional
from datetime import datetime

try:
    from graph_store_neo4j import Neo4jGraphStore
    _neo4j_graph: Optional[Neo4jGraphStore] = Neo4jGraphStore()
    _NEO4J_AVAILABLE = True
except ImportError:
    _neo4j_graph = None
    _NEO4J_AVAILABLE = False

from state.temporal_schemas import (
    TemporalEntity,
    TemporalTriplet,
    TemporalEvent,
)


async def insert_entity(entity: TemporalEntity) -> None:
    """
    Insert entity into Neo4j while preserving existing behavior.
    
    Mirrors canonical entity data to Neo4jGraphStore.
    """
    if not _NEO4J_AVAILABLE:
        return
        
    try:
        if _neo4j_graph is not None:
            _neo4j_graph.upsert_entity(
                entity_id=entity.entity_id,
                etype=entity.entity_type,
                name=entity.entity_id,  # Use entity_id as name for now
                metadata={
                    "canonical_id": entity.canonical_id,
                    "aliases": list(entity.aliases),
                    "confidence": entity.confidence,
                    "created_at": entity.created_at.isoformat(),
                    **entity.metadata,
                },
            )
    except Exception:
        # Log error but don't fail - Neo4j is optional mirror
        pass


async def insert_triplet(triplet: TemporalTriplet) -> None:
    """
    Insert triplet as relation in Neo4j while preserving existing behavior.
    
    Creates RELATION edge between subject and object entities.
    """
    if not _NEO4J_AVAILABLE:
        return
        
    try:
        if _neo4j_graph is not None:
            _neo4j_graph.upsert_relation(
                rel_id=triplet.triplet_id,
                subject_id=triplet.subject,
                predicate=triplet.predicate,
                object_id=triplet.object,
                valid_at=triplet.temporal_range.valid_at.isoformat(),
                invalid_at=triplet.temporal_range.invalid_at.isoformat() if triplet.temporal_range.invalid_at else None,
                attrs={
                    "confidence": triplet.confidence,
                    "source": triplet.source,
                    "status": triplet.status.value,
                    **triplet.metadata,
                },
            )
    except Exception:
        # Log error but don't fail - Neo4j is optional mirror
        pass


async def insert_event(event: TemporalEvent) -> None:
    """
    Insert temporal event in Neo4j while preserving existing behavior.
    
    Updates relation invalidation if event affects a triplet.
    """
    if not _NEO4J_AVAILABLE:
        return
        
    try:
        if _neo4j_graph is not None:
            if event.triplet_id and event.event_type in ["invalidation", "expiration"]:
                # Update relation invalidity
                invalid_at = event.metadata.get("invalid_at")
                invalidated_by = event.metadata.get("invalidated_by")
                
                _neo4j_graph.update_relation_invalidity(
                    rel_id=event.triplet_id,
                    invalid_at=invalid_at.isoformat() if isinstance(invalid_at, datetime) else invalid_at,
                    invalidated_by=invalidated_by,
                )
    except Exception:
        # Log error but don't fail - Neo4j is optional mirror
        pass


async def batch_process_invalidation(
    events_to_update: List[TemporalEvent]
) -> None:
    """
    Process batch invalidation updates to Neo4j while preserving existing behavior.
    
    Updates multiple relations' invalidity status.
    """
    if not _NEO4J_AVAILABLE:
        return
        
    for event in events_to_update:
        await insert_event(event)


async def ingest_transcript(
    transcript_id: str,
    entities: List[TemporalEntity],
    triplets: List[TemporalTriplet],
    events: List[TemporalEvent],
) -> None:
    """
    Ingest complete transcript data to Neo4j while preserving existing behavior.
    
    Mirrors all transcript components to Neo4jGraphStore.
    """
    if not _NEO4J_AVAILABLE:
        return
        
    # Insert entities first
    for entity in entities:
        await insert_entity(entity)
    
    # Insert triplets as relations
    for triplet in triplets:
        await insert_triplet(triplet)
    
    # Insert events (including invalidations)
    for event in events:
        await insert_event(event)
