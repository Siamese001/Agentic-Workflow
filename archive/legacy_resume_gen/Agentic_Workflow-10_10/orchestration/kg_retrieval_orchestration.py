"""KG-First Retrieval Orchestration - Hybrid KG + Vector Retrieval DAG

This module implements L3 orchestration for KG-first retrieval,
combining knowledge graph queries with vector search for enhanced
context retrieval.

Layer: L3 (Orchestration)
Responsibilities:
- Orchestrate KG → Vector → Fusion pipeline
- Build retrieval DAGs
- Coordinate L1 planners and L2 executors
- Manage hybrid ranking

Non-responsibilities:
- Query planning (L1)
- Query execution (L2)
- State storage (L4)
- Policy enforcement (L5)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Callable
from datetime import datetime, UTC
from enum import Enum
import asyncio


class RetrievalStage(str, Enum):
    """Stages in the retrieval pipeline."""
    KG_QUERY = "kg_query"
    VECTOR_SEARCH = "vector_search"
    FUSION = "fusion"
    RERANKING = "reranking"
    FILTERING = "filtering"


@dataclass
class RetrievalNode:
    """A node in the retrieval DAG."""
    
    node_id: str
    stage: RetrievalStage
    
    # Configuration
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Dependencies
    depends_on: List[str] = field(default_factory=list)
    
    # Results (populated after execution)
    result: Optional[Any] = None
    executed: bool = False
    execution_time_ms: int = 0
    error: Optional[str] = None


@dataclass
class RetrievalDAG:
    """Directed Acyclic Graph for retrieval orchestration."""
    
    dag_id: str
    nodes: Dict[str, RetrievalNode]
    
    # Execution state
    executed: bool = False
    total_execution_time_ms: int = 0
    
    def add_node(self, node: RetrievalNode) -> None:
        """Add a node to the DAG."""
        self.nodes[node.node_id] = node
    
    def get_execution_order(self) -> List[str]:
        """Get topologically sorted execution order."""
        visited: Set[str] = set()
        order: List[str] = []
        
        def visit(node_id: str) -> None:
            if node_id in visited:
                return
            visited.add(node_id)
            node = self.nodes.get(node_id)
            if node:
                for dep in node.depends_on:
                    visit(dep)
                order.append(node_id)
        
        for node_id in self.nodes:
            visit(node_id)
        
        return order


@dataclass
class HybridRetrievalContext:
    """Context for hybrid retrieval."""
    
    query: str
    user_id: Optional[str] = None
    job_id: Optional[str] = None
    
    # KG context
    kg_entities: List[str] = field(default_factory=list)
    kg_predicates: Optional[List[str]] = None
    kg_max_hops: int = 2
    
    # Vector context
    vector_namespace: str = "default"
    vector_top_k: int = 10
    
    # Fusion settings
    kg_weight: float = 0.4
    vector_weight: float = 0.6
    min_score: float = 0.3
    
    # Temporal
    temporal_constraint: Optional[datetime] = None


@dataclass
class HybridRetrievalResult:
    """Result of hybrid KG + Vector retrieval."""
    
    # Combined results
    results: List[Dict[str, Any]]
    
    # Component results
    kg_results: List[Dict[str, Any]] = field(default_factory=list)
    vector_results: List[Dict[str, Any]] = field(default_factory=list)
    
    # Scores
    kg_contribution: float = 0.0
    vector_contribution: float = 0.0
    
    # Statistics
    total_kg_facts: int = 0
    total_vector_hits: int = 0
    execution_time_ms: int = 0
    
    # DAG execution trace
    dag_trace: Optional[RetrievalDAG] = None


class KGFirstRetrievalOrchestrator:
    """Orchestrator for KG-first hybrid retrieval.
    
    This orchestrator builds and executes retrieval DAGs that:
    1. First query the Knowledge Graph for structured facts
    2. Use KG entities to enhance vector search
    3. Fuse results with weighted combination
    4. Optionally rerank for relevance
    """
    
    def __init__(
        self,
        kg_planner: Optional[Any] = None,
        kg_executor: Optional[Any] = None,
        vector_executor: Optional[Any] = None,
    ):
        """Initialize orchestrator.
        
        Args:
            kg_planner: L1 KG retrieval planner
            kg_executor: L2 KG retrieval executor
            vector_executor: L2 vector search executor
        """
        self.kg_planner = kg_planner
        self.kg_executor = kg_executor
        self.vector_executor = vector_executor
    
    def build_dag(self, context: HybridRetrievalContext) -> RetrievalDAG:
        """Build a retrieval DAG for the given context.
        
        Args:
            context: Retrieval context
            
        Returns:
            RetrievalDAG ready for execution
        """
        dag_id = f"retrieval_dag_{datetime.now(UTC).strftime('%Y%m%d%H%M%S%f')}"
        dag = RetrievalDAG(dag_id=dag_id, nodes={})
        
        # Stage 1: KG Query
        kg_node = RetrievalNode(
            node_id="kg_query",
            stage=RetrievalStage.KG_QUERY,
            config={
                "entities": context.kg_entities,
                "predicates": context.kg_predicates,
                "max_hops": context.kg_max_hops,
                "temporal_constraint": context.temporal_constraint,
            },
        )
        dag.add_node(kg_node)
        
        # Stage 2: Vector Search (can run in parallel with KG)
        vector_node = RetrievalNode(
            node_id="vector_search",
            stage=RetrievalStage.VECTOR_SEARCH,
            config={
                "query": context.query,
                "namespace": context.vector_namespace,
                "top_k": context.vector_top_k,
            },
        )
        dag.add_node(vector_node)
        
        # Stage 3: KG-Enhanced Vector Search (depends on KG results)
        enhanced_vector_node = RetrievalNode(
            node_id="enhanced_vector_search",
            stage=RetrievalStage.VECTOR_SEARCH,
            depends_on=["kg_query"],
            config={
                "query": context.query,
                "namespace": context.vector_namespace,
                "top_k": context.vector_top_k,
                "use_kg_entities": True,
            },
        )
        dag.add_node(enhanced_vector_node)
        
        # Stage 4: Fusion (depends on all search results)
        fusion_node = RetrievalNode(
            node_id="fusion",
            stage=RetrievalStage.FUSION,
            depends_on=["kg_query", "vector_search", "enhanced_vector_search"],
            config={
                "kg_weight": context.kg_weight,
                "vector_weight": context.vector_weight,
                "min_score": context.min_score,
            },
        )
        dag.add_node(fusion_node)
        
        # Stage 5: Final filtering
        filter_node = RetrievalNode(
            node_id="filtering",
            stage=RetrievalStage.FILTERING,
            depends_on=["fusion"],
            config={
                "min_score": context.min_score,
                "deduplicate": True,
            },
        )
        dag.add_node(filter_node)
        
        return dag
    
    async def execute_dag(
        self,
        dag: RetrievalDAG,
        context: HybridRetrievalContext,
    ) -> HybridRetrievalResult:
        """Execute a retrieval DAG.
        
        Args:
            dag: DAG to execute
            context: Retrieval context
            
        Returns:
            HybridRetrievalResult
        """
        start_time = datetime.now(UTC)
        
        kg_results: List[Dict[str, Any]] = []
        vector_results: List[Dict[str, Any]] = []
        
        execution_order = dag.get_execution_order()
        
        for node_id in execution_order:
            node = dag.nodes.get(node_id)
            if not node:
                continue
            
            node_start = datetime.now(UTC)
            
            try:
                if node.stage == RetrievalStage.KG_QUERY:
                    node.result = await self._execute_kg_query(node.config, context)
                    kg_results = node.result or []
                    
                elif node.stage == RetrievalStage.VECTOR_SEARCH:
                    # Get KG entities from previous node if available
                    kg_entities = []
                    if node.config.get("use_kg_entities"):
                        kg_node = dag.nodes.get("kg_query")
                        if kg_node and kg_node.result:
                            kg_entities = self._extract_entities_from_kg(kg_node.result)
                    
                    node.result = await self._execute_vector_search(
                        node.config, context, kg_entities
                    )
                    if node.node_id == "vector_search":
                        vector_results = node.result or []
                        
                elif node.stage == RetrievalStage.FUSION:
                    node.result = self._execute_fusion(dag, node.config)
                    
                elif node.stage == RetrievalStage.FILTERING:
                    node.result = self._execute_filtering(dag, node.config)
                
                node.executed = True
                
            except Exception as e:
                node.error = str(e)
            
            node_end = datetime.now(UTC)
            node.execution_time_ms = int((node_end - node_start).total_seconds() * 1000)
        
        dag.executed = True
        
        end_time = datetime.now(UTC)
        total_time = int((end_time - start_time).total_seconds() * 1000)
        dag.total_execution_time_ms = total_time
        
        # Get final results from filtering node
        filter_node = dag.nodes.get("filtering")
        final_results = filter_node.result if filter_node and filter_node.result else []
        
        return HybridRetrievalResult(
            results=final_results,
            kg_results=kg_results,
            vector_results=vector_results,
            kg_contribution=context.kg_weight,
            vector_contribution=context.vector_weight,
            total_kg_facts=len(kg_results),
            total_vector_hits=len(vector_results),
            execution_time_ms=total_time,
            dag_trace=dag,
        )
    
    async def _execute_kg_query(
        self,
        config: Dict[str, Any],
        context: HybridRetrievalContext,
    ) -> List[Dict[str, Any]]:
        """Execute KG query stage.
        
        Args:
            config: Node configuration
            context: Retrieval context
            
        Returns:
            List of KG facts as dictionaries
        """
        if not self.kg_planner or not self.kg_executor:
            return []
        
        # Use the L1 planner to create a query plan
        from l1.kg_retrieval_planning import KGRetrievalPlanner, QueryType
        
        planner = self.kg_planner or KGRetrievalPlanner()
        plan = planner.plan_query(
            query_type=QueryType.NEIGHBORHOOD,
            start_entities=config.get("entities", []),
            predicates=config.get("predicates"),
            max_hops=config.get("max_hops", 2),
            temporal_constraint=config.get("temporal_constraint"),
        )
        
        # Execute the plan
        result = self.kg_executor.execute(plan)
        
        # Convert triplets to dictionaries
        return [
            {
                "id": t.id,
                "subject": t.subject,
                "predicate": t.predicate,
                "object": t.object,
                "confidence": t.confidence,
                "source": "kg",
                "text": t.to_text(),
            }
            for t in result.triplets
        ]
    
    async def _execute_vector_search(
        self,
        config: Dict[str, Any],
        context: HybridRetrievalContext,
        kg_entities: List[str],
    ) -> List[Dict[str, Any]]:
        """Execute vector search stage.
        
        Args:
            config: Node configuration
            context: Retrieval context
            kg_entities: Entities from KG for query enhancement
            
        Returns:
            List of vector search results
        """
        if not self.vector_executor:
            return []
        
        # Enhance query with KG entities if available
        query = config.get("query", context.query)
        if kg_entities and config.get("use_kg_entities"):
            entity_terms = " ".join(kg_entities[:5])  # Add top 5 entities
            query = f"{query} {entity_terms}"
        
        # Execute vector search
        results = self.vector_executor.execute_search(
            namespace=config.get("namespace", context.vector_namespace),
            query_text=query,
            top_k=config.get("top_k", context.vector_top_k),
        )
        
        return [
            {
                "id": r.id,
                "score": r.score,
                "text": r.metadata.get("text", ""),
                "metadata": r.metadata,
                "source": "vector",
            }
            for r in results
        ]
    
    def _extract_entities_from_kg(
        self,
        kg_results: List[Dict[str, Any]],
    ) -> List[str]:
        """Extract entity names from KG results.
        
        Args:
            kg_results: KG query results
            
        Returns:
            List of entity names
        """
        entities: Set[str] = set()
        
        for fact in kg_results:
            entities.add(fact.get("subject", ""))
            entities.add(fact.get("object", ""))
        
        # Filter out empty strings
        return [e for e in entities if e]
    
    def _execute_fusion(
        self,
        dag: RetrievalDAG,
        config: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Execute fusion stage - combine KG and vector results.
        
        Args:
            dag: Current DAG with node results
            config: Fusion configuration
            
        Returns:
            Fused results
        """
        kg_weight = config.get("kg_weight", 0.4)
        vector_weight = config.get("vector_weight", 0.6)
        
        # Collect results from dependencies
        kg_results = []
        vector_results = []
        
        kg_node = dag.nodes.get("kg_query")
        if kg_node and kg_node.result:
            kg_results = kg_node.result
        
        vector_node = dag.nodes.get("vector_search")
        if vector_node and vector_node.result:
            vector_results = vector_node.result
        
        enhanced_node = dag.nodes.get("enhanced_vector_search")
        if enhanced_node and enhanced_node.result:
            vector_results.extend(enhanced_node.result)
        
        # Score and combine results
        scored_results: Dict[str, Dict[str, Any]] = {}
        
        # Score KG results
        for i, fact in enumerate(kg_results):
            fact_id = fact.get("id", f"kg_{i}")
            score = fact.get("confidence", 1.0) * kg_weight
            
            if fact_id not in scored_results:
                scored_results[fact_id] = {
                    "id": fact_id,
                    "text": fact.get("text", ""),
                    "score": 0.0,
                    "kg_score": 0.0,
                    "vector_score": 0.0,
                    "sources": [],
                    "metadata": fact,
                }
            
            scored_results[fact_id]["kg_score"] = score
            scored_results[fact_id]["score"] += score
            scored_results[fact_id]["sources"].append("kg")
        
        # Score vector results
        for result in vector_results:
            result_id = result.get("id", "")
            score = result.get("score", 0.0) * vector_weight
            
            if result_id not in scored_results:
                scored_results[result_id] = {
                    "id": result_id,
                    "text": result.get("text", ""),
                    "score": 0.0,
                    "kg_score": 0.0,
                    "vector_score": 0.0,
                    "sources": [],
                    "metadata": result.get("metadata", {}),
                }
            
            scored_results[result_id]["vector_score"] = max(
                scored_results[result_id]["vector_score"], score
            )
            scored_results[result_id]["score"] += score
            if "vector" not in scored_results[result_id]["sources"]:
                scored_results[result_id]["sources"].append("vector")
        
        # Sort by combined score
        fused = sorted(
            scored_results.values(),
            key=lambda x: x["score"],
            reverse=True,
        )
        
        return fused
    
    def _execute_filtering(
        self,
        dag: RetrievalDAG,
        config: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Execute filtering stage.
        
        Args:
            dag: Current DAG with node results
            config: Filtering configuration
            
        Returns:
            Filtered results
        """
        fusion_node = dag.nodes.get("fusion")
        if not fusion_node or not fusion_node.result:
            return []
        
        results = fusion_node.result
        min_score = config.get("min_score", 0.0)
        
        # Filter by minimum score
        filtered = [r for r in results if r.get("score", 0) >= min_score]
        
        # Deduplicate if requested
        if config.get("deduplicate", True):
            seen_texts: Set[str] = set()
            unique: List[Dict[str, Any]] = []
            
            for result in filtered:
                text = result.get("text", "")
                if text and text not in seen_texts:
                    seen_texts.add(text)
                    unique.append(result)
            
            filtered = unique
        
        return filtered
    
    def orchestrate(
        self,
        context: HybridRetrievalContext,
    ) -> HybridRetrievalResult:
        """Synchronous orchestration entry point.
        
        Args:
            context: Retrieval context
            
        Returns:
            HybridRetrievalResult
        """
        dag = self.build_dag(context)
        return asyncio.run(self.execute_dag(dag, context))


# =============================================================================
# Convenience Functions
# =============================================================================

def create_hybrid_context(
    query: str,
    user_id: Optional[str] = None,
    job_id: Optional[str] = None,
    kg_entities: Optional[List[str]] = None,
    kg_weight: float = 0.4,
    vector_weight: float = 0.6,
) -> HybridRetrievalContext:
    """Create a hybrid retrieval context.
    
    Args:
        query: Search query
        user_id: Optional user ID for KG
        job_id: Optional job ID for KG
        kg_entities: Optional starting KG entities
        kg_weight: Weight for KG results
        vector_weight: Weight for vector results
        
    Returns:
        HybridRetrievalContext
    """
    entities = kg_entities or []
    if user_id:
        entities.append(user_id)
    if job_id:
        entities.append(job_id)
    
    return HybridRetrievalContext(
        query=query,
        user_id=user_id,
        job_id=job_id,
        kg_entities=entities,
        kg_weight=kg_weight,
        vector_weight=vector_weight,
    )


__all__ = [
    "RetrievalStage",
    "RetrievalNode",
    "RetrievalDAG",
    "HybridRetrievalContext",
    "HybridRetrievalResult",
    "KGFirstRetrievalOrchestrator",
    "create_hybrid_context",
]
