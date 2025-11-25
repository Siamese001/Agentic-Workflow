"""KG Retrieval Executor - Multi-hop Knowledge Graph Traversal

This module implements L2 execution for multi-hop knowledge graph retrieval,
performing graph traversal based on L1 query plans.

Layer: L2 (Execution)
Responsibilities:
- Execute multi-hop graph traversal
- Apply filters and constraints per hop
- Aggregate and deduplicate results
- Return structured retrieval results

Non-responsibilities:
- Query planning (L1)
- Triplet storage (L4)
- Orchestration (L3)
- Policy enforcement (L5)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from datetime import datetime, UTC
from collections import defaultdict

from agents.planning.kg_retrieval_planning import (
    KGQueryPlan,
    HopSpec,
    HopDirection,
    QueryType,
)
from state.triplet_store import Triplet, TripletStore, TripletQuery


@dataclass
class TraversalPath:
    """A path through the knowledge graph."""
    
    entities: List[str]
    triplets: List[Triplet]
    total_confidence: float = 1.0
    
    def add_hop(self, triplet: Triplet, next_entity: str) -> "TraversalPath":
        """Add a hop to the path.
        
        Args:
            triplet: Triplet traversed
            next_entity: Next entity in path
            
        Returns:
            New TraversalPath with added hop
        """
        return TraversalPath(
            entities=self.entities + [next_entity],
            triplets=self.triplets + [triplet],
            total_confidence=self.total_confidence * triplet.confidence,
        )


@dataclass
class KGRetrievalResult:
    """Result of KG retrieval execution."""
    
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
    """Executor for multi-hop knowledge graph retrieval.
    
    This executor traverses the knowledge graph according to
    query plans created by L1.
    """
    
    def __init__(self, triplet_store: TripletStore):
        """Initialize with triplet store.
        
        Args:
            triplet_store: L4 TripletStore instance
        """
        self.store = triplet_store
    
    def execute(self, plan: KGQueryPlan) -> KGRetrievalResult:
        """Execute a KG query plan.
        
        Args:
            plan: Query plan from L1
            
        Returns:
            KGRetrievalResult with retrieved data
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
        """Execute entity facts query.
        
        Args:
            plan: Query plan
            
        Returns:
            List of triplets about the entities
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
        """Execute path finding between entities.
        
        Uses BFS to find paths between start and target entities.
        
        Args:
            plan: Query plan
            
        Returns:
            List of paths found
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
        """Execute N-hop neighborhood exploration.
        
        Args:
            plan: Query plan
            
        Returns:
            Tuple of (triplets, entities)
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
        """Execute temporal slice query.
        
        Args:
            plan: Query plan
            
        Returns:
            List of triplets valid at the specified time
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
        """Get neighboring entities via triplets.
        
        Args:
            entity: Current entity
            hop_spec: Hop specification
            temporal_constraint: Optional temporal filter
            
        Returns:
            List of (triplet, neighbor_entity) tuples
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
        """Filter triplets by temporal constraint.
        
        Args:
            triplets: Triplets to filter
            timestamp: Point in time
            
        Returns:
            Filtered triplets
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
        """Remove duplicate triplets.
        
        Args:
            triplets: List with potential duplicates
            
        Returns:
            Deduplicated list
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
        """Aggregate triplets by entity.
        
        Args:
            triplets: Triplets to aggregate
            
        Returns:
            Dict mapping entity to triplets
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
        """Aggregate triplets by predicate.
        
        Args:
            triplets: Triplets to aggregate
            
        Returns:
            Dict mapping predicate to triplets
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
    from agents.planning.kg_retrieval_planning import plan_entity_retrieval
    
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
    from agents.planning.kg_retrieval_planning import KGRetrievalPlanner, QueryType
    
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
