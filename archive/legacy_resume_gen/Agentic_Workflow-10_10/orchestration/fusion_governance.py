"""L3 Fusion Governance Layer

Top-level governance and oversight layer that fuses Temporal KG reasoning,
RAG, MoR recursion, and L5 safety into a single production-grade interface.

Layer: L3 (Orchestration / DAGs)
Responsibilities:
- Orchestrate the complete fusion pipeline (L1 → L3 → L2 → L4 → L5)
- Apply safety checkpoints at critical decision points
- Manage MoR recursion depth and compute allocation
- Provide single entry point for production queries
- Track session-level safety and compliance

Non-responsibilities:
- Planning or reasoning strategy (L1)
- Direct tool calls or execution (L2)
- State persistence or mutation (L4)
- Safety policy implementation (L5)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, UTC
from enum import Enum
import logging
import uuid

from l1.kg_rag_fusion_planning import (
    KGRAGFusionPlanner,
    KGRAGFusionPlan,
)
from l2.fusion_executor import (
    FusionExecutor,
    FusionExecutionResult,
)
from l4.temporal_schemas import (
    FusionSession,
)
from l5.policy import (
    SafetyEngine,
    SafetyContext,
    PolicyResult,
)
from l5.types import (
    SafetyFinding,
    Verdict,
    Severity,
)
from runtime.observability import start_span, end_span, emit_node_event


logger = logging.getLogger(__name__)


class FusionPhase(str, Enum):
    """Phases in the fusion pipeline."""
    PLANNING = "planning"
    PRE_EXECUTION_SAFETY = "pre_execution_safety"
    EXECUTION = "execution"
    POST_EXECUTION_SAFETY = "post_execution_safety"
    RECURSIVE_DEEPENING = "recursive_deepening"
    FINAL = "final"


class SafetyCheckpoint(str, Enum):
    """Safety checkpoints in the fusion pipeline."""
    PLAN_APPROVAL = "plan_approval"
    TOOL_CALL_APPROVAL = "tool_call_approval"
    ANSWER_FILTERING = "answer_filtering"
    RECURSION_BUDGET = "recursion_budget"


@dataclass
class SafetyWrappedResult:
    """Result wrapped with safety information."""
    
    success: bool
    answer: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    
    # Safety information
    safety_verdict: Verdict = Verdict.ALLOW
    safety_findings: List[SafetyFinding] = field(default_factory=list)
    policy_decisions: List[Dict[str, Any]] = field(default_factory=list)
    
    # Execution metadata
    session_id: str = ""
    execution_time_ms: int = 0
    recursion_depth_used: int = 1
    complexity_score: float = 0.0
    
    # Compliance
    compliance_flags: List[str] = field(default_factory=list)
    risk_assessment: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "success": self.success,
            "answer": self.answer,
            "data": self.data,
            "safety_verdict": self.safety_verdict.value,
            "safety_findings": [f.to_dict() for f in self.safety_findings],
            "policy_decisions": self.policy_decisions,
            "session_id": self.session_id,
            "execution_time_ms": self.execution_time_ms,
            "recursion_depth_used": self.recursion_depth_used,
            "complexity_score": self.complexity_score,
            "compliance_flags": self.compliance_flags,
            "risk_assessment": self.risk_assessment,
        }


@dataclass
class FusionGovernanceConfig:
    """Configuration for fusion governance."""
    
    # Safety thresholds
    max_risk_score: float = 0.8
    recursion_safety_multiplier: float = 1.2  # Higher recursion = higher scrutiny
    require_plan_approval: bool = True
    require_answer_filtering: bool = True
    
    # MoR recursion limits
    max_recursion_depth: int = 5
    recursion_timeout_minutes: int = 10
    compute_budget_per_recursion: float = 1.0
    
    # Performance
    session_timeout_minutes: int = 30
    enable_parallel_execution: bool = True
    cache_safety_decisions: bool = True
    
    # Compliance
    audit_all_sessions: bool = True
    retain_session_data_hours: int = 24
    require_user_consent_for_risky_queries: bool = True


class FusionGovernanceLayer:
    """Top-level governance layer for KG + RAG + MoR + L5 Safety fusion.
    
    This layer provides the single entry point for production-grade
    temporal knowledge graph queries with full safety oversight.
    """
    
    def __init__(
        self,
        l1_planner: KGRAGFusionPlanner,
        l2_executor: FusionExecutor,
        l5_safety_engine: SafetyEngine,
        l4_state_manager: Optional[Any] = None,
        config: Optional[FusionGovernanceConfig] = None,
    ):
        """Initialize the fusion governance layer.
        
        Args:
            l1_planner: L1 fusion planner
            l2_executor: L2 fusion executor
            l5_safety_engine: L5 safety engine
            l4_state_manager: L4 state manager for session tracking
            config: Governance configuration
        """
        self.l1_planner = l1_planner
        self.l2_executor = l2_executor
        self.l5_safety_engine = l5_safety_engine
        self.l4_state_manager = l4_state_manager
        self.config = config or FusionGovernanceConfig()
        
        # Session tracking
        self.active_sessions: Dict[str, FusionSession] = {}
        self.session_metrics: Dict[str, Dict[str, Any]] = {}
        
        # Safety decision cache
        self.safety_cache: Dict[str, PolicyResult] = {}
    
    async def run_safe_temporal_kg_rag_session(
        self,
        question: str,
        user_context: Optional[Dict[str, Any]] = None,
        safety_profile: Optional[str] = None,
        temporal_constraints: Optional[Dict[str, Any]] = None,
        max_recursion_depth: Optional[int] = None,
    ) -> SafetyWrappedResult:
        """Run a complete safe temporal KG + RAG fusion session.
        
        Args:
            question: User's natural language query
            user_context: Optional user context for safety evaluation
            safety_profile: Safety profile to apply
            temporal_constraints: Temporal filtering constraints
            max_recursion_depth: Override for recursion depth limit
            
        Returns:
            SafetyWrappedResult with answer and safety information
        """
        session_id = f"fusion_{uuid.uuid4().hex[:12]}_{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"
        start_time = datetime.now(UTC)
        
        try:
            # Create session tracking
            session = FusionSession(
                session_id=session_id,
                user_query=question,
                temporal_constraints=temporal_constraints,
                safety_profile=safety_profile,
            )
            
            if self.l4_state_manager:
                self.active_sessions[session_id] = session
            
            # Start observability span
            span = start_span("fusion.governance.session", {"session_id": session_id})
            
            emit_node_event(
                node="fusion_session",
                status="start",
                details={
                    "session_id": session_id,
                    "question": question[:100] + "..." if len(question) > 100 else question,
                    "safety_profile": safety_profile,
                }
            )
            
            # Execute fusion pipeline with safety checkpoints
            result = await self._execute_fusion_pipeline(
                session_id=session_id,
                question=question,
                user_context=user_context or {},
                safety_profile=safety_profile,
                temporal_constraints=temporal_constraints or {},
                max_recursion_depth=max_recursion_depth or self.config.max_recursion_depth,
            )
            
            # Update session with completion
            session.completed_at = datetime.now(UTC)
            session.retrieval_plan = result.data.get("plan_id") if result.data else None
            
            # Calculate execution metrics
            execution_time = int((datetime.now(UTC) - start_time).total_seconds() * 1000)
            result.session_id = session_id
            result.execution_time_ms = execution_time
            
            # Log session completion
            emit_node_event(
                node="fusion_session",
                status="success" if result.success else "blocked",
                details={
                    "session_id": session_id,
                    "execution_time_ms": execution_time,
                    "safety_verdict": result.safety_verdict.value,
                    "recursion_depth": result.recursion_depth_used,
                }
            )
            
            end_span(span)
            return result
            
        except Exception as e:
            logger.error(f"Fusion session {session_id} failed: {str(e)}")
            
            execution_time = int((datetime.now(UTC) - start_time).total_seconds() * 1000)
            
            return SafetyWrappedResult(
                success=False,
                session_id=session_id,
                execution_time_ms=execution_time,
                safety_verdict=Verdict.BLOCK,
                safety_findings=[
                    SafetyFinding(
                        id=f"session_error_{uuid.uuid4().hex[:8]}",
                        type="system",
                        severity=Severity.CRITICAL,
                        message=f"Session failed: {str(e)}",
                        details={"error": str(e), "session_id": session_id},
                        location="fusion_governance",
                    )
                ],
            )
        
        finally:
            # Clean up session
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
    
    async def _execute_fusion_pipeline(
        self,
        session_id: str,
        question: str,
        user_context: Dict[str, Any],
        safety_profile: Optional[str],
        temporal_constraints: Dict[str, Any],
        max_recursion_depth: int,
    ) -> SafetyWrappedResult:
        """Execute the complete fusion pipeline with safety checkpoints."""
        
        # Phase 1: Planning
        plan, planning_error = await self._phase_planning(
            question, temporal_constraints, max_recursion_depth
        )
        if not plan:
            return SafetyWrappedResult(
                success=False,
                safety_verdict=Verdict.BLOCK,
                safety_findings=[
                    SafetyFinding(
                        id="planning_failed",
                        type="system",
                        severity=Severity.HIGH,
                        message="Query planning failed",
                        details={"error": planning_error},
                        location="planning_phase",
                    )
                ],
            )
        
        # Phase 2: Pre-execution safety check
        safety_result = await self._phase_pre_execution_safety(
            session_id, plan, user_context, safety_profile
        )
        if safety_result.final_verdict == Verdict.BLOCK:
            return SafetyWrappedResult(
                success=False,
                safety_verdict=Verdict.BLOCK,
                safety_findings=safety_result.all_findings,
                policy_decisions=[d.to_dict() for d in safety_result.decisions],
                data={"plan_id": plan.query_id, "blocked_at": "pre_execution"},
            )
        
        # Phase 3: Execution with recursive deepening
        execution_result, final_recursion_depth = await self._phase_execution_with_recursion(
            plan, temporal_constraints, max_recursion_depth, safety_profile
        )
        
        if not execution_result.success:
            return SafetyWrappedResult(
                success=False,
                safety_verdict=Verdict.BLOCK,
                safety_findings=[
                    SafetyFinding(
                        id="execution_failed",
                        type="system",
                        severity=Severity.HIGH,
                        message="Query execution failed",
                        details={"error": execution_result.error},
                        location="execution_phase",
                    )
                ],
                data={"plan_id": plan.query_id, "blocked_at": "execution"},
            )
        
        # Phase 4: Post-execution safety filtering
        filtered_result = await self._phase_post_execution_safety(
            session_id, execution_result, user_context, safety_profile
        )
        
        if filtered_result.final_verdict == Verdict.BLOCK:
            return SafetyWrappedResult(
                success=False,
                safety_verdict=Verdict.BLOCK,
                safety_findings=filtered_result.all_findings,
                policy_decisions=[d.to_dict() for d in filtered_result.decisions],
                data={"plan_id": plan.query_id, "blocked_at": "post_execution"},
            )
        
        # Phase 5: Final result assembly
        return await self._phase_final_result_assembly(
            plan, execution_result, final_recursion_depth, filtered_result
        )
    
    async def _phase_planning(
        self,
        question: str,
        temporal_constraints: Dict[str, Any],
        max_recursion_depth: int,
    ) -> Tuple[Optional[KGRAGFusionPlan], Optional[str]]:
        """Phase 1: Generate fusion plan."""
        try:
            plan = self.l1_planner.plan_fusion_query(
                user_question=question,
                temporal_constraints=temporal_constraints,
                max_recursion_depth=max_recursion_depth,
            )
            
            return plan, None
            
        except Exception as e:
            logger.error(f"Planning phase failed: {str(e)}")
            return None, str(e)
    
    async def _phase_pre_execution_safety(
        self,
        session_id: str,
        plan: KGRAGFusionPlan,
        user_context: Dict[str, Any],
        safety_profile: Optional[str],
    ) -> PolicyResult:
        """Phase 2: Pre-execution safety checkpoint."""
        
        # Create safety context for plan approval
        safety_context = SafetyContext(
            content_type="fusion_plan",
            content=plan.to_dict() if hasattr(plan, 'to_dict') else str(plan),
            source="fusion_planning",
            destination="execution",
            user_id=user_context.get("user_id"),
            session_id=session_id,
            metadata={
                "query_complexity": plan.query_complexity.value,
                "max_recursion_depth": plan.max_recursion_depth,
                "estimated_cost": plan.estimated_compute_cost,
                "risk_factors": plan.risk_factors,
                "safety_profile": safety_profile,
            },
        )
        
        # Apply recursion safety multiplier
        if plan.max_recursion_depth > 1:
            safety_context.metadata["risk_multiplier"] = (
                self.config.recursion_safety_multiplier * plan.max_recursion_depth
            )
        
        # Check cache first
        cache_key = f"plan_approval_{hash(str(safety_context))}"
        if self.config.cache_safety_decisions and cache_key in self.safety_cache:
            return self.safety_cache[cache_key]
        
        # Evaluate safety
        policy_result = self.l5_safety_engine.evaluate(safety_context)
        
        # Cache result
        if self.config.cache_safety_decisions:
            self.safety_cache[cache_key] = policy_result
        
        return policy_result
    
    async def _phase_execution_with_recursion(
        self,
        plan: KGRAGFusionPlan,
        temporal_constraints: Dict[str, Any],
        max_recursion_depth: int,
        safety_profile: Optional[str],
    ) -> Tuple[FusionExecutionResult, int]:
        """Phase 3: Execute with recursive deepening."""
        
        current_result = None
        current_depth = 1
        
        while current_depth <= max_recursion_depth:
            try:
                # Execute current plan
                execution_context = {
                    "recursion_depth": current_depth,
                    "temporal_constraints": temporal_constraints,
                    "safety_profile": safety_profile,
                }
                
                current_result = await self.l2_executor.execute_fusion_plan(
                    plan, execution_context
                )
                
                # Check if recursion should continue
                should_continue = await self._should_continue_recursion(
                    current_result, plan, current_depth, max_recursion_depth
                )
                
                if not should_continue or not current_result.success:
                    break
                
                # Plan next recursion level if needed
                if current_depth < max_recursion_depth:
                    plan = await self._plan_next_recursion_level(
                        plan, current_result, current_depth
                    )
                
                current_depth += 1
                
            except Exception as e:
                logger.error(f"Execution at depth {current_depth} failed: {str(e)}")
                break
        
        final_result = current_result or FusionExecutionResult(
            plan_id=plan.query_id,
            success=False,
            error="All execution attempts failed",
        )
        
        return final_result, current_depth
    
    async def _phase_post_execution_safety(
        self,
        session_id: str,
        execution_result: FusionExecutionResult,
        user_context: Dict[str, Any],
        safety_profile: Optional[str],
    ) -> PolicyResult:
        """Phase 4: Post-execution safety filtering."""
        
        # Extract answer from execution result
        answer_text = self._extract_answer_from_result(execution_result)
        
        if not answer_text:
            return PolicyResult()  # No content to filter
        
        # Create safety context for answer filtering
        safety_context = SafetyContext(
            content_type="fusion_answer",
            content=answer_text,
            source="execution",
            destination="user",
            user_id=user_context.get("user_id"),
            session_id=session_id,
            metadata={
                "execution_success": execution_result.success,
                "complexity_score": execution_result.complexity_score,
                "safety_profile": safety_profile,
            },
        )
        
        # Evaluate safety
        policy_result = self.l5_safety_engine.evaluate(safety_context)
        
        return policy_result
    
    async def _phase_final_result_assembly(
        self,
        plan: KGRAGFusionPlan,
        execution_result: FusionExecutionResult,
        recursion_depth: int,
        safety_result: PolicyResult,
    ) -> SafetyWrappedResult:
        """Phase 5: Assemble final result."""
        
        # Extract answer
        answer = self._extract_answer_from_result(execution_result)
        
        # Apply safety filtering if needed
        if safety_result.final_verdict == Verdict.REVIEW:
            answer = self._apply_safety_filtering(answer, safety_result)
        
        # Assess compliance
        compliance_flags = self._assess_compliance(plan, execution_result, safety_result)
        
        # Calculate risk assessment
        risk_assessment = {
            "complexity_risk": plan.estimated_compute_cost,
            "recursion_risk": recursion_depth / self.config.max_recursion_depth,
            "safety_risk": len(safety_result.blocking_findings) / max(1, len(safety_result.all_findings)),
            "overall_risk": min(1.0, (
                plan.estimated_compute_cost * 0.3 +
                (recursion_depth / self.config.max_recursion_depth) * 0.3 +
                (len(safety_result.blocking_findings) / max(1, len(safety_result.all_findings))) * 0.4
            )),
        }
        
        return SafetyWrappedResult(
            success=True,
            answer=answer,
            data={
                "plan_id": plan.query_id,
                "execution_metrics": execution_result.final_results,
                "fusion_strategy": plan.fusion_strategy,
            },
            safety_verdict=safety_result.final_verdict,
            safety_findings=safety_result.all_findings,
            policy_decisions=[d.to_dict() for d in safety_result.decisions],
            recursion_depth_used=recursion_depth,
            complexity_score=execution_result.complexity_score,
            compliance_flags=compliance_flags,
            risk_assessment=risk_assessment,
        )
    
    async def _should_continue_recursion(
        self,
        result: FusionExecutionResult,
        plan: KGRAGFusionPlan,
        current_depth: int,
        max_depth: int,
    ) -> bool:
        """Determine if recursion should continue."""
        
        if not result.success or current_depth >= max_depth:
            return False
        
        # Check ambiguity score and recursion threshold
        if result.complexity_score < plan.recursion_threshold:
            return False
        
        # Check if any step indicated need for deeper thought
        for step_result in result.step_results:
            if hasattr(step_result, 'data') and step_result.data:
                if step_result.data.get("should_recurse", False):
                    return True
        
        return False
    
    async def _plan_next_recursion_level(
        self,
        current_plan: KGRAGFusionPlan,
        execution_result: FusionExecutionResult,
        current_depth: int,
    ) -> KGRAGFusionPlan:
        """Plan the next level of recursion."""
        
        # Create a refined plan based on execution results
        # This is a simplified implementation
        refined_plan = KGRAGFusionPlan(
            query_id=f"{current_plan.query_id}_recursion_{current_depth + 1}",
            query_type=current_plan.query_type,
            start_entities=current_plan.start_entities,
            hops=current_plan.hops,
            fusion_steps=current_plan.fusion_steps,
            max_recursion_depth=current_plan.max_recursion_depth,
            recursion_threshold=current_plan.recursion_threshold * 0.9,  # Lower threshold for deeper recursion
            thinking_budget=current_plan.thinking_budget + 2,  # More thinking budget
            context={
                **current_plan.context,
                "recursion_level": current_depth + 1,
                "previous_results": execution_result.final_results,
            },
        )
        
        return refined_plan
    
    def _extract_answer_from_result(self, result: FusionExecutionResult) -> Optional[str]:
        """Extract answer text from execution result."""
        
        if not result.success or not result.final_results:
            return None
        
        # Try to extract answer from different result formats
        final_results = result.final_results
        
        # Check for direct answer
        if "answer" in final_results:
            return final_results["answer"]
        
        # Check for synthesized content
        if "synthesized_content" in final_results:
            return final_results["synthesized_content"]
        
        # Check for fusion results
        if "fusion_results" in final_results:
            fusion_data = final_results["fusion_results"]
            if isinstance(fusion_data, dict) and "summary" in fusion_data:
                return fusion_data["summary"]
        
        # Fallback: create a summary from available data
        return self._create_fallback_summary(final_results)
    
    def _create_fallback_summary(self, results: Dict[str, Any]) -> str:
        """Create a fallback summary from execution results."""
        
        summary_parts = []
        
        if results.get("kg_triplets"):
            summary_parts.append(f"Found {len(results['kg_triplets'])} relevant knowledge graph facts")
        
        if results.get("rag_documents"):
            summary_parts.append(f"Retrieved {len(results['rag_documents'])} relevant documents")
        
        if results.get("entities"):
            summary_parts.append(f"Identified {len(results['entities'])} key entities")
        
        if not summary_parts:
            return "Query processed, but no specific results were generated."
        
        return " | ".join(summary_parts)
    
    def _apply_safety_filtering(
        self,
        answer: Optional[str],
        safety_result: PolicyResult,
    ) -> Optional[str]:
        """Apply safety filtering to answer."""
        
        if not answer:
            return answer
        
        # Simple redaction based on findings
        filtered_answer = answer
        
        for finding in safety_result.blocking_findings:
            if finding.location and finding.location in filtered_answer:
                # Redact problematic content
                filtered_answer = filtered_answer.replace(finding.location, "[REDACTED]")
        
        return filtered_answer
    
    def _assess_compliance(
        self,
        plan: KGRAGFusionPlan,
        execution_result: FusionExecutionResult,
        safety_result: PolicyResult,
    ) -> List[str]:
        """Assess compliance flags."""
        
        flags = []
        
        # Check complexity compliance
        if plan.estimated_compute_cost > self.config.max_risk_score:
            flags.append("high_complexity")
        
        # Check recursion compliance
        if execution_result.total_recursion_depth > self.config.max_recursion_depth:
            flags.append("excessive_recursion")
        
        # Check safety compliance
        if safety_result.blocking_findings:
            flags.append("safety_violations")
        
        # Check temporal compliance
        if plan.context.get("temporal_constraints"):
            flags.append("temporal_reasoning")
        
        return flags
    
    def get_session_status(self, session_id: str) -> Optional[FusionSession]:
        """Get status of a fusion session."""
        return self.active_sessions.get(session_id)
    
    def list_active_sessions(self) -> List[FusionSession]:
        """List all currently active sessions."""
        return list(self.active_sessions.values())
    
    def get_governance_metrics(self) -> Dict[str, Any]:
        """Get governance layer metrics."""
        return {
            "active_sessions": len(self.active_sessions),
            "cached_safety_decisions": len(self.safety_cache),
            "total_sessions_processed": len(self.session_metrics),
            "average_session_time": (
                sum(m.get("execution_time_ms", 0) for m in self.session_metrics.values()) /
                max(1, len(self.session_metrics))
            ),
        }


# =============================================================================
# Convenience Functions
# =============================================================================

async def ask_temporal_kg_question(
    question: str,
    kg_adapter: Optional[Any] = None,
    vector_store: Optional[Any] = None,
    safety_engine: Optional[SafetyEngine] = None,
    user_context: Optional[Dict[str, Any]] = None,
) -> SafetyWrappedResult:
    """Ask a question to the temporal KG with full safety oversight."""
    
    # Initialize components
    planner = KGRAGFusionPlanner()
    executor = FusionExecutor(kg_adapter=kg_adapter, vector_store=vector_store)
    safety = safety_engine or SafetyEngine()
    
    # Create governance layer
    governance = FusionGovernanceLayer(
        l1_planner=planner,
        l2_executor=executor,
        l5_safety_engine=safety,
    )
    
    # Execute query
    return await governance.run_safe_temporal_kg_rag_session(
        question=question,
        user_context=user_context,
    )


__all__ = [
    "FusionPhase",
    "SafetyCheckpoint",
    "SafetyWrappedResult",
    "FusionGovernanceConfig",
    "FusionGovernanceLayer",
    "ask_temporal_kg_question",
]
