"""Outreach Orchestrator - L3 orchestration for outreach workflows.

Implements clean L1 → L2 → L5 → L4 orchestration flow with deterministic
behavior and proper safety gating. Zero interference with resume orchestration.
"""

from __future__ import annotations

import logging
import asyncio
import concurrent.futures
import re
import time
from typing import Dict, List, Optional, Any
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
from l5.safety_validator import SafetyValidator
from runtime.telemetry_bus import get_telemetry_bus
from runtime.execution_budget_manager import get_budget_manager, create_budget_limits_from_config


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
        safety_validator: SafetyValidator,
        budget_manager: Optional[Any] = None,  # ExecutionBudgetManager
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
        
        # Initialize telemetry bus
        self.telemetry_bus = get_telemetry_bus()
        
        # Initialize budget manager with dependency injection fallback
        self.budget_manager = budget_manager or get_budget_manager()
        
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
        
        # Configure budget manager from config
        budget_limits = create_budget_limits_from_config(config)
        self.budget_manager.configure(budget_limits)
        
        # Check budget before starting workflow
        if not self.budget_manager.check_budget("outreach"):
            return OutreachPipelineResult(
                success=False,
                message=f"Budget exceeded: {self.budget_manager.get_budget_exceeded_reason()}",
                metadata={
                    "error": "budget_exceeded",
                    "workflow_type": "outreach"
                }
            )
        
        # Check context size limits
        recipient_size = len(str(recipient.__dict__))
        if not self.budget_manager.check_context_size(recipient_size):
            return OutreachPipelineResult(
                success=False,
                message=f"Context size {recipient_size} exceeds limit {budget_limits.max_context_size}",
                metadata={
                    "error": "context_size_exceeded",
                    "context_size": recipient_size,
                    "max_context_size": budget_limits.max_context_size,
                    "workflow_type": "outreach"
                }
            )
        
        # Configure telemetry from config
        telemetry_enabled = config.get("telemetry_enabled", True)
        telemetry_detail_level = config.get("telemetry_detail_level", "standard")
        self.telemetry_bus.configure(enabled=telemetry_enabled, detail_level=telemetry_detail_level)
        
        # Record workflow start and budget tracking
        workflow_start_time = time.time()
        self.budget_manager.start_stage("outreach")
        self.budget_manager.record_request()
        try:
            self.telemetry_bus.record_event("phase_start", "L3", {
                "workflow_type": "outreach",
                "stage": "orchestration",
                "mission_id": getattr(mission, 'id', 'unknown'),
                "recipient": recipient.name
            })
        except Exception:
            # Telemetry failures should never break workflow
            pass
        
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
        
        # Track recursion depth for budget management
        max_attempts = config.get("max_fallback_attempts", len(fallback_sequence))
        
        for attempt, archetype in enumerate(fallback_sequence[:max_attempts], 1):
            logger.info(f"Meta-loop attempt {attempt}/{max_attempts}: {archetype}")
            
            # Check recursion depth budget
            if not self.budget_manager.increment_depth("outreach"):
                logger.warning("Recursion depth budget exceeded")
                return OutreachPipelineResult(
                    success=False,
                    message=f"Recursion depth exceeded: {self.budget_manager.get_budget_exceeded_reason()}",
                    metadata={
                        "error": "depth_exceeded",
                        "attempts_made": attempt - 1,
                        "workflow_type": "outreach"
                    }
                )
            
            try:
                # Update archetype context
                ctx.archetype = archetype
                
                # Execute workflow phases
                result = self._execute_workflow_phases(mission, recipient, ctx, config)
                
                if result.success:
                    logger.info(f"Outreach successful with archetype {archetype}")
                    
                    # Record workflow success
                    try:
                        self.telemetry_bus.record_event("phase_end", "L3", {
                            "workflow_type": "outreach",
                            "stage": "orchestration",
                            "mission_id": getattr(mission, 'id', 'unknown'),
                            "archetype": archetype,
                            "success": True,
                            "duration": time.time() - workflow_start_time
                        })
                    except Exception:
                        pass
                    
                    return result
                    
                # Safety failure - try next archetype
                logger.warning(f"Safety failure with archetype {archetype}, trying fallback")
                
            except Exception as e:
                logger.error(f"Unexpected error in meta-loop attempt {attempt}: {e}")
                
                # Record error telemetry
                try:
                    self.telemetry_bus.record_error("workflow_failure", "L3", e, {
                        "workflow_type": "outreach",
                        "stage": "orchestration",
                        "mission_id": getattr(mission, 'id', 'unknown'),
                        "archetype": archetype,
                        "attempt": attempt
                    })
                except Exception:
                    pass
            finally:
                # Always decrement depth after each attempt
                self.budget_manager.decrement_depth("outreach")
        
        # All attempts failed
        try:
            self.telemetry_bus.record_error("workflow_failure", "L3", Exception("All archetype attempts failed"), {
                "workflow_type": "outreach",
                "stage": "orchestration",
                "mission_id": getattr(mission, 'id', 'unknown'),
                "attempts": len(fallback_sequence)
            })
        except Exception:
            pass
        
        return OutreachPipelineResult(
            success=False,
            message="",
            metadata={
                "error": "All archetype attempts failed",
                "attempts": len(fallback_sequence),
                "workflow_type": "outreach"
            }
        )
    
    async def orchestrate_outreach_concurrent(
        self,
        mission: OutreachMission,
        recipient: RecipientProfile,
        config: Optional[Dict[str, Any]] = None,
    ) -> OutreachPipelineResult:
        """Execute outreach workflow with optional concurrent execution.
        
        Args:
            mission: Outreach mission details
            recipient: Target recipient profile
            config: Optional configuration overrides
            
        Returns:
            OutreachPipelineResult with generated message and metadata
        """
        config = config or {}
        
        # Configure budget manager from config
        budget_limits = create_budget_limits_from_config(config)
        self.budget_manager.configure(budget_limits)
        
        # Check budget before starting workflow
        if not self.budget_manager.check_budget("outreach_concurrent"):
            return OutreachPipelineResult(
                success=False,
                message=f"Budget exceeded: {self.budget_manager.get_budget_exceeded_reason()}",
                metadata={
                    "error": "budget_exceeded",
                    "workflow_type": "outreach_concurrent"
                }
            )
        
        # Check context size limits
        recipient_size = len(str(recipient.__dict__))
        if not self.budget_manager.check_context_size(recipient_size):
            return OutreachPipelineResult(
                success=False,
                message=f"Context size {recipient_size} exceeds limit {budget_limits.max_context_size}",
                metadata={
                    "error": "context_size_exceeded",
                    "context_size": recipient_size,
                    "max_context_size": budget_limits.max_context_size,
                    "workflow_type": "outreach_concurrent"
                }
            )
        
        # Configure telemetry from config
        telemetry_enabled = config.get("telemetry_enabled", True)
        telemetry_detail_level = config.get("telemetry_detail_level", "standard")
        self.telemetry_bus.configure(enabled=telemetry_enabled, detail_level=telemetry_detail_level)
        
        # Record workflow start and budget tracking
        workflow_start_time = time.time()
        self.budget_manager.start_stage("outreach_concurrent")
        self.budget_manager.record_request()
        try:
            self.telemetry_bus.record_event("phase_start", "L3", {
                "workflow_type": "outreach_concurrent",
                "stage": "orchestration",
                "mission_id": getattr(mission, 'id', 'unknown')
            })
        except Exception:
            pass
        
        # Apply default concurrency settings (all False for backward compatibility)
        use_concurrent_research = config.get("use_concurrent_research", False)
        use_multi_draft = config.get("use_multi_draft", False)
        
        # P1 — Archetype Planning (same as sequential)
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
                
                # Execute workflow phases with optional concurrency
                if use_concurrent_research or use_multi_draft:
                    # Use async execution
                    try:
                        # Check if event loop is already running
                        loop = asyncio.get_running_loop()
                        # If loop is running, we need to run in thread
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            future = executor.submit(
                                asyncio.run, 
                                self._execute_workflow_phases_concurrent_async(mission, recipient, ctx, config)
                            )
                            result = future.result()
                    except RuntimeError:
                        # No event loop running, safe to use asyncio.run
                        result = asyncio.run(self._execute_workflow_phases_concurrent_async(mission, recipient, ctx, config))
                else:
                    # Use sequential execution (identical to original)
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
                            "workflow_type": "outreach_concurrent"
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
                "workflow_type": "outreach_concurrent"
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
        research_start_time = time.time()
        try:
            self.telemetry_bus.record_event("phase_start", "L3", {
                "workflow_type": "outreach",
                "stage": "research",
                "archetype": ctx.archetype,
                "mission_id": getattr(mission, 'id', 'unknown')
            })
        except Exception:
            pass
        
        research_plan = self.research_planner.plan_research(ctx, mission, recipient)
        
        # Research Execution
        logger.info("P2: Executing research")
        company_info = self.company_executor.search_company_context(
            mission_id=getattr(mission, 'id', 'unknown'),
            target_company=recipient.company,
            archetype=ctx.archetype,
            rag_params=ctx.rag_params.__dict__ if hasattr(ctx, 'rag_params') else {},
            signal_params=ctx.signal_params.__dict__ if hasattr(ctx, 'signal_params') else {}
        )
        contact_info = self.contact_executor.search_contact_profile(
            mission_id=getattr(mission, 'id', 'unknown'),
            target_role=recipient.title,
            target_company=recipient.company,
            archetype=ctx.archetype,
            rag_params=ctx.rag_params.__dict__ if hasattr(ctx, 'rag_params') else {},
            signal_params=ctx.signal_params.__dict__ if hasattr(ctx, 'signal_params') else {}
        )
        
        # Record research completion
        try:
            self.telemetry_bus.record_event("phase_end", "L3", {
                "workflow_type": "outreach",
                "stage": "research",
                "archetype": ctx.archetype,
                "mission_id": getattr(mission, 'id', 'unknown'),
                "success": True,
                "duration": time.time() - research_start_time
            })
        except Exception:
            pass
        
        # Aggregate as ResearchBundle
        research_bundle = ResearchBundle(
            company=company_info.__dict__ if hasattr(company_info, '__dict__') else company_info,
            contact=contact_info.__dict__ if hasattr(contact_info, '__dict__') else contact_info
        )
        
        # P3 — Message Planning & Generation
        logger.info("P3: Planning and generating message")
        message_start_time = time.time()
        try:
            self.telemetry_bus.record_event("phase_start", "L3", {
                "workflow_type": "outreach",
                "stage": "message",
                "archetype": ctx.archetype,
                "mission_id": getattr(mission, 'id', 'unknown')
            })
        except Exception:
            pass
        
        mp = self.message_planner.create_message_plan(ctx, research_bundle.__dict__)
        
        message_result = self.message_executor.generate_message(
            message_plan=mp.__dict__,
            archetype_context=ctx.__dict__
        )
        
        # Validate message length against budget limits
        message_content = getattr(message_result, 'message', getattr(message_result, 'content', ''))
        if not self.budget_manager.check_message_length(len(message_content)):
            return OutreachPipelineResult(
                success=False,
                message=f"Generated message length {len(message_content)} exceeds budget limit",
                metadata={
                    "error": "message_length_exceeded",
                    "message_length": len(message_content),
                    "max_message_length": self.budget_manager.get_limits()['max_message_length'],
                    "workflow_type": "outreach"
                }
            )
        
        # Record message completion
        try:
            self.telemetry_bus.record_event("phase_end", "L3", {
                "workflow_type": "outreach",
                "stage": "message",
                "archetype": ctx.archetype,
                "mission_id": getattr(mission, 'id', 'unknown'),
                "success": True,
                "duration": time.time() - message_start_time
            })
        except Exception:
            pass
        
        # P4 — Final Safety Check (MUST be after message generation)
        logger.info("P4: Safety validation")
        safety_start_time = time.time()
        try:
            self.telemetry_bus.record_event("phase_start", "L3", {
                "workflow_type": "outreach",
                "stage": "safety",
                "archetype": ctx.archetype,
                "mission_id": getattr(mission, 'id', 'unknown')
            })
        except Exception:
            pass
        
        safety_result = self.safety_validator.evaluate(message_result.message)
        
        # Record safety completion
        try:
            self.telemetry_bus.record_event("phase_end", "L3", {
                "workflow_type": "outreach",
                "stage": "safety",
                "archetype": ctx.archetype,
                "mission_id": getattr(mission, 'id', 'unknown'),
                "success": safety_result.passed,
                "duration": time.time() - safety_start_time
            })
        except Exception:
            pass
        
        if not safety_result.passed:
            # Record safety failure
            try:
                self.telemetry_bus.record_error("safety_failure", "L5", Exception("Safety validation failed"), {
                    "workflow_type": "outreach",
                    "stage": "safety",
                    "archetype": ctx.archetype,
                    "mission_id": getattr(mission, 'id', 'unknown'),
                    "findings": safety_result.findings
                })
            except Exception:
                pass
            
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
    
    async def _execute_workflow_phases_concurrent_async(
        self,
        mission: OutreachMission,
        recipient: RecipientProfile,
        ctx: ArchetypeContext,
        config: Dict[str, Any],
    ) -> OutreachPipelineResult:
        """Execute workflow phases with optional concurrency (async version)."""
        
        # P2 — Research Planning (same as sequential)
        logger.info("P2: Planning research")
        research_plan = self.research_planner.plan_research(ctx, mission, recipient)
        
        # Research Execution with optional concurrency
        use_concurrent_research = config.get("use_concurrent_research", False)
        if use_concurrent_research:
            logger.info("P2: Executing research concurrently")
            research_bundle = await self._execute_research_concurrent(mission, recipient, ctx)
        else:
            logger.info("P2: Executing research sequentially")
            company_info = self.company_executor.search_company_context(
                mission_id=getattr(mission, 'id', 'unknown'),
                target_company=recipient.company,
                archetype=ctx.archetype,
                rag_params=ctx.rag_params.__dict__ if hasattr(ctx, 'rag_params') else {},
                signal_params=ctx.signal_params.__dict__ if hasattr(ctx, 'signal_params') else {}
            )
            contact_info = self.contact_executor.search_contact_profile(
                mission_id=getattr(mission, 'id', 'unknown'),
                target_role=recipient.title,
                target_company=recipient.company,
                archetype=ctx.archetype,
                rag_params=ctx.rag_params.__dict__ if hasattr(ctx, 'rag_params') else {},
                signal_params=ctx.signal_params.__dict__ if hasattr(ctx, 'signal_params') else {}
            )
            
            research_bundle = ResearchBundle(
                company=company_info.__dict__ if hasattr(company_info, '__dict__') else company_info,
                contact=contact_info.__dict__ if hasattr(contact_info, '__dict__') else contact_info
            )
        
        # P3 — Message Planning & Generation with optional multi-draft
        use_multi_draft = config.get("use_multi_draft", False)
        logger.info("P3: Planning and generating message")
        mp = self.message_planner.create_message_plan(ctx, research_bundle.__dict__)
        
        if use_multi_draft:
            message_result = await self._generate_multiple_drafts_and_select_best(mp, ctx, config)
        else:
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
                    "workflow_type": "outreach_concurrent"
                }
            )
        
        # P6 — State Persistence (same as sequential)
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
        
        # Record workflow success
        try:
            self.telemetry_bus.record_event("phase_end", "L3", {
                "workflow_type": "outreach_concurrent",
                "stage": "orchestration",
                "mission_id": getattr(mission, 'id', 'unknown'),
                "success": True,
                "duration": time.time() - workflow_start_time
            })
        except Exception:
            pass
        
        # Return successful result
        return OutreachPipelineResult(
            success=True,
            message=message_result.message,
            metadata={
                "archetype": ctx.archetype,
                "research_bundle": research_bundle.__dict__,
                "message_plan": mp.__dict__,
                "safety_result": safety_result.__dict__,
                "workflow_type": "outreach_concurrent"
            }
        )
    
    async def _execute_research_concurrent(
        self,
        mission: OutreachMission,
        recipient: RecipientProfile,
        ctx: ArchetypeContext,
    ) -> ResearchBundle:
        """Execute company and contact research concurrently."""
        
        # Acquire concurrent execution slot
        timeout = self.budget_manager.get_limits()['executor_timeout']
        if not self.budget_manager.acquire_concurrent_slot(timeout=timeout):
            raise Exception(f"Could not acquire concurrent execution slot within {timeout}s")
        
        try:
            # Create tasks for concurrent execution
            company_task = asyncio.create_task(
                asyncio.to_thread(
                    self.company_executor.search_company_context,
                    getattr(mission, 'id', 'unknown'),
                    recipient.company,
                    ctx.archetype,
                    ctx.rag_params.__dict__ if hasattr(ctx, 'rag_params') else {},
                    ctx.signal_params.__dict__ if hasattr(ctx, 'signal_params') else {}
                )
            )
            
            contact_task = asyncio.create_task(
                asyncio.to_thread(
                    self.contact_executor.search_contact_profile,
                    getattr(mission, 'id', 'unknown'),
                    recipient.title,
                    recipient.company,
                    ctx.archetype,
                    ctx.rag_params.__dict__ if hasattr(ctx, 'rag_params') else {},
                    ctx.signal_params.__dict__ if hasattr(ctx, 'signal_params') else {}
                )
            )
            
            # Wait for both tasks to complete, handling partial failures
            company_result, contact_result = await asyncio.gather(
                company_task, 
                contact_task, 
                return_exceptions=True
            )
            
            # Process results, handling failures gracefully
            company_data = {}
            contact_data = {}
            
            if not isinstance(company_result, Exception):
                company_data = company_result.__dict__ if hasattr(company_result, '__dict__') else company_result
            else:
                logger.warning(f"Company research failed: {company_result}")
            
            if not isinstance(contact_result, Exception):
                contact_data = contact_result.__dict__ if hasattr(contact_result, '__dict__') else contact_result
            else:
                logger.warning(f"Contact research failed: {contact_result}")
            
            return ResearchBundle(company=company_data, contact=contact_data)
            
        except Exception as e:
            logger.error(f"Concurrent research execution failed: {e}")
            # Return empty research bundle on failure
            return ResearchBundle(company={}, contact={})
        finally:
            # Always release the concurrent execution slot
            self.budget_manager.release_concurrent_slot()
    
    async def _generate_multiple_drafts_and_select_best(
        self,
        message_plan: Any,
        ctx: ArchetypeContext,
        config: Dict[str, Any],
    ) -> Any:
        """Generate multiple message drafts and select the best one."""
        
        max_parallel_drafts = config.get("max_parallel_drafts", 2)
        temperatures = [0.3, 0.7, 1.0][:max_parallel_drafts]
        
        # Generate drafts concurrently
        draft_tasks = []
        for temp in temperatures:
            # Create modified message plan with temperature
            temp_plan = message_plan.__dict__.copy()
            temp_plan["temperature"] = temp
            
            task = asyncio.create_task(
                asyncio.to_thread(
                    self.message_executor.generate_message,
                    message_plan=temp_plan,
                    archetype_context=ctx.__dict__
                )
            )
            draft_tasks.append(task)
        
        # Wait for all drafts to complete
        drafts = await asyncio.gather(*draft_tasks, return_exceptions=True)
        
        # Filter out failed drafts
        valid_drafts = [d for d in drafts if not isinstance(d, Exception)]
        
        if not valid_drafts:
            raise Exception("All message draft generation attempts failed")
        
        # Select best draft using voting
        return self._vote_best_draft(valid_drafts, ctx)
    
    def _vote_best_draft(self, drafts: List[Any], ctx: ArchetypeContext) -> Any:
        """Select the best draft using voting heuristic."""
        
        # First, filter drafts by safety
        safe_drafts = []
        for draft in drafts:
            safety_result = self.safety_validator.evaluate(draft.message)
            if safety_result.passed:
                safe_drafts.append((draft, safety_result))
        
        # If no safe drafts, raise exception
        if not safe_drafts:
            raise Exception("No message drafts passed safety validation")
        
        # Score safe drafts based on length and signal density
        scored_drafts = []
        for draft, safety_result in safe_drafts:
            length_score = len(draft.message)
            signal_density_score = self._calculate_signal_density(draft.message)
            combined_score = length_score * signal_density_score
            scored_drafts.append((draft, combined_score))
        
        # Sort by combined score (higher is better)
        scored_drafts.sort(key=lambda x: x[1], reverse=True)
        
        # Return the highest scoring draft
        return scored_drafts[0][0]
    
    def _calculate_signal_density(self, message: str) -> float:
        """Calculate signal density of a message."""
        
        if not message:
            return 0.0
        
        # Count numeric mentions
        numeric_count = len(re.findall(r'\b\d+(?:\.\d+)?\b', message))
        
        # Count business/technical keywords
        signal_keywords = [
            'revenue', 'growth', 'team', 'product', 'technology', 'platform',
            'scale', 'performance', 'efficiency', 'innovation', 'strategy',
            'market', 'customer', 'user', 'data', 'analytics', 'ai', 'ml',
            'engineering', 'development', 'architecture', 'system', 'solution'
        ]
        
        keyword_count = sum(1 for keyword in signal_keywords if keyword.lower() in message.lower())
        
        # Calculate density (signals per word)
        words = len(message.split())
        if words == 0:
            return 0.0
        
        total_signals = numeric_count + keyword_count
        return total_signals / words
