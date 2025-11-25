"""L4 Temporal Knowledge Graph Schemas

Extended schemas for temporal KG self-healing, ingestion, and fusion.
Layer: L4 (State & Memory) - Pure data definitions and persistence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from datetime import datetime, UTC
from enum import Enum
import hashlib
import json

from .types import StatePath, StateTransition, StateSnapshot


class TemporalFactStatus(str, Enum):
    """Status of temporal facts in the knowledge graph."""
    ACTIVE = "active"
    INVALIDATED = "invalidated"
    PENDING_VALIDATION = "pending_validation"
    CONFLICTED = "conflicted"
    STALE = "stale"


class ConflictType(str, Enum):
    """Types of conflicts detected in temporal facts."""
    OVERLAPPING_FACTS = "overlapping_facts"
    CONTRADICTORY_PREDICATES = "contradictory_predicates"
    TEMPORAL_INCONSISTENCY = "temporal_inconsistency"
    ENTITY_IDENTITY_CONFLICT = "entity_identity_conflict"
    DUPLICATE_TRIPLETS = "duplicate_triplets"


@dataclass(frozen=True)
class TemporalRange:
    """Immutable temporal range for fact validity."""
    valid_at: datetime
    invalid_at: Optional[datetime] = None
    
    def is_valid_at(self, timestamp: datetime) -> bool:
        """Check if this range is valid at the given timestamp."""
        return self.valid_at <= timestamp and (
            self.invalid_at is None or timestamp < self.invalid_at
        )
    
    def overlaps_with(self, other: TemporalRange) -> bool:
        """Check if this range overlaps with another."""
        start = max(self.valid_at, other.valid_at)
        end = min(
            self.invalid_at or datetime.max.replace(tzinfo=UTC),
            other.invalid_at or datetime.max.replace(tzinfo=UTC)
        )
        return start < end
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "valid_at": self.valid_at.isoformat(),
            "invalid_at": self.invalid_at.isoformat() if self.invalid_at else None,
        }


@dataclass(frozen=True)
class TemporalEntity:
    """Immutable entity in the temporal knowledge graph."""
    entity_id: str
    entity_type: str
    canonical_id: Optional[str] = None
    aliases: Set[str] = field(default_factory=set)
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "canonical_id": self.canonical_id,
            "aliases": list(self.aliases),
            "confidence": self.confidence,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class TemporalTriplet:
    """Immutable triplet in the temporal knowledge graph."""
    triplet_id: str
    subject: str
    predicate: str
    object: str
    temporal_range: TemporalRange
    confidence: float = 1.0
    source: str = "system"
    status: TemporalFactStatus = TemporalFactStatus.ACTIVE
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_text(self) -> str:
        """Convert triplet to natural language text."""
        validity = f" (valid from {self.temporal_range.valid_at.isoformat()}"
        if self.temporal_range.invalid_at:
            validity += f" until {self.temporal_range.invalid_at.isoformat()}"
        validity += ")"
        return f"{self.subject} {self.predicate} {self.object}{validity}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "triplet_id": self.triplet_id,
            "subject": self.subject,
            "predicate": self.predicate,
            "object": self.object,
            "temporal_range": self.temporal_range.to_dict(),
            "confidence": self.confidence,
            "source": self.source,
            "status": self.status.value,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class TemporalEvent:
    """Immutable temporal event for tracking changes."""
    event_id: str
    event_type: str
    entity_id: Optional[str] = None
    triplet_id: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "entity_id": self.entity_id,
            "triplet_id": self.triplet_id,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class ConflictDetection:
    """Immutable conflict detection result."""
    conflict_id: str
    conflict_type: ConflictType
    affected_triplets: List[str]
    description: str
    severity: str = "medium"
    detected_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "conflict_id": self.conflict_id,
            "conflict_type": self.conflict_type.value,
            "affected_triplets": self.affected_triplets,
            "description": self.description,
            "severity": self.severity,
            "detected_at": self.detected_at.isoformat(),
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class IngestionBatch:
    """Immutable batch for ingestion tracking."""
    batch_id: str
    source_id: str
    document_count: int
    triplet_count: int
    status: str = "pending"
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "batch_id": self.batch_id,
            "source_id": self.source_id,
            "document_count": self.document_count,
            "triplet_count": self.triplet_count,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class FusionSession:
    """Immutable fusion session tracking."""
    session_id: str
    user_query: str
    temporal_constraints: Optional[Dict[str, Any]] = None
    safety_profile: Optional[str] = None
    retrieval_plan: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "session_id": self.session_id,
            "user_query": self.user_query,
            "temporal_constraints": self.temporal_constraints,
            "safety_profile": self.safety_profile,
            "retrieval_plan": self.retrieval_plan,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "metadata": self.metadata,
        }


# =============================================================================
# State Management Extensions
# =============================================================================

@dataclass(frozen=True)
class TemporalKGState:
    """Complete state of the temporal knowledge graph."""
    entities: Dict[str, TemporalEntity] = field(default_factory=dict)
    triplets: Dict[str, TemporalTriplet] = field(default_factory=dict)
    events: List[TemporalEvent] = field(default_factory=list)
    conflicts: List[ConflictDetection] = field(default_factory=list)
    ingestion_batches: Dict[str, IngestionBatch] = field(default_factory=dict)
    fusion_sessions: Dict[str, FusionSession] = field(default_factory=dict)
    
    def with_entity(self, entity: TemporalEntity) -> TemporalKGState:
        """Create new state with added/updated entity."""
        new_entities = self.entities.copy()
        new_entities[entity.entity_id] = entity
        return TemporalKGState(
            entities=new_entities,
            triplets=self.triplets,
            events=self.events,
            conflicts=self.conflicts,
            ingestion_batches=self.ingestion_batches,
            fusion_sessions=self.fusion_sessions,
        )
    
    def with_triplet(self, triplet: TemporalTriplet) -> TemporalKGState:
        """Create new state with added/updated triplet."""
        new_triplets = self.triplets.copy()
        new_triplets[triplet.triplet_id] = triplet
        return TemporalKGState(
            entities=self.entities,
            triplets=new_triplets,
            events=self.events,
            conflicts=self.conflicts,
            ingestion_batches=self.ingestion_batches,
            fusion_sessions=self.fusion_sessions,
        )
    
    def with_event(self, event: TemporalEvent) -> TemporalKGState:
        """Create new state with added event."""
        new_events = self.events + [event]
        return TemporalKGState(
            entities=self.entities,
            triplets=self.triplets,
            events=new_events,
            conflicts=self.conflicts,
            ingestion_batches=self.ingestion_batches,
            fusion_sessions=self.fusion_sessions,
        )


# =============================================================================
# Factory Functions
# =============================================================================

def create_temporal_triplet(
    subject: str,
    predicate: str,
    object: str,
    valid_at: datetime,
    invalid_at: Optional[datetime] = None,
    confidence: float = 1.0,
    source: str = "system",
    metadata: Optional[Dict[str, Any]] = None,
) -> TemporalTriplet:
    """Create a temporal triplet with generated ID."""
    triplet_hash = hashlib.sha256(
        f"{subject}_{predicate}_{object}_{valid_at.isoformat()}".encode()
    ).hexdigest()[:16]
    
    return TemporalTriplet(
        triplet_id=f"triplet_{triplet_hash}",
        subject=subject,
        predicate=predicate,
        object=object,
        temporal_range=TemporalRange(valid_at=valid_at, invalid_at=invalid_at),
        confidence=confidence,
        source=source,
        metadata=metadata or {},
    )


def create_temporal_entity(
    entity_id: str,
    entity_type: str,
    canonical_id: Optional[str] = None,
    aliases: Optional[Set[str]] = None,
    confidence: float = 1.0,
    metadata: Optional[Dict[str, Any]] = None,
) -> TemporalEntity:
    """Create a temporal entity."""
    return TemporalEntity(
        entity_id=entity_id,
        entity_type=entity_type,
        canonical_id=canonical_id,
        aliases=aliases or set(),
        confidence=confidence,
        metadata=metadata or {},
    )


def create_conflict_detection(
    conflict_type: ConflictType,
    affected_triplets: List[str],
    description: str,
    severity: str = "medium",
    metadata: Optional[Dict[str, Any]] = None,
) -> ConflictDetection:
    """Create a conflict detection result."""
    conflict_hash = hashlib.sha256(
        f"{conflict_type.value}_{','.join(sorted(affected_triplets))}_{description}".encode()
    ).hexdigest()[:16]
    
    return ConflictDetection(
        conflict_id=f"conflict_{conflict_hash}",
        conflict_type=conflict_type,
        affected_triplets=affected_triplets,
        description=description,
        severity=severity,
        metadata=metadata or {},
    )


__all__ = [
    "TemporalFactStatus",
    "ConflictType",
    "TemporalRange",
    "TemporalEntity",
    "TemporalTriplet",
    "TemporalEvent",
    "ConflictDetection",
    "IngestionBatch",
    "FusionSession",
    "TemporalKGState",
    "create_temporal_triplet",
    "create_temporal_entity",
    "create_conflict_detection",
]
