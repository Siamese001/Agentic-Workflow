"""
Knowledge graph retrieval executor for resume processing workflows.

Implements L2 execution for multi-hop knowledge graph traversal
to support resume enhancement and job alignment operations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from datetime import datetime, UTC
from collections import defaultdict

from l1.kg_retrieval_planning import (
    KGQueryPlan,
    HopSpec,
    HopDirection,
    QueryType,
)
from l4.triplet_store import Triplet, TripletStore, TripletQuery


@dataclass
class TraversalPath:
    """
    Represents a path through the resume processing knowledge graph.

    Enables systematic traversal of resume enhancement data relationships.
    """
    
    entities: List[str]
    triplets: List[Triplet]
    total_confidence: float = 1.0
    
    def add_hop(self, triplet: Triplet, next_entity: str) -> "TraversalPath":
        """
        Adds a hop to the resume processing knowledge graph path.

        Extends the path for resume data exploration and job alignment.
        
        Args:
            triplet: Triplet traversed in resume data graph
            next_entity: Next entity in resume processing path
            
        Returns:
            New TraversalPath with added hop for resume enhancement
        """
        return TraversalPath(
            entities=self.entities + [next_entity],
            triplets=self.triplets + [triplet],
            total_confidence=self.total_confidence * triplet.confidence,
        )


@dataclass
class KGRetrievalResult:
    """
    Result of knowledge graph retrieval for resume processing workflows.

    Provides structured data extraction for resume enhancement and job alignment.
    """
    
    query_id: str
    query_type: QueryType
    
    # Retrieved data
    triplets: List[Triplet]
    entities: Set[str]
    paths: List[TraversalPath]
    
    # Statistics
    total_triplets: int = 0
    total_hops_executed: int = 0
    execution_time_ms: int = 0
    
    # Aggregated facts
    facts_by_entity: Dict[str, List[Triplet]] = field(default_factory=dict)
    facts_by_predicate: Dict[str, List[Triplet]] = field(default_factory=dict)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


class KGRetrievalExecutor:
    """
    Executor for multi-hop knowledge graph retrieval in resume processing.

    Traverses knowledge graph according to L1 plans for resume enhancement
    and job alignment workflows.
    """
    
    def __init__(self, triplet_store: TripletStore):
        """
        Initializes knowledge graph retrieval executor for resume processing.

        Args:
            triplet_store: L4 TripletStore for resume workflow coordination
        """
        self.store = triplet_store
    
    def execute(self, plan: KGQueryPlan) -> KGRetrievalResult:
        """Executes KG query plan for resume processing workflows.

        Args:
            plan: Query plan from L1 for resume enhancement
        """
        start_time = datetime.now(UTC)
        
        # Initialize result containers
        all_triplets: List[Triplet] = []
        all_entities: Set[str] = set(plan.start_entities)
        all_paths: List[TraversalPath] = []
        
        # Execute based on query type
        if plan.query_type == QueryType.ENTITY_FACTS:
            triplets = self._execute_entity_facts(plan)
            all_triplets.extend(triplets)
            
        elif plan.query_type == QueryType.PATH_FINDING:
            paths = self._execute_path_finding(plan)
            all_paths.extend(paths)
            for path in paths:
                all_triplets.extend(path.triplets)
                all_entities.update(path.entities)
                
        elif plan.query_type == QueryType.NEIGHBORHOOD:
            triplets, entities = self._execute_neighborhood(plan)
            all_triplets.extend(triplets)
            all_entities.update(entities)
            
        elif plan.query_type == QueryType.TEMPORAL_SLICE:
            triplets = self._execute_temporal_slice(plan)
            all_triplets.extend(triplets)
            
        else:
            # Default to entity facts
            triplets = self._execute_entity_facts(plan)
            all_triplets.extend(triplets)
        
        # Deduplicate if requested
        if plan.deduplicate:
            all_triplets = self._deduplicate_triplets(all_triplets)
        
        # Aggregate results
        facts_by_entity = self._aggregate_by_entity(all_triplets)
        facts_by_predicate = self._aggregate_by_predicate(all_triplets)
        
        # Update entity set from triplets
        for triplet in all_triplets:
            all_entities.add(triplet.subject)
            all_entities.add(triplet.object)
        
        end_time = datetime.now(UTC)
        execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
        
        return KGRetrievalResult(
            query_id=plan.query_id,
            query_type=plan.query_type,
            triplets=all_triplets,
            entities=all_entities,
            paths=all_paths,
            total_triplets=len(all_triplets),
            total_hops_executed=len(plan.hops),
            execution_time_ms=execution_time_ms,
            facts_by_entity=facts_by_entity,
            facts_by_predicate=facts_by_predicate,
            metadata=plan.context,
        )
    
    def _execute_entity_facts(self, plan: KGQueryPlan) -> List[Triplet]:
        """Executes entity facts query for resume processing.

        Retrieves triplets about entities for resume enhancement.
        """
        all_triplets: List[Triplet] = []
        
        for entity in plan.start_entities:
            triplets = self.store.get_entity_triplets(entity)
            
            # Apply predicate filters
            if plan.predicate_whitelist:
                triplets = [t for t in triplets if t.predicate in plan.predicate_whitelist]
            if plan.predicate_blacklist:
                triplets = [t for t in triplets if t.predicate not in plan.predicate_blacklist]
            
            # Apply temporal constraint
            if plan.temporal_constraint:
                triplets = self._filter_by_temporal(triplets, plan.temporal_constraint)
            
            all_triplets.extend(triplets)
        
        return all_triplets
    
    def _execute_path_finding(self, plan: KGQueryPlan) -> List[TraversalPath]:
        """Executes path finding for resume entity relationships.

        Uses BFS to find paths for resume enhancement and job alignment.
        """
        if not plan.target_entities:
            return []
        
        target_set = set(plan.target_entities)
        found_paths: List[TraversalPath] = []
        
        # Initialize frontier with start entities
        frontier: List[TraversalPath] = [
            TraversalPath(entities=[e], triplets=[])
            for e in plan.start_entities
        ]
        
        visited: Set[str] = set(plan.start_entities)
        
        for hop_spec in plan.hops:
            if not frontier:
                break
            
            next_frontier: List[TraversalPath] = []
            
            for path in frontier:
                current_entity = path.entities[-1]
                
                # Get neighbors based on direction
                neighbors = self._get_neighbors(
                    current_entity,
                    hop_spec,
                    plan.temporal_constraint,
                )
                
                for triplet, next_entity in neighbors:
                    if next_entity in visited and next_entity not in target_set:
                        continue
                    
                    new_path = path.add_hop(triplet, next_entity)
                    
                    # Check if we reached a target
                    if next_entity in target_set:
                        found_paths.append(new_path)
                    else:
                        next_frontier.append(new_path)
                        visited.add(next_entity)
            
            frontier = next_frontier[:hop_spec.max_results]  # Limit branching
        
        return found_paths
    
    def _execute_neighborhood(
        self,
        plan: KGQueryPlan,
    ) -> Tuple[List[Triplet], Set[str]]:
        """Executes N-hop neighborhood exploration for resume entities.

        Explores entity relationships for resume enhancement workflows.
        """
        all_triplets: List[Triplet] = []
        all_entities: Set[str] = set(plan.start_entities)
        current_entities = set(plan.start_entities)
        
        for hop_spec in plan.hops:
            if not current_entities:
                break
            
            next_entities: Set[str] = set()
            
            for entity in current_entities:
                neighbors = self._get_neighbors(
                    entity,
                    hop_spec,
                    plan.temporal_constraint,
                )
                
                for triplet, next_entity in neighbors[:hop_spec.max_results]:
                    all_triplets.append(triplet)
                    if next_entity not in all_entities:
                        next_entities.add(next_entity)
                        all_entities.add(next_entity)
            
            current_entities = next_entities
        
        return all_triplets, all_entities
    
    def _execute_temporal_slice(self, plan: KGQueryPlan) -> List[Triplet]:
        """Executes temporal slice query for resume timeline analysis.

        Retrieves triplets valid at specified time for job alignment.
        """
        all_triplets: List[Triplet] = []
        
        for entity in plan.start_entities:
            query = TripletQuery(
                subject=entity,
                valid_at=plan.temporal_constraint,
                include_invalidated=False,
            )
            triplets = self.store.query(query)
            
            # Also get triplets where entity is object
            query_obj = TripletQuery(
                object=entity,
                valid_at=plan.temporal_constraint,
                include_invalidated=False,
            )
            triplets.extend(self.store.query(query_obj))
            
            all_triplets.extend(triplets)
        
        return all_triplets
    
    def _get_neighbors(
        self,
        entity: str,
        hop_spec: HopSpec,
        temporal_constraint: Optional[datetime],
    ) -> List[Tuple[Triplet, str]]:
        """Gets neighboring entities for resume relationship analysis.

        Retrieves connected entities for resume enhancement workflows.
        """
        neighbors: List[Tuple[Triplet, str]] = []
        
        # Outgoing edges (entity is subject)
        if hop_spec.direction in (HopDirection.OUTGOING, HopDirection.BIDIRECTIONAL):
            query = TripletQuery(
                subject=entity,
                valid_at=temporal_constraint or hop_spec.valid_at,
                include_invalidated=hop_spec.include_invalidated,
                min_confidence=hop_spec.min_confidence,
            )
            triplets = self.store.query(query)
            
            for triplet in triplets:
                if hop_spec.predicate_filter and triplet.predicate not in hop_spec.predicate_filter:
                    continue
                neighbors.append((triplet, triplet.object))
        
        # Incoming edges (entity is object)
        if hop_spec.direction in (HopDirection.INCOMING, HopDirection.BIDIRECTIONAL):
            query = TripletQuery(
                object=entity,
                valid_at=temporal_constraint or hop_spec.valid_at,
                include_invalidated=hop_spec.include_invalidated,
                min_confidence=hop_spec.min_confidence,
            )
            triplets = self.store.query(query)
            
            for triplet in triplets:
                if hop_spec.predicate_filter and triplet.predicate not in hop_spec.predicate_filter:
                    continue
                neighbors.append((triplet, triplet.subject))
        
        return neighbors
    
    def _filter_by_temporal(
        self,
        triplets: List[Triplet],
        timestamp: datetime,
    ) -> List[Triplet]:
        """Filters triplets by temporal constraint for resume timeline analysis.

        Ensures temporal accuracy for resume job alignment.
        """
        filtered = []
        for triplet in triplets:
            if triplet.valid_from and triplet.valid_from > timestamp:
                continue
            if triplet.valid_until and triplet.valid_until < timestamp:
                continue
            filtered.append(triplet)
        return filtered
    
    def _deduplicate_triplets(self, triplets: List[Triplet]) -> List[Triplet]:
        """Removes duplicate triplets for resume data consistency.

        Ensures clean resume enhancement data for job alignment.
        """
        seen: Set[str] = set()
        unique: List[Triplet] = []
        
        for triplet in triplets:
            if triplet.id not in seen:
                seen.add(triplet.id)
                unique.append(triplet)
        
        return unique
    
    def _aggregate_by_entity(
        self,
        triplets: List[Triplet],
    ) -> Dict[str, List[Triplet]]:
        """Aggregates triplets by entity for resume data organization.

        Groups resume enhancement data by entity for job alignment.
        """
        aggregated: Dict[str, List[Triplet]] = defaultdict(list)
        
        for triplet in triplets:
            aggregated[triplet.subject].append(triplet)
            aggregated[triplet.object].append(triplet)
        
        return dict(aggregated)
    
    def _aggregate_by_predicate(
        self,
        triplets: List[Triplet],
    ) -> Dict[str, List[Triplet]]:
        """Aggregates triplets by predicate for resume data organization.

        Groups resume enhancement data by relationship type for job alignment.
        """
        aggregated: Dict[str, List[Triplet]] = defaultdict(list)
        
        for triplet in triplets:
            aggregated[triplet.predicate].append(triplet)
        
        return dict(aggregated)


# =============================================================================
# Convenience Functions
# =============================================================================

def execute_entity_query(
    store: TripletStore,
    entity_id: str,
    predicates: Optional[List[str]] = None,
) -> KGRetrievalResult:
    """Execute a simple entity query.
    
    Args:
        store: TripletStore instance
        entity_id: Entity to query
        predicates: Optional predicate filter
        
    Returns:
        KGRetrievalResult
    """
    from l1.kg_retrieval_planning import plan_entity_retrieval
    
    plan = plan_entity_retrieval(entity_id, predicates)
    executor = KGRetrievalExecutor(store)
    return executor.execute(plan)


def execute_multi_hop_query(
    store: TripletStore,
    start_entity: str,
    max_hops: int = 2,
    predicates: Optional[List[str]] = None,
) -> KGRetrievalResult:
    """Execute a multi-hop neighborhood query.
    
    Args:
        store: TripletStore instance
        start_entity: Starting entity
        max_hops: Maximum hops
        predicates: Optional predicate filter
        
    Returns:
        KGRetrievalResult
    """
    from l1.kg_retrieval_planning import KGRetrievalPlanner, QueryType
    
    planner = KGRetrievalPlanner()
    plan = planner.plan_query(
        query_type=QueryType.NEIGHBORHOOD,
        start_entities=[start_entity],
        predicates=predicates,
        max_hops=max_hops,
    )
    
    executor = KGRetrievalExecutor(store)
    return executor.execute(plan)


__all__ = [
    "TraversalPath",
    "KGRetrievalResult",
    "KGRetrievalExecutor",
    "execute_entity_query",
    "execute_multi_hop_query",
]
