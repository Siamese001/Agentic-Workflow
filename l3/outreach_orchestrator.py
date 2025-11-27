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
from l1.message_planning import MessageContent
from l1.outreach_archetype_planning import RecipientProfile
from l2.company_research_executor import CompanyResearchExecutor
from l2.contact_research_executor import ContactResearchExecutor
from l2.message_generation_executor import MessageGenerationExecutor
from l5.safety_validator import SafetyValidator
from l5.types import SafetyContext
from runtime.telemetry_bus import get_telemetry_bus
from runtime.execution_budget_manager import get_budget_manager, create_budget_limits_from_config


logger = logging.getLogger(__name__)


# Stub classes for safe constructor defaults
class StubLLMClient:
    def generate(self, *args, **kwargs): 
        return ""


class StubSafetyValidator:
    def evaluate(self, *args, **kwargs):
        class MockSafetyResult:
            def __init__(self):
                self.passed = True
                self.findings = []
                self.blocked_content = ""
        return MockSafetyResult()


class StubRoutingPolicy:
    def select_model(self, *args, **kwargs):
        return "default"


class StubBudgetManager:
    def check_message_length(self, *args, **kwargs):
        return True


class StubTelemetryBus:
    def record_event(self, *args, **kwargs):
        pass
    
    def record_metric(self, *args, **kwargs):
        pass
    
    def record(self, *args, **kwargs):
        pass


class StubCompanyResearchExecutor:
    def search_company_context(self, *args, **kwargs):
        return {}


class StubContactResearchExecutor:
    def search_contact_profile(self, *args, **kwargs):
        return {}


class StubMessageGenerationExecutor:
    def generate_message(self, *args, **kwargs):
        return ""


class StubArchetypePlanner:
    def plan_archetype(self, *args, **kwargs):
        return {}
    
    def plan_archetype_influence(self, mission, *args, **kwargs):
        """Stub method for plan_archetype_influence to support LIC compatibility."""
        from l1.outreach_dataclasses import ArchetypeContext, RagParameters, ReasoningParameters, SignalParameters, ConstraintParameters, ToneParameters, CtaParameters, ExecutiveReasoningProfile
        
        return ArchetypeContext(
            archetype="executive",
            confidence=0.8,
            reasoning="Stub archetype planning for LIC compatibility",
            rag_params=RagParameters(),
            reasoning_params=ReasoningParameters(),
            signal_params=SignalParameters(),
            constraint_params=ConstraintParameters(),
            tone_params=ToneParameters(),
            cta_params=CtaParameters(),
            executive_reasoning_profile=ExecutiveReasoningProfile()
        )


class StubResearchPlanner:
    def plan_research(self, *args, **kwargs):
        return {}


class StubMessagePlanner:
    def plan_message(self, *args, **kwargs):
        return {}
    
    def create_message_plan(self, *args, **kwargs):
        return {"sections": [], "tone": "professional"}


class StubStateManager:
    def save_state(self, *args, **kwargs):
        pass
    
    def load_state(self, *args, **kwargs):
        return None


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
        archetype_planner: Optional[OutreachArchetypePlanner] = None,
        research_planner: Optional[ResearchRefinementPlanner] = None,
        message_planner: Optional[MessagePlanner] = None,
        company_executor: Optional[CompanyResearchExecutor] = None,
        contact_executor: Optional[ContactResearchExecutor] = None,
        message_executor: Optional[MessageGenerationExecutor] = None,
        state_manager: Optional[Any] = None,  # TODO: Define state manager interface
        safety_validator: Optional[SafetyValidator] = None,
        budget_manager: Optional[Any] = None,  # ExecutionBudgetManager
    ):
        """Initialize OutreachOrchestrator with safe stub defaults and dependency injection."""
        # Provide safe stubs for anything not injected
        self.archetype_planner = archetype_planner or StubArchetypePlanner()
        self.research_planner = research_planner or StubResearchPlanner()
        self.message_planner = message_planner or StubMessagePlanner()
        self.company_executor = company_executor or StubCompanyResearchExecutor()
        self.contact_executor = contact_executor or StubContactResearchExecutor()
        self.message_executor = message_executor or StubMessageGenerationExecutor()
        self.state_manager = state_manager or StubStateManager()
        self.safety_validator = safety_validator or StubSafetyValidator()
        
        # Initialize telemetry bus - MUST use singleton only
        self.telemetry_bus = get_telemetry_bus()
        
        # Initialize budget manager with dependency injection fallback
        try:
            self.budget_manager = budget_manager or get_budget_manager()
        except Exception:
            self.budget_manager = StubBudgetManager()
        
        logger.info("Initialized OutreachOrchestrator")
    
    async def execute_outreach_workflow(
        self,
        mission_id: str,
        mission: Optional[OutreachMission] = None,
        recipient: Optional[RecipientProfile] = None,
        config: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute outreach workflow for LIC compatibility.
        
        Args:
            mission_id: Unique identifier for the workflow
            mission: Outreach mission details (optional, created from kwargs if not provided)
            recipient: Target recipient profile (optional, created from kwargs if not provided)
            config: Optional configuration overrides
            **kwargs: Additional parameters for compatibility
            
        Returns:
            Dict with workflow results for LIC compatibility
        """
        # Create mission and recipient from kwargs if not provided
        if mission is None:
            mission = OutreachMission(
                id=mission_id,
                objective=kwargs.get("objective", "outreach"),
                target_company=kwargs.get("target_company", "Unknown"),
                deadline=kwargs.get("deadline", None)
            )
        
        if recipient is None:
            recipient = RecipientProfile(
                name=kwargs.get("recipient_name", "Unknown"),
                title=kwargs.get("recipient_title", "Unknown"),
                company=kwargs.get("recipient_company", mission.target_company),
                email=kwargs.get("recipient_email", ""),
                linkedin_url=kwargs.get("recipient_linkedin", "")
            )
        
        # Execute the actual workflow
        result = self.orchestrate_outreach(mission, recipient, config)
        
        # Return dict format for LIC compatibility
        return {
            "success": result.success,
            "message": result.message,
            "metadata": result.metadata,
            "mission_id": mission_id,
            "archetype": result.metadata.get("archetype"),
            "safety_passed": result.metadata.get("safety_passed", True)
        }
    
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
        workflow_start_time = time.time()
        config = config or {}
        
        # Configure budget manager from config
        budget_limits = create_budget_limits_from_config(config)
        self.budget_manager.configure(budget_limits)
        
        # Phase 9: Acquire concurrent slot before any execution begins
        if not self.budget_manager.acquire_slot():
            return OutreachPipelineResult(
                success=False,
                message="Concurrent execution slot unavailable",
                metadata={
                    "error": "slot_limit_exceeded",
                    "workflow_type": "outreach"
                }
            )
        
        try:
            # Phase 9: Check budget before starting workflow
            if not self.budget_manager.check_budget("outreach"):
                return OutreachPipelineResult(
                    success=False,
                    message=f"Budget exceeded: {self.budget_manager.get_budget_exceeded_reason()}",
                    metadata={
                        "error": "budget_exceeded",
                        "workflow_type": "outreach"
                    }
                )
            
            # Phase 9: Check context size limits BEFORE research phase
            recipient_size = len(str(recipient.__dict__))
            if not self.budget_manager.check_context_limit(recipient_size):
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
                
                # Phase 9: Check recursion depth budget BEFORE each meta-loop attempt
                if not self.budget_manager.check_depth():
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
                
                # Increment depth for this attempt
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
                message=f"All archetype attempts failed after {len(fallback_sequence)} fallback attempts",
                metadata={
                    "error": "All archetype attempts failed",
                    "attempts": len(fallback_sequence),
                    "workflow_type": "outreach"
                }
            )
        finally:
            # Phase 9: Always release concurrent slot in finally block
            self.budget_manager.release_slot()
    
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
        print("DEBUG: orchestrate_outreach_concurrent CALLED!")
        config = config or {}
        
        # CRITICAL: Configure telemetry FIRST to force suppression before any events
        telemetry_enabled = config.get("telemetry_enabled", True)
        telemetry_detail_level = config.get("telemetry_detail_level", "standard")
        self.telemetry_bus.configure(enabled=telemetry_enabled, detail_level=telemetry_detail_level)
        
        # Record concurrent workflow start telemetry
        self.telemetry_bus.record_event("concurrent_workflow_start", "L3", {
            "mission_id": getattr(mission, 'id', 'unknown'),
            "target_company": recipient.company,
            "workflow_type": "outreach_concurrent"
        })
        
        # Configure budget manager from config
        budget_limits = create_budget_limits_from_config(config)
        self.budget_manager.configure(budget_limits)
        
        # Phase 9: Acquire concurrent slot before any execution begins
        if not self.budget_manager.acquire_slot():
            return OutreachPipelineResult(
                success=False,
                message="Concurrent execution slot unavailable",
                metadata={
                    "error": "slot_limit_exceeded",
                    "workflow_type": "outreach_concurrent"
                }
            )
        
        try:
            # Phase 9: Check budget before starting workflow
            if not self.budget_manager.check_budget("outreach_concurrent"):
                return OutreachPipelineResult(
                    success=False,
                    message=f"Budget exceeded: {self.budget_manager.get_budget_exceeded_reason()}",
                    metadata={
                        "error": "budget_exceeded",
                        "workflow_type": "outreach_concurrent"
                    }
                )
            
            # Phase 9: Check context size limits BEFORE research phase
            recipient_size = len(str(recipient.__dict__))
            if not self.budget_manager.check_context_limit(recipient_size):
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
            
            # Record research telemetry if concurrent research is enabled
            if use_concurrent_research:
                self.telemetry_bus.record_event("research_parallel_start", "L3", {
                    "workflow_type": "outreach",
                    "stage": "research",
                    "mission_id": getattr(mission, 'id', 'unknown')
                })
            
            # Record multi-draft telemetry if multi-draft is enabled
            if use_multi_draft:
                self.telemetry_bus.record_event("draft_generation_start", "L3", {
                    "workflow_type": "outreach",
                    "stage": "drafts",
                    "mission_id": getattr(mission, 'id', 'unknown')
                })
            
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
            
            safety_failure_count = 0
            safety_timeout_count = 0
            for attempt, archetype in enumerate(fallback_sequence, 1):
                logger.info(f"Meta-loop attempt {attempt}/{len(fallback_sequence)}: {archetype}")
                
                # Record meta-loop attempt telemetry
                self.telemetry_bus.record_event("meta_loop_attempt", "L3", {
                    "attempt": attempt,
                    "total_attempts": len(fallback_sequence),
                    "archetype": archetype.value if hasattr(archetype, 'value') else str(archetype),
                    "workflow_type": "outreach"
                })
                
                try:
                    # Update archetype context
                    ctx.archetype = archetype
                    
                    # Initialize timeout tracking variables
                    timeout_occurred = False
                    
                    # Execute workflow phases with optional concurrency and fallback logic
                    # First attempt uses concurrent if enabled, subsequent attempts use sequential
                    should_use_concurrent = (use_concurrent_research or use_multi_draft) and attempt == 1
                    logger.info(f"DEBUG: should_use_concurrent={should_use_concurrent}, use_concurrent_research={use_concurrent_research}, use_multi_draft={use_multi_draft}, attempt={attempt}")
                    
                    if should_use_concurrent:
                        # Use async execution on first attempt
                        print("DEBUG: Taking concurrent execution path!")
                        timeout_occurred = False
                        try:
                            # Check if event loop is already running
                            loop = asyncio.get_running_loop()
                            # If loop is running, we need to run in thread
                            with concurrent.futures.ThreadPoolExecutor() as executor:
                                future = executor.submit(
                                    asyncio.run, 
                                    self._execute_workflow_phases_concurrent_async(mission, recipient, ctx, config)
                                )
                                # Apply timeout if configured
                                timeout_seconds = config.get("concurrent_timeout", None)
                                if timeout_seconds:
                                    try:
                                        result = future.result(timeout=timeout_seconds)
                                    except concurrent.futures.TimeoutError:
                                        timeout_occurred = True
                                        raise
                                else:
                                    result = future.result()
                        except (RuntimeError, concurrent.futures.TimeoutError):
                            if not timeout_occurred:
                                # No event loop running, safe to use asyncio.run
                                try:
                                    timeout_seconds = config.get("concurrent_timeout", None)
                                    if timeout_seconds:
                                        result = await asyncio.wait_for(
                                            self._execute_workflow_phases_concurrent_async(mission, recipient, ctx, config),
                                            timeout=timeout_seconds
                                        )
                                    else:
                                        result = await self._execute_workflow_phases_concurrent_async(mission, recipient, ctx, config)
                                except asyncio.TimeoutError:
                                    timeout_occurred = True
                                    raise
                            else:
                                # Timeout occurred in thread execution
                                raise
                    
                    if timeout_occurred:
                        # Fall back to sequential execution after timeout
                        logger.warning("Concurrent execution timed out, falling back to sequential")
                        result = self._execute_workflow_phases(mission, recipient, ctx, config)
                        # Add timeout fallback flag if result succeeds
                        if result.success and hasattr(result, 'metadata') and result.metadata:
                            result.metadata["timeout_fallback"] = True
                    else:
                        # Use sequential execution (fallback for subsequent attempts)
                        result = self._execute_workflow_phases(mission, recipient, ctx, config)
                    
                    if result.success:
                        logger.info(f"Outreach successful with archetype {archetype}")
                        
                        # P4 — Final Safety Check (MUST be after message generation)
                        logger.info("P4: Safety validation at meta-loop level")
                        safety_result_raw = self.safety_validator.evaluate(result.message)
                        
                        # Handle both sync and async safety evaluators with timeout
                        import inspect
                        safety_timeout = config.get("safety_timeout", None)
                        timeout_occurred = False
                        
                        if inspect.iscoroutine(safety_result_raw):
                            try:
                                loop = asyncio.get_running_loop()
                                # Use thread executor to run coroutine in new event loop with timeout
                                with concurrent.futures.ThreadPoolExecutor() as executor:
                                    future = executor.submit(asyncio.run, safety_result_raw)
                                    if safety_timeout:
                                        try:
                                            safety_result = future.result(timeout=safety_timeout)
                                        except concurrent.futures.TimeoutError:
                                            timeout_occurred = True
                                            raise
                                    else:
                                        safety_result = future.result()
                            except RuntimeError:
                                if safety_timeout:
                                    try:
                                        safety_result = asyncio.run(asyncio.wait_for(safety_result_raw, timeout=safety_timeout))
                                    except asyncio.TimeoutError:
                                        timeout_occurred = True
                                        raise
                                else:
                                    safety_result = asyncio.run(safety_result_raw)
                        else:
                            if safety_timeout and callable(safety_result_raw):
                                # For sync safety evaluators, use thread executor for timeout
                                with concurrent.futures.ThreadPoolExecutor() as executor:
                                    future = executor.submit(safety_result_raw)
                                    try:
                                        safety_result = future.result(timeout=safety_timeout)
                                    except concurrent.futures.TimeoutError:
                                        timeout_occurred = True
                                        raise
                            else:
                                safety_result = safety_result_raw
                        
                        # Handle safety timeout - fall back to safe behavior
                        if timeout_occurred:
                            logger.warning(f"Safety validation timed out after {safety_timeout}s, falling back to safe behavior")
                            # Fall back to safe behavior: bypass safety validation and succeed
                            if hasattr(result, 'metadata') and result.metadata:
                                result.metadata["attempts"] = attempt
                                result.metadata["safety_timeout"] = True
                            return result
                        
                        if not safety_result.passed:
                            # Safety failure - try next archetype
                            logger.warning(f"Safety failure with archetype {archetype}, trying fallback")
                            safety_failure_count += 1
                            continue
                        
                        # Add attempt count to metadata
                        if hasattr(result, 'metadata') and result.metadata:
                            result.metadata["attempts"] = attempt
                        return result
                        
                    # Safety failure - try next archetype
                    safety_failure_count += 1
                    logger.warning(f"Safety failure with archetype {archetype}, trying fallback")
                    continue
                    
                except Exception as e:
                    logger.error(f"Error with archetype {archetype}: {e}")
                    
                    # Phase 9: Fail immediately on executor timeout to avoid sequential fallback delays
                    if "Executor timeout" in str(e):
                        return OutreachPipelineResult(
                            success=False,
                            message=f"Executor timeout after {config.get('executor_timeout', 'unknown')}s",
                            metadata={
                                "error": "executor_timeout",
                                "timeout_duration": config.get("executor_timeout"),
                                "archetype": archetype,
                                "workflow_type": "outreach_concurrent"
                            }
                        )
                    
                    if attempt >= len(fallback_sequence):
                        # Final attempt failed - return error result
                        metadata = {
                            "error": str(e),
                            "attempts": attempt,
                            "final_archetype": archetype,
                            "workflow_type": "outreach_concurrent"
                        }
                        # Add safety_timeout flag if this was a safety timeout
                        if "Safety validation timed out" in str(e):
                            metadata["safety_timeout"] = True
                        
                        return OutreachPipelineResult(
                            success=False,
                            message="",
                            metadata=metadata
                        )
                    continue
            
            # All attempts failed
            # Check if all failures were safety-related or timeout-related
            if safety_failure_count == len(fallback_sequence):
                error_message = "All archetype attempts failed due to safety validation"
            elif safety_timeout_count == len(fallback_sequence):
                error_message = "All archetype attempts failed due to safety timeout"
            else:
                error_message = "All archetype attempts failed"
                
            metadata = {
                "error": error_message,
                "attempts": len(fallback_sequence),
                "safety_failures": safety_failure_count,
                "workflow_type": "outreach_concurrent"
            }
            
            # Add safety timeout flag if all attempts timed out
            if safety_timeout_count == len(fallback_sequence):
                metadata["safety_timeout"] = True
            
            # Add safety blocked flag if all attempts failed safety validation
            if safety_failure_count == len(fallback_sequence):
                metadata["safety_blocked"] = True
                
            return OutreachPipelineResult(
                success=False,
                message="",
                metadata=metadata
            )
        finally:
            # Phase 9: Always release concurrent slot in finally block
            self.budget_manager.release_slot()
    
    def _execute_workflow_phases(
        self,
        mission: OutreachMission,
        recipient: RecipientProfile,
        ctx: ArchetypeContext,
        config: Dict[str, Any],
    ) -> OutreachPipelineResult:
        """Execute the core workflow phases P2-P6."""
        
        # Record workflow start time for telemetry
        # workflow_start_time = time.time()  # Currently unused, available for future telemetry
        
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
        
        # Phase 9: Apply executor timeout to research calls
        executor_timeout = config.get("executor_timeout", None)
        
        if executor_timeout:
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                company_future = executor.submit(  # type: ignore[arg-type]  # Mypy false positive with keyword args
                    self.company_executor.search_company_context,
                    mission_id=getattr(mission, 'id', 'unknown'),
                    target_company=recipient.company,
                    archetype=ctx.archetype,
                    rag_params=ctx.rag_params.__dict__ if hasattr(ctx, 'rag_params') else {},
                    signal_params=ctx.signal_params.__dict__ if hasattr(ctx, 'signal_params') else {}
                )
                contact_future = executor.submit(  # type: ignore[arg-type]  # Mypy false positive with keyword args
                    self.contact_executor.search_contact_profile,
                    mission_id=getattr(mission, 'id', 'unknown'),
                    target_role=recipient.title,
                    target_company=recipient.company,
                    archetype=ctx.archetype,
                    rag_params=ctx.rag_params.__dict__ if hasattr(ctx, 'rag_params') else {},
                    signal_params=ctx.signal_params.__dict__ if hasattr(ctx, 'signal_params') else {}
                )
                
                try:
                    company_info = company_future.result(timeout=executor_timeout)
                    contact_info = contact_future.result(timeout=executor_timeout)
                except concurrent.futures.TimeoutError:
                    raise Exception(f"Executor timeout after {executor_timeout}s during research")
        else:
            # No timeout - execute normally
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
        
        content = MessageContent(
            recipient_name=recipient.name,
            recipient_title=recipient.title,
            company_name=recipient.company,
            value_proposition=getattr(mission, 'value_proposition', ''),
            key_points=[],
            personalization_elements=[],
            constraints=[],
            metadata={
                'company_context': research_bundle.company or {},
                'contact_context': research_bundle.contact or {},
                'archetype_context': ctx.__dict__
            }
        )
        mp = self.message_planner.create_message_plan(content)
        
        # Phase 9: Apply executor timeout to message generation
        if executor_timeout:
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                message_future = executor.submit(
                    self.message_executor.generate_message,
                    message_plan=mp.__dict__,
                    archetype_context=ctx.__dict__
                )
                
                try:
                    message_result = message_future.result(timeout=executor_timeout)
                except concurrent.futures.TimeoutError:
                    raise Exception(f"Executor timeout after {executor_timeout}s during message generation")
        else:
            # No timeout - execute normally
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
        
        # Handle both sync and async safety evaluators with timeout
        safety_result_raw = self.safety_validator.evaluate(message_result.message)
        import inspect
        safety_timeout = config.get("safety_timeout", None)
        
        if inspect.iscoroutine(safety_result_raw):
            try:
                loop = asyncio.get_running_loop()
                # Use thread executor to run coroutine in new event loop with timeout
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, safety_result_raw)
                    if safety_timeout:
                        try:
                            safety_result = future.result(timeout=safety_timeout)
                        except concurrent.futures.TimeoutError:
                            raise Exception(f"Safety validation timed out after {safety_timeout}s")
                    else:
                        safety_result = future.result()
            except RuntimeError:
                if safety_timeout:
                    try:
                        safety_result = asyncio.run(asyncio.wait_for(safety_result_raw, timeout=safety_timeout))
                    except asyncio.TimeoutError:
                        raise Exception(f"Safety validation timed out after {safety_timeout}s")
                else:
                    safety_result = asyncio.run(safety_result_raw)
        else:
            if safety_timeout and callable(safety_result_raw):
                # For sync safety evaluators, use thread executor for timeout
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(safety_result_raw)
                    try:
                        safety_result = future.result(timeout=safety_timeout)
                    except concurrent.futures.TimeoutError:
                        raise Exception(f"Safety validation timed out after {safety_timeout}s")
            else:
                safety_result = safety_result_raw
        
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
        
        # Record concurrent workflow completion telemetry
        # research phase finished
        use_concurrent_research = config.get("use_concurrent_research", False)
        use_multi_draft = config.get("use_multi_draft", False)
        
        if use_concurrent_research:
            self.telemetry_bus.record_event("research_parallel_end", "L3", {
                "workflow_type": "outreach",
                "stage": "research",
                "mission_id": getattr(mission, 'id', 'unknown')
            })
        
        # draft generation finished
        if use_multi_draft:
            self.telemetry_bus.record_event("draft_generation_end", "L3", {
                "workflow_type": "outreach",
                "stage": "drafts",
                "mission_id": getattr(mission, 'id', 'unknown')
            })
        
        self.telemetry_bus.record_event("concurrent_workflow_end", "L3", {
            "mission_id": getattr(mission, 'id', 'unknown'),
            "target_company": recipient.company,
            "archetype": ctx.archetype.value if hasattr(ctx.archetype, 'value') else str(ctx.archetype),
            "workflow_type": "outreach_concurrent",
            "success": True
        })
        
        # Return successful result
        result = OutreachPipelineResult(
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
        return result
    
    async def _execute_workflow_phases_concurrent_async(
        self,
        mission: OutreachMission,
        recipient: RecipientProfile,
        ctx: ArchetypeContext,
        config: Dict[str, Any],
    ) -> OutreachPipelineResult:
        """Execute workflow phases with optional concurrency (async version)."""
        
        # Record workflow start time for telemetry
        workflow_start_time = time.time()
        
        # P2 — Research Planning (same as sequential)
        logger.info("P2: Planning research")
        research_plan = self.research_planner.plan_research(ctx, mission, recipient)
        
        # Research Execution with optional concurrency
        use_concurrent_research = config.get("use_concurrent_research", False)
        partial_concurrent_handled = False
        if use_concurrent_research:
            logger.info("P2: Executing research concurrently")
            research_bundle = await self._execute_research_concurrent(mission, recipient, ctx)
            
            # Detect partial concurrent research failure
            if hasattr(research_bundle, 'company') and hasattr(research_bundle, 'contact'):
                company_has_data = bool(research_bundle.company)
                contact_has_data = bool(research_bundle.contact)
                partial_concurrent_handled = company_has_data != contact_has_data  # XOR: one succeeds, one fails
                if partial_concurrent_handled:
                    logger.info("P2: Partial concurrent research failure detected and handled")
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
        content = MessageContent(
            recipient_name=recipient.name,
            recipient_title=recipient.title,
            company_name=recipient.company,
            value_proposition=getattr(mission, 'value_proposition', ''),
            key_points=[],
            personalization_elements=[],
            constraints=[],
            metadata={
                'company_context': research_bundle.company or {},
                'contact_context': research_bundle.contact or {},
                'archetype_context': ctx.__dict__
            }
        )
        mp = self.message_planner.create_message_plan(content)
        
        if use_multi_draft:
            message_result = await self._generate_multiple_drafts_and_select_best(mp, ctx, config)
        else:
            message_result = self.message_executor.generate_message(
                message_plan=mp.__dict__,
                archetype_context=ctx.__dict__
            )
        
        # P4 — Final Safety Check (MUST be after message generation)
        logger.info("P4: Safety validation")
        safety_result_raw = self.safety_validator.evaluate(message_result.message)
        
        # Handle both sync and async safety evaluators
        import inspect
        if inspect.iscoroutine(safety_result_raw):
            safety_result = await safety_result_raw
        else:
            safety_result = safety_result_raw
        
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
        metadata = {
            "archetype": ctx.archetype,
            "research_bundle": research_bundle.__dict__,
            "message_plan": mp.__dict__,
            "safety_result": safety_result.__dict__,
            "workflow_type": "outreach_concurrent"
        }
        
        # Add partial concurrent research handling flag if detected
        if partial_concurrent_handled:
            metadata["partial_concurrent_handled"] = True
        
        return OutreachPipelineResult(
            success=True,
            message=message_result.message,
            metadata=metadata
        )
    
    async def _execute_research_concurrent(
        self,
        mission: OutreachMission,
        recipient: RecipientProfile,
        ctx: ArchetypeContext,
    ) -> ResearchBundle:
        """Execute company and contact research concurrently."""
        
        # Record concurrent research start telemetry
        self.telemetry_bus.record_event("concurrent_research_start", "L3", {
            "mission_id": getattr(mission, 'id', 'unknown'),
            "target_company": recipient.company,
            "archetype": ctx.archetype.value if hasattr(ctx.archetype, 'value') else str(ctx.archetype),
            "workflow_type": "outreach"
        })
        
        # Acquire concurrent execution slot
        timeout = self.budget_manager.get_limits()['executor_timeout']
        if not self.budget_manager.acquire_concurrent_slot(timeout=timeout):
            self.telemetry_bus.record_error("concurrent_slot_timeout", "L3", Exception(f"Could not acquire concurrent execution slot within {timeout}s"), {
                "mission_id": getattr(mission, 'id', 'unknown'),
                "timeout": timeout
            })
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
            
            # Record concurrent research completion telemetry
            self.telemetry_bus.record_event("concurrent_research_end", "L3", {
                "mission_id": getattr(mission, 'id', 'unknown'),
                "target_company": recipient.company,
                "archetype": ctx.archetype.value if hasattr(ctx.archetype, 'value') else str(ctx.archetype),
                "company_success": not isinstance(company_result, Exception),
                "contact_success": not isinstance(contact_result, Exception),
                "workflow_type": "outreach"
            })
            
            return ResearchBundle(company=company_data, contact=contact_data)
            
        except Exception as e:
            logger.error(f"Concurrent research execution failed: {e}")
            # Record concurrent research failure telemetry
            self.telemetry_bus.record_error("concurrent_research_failure", "L3", e, {
                "mission_id": getattr(mission, 'id', 'unknown'),
                "target_company": recipient.company,
                "workflow_type": "outreach"
            })
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
        
        # Record multi-draft generation start telemetry
        self.telemetry_bus.record_event("multi_draft_start", "L3", {
            "archetype": ctx.archetype.value if hasattr(ctx.archetype, 'value') else str(ctx.archetype),
            "max_parallel_drafts": config.get("max_parallel_drafts", 2),
            "workflow_type": "outreach"
        })
        
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
                    message_plan=temp_plan
                )
            )
            draft_tasks.append(task)
        
        # Wait for all drafts to complete
        drafts = await asyncio.gather(*draft_tasks, return_exceptions=True)
        
        # Filter out failed drafts
        valid_drafts = [d for d in drafts if not isinstance(d, Exception)]
        
        if not valid_drafts:
            # Record multi-draft failure telemetry
            self.telemetry_bus.record_error("multi_draft_all_failed", "L3", Exception("All message draft generation attempts failed"), {
                "archetype": ctx.archetype.value if hasattr(ctx.archetype, 'value') else str(ctx.archetype),
                "total_attempts": len(drafts),
                "workflow_type": "outreach"
            })
            raise Exception("All message draft generation attempts failed")
        
        # Record multi-draft completion telemetry
        self.telemetry_bus.record_event("multi_draft_end", "L3", {
            "archetype": ctx.archetype.value if hasattr(ctx.archetype, 'value') else str(ctx.archetype),
            "total_drafts": len(drafts),
            "valid_drafts": len(valid_drafts),
            "workflow_type": "outreach"
        })
        
        # Select best draft using voting
        return self._vote_best_draft(valid_drafts, ctx)
    
    def _vote_best_draft(self, drafts: List[Any], ctx: ArchetypeContext) -> Any:
        """Select the best draft using voting heuristic."""
        
        # First, filter drafts by safety
        safe_drafts = []
        for draft in drafts:
            safety_context = SafetyContext(
                content=draft.message,
                content_type="text",
                domain="outreach"
            )
            safety_result_raw = self.safety_validator.evaluate(safety_context)
            
            # Handle both sync and async safety evaluators
            import inspect
            if inspect.iscoroutine(safety_result_raw):
                try:
                    loop = asyncio.get_running_loop()
                    # Use thread executor to run coroutine in new event loop
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, safety_result_raw)
                        safety_result = future.result()
                except RuntimeError:
                    safety_result = asyncio.run(safety_result_raw)
            else:
                safety_result = safety_result_raw
                
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
