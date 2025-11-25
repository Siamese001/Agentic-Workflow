"""
Knowledge graph retrieval planning for résumé processing workflows.

Implements L1 planning for multi-hop knowledge graph retrieval to support comprehensive résumé enhancement operations.

Layer: L1 (Planning)
Responsibilities:
- Plan multi-hop KG traversal paths for résumé data retrieval
- Decompose complex résumé queries into traversal steps
- Determine hop count and entity filters for résumé matching
- Plan temporal constraint application for accurate résumé information

Non-responsibilities:
- Graph traversal execution (L2)
- Triplet storage (L4)
- Orchestration (L3)
- Policy enforcement (L5)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from datetime import datetime, UTC
from enum import Enum


class HopDirection(str, Enum):
    """Direction of traversal in résumé processing knowledge graph."""
    OUTGOING = "outgoing"    # Subject -> Object
    INCOMING = "incoming"    # Object <- Subject
    BIDIRECTIONAL = "both"   # Both directions


class QueryType(str, Enum):
    """Type of résumé processing KG query."""
    ENTITY_FACTS = "entity_facts"           # All facts about an entity
    PATH_FINDING = "path_finding"           # Find path between entities
    NEIGHBORHOOD = "neighborhood"           # N-hop neighborhood
    PATTERN_MATCH = "pattern_match"         # Match specific pattern
    TEMPORAL_SLICE = "temporal_slice"       # Facts valid at time T


@dataclass
class HopSpec:
    """Specification for a single hop in résumé processing multi-hop traversal."""
    
    hop_number: int
    direction: HopDirection
    
    # Filters
    predicate_filter: Optional[List[str]] = None
    entity_type_filter: Optional[List[str]] = None
    
    # Limits
    max_results: int = 100
    min_confidence: float = 0.0
    
    # Temporal constraints
    valid_at: Optional[datetime] = None
    include_invalidated: bool = False


@dataclass
class KGQueryPlan:
    """Plan for résumé processing knowledge graph query execution."""
    
    query_id: str
    query_type: QueryType
    
    # Starting point(s)
    start_entities: List[str]
    
    # Target (for path finding)
    target_entities: Optional[List[str]] = None
    
    # Hop specifications
    hops: List[HopSpec] = field(default_factory=list)
    max_hops: int = 3
    
    # Global filters
    predicate_whitelist: Optional[Set[str]] = None
    predicate_blacklist: Optional[Set[str]] = None
    
    # Temporal constraints
    temporal_constraint: Optional[datetime] = None
    
    # Aggregation
    aggregate_results: bool = True
    deduplicate: bool = True
    
    # Context
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PathTemplate:
    """Template for résumé processing known traversal pattern."""
    
    name: str
    description: str
    hops: List[HopSpec]
    
    # Conditions for applying this template
    applicable_query_types: List[QueryType]
    required_predicates: Optional[List[str]] = None


class KGRetrievalPlanner:
    """
    Planner for résumé processing multi-hop knowledge graph retrieval.
    
    Creates execution plans for KG queries in résumé enhancement workflows.
    """
    
    def __init__(self):
        """Initialize planner with path templates."""
        self._templates = self._build_templates()
    
    def _build_templates(self) -> Dict[str, PathTemplate]:
        """Build predefined path templates."""
        return {
            # Find skills of companies where person worked
            "person_company_skills": PathTemplate(
                name="person_company_skills",
                description="Find skills used at companies where person worked",
                hops=[
                    HopSpec(
                        hop_number=1,
                        direction=HopDirection.OUTGOING,
                        predicate_filter=["worked_at"],
                    ),
                    HopSpec(
                        hop_number=2,
                        direction=HopDirection.INCOMING,
                        predicate_filter=["requires_skill", "prefers_skill"],
                    ),
                ],
                applicable_query_types=[QueryType.NEIGHBORHOOD, QueryType.PATTERN_MATCH],
            ),
            
            # Find people with similar skills
            "similar_skills": PathTemplate(
                name="similar_skills",
                description="Find entities with similar skills",
                hops=[
                    HopSpec(
                        hop_number=1,
                        direction=HopDirection.OUTGOING,
                        predicate_filter=["has_skill"],
                    ),
                    HopSpec(
                        hop_number=2,
                        direction=HopDirection.INCOMING,
                        predicate_filter=["has_skill"],
                    ),
                ],
                applicable_query_types=[QueryType.NEIGHBORHOOD],
            ),
            
            # Find job requirements chain
            "job_requirements": PathTemplate(
                name="job_requirements",
                description="Find all requirements for a job",
                hops=[
                    HopSpec(
                        hop_number=1,
                        direction=HopDirection.OUTGOING,
                        predicate_filter=["requires_skill", "requires_experience", "prefers_skill"],
                        max_results=50,
                    ),
                ],
                applicable_query_types=[QueryType.ENTITY_FACTS],
            ),
            
            # Career path traversal
            "career_path": PathTemplate(
                name="career_path",
                description="Traverse career history",
                hops=[
                    HopSpec(
                        hop_number=1,
                        direction=HopDirection.OUTGOING,
                        predicate_filter=["worked_at", "held_role"],
                    ),
                    HopSpec(
                        hop_number=2,
                        direction=HopDirection.OUTGOING,
                        predicate_filter=["part_of", "subsidiary_of"],
                    ),
                ],
                applicable_query_types=[QueryType.NEIGHBORHOOD, QueryType.PATH_FINDING],
            ),
        }
    
    def plan_query(
        self,
        query_type: QueryType,
        start_entities: List[str],
        target_entities: Optional[List[str]] = None,
        predicates: Optional[List[str]] = None,
        max_hops: int = 3,
        temporal_constraint: Optional[datetime] = None,
        template_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> KGQueryPlan:
        """Create a query plan for résumé processing KG retrieval.
        
        Args:
            query_type: Type of résumé processing query
            start_entities: Starting entities for résumé data traversal
            target_entities: Target entities for résumé path finding
            predicates: Specific predicates to traverse for résumé matching
            max_hops: Maximum number of hops for résumé data retrieval
            temporal_constraint: Optional temporal filter for accurate résumé information
            template_name: Optional template to use for résumé processing patterns
            context: Additional context for résumé enhancement workflows
            
        Returns:
            KGQueryPlan for résumé processing execution
        """
        # Generate query ID
        query_id = f"kg_query_{datetime.now(UTC).strftime('%Y%m%d%H%M%S%f')}"
        
        # Use template if specified
        if template_name and template_name in self._templates:
            template = self._templates[template_name]
            return self._plan_from_template(
                query_id, template, start_entities, target_entities,
                temporal_constraint, context
            )
        
        # Otherwise, build plan based on query type
        if query_type == QueryType.ENTITY_FACTS:
            return self._plan_entity_facts(
                query_id, start_entities, predicates, temporal_constraint, context
            )
        
        elif query_type == QueryType.PATH_FINDING:
            return self._plan_path_finding(
                query_id, start_entities, target_entities or [],
                max_hops, temporal_constraint, context
            )
        
        elif query_type == QueryType.NEIGHBORHOOD:
            return self._plan_neighborhood(
                query_id, start_entities, max_hops, predicates,
                temporal_constraint, context
            )
        
        elif query_type == QueryType.TEMPORAL_SLICE:
            return self._plan_temporal_slice(
                query_id, start_entities, temporal_constraint or datetime.now(UTC),
                predicates, context
            )
        
        else:
            # Default plan
            return self._plan_neighborhood(
                query_id, start_entities, max_hops, predicates,
                temporal_constraint, context
            )
    
    def _plan_from_template(
        self,
        query_id: str,
        template: PathTemplate,
        start_entities: List[str],
        target_entities: Optional[List[str]],
        temporal_constraint: Optional[datetime],
        context: Optional[Dict[str, Any]],
    ) -> KGQueryPlan:
        """Create plan from a template."""
        return KGQueryPlan(
            query_id=query_id,
            query_type=template.applicable_query_types[0],
            start_entities=start_entities,
            target_entities=target_entities,
            hops=template.hops.copy(),
            max_hops=len(template.hops),
            temporal_constraint=temporal_constraint,
            context=context or {},
        )
    
    def _plan_entity_facts(
        self,
        query_id: str,
        entities: List[str],
        predicates: Optional[List[str]],
        temporal_constraint: Optional[datetime],
        context: Optional[Dict[str, Any]],
    ) -> KGQueryPlan:
        """Plan query to get all facts about entities."""
        hops = [
            HopSpec(
                hop_number=1,
                direction=HopDirection.BIDIRECTIONAL,
                predicate_filter=predicates,
                valid_at=temporal_constraint,
            )
        ]
        
        return KGQueryPlan(
            query_id=query_id,
            query_type=QueryType.ENTITY_FACTS,
            start_entities=entities,
            hops=hops,
            max_hops=1,
            temporal_constraint=temporal_constraint,
            context=context or {},
        )
    
    def _plan_path_finding(
        self,
        query_id: str,
        start_entities: List[str],
        target_entities: List[str],
        max_hops: int,
        temporal_constraint: Optional[datetime],
        context: Optional[Dict[str, Any]],
    ) -> KGQueryPlan:
        """Plan path finding query between entities."""
        # Build hops for BFS-style traversal
        hops = []
        for i in range(max_hops):
            hops.append(HopSpec(
                hop_number=i + 1,
                direction=HopDirection.BIDIRECTIONAL,
                valid_at=temporal_constraint,
                max_results=50,  # Limit branching factor
            ))
        
        return KGQueryPlan(
            query_id=query_id,
            query_type=QueryType.PATH_FINDING,
            start_entities=start_entities,
            target_entities=target_entities,
            hops=hops,
            max_hops=max_hops,
            temporal_constraint=temporal_constraint,
            deduplicate=True,
            context=context or {},
        )
    
    def _plan_neighborhood(
        self,
        query_id: str,
        entities: List[str],
        max_hops: int,
        predicates: Optional[List[str]],
        temporal_constraint: Optional[datetime],
        context: Optional[Dict[str, Any]],
    ) -> KGQueryPlan:
        """Plan N-hop neighborhood exploration."""
        hops = []
        for i in range(max_hops):
            hops.append(HopSpec(
                hop_number=i + 1,
                direction=HopDirection.OUTGOING,
                predicate_filter=predicates,
                valid_at=temporal_constraint,
                max_results=100 // (i + 1),  # Reduce branching at deeper levels
            ))
        
        return KGQueryPlan(
            query_id=query_id,
            query_type=QueryType.NEIGHBORHOOD,
            start_entities=entities,
            hops=hops,
            max_hops=max_hops,
            temporal_constraint=temporal_constraint,
            aggregate_results=True,
            context=context or {},
        )
    
    def _plan_temporal_slice(
        self,
        query_id: str,
        entities: List[str],
        timestamp: datetime,
        predicates: Optional[List[str]],
        context: Optional[Dict[str, Any]],
    ) -> KGQueryPlan:
        """Plan query for facts valid at a specific time."""
        hops = [
            HopSpec(
                hop_number=1,
                direction=HopDirection.BIDIRECTIONAL,
                predicate_filter=predicates,
                valid_at=timestamp,
                include_invalidated=False,
            )
        ]
        
        return KGQueryPlan(
            query_id=query_id,
            query_type=QueryType.TEMPORAL_SLICE,
            start_entities=entities,
            hops=hops,
            max_hops=1,
            temporal_constraint=timestamp,
            context=context or {},
        )
    
    def get_template(self, name: str) -> Optional[PathTemplate]:
        """Get a path template by name.
        
        Args:
            name: Template name
            
        Returns:
            PathTemplate or None
        """
        return self._templates.get(name)
    
    def list_templates(self) -> List[str]:
        """List available template names.
        
        Returns:
            List of template names
        """
        return list(self._templates.keys())


# =============================================================================
# Planning Helpers
# =============================================================================

def plan_entity_retrieval(
    entity_id: str,
    predicates: Optional[List[str]] = None,
    max_hops: int = 1,
) -> KGQueryPlan:
    """Create a simple plan to retrieve facts about an entity.
    
    Args:
        entity_id: Entity to query
        predicates: Optional predicate filter
        max_hops: Number of hops
        
    Returns:
        KGQueryPlan
    """
    planner = KGRetrievalPlanner()
    return planner.plan_query(
        query_type=QueryType.ENTITY_FACTS,
        start_entities=[entity_id],
        predicates=predicates,
        max_hops=max_hops,
    )


def plan_skill_similarity(
    entity_id: str,
    max_similar: int = 10,
) -> KGQueryPlan:
    """Plan query to find entities with similar skills.
    
    Args:
        entity_id: Entity to find similar for
        max_similar: Maximum similar entities to return
        
    Returns:
        KGQueryPlan
    """
    planner = KGRetrievalPlanner()
    return planner.plan_query(
        query_type=QueryType.NEIGHBORHOOD,
        start_entities=[entity_id],
        template_name="similar_skills",
        context={"max_similar": max_similar},
    )


def plan_job_requirements(job_id: str) -> KGQueryPlan:
    """Plan query to get all job requirements.
    
    Args:
        job_id: Job entity ID
        
    Returns:
        KGQueryPlan
    """
    planner = KGRetrievalPlanner()
    return planner.plan_query(
        query_type=QueryType.ENTITY_FACTS,
        start_entities=[job_id],
        template_name="job_requirements",
    )


__all__ = [
    "HopDirection",
    "QueryType",
    "HopSpec",
    "KGQueryPlan",
    "PathTemplate",
    "KGRetrievalPlanner",
    "plan_entity_retrieval",
    "plan_skill_similarity",
    "plan_job_requirements",
]
