"""Knowledge Graph retrieval planning for outreach campaigns."""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

# Import EntityType from L4 module as expected by tests
from agentic_core.l4_memory_state.temporal.entity_resolution import EntityType

class QueryType(Enum):
    """Knowledge graph query type enumeration."""
    ENTITY_LOOKUP = "entity_lookup"
    RELATIONSHIP_SEARCH = "relationship_search"
    PATH_FINDING = "path_finding"
    NEIGHBORHOOD_SEARCH = "neighborhood_search"
    REASONING_QUERY = "reasoning_query"
    NEIGHBORHOOD = "neighborhood"
    PATTERN_MATCH = "pattern_match"
    ENTITY_FACTS = "entity_facts"

class HopDirection(Enum):
    """Knowledge graph hop direction enumeration."""
    FORWARD = "forward"
    BACKWARD = "backward"
    BIDIRECTIONAL = "bidirectional"
    OUTGOING = "outgoing"
    INCOMING = "incoming"

@dataclass
class KGQuery:
    """Knowledge graph query structure."""
    entity: str = ""
    relation: str = ""
    target: str = ""
    constraints: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class KGResult:
    """Knowledge graph retrieval result."""
    query: KGQuery = field(default_factory=KGQuery)
    results: List[Dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.8
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class KGQueryPlan:
    """Knowledge graph query plan structure."""
    query_id: str = ""
    primary_entity: str = ""
    target_entity: str = ""
    query_type: str = "entity_lookup"
    relationship_types: List[str] = field(default_factory=list)
    traversal_depth: int = 3
    constraints: Dict[str, Any] = field(default_factory=dict)
    reasoning_enabled: bool = True
    priority: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if not self.query_id:
            self.query_id = f"kg_query_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

class KGRetrievalPlanner:
    """Knowledge Graph retrieval planning engine."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.kg_endpoint = self.config.get("kg_endpoint", "default")
        self.max_results = self.config.get("max_results", 10)
        self.planning_history = []

    def plan_query(self, query: str, context: Dict[str, Any] = None, query_type: str = "entity_lookup") -> KGQueryPlan:
        """Plan a KG query."""
        return KGQueryPlan(
            primary_entity=query,
            target_entity="",
            query_type=query_type,
            relationship_types=["related_to", "part_of"],
            constraints=context or {},
            reasoning_enabled=True,
            metadata={"query_type": query_type}
        )

    def plan_retrieval(self, query: KGQuery) -> KGResult:
        """Plan KG retrieval based on query."""
        return KGResult(
            query=query,
            results=[],
            confidence=0.9,
            execution_time=0.1,
            metadata={"planned_endpoint": self.kg_endpoint}
        )

    def execute_retrieval(self, query: KGQuery) -> KGResult:
        """Execute KG retrieval and return results."""
        # Mock implementation
        mock_results = [
            {"entity": query.entity, "relation": query.relation, "target": query.target},
            {"entity": query.entity, "relation": "related_to", "target": "concept"}
        ]
        return KGResult(
            query=query,
            results=mock_results[:self.max_results],
            confidence=0.8,
            execution_time=0.5,
            metadata={"endpoint": self.kg_endpoint, "results_count": len(mock_results)}
        )

    def refine_query(self, initial_query: KGQuery, feedback: Dict[str, Any]) -> KGQuery:
        """Refine KG query based on feedback."""
        refined = KGQuery(
            entity=initial_query.entity,
            relation=feedback.get("suggested_relation", initial_query.relation),
            target=initial_query.target,
            constraints={**initial_query.constraints, **feedback.get("additional_constraints", {})},
            metadata={**initial_query.metadata, "refined": True}
        )
        return refined

def plan_entity_retrieval(entity_name: str, entity_type: Optional[EntityType] = None,
                         entity_id: str = "", constraints: Dict[str, Any] = None,
                         predicates: List[str] = None) -> KGQueryPlan:
    """Plan entity retrieval from knowledge graph."""
    return KGQueryPlan(
        primary_entity=entity_name,
        target_entity="",
        relationship_types=predicates or ["related_to", "part_of", "works_for"],
        constraints=constraints or {},
        reasoning_enabled=True,
        metadata={
            "entity_type": entity_type.value if entity_type else "unknown",
            "entity_id": entity_id
        }
    )
