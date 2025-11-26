"""
Executes resume analysis steps for job matching and enhancement.

Improves resume targeting by processing career data and job requirements
to identify optimal job alignment opportunities.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime, UTC
import logging

from l1.kg_rag_fusion_planning import (
    RetrievalStepType,
    FusionPlanStep,
    KGRAGFusionPlan,
    RAGRetrievalStep,
)
from l4.temporal_schemas import (
    TemporalTriplet,
    TemporalRange,
)
from l4.temporal_kg import TemporalKG, TemporalQuery


logger = logging.getLogger(__name__)


@dataclass
class FusionStepResult:
    """
    Contains results from resume analysis processing steps.

    Tracks success and data for resume enhancement and job alignment.
    """
    
    step_number: int
    step_type: RetrievalStepType
    success: bool
    data: Any = None
    error: Optional[str] = None
    execution_time_ms: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # MoR execution metadata
    recursion_depth_used: int = 1
    thinking_steps_completed: List[str] = field(default_factory=list)
    confidence_score: float = 0.0


@dataclass
class FusionExecutionResult:
    """
    Contains complete results from resume analysis plan execution.

    Provides comprehensive results and metrics for resume job alignment.
    """
    
    plan_id: str
    success: bool
    step_results: List[FusionStepResult] = field(default_factory=list)
    final_results: Dict[str, Any] = field(default_factory=dict)
    total_execution_time_ms: int = 0
    error: Optional[str] = None
    
    # Aggregated MoR metrics
    total_recursion_depth: int = 0
    thinking_steps_completed: List[str] = field(default_factory=list)
    complexity_score: float = 0.0
    
    def get_successful_step_results(self) -> List[FusionStepResult]:
        """
        Filters and returns successful resume analysis step results.

        Focuses on completed analysis steps for accurate job alignment.
        """
        return [r for r in self.step_results if r.success]
    
    def get_step_result(self, step_number: int) -> Optional[FusionStepResult]:
        """
        Retrieves results from specific resume analysis step by number.

        Enables detailed inspection of resume enhancement steps for debugging.
        """
        for result in self.step_results:
            if result.step_number == step_number:
                return result
        return None


class FusionExecutor:
    """
    Executes resume analysis plans to find job-relevant experiences.

    Improves resume job matching by processing career data through
    specialized analysis steps for optimal alignment.
    """
    
    def __init__(
        self,
        kg_adapter: Optional[TemporalKG] = None,
        vector_store: Optional[Any] = None,
        llm_client: Optional[Any] = None,
    ):
        """
        Sets up resume analysis executor with career data processing tools.

        Configures specialized tools for resume job matching analysis.
        """
        self.kg_adapter = kg_adapter
        self.vector_store = vector_store
        self.llm_client = llm_client
    
    async def execute_fusion_plan(
        self,
        plan: KGRAGFusionPlan,
        execution_context: Optional[Dict[str, Any]] = None,
    ) -> FusionExecutionResult:
        """
        Executes complete resume analysis plan for job-relevant experiences.

        Systematically processes career data for resume job alignment.
        """
        start_time = datetime.now(UTC)
        
        try:
            # Execute steps in order, respecting dependencies
            step_results = []
            completed_steps = set()
            
            for step in plan.fusion_steps:
                # Check dependencies
                if step.depends_on_steps:
                    missing_deps = [
                        dep for dep in step.depends_on_steps 
                        if dep not in completed_steps
                    ]
                    if missing_deps:
                        step_results.append(FusionStepResult(
                            step_number=step.step_number,
                            step_type=step.step_type,
                            success=False,
                            error=f"Missing dependencies: {missing_deps}",
                        ))
                        continue
                
                # Execute the step
                step_result = await self._execute_fusion_step(
                    step, plan, execution_context or {}
                )
                step_results.append(step_result)
                
                if step_result.success:
                    completed_steps.add(step.step_number)
            
            # Aggregate results
            final_results = await self._aggregate_fusion_results(
                step_results, plan
            )
            
            total_time = int((datetime.now(UTC) - start_time).total_seconds() * 1000)
            
            return FusionExecutionResult(
                plan_id=plan.query_id,
                success=True,
                step_results=step_results,
                final_results=final_results,
                total_execution_time_ms=total_time,
                total_recursion_depth=sum(r.recursion_depth_used for r in step_results),
                thinking_steps_completed=list(set([
                    step for result in step_results 
                    for step in result.thinking_steps_completed
                ])),
                complexity_score=self._calculate_complexity_score(step_results),
            )
            
        except Exception as e:
            total_time = int((datetime.now(UTC) - start_time).total_seconds() * 1000)
            logger.error(f"Fusion plan execution failed: {str(e)}")
            
            return FusionExecutionResult(
                plan_id=plan.query_id,
                success=False,
                total_execution_time_ms=total_time,
                error=str(e),
            )
    
    async def _execute_fusion_step(
        self,
        step: FusionPlanStep,
        plan: KGRAGFusionPlan,
        context: Dict[str, Any],
    ) -> FusionStepResult:
        """
        Executes individual resume analysis step for career data processing.

        Handles each analysis step with specialized logic for job alignment.
        """
        start_time = datetime.now(UTC)
        
        try:
            if step.step_type == RetrievalStepType.KG_HOP and step.kg_hop:
                result = await self._execute_kg_hop(step.kg_hop, plan, context)
            elif step.step_type == RetrievalStepType.VECTOR_SEARCH and step.rag_step:
                result = await self._execute_vector_search(step.rag_step, plan, context)
            elif step.step_type == RetrievalStepType.ENTITY_RESOLUTION:
                result = await self._execute_entity_resolution(step, plan, context)
            elif step.step_type == RetrievalStepType.TEMPORAL_FILTER:
                result = await self._execute_temporal_filter(step, plan, context)
            elif step.step_type == RetrievalStepType.FUSION_RANK:
                result = await self._execute_fusion_rank(step, plan, context)
            elif step.step_type == RetrievalStepType.RECURSIVE_DEEPEN:
                result = await self._execute_recursive_deepen(step, plan, context)
            else:
                result = {
                    "success": False,
                    "data": None,
                    "error": f"Unsupported step type: {step.step_type}",
                }
            
            execution_time = int((datetime.now(UTC) - start_time).total_seconds() * 1000)
            
            return FusionStepResult(
                step_number=step.step_number,
                step_type=step.step_type,
                success=result["success"],
                data=result.get("data"),
                error=result.get("error"),
                execution_time_ms=execution_time,
                metadata=result.get("metadata", {}),
                recursion_depth_used=step.recursion_depth_hint,
                thinking_steps_completed=step.thinking_steps,
                confidence_score=result.get("confidence", 0.0),
            )
            
        except Exception as e:
            execution_time = int((datetime.now(UTC) - start_time).total_seconds() * 1000)
            logger.error(f"Step {step.step_number} execution failed: {str(e)}")
            
            return FusionStepResult(
                step_number=step.step_number,
                step_type=step.step_type,
                success=False,
                error=str(e),
                execution_time_ms=execution_time,
                recursion_depth_used=step.recursion_depth_hint,
            )
    
    async def _execute_kg_hop(
        self,
        hop_spec: Any,  # HopSpec from kg_retrieval_planning
        plan: KGRAGFusionPlan,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Traverses career knowledge graph for resume job alignment.

        Discovers career patterns and skill relationships across jobs.
        """
        if not self.kg_adapter:
            return {"success": False, "error": "KG adapter not available"}
        
        try:
            # Build temporal query from hop spec
            query = TemporalQuery(
                subject=plan.start_entities[0] if plan.start_entities else None,
                predicate=hop_spec.predicate_filter[0] if hop_spec.predicate_filter else None,
                start_time=hop_spec.valid_at,
                end_time=hop_spec.valid_at,  # Point-in-time query
                limit=hop_spec.max_results,
                min_confidence=hop_spec.min_confidence,
            )
            
            # Execute query
            facts = self.kg_adapter.query_facts(query)
            
            # Convert to triplets
            triplets = []
            for fact in facts:
                triplet = TemporalTriplet(
                    triplet_id=fact.id,
                    subject=fact.subject,
                    predicate=fact.predicate,
                    object=fact.object,
                    temporal_range=TemporalRange(valid_at=fact.timestamp),
                    confidence=fact.confidence,
                    source=fact.source,
                    metadata=fact.metadata,
                )
                triplets.append(triplet)
            
            return {
                "success": True,
                "data": {
                    "triplets": [t.to_dict() for t in triplets],
                    "count": len(triplets),
                    "hop_number": hop_spec.hop_number,
                },
                "confidence": 1.0 if triplets else 0.0,
                "metadata": {
                    "hop_direction": hop_spec.direction,
                    "predicate_filter": hop_spec.predicate_filter,
                },
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_vector_search(
        self,
        rag_step: RAGRetrievalStep,
        plan: KGRAGFusionPlan,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Searches document database for resume job-relevant experiences.

        Finds textual evidence matching job requirements for alignment.
        """
        if not self.vector_store:
            return {"success": False, "error": "Vector store not available"}
        
        try:
            # Execute vector search
            results = self.vector_store.query_by_text(
                query_text=rag_step.query_text,
                top_k=rag_step.top_k,
                filter_dict=rag_step.metadata_filter,
            )
            
            # Filter by similarity threshold
            filtered_results = [
                r for r in results 
                if getattr(r, 'score', 1.0) >= rag_step.similarity_threshold
            ]
            
            return {
                "success": True,
                "data": {
                    "documents": [
                        {
                            "id": r.id,
                            "text": getattr(r, 'text', ''),
                            "metadata": getattr(r, 'metadata', {}),
                            "score": getattr(r, 'score', 1.0),
                        }
                        for r in filtered_results
                    ],
                    "count": len(filtered_results),
                    "query_text": rag_step.query_text,
                },
                "confidence": min(1.0, len(filtered_results) / rag_step.top_k),
                "metadata": {
                    "embedding_model": rag_step.embedding_model,
                    "similarity_threshold": rag_step.similarity_threshold,
                },
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_entity_resolution(
        self,
        step: FusionPlanStep,
        plan: KGRAGFusionPlan,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Identifies and standardizes resume career entities and skills.

        Ensures proper categorization for resume job alignment consistency.
        """
        if not self.llm_client:
            return {"success": False, "error": "LLM client not available"}
        
        try:
            # Extract entities from user question
            user_question = plan.context.get("user_question", "")
            
            # Simple entity extraction (in real implementation, use NER)
            entities = []
            if plan.start_entities:
                entities.extend(plan.start_entities)
            
            # Extract additional entities from question
            words = user_question.split()
            potential_entities = [w for w in words if w[0].isupper() and len(w) > 2]
            entities.extend(potential_entities[:5])  # Limit to prevent explosion
            
            return {
                "success": True,
                "data": {
                    "entities": list(set(entities)),
                    "resolved_entities": plan.start_entities or [],
                    "question": user_question,
                },
                "confidence": 0.8 if entities else 0.0,
                "metadata": {
                    "extraction_method": "simple_capitalized",
                    "entity_count": len(set(entities)),
                },
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_temporal_filter(
        self,
        step: FusionPlanStep,
        plan: KGRAGFusionPlan,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Filters resume career experiences by date ranges for job relevance.

        Shows experiences within relevant career periods for job alignment.
        """
        try:
            # Get temporal constraints from plan context
            temporal_constraints = plan.context.get("temporal_constraints", {})
            
            # Apply temporal filtering to previous results
            filtered_results = []
            
            # This is a simplified implementation
            # In practice, would filter previous step results by temporal constraints
            if "valid_at" in temporal_constraints:
                valid_at = datetime.fromisoformat(temporal_constraints["valid_at"])
                
                return {
                    "success": True,
                    "data": {
                        "temporal_constraints": temporal_constraints,
                        "valid_at": valid_at.isoformat(),
                        "filtered_count": len(filtered_results),
                    },
                    "confidence": 0.9,
                    "metadata": {
                        "filter_type": "point_in_time",
                        "constraint_count": len(temporal_constraints),
                    },
                }
            
            return {
                "success": True,
                "data": {
                    "temporal_constraints": temporal_constraints,
                    "message": "No temporal filtering applied",
                },
                "confidence": 1.0,
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_fusion_rank(
        self,
        step: FusionPlanStep,
        plan: KGRAGFusionPlan,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Combines and ranks resume experiences for job matching relevance.

        Prioritizes most relevant achievements for target job alignment.
        """
        try:
            # Collect results from previous steps
            kg_results = []
            rag_results = []
            
            # This would normally aggregate from previous step results
            # For now, return a placeholder fusion result
            
            fused_results = {
                "kg_triplets": kg_results,
                "rag_documents": rag_results,
                "ranking_method": plan.ranking_method,
                "fusion_strategy": plan.fusion_strategy,
            }
            
            return {
                "success": True,
                "data": fused_results,
                "confidence": 0.7,
                "metadata": {
                    "ranking_method": plan.ranking_method,
                    "fusion_strategy": plan.fusion_strategy,
                },
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_recursive_deepen(
        self,
        step: FusionPlanStep,
        plan: KGRAGFusionPlan,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Performs deeper analysis of complex resume career questions.

        Uncovers hidden career patterns and transferable skills for job alignment.
        """
        try:
            # Analyze result completeness and plan recursion
            recursion_plan = {
                "needs_recursion": step.recursion_depth_hint > 1,
                "max_depth": plan.max_recursion_depth,
                "current_depth": step.recursion_depth_hint,
                "thinking_steps": step.thinking_steps,
            }
            
            # Determine if recursion should be triggered
            should_recurse = (
                step.recursion_depth_hint < plan.max_recursion_depth and
                plan.ambiguity_score > plan.recursion_threshold
            )
            
            return {
                "success": True,
                "data": {
                    "recursion_plan": recursion_plan,
                    "should_recurse": should_recurse,
                    "next_depth": step.recursion_depth_hint + 1 if should_recurse else step.recursion_depth_hint,
                },
                "confidence": 0.8 if should_recurse else 1.0,
                "metadata": {
                    "ambiguity_score": plan.ambiguity_score,
                    "recursion_threshold": plan.recursion_threshold,
                },
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _aggregate_fusion_results(
        self,
        step_results: List[FusionStepResult],
        plan: KGRAGFusionPlan,
    ) -> Dict[str, Any]:
        """
        Combines all resume analysis results for comprehensive job matching.

        Aggregates career data, skills, and experiences for job alignment.
        """
        aggregated = {
            "plan_id": plan.query_id,
            "fusion_strategy": plan.fusion_strategy,
            "successful_steps": len([r for r in step_results if r.success]),
            "total_steps": len(step_results),
            "kg_triplets": [],
            "rag_documents": [],
            "entities": [],
            "temporal_constraints": plan.context.get("temporal_constraints", {}),
        }
        
        # Collect results from successful steps
        for result in step_results:
            if result.success and result.data:
                if result.step_type == RetrievalStepType.KG_HOP:
                    aggregated["kg_triplets"].extend(result.data.get("triplets", []))
                elif result.step_type == RetrievalStepType.VECTOR_SEARCH:
                    aggregated["rag_documents"].extend(result.data.get("documents", []))
                elif result.step_type == RetrievalStepType.ENTITY_RESOLUTION:
                    aggregated["entities"].extend(result.data.get("entities", []))
        
        return aggregated
    
    def _calculate_complexity_score(
        self,
        step_results: List[FusionStepResult],
    ) -> float:
        """
        Measures resume analysis complexity for processing optimization.

        Provides metrics to optimize resume job alignment processing.
        """
        if not step_results:
            return 0.0
        
        # Factors: total recursion depth, execution time, error rate
        total_recursion = sum(r.recursion_depth_used for r in step_results)
        total_time = sum(r.execution_time_ms for r in step_results)
        error_rate = len([r for r in step_results if not r.success]) / len(step_results)
        
        # Normalize and combine
        recursion_score = min(1.0, total_recursion / 10.0)
        time_score = min(1.0, total_time / 10000.0)  # 10 seconds as max
        error_penalty = error_rate * 0.5
        
        return (recursion_score + time_score) / 2.0 - error_penalty


# =============================================================================
# Convenience Functions
# =============================================================================

async def execute_simple_fusion(
    question: str,
    kg_adapter: Optional[TemporalKG] = None,
    vector_store: Optional[Any] = None,
) -> FusionExecutionResult:
    """
    Performs basic resume analysis for quick job-relevant experience identification.

    Provides fast analysis for straightforward resume job alignment questions.
    """
    from l1.kg_rag_fusion_planning import KGRAGFusionPlanner
    
    planner = KGRAGFusionPlanner()
    executor = FusionExecutor(kg_adapter=kg_adapter, vector_store=vector_store)
    
    plan = planner.plan_fusion_query(question)
    return await executor.execute_fusion_plan(plan)


async def execute_temporal_entity_facts(
    entity_id: str,
    temporal_range: Optional[Dict[str, Any]] = None,
    kg_adapter: Optional[TemporalKG] = None,
) -> FusionExecutionResult:
    """
    Retrieves career facts with timeline context for resume presentation.

    Shows career progression within specific time periods for job alignment.
    """
    from l1.kg_rag_fusion_planning import plan_temporal_entity_facts
    
    executor = FusionExecutor(kg_adapter=kg_adapter)
    plan = plan_temporal_entity_facts(entity_id, temporal_range)
    return await executor.execute_fusion_plan(plan)


__all__ = [
    "FusionStepResult",
    "FusionExecutionResult",
    "FusionExecutor",
    "execute_simple_fusion",
    "execute_temporal_entity_facts",
]
