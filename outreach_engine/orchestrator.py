"""L3 Orchestrator - Coordinates the complete L1→K1-K7 hop-based pipeline.

Incorporated from L3 lic_orchestrator.py to orchestrate the full hop-based
architecture with all 6 L1 planners and 7 K executors for end-to-end
outreach message generation.

This is the L3 orchestration layer that coordinates:
L1 Planning (fusion, grounding, persona, profile, research, message)
→ K1 Research → K2 Insights → K3 Draft → K4 Regeneration → K5 Validation → K6 CTA → K7 Assembly
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import logging
import time

logger = logging.getLogger(__name__)


# Import all L1 planners
from .fusion_planner import FusionPlanner, FusionPlan
from .grounding_planner import GroundingPlanner, GroundingPlan
from .persona_planner import PersonaPlanner, PersonaPlan
from .profile_planner import ProfilePlanner, ProfilePlan
from .research_planner import ResearchPlanner, ResearchPlan
from .message_planner import MessagePlanner, MessagePlan

# Import all K executors
from .k1_research import K1ResearchExecutor, ResearchOutput
from .k2_insights import K2InsightsExecutor, InsightOutput
from .k3_draft import K3DraftExecutor, DraftOutput
from .k4_regen import K4RegenExecutor, RegenOutput
from .k5_validation import K5ValidationExecutor, ValidationOutput
from .k6_cta import K6CTAExecutor, CTAOutput
from .k7_assembly import K7AssemblyExecutor, AssemblyOutput


@dataclass
class OrchestratorOutput:
    """Complete output from the L3 orchestrator."""
    final_message: str
    execution_trace: List[Dict[str, Any]]
    l1_plans: Dict[str, Any]
    k_node_outputs: Dict[str, Any]
    success: bool
    error_message: str
    execution_time_ms: int
    pipeline_confidence: float
    delivery_format: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class OutreachOrchestrator:
    """L3 orchestrator for the complete hop-based outreach pipeline.
    
    Coordinates all 6 L1 planners and 7 K executors in sequence:
    L1 Planning → K1 Research → K2 Insights → K3 Draft → K4 Regeneration → K5 Validation → K6 CTA → K7 Assembly
    """
    
    def __init__(self, 
                 atomic_spec: Optional[Dict[str, Any]] = None,
                 telemetry_bus: Optional[Any] = None) -> None:
        """Initialize outreach orchestrator."""
        self.spec = atomic_spec or {}
        self.telemetry_bus = telemetry_bus
        
        # Initialize all L1 planners
        self.fusion_planner = FusionPlanner()
        self.grounding_planner = GroundingPlanner()
        self.persona_planner = PersonaPlanner()
        self.profile_planner = ProfilePlanner()
        self.research_planner = ResearchPlanner()
        self.message_planner = MessagePlanner()
        
        # Initialize all K executors
        self.k1_research = K1ResearchExecutor()
        self.k2_insights = K2InsightsExecutor()
        self.k3_draft = K3DraftExecutor()
        self.k4_regen = K4RegenExecutor()
        self.k5_validation = K5ValidationExecutor()
        self.k6_cta = K6CTAExecutor()
        self.k7_assembly = K7AssemblyExecutor()
    
    def execute_outreach_pipeline(
        self,
        *,
        recipient_profile: Dict[str, Any],
        resume_features: Optional[Dict[str, Any]] = None,
        outreach_context: Optional[Dict[str, Any]] = None
    ) -> OrchestratorOutput:
        """Execute the complete L1→K1-K7 hop-based outreach pipeline.
        
        Args:
            recipient_profile: Target recipient profile data
            resume_features: Optional resume features for fusion planning
            outreach_context: Additional context for message generation
            
        Returns:
            Complete orchestrated output with final message and execution trace
        """
        start_time = time.time()
        outreach_context = outreach_context or {}
        
        execution_trace = []
        l1_plans = {}
        k_node_outputs = {}
        
        try:
            # === L1 PLANNING PHASE ===
            logger.info("Starting L1 Planning Phase")
            l1_start = time.time()
            
            # 1. Profile planning
            profile_plan = self._execute_l1_profile_planning(recipient_profile, outreach_context)
            l1_plans["profile"] = profile_plan
            execution_trace.append({
                "phase": "L1",
                "component": "profile_planner",
                "status": "SUCCESS",
                "timestamp": time.time()
            })
            
            # 2. Research planning
            research_plan = self._execute_l1_research_planning(recipient_profile, profile_plan, outreach_context)
            l1_plans["research"] = research_plan
            execution_trace.append({
                "phase": "L1", 
                "component": "research_planner",
                "status": "SUCCESS",
                "timestamp": time.time()
            })
            
            # 3. Grounding planning
            grounding_plan = self._execute_l1_grounding_planning(resume_features, outreach_context)
            l1_plans["grounding"] = grounding_plan
            execution_trace.append({
                "phase": "L1",
                "component": "grounding_planner", 
                "status": "SUCCESS",
                "timestamp": time.time()
            })
            
            # 4. Persona planning
            persona_plan = self._execute_l1_persona_planning(profile_plan, grounding_plan, outreach_context)
            l1_plans["persona"] = persona_plan
            execution_trace.append({
                "phase": "L1",
                "component": "persona_planner",
                "status": "SUCCESS", 
                "timestamp": time.time()
            })
            
            # 5. Fusion planning
            fusion_plan = self._execute_l1_fusion_planning(resume_features, research_plan, grounding_plan, outreach_context)
            l1_plans["fusion"] = fusion_plan
            execution_trace.append({
                "phase": "L1",
                "component": "fusion_planner",
                "status": "SUCCESS",
                "timestamp": time.time()
            })
            
            # 6. Message planning
            message_plan = self._execute_l1_message_planning(recipient_profile, persona_plan, grounding_plan, fusion_plan, outreach_context)
            l1_plans["message"] = message_plan
            execution_trace.append({
                "phase": "L1",
                "component": "message_planner",
                "status": "SUCCESS",
                "timestamp": time.time()
            })
            
            l1_time = time.time() - l1_start
            logger.info(f"L1 Planning Phase completed in {l1_time:.2f}s")
            
            # === K-NODE EXECUTION PHASE ===
            logger.info("Starting K-Node Execution Phase")
            k_start = time.time()
            
            # K1: Research
            k1_output = self._execute_k1_research(research_plan, recipient_profile, outreach_context)
            k_node_outputs["k1_research"] = k1_output
            execution_trace.append({
                "phase": "K1",
                "component": "research_executor",
                "status": "SUCCESS" if k1_output else "FAILED",
                "timestamp": time.time()
            })
            
            # K2: Insights
            k2_output = self._execute_k2_insights(k1_output, outreach_context)
            k_node_outputs["k2_insights"] = k2_output
            execution_trace.append({
                "phase": "K2",
                "component": "insights_executor", 
                "status": "SUCCESS" if k2_output else "FAILED",
                "timestamp": time.time()
            })
            
            # K3: Draft
            k3_output = self._execute_k3_draft(fusion_plan, persona_plan, grounding_plan, profile_plan, research_plan, message_plan, k2_output, recipient_profile, outreach_context)
            k_node_outputs["k3_draft"] = k3_output
            execution_trace.append({
                "phase": "K3",
                "component": "draft_executor",
                "status": "SUCCESS" if k3_output else "FAILED",
                "timestamp": time.time()
            })
            
            # K4: Regeneration
            k4_output = self._execute_k4_regeneration(k3_output, k2_output, persona_plan, message_plan, outreach_context)
            k_node_outputs["k4_regen"] = k4_output
            execution_trace.append({
                "phase": "K4",
                "component": "regen_executor",
                "status": "SUCCESS" if k4_output else "FAILED", 
                "timestamp": time.time()
            })
            
            # K5: Validation
            k5_output = self._execute_k5_validation(k4_output, persona_plan, message_plan, outreach_context)
            k_node_outputs["k5_validation"] = k5_output
            execution_trace.append({
                "phase": "K5",
                "component": "validation_executor",
                "status": "SUCCESS" if k5_output else "FAILED",
                "timestamp": time.time()
            })
            
            # K6: CTA
            k6_output = self._execute_k6_cta(k5_output, persona_plan, message_plan, fusion_plan, recipient_profile, outreach_context)
            k_node_outputs["k6_cta"] = k6_output
            execution_trace.append({
                "phase": "K6",
                "component": "cta_executor",
                "status": "SUCCESS" if k6_output else "FAILED",
                "timestamp": time.time()
            })
            
            # K7: Assembly
            k7_output = self._execute_k7_assembly(k1_output, k2_output, k3_output, k4_output, k5_output, k6_output, l1_plans, outreach_context)
            k_node_outputs["k7_assembly"] = k7_output
            execution_trace.append({
                "phase": "K7",
                "component": "assembly_executor",
                "status": "SUCCESS" if k7_output else "FAILED",
                "timestamp": time.time()
            })
            
            k_time = time.time() - k_start
            logger.info(f"K-Node Execution Phase completed in {k_time:.2f}s")
            
            # Calculate final metrics
            execution_time_ms = int((time.time() - start_time) * 1000)
            pipeline_confidence = getattr(k7_output, 'pipeline_confidence', 0.0) if k7_output else 0.0
            delivery_format = outreach_context.get("delivery_format", "email")
            
            # Create final output
            output = OrchestratorOutput(
                final_message=getattr(k7_output, 'final_message', '') if k7_output else '',
                execution_trace=execution_trace,
                l1_plans=l1_plans,
                k_node_outputs=k_node_outputs,
                success=k7_output is not None and getattr(k7_output, 'validation_status', 'invalid') == 'valid',
                error_message='' if k7_output else 'Pipeline execution failed',
                execution_time_ms=execution_time_ms,
                pipeline_confidence=pipeline_confidence,
                delivery_format=delivery_format,
                metadata={
                    "l1_planning_time_ms": int(l1_time * 1000),
                    "k_execution_time_ms": int(k_time * 1000),
                    "hop_based_pipeline": True,
                    "total_components": len(l1_plans) + len(k_node_outputs)
                }
            )
            
            # Record telemetry
            self._safe_record_orchestration_telemetry(output)
            
            return output
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {str(e)}")
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            return OrchestratorOutput(
                final_message='',
                execution_trace=execution_trace,
                l1_plans=l1_plans,
                k_node_outputs=k_node_outputs,
                success=False,
                error_message=str(e),
                execution_time_ms=execution_time_ms,
                pipeline_confidence=0.0,
                delivery_format=outreach_context.get("delivery_format", "email"),
                metadata={"error_phase": "execution"}
            )
    
    def _execute_l1_profile_planning(self, recipient_profile: Dict[str, Any], context: Dict[str, Any]) -> ProfilePlan:
        """Execute L1 profile planning."""
        return self.profile_planner.plan(
            recipient_profile=recipient_profile,
            outreach_context=context
        )
    
    def _execute_l1_research_planning(self, recipient_profile: Dict[str, Any], profile_plan: ProfilePlan, context: Dict[str, Any]) -> ResearchPlan:
        """Execute L1 research planning."""
        return self.research_planner.plan(
            role_title=recipient_profile.get("title", ""),
            company_name=recipient_profile.get("company", ""),
            archetype=profile_plan.inferred_archetype,
            recipient_profile=recipient_profile,
            outreach_context=context
        )
    
    def _execute_l1_grounding_planning(self, resume_features: Optional[Dict[str, Any]], context: Dict[str, Any]) -> GroundingPlan:
        """Execute L1 grounding planning."""
        return self.grounding_planner.plan(
            resume_features=resume_features or {},
            outreach_context=context
        )
    
    def _execute_l1_persona_planning(self, profile_plan: ProfilePlan, grounding_plan: GroundingPlan, context: Dict[str, Any]) -> PersonaPlan:
        """Execute L1 persona planning."""
        recipient_profile = {"archetype": profile_plan.inferred_archetype, "seniority": profile_plan.seniority_level, "industry": profile_plan.industry_focus}
        return self.persona_planner.plan(
            archetype=profile_plan.inferred_archetype,
            recipient_profile=recipient_profile,
            grounding_plan=grounding_plan,
            outreach_context=context
        )
    
    def _execute_l1_fusion_planning(self, resume_features: Optional[Dict[str, Any]], research_plan: ResearchPlan, grounding_plan: GroundingPlan, context: Dict[str, Any]) -> FusionPlan:
        """Execute L1 fusion planning."""
        return self.fusion_planner.plan(
            role_title=research_plan.target_role,
            company_name=research_plan.target_company,
            archetype=research_plan.archetype,
            resume_features=resume_features or {},
            research_signals={"archetype": research_plan.archetype},
            rag_evidence=[]
        )
    
    def _execute_l1_message_planning(self, recipient_profile: Dict[str, Any], persona_plan: PersonaPlan, grounding_plan: GroundingPlan, fusion_plan: FusionPlan, context: Dict[str, Any]) -> MessagePlan:
        """Execute L1 message planning."""
        from .message_planner import MessageContent
        
        content = MessageContent(
            recipient_name=recipient_profile.get("first_name", ""),
            recipient_title=recipient_profile.get("title", ""),
            company_name=recipient_profile.get("company", ""),
            value_proposition="value proposition",  # Would be populated from fusion plan
            key_points=[],
            personalization_elements=[],
            constraints=[],
            metadata={}
        )
        
        return self.message_planner.plan(
            content=content,
            archetype=persona_plan.archetype,
            persona_plan=persona_plan,
            grounding_plan=grounding_plan,
            fusion_plan=fusion_plan,
            outreach_context=context
        )
    
    def _execute_k1_research(self, research_plan: ResearchPlan, recipient_profile: Dict[str, Any], context: Dict[str, Any]) -> Optional[ResearchOutput]:
        """Execute K1 research."""
        try:
            return self.k1_research.execute(
                research_plan=research_plan,
                recipient_profile=recipient_profile,
                outreach_context=context
            )
        except Exception as e:
            logger.error(f"K1 research failed: {e}")
            return None
    
    def _execute_k2_insights(self, k1_output: Optional[ResearchOutput], context: Dict[str, Any]) -> Optional[InsightOutput]:
        """Execute K2 insights."""
        try:
            if not k1_output:
                return None
            return self.k2_insights.execute(
                research_output=k1_output,
                outreach_context=context
            )
        except Exception as e:
            logger.error(f"K2 insights failed: {e}")
            return None
    
    def _execute_k3_draft(self, fusion_plan: FusionPlan, persona_plan: PersonaPlan, grounding_plan: GroundingPlan, profile_plan: ProfilePlan, research_plan: ResearchPlan, message_plan: MessagePlan, k2_output: Optional[InsightOutput], recipient_profile: Dict[str, Any], context: Dict[str, Any]) -> Optional[DraftOutput]:
        """Execute K3 draft."""
        try:
            return self.k3_draft.execute(
                fusion_plan=fusion_plan,
                persona_plan=persona_plan,
                grounding_plan=grounding_plan,
                profile_plan=profile_plan,
                research_plan=research_plan,
                message_plan=message_plan,
                insights_output=k2_output,
                recipient_profile=recipient_profile,
                outreach_context=context
            )
        except Exception as e:
            logger.error(f"K3 draft failed: {e}")
            return None
    
    def _execute_k4_regeneration(self, k3_output: Optional[DraftOutput], k2_output: Optional[InsightOutput], persona_plan: PersonaPlan, message_plan: MessagePlan, context: Dict[str, Any]) -> Optional[RegenOutput]:
        """Execute K4 regeneration."""
        try:
            if not k3_output:
                return None
            return self.k4_regen.execute(
                draft_output=k3_output,
                insights_output=k2_output,
                persona_plan=persona_plan,
                message_plan=message_plan,
                outreach_context=context
            )
        except Exception as e:
            logger.error(f"K4 regeneration failed: {e}")
            return None
    
    def _execute_k5_validation(self, k4_output: Optional[RegenOutput], persona_plan: PersonaPlan, message_plan: MessagePlan, context: Dict[str, Any]) -> Optional[ValidationOutput]:
        """Execute K5 validation."""
        try:
            if not k4_output:
                return None
            return self.k5_validation.execute(
                regen_output=k4_output,
                persona_plan=persona_plan,
                message_plan=message_plan,
                outreach_context=context
            )
        except Exception as e:
            logger.error(f"K5 validation failed: {e}")
            return None
    
    def _execute_k6_cta(self, k5_output: Optional[ValidationOutput], persona_plan: PersonaPlan, message_plan: MessagePlan, fusion_plan: FusionPlan, recipient_profile: Dict[str, Any], context: Dict[str, Any]) -> Optional[CTAOutput]:
        """Execute K6 CTA."""
        try:
            if not k5_output:
                return None
            return self.k6_cta.execute(
                validation_output=k5_output,
                persona_plan=persona_plan,
                message_plan=message_plan,
                fusion_plan=fusion_plan,
                recipient_profile=recipient_profile,
                outreach_context=context
            )
        except Exception as e:
            logger.error(f"K6 CTA failed: {e}")
            return None
    
    def _execute_k7_assembly(self, k1_output: Optional[ResearchOutput], k2_output: Optional[InsightOutput], k3_output: Optional[DraftOutput], k4_output: Optional[RegenOutput], k5_output: Optional[ValidationOutput], k6_output: Optional[CTAOutput], l1_plans: Dict[str, Any], context: Dict[str, Any]) -> Optional[AssemblyOutput]:
        """Execute K7 assembly."""
        try:
            if not all([k1_output, k2_output, k3_output, k4_output, k5_output, k6_output]):
                return None
            return self.k7_assembly.execute(
                k1_research_output=k1_output,
                k2_insights_output=k2_output,
                k3_draft_output=k3_output,
                k4_regen_output=k4_output,
                k5_validation_output=k5_output,
                k6_cta_output=k6_output,
                l1_plans=l1_plans,
                outreach_context=context
            )
        except Exception as e:
            logger.error(f"K7 assembly failed: {e}")
            return None
    
    def _safe_record_orchestration_telemetry(self, output: OrchestratorOutput) -> None:
        """Record orchestration telemetry (best-effort)."""
        try:
            if self.telemetry_bus:
                self.telemetry_bus.record("orchestrator_executed", {
                    "success": output.success,
                    "execution_time_ms": output.execution_time_ms,
                    "pipeline_confidence": output.pipeline_confidence,
                    "l1_plans_count": len(output.l1_plans),
                    "k_nodes_count": len(output.k_node_outputs),
                    "hop_based_pipeline": True
                })
        except Exception as e:
            logger.debug(f"Failed to record orchestration telemetry: {e}")
    
    def get_orchestration_summary(self, output: OrchestratorOutput) -> Dict[str, Any]:
        """Get a summary of the orchestration execution."""
        return {
            "success": output.success,
            "execution_time_ms": output.execution_time_ms,
            "pipeline_confidence": output.pipeline_confidence,
            "l1_plans_executed": list(output.l1_plans.keys()),
            "k_nodes_executed": list(output.k_node_outputs.keys()),
            "final_message_length": len(output.final_message),
            "hop_based_complete": True,
            "error_message": output.error_message
        }
