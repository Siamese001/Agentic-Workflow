"""Triplet store for temporal knowledge graph operations."""
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class TripletStatus(Enum):
    """Status enumeration for triplets."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    VERIFIED = "verified"
    DEPRECATED = "deprecated"

@dataclass
class TripletQuery:
    """Query structure for triplet retrieval."""
    subject: str = ""
    predicate: str = ""
    object: str = ""
    status: Optional[TripletStatus] = None
    temporal_range: Optional[Tuple[datetime, datetime]] = None
    constraints: Dict[str, Any] = field(default_factory=dict)
    limit: int = 100
    offset: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Triplet:
    """Knowledge graph triplet with temporal metadata."""
    id: str = ""
    subject: str = ""
    predicate: str = ""
    object: str = ""
    confidence: float = 0.8
    status: TripletStatus = TripletStatus.ACTIVE
    source: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    valid_from: datetime = field(default_factory=datetime.now)
    valid_until: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.id:
            self.id = f"triplet_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(self.subject + self.predicate + self.object)}"

class TripletStore:
    """Temporal triplet store for knowledge graph operations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize triplet store with configuration."""
        self.config = config or {}
        self.triplets = {}
        self.indexes = {
            "subject": {},
            "predicate": {},
            "object": {},
            "status": {}
        }
        self.stats = {
            "total_triplets": 0,
            "triplets_by_status": {},
            "last_query_time": 0.0,
            "query_count": 0
        }
    
    def add_triplet(self, triplet: Triplet) -> bool:
        """Add a triplet to the store."""
        if triplet.id in self.triplets:
            return False
        
        # Store triplet
        self.triplets[triplet.id] = triplet
        
        # Update indexes
        self._update_indexes(triplet, "add")
        
        # Update stats
        self.stats["total_triplets"] += 1
        status_key = triplet.status.value
        self.stats["triplets_by_status"][status_key] = self.stats["triplets_by_status"].get(status_key, 0) + 1
        
        return True
    
    def query_triplets(self, query: TripletQuery) -> Dict[str, Any]:
        """Query triplets based on criteria."""
        start_time = datetime.now()
        
        # Start with all triplets
        candidates = list(self.triplets.values())
        
        # Apply filters
        if query.subject:
            candidates = [t for t in candidates if t.subject == query.subject]
        
        if query.predicate:
            candidates = [t for t in candidates if t.predicate == query.predicate]
        
        if query.object:
            candidates = [t for t in candidates if t.object == query.object]
        
        if query.status:
            candidates = [t for t in candidates if t.status == query.status]
        
        # Sort by confidence (descending)
        candidates.sort(key=lambda t: t.confidence, reverse=True)
        
        # Apply pagination
        total_count = len(candidates)
        paginated_candidates = candidates[query.offset:query.offset + query.limit]
        
        query_time = (datetime.now() - start_time).total_seconds()
        
        # Update stats
        self.stats["last_query_time"] = query_time
        self.stats["query_count"] += 1
        
        return {
            "triplets": paginated_candidates,
            "total_count": total_count,
            "query_time": query_time,
            "metadata": {
                "query_subject": query.subject,
                "query_predicate": query.predicate,
                "query_object": query.object
            }
        }
    
    def _update_indexes(self, triplet: Triplet, operation: str) -> None:
        """Update indexes when adding or removing triplets."""
        if operation == "add":
            # Subject index
            if triplet.subject not in self.indexes["subject"]:
                self.indexes["subject"][triplet.subject] = set()
            self.indexes["subject"][triplet.subject].add(triplet.id)
            
            # Predicate index
            if triplet.predicate not in self.indexes["predicate"]:
                self.indexes["predicate"][triplet.predicate] = set()
            self.indexes["predicate"][triplet.predicate].add(triplet.id)
            
            # Object index
            if triplet.object not in self.indexes["object"]:
                self.indexes["object"][triplet.object] = set()
            self.indexes["object"][triplet.object].add(triplet.id)
            
            # Status index
            if triplet.status.value not in self.indexes["status"]:
                self.indexes["status"][triplet.status.value] = set()
            self.indexes["status"][triplet.status.value].add(triplet.id)

def create_triplet(subject: str, predicate: str, object: str,
                  confidence: float = 0.8, source: str = "",
                  metadata: Dict[str, Any] = None) -> Triplet:
    """Factory function to create a triplet."""
    return Triplet(
        subject=subject,
        predicate=predicate,
        object=object,
        confidence=confidence,
        source=source,
        metadata=metadata or {}
    )
