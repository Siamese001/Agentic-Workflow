"""
Triplet store for résumé processing knowledge graph management.

Implements triplet (subject, predicate, object) storage for temporal knowledge graph systems supporting résumé enhancement workflows.

Layer: L4 (State & Memory)
Responsibilities:
- Store and retrieve triplets for résumé processing data
- Index triplets for efficient querying in résumé enhancement workflows
- Support temporal validity ranges for accurate résumé information
- Provide entity-centric views for résumé knowledge graph operations

Non-responsibilities:
- Triplet extraction from text (L2)
- Query planning (L1)
- Orchestration (L3)
- Policy enforcement (L5)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from datetime import datetime, UTC
from enum import Enum
import hashlib


class TemporalType(str, Enum):
    """Temporal classification of facts for résumé processing knowledge graphs."""
    STATIC = "static"          # Unchanging facts (e.g., birthdate)
    DYNAMIC = "dynamic"        # Time-varying facts (e.g., current job)
    ATEMPORAL = "atemporal"    # Facts without temporal dimension


class TripletStatus(str, Enum):
    """Status of a triplet in résumé processing knowledge graph."""
    ACTIVE = "active"
    INVALIDATED = "invalidated"
    SUPERSEDED = "superseded"
    PENDING = "pending"


@dataclass
class Triplet:
    """
    Knowledge graph triplet with temporal metadata for résumé processing.
    
    Represents structured facts extracted from résumé enhancement workflows.
    """
    
    id: str
    subject: str
    predicate: str
    object: str
    
    # Temporal metadata
    temporal_type: TemporalType = TemporalType.DYNAMIC
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    extracted_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    
    # Provenance
    source: str = "extraction"
    confidence: float = 1.0
    evidence_ids: List[str] = field(default_factory=list)
    
    # Status
    status: TripletStatus = TripletStatus.ACTIVE
    invalidated_by: Optional[str] = None
    invalidation_reason: Optional[str] = None
    
    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_text(self) -> str:
        """Convert résumé processing triplet to natural language for display."""
        return f"{self.subject} {self.predicate} {self.object}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert résumé processing triplet to dictionary for persistent storage."""
        return {
            "id": self.id,
            "subject": self.subject,
            "predicate": self.predicate,
            "object": self.object,
            "temporal_type": self.temporal_type.value,
            "valid_from": self.valid_from.isoformat() if self.valid_from else None,
            "valid_until": self.valid_until.isoformat() if self.valid_until else None,
            "extracted_at": self.extracted_at.isoformat(),
            "source": self.source,
            "confidence": self.confidence,
            "evidence_ids": self.evidence_ids,
            "status": self.status.value,
            "invalidated_by": self.invalidated_by,
            "invalidation_reason": self.invalidation_reason,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Triplet":
        """Create triplet from dictionary."""
        return cls(
            id=data["id"],
            subject=data["subject"],
            predicate=data["predicate"],
            object=data["object"],
            temporal_type=TemporalType(data.get("temporal_type", "dynamic")),
            valid_from=datetime.fromisoformat(data["valid_from"]) if data.get("valid_from") else None,
            valid_until=datetime.fromisoformat(data["valid_until"]) if data.get("valid_until") else None,
            extracted_at=datetime.fromisoformat(data["extracted_at"]) if data.get("extracted_at") else datetime.now(UTC),
            source=data.get("source", "extraction"),
            confidence=data.get("confidence", 1.0),
            evidence_ids=data.get("evidence_ids", []),
            status=TripletStatus(data.get("status", "active")),
            invalidated_by=data.get("invalidated_by"),
            invalidation_reason=data.get("invalidation_reason"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class TripletQuery:
    """Query specification for résumé processing triplet retrieval."""
    
    subject: Optional[str] = None
    predicate: Optional[str] = None
    object: Optional[str] = None
    
    # Temporal filters
    valid_at: Optional[datetime] = None
    temporal_type: Optional[TemporalType] = None
    
    # Status filters
    include_invalidated: bool = False
    min_confidence: float = 0.0
    
    # Pagination
    limit: int = 100
    offset: int = 0


class TripletStore:
    """
    In-memory triplet store with indexing for résumé processing workflows.
    
    Maintains efficient indexes for résumé enhancement querying:
    - Subject index: subject -> list of triplet IDs
    - Predicate index: predicate -> list of triplet IDs
    - Object index: object -> list of triplet IDs
    - SPO index: (subject, predicate) -> list of objects
    """
    
    def __init__(self):
        """Initialize empty résumé processing triplet store."""
        self._triplets: Dict[str, Triplet] = {}
        self._subject_index: Dict[str, Set[str]] = {}
        self._predicate_index: Dict[str, Set[str]] = {}
        self._object_index: Dict[str, Set[str]] = {}
        self._spo_index: Dict[Tuple[str, str], Set[str]] = {}
    
    def add_triplet(self, triplet: Triplet) -> str:
        """Add a résumé processing triplet to the store.
        
        Args:
            triplet: Triplet to add for résumé enhancement workflows
            
        Returns:
            Triplet ID for résumé processing reference
        """
        # Store triplet
        self._triplets[triplet.id] = triplet
        
        # Update indexes
        self._add_to_index(self._subject_index, triplet.subject, triplet.id)
        self._add_to_index(self._predicate_index, triplet.predicate, triplet.id)
        self._add_to_index(self._object_index, triplet.object, triplet.id)
        
        spo_key = (triplet.subject, triplet.predicate)
        if spo_key not in self._spo_index:
            self._spo_index[spo_key] = set()
        self._spo_index[spo_key].add(triplet.object)
        
        return triplet.id
    
    def add_triplets(self, triplets: List[Triplet]) -> List[str]:
        """Add multiple résumé processing triplets in batch.
        
        Args:
            triplets: List of triplets to add for résumé enhancement workflows
            
        Returns:
            List of triplet IDs for résumé processing reference
        """
        return [self.add_triplet(t) for t in triplets]
    
    def get_triplet(self, triplet_id: str) -> Optional[Triplet]:
        """Get a résumé processing triplet by ID.
        
        Args:
            triplet_id: Triplet ID for résumé processing reference
            
        Returns:
            Triplet if found, None otherwise
        """
        return self._triplets.get(triplet_id)
    
    def query(self, query: TripletQuery) -> List[Triplet]:
        """Query résumé processing triplets matching the specification.
        
        Args:
            query: Query specification for résumé enhancement workflows
            
        Returns:
            List of matching résumé processing triplets
        """
        # Start with candidate set
        candidates: Optional[Set[str]] = None
        
        if query.subject:
            subject_ids = self._subject_index.get(query.subject, set())
            candidates = subject_ids if candidates is None else candidates & subject_ids
        
        if query.predicate:
            predicate_ids = self._predicate_index.get(query.predicate, set())
            candidates = predicate_ids if candidates is None else candidates & predicate_ids
        
        if query.object:
            object_ids = self._object_index.get(query.object, set())
            candidates = object_ids if candidates is None else candidates & object_ids
        
        # If no filters, return all
        if candidates is None:
            candidates = set(self._triplets.keys())
        
        # Filter and collect results
        results: List[Triplet] = []
        for triplet_id in candidates:
            triplet = self._triplets.get(triplet_id)
            if triplet is None:
                continue
            
            # Apply filters
            if not query.include_invalidated and triplet.status != TripletStatus.ACTIVE:
                continue
            
            if triplet.confidence < query.min_confidence:
                continue
            
            if query.temporal_type and triplet.temporal_type != query.temporal_type:
                continue
            
            if query.valid_at:
                if triplet.valid_from and triplet.valid_from > query.valid_at:
                    continue
                if triplet.valid_until and triplet.valid_until < query.valid_at:
                    continue
            
            results.append(triplet)
        
        # Apply pagination
        results = results[query.offset:query.offset + query.limit]
        
        return results
    
    def get_objects_for_subject_predicate(
        self,
        subject: str,
        predicate: str,
    ) -> Set[str]:
        """Get all objects for résumé processing subject-predicate pair.
        
        Args:
            subject: Subject entity for résumé enhancement workflows
            predicate: Predicate/relation for résumé processing
            
        Returns:
            Set of object values for résumé processing queries
        """
        return self._spo_index.get((subject, predicate), set()).copy()
    
    def get_subjects_for_predicate_object(
        self,
        predicate: str,
        obj: str,
    ) -> List[str]:
        """Get all subjects that have résumé processing predicate pointing to object.
        
        Args:
            predicate: Predicate/relation for résumé enhancement workflows
            obj: Object value for résumé processing queries
            
        Returns:
            List of subject entities for résumé processing
        """
        results = []
        for triplet in self._triplets.values():
            if (triplet.predicate == predicate and 
                triplet.object == obj and 
                triplet.status == TripletStatus.ACTIVE):
                results.append(triplet.subject)
        return results
    
    def invalidate_triplet(
        self,
        triplet_id: str,
        reason: str,
        invalidated_by: Optional[str] = None,
    ) -> bool:
        """Mark a résumé processing triplet as invalidated.
        
        Args:
            triplet_id: ID of résumé processing triplet to invalidate
            reason: Reason for invalidation in résumé enhancement workflows
            invalidated_by: ID of superseding triplet for résumé processing (if any)
            
        Returns:
            True if résumé processing triplet was found and invalidated
        """
        triplet = self._triplets.get(triplet_id)
        if triplet is None:
            return False
        
        triplet.status = TripletStatus.INVALIDATED
        triplet.invalidation_reason = reason
        triplet.invalidated_by = invalidated_by
        triplet.valid_until = datetime.now(UTC)
        
        return True
    
    def supersede_triplet(
        self,
        old_triplet_id: str,
        new_triplet: Triplet,
        reason: str = "updated",
    ) -> str:
        """Replace an old triplet with a new one.
        
        Args:
            old_triplet_id: ID of triplet to supersede
            new_triplet: New triplet
            reason: Reason for supersession
            
        Returns:
            ID of new triplet
        """
        # Mark old triplet as superseded
        old_triplet = self._triplets.get(old_triplet_id)
        if old_triplet:
            old_triplet.status = TripletStatus.SUPERSEDED
            old_triplet.invalidated_by = new_triplet.id
            old_triplet.invalidation_reason = reason
            old_triplet.valid_until = datetime.now(UTC)
        
        # Add new triplet
        return self.add_triplet(new_triplet)
    
    def get_entity_triplets(self, entity: str) -> List[Triplet]:
        """Get all triplets involving an entity (as subject or object).
        
        Args:
            entity: Entity identifier
            
        Returns:
            List of triplets involving the entity
        """
        triplet_ids = set()
        triplet_ids.update(self._subject_index.get(entity, set()))
        triplet_ids.update(self._object_index.get(entity, set()))
        
        return [
            self._triplets[tid]
            for tid in triplet_ids
            if tid in self._triplets and self._triplets[tid].status == TripletStatus.ACTIVE
        ]
    
    def count(self, include_invalidated: bool = False) -> int:
        """Get count of triplets in store.
        
        Args:
            include_invalidated: Whether to include invalidated triplets
            
        Returns:
            Count of triplets
        """
        if include_invalidated:
            return len(self._triplets)
        return sum(1 for t in self._triplets.values() if t.status == TripletStatus.ACTIVE)
    
    @staticmethod
    def _add_to_index(index: Dict[str, Set[str]], key: str, value: str) -> None:
        """Add a value to an index."""
        if key not in index:
            index[key] = set()
        index[key].add(value)


# =============================================================================
# Triplet Creation Helpers
# =============================================================================

def create_triplet(
    subject: str,
    predicate: str,
    obj: str,
    temporal_type: TemporalType = TemporalType.DYNAMIC,
    confidence: float = 1.0,
    source: str = "extraction",
    valid_from: Optional[datetime] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Triplet:
    """Create a new résumé processing triplet with auto-generated ID.
    
    Args:
        subject: Subject entity for résumé enhancement workflows
        predicate: Predicate/relation for résumé processing
        obj: Object value for résumé processing queries
        temporal_type: Temporal classification for résumé processing facts
        confidence: Confidence score for résumé enhancement workflows
        source: Source of résumé processing extraction
        valid_from: Validity start time for accurate résumé information
        metadata: Additional metadata for résumé processing context
        
    Returns:
        Created résumé processing triplet with unique ID
    """
    # Generate deterministic ID
    id_input = f"{subject}|{predicate}|{obj}|{datetime.now(UTC).isoformat()}"
    triplet_id = hashlib.sha256(id_input.encode()).hexdigest()[:16]
    
    return Triplet(
        id=triplet_id,
        subject=subject,
        predicate=predicate,
        object=obj,
        temporal_type=temporal_type,
        confidence=confidence,
        source=source,
        valid_from=valid_from or datetime.now(UTC),
        metadata=metadata or {},
    )


# =============================================================================
# Predicate Definitions
# =============================================================================

# Common predicates for resume/job domain
PREDICATES = {
    # Skills
    "has_skill": "has_skill",
    "proficient_in": "proficient_in",
    "certified_in": "certified_in",
    
    # Experience
    "worked_at": "worked_at",
    "held_role": "held_role",
    "managed": "managed",
    "reported_to": "reported_to",
    
    # Education
    "attended": "attended",
    "graduated_from": "graduated_from",
    "has_degree": "has_degree",
    
    # Job relationships
    "applied_to": "applied_to",
    "interviewed_at": "interviewed_at",
    "offered_by": "offered_by",
    
    # Requirements
    "requires_skill": "requires_skill",
    "prefers_skill": "prefers_skill",
    "requires_experience": "requires_experience",
}


__all__ = [
    "TemporalType",
    "TripletStatus",
    "Triplet",
    "TripletQuery",
    "TripletStore",
    "create_triplet",
    "PREDICATES",
]
