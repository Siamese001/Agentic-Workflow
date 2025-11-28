"""Outreach Orchestrator - L3 orchestration for outreach workflows.

Implements clean L1 â†’ L2 â†’ L5 â†’ L4 orchestration flow with deterministic
behavior and proper safety gating. Zero interference with resume orchestration.
"""

from __future__ import annotations

import asyncio
import inspect
import logging
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union

# L1 components (pure planning)
from l1.outreach_archetype_planning import OutreachArchetypePlanner, RecipientProfile
from l1.research_planning import ResearchRefinementPlanner
from l1.message_planning import MessagePlanner, MessageContent
from l1.outreach_dataclasses import (
    OutreachMission,
    ArchetypeContext,
    ArchetypeType,
)

# LIC-specific L1 planners
from l1.lic_profile_planner import LICProfilePlanner
from l1.lic_research_planner import LICResearchPlanner
from l1.lic_grounding_planner import LICGroundingPlanner
from l1.lic_fusion_planner import LICFusionPlanner
from l1.lic_persona_planner import LICPersonaPlanner

# L2 components (pure execution)
from l2.company_research_executor import CompanyResearchExecutor
from l2.contact_research_executor import ContactResearchExecutor
from l2.message_generation_executor import MessageGenerationExecutor
from l2.lic_research_executor import LICResearchExecutor
from l2.lic_message_executor import LICMessageExecutor
from l2.interfaces import L2ExecutionResult

# L5 components (safety)
from l5.safety_validator import SafetyValidator
from l5.types import SafetyContext

# Runtime components
from runtime.telemetry_bus import get_telemetry_bus
from runtime.execution_budget_manager import get_budget_manager, create_budget_limits_from_config

# LIC-specific L4 components
from l4.lic_vector_memory import VectorMemoryStore
from l4.lic_signal_scoring import SignalScorer
from l4.lic_cache_critique import CacheCritiquer


logger = logging.getLogger(__name__)


@dataclass
class OutreachPipelineResult:
    """Result of outreach pipeline execution."""
    success: bool
    message: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CircuitBreakerState:
    """Simple circuit breaker implementation for orchestration."""
    failure_count: int = 0
    last_failure_time: Optional[float] = None
    state: str = "closed"  # closed, open, half_open
    threshold: int = 5
    timeout_seconds: float = 60.0
    
    def should_open(self, result: OutreachPipelineResult) -> bool:
        """Check if circuit should open based on result."""
        if result.success:
            return False
            
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.threshold:
            self.state = "open"
            return True
        return False
    
    def is_open(self) -> bool:
        """Check if circuit is currently open."""
        if self.state == "closed":
            return False
        elif self.state == "open":
            if (self.last_failure_time and 
                time.time() - self.last_failure_time > self.timeout_seconds):
                self.state = "half_open"
                return False
            return True
        return False
    
    def reset(self) -> None:
        """Reset circuit breaker to closed state."""
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"


@dataclass
class FallbackTree:
    """LIC-style fallback tree for archetype sequence."""
    sequence: List[ArchetypeType] = field(default_factory=lambda: [
        ArchetypeType.EXECUTIVE,
        ArchetypeType.SENIOR_TA,
        ArchetypeType.RECRUITER,
    ])
    
    def iter_attempts(self, initial_context: ArchetypeContext) -> List[ArchetypeType]:
        """Get ordered list of archetype attempts."""
        return self.sequence.copy()


class PersonaDriftController:
    """Plug-in style persona drift controller."""
    
    def correct_if_needed(self, message_result: Any, archetype_context: ArchetypeContext) -> Any:
        """Correct persona drift if detected."""
        # Simple implementation - return as-is for now
        return message_result


class OutreachOrchestrator:
    """
    L3 Outreach Orchestrator implementing clean phase sequence.
    
    Executes outreach workflow with deterministic L1 â†’ L2 â†’ L5 â†’ L4 flow,
    proper budget management, safety gating, and LIC meta-loop integration.
    """
    
    def __init__(
        self,
        *,
        archetype_planner: Optional[OutreachArchetypePlanner] = None,
        research_planner: Optional[ResearchRefinementPlanner] = None,
        message_planner: Optional[MessagePlanner] = None,
        company_research_executor: Optional[CompanyResearchExecutor] = None,
        contact_research_executor: Optional[ContactResearchExecutor] = None,
        message_generation_executor: Optional[MessageGenerationExecutor] = None,
        safety_validator: Optional[SafetyValidator] = None,
        routing_policy: Optional[Any] = None,
        budget_manager: Optional[Any] = None,
        telemetry_bus: Optional[Any] = None,
        use_lic_pipeline: bool = False,
        circuit_breaker: Optional[CircuitBreakerState] = None,
        persona_drift_controller: Optional[PersonaDriftController] = None,
        fallback_tree: Optional[FallbackTree] = None,
        # LIC-specific components
        lic_profile_planner: Optional[LICProfilePlanner] = None,
        lic_research_planner: Optional[LICResearchPlanner] = None,
        lic_grounding_planner: Optional[LICGroundingPlanner] = None,
        lic_fusion_planner: Optional[LICFusionPlanner] = None,
        lic_persona_planner: Optional[LICPersonaPlanner] = None,
        lic_research_executor: Optional[LICResearchExecutor] = None,
        lic_message_executor: Optional[LICMessageExecutor] = None,
        vector_memory_store: Optional[VectorMemoryStore] = None,
        signal_scorer: Optional[SignalScorer] = None,
        cache_critiquer: Optional[CacheCritiquer] = None,
        **kwargs,
    ) -> None:
        """Initialize OutreachOrchestrator with dependency injection."""
        # Core L1/L2 components
        self.archetype_planner = archetype_planner
        self.research_planner = research_planner
        self.message_planner = message_planner
        self.company_research_executor = company_research_executor
        self.contact_research_executor = contact_research_executor
        self.message_generation_executor = message_generation_executor
        self.safety_validator = safety_validator
        
        # Runtime components
        self.routing_policy = routing_policy
        self.budget_manager = budget_manager or get_budget_manager()
        self.telemetry_bus = telemetry_bus or get_telemetry_bus()
        
        # LIC configuration
        self.use_lic_pipeline = use_lic_pipeline
        self.lic_profile_planner = lic_profile_planner
        self.lic_research_planner = lic_research_planner
        self.lic_grounding_planner = lic_grounding_planner
        self.lic_fusion_planner = lic_fusion_planner
        self.lic_persona_planner = lic_persona_planner
        self.lic_research_executor = lic_research_executor
        self.lic_message_executor = lic_message_executor
        self.vector_memory_store = vector_memory_store
        self.signal_scorer = signal_scorer
        self.cache_critiquer = cache_critiquer
        
        # Orchestration components
        self.circuit_breaker = circuit_breaker or CircuitBreakerState()
        self.persona_drift_controller = persona_drift_controller or PersonaDriftController()
        self.fallback_tree = fallback_tree or FallbackTree()
        
        # Configure telemetry
        self.telemetry_bus.configure(enabled=True, detail_level="standard")
    
    # Helper methods for budget and telemetry management
    
    async def _acquire_slot(self) -> bool:
        """Acquire execution slot from budget manager."""
        return self.budget_manager.acquire_slot()
    
    async def _release_slot(self) -> None:
        """Release execution slot from budget manager."""
        self.budget_manager.release_slot()
    
    def _emit_telemetry(self, event: str, stage: str, metadata: Dict[str, Any]) -> None:
        """Emit telemetry event safely (never blocks or throws)."""
        try:
            self.telemetry_bus.record_event(event, "L3", {
                "stage": stage,
                "workflow_type": "outreach",
                **metadata
            })
        except Exception:
            # Telemetry failures should never break workflow
            pass
    
    async def _execute_safety_check(self, message: str, context: Dict[str, Any], archetype: ArchetypeType) -> Any:
        """Execute safety validation with proper async handling."""
        if not self.safety_validator:
            # Mock safety result if validator not provided
            class MockSafetyResult:
                def __init__(self):
                    self.passes = True
                    self.violations = []
                    self.metadata = {"failure_type": "none"}
            return MockSafetyResult()
        
        safety_context = SafetyContext(
            content=message,
            content_type="text",
            domain="outreach",
            metadata={
                "context": context,
                "archetype": archetype
            }
        )
        
        safety_result = self.safety_validator.evaluate(safety_context)
        
        # Handle async safety results
        if inspect.iscoroutine(safety_result):
            safety_result = await safety_result
        
        return safety_result
    
    def _make_result(self, success: bool, message: str, metadata: Dict[str, Any]) -> OutreachPipelineResult:
        """Create standardized OutreachPipelineResult."""
        return OutreachPipelineResult(
            success=success,
            message=message,
            metadata=metadata
        )
    
    def _make_circuit_open_result(self) -> OutreachPipelineResult:
        """Create result for circuit breaker open condition."""
        return self._make_result(
            success=False,
            message="Circuit breaker is open - too many recent failures",
            metadata={
                "error": "circuit_breaker_open",
                "failure_count": self.circuit_breaker.failure_count,
                "used_pipeline": "lic" if self.use_lic_pipeline else "baseline"
            }
        )
    
    def _make_all_failed_result(self, attempts: int) -> OutreachPipelineResult:
        """Create result when all archetype attempts failed."""
        return self._make_result(
            success=False,
            message=f"All archetype attempts failed after {attempts} tries",
            metadata={
                "error": "all_attempts_failed",
                "attempts": attempts,
                "used_pipeline": "lic" if self.use_lic_pipeline else "baseline"
            }
        )
    
    def _make_budget_error_result(self, reason: str) -> OutreachPipelineResult:
        """Create result for budget-related failures."""
        return self._make_result(
            success=False,
            message=f"Budget error: {reason}",
            metadata={
                "error": "budget_error",
                "budget_reason": reason,
                "used_pipeline": "lic" if self.use_lic_pipeline else "baseline"
            }
        )
    
    # Sequential pipeline implementation
    
    async def orchestrate_outreach(
        self,
        mission: OutreachMission,
        recipient: RecipientProfile,
        config: Optional[Dict[str, Any]] = None,
    ) -> OutreachPipelineResult:
        """Sequential outreach pipeline with clean L1â†’L2â†’L5 orchestration."""
        workflow_start_time = time.time()
        config = config or {}
        
        # Configure budget manager
        budget_limits = create_budget_limits_from_config(config)
        self.budget_manager.configure(budget_limits)
        
        # Emit workflow start telemetry
        self._emit_telemetry("workflow_start", "orchestration", {
            "mission_id": getattr(mission, 'id', 'unknown'),
            "recipient": recipient.name,
            "used_pipeline": "lic" if self.use_lic_pipeline else "baseline"
        })
        
        # Acquire execution slot
        if not await self._acquire_slot():
            return self._make_budget_error_result("Concurrent execution slot unavailable")
        
        try:
            # Check budget before starting
            if not self.budget_manager.check_budget("outreach"):
                return self._make_budget_error_result(self.budget_manager.get_budget_exceeded_reason())
            
            # Choose execution path based on feature flag
            if self.use_lic_pipeline:
                return await self._execute_lic_sequential_workflow(mission, recipient, config, workflow_start_time)
            else:
                return await self._execute_baseline_sequential_workflow(mission, recipient, config, workflow_start_time)
        
        finally:
            # Always release slot in finally block
            await self._release_slot()
    
    async def _execute_baseline_sequential_workflow(
        self,
        mission: OutreachMission,
        recipient: RecipientProfile,
        config: Dict[str, Any],
        workflow_start_time: float,
    ) -> OutreachPipelineResult:
        """Execute baseline sequential workflow."""
        try:
            # L1: Archetype planning
            self._emit_telemetry("phase_start", "archetype_planning", {})
            archetype_context = self.archetype_planner.plan_archetype_influence(mission)
            self._emit_telemetry("phase_end", "archetype_planning", {
                "archetype": archetype_context.archetype
            })
            
            # L1: Research planning
            self._emit_telemetry("phase_start", "research_planning", {})
            research_plan = self.research_planner.plan_research_refinement(
                mission, archetype_context, config
            )
            self._emit_telemetry("phase_end", "research_planning", {})
            
            # L2: Research execution
            self._emit_telemetry("phase_start", "research_execution", {})
            company_results = self.company_research_executor.search_company_context(
                recipient.company, archetype_context.archetype, {}
            )
            contact_results = self.contact_research_executor.search_contact_context(
                recipient.name, recipient.title, archetype_context.archetype, {}
            )
            self._emit_telemetry("phase_end", "research_execution", {
                "company_results_count": len(company_results),
                "contact_results_count": len(contact_results)
            })
            
            # L1: Message planning
            self._emit_telemetry("phase_start", "message_planning", {})
            message_plan = self.message_planner.create_message_plan(
                mission, archetype_context, research_plan, 
                {"company": company_results, "contact": contact_results}
            )
            self._emit_telemetry("phase_end", "message_planning", {})
            
            # L2: Message generation
            self._emit_telemetry("phase_start", "message_generation", {})
            message_result = self.message_generation_executor.generate_message(message_plan)
            self._emit_telemetry("phase_end", "message_generation", {})
            
            # L5: Safety validation
            self._emit_telemetry("phase_start", "safety_validation", {})
            safety_result = await self._execute_safety_check(
                message_result.message,
                {"mission": mission.__dict__, "recipient": recipient.__dict__},
                archetype_context.archetype
            )
            self._emit_telemetry("phase_end", "safety_validation", {
                "safety_passed": getattr(safety_result, 'passes', True)
            })
            
            # Check safety result
            if not getattr(safety_result, 'passes', True):
                return self._make_result(
                    success=False,
                    message="Safety validation failed",
                    metadata={
                        "safety_violations": getattr(safety_result, 'violations', []),
                        "archetype": archetype_context.archetype,
                        "used_pipeline": "baseline",
                        "safety_passed": False
                    }
                )
            
            # Success
            duration = time.time() - workflow_start_time
            self._emit_telemetry("workflow_end", "orchestration", {
                "success": True,
                "duration": duration,
                "archetype": archetype_context.archetype,
                "safety_passed": True
            })
            
            return self._make_result(
                success=True,
                message=message_result.message,
                metadata={
                    "archetype": archetype_context.archetype,
                    "used_pipeline": "baseline",
                    "safety_passed": True,
                    "fallback_used": False,
                    "attempts": 1,
                    "duration": duration
                }
            )
            
        except Exception as e:
            duration = time.time() - workflow_start_time
            self._emit_telemetry("workflow_end", "orchestration", {
                "success": False,
                "duration": duration,
                "error": str(e)
            })
            
            return self._make_result(
                success=False,
                message=f"Sequential workflow failed: {str(e)}",
                metadata={
                    "error": str(e),
                    "used_pipeline": "baseline",
                    "duration": duration
                }
            )
    
    async def _execute_lic_sequential_workflow(
        self,
        mission: OutreachMission,
        recipient: RecipientProfile,
        config: Dict[str, Any],
        workflow_start_time: float,
    ) -> OutreachPipelineResult:
        """Execute LIC sequential workflow with meta-loop fallback."""
        try:
            # Check if LIC components are available
            if not self._has_lic_components():
                return self._make_result(
                    success=False,
                    message="LIC components not available",
                    metadata={"error": "lic_components_missing", "used_pipeline": "lic"}
                )
            
            # Create archetype context for fallback sequence
            archetype_context = ArchetypeContext(
                mission=mission,
                recipient=recipient,
                archetype=ArchetypeType.EXECUTIVE  # Will be overridden in fallback loop
            )
            
            # Execute meta-loop with fallback sequence
            return await self._execute_lic_meta_loop(archetype_context, config, workflow_start_time)
            
        except Exception as e:
            duration = time.time() - workflow_start_time
            self._emit_telemetry("workflow_end", "orchestration", {
                "success": False,
                "duration": duration,
                "error": str(e),
                "used_pipeline": "lic"
            })
            
            return self._make_result(
                success=False,
                message=f"LIC sequential workflow failed: {str(e)}",
                metadata={
                    "error": str(e),
                    "used_pipeline": "lic",
                    "duration": duration
                }
            )
    
    def _has_lic_components(self) -> bool:
        """Check if required LIC components are available."""
        return (
            self.lic_profile_planner and
            self.lic_research_planner and
            self.lic_grounding_planner and
            self.lic_fusion_planner and
            self.lic_persona_planner and
            self.lic_research_executor and
            self.lic_message_executor
        )
    
    async def _execute_lic_meta_loop(
        self,
        archetype_context: ArchetypeContext,
        config: Dict[str, Any],
        workflow_start_time: float,
    ) -> OutreachPipelineResult:
        """Execute LIC meta-loop with Execâ†’Senior_TAâ†’Recruiter fallback."""
        archetype_sequence = self.fallback_tree.iter_attempts(archetype_context)
        fallback_used = False
        
        for attempt, archetype in enumerate(archetype_sequence, 1):
            # Check circuit breaker
            if self.circuit_breaker.is_open():
                return self._make_circuit_open_result()
            
            # Check budget before each attempt
            if not self.budget_manager.check_depth():
                return self._make_budget_error_result("Recursion depth exceeded")
            
            if not self.budget_manager.increment_depth("outreach"):
                return self._make_budget_error_result("Recursion depth exceeded")
            
            try:
                self._emit_telemetry("meta_loop_attempt", "orchestration", {
                    "attempt": attempt,
                    "archetype": archetype,
                    "max_attempts": len(archetype_sequence)
                })
                
                # Update archetype in context
                archetype_context.archetype = archetype
                
                # Execute workflow for this archetype
                result = await self._execute_lic_archetype_workflow(archetype_context, config)
                
                if result.success:
                    # Success - record and return
                    if attempt > 1:
                        fallback_used = True
                    
                    duration = time.time() - workflow_start_time
                    self._emit_telemetry("workflow_end", "orchestration", {
                        "success": True,
                        "duration": duration,
                        "archetype": archetype,
                        "used_pipeline": "lic",
                        "attempts": attempt,
                        "fallback_used": fallback_used
                    })
                    
                    # Update metadata with fallback info
                    result.metadata.update({
                        "fallback_used": fallback_used,
                        "attempts": attempt,
                        "duration": duration
                    })
                    
                    return result
                
                # Failure - record and continue
                self.circuit_breaker.should_open(result)
                fallback_used = True
                
            except Exception as e:
                logger.error(f"LIC archetype workflow failed for {archetype}: {str(e)}")
                self.circuit_breaker.should_open(self._make_result(False, str(e), {}))
                fallback_used = True
                
            finally:
                # Always decrement depth
                self.budget_manager.decrement_depth("outreach")
            
            # Small delay between attempts
            if archetype != archetype_sequence[-1]:
                await asyncio.sleep(0.5)
        
        # All attempts failed
        return self._make_all_failed_result(len(archetype_sequence))
    
    async def _execute_lic_archetype_workflow(
        self,
        archetype_context: ArchetypeContext,
        config: Dict[str, Any],
    ) -> OutreachPipelineResult:
        """Execute LIC workflow for specific archetype."""
        try:
            mission = archetype_context.mission
            recipient = archetype_context.recipient
            archetype = archetype_context.archetype
            
            # Step 1: Profile analysis
            profile_plan = self.lic_profile_planner.plan_profile_analysis(
                recipient_name=recipient.name,
                recipient_title=recipient.title,
                recipient_company=recipient.company
            )
            
            # Step 2: Research planning
            research_plan = self.lic_research_planner.plan_research(
                recipient_company=recipient.company,
                recipient_name=recipient.name,
                recipient_archetype=archetype.value
            )
            
            # Step 3: Research execution
            research_result = await self.lic_research_executor.execute_research(research_plan)
            
            if not research_result.success:
                return self._make_result(
                    success=False,
                    message=f"Research execution failed: {research_result.message}",
                    metadata={"error": "research_failed", "archetype": archetype.value}
                )
            
            # Step 4: Grounding planning
            mission_context_str = (
                f"objective: {mission.objective}, "
                f"target_role: {mission.target_role}, "
                f"target_company: {mission.target_company}, "
                f"value_proposition: {mission.value_proposition}, "
                f"urgency: {mission.urgency}"
            )
            
            grounding_plan = self.lic_grounding_planner.plan_grounding_extraction(
                mission_context=mission_context_str,
                recipient_archetype=archetype.value
            )
            
            # Step 5: Fusion planning
            resume_capabilities = self._extract_resume_capabilities(mission, recipient)
            
            fusion_plan = self.lic_fusion_planner.plan_resume_fusion(
                mission_context=mission_context_str,
                recipient_archetype=archetype.value,
                resume_capabilities=resume_capabilities
            )
            
            # Step 6: Persona planning
            persona_plan = self.lic_persona_planner.plan_persona_consistency(
                mission_context=mission_context_str,
                recipient_archetype=archetype.value,
                sender_persona_profile={"communication_style": "professional", "tone": "confident"}
            )
            
            # Step 7: Message generation
            if not self.lic_message_executor:
                return self._make_result(
                    success=False,
                    message="LIC message executor not available",
                    metadata={"error": "message_executor_missing", "archetype": archetype.value}
                )
            
            message_result = await self.lic_message_executor.execute_message_generation(
                fusion_plan, grounding_plan, profile_plan
            )
            
            if not message_result.success:
                return self._make_result(
                    success=False,
                    message=f"Message generation failed: {message_result.message}",
                    metadata={"error": "message_failed", "archetype": archetype.value}
                )
            
            # Step 8: Safety validation
            safety_result = await self._execute_safety_check(
                message_result.data.primary_message.message if hasattr(message_result.data, 'primary_message') else str(message_result.data),
                {"mission": mission.__dict__, "recipient": recipient.__dict__},
                archetype
            )
            
            # Check safety result
            if not getattr(safety_result, 'passes', True):
                return self._make_result(
                    success=False,
                    message="Safety validation failed",
                    metadata={
                        "safety_violations": getattr(safety_result, 'violations', []),
                        "archetype": archetype.value,
                        "safety_passed": False
                    }
                )
            
            # Success
            final_message = self._assemble_lic_message(message_result.data)
            
            return self._make_result(
                success=True,
                message=final_message,
                metadata={
                    "archetype": archetype.value,
                    "research_data": research_result.data.__dict__ if hasattr(research_result.data, '__dict__') else {},
                    "message_data": message_result.data.__dict__ if hasattr(message_result.data, '__dict__') else {},
                    "safety_passed": True
                }
            )
            
        except Exception as e:
            return self._make_result(
                success=False,
                message=f"LIC archetype workflow failed: {str(e)}",
                metadata={"error": str(e)}
            )
    
    def _extract_resume_capabilities(self, mission: OutreachMission, recipient: RecipientProfile) -> Dict[str, List[str]]:
        """Extract resume capabilities from mission context."""
        default_capabilities = {
            "technical_skills": ["Python", "AI", "ML", "Data Analysis", "Project Management"],
            "achievements": ["Led successful projects", "Delivered measurable business impact"],
            "experience": ["Software development", "Team leadership", "Strategic planning"],
            "technologies": ["Machine Learning", "Cloud Computing", "Data Analytics"]
        }
        
        # Extract from mission context if available
        if hasattr(mission, 'sender_capabilities') and mission.sender_capabilities:
            capabilities = mission.sender_capabilities.copy()
            for category, defaults in default_capabilities.items():
                if category not in capabilities or not capabilities[category]:
                    capabilities[category] = defaults
            return capabilities
        
        # Extract from mission metadata if available
        if hasattr(mission, 'metadata') and mission.metadata:
            metadata_caps = mission.metadata.get('resume_capabilities', {})
            if metadata_caps:
                capabilities = metadata_caps.copy()
                for category, defaults in default_capabilities.items():
                    if category not in capabilities or not capabilities[category]:
                        capabilities[category] = defaults
                return capabilities
        
        # Return default capabilities
        return default_capabilities
    
    def _assemble_lic_message(self, message_data: Any) -> str:
        """Assemble final message from LIC message data."""
        if hasattr(message_data, 'primary_message'):
            primary = message_data.primary_message
            components = [
                getattr(primary, 'hook', ''),
                getattr(primary, 'value_prop', ''),
                getattr(primary, 'evidence', ''),
                getattr(primary, 'cta', ''),
                getattr(primary, 'closing', '')
            ]
            return "\n\n".join(filter(None, components))
        return str(message_data)
    
    # Concurrent pipeline implementation
    
    async def orchestrate_outreach_concurrent(
        self,
        mission: OutreachMission,
        recipient: RecipientProfile,
        config: Optional[Dict[str, Any]] = None,
    ) -> OutreachPipelineResult:
        """Concurrent outreach pipeline with async task management."""
        workflow_start_time = time.time()
        config = config or {}
        
        # Configure budget manager
        budget_limits = create_budget_limits_from_config(config)
        self.budget_manager.configure(budget_limits)
        
        # Emit concurrent workflow start telemetry
        self._emit_telemetry("concurrent_workflow_start", "orchestration", {
            "mission_id": getattr(mission, 'id', 'unknown'),
            "recipient": recipient.name,
            "used_pipeline": "lic" if self.use_lic_pipeline else "baseline"
        })
        
        # Acquire execution slot
        if not await self._acquire_slot():
            return self._make_budget_error_result("Concurrent execution slot unavailable")
        
        try:
            # Choose execution path based on feature flag
            if self.use_lic_pipeline:
                return await self._execute_lic_concurrent_workflow(mission, recipient, config, workflow_start_time)
            else:
                return await self._execute_baseline_concurrent_workflow(mission, recipient, config, workflow_start_time)
        
        finally:
            # Always release slot in finally block
            await self._release_slot()
    
    async def _execute_baseline_concurrent_workflow(
        self,
        mission: OutreachMission,
        recipient: RecipientProfile,
        config: Dict[str, Any],
        workflow_start_time: float,
    ) -> OutreachPipelineResult:
        """Execute baseline concurrent workflow."""
        try:
            # L1: Archetype planning
            self._emit_telemetry("phase_start", "archetype_planning", {})
            archetype_context = self.archetype_planner.plan_archetype_influence(mission)
            self._emit_telemetry("phase_end", "archetype_planning", {
                "archetype": archetype_context.archetype
            })
            
            # L1: Research planning
            self._emit_telemetry("phase_start", "research_planning", {})
            research_plan = self.research_planner.plan_research_refinement(
                mission, archetype_context, config
            )
            self._emit_telemetry("phase_end", "research_planning", {})
            
            # L2: Concurrent research execution
            self._emit_telemetry("research_parallel_start", "execution", {})
            
            # Create async tasks for concurrent execution
            async def execute_company_research():
                return self.company_research_executor.search_company_context(
                    recipient.company, archetype_context.archetype, {}
                )
            
            async def execute_contact_research():
                return self.contact_research_executor.search_contact_context(
                    recipient.name, recipient.title, archetype_context.archetype, {}
                )
            
            research_tasks = [
                asyncio.create_task(execute_company_research()),
                asyncio.create_task(execute_contact_research())
            ]
            
            company_results, contact_results = await asyncio.gather(*research_tasks, return_exceptions=True)
            
            # Handle exceptions in research
            if isinstance(company_results, Exception):
                company_results = {}
            if isinstance(contact_results, Exception):
                contact_results = {}
            
            self._emit_telemetry("research_parallel_end", "execution", {
                "company_results_count": len(company_results),
                "contact_results_count": len(contact_results)
            })
            
            # L1: Message planning
            self._emit_telemetry("phase_start", "message_planning", {})
            message_plan = self.message_planner.create_message_plan(
                mission, archetype_context, research_plan,
                {"company": company_results, "contact": contact_results}
            )
            self._emit_telemetry("phase_end", "message_planning", {})
            
            # L2: Message generation (with multi-draft if enabled)
            self._emit_telemetry("draft_generation_start", "execution", {})
            if config.get("use_multi_draft", False):
                # Generate multiple drafts concurrently
                async def generate_draft():
                    return self.message_generation_executor.generate_message(message_plan)
                
                draft_tasks = []
                for i in range(config.get("draft_count", 3)):
                    task = asyncio.create_task(generate_draft())
                    draft_tasks.append(task)
                
                draft_results = await asyncio.gather(*draft_tasks, return_exceptions=True)
                
                # Filter successful drafts and apply persona drift controller
                successful_drafts = [r for r in draft_results if not isinstance(r, Exception)]
                if successful_drafts:
                    message_result = successful_drafts[0]  # Use first successful draft
                    message_result = self.persona_drift_controller.correct_if_needed(message_result, archetype_context)
                else:
                    return self._make_result(
                        success=False,
                        message="All draft generations failed",
                        metadata={"error": "all_drafts_failed", "archetype": archetype_context.archetype}
                    )
            else:
                message_result = self.message_generation_executor.generate_message(message_plan)
            
            self._emit_telemetry("draft_generation_end", "execution", {})
            
            # L5: Safety validation
            self._emit_telemetry("safety_validation_start", "validation", {})
            safety_result = await self._execute_safety_check(
                message_result.message,
                {"mission": mission.__dict__, "recipient": recipient.__dict__},
                archetype_context.archetype
            )
            self._emit_telemetry("safety_validation_end", "validation", {
                "safety_passed": getattr(safety_result, 'passes', True)
            })
            
            # Check safety result
            if not getattr(safety_result, 'passes', True):
                return self._make_result(
                    success=False,
                    message="Safety validation failed",
                    metadata={
                        "safety_violations": getattr(safety_result, 'violations', []),
                        "archetype": archetype_context.archetype,
                        "used_pipeline": "baseline",
                        "safety_passed": False
                    }
                )
            
            # Success
            duration = time.time() - workflow_start_time
            self._emit_telemetry("concurrent_workflow_end", "orchestration", {
                "success": True,
                "duration": duration,
                "archetype": archetype_context.archetype,
                "safety_passed": True,
                "used_pipeline": "baseline"
            })
            
            return self._make_result(
                success=True,
                message=message_result.message,
                metadata={
                    "archetype": archetype_context.archetype,
                    "used_pipeline": "baseline",
                    "safety_passed": True,
                    "fallback_used": False,
                    "attempts": 1,
                    "duration": duration,
                    "concurrent": True
                }
            )
            
        except Exception as e:
            duration = time.time() - workflow_start_time
            self._emit_telemetry("concurrent_workflow_end", "orchestration", {
                "success": False,
                "duration": duration,
                "error": str(e),
                "used_pipeline": "baseline"
            })
            
            return self._make_result(
                success=False,
                message=f"Concurrent workflow failed: {str(e)}",
                metadata={
                    "error": str(e),
                    "used_pipeline": "baseline",
                    "duration": duration,
                    "concurrent": True
                }
            )
    
    async def _execute_lic_concurrent_workflow(
        self,
        mission: OutreachMission,
        recipient: RecipientProfile,
        config: Dict[str, Any],
        workflow_start_time: float,
    ) -> OutreachPipelineResult:
        """Execute LIC concurrent workflow with meta-loop fallback."""
        try:
            # Check if LIC components are available
            if not self._has_lic_components():
                return self._make_result(
                    success=False,
                    message="LIC components not available",
                    metadata={"error": "lic_components_missing", "used_pipeline": "lic"}
                )
            
            # Create archetype context for fallback sequence
            archetype_context = ArchetypeContext(
                mission=mission,
                recipient=recipient,
                archetype=ArchetypeType.EXECUTIVE  # Will be overridden in fallback loop
            )
            
            # Execute meta-loop with fallback sequence
            return await self._execute_lic_concurrent_meta_loop(archetype_context, config, workflow_start_time)
            
        except Exception as e:
            duration = time.time() - workflow_start_time
            self._emit_telemetry("concurrent_workflow_end", "orchestration", {
                "success": False,
                "duration": duration,
                "error": str(e),
                "used_pipeline": "lic"
            })
            
            return self._make_result(
                success=False,
                message=f"LIC concurrent workflow failed: {str(e)}",
                metadata={
                    "error": str(e),
                    "used_pipeline": "lic",
                    "duration": duration
                }
            )
    
    async def _execute_lic_concurrent_meta_loop(
        self,
        archetype_context: ArchetypeContext,
        config: Dict[str, Any],
        workflow_start_time: float,
    ) -> OutreachPipelineResult:
        """Execute LIC concurrent meta-loop with fallback sequence."""
        archetype_sequence = self.fallback_tree.iter_attempts(archetype_context)
        fallback_used = False
        
        for attempt, archetype in enumerate(archetype_sequence, 1):
            # Check circuit breaker
            if self.circuit_breaker.is_open():
                return self._make_circuit_open_result()
            
            # Check budget before each attempt
            if not self.budget_manager.check_depth():
                return self._make_budget_error_result("Recursion depth exceeded")
            
            if not self.budget_manager.increment_depth("outreach"):
                return self._make_budget_error_result("Recursion depth exceeded")
            
            try:
                self._emit_telemetry("concurrent_meta_loop_attempt", "orchestration", {
                    "attempt": attempt,
                    "archetype": archetype,
                    "max_attempts": len(archetype_sequence)
                })
                
                # Update archetype in context
                archetype_context.archetype = archetype
                
                # Execute concurrent workflow for this archetype
                result = await self._execute_lic_concurrent_archetype_workflow(archetype_context, config)
                
                if result.success:
                    # Success - record and return
                    if attempt > 1:
                        fallback_used = True
                    
                    duration = time.time() - workflow_start_time
                    self._emit_telemetry("concurrent_workflow_end", "orchestration", {
                        "success": True,
                        "duration": duration,
                        "archetype": archetype,
                        "used_pipeline": "lic",
                        "attempts": attempt,
                        "fallback_used": fallback_used
                    })
                    
                    # Update metadata with fallback info
                    result.metadata.update({
                        "fallback_used": fallback_used,
                        "attempts": attempt,
                        "duration": duration,
                        "concurrent": True
                    })
                    
                    return result
                
                # Failure - record and continue
                self.circuit_breaker.should_open(result)
                fallback_used = True
                
            except Exception as e:
                logger.error(f"LIC concurrent archetype workflow failed for {archetype}: {str(e)}")
                self.circuit_breaker.should_open(self._make_result(False, str(e), {}))
                fallback_used = True
                
            finally:
                # Always decrement depth
                self.budget_manager.decrement_depth("outreach")
            
            # Small delay between attempts
            if archetype != archetype_sequence[-1]:
                await asyncio.sleep(0.5)
        
        # All attempts failed
        return self._make_all_failed_result(len(archetype_sequence))
    
    async def _execute_lic_concurrent_archetype_workflow(
        self,
        archetype_context: ArchetypeContext,
        config: Dict[str, Any],
    ) -> OutreachPipelineResult:
        """Execute LIC concurrent workflow for specific archetype."""
        try:
            mission = archetype_context.mission
            recipient = archetype_context.recipient
            archetype = archetype_context.archetype
            
            # Step 1: Profile analysis
            profile_plan = self.lic_profile_planner.plan_profile_analysis(
                recipient_name=recipient.name,
                recipient_title=recipient.title,
                recipient_company=recipient.company
            )
            
            # Step 2: Research planning
            research_plan = self.lic_research_planner.plan_research(
                recipient_company=recipient.company,
                recipient_name=recipient.name,
                recipient_archetype=archetype.value
            )
            
            # Step 3: Concurrent research execution
            self._emit_telemetry("research_parallel_start", "lic_execution", {})
            research_result = await self.lic_research_executor.execute_research(research_plan)
            self._emit_telemetry("research_parallel_end", "lic_execution", {})
            
            if not research_result.success:
                return self._make_result(
                    success=False,
                    message=f"Research execution failed: {research_result.message}",
                    metadata={"error": "research_failed", "archetype": archetype.value}
                )
            
            # Step 4: Grounding planning
            mission_context_str = (
                f"objective: {mission.objective}, "
                f"target_role: {mission.target_role}, "
                f"target_company: {mission.target_company}, "
                f"value_proposition: {mission.value_proposition}, "
                f"urgency: {mission.urgency}"
            )
            
            grounding_plan = self.lic_grounding_planner.plan_grounding_extraction(
                mission_context=mission_context_str,
                recipient_archetype=archetype.value
            )
            
            # Step 5: Fusion planning
            resume_capabilities = self._extract_resume_capabilities(mission, recipient)
            
            fusion_plan = self.lic_fusion_planner.plan_resume_fusion(
                mission_context=mission_context_str,
                recipient_archetype=archetype.value,
                resume_capabilities=resume_capabilities
            )
            
            # Step 6: Persona planning
            persona_plan = self.lic_persona_planner.plan_persona_consistency(
                mission_context=mission_context_str,
                recipient_archetype=archetype.value,
                sender_persona_profile={"communication_style": "professional", "tone": "confident"}
            )
            
            # Step 7: Concurrent message generation
            self._emit_telemetry("draft_generation_start", "lic_execution", {})
            if config.get("use_multi_draft", False):
                # Generate multiple drafts concurrently
                async def generate_lic_draft():
                    return await self.lic_message_executor.execute_message_generation(fusion_plan, grounding_plan, profile_plan)
                
                draft_tasks = []
                for i in range(config.get("draft_count", 3)):
                    task = asyncio.create_task(generate_lic_draft())
                    draft_tasks.append(task)
                
                draft_results = await asyncio.gather(*draft_tasks, return_exceptions=True)
                
                # Filter successful drafts and apply persona drift controller
                successful_drafts = [r for r in draft_results if not isinstance(r, Exception) and r.success]
                if successful_drafts:
                    message_result = successful_drafts[0]  # Use first successful draft
                    # Apply persona drift controller if available
                    if hasattr(self.persona_drift_controller, 'correct_if_needed'):
                        message_result = self.persona_drift_controller.correct_if_needed(message_result, archetype_context)
                else:
                    return self._make_result(
                        success=False,
                        message="All draft generations failed",
                        metadata={"error": "all_drafts_failed", "archetype": archetype.value}
                    )
            else:
                message_result = await self.lic_message_executor.execute_message_generation(fusion_plan, grounding_plan, profile_plan)
            
            self._emit_telemetry("draft_generation_end", "lic_execution", {})
            
            if not message_result.success:
                return self._make_result(
                    success=False,
                    message=f"Message generation failed: {message_result.message}",
                    metadata={"error": "message_failed", "archetype": archetype.value}
                )
            
            # Step 8: Safety validation
            safety_result = await self._execute_safety_check(
                message_result.data.primary_message.message if hasattr(message_result.data, 'primary_message') else str(message_result.data),
                {"mission": mission.__dict__, "recipient": recipient.__dict__},
                archetype
            )
            
            # Check safety result
            if not getattr(safety_result, 'passes', True):
                return self._make_result(
                    success=False,
                    message="Safety validation failed",
                    metadata={
                        "safety_violations": getattr(safety_result, 'violations', []),
                        "archetype": archetype.value,
                        "safety_passed": False
                    }
                )
            
            # Success
            final_message = self._assemble_lic_message(message_result.data)
            
            return self._make_result(
                success=True,
                message=final_message,
                metadata={
                    "archetype": archetype.value,
                    "research_data": research_result.data.__dict__ if hasattr(research_result.data, '__dict__') else {},
                    "message_data": message_result.data.__dict__ if hasattr(message_result.data, '__dict__') else {},
                    "safety_passed": True
                }
            )
            
        except Exception as e:
            return self._make_result(
                success=False,
                message=f"LIC concurrent archetype workflow failed: {str(e)}",
                metadata={"error": str(e)}
            )
    
    # Synchronous wrapper and compatibility methods
    
    def run_single_outreach(
        self,
        mission: OutreachMission,
        recipient: RecipientProfile,
        config: Optional[Dict[str, Any]] = None,
    ) -> OutreachPipelineResult:
        """Synchronous wrapper for sequential pipeline, used by tests."""
        try:
            # Get current event loop or create new one
            try:
                loop = asyncio.get_running_loop()
                # If loop is running, we need to run in thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run,
                        self.orchestrate_outreach(mission, recipient, config)
                    )
                    return future.result(timeout=config.get("timeout", 120) if config else 120)
            except RuntimeError:
                # No event loop running, safe to use asyncio.run
                return asyncio.run(self.orchestrate_outreach(mission, recipient, config))
        except Exception as e:
            return self._make_result(
                success=False,
                message=f"Synchronous outreach failed: {str(e)}",
                metadata={"error": str(e)}
            )
    
    async def execute_outreach_workflow(
        self,
        mission_context: Union[OutreachMission, Dict[str, Any]],
        recipient_profile: Union[RecipientProfile, Dict[str, Any]],
        config: Optional[Dict[str, Any]] = None,
    ) -> OutreachPipelineResult:
        """Backward-compatible wrapper around orchestrate_outreach[_concurrent]."""
        # Handle dict inputs for backward compatibility
        if isinstance(mission_context, dict):
            mission = OutreachMission(
                id=mission_context.get("id", "unknown"),
                objective=mission_context.get("objective", "outreach"),
                target_company=mission_context.get("target_company", "Unknown"),
                target_role=mission_context.get("target_role", ""),
                value_proposition=mission_context.get("value_proposition", ""),
                urgency=mission_context.get("urgency", "low"),
                personalization_points=mission_context.get("personalization_points", []),
                constraints=mission_context.get("constraints", []),
                metadata=mission_context.get("metadata", {})
            )
        else:
            mission = mission_context
        
        if isinstance(recipient_profile, dict):
            recipient = RecipientProfile(
                name=recipient_profile.get("name", "Unknown"),
                title=recipient_profile.get("title", "Unknown"),
                company=recipient_profile.get("company", mission.target_company),
                email=recipient_profile.get("email", ""),
                linkedin_url=recipient_profile.get("linkedin_url", "")
            )
        else:
            recipient = recipient_profile
        
        # Choose pipeline based on config
        use_concurrent = config.get("use_concurrent", False) if config else False
        
        if use_concurrent:
            return await self.orchestrate_outreach_concurrent(mission, recipient, config)
        else:
            return await self.orchestrate_outreach(mission, recipient, config)
        
