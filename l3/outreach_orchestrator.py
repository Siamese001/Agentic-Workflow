"""Outreach Orchestrator - L3 orchestration for outreach workflows.

Implements clean L1 → L2 → L5 → L4 orchestration flow with deterministic
behavior and proper safety gating. Zero interference with resume orchestration.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional
from dataclasses import dataclass, field

from l1.outreach_archetype_planning import OutreachArchetypePlanner
from l1.research_planning import ResearchRefinementPlanner
from l1.message_planning import MessagePlanner
from l1.outreach_dataclasses import (
    OutreachMission,
    ArchetypeContext,
    ArchetypeType,
)
from l1.outreach_archetype_planning import RecipientProfile
from l2.company_research_executor import CompanyResearchExecutor
from l2.contact_research_executor import ContactResearchExecutor
from l2.message_generation_executor import MessageGenerationExecutor
from l5.safety_validator import L5SafetyValidator


logger = logging.getLogger(__name__)


@dataclass
class OutreachWorkflowState:
    """Workflow state for outreach orchestration persistence."""
    mission_id: str
    recipient_id: str
    archetype: str
    research_bundle: Dict[str, Any]
    message_plan: Dict[str, Any]
    message: str
    safety_result: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OutreachPipelineResult:
    """Result of outreach pipeline execution."""
    success: bool
    message: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResearchBundle:
    """Aggregated research results from company and contact executors."""
    company: Dict[str, Any] = field(default_factory=dict)
    contact: Dict[str, Any] = field(default_factory=dict)
    
    def __bool__(self) -> bool:
        return bool(self.company or self.contact)


class OutreachOrchestrator:
    """L3 Outreach Orchestrator implementing clean phase sequence.
    
    Executes outreach workflow with deterministic L1 → L2 → L5 → L4 flow,
    proper safety gating, and meta-loop fallback sequence.
    """
    
    def __init__(
        self,
        archetype_planner: OutreachArchetypePlanner,
        research_planner: ResearchRefinementPlanner,
        message_planner: MessagePlanner,
        company_executor: CompanyResearchExecutor,
        contact_executor: ContactResearchExecutor,
        message_executor: MessageGenerationExecutor,
        state_manager: Any,  # TODO: Define state manager interface
        safety_validator: L5SafetyValidator,
    ):
        """Initialize OutreachOrchestrator with required components."""
        self.archetype_planner = archetype_planner
        self.research_planner = research_planner
        self.message_planner = message_planner
        self.company_executor = company_executor
        self.contact_executor = contact_executor
        self.message_executor = message_executor
        self.state_manager = state_manager
        self.safety_validator = safety_validator
        
        logger.info("Initialized OutreachOrchestrator")
    
    def orchestrate_outreach(
        self,
        mission: OutreachMission,
        recipient: RecipientProfile,
        config: Optional[Dict[str, Any]] = None,
    ) -> OutreachPipelineResult:
        """Execute complete outreach workflow with meta-loop fallback.
        
        Args:
            mission: Outreach mission details
            recipient: Target recipient profile
            config: Optional configuration overrides
            
        Returns:
            LICPipelineResult with generated message and metadata
        """
        config = config or {}
        
        # P1 — Archetype Planning
        logger.info(f"P1: Building archetype context for {recipient.name}")
        ctx = self.archetype_planner.plan_archetype_influence(mission)
        
        # Meta-loop fallback sequence: C_LEVEL → EXECUTIVE → SENIOR_TA → RECRUITER
        fallback_sequence = [
            ArchetypeType.C_LEVEL,
            ArchetypeType.EXECUTIVE,
            ArchetypeType.SENIOR_TA,
            ArchetypeType.RECRUITER,
        ]
        
        for attempt, archetype in enumerate(fallback_sequence, 1):
            logger.info(f"Meta-loop attempt {attempt}/{len(fallback_sequence)}: {archetype}")
            
            try:
                # Update archetype context
                ctx.archetype = archetype
                
                # Execute workflow phases
                result = self._execute_workflow_phases(mission, recipient, ctx, config)
                
                if result.success:
                    logger.info(f"Outreach successful with archetype {archetype}")
                    return result
                    
                # Safety failure - try next archetype
                logger.warning(f"Safety failure with archetype {archetype}, trying fallback")
                continue
                
            except Exception as e:
                logger.error(f"Error with archetype {archetype}: {e}")
                if attempt >= len(fallback_sequence):
                    # Final attempt failed - return error result
                    return OutreachPipelineResult(
                        success=False,
                        message="",
                        metadata={
                            "error": str(e),
                            "attempts": attempt,
                            "final_archetype": archetype,
                            "workflow_type": "outreach"
                        }
                    )
                continue
        
        # All attempts failed
        return OutreachPipelineResult(
            success=False,
            message="",
            metadata={
                "error": "All archetype attempts failed",
                "attempts": len(fallback_sequence),
                "workflow_type": "outreach"
            }
        )
    
    def _execute_workflow_phases(
        self,
        mission: OutreachMission,
        recipient: RecipientProfile,
        ctx: ArchetypeContext,
        config: Dict[str, Any],
    ) -> OutreachPipelineResult:
        """Execute the core workflow phases P2-P6."""
        
        # P2 — Research Planning
        logger.info("P2: Planning research")
        research_plan = self.research_planner.plan_research(ctx, mission, recipient)
        
        # Research Execution
        logger.info("P2: Executing research")
        company_info = self.company_executor.search_company_context(
            query=recipient.company,
            archetype=ctx.archetype
        )
        contact_info = self.contact_executor.search_contact_profile(
            query=recipient.name,
            archetype=ctx.archetype
        )
        
        # Aggregate as ResearchBundle
        research_bundle = ResearchBundle(
            company=company_info.__dict__ if hasattr(company_info, '__dict__') else company_info,
            contact=contact_info.__dict__ if hasattr(contact_info, '__dict__') else contact_info
        )
        
        # P3 — Message Planning & Generation
        logger.info("P3: Planning and generating message")
        mp = self.message_planner.create_message_plan(ctx, research_bundle.__dict__)
        
        message_result = self.message_executor.generate_message(
            message_plan=mp.__dict__,
            archetype_context=ctx.__dict__
        )
        
        # P4 — Final Safety Check (MUST be after message generation)
        logger.info("P4: Safety validation")
        safety_result = self.safety_validator.evaluate(message_result.message)
        
        if not safety_result.passed:
            return OutreachPipelineResult(
                success=False,
                message="",
                metadata={
                    "safety_failure": True,
                    "safety_findings": safety_result.findings,
                    "archetype": ctx.archetype,
                    "workflow_type": "outreach"
                }
            )
        
        # P6 — State Persistence
        logger.info("P6: Persisting workflow state")
        workflow_state = OutreachWorkflowState(
            mission_id=getattr(mission, 'id', 'unknown'),
            recipient_id=getattr(recipient, 'id', 'unknown'),
            archetype=ctx.archetype,
            research_bundle=research_bundle.__dict__,
            message_plan=mp.__dict__,
            message=message_result.message,
            safety_result=safety_result.__dict__,
            metadata=config
        )
        
        if hasattr(self.state_manager, 'save_state'):
            self.state_manager.save_state(workflow_state)
        
        # Return successful result
        return OutreachPipelineResult(
            success=True,
            message=message_result.message,
            metadata={
                "archetype": ctx.archetype,
                "research_bundle": research_bundle.__dict__,
                "message_plan": mp.__dict__,
                "safety_result": safety_result.__dict__,
                "workflow_type": "outreach"
            }
        )
