"""
L4 triplet store for resume job alignment workflows.

Implements subject-predicate-object storage for resume enhancement processing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from datetime import datetime, UTC
from enum import Enum
import hashlib


class TemporalType(str, Enum):
    """Temporal classification of facts for resume job alignment workflows."""
    STATIC = "static"          # Unchanging facts (e.g., birthdate)
    DYNAMIC = "dynamic"        # Time-varying facts (e.g., current job)
    ATEMPORAL = "atemporal"    # Facts without temporal dimension


class TripletStatus(str, Enum):
    """Status of triplet in resume job alignment workflow."""
    ACTIVE = "active"
    INVALIDATED = "invalidated"
    SUPERSEDED = "superseded"
    PENDING = "pending"


@dataclass
class Triplet:
    """
    Knowledge graph triplet for resume job alignment workflows.
    
    Represents structured facts for resume enhancement processing.
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
        """Converts resume workflow triplet to natural language for display."""
        return f"{self.subject} {self.predicate} {self.object}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Converts resume workflow triplet to storage format for processing."""
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
        """Creates resume workflow triplet from storage dictionary."""
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
    """Query specification for resume workflow triplet retrieval."""
    
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
    In-memory triplet store for resume job alignment workflows.
    
    Maintains efficient indexes for resume enhancement querying.
    """
    
    def __init__(self):
        """Initializes empty resume workflow triplet store."""
        self._triplets: Dict[str, Triplet] = {}
        self._subject_index: Dict[str, Set[str]] = {}
        self._predicate_index: Dict[str, Set[str]] = {}
        self._object_index: Dict[str, Set[str]] = {}
        self._spo_index: Dict[Tuple[str, str], Set[str]] = {}
    
    def add_triplet(self, triplet: Triplet) -> str:
        """Adds resume workflow triplet to the store for enhancement processing."""
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
        """Adds multiple resume workflow triplets in batch for processing."""
        return [self.add_triplet(t) for t in triplets]
    
    def get_triplet(self, triplet_id: str) -> Optional[Triplet]:
        """Gets resume workflow triplet by ID for enhancement processing."""
        return self._triplets.get(triplet_id)
    
    def query(self, query: TripletQuery) -> List[Triplet]:
        """Queries resume workflow triplets matching specification for enhancement."""
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
        """Gets all objects for resume workflow subject-predicate pair."""
        return self._spo_index.get((subject, predicate), set()).copy()
    
    def get_subjects_for_predicate_object(
        self,
        predicate: str,
        obj: str,
    ) -> List[str]:
        """Gets all subjects with resume workflow predicate pointing to object."""
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
        """Marks resume workflow triplet as invalidated for enhancement processing."""
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
        """Replaces old resume workflow triplet with new one for enhancement."""
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
        """Gets all resume workflow triplets involving entity for enhancement."""
        
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
        """Gets count of resume workflow triplets in store for enhancement."""
        if include_invalidated:
            return len(self._triplets)
        return sum(1 for t in self._triplets.values() if t.status == TripletStatus.ACTIVE)
    
    @staticmethod
    def _add_to_index(index: Dict[str, Set[str]], key: str, value: str) -> None:
        """Adds value to resume workflow index for enhancement processing."""
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
    """Creates new resume workflow triplet with auto-generated ID for enhancement."""
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
