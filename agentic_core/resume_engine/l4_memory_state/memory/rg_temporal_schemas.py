from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

class TemporalRelation(str, Enum):
    """Temporal relationship types."""
    BEFORE = "before"
    AFTER = "after"
    DURING = "during"
    OVERLAPS = "overlaps"
    MEETS = "meets"
    STARTS = "starts"
    ENDS = "ends"

@dataclass
class TemporalEntity:
    """Represents a temporal entity with time-based properties."""
    entity_id: str
    entity_type: str
    start_time: datetime
    end_time: Optional[datetime] = None
    properties: Dict[str, Any] = None
    confidence: float = 1.0

    def __post_init__(self):
        if self.properties is None:
            self.properties = {}

    def process(self, *args, **kwargs) -> Any:
        """Process temporal entity with validation."""
        duration = None
        if self.end_time:
            duration = (self.end_time - self.start_time).total_seconds()
        
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": duration,
            "processed": True,
            "confidence": self.confidence
        }

    def is_active_at(self, timestamp: datetime) -> bool:
        """Check if entity is active at given timestamp."""
        if timestamp < self.start_time:
            return False
        if self.end_time and timestamp > self.end_time:
            return False
        return True

@dataclass
class TemporalEvent:
    """Represents a discrete temporal event."""
    event_id: str
    event_type: str
    timestamp: datetime
    participants: List[str] = None
    properties: Dict[str, Any] = None
    severity: str = "info"

    def __post_init__(self):
        if self.participants is None:
            self.participants = []
        if self.properties is None:
            self.properties = {}

    def process(self, *args, **kwargs) -> Any:
        """Process temporal event with context."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "participants": self.participants,
            "severity": self.severity,
            "processed": True
        }

@dataclass
class TemporalRange:
    """Represents a temporal range with validation."""
    range_id: str
    start: datetime
    end: datetime
    range_type: str = "generic"
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.start > self.end:
            raise ValueError("Start time must be before end time")

    def process(self, *args, **kwargs) -> Any:
        """Process temporal range with duration calculation."""
        duration = (self.end - self.start).total_seconds()
        return {
            "range_id": self.range_id,
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
            "duration_seconds": duration,
            "range_type": self.range_type,
            "processed": True
        }

    def contains(self, timestamp: datetime) -> bool:
        """Check if timestamp is within range."""
        return self.start <= timestamp <= self.end

    def overlaps(self, other: 'TemporalRange') -> bool:
        """Check if this range overlaps with another."""
        return self.start <= other.end and other.start <= self.end

@dataclass
class TemporalTriplet:
    """Represents a temporal relationship between entities."""
    subject_id: str
    relation: TemporalRelation
    object_id: str
    timestamp: datetime
    confidence: float = 1.0
    context: Dict[str, Any] = None

    def __post_init__(self):
        if self.context is None:
            self.context = {}

    def process(self, *args, **kwargs) -> Any:
        """Process temporal triplet with validation."""
        return {
            "subject": self.subject_id,
            "relation": self.relation.value,
            "object": self.object_id,
            "timestamp": self.timestamp.isoformat(),
            "confidence": self.confidence,
            "processed": True
        }

    def invert(self) -> 'TemporalTriplet':
        """Create inverted triplet (swap subject/object with inverse relation)."""
        inverse_relations = {
            TemporalRelation.BEFORE: TemporalRelation.AFTER,
            TemporalRelation.AFTER: TemporalRelation.BEFORE,
            TemporalRelation.DURING: TemporalRelation.DURING,
            TemporalRelation.OVERLAPS: TemporalRelation.OVERLAPS,
            TemporalRelation.MEETS: TemporalRelation.MEETS,
            TemporalRelation.STARTS: TemporalRelation.ENDS,
            TemporalRelation.ENDS: TemporalRelation.STARTS,
        }
        
        return TemporalTriplet(
            subject_id=self.object_id,
            relation=inverse_relations.get(self.relation, self.relation),
            object_id=self.subject_id,
            timestamp=self.timestamp,
            confidence=self.confidence,
            context=self.context.copy()
        )
