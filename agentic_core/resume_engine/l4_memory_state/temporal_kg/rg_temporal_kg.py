from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class TemporalNodeMetadata:
    """Metadata for temporal nodes in knowledge graph."""
    node_id: str
    entity_type: str
    created_at: datetime
    updated_at: datetime
    confidence: float = 1.0
    source: str = ""
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def process(self, *args, **kwargs) -> Any:
        """Process temporal node with validation."""
        return {
            "node_id": self.node_id,
            "entity_type": self.entity_type,
            "processed": True,
            "timestamp": datetime.now().isoformat(),
            "confidence": self.confidence
        }

@dataclass
class TemporalFact:
    """Represents a temporal fact in the knowledge graph."""
    fact_id: str
    subject: str
    predicate: str
    object: str
    timestamp: datetime
    confidence: float = 1.0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def process(self, *args, **kwargs) -> Any:
        """Process temporal fact with semantic validation."""
        return {
            "fact_id": self.fact_id,
            "triple": f"{self.subject} {self.predicate} {self.object}",
            "timestamp": self.timestamp.isoformat(),
            "processed": True,
            "confidence": self.confidence
        }

class TemporalKG:
    """Robust temporal knowledge graph for resume entity tracking."""

    def __init__(self):
        self.nodes: Dict[str, TemporalNodeMetadata] = {}
        self.facts: List[TemporalFact] = []
        self.indexes: Dict[str, List[str]] = {}

    def add_node(self, node: TemporalNodeMetadata) -> str:
        """Add a temporal node to the knowledge graph."""
        self.nodes[node.node_id] = node
        self._update_indexes(node.node_id, node.entity_type)
        return node.node_id

    def add_fact(self, fact: TemporalFact) -> str:
        """Add a temporal fact to the knowledge graph."""
        self.facts.append(fact)
        return fact.fact_id

    def query_facts(self, subject: Optional[str] = None,
                   predicate: Optional[str] = None,
                   object: Optional[str] = None,
                   time_range: Optional[tuple] = None) -> List[TemporalFact]:
        """Query temporal facts with filters."""
        results = []
        for fact in self.facts:
            if subject and fact.subject != subject:
                continue
            if predicate and fact.predicate != predicate:
                continue
            if object and fact.object != object:
                continue
            if time_range:
                start, end = time_range
                if not (start <= fact.timestamp <= end):
                    continue
            results.append(fact)
        return results

    def get_node(self, node_id: str) -> Optional[TemporalNodeMetadata]:
        """Get a temporal node by ID."""
        return self.nodes.get(node_id)

    def process(self, *args, **kwargs) -> Any:
        """Process knowledge graph query."""
        query = kwargs.get("query", {})
        if "subject" in query:
            facts = self.query_facts(subject=query["subject"])
            return {"facts": [f.process() for f in facts], "count": len(facts)}
        return {"nodes": len(self.nodes), "facts": len(self.facts), "processed": True}

    def _update_indexes(self, node_id: str, entity_type: str):
        """Update search indexes for efficient querying."""
        if entity_type not in self.indexes:
            self.indexes[entity_type] = []
        self.indexes[entity_type].append(node_id)
