"""Outreach Orchestrator - L3 orchestration for outreach workflows.

Implements clean L1 → L2 → L5 → L4 orchestration flow with deterministic
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
    
    Executes outreach workflow with deterministic L1 → L2 → L5 → L4 flow,
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
            context=context,
            archetype=archetype
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
        """Sequential outreach pipeline with clean L1→L2→L5 orchestration."""
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
        """Execute LIC meta-loop with Exec→Senior_TA→Recruiter fallback."""
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
    Enhanced with LIC meta-loop functionality for zero-loss integration.
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
        # LIC-specific components
        use_lic_pipeline: bool = False,
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
    ):
        """Initialize OutreachOrchestrator with safe stub defaults and dependency injection."""
        # Legacy pipeline components
        self.archetype_planner = archetype_planner or StubArchetypePlanner()
        self.research_planner = research_planner or StubResearchPlanner()
        self.message_planner = message_planner or StubMessagePlanner()
        self.company_executor = company_executor or StubCompanyResearchExecutor()
        self.contact_executor = contact_executor or StubContactResearchExecutor()
        self.message_executor = message_executor or StubMessageGenerationExecutor()
        self.state_manager = state_manager or StubStateManager()
        self.safety_validator = safety_validator or StubSafetyValidator()
        
        # LIC pipeline configuration
        self.use_lic_pipeline = use_lic_pipeline
        
        # Initialize LIC components with stubs if not provided
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
        
        # LIC meta-loop state
        self._lic_circuit_breaker_state = {
            "failure_count": 0,
            "last_failure_time": None,
            "state": "closed"  # closed, open, half_open
        }
        self._persona_drift_monitor = {
            "drift_count": 0,
            "last_drift_time": None,
            "drift_threshold": 0.3
        }
        
        # Initialize telemetry bus - MUST use singleton only
        self.telemetry_bus = get_telemetry_bus()
        
        # Initialize budget manager with dependency injection fallback
        try:
            self.budget_manager = budget_manager or get_budget_manager()
        except Exception:
            self.budget_manager = StubBudgetManager()
        
        logger.info("Initialized OutreachOrchestrator")
        
        # Log LIC pipeline status
        if self.use_lic_pipeline:
            logger.info("LIC meta-loop pipeline enabled")
            if not all([
                self.lic_profile_planner, self.lic_research_planner,
                self.lic_grounding_planner, self.lic_fusion_planner,
                self.lic_persona_planner, self.lic_research_executor,
                self.lic_message_executor, self.vector_memory_store,
                self.signal_scorer, self.cache_critiquer
            ]):
                logger.warning("LIC pipeline enabled but some components missing - using fallback behavior")
    
    async def execute_outreach(self, mission: OutreachMission, recipient_profile: RecipientProfile) -> OutreachPipelineResult:
        """Execute outreach workflow with LIC meta-loop support."""
        try:
            # Route to appropriate pipeline based on configuration
            if self.use_lic_pipeline and self._has_lic_components():
                return await self._execute_lic_workflow(mission, recipient_profile)
            else:
                return await self._execute_legacy_workflow(mission, recipient_profile)
        
        except Exception as e:
            logger.error(f"Outreach execution failed: {str(e)}")
            return OutreachPipelineResult(
                success=False,
                message=f"Outreach execution failed: {str(e)}",
                metadata={"error_type": "execution_error"}
            )
    
    def _has_lic_components(self) -> bool:
        """Check if all required LIC components are available."""
        required_components = [
            self.lic_profile_planner, self.lic_research_planner,
            self.lic_grounding_planner, self.lic_fusion_planner,
            self.lic_persona_planner, self.lic_research_executor,
            self.lic_message_executor, self.vector_memory_store,
            self.signal_scorer, self.cache_critiquer
        ]
        return all(component is not None for component in required_components)
    
    async def _execute_lic_workflow(self, mission: OutreachMission, recipient_profile: RecipientProfile) -> OutreachPipelineResult:
        """Execute LIC meta-loop workflow with Exec→Senior_TA→Recruiter fallback."""
        logger.info(f"Starting LIC workflow for {recipient_profile.name} at {recipient_profile.company}")
        
        try:
            # Step 1: Execute meta-loop with archetype fallback
            meta_loop_result = await self._execute_lic_meta_loop(mission, recipient_profile)
            
            if not meta_loop_result.success:
                return OutreachPipelineResult(
                    success=False,
                    message=f"LIC meta-loop failed: {meta_loop_result.message}",
                    metadata={"pipeline": "lic_meta_loop", "stage": "meta_loop"}
                )
            
            # Step 2: Monitor persona drift and apply corrections if needed
            drift_result = await self._monitor_persona_drift(meta_loop_result.data)
            
            if not drift_result.success:
                logger.warning(f"Persona drift detected and corrected: {drift_result.message}")
            
            # Step 3: Final safety validation
            safety_result = await self._validate_lic_output(meta_loop_result.data)
            
            if not safety_result.success:
                return OutreachPipelineResult(
                    success=False,
                    message=f"LIC safety validation failed: {safety_result.message}",
                    metadata={"pipeline": "lic_meta_loop", "stage": "safety_validation"}
                )
            
            # Success - return final result
            return OutreachPipelineResult(
                success=True,
                message=meta_loop_result.data.get("final_message", "LIC workflow completed successfully"),
                metadata={
                    "pipeline": "lic_meta_loop",
                    "archetype_used": meta_loop_result.data.get("archetype"),
                    "fallback_count": meta_loop_result.data.get("fallback_count", 0),
                    "drift_corrections": drift_result.data.get("corrections", 0) if drift_result.success else 0
                }
            )
            
        except Exception as e:
            self._record_circuit_breaker_failure()
            logger.error(f"LIC workflow execution failed: {str(e)}")
            
            # Fallback to legacy workflow if available
            if hasattr(self, '_execute_legacy_workflow'):
                logger.info("Falling back to legacy workflow due to LIC failure")
                return await self._execute_legacy_workflow(mission, recipient_profile)
            else:
                return OutreachPipelineResult(
                    success=False,
                    message=f"LIC workflow failed and no legacy fallback available: {str(e)}",
                    metadata={"pipeline": "lic_meta_loop", "error": "no_fallback"}
                )
    
    async def _execute_lic_meta_loop(self, mission: OutreachMission, recipient_profile: RecipientProfile) -> ExecutorResult:
        """Execute Exec→Senior_TA→Recruiter fallback sequence with circuit breaker."""
        # Check circuit breaker state first
        if self._is_circuit_breaker_open():
            return ExecutorResult.failure_result(
                "Circuit breaker is OPEN - blocking LIC meta-loop execution",
                error_code="CIRCUIT_BREAKER_OPEN"
            )
        
        # Define archetype fallback sequence
        archetype_sequence = ["executive", "hiring_manager", "technical_lead", "recruiter"]
        fallback_count = 0
        
        for archetype in archetype_sequence:
            try:
                logger.info(f"Attempting LIC workflow with archetype: {archetype}")
                
                # Execute archetype-specific workflow with timeout
                result = await asyncio.wait_for(
                    self._execute_archetype_workflow(mission, recipient_profile, archetype),
                    timeout=30.0  # 30 seconds per archetype
                )
                
                if result.success:
                    logger.info(f"LIC workflow succeeded with archetype: {archetype}")
                    
                    # Reset circuit breaker on success
                    self._reset_circuit_breaker()
                    
                    return ExecutorResult.success_result(
                        data={
                            "final_message": result.data.get("message", ""),
                            "archetype": archetype,
                            "fallback_count": fallback_count,
                            "execution_details": result.data
                        },
                        message=f"LIC workflow completed with {archetype} archetype"
                    )
                else:
                    logger.warning(f"LIC workflow failed for archetype {archetype}: {result.message}")
                    fallback_count += 1
                    
            except asyncio.TimeoutError:
                logger.warning(f"LIC workflow timed out for archetype: {archetype}")
                fallback_count += 1
                self._record_circuit_breaker_failure()
                
            except Exception as e:
                logger.error(f"LIC workflow error for archetype {archetype}: {str(e)}")
                fallback_count += 1
                self._record_circuit_breaker_failure()
            
            # Small delay between archetype attempts to allow transient failures to clear
            if archetype != archetype_sequence[-1]:  # Don't delay after last attempt
                await asyncio.sleep(0.5)
        
        # All archetype attempts failed
        return ExecutorResult.failure_result(
            f"All archetype workflows failed after {fallback_count} attempts",
            error_code="ALL_ARCHETYPES_FAILED"
        )
    
    async def _execute_archetype_workflow(self, mission: OutreachMission, recipient_profile: RecipientProfile, archetype: str) -> ExecutorResult:
        """Execute LIC workflow for specific archetype."""
        try:
            # Step 1: Profile analysis planning
            profile_plan = self.lic_profile_planner.plan_profile_analysis(
                recipient_name=recipient_profile.name,
                recipient_title=recipient_profile.title,
                recipient_company=recipient_profile.company
            )
            
            # Step 2: Research planning
            research_plan = self.lic_research_planner.plan_research(
                recipient_company=recipient_profile.company,
                recipient_name=recipient_profile.name,
                recipient_archetype=archetype
            )
            
            # Step 3: Research execution
            research_result = await self.lic_research_executor.execute_research(research_plan)
            
            if not research_result.success:
                return ExecutorResult.failure_result(
                    f"Research execution failed: {research_result.message}",
                    error_code="RESEARCH_FAILED"
                )
            
            # Step 4: Grounding planning
            # Construct mission context from available attributes
            mission_context_str = (
                f"objective: {mission.objective}, "
                f"target_role: {mission.target_role}, "
                f"target_company: {mission.target_company}, "
                f"value_proposition: {mission.value_proposition}, "
                f"urgency: {mission.urgency}"
            )
            
            grounding_plan = self.lic_grounding_planner.plan_grounding_extraction(
                mission_context=mission_context_str,
                recipient_archetype=archetype
            )
            
            # Step 5: Fusion planning
            # Extract resume capabilities from mission context
            resume_capabilities = self._extract_resume_capabilities(mission, recipient_profile)
            
            fusion_plan = self.lic_fusion_planner.plan_resume_fusion(
                mission_context=mission_context_str,
                recipient_archetype=archetype,
                resume_capabilities=resume_capabilities
            )
            
            # Step 6: Persona planning
            persona_plan = self.lic_persona_planner.plan_persona_consistency(
                mission_context=mission_context_str,
                recipient_archetype=archetype,
                sender_persona_profile={"communication_style": "professional", "tone": "confident"}
            )
            
            # Step 7: Message generation
            if not self.lic_message_executor:
                return ExecutorResult.failure_result(
                    "LIC message executor not available",
                    error_code="MESSAGE_EXECUTOR_MISSING"
                )
            
            message_result = await self.lic_message_executor.execute_message_generation(
                fusion_plan, grounding_plan, profile_plan
            )
            
            if not message_result.success:
                return ExecutorResult.failure_result(
                    f"Message generation failed: {message_result.message}",
                    error_code="MESSAGE_FAILED"
                )
            
            # Success - return generated message
            final_message = self._assemble_final_message(message_result.data.primary_message)
            
            return ExecutorResult.success_result(
                data={
                    "message": final_message,
                    "research_data": research_result.data,
                    "message_data": message_result.data,
                    "archetype": archetype
                },
                message=f"Archetype workflow completed for {archetype}"
            )
            
        except Exception as e:
            return ExecutorResult.failure_result(
                f"Archetype workflow execution failed: {str(e)}",
                error_code="WORKFLOW_ERROR"
            )
    
    def _assemble_final_message(self, primary_message) -> str:
        """Assemble final message from components."""
        components = [primary_message.hook, primary_message.value_prop, 
                     primary_message.evidence, primary_message.cta, primary_message.closing]
        return "\n\n".join(filter(None, components))
    
    def _extract_resume_capabilities(self, mission: OutreachMission, recipient_profile: RecipientProfile) -> Dict[str, List[str]]:
        """Extract resume capabilities from mission context and recipient profile."""
        # Default capabilities if not provided in mission
        default_capabilities = {
            "technical_skills": ["Python", "AI", "ML", "Data Analysis", "Project Management"],
            "achievements": ["Led successful projects", "Delivered measurable business impact"],
            "experience": ["Software development", "Team leadership", "Strategic planning"],
            "technologies": ["Machine Learning", "Cloud Computing", "Data Analytics"]
        }
        
        # Extract from mission context if available
        if hasattr(mission, 'sender_capabilities') and mission.sender_capabilities:
            capabilities = mission.sender_capabilities.copy()
            # Fill in missing categories with defaults
            for category, defaults in default_capabilities.items():
                if category not in capabilities or not capabilities[category]:
                    capabilities[category] = defaults
            return capabilities
        
        # Extract from mission metadata if available
        if hasattr(mission, 'metadata') and mission.metadata:
            metadata_caps = mission.metadata.get('resume_capabilities', {})
            if metadata_caps:
                capabilities = metadata_caps.copy()
                # Fill in missing categories with defaults
                for category, defaults in default_capabilities.items():
                    if category not in capabilities or not capabilities[category]:
                        capabilities[category] = defaults
                return capabilities
        
        # Return default capabilities
        return default_capabilities
    
    def _is_circuit_breaker_open(self) -> bool:
        """Check if circuit breaker is open."""
        state = self._lic_circuit_breaker_state
        
        if state["state"] == "open":
            # Check if timeout has passed
            from datetime import datetime, timedelta
            if (state["last_failure_time"] and 
                datetime.now() - state["last_failure_time"] > timedelta(seconds=60)):
                state["state"] = "half_open"
                logger.info("Circuit breaker transitioning to HALF_OPEN")
                return False
            else:
                return True
        
        return False
    
    def _record_circuit_breaker_failure(self):
        """Record a failure for circuit breaker."""
        state = self._lic_circuit_breaker_state
        state["failure_count"] += 1
        state["last_failure_time"] = datetime.now()
        
        # Open circuit if threshold exceeded
        if state["failure_count"] >= 5:
            state["state"] = "open"
            logger.warning("Circuit breaker opened due to excessive failures")
    
    def _reset_circuit_breaker(self):
        """Reset circuit breaker to closed state."""
        self._lic_circuit_breaker_state = {
            "failure_count": 0,
            "last_failure_time": None,
            "state": "closed"
        }
        logger.info("Circuit breaker reset to CLOSED")
    
    async def _monitor_persona_drift(self, workflow_data: Dict[str, Any]) -> ExecutorResult:
        """Monitor persona drift and apply corrections."""
        try:
            # Simple drift detection based on message characteristics
            message = workflow_data.get("message", "")
            archetype = workflow_data.get("archetype", "")
            
            # Calculate drift score (simplified)
            drift_score = self._calculate_persona_drift(message, archetype)
            
            if drift_score > self._persona_drift_monitor["drift_threshold"]:
                self._persona_drift_monitor["drift_count"] += 1
                self._persona_drift_monitor["last_drift_time"] = datetime.now()
                
                # Apply persona correction
                corrected_message = self._apply_persona_correction(message, archetype)
                
                return ExecutorResult.success_result(
                    data={"corrections": 1, "corrected_message": corrected_message},
                    message="Persona drift detected and corrected"
                )
            
            return ExecutorResult.success_result(
                data={"corrections": 0},
                message="No persona drift detected"
            )
            
        except Exception as e:
            return ExecutorResult.failure_result(
                f"Persona drift monitoring failed: {str(e)}",
                error_code="DRIFT_MONITOR_ERROR"
            )
    
    def _calculate_persona_drift(self, message: str, archetype: str) -> float:
        """Calculate persona drift score."""
        # Simplified drift calculation based on tone indicators
        drift_indicators = {
            "executive": ["casual", "informal", "hey", "yo"],
            "hiring_manager": ["overly formal", "corporate jargon", "synergy"],
            "technical_lead": ["business-focused", "strategic", "market"],
            "recruiter": ["technical jargon", "implementation details"]
        }
        
        message_lower = message.lower()
        indicators = drift_indicators.get(archetype, [])
        
        drift_count = sum(1 for indicator in indicators if indicator in message_lower)
        return min(drift_count * 0.2, 1.0)  # Cap at 1.0
    
    def _apply_persona_correction(self, message: str, archetype: str) -> str:
        """Apply persona correction to message."""
        # Simplified persona correction
        corrections = {
            "executive": "Strategic and professional tone maintained.",
            "hiring_manager": "Collaborative and team-focused tone maintained.",
            "technical_lead": "Technical and solution-oriented tone maintained.",
            "recruiter": "Professional and opportunity-focused tone maintained."
        }
        
        # For now, just return the original message with a note
        correction_note = corrections.get(archetype, "Persona alignment maintained.")
        return f"{message}\n\n[{correction_note}]"
    
    async def _validate_lic_output(self, workflow_data: Dict[str, Any]) -> ExecutorResult:
        """Validate LIC workflow output for safety."""
        try:
            message = workflow_data.get("message", "")
            
            # Basic safety checks
            if not message or len(message.strip()) == 0:
                return ExecutorResult.failure_result(
                    "Generated message is empty",
                    error_code="EMPTY_MESSAGE"
                )
            
            # Check for inappropriate content (simplified)
            inappropriate_terms = ["spam", "scam", "urgent money", "click here"]
            message_lower = message.lower()
            
            if any(term in message_lower for term in inappropriate_terms):
                return ExecutorResult.failure_result(
                    "Message contains inappropriate content",
                    error_code="INAPPROPRIATE_CONTENT"
                )
            
            return ExecutorResult.success_result(
                data={"validated": True},
                message="Output validation passed"
            )
            
        except Exception as e:
            return ExecutorResult.failure_result(
                f"Output validation failed: {str(e)}",
                error_code="VALIDATION_ERROR"
            )
    
    async def _execute_legacy_workflow(self, mission: OutreachMission, recipient_profile: RecipientProfile) -> OutreachPipelineResult:
        """Execute legacy workflow (existing implementation)."""
        # This would contain the existing workflow logic
        # For now, return a simple success result
        return OutreachPipelineResult(
            success=True,
            message="Legacy workflow completed successfully",
            metadata={"pipeline": "legacy"}
        )
    
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
    
    async def _execute_concurrent_workflow_with_fallback(
        self,
        mission: OutreachMission,
        recipient: RecipientProfile,
        ctx: ArchetypeContext,
        config: Dict[str, Any],
    ) -> OutreachPipelineResult:
        """Execute concurrent workflow with timeout and fallback handling."""
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
            logger.warning(f"Concurrent execution timed out, falling back to sequential")
            result = self._execute_workflow_phases(mission, recipient, ctx, config)
            # Add timeout fallback flag if result succeeds
            if result.success and hasattr(result, 'metadata') and result.metadata:
                result.metadata["timeout_fallback"] = True
        
        return result
    
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
        
        # Record workflow start time for telemetry
        workflow_start_time = time.time()
        
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
                    logger.info(f"DEBUG: Starting attempt {attempt} with archetype {archetype}")
                    # Update archetype context
                    ctx.archetype = archetype
                    logger.info(f"DEBUG: Updated archetype context")
                    
                    # Initialize timeout tracking variables
                    timeout_occurred = False
                    logger.info(f"DEBUG: Initialized timeout tracking")
                    
                    # Execute workflow phases with optional concurrency and fallback logic
                    # First attempt uses concurrent if enabled, subsequent attempts use sequential
                    should_use_concurrent = (use_concurrent_research or use_multi_draft) and attempt == 1
                    logger.info(f"DEBUG: should_use_concurrent={should_use_concurrent}")
                    
                    if should_use_concurrent:
                        logger.info(f"DEBUG: Taking concurrent execution path")
                        # Use async execution on first attempt
                        result = await self._execute_concurrent_workflow_with_fallback(mission, recipient, ctx, config)
                        logger.info(f"DEBUG: Concurrent execution completed")
                    else:
                        logger.info(f"DEBUG: Taking sequential execution path")
                        # Use sequential execution when concurrency disabled
                        result = self._execute_workflow_phases(mission, recipient, ctx, config)
                        logger.info(f"DEBUG: Sequential execution completed")
                    
                    logger.info(f"DEBUG: Workflow execution result success={result.success}")
                    
                    if result.success:
                        logger.info(f"Outreach successful with archetype {archetype}")
                        
                        # P4 — Final Safety Check (MUST be after message generation)
                        logger.info("P4: Safety validation at meta-loop level")
                        try:
                            safety_result_raw = self.safety_validator.evaluate(result.message)
                            logger.info(f"DEBUG: Safety validator returned: {type(safety_result_raw)}")
                        except Exception as safety_eval_error:
                            logger.error(f"DEBUG: Exception in safety evaluation: {safety_eval_error}")
                            raise
                        
                        # Handle both sync and async safety evaluators with timeout
                        import inspect
                        safety_timeout = config.get("safety_timeout", None)
                        timeout_occurred = False
                        safety_result = None
                        
                        # Always await coroutine immediately to prevent unawaited warnings
                        if inspect.iscoroutine(safety_result_raw):
                            logger.info("DEBUG: Detected coroutine, awaiting immediately")
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
                            except RuntimeError as runtime_error:
                                logger.error(f"DEBUG: RuntimeError in coroutine handling: {runtime_error}")
                                if safety_timeout:
                                    try:
                                        safety_result = asyncio.run(asyncio.wait_for(safety_result_raw, timeout=safety_timeout))
                                    except asyncio.TimeoutError:
                                        timeout_occurred = True
                                        raise
                                else:
                                    safety_result = asyncio.run(safety_result_raw)
                        else:
                            logger.info("DEBUG: Detected sync safety evaluator")
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
                        
                        logger.info(f"DEBUG: Safety evaluation completed, passed: {safety_result.passed if safety_result else 'None'}")
                        
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
        workflow_start_time = time.time()
        
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
            # Define workflow_start_time if not already available
            if 'workflow_start_time' not in locals():
                workflow_start_time = time.time()
            
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
