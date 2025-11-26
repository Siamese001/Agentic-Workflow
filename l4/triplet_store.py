"""
L4 Triplet Store for resume job alignment workflows.

Maintains efficient indexes for resume enhancement querying.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, UTC
from typing import Any, Dict, List, Optional, Set, Tuple
from enum import Enum


class TemporalType(Enum):
    """Temporal classification of facts for resume job alignment workflows."""
    STATIC = "static"
    DYNAMIC = "dynamic"
    TEMPORARY = "temporary"


class TripletStatus(Enum):
    """Status of triplet in resume job alignment workflow."""
    ACTIVE = "active"
    INVALIDATED = "invalidated"
    ARCHIVED = "archived"


@dataclass
class Triplet:
    """
    Resume workflow triplet representing a relationship between entities.
    
    Used for resume enhancement and job alignment processing.
    """
    id: str
    subject: str
    predicate: str
    object: str
    temporal_type: TemporalType = TemporalType.DYNAMIC
    confidence: float = 1.0
    source: str = "extraction"
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    status: TripletStatus = TripletStatus.ACTIVE
    metadata: Optional[Dict[str, Any]] = None
    
    def to_natural_language(self) -> str:
        """Converts resume workflow triplet to natural language for display."""
        return f"{self.subject} {self.predicate} {self.object}"
    
    def to_storage_dict(self) -> Dict[str, Any]:
        """Converts resume workflow triplet to storage format for processing."""
        return {
            "id": self.id,
            "subject": self.subject,
            "predicate": self.predicate,
            "object": self.object,
            "temporal_type": self.temporal_type.value,
            "confidence": self.confidence,
            "source": self.source,
            "valid_from": self.valid_from.isoformat() if self.valid_from else None,
            "valid_until": self.valid_until.isoformat() if self.valid_until else None,
            "status": self.status.value,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_storage_dict(cls, data: Dict[str, Any]) -> "Triplet":
        """Creates resume workflow triplet from storage dictionary."""
        return cls(
            id=data["id"],
            subject=data["subject"],
            predicate=data["predicate"],
            object=data["object"],
            temporal_type=TemporalType(data["temporal_type"]),
            confidence=data["confidence"],
            source=data["source"],
            valid_from=datetime.fromisoformat(data["valid_from"]) if data["valid_from"] else None,
            valid_until=datetime.fromisoformat(data["valid_until"]) if data["valid_until"] else None,
            status=TripletStatus(data["status"]),
            metadata=data.get("metadata"),
        )


@dataclass
class TripletQuery:
    """Query specification for resume workflow triplet retrieval."""
    subject: Optional[str] = None
    predicate: Optional[str] = None
    object: Optional[str] = None
    temporal_type: Optional[TemporalType] = None
    status: TripletStatus = TripletStatus.ACTIVE
    valid_at: Optional[datetime] = None
    metadata_filter: Optional[Dict[str, Any]] = None


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
        
        if candidates is None:
            candidates = set(self._triplets.keys())
        
        # Filter by status and other criteria
        results = []
        for triplet_id in candidates:
            triplet = self._triplets.get(triplet_id)
            if triplet and triplet.status == query.status:
                if query.temporal_type and triplet.temporal_type != query.temporal_type:
                    continue
                if query.valid_at and not self._is_valid_at(triplet, query.valid_at):
                    continue
                if query.metadata_filter and not self._matches_metadata(triplet, query.metadata_filter):
                    continue
                results.append(triplet)
        
        return results
    
    def get_objects_for_subject_predicate(self, subject: str, predicate: str) -> List[str]:
        """Gets all objects for resume workflow subject-predicate pair."""
        spo_key = (subject, predicate)
        return list(self._spo_index.get(spo_key, set()))
    
    def get_subjects_for_predicate_object(self, predicate: str, obj: str) -> List[str]:
        """Gets all subjects with resume workflow predicate pointing to object."""
        subjects = []
        for subject, predicate_key in self._spo_index.keys():
            if predicate_key == predicate and obj in self._spo_index[(subject, predicate_key)]:
                subjects.append(subject)
        return subjects
    
    def invalidate_triplet(self, triplet_id: str) -> bool:
        """Marks resume workflow triplet as invalidated for enhancement processing."""
        triplet = self._triplets.get(triplet_id)
        if triplet:
            triplet.status = TripletStatus.INVALIDATED
            return True
        return False
    
    def replace_triplet(self, old_triplet_id: str, new_triplet: Triplet) -> Optional[str]:
        """Replaces old resume workflow triplet with new one for enhancement processing."""
        if old_triplet_id in self._triplets:
            self.invalidate_triplet(old_triplet_id)
            return self.add_triplet(new_triplet)
        return None
    
    def get_triplets_for_entity(self, entity: str) -> List[Triplet]:
        """Gets all resume workflow triplets involving entity for enhancement."""
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
    
    def _is_valid_at(self, triplet: Triplet, valid_at: datetime) -> bool:
        """Checks if resume workflow triplet is valid at given time."""
        if triplet.valid_from and valid_at < triplet.valid_from:
            return False
        if triplet.valid_until and valid_at > triplet.valid_until:
            return False
        return True
    
    def _matches_metadata(self, triplet: Triplet, filter_dict: Dict[str, Any]) -> bool:
        """Checks if resume workflow triplet matches metadata filter."""
        if not triplet.metadata:
            return False
        for key, value in filter_dict.items():
            if triplet.metadata.get(key) != value:
                return False
        return True


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
        metadata=metadata,
    )


PREDICATES = {
    # Skills
    "has_skill": "has_skill",
    "proficient_in": "proficient_in",
    "certified_in": "certified_in",
    
    # Experience
    "worked_at": "worked_at",
    "held_role": "held_role",
    "managed": "managed",
    
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
