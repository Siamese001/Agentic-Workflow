"""
Plans knowledge graph and document retrieval for resume analysis.

Improves resume accuracy by finding relevant job experiences
and skills that match specific positions.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime, UTC
from enum import Enum

from .kg_retrieval_planning import (
    QueryType,
    KGQueryPlan,
    KGRetrievalPlanner,
    HopSpec,
    HopDirection,
)


class RetrievalStepType(str, Enum):
    """
    Defines types of information retrieval steps for resume processing.

    Improves resume completeness by ensuring all relevant experiences
    and skills are captured systematically.
    """
    KG_HOP = "kg_hop"
    VECTOR_SEARCH = "vector_search"
    ENTITY_RESOLUTION = "entity_resolution"
    TEMPORAL_FILTER = "temporal_filter"
    FUSION_RANK = "fusion_rank"
    RECURSIVE_DEEPEN = "recursive_deepen"


class QueryComplexity(str, Enum):
    """
    Determines how complex a resume query is to process.

    Improves resume processing efficiency by matching analysis
    depth to job requirement complexity.
    """
    SIMPLE = "simple"           # Direct entity lookup
    MEDIUM = "medium"           # Multi-hop KG traversal
    COMPLEX = "complex"         # KG + RAG fusion
    VERY_COMPLEX = "very_complex"  # Temporal + recursive reasoning


@dataclass
class RAGRetrievalStep:
    """
    Defines a single document search step for resume information retrieval.

    Improves resume relevance by finding job-specific documents
    and experiences that match target positions.
    """
    
    step_type: RetrievalStepType
    step_number: int
    
    # Query specification
    query_text: Optional[str] = None
    embedding_model: Optional[str] = None
    top_k: int = 10
    similarity_threshold: float = 0.7
    
    # Filters
    metadata_filter: Optional[Dict[str, Any]] = None
    temporal_filter: Optional[Dict[str, Any]] = None
    
    # Context
    context_sources: List[str] = field(default_factory=list)
    depends_on_steps: List[int] = field(default_factory=list)
    
    # MoR hints
    recursion_priority: int = 1
    needs_deeper_thought: bool = False


@dataclass
class FusionPlanStep:
    """
    Combines knowledge graph and document search steps for resume analysis.

    Improves resume comprehensiveness by integrating structured career
    data with relevant job experiences.
    """
    
    step_type: RetrievalStepType
    step_number: int
    
    # KG-specific fields
    kg_hop: Optional[HopSpec] = None
    
    # RAG-specific fields
    rag_step: Optional[RAGRetrievalStep] = None
    
    # Shared fields
    priority: int = 1
    parallel_group: Optional[str] = None
    timeout_seconds: int = 30
    
    # MoR recursion hints
    recursion_depth_hint: int = 1
    thinking_steps: List[str] = field(default_factory=list)
    complexity_boost: float = 0.0


@dataclass
class KGRAGFusionPlan(KGQueryPlan):
    """
    Creates comprehensive retrieval plans for resume job matching analysis.

    Improves resume targeting by combining career history with job-specific
    requirements and skills for better alignment.
    """
    
    # RAG fusion components
    rag_retrieval_steps: List[RAGRetrievalStep] = field(default_factory=list)
    fusion_steps: List[FusionPlanStep] = field(default_factory=list)
    
    # MoR recursion configuration
    max_recursion_depth: int = 3
    recursion_threshold: float = 0.8  # Confidence threshold to trigger recursion
    thinking_budget: int = 5  # Max thinking steps per query
    
    # Query analysis
    query_complexity: QueryComplexity = QueryComplexity.SIMPLE
    temporal_depth_required: int = 1
    ambiguity_score: float = 0.0
    
    # Fusion strategy
    fusion_strategy: str = "late"  # "early", "late", "hybrid"
    ranking_method: str = "weighted"  # "weighted", "reciprocal", "neural"
    
    # Execution hints for L3
    estimated_compute_cost: float = 1.0
    requires_safety_review: bool = False
    risk_factors: List[str] = field(default_factory=list)


class KGRAGFusionPlanner:
    """
    Plans comprehensive résumé analysis using career data and job requirements.

    Improves résumé job matching by finding relevant experiences, skills, and achievements for target positions.
    """
    
    def __init__(self, kg_planner: Optional[KGRetrievalPlanner] = None):
        """
        Sets up the résumé analysis planner with career data processing capabilities.

        Improves résumé processing speed by using pre-configured analysis templates for common job types.
        """
        self.kg_planner = kg_planner or KGRetrievalPlanner()
        self._fusion_templates = self._build_fusion_templates()
    
    def _build_fusion_templates(self) -> Dict[str, Dict[str, Any]]:
        """
        Creates résumé analysis templates for different job categories and experience levels.

        Improves résumé relevance by using job-specific analysis patterns that highlight relevant achievements.
        """
        return {
            # Temporal entity facts with context
            "temporal_entity_context": {
                "description": "Get entity facts with temporal context and supporting documents",
                "kg_steps": 1,
                "rag_steps": 2,
                "complexity": QueryComplexity.MEDIUM,
                "fusion_strategy": "hybrid",
            },
            
            # Complex career path analysis
            "career_path_analysis": {
                "description": "Analyze career progression with skill evolution and company context",
                "kg_steps": 3,
                "rag_steps": 2,
                "complexity": QueryComplexity.COMPLEX,
                "fusion_strategy": "late",
            },
            
            # Job matching with temporal constraints
            "temporal_job_matching": {
                "description": "Match candidates to jobs with temporal skill requirements",
                "kg_steps": 2,
                "rag_steps": 3,
                "complexity": QueryComplexity.COMPLEX,
                "fusion_strategy": "hybrid",
            },
            
            # Deep recursive reasoning
            "recursive_reasoning": {
                "description": "Deep multi-hop reasoning with recursive refinement",
                "kg_steps": 4,
                "rag_steps": 3,
                "complexity": QueryComplexity.VERY_COMPLEX,
                "fusion_strategy": "early",
                "max_recursion_depth": 5,
            },
        }
    
    def plan_fusion_query(
        self,
        user_question: str,
        start_entities: Optional[List[str]] = None,
        temporal_constraints: Optional[Dict[str, Any]] = None,
        kg_config: Optional[Dict[str, Any]] = None,
        rag_config: Optional[Dict[str, Any]] = None,
        fusion_template: Optional[str] = None,
        max_recursion_depth: int = 3,
        complexity_hint: Optional[QueryComplexity] = None,
    ) -> KGRAGFusionPlan:
        """
        Creates a tailored analysis plan for résumé job matching and experience highlighting.

        Improves résumé effectiveness by identifying the most relevant career achievements and skills for specific jobs.
        """
        # Analyze query complexity
        complexity = self._analyze_query_complexity(
            user_question, start_entities, temporal_constraints, complexity_hint
        )
        
        # Generate query ID
        query_id = f"kg_rag_fusion_{datetime.now(UTC).strftime('%Y%m%d%H%M%S%f')}"
        
        # Use template if specified
        if fusion_template and fusion_template in self._fusion_templates:
            return self._plan_from_fusion_template(
                query_id, fusion_template, user_question, start_entities,
                temporal_constraints, kg_config, rag_config, max_recursion_depth
            )
        
        # Otherwise, build plan based on complexity
        if complexity == QueryComplexity.SIMPLE:
            return self._plan_simple_fusion(
                query_id, user_question, start_entities, temporal_constraints
            )
        elif complexity == QueryComplexity.MEDIUM:
            return self._plan_medium_fusion(
                query_id, user_question, start_entities, temporal_constraints,
                kg_config, rag_config
            )
        elif complexity == QueryComplexity.COMPLEX:
            return self._plan_complex_fusion(
                query_id, user_question, start_entities, temporal_constraints,
                kg_config, rag_config, max_recursion_depth
            )
        else:  # VERY_COMPLEX
            return self._plan_recursive_fusion(
                query_id, user_question, start_entities, temporal_constraints,
                kg_config, rag_config, max_recursion_depth
            )
    
    def _analyze_query_complexity(
        self,
        question: str,
        start_entities: Optional[List[str]],
        temporal_constraints: Optional[Dict[str, Any]],
        hint: Optional[QueryComplexity],
    ) -> QueryComplexity:
        """
        Determines how complex a résumé question is to analyze and process effectively.

        Improves résumé analysis efficiency by matching processing depth to job requirement complexity.
        """
        if hint:
            return hint
        
        complexity_score = 0
        
        # Question length and complexity indicators
        if len(question) > 100:
            complexity_score += 1
        if any(word in question.lower() for word in ["evolution", "progression", "history", "timeline"]):
            complexity_score += 2
        
        # Temporal constraints increase complexity
        if temporal_constraints:
            complexity_score += 1
            if any(key in temporal_constraints for key in ["range", "duration", "evolution"]):
                complexity_score += 1
        
        # Starting entities suggest KG traversal
        if start_entities and len(start_entities) > 1:
            complexity_score += 1
        
        # Multi-hop indicators
        hop_indicators = ["through", "via", "connected to", "related to", "path from"]
        if any(indicator in question.lower() for indicator in hop_indicators):
            complexity_score += 2
        
        # Map score to complexity
        if complexity_score <= 2:
            return QueryComplexity.SIMPLE
        elif complexity_score <= 4:
            return QueryComplexity.MEDIUM
        elif complexity_score <= 6:
            return QueryComplexity.COMPLEX
        else:
            return QueryComplexity.VERY_COMPLEX
    
    def _plan_from_fusion_template(
        self,
        query_id: str,
        template_name: str,
        user_question: str,
        start_entities: Optional[List[str]],
        temporal_constraints: Optional[Dict[str, Any]],
        kg_config: Optional[Dict[str, Any]],
        rag_config: Optional[Dict[str, Any]],
        max_recursion_depth: int,
    ) -> KGRAGFusionPlan:
        """
        Creates résumé analysis plans using job-specific templates for different career levels.

        Improves résumé targeting by applying proven analysis patterns for specific job categories and roles.
        """
        template = self._fusion_templates[template_name]
        
        # Build base KG plan
        kg_plan = self.kg_planner.plan_query(
            query_type=QueryType.NEIGHBORHOOD,
            start_entities=start_entities or [],
            max_hops=template["kg_steps"],
            temporal_constraint=temporal_constraints.get("valid_at") if temporal_constraints else None,
        )
        
        # Create fusion steps
        fusion_steps = []
        step_counter = 1
        
        # Add KG hops
        for i, hop in enumerate(kg_plan.hops):
            fusion_steps.append(FusionPlanStep(
                step_type=RetrievalStepType.KG_HOP,
                step_number=step_counter,
                kg_hop=hop,
                priority=2,
                recursion_depth_hint=1,
                thinking_steps=[f"Explore {hop.direction} connections"]
            ))
            step_counter += 1
        
        # Add RAG retrieval steps
        for i in range(template["rag_steps"]):
            rag_step = RAGRetrievalStep(
                step_type=RetrievalStepType.VECTOR_SEARCH,
                step_number=i,
                query_text=user_question,
                top_k=10,
                recursion_priority=1,
                needs_deeper_thought=i == 0,  # First step gets deeper thought
            )
            
            fusion_steps.append(FusionPlanStep(
                step_type=RetrievalStepType.VECTOR_SEARCH,
                step_number=step_counter,
                rag_step=rag_step,
                priority=1,
                parallel_group=f"rag_batch_{i // 2 + 1}",
                recursion_depth_hint=2 if i == 0 else 1,
                thinking_steps=[f"Retrieve context for step {i+1}"]
            ))
            step_counter += 1
        
        # Create fusion plan
        return KGRAGFusionPlan(
            query_id=query_id,
            query_type=kg_plan.query_type,
            start_entities=start_entities or [],
            hops=kg_plan.hops,
            max_hops=kg_plan.max_hops,
            temporal_constraint=kg_plan.temporal_constraint,
            
            # Fusion components
            fusion_steps=fusion_steps,
            fusion_strategy=template["fusion_strategy"],
            
            # MoR configuration
            max_recursion_depth=template.get("max_recursion_depth", max_recursion_depth),
            query_complexity=template["complexity"],
            thinking_budget=5,
            
            # Execution hints
            estimated_compute_cost=2.0 if template["complexity"] == QueryComplexity.VERY_COMPLEX else 1.5,
            requires_safety_review=template["complexity"] in [QueryComplexity.COMPLEX, QueryComplexity.VERY_COMPLEX],
            
            # Context
            context={
                "user_question": user_question,
                "template": template_name,
                "kg_config": kg_config or {},
                "rag_config": rag_config or {},
                "temporal_constraints": temporal_constraints or {},
            },
        )
    
    def _plan_simple_fusion(
        self,
        query_id: str,
        user_question: str,
        start_entities: Optional[List[str]],
        temporal_constraints: Optional[Dict[str, Any]],
    ) -> KGRAGFusionPlan:
        """
        Creates basic résumé analysis plans for straightforward job matching questions.

        Improves résumé clarity by highlighting key experiences and skills that directly match job requirements.
        """
        # Single KG hop + single RAG retrieval
        kg_plan = self.kg_planner.plan_query(
            query_type=QueryType.ENTITY_FACTS,
            start_entities=start_entities or [],
            max_hops=1,
        )
        
        fusion_steps = [
            FusionPlanStep(
                step_type=RetrievalStepType.KG_HOP,
                step_number=1,
                kg_hop=kg_plan.hops[0] if kg_plan.hops else HopSpec(hop_number=1, direction=HopDirection.OUTGOING),
                priority=1,
                recursion_depth_hint=1,
            ),
            FusionPlanStep(
                step_type=RetrievalStepType.VECTOR_SEARCH,
                step_number=2,
                rag_step=RAGRetrievalStep(
                    step_type=RetrievalStepType.VECTOR_SEARCH,
                    step_number=1,
                    query_text=user_question,
                    top_k=5,
                ),
                priority=1,
                recursion_depth_hint=1,
            ),
        ]
        
        return KGRAGFusionPlan(
            query_id=query_id,
            query_type=kg_plan.query_type,
            start_entities=start_entities or [],
            hops=kg_plan.hops,
            max_hops=1,
            fusion_steps=fusion_steps,
            fusion_strategy="late",
            query_complexity=QueryComplexity.SIMPLE,
            max_recursion_depth=1,
            context={"user_question": user_question},
        )
    
    def _plan_medium_fusion(
        self,
        query_id: str,
        user_question: str,
        start_entities: Optional[List[str]],
        temporal_constraints: Optional[Dict[str, Any]],
        kg_config: Optional[Dict[str, Any]],
        rag_config: Optional[Dict[str, Any]],
    ) -> KGRAGFusionPlan:
        """
        Creates intermediate résumé analysis plans for multi-step career progression questions.

        Improves résumé comprehensiveness by connecting related experiences and showing career growth patterns.
        """
        kg_plan = self.kg_planner.plan_query(
            query_type=QueryType.NEIGHBORHOOD,
            start_entities=start_entities or [],
            max_hops=2,
            temporal_constraint=temporal_constraints.get("valid_at") if temporal_constraints else None,
        )
        
        fusion_steps = []
        step_counter = 1
        
        # KG hops
        for hop in kg_plan.hops:
            fusion_steps.append(FusionPlanStep(
                step_type=RetrievalStepType.KG_HOP,
                step_number=step_counter,
                kg_hop=hop,
                priority=2,
                recursion_depth_hint=1,
            ))
            step_counter += 1
        
        # RAG retrieval with entity resolution
        fusion_steps.append(FusionPlanStep(
            step_type=RetrievalStepType.ENTITY_RESOLUTION,
            step_number=step_counter,
            priority=1,
            recursion_depth_hint=2,
            thinking_steps=["Resolve entity mentions in query"],
        ))
        step_counter += 1
        
        fusion_steps.append(FusionPlanStep(
            step_type=RetrievalStepType.VECTOR_SEARCH,
            step_number=step_counter,
            rag_step=RAGRetrievalStep(
                step_type=RetrievalStepType.VECTOR_SEARCH,
                step_number=1,
                query_text=user_question,
                top_k=8,
                needs_deeper_thought=True,
            ),
            priority=1,
            recursion_depth_hint=2,
        ))
        
        return KGRAGFusionPlan(
            query_id=query_id,
            query_type=kg_plan.query_type,
            start_entities=start_entities or [],
            hops=kg_plan.hops,
            max_hops=2,
            temporal_constraint=kg_plan.temporal_constraint,
            fusion_steps=fusion_steps,
            fusion_strategy="hybrid",
            query_complexity=QueryComplexity.MEDIUM,
            max_recursion_depth=2,
            thinking_budget=3,
            context={
                "user_question": user_question,
                "kg_config": kg_config or {},
                "rag_config": rag_config or {},
                "temporal_constraints": temporal_constraints or {},
            },
        )
    
    def _plan_complex_fusion(
        self,
        query_id: str,
        user_question: str,
        start_entities: Optional[List[str]],
        temporal_constraints: Optional[Dict[str, Any]],
        kg_config: Optional[Dict[str, Any]],
        rag_config: Optional[Dict[str, Any]],
        max_recursion_depth: int,
    ) -> KGRAGFusionPlan:
        """
        Creates advanced résumé analysis plans for complex career trajectory and skill transfer questions.

        Improves résumé impact by demonstrating sophisticated career progression and transferable expertise.
        """
        kg_plan = self.kg_planner.plan_query(
            query_type=QueryType.TEMPORAL_SLICE,
            start_entities=start_entities or [],
            max_hops=3,
            temporal_constraint=temporal_constraints.get("valid_at") if temporal_constraints else datetime.now(UTC),
        )
        
        fusion_steps = []
        step_counter = 1
        
        # Entity resolution first
        fusion_steps.append(FusionPlanStep(
            step_type=RetrievalStepType.ENTITY_RESOLUTION,
            step_number=step_counter,
            priority=3,
            recursion_depth_hint=2,
            thinking_steps=["Extract and resolve all entities"],
        ))
        step_counter += 1
        
        # Multi-hop KG traversal
        for i, hop in enumerate(kg_plan.hops):
            fusion_steps.append(FusionPlanStep(
                step_type=RetrievalStepType.KG_HOP,
                step_number=step_counter,
                kg_hop=hop,
                priority=2,
                recursion_depth_hint=1 + (i // 2),  # Deeper for later hops
                thinking_steps=[f"Explore hop {i+1}: {hop.direction}"],
            ))
            step_counter += 1
        
        # Temporal filtering
        if temporal_constraints:
            fusion_steps.append(FusionPlanStep(
                step_type=RetrievalStepType.TEMPORAL_FILTER,
                step_number=step_counter,
                priority=2,
                recursion_depth_hint=2,
                timeout_seconds=20,
                thinking_steps=["Apply temporal constraints"],
            ))
            step_counter += 1
        
        # Multiple RAG retrievals in parallel
        for i in range(2):
            fusion_steps.append(FusionPlanStep(
                step_type=RetrievalStepType.VECTOR_SEARCH,
                step_number=step_counter,
                rag_step=RAGRetrievalStep(
                    step_type=RetrievalStepType.VECTOR_SEARCH,
                    step_number=i,
                    query_text=user_question,
                    top_k=10,
                    needs_deeper_thought=i == 0,
                    recursion_priority=2,
                ),
                priority=1,
                parallel_group="rag_parallel",
                recursion_depth_hint=3 if i == 0 else 2,
            ))
            step_counter += 1
        
        # Fusion and ranking
        fusion_steps.append(FusionPlanStep(
            step_type=RetrievalStepType.FUSION_RANK,
            step_number=step_counter,
            priority=1,
            recursion_depth_hint=3,
            thinking_steps=["Fuse KG and RAG results with ranking"],
            depends_on_steps=list(range(1, step_counter)),
        ))
        
        return KGRAGFusionPlan(
            query_id=query_id,
            query_type=kg_plan.query_type,
            start_entities=start_entities or [],
            hops=kg_plan.hops,
            max_hops=3,
            temporal_constraint=kg_plan.temporal_constraint,
            fusion_steps=fusion_steps,
            fusion_strategy="late",
            query_complexity=QueryComplexity.COMPLEX,
            max_recursion_depth=max_recursion_depth,
            thinking_budget=5,
            temporal_depth_required=2,
            estimated_compute_cost=2.0,
            requires_safety_review=True,
            context={
                "user_question": user_question,
                "kg_config": kg_config or {},
                "rag_config": rag_config or {},
                "temporal_constraints": temporal_constraints or {},
            },
        )
    
    def _plan_recursive_fusion(
        self,
        query_id: str,
        user_question: str,
        start_entities: Optional[List[str]],
        temporal_constraints: Optional[Dict[str, Any]],
        kg_config: Optional[Dict[str, Any]],
        rag_config: Optional[Dict[str, Any]],
        max_recursion_depth: int,
    ) -> KGRAGFusionPlan:
        """
        Creates sophisticated résumé analysis plans with deep recursive reasoning for complex career narratives.

        Improves résumé persuasiveness by building compelling career stories that demonstrate growth and expertise.
        """
        kg_plan = self.kg_planner.plan_query(
            query_type=QueryType.PATH_FINDING,
            start_entities=start_entities or [],
            max_hops=4,
            temporal_constraint=temporal_constraints.get("valid_at") if temporal_constraints else None,
        )
        
        fusion_steps = []
        step_counter = 1
        
        # Initial entity resolution with deep thinking
        fusion_steps.append(FusionPlanStep(
            step_type=RetrievalStepType.ENTITY_RESOLUTION,
            step_number=step_counter,
            priority=3,
            recursion_depth_hint=3,
            thinking_steps=["Deep entity analysis", "Identify key entities", "Map entity relationships"],
        ))
        step_counter += 1
        
        # Multi-hop KG with increasing depth
        for i, hop in enumerate(kg_plan.hops):
            fusion_steps.append(FusionPlanStep(
                step_type=RetrievalStepType.KG_HOP,
                step_number=step_counter,
                kg_hop=hop,
                priority=2,
                recursion_depth_hint=min(1 + i, max_recursion_depth),
                thinking_steps=[
                    f"KG hop {i+1} analysis",
                    f"Explore {hop.direction} connections",
                    "Validate temporal consistency" if temporal_constraints else None
                ],
                complexity_boost=0.1 * i,
            ))
            step_counter += 1
        
        # Temporal analysis if needed
        if temporal_constraints:
            fusion_steps.append(FusionPlanStep(
                step_type=RetrievalStepType.TEMPORAL_FILTER,
                step_number=step_counter,
                priority=2,
                recursion_depth_hint=3,
                thinking_steps=["Temporal range analysis", "Identify key time periods", "Check for gaps"],
            ))
            step_counter += 1
        
        # Multiple staged RAG retrievals
        for stage in range(3):
            fusion_steps.append(FusionPlanStep(
                step_type=RetrievalStepType.VECTOR_SEARCH,
                step_number=step_counter,
                rag_step=RAGRetrievalStep(
                    step_type=RetrievalStepType.VECTOR_SEARCH,
                    step_number=stage,
                    query_text=user_question,
                    top_k=15,
                    needs_deeper_thought=stage < 2,
                    recursion_priority=3 - stage,
                ),
                priority=1,
                parallel_group=f"recursive_stage_{stage}",
                recursion_depth_hint=min(max_recursion_depth, 4 - stage),
                thinking_steps=[
                    f"Stage {stage+1} context retrieval",
                    "Deep semantic analysis" if stage == 0 else None,
                    "Refine search strategy" if stage == 1 else None,
                ],
            ))
            step_counter += 1
        
        # Recursive deepening step
        fusion_steps.append(FusionPlanStep(
            step_type=RetrievalStepType.RECURSIVE_DEEPEN,
            step_number=step_counter,
            priority=1,
            recursion_depth_hint=max_recursion_depth,
            thinking_steps=[
                "Analyze result completeness",
                "Identify ambiguity patterns",
                "Plan recursive refinement",
            ],
            depends_on_steps=list(range(1, step_counter)),
        ))
        step_counter += 1
        
        # Final fusion with advanced ranking
        fusion_steps.append(FusionPlanStep(
            step_type=RetrievalStepType.FUSION_RANK,
            step_number=step_counter,
            priority=1,
            recursion_depth_hint=max_recursion_depth,
            thinking_steps=[
                "Multi-modal result fusion",
                "Temporal-aware ranking",
                "Confidence calibration",
                "Final result synthesis",
            ],
            depends_on_steps=list(range(1, step_counter)),
        ))
        
        return KGRAGFusionPlan(
            query_id=query_id,
            query_type=kg_plan.query_type,
            start_entities=start_entities or [],
            hops=kg_plan.hops,
            max_hops=4,
            temporal_constraint=kg_plan.temporal_constraint,
            fusion_steps=fusion_steps,
            fusion_strategy="early",
            ranking_method="neural",
            query_complexity=QueryComplexity.VERY_COMPLEX,
            max_recursion_depth=max_recursion_depth,
            thinking_budget=8,
            temporal_depth_required=3,
            ambiguity_score=0.7,
            estimated_compute_cost=3.0,
            requires_safety_review=True,
            risk_factors=["deep_recursion", "temporal_reasoning", "multi_modal_fusion"],
            context={
                "user_question": user_question,
                "kg_config": kg_config or {},
                "rag_config": rag_config or {},
                "temporal_constraints": temporal_constraints or {},
                "recursive_mode": True,
            },
        )
    
    def get_fusion_template(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves job-specific résumé analysis templates for different career stages.

        Improves résumé processing speed by using proven templates for common job categories.
        """
        return self._fusion_templates.get(name)
    
    def list_fusion_templates(self) -> List[str]:
        """
        Lists all available résumé analysis templates for different job types and career levels.

        Improves résumé targeting by showing which specialized analysis templates are available.
        """
        return list(self._fusion_templates.keys())


# =============================================================================
# Convenience Functions
# =============================================================================

def plan_temporal_entity_facts(
    entity_id: str,
    temporal_range: Optional[Dict[str, Any]] = None,
) -> KGRAGFusionPlan:
    """
    Creates résumé analysis plans for specific career experiences with timeline context.

    Improves résumé chronology by showing career progression and experience duration for target jobs.
    """
    planner = KGRAGFusionPlanner()
    return planner.plan_fusion_query(
        user_question=f"What are the facts about {entity_id}?",
        start_entities=[entity_id],
        temporal_constraints=temporal_range,
        fusion_template="temporal_entity_context",
    )


def plan_career_path_analysis(
    person_id: str,
    include_skills: bool = True,
) -> KGRAGFusionPlan:
    """
    Creates comprehensive résumé analysis plans for career progression and skill development tracking.

    Improves résumé narrative by showing clear career advancement and skill growth patterns to recruiters.
    """
    planner = KGRAGFusionPlanner()
    question = f"What is the career progression for {person_id}?"
    if include_skills:
        question += " Include skill evolution."
    
    return planner.plan_fusion_query(
        user_question=question,
        start_entities=[person_id],
        fusion_template="career_path_analysis",
    )


def plan_recursive_reasoning(
    question: str,
    start_entities: Optional[List[str]] = None,
    max_depth: int = 5,
) -> KGRAGFusionPlan:
    """
    Creates deep résumé analysis plans with multi-level reasoning for complex career questions.

    Improves résumé depth by thoroughly analyzing career decisions and their impact on job qualifications.
    """
    planner = KGRAGFusionPlanner()
    return planner.plan_fusion_query(
        user_question=question,
        start_entities=start_entities,
        fusion_template="recursive_reasoning",
        max_recursion_depth=max_depth,
    )


__all__ = [
    "RetrievalStepType",
    "QueryComplexity",
    "RAGRetrievalStep",
    "FusionPlanStep",
    "KGRAGFusionPlan",
    "KGRAGFusionPlanner",
    "plan_temporal_entity_facts",
    "plan_career_path_analysis",
    "plan_recursive_reasoning",
]
