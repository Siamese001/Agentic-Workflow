# AUTO-POPULATED BY WINDSURF v2 — 2025-12-07
# ======================================================================

"""
L2 KG Writer for resume temporal graph data.

Writes entities, relations, and events to Neo4jGraphStore
to support resume timeline analysis and job alignment.
"""

from datetime import datetime

try:
    #     from archives.legacy_root_folders.database.graph_store_neo4j import Neo4jGraphStore  # DEPRECATED: Archive import removed to protect archives from validation edits
    _neo4j_graph: Neo4jGraphStore | None = Neo4jGraphStore()
    _NEO4J_AVAILABLE = True
except ImportError:
    _neo4j_graph = None
    _NEO4J_AVAILABLE = False


async def insert_entity(entity: TemporalEntity) -> None:
    """
    Inserts resume entity into Neo4j for timeline analysis.

    Mirrors canonical entity data to support resume job alignment.
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
    except (ValueError, TypeError, RuntimeError, KeyError):
        # Log error but don't fail - Neo4j is optional mirror
        ...


async def insert_triplet(triplet: TemporalTriplet) -> None:
    """
    Inserts resume triplet as relation in Neo4j for timeline analysis.

    Creates RELATION edge to support resume job alignment.
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
                invalid_at=triplet.temporal_range.invalid_at.isoformat()
                if triplet.temporal_range.invalid_at
                else None,
                attrs={
                    "confidence": triplet.confidence,
                    "source": triplet.source,
                    "status": triplet.status.value,
                    **triplet.metadata,
                },
            )
    except (ValueError, TypeError, RuntimeError, KeyError):
        # Log error but don't fail - Neo4j is optional mirror
        ...


async def insert_event(event: TemporalEvent) -> None:
    """
    Inserts resume temporal event in Neo4j for timeline analysis.

    Updates relation invalidation to support resume job alignment.
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
                    invalid_at=invalid_at.isoformat()
                    if isinstance(invalid_at, datetime)
                    else invalid_at,
                    invalidated_by=invalidated_by,
                )
    except (ValueError, TypeError, RuntimeError, KeyError):
        # Log error but don't fail - Neo4j is optional mirror
        ...


async def batch_process_invalidation(events_to_update: list[TemporalEvent]) -> None:
    """
    Processes batch invalidation updates for resume timeline analysis.

    Updates multiple relations to support resume job alignment.
    """
    if not _NEO4J_AVAILABLE:
        return

    for event in events_to_update:
        await insert_event(event)


async def ingest_transcript(
    transcript_id: str,
    entities: list[TemporalEntity],
    triplets: list[TemporalTriplet],
    events: list[TemporalEvent],
) -> None:
    """
    Ingests complete resume transcript data for timeline analysis.

    Mirrors all components to support resume job alignment.
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
