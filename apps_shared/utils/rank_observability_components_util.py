"""
L2 KG Writer for resume temporal graph data.

Writes entities, relations, and events to Neo4jGraphStore
to support resume timeline analysis and job alignment.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from types import SimpleNamespace
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import emit_determinism_digest

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32

emit_determinism_digest("p0", "rank_observability_components_util")


@dataclass
class TemporalEntity:
    entity_id: str
    entity_type: str = "entity"
    canonical_id: str = ""
    aliases: tuple[str, ...] = ()
    confidence: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TemporalRange:
    valid_at: datetime = field(default_factory=datetime.utcnow)
    invalid_at: datetime | None = None


@dataclass
class TemporalTriplet:
    triplet_id: str
    subject: str = ""
    predicate: str = "related_to"
    object: str = ""
    temporal_range: TemporalRange = field(default_factory=TemporalRange)
    confidence: float = 0.0
    source: str = "unknown"
    status: Any = field(default_factory=lambda: SimpleNamespace(value="active"))
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TemporalEvent:
    event_type: str = ""
    triplet_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


try:
    from agentic_core.L4_state.enforcement.neo4j_store import Neo4jGraphStore
except Exception:
    Neo4jGraphStore = None  # type: ignore[assignment]

try:
    _neo4j_graph: Neo4jGraphStore | None = Neo4jGraphStore() if Neo4jGraphStore else None
    _NEO4J_AVAILABLE = True
except Exception:
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
                name=entity.entity_id,
                metadata={
                    "canonical_id": entity.canonical_id,
                    "aliases": list(entity.aliases),
                    "confidence": entity.confidence,
                    "created_at": entity.created_at.isoformat(),
                    **entity.metadata,
                },
            )
    except (ValueError, TypeError, RuntimeError, KeyError):
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
                invalid_at = event.metadata.get("invalid_at")
                invalidated_by = event.metadata.get("invalidated_by")
                _neo4j_graph.update_relation_invalidity(
                    rel_id=event.triplet_id,
                    invalid_at=invalid_at.isoformat() if isinstance(invalid_at, datetime) else invalid_at,
                    invalidated_by=invalidated_by,
                )
    except (ValueError, TypeError, RuntimeError, KeyError):
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
    for entity in entities:
        await insert_entity(entity)
    for triplet in triplets:
        await insert_triplet(triplet)
    for event in events:
        await insert_event(event)
