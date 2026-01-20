#!/usr/bin/env python3
"""
AppWorkflowOrchestratorAgent - Unified Application Workflow Orchestration

Phase 1 Consolidation: Merges functionality from:
- LicWorkflowOrchestratorAgent (LIC outreach workflows)
- OutreachPhase5OrchestratorAgent (Phase 5 outreach)
- Phase4OrchestratorAgent (Phase 4 resume)
- Phase6OrchestratorAgent (Phase 6 resume)
- Phase7OrchestratorAgent (Phase 7 resume)

Features:
- Configuration-driven state machine for phase transitions
- Dependency gate validation between phases
- Support for both LIC (outreach) and RG (resume) workflows
- Phase-specific execution with validation
"""
from __future__ import annotations

import logging
import warnings
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Set, Type

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L2_execution.mcp.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin
from agentic_core.utils.core_extensions.timeout_decorator import timeout

Logger = logging.getLogger(__name__)


class WorkflowPhase(Enum):
    """Workflow phases for LIC and RG applications."""
    # Common phases
    INIT = auto()
    VALIDATION = auto()
    COMPLETE = auto()
    ERROR = auto()
    
    # LIC (Outreach) phases
    LIC_PHASE_1_PROFILE = auto()
    LIC_PHASE_2_RESEARCH = auto()
    LIC_PHASE_3_GROUNDING = auto()
    LIC_PHASE_4_ROUTING = auto()
    LIC_PHASE_5_GENERATION = auto()
    LIC_PHASE_6_VALIDATION = auto()
    LIC_PHASE_7_GATE = auto()
    LIC_PHASE_8_QA = auto()
    
    # RG (Resume) phases
    RG_PHASE_1_INTAKE = auto()
    RG_PHASE_2_ANALYSIS = auto()
    RG_PHASE_3_STRATEGY = auto()
    RG_PHASE_4_GENERATION = auto()
    RG_PHASE_5_REFINEMENT = auto()
    RG_PHASE_6_VALIDATION = auto()
    RG_PHASE_7_FINALIZATION = auto()


class WorkflowType(Enum):
    """Type of workflow."""
    LIC = "lic"  # LinkedIn Outreach
    RG = "rg"    # Resume Generation


@dataclass
class PhaseConfig:
    """Configuration for a workflow phase."""
    phase: WorkflowPhase
    name: str
    description: str
    required_inputs: List[str] = field(default_factory=list)
    produces_outputs: List[str] = field(default_factory=list)
    dependencies: List[WorkflowPhase] = field(default_factory=list)
    timeout_seconds: int = 300
    can_skip: bool = False
    retry_on_failure: bool = True
    max_retries: int = 2


@dataclass
class PhaseResult:
    """Result of a phase execution."""
    phase: WorkflowPhase
    success: bool
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    execution_time: float = 0.0
    skipped: bool = False
    retries_used: int = 0


@dataclass
class WorkflowState:
    """Current state of a workflow execution."""
    workflow_id: str
    workflow_type: WorkflowType
    current_phase: WorkflowPhase
    completed_phases: Set[WorkflowPhase] = field(default_factory=set)
    phase_results: Dict[WorkflowPhase, PhaseResult] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    
    @property
    def is_complete(self) -> bool:
        """Check if workflow is complete."""
        return self.current_phase in (WorkflowPhase.COMPLETE, WorkflowPhase.ERROR)
    
    @property
    def is_error(self) -> bool:
        """Check if workflow ended in error."""
        return self.current_phase == WorkflowPhase.ERROR


# Default phase configurations
LIC_PHASE_CONFIGS: List[PhaseConfig] = [
    PhaseConfig(
        phase=WorkflowPhase.LIC_PHASE_1_PROFILE,
        name="Profile Analysis",
        description="Analyze recipient profile",
        required_inputs=["recipient_id"],
        produces_outputs=["profile_data", "archetype"],
    ),
    PhaseConfig(
        phase=WorkflowPhase.LIC_PHASE_2_RESEARCH,
        name="Research",
        description="Research recipient and company",
        required_inputs=["profile_data"],
        produces_outputs=["research_data", "talking_points"],
        dependencies=[WorkflowPhase.LIC_PHASE_1_PROFILE],
    ),
    PhaseConfig(
        phase=WorkflowPhase.LIC_PHASE_3_GROUNDING,
        name="Sender Grounding",
        description="Ground message in sender context",
        required_inputs=["research_data"],
        produces_outputs=["grounding_context"],
        dependencies=[WorkflowPhase.LIC_PHASE_2_RESEARCH],
    ),
    PhaseConfig(
        phase=WorkflowPhase.LIC_PHASE_4_ROUTING,
        name="Route Selection",
        description="Select optimal delivery route",
        required_inputs=["archetype", "grounding_context"],
        produces_outputs=["selected_route", "route_config"],
        dependencies=[WorkflowPhase.LIC_PHASE_3_GROUNDING],
    ),
    PhaseConfig(
        phase=WorkflowPhase.LIC_PHASE_5_GENERATION,
        name="Message Generation",
        description="Generate personalized message",
        required_inputs=["route_config", "talking_points", "grounding_context"],
        produces_outputs=["draft_message"],
        dependencies=[WorkflowPhase.LIC_PHASE_4_ROUTING],
    ),
    PhaseConfig(
        phase=WorkflowPhase.LIC_PHASE_6_VALIDATION,
        name="Message Validation",
        description="Validate message quality and compliance",
        required_inputs=["draft_message"],
        produces_outputs=["validation_result", "validated_message"],
        dependencies=[WorkflowPhase.LIC_PHASE_5_GENERATION],
    ),
    PhaseConfig(
        phase=WorkflowPhase.LIC_PHASE_7_GATE,
        name="Gate Decision",
        description="Final gate decision for sending",
        required_inputs=["validation_result", "validated_message"],
        produces_outputs=["gate_decision", "final_message"],
        dependencies=[WorkflowPhase.LIC_PHASE_6_VALIDATION],
    ),
    PhaseConfig(
        phase=WorkflowPhase.LIC_PHASE_8_QA,
        name="QA Report",
        description="Generate QA report",
        required_inputs=["gate_decision", "final_message"],
        produces_outputs=["qa_report"],
        dependencies=[WorkflowPhase.LIC_PHASE_7_GATE],
        can_skip=True,
    ),
]

RG_PHASE_CONFIGS: List[PhaseConfig] = [
    PhaseConfig(
        phase=WorkflowPhase.RG_PHASE_1_INTAKE,
        name="Intake",
        description="Intake and parse resume data",
        required_inputs=["resume_data"],
        produces_outputs=["parsed_resume", "job_target"],
    ),
    PhaseConfig(
        phase=WorkflowPhase.RG_PHASE_2_ANALYSIS,
        name="Analysis",
        description="Analyze resume against job requirements",
        required_inputs=["parsed_resume", "job_target"],
        produces_outputs=["gap_analysis", "strength_map"],
        dependencies=[WorkflowPhase.RG_PHASE_1_INTAKE],
    ),
    PhaseConfig(
        phase=WorkflowPhase.RG_PHASE_3_STRATEGY,
        name="Strategy",
        description="Develop optimization strategy",
        required_inputs=["gap_analysis", "strength_map"],
        produces_outputs=["optimization_strategy"],
        dependencies=[WorkflowPhase.RG_PHASE_2_ANALYSIS],
    ),
    PhaseConfig(
        phase=WorkflowPhase.RG_PHASE_4_GENERATION,
        name="Generation",
        description="Generate optimized resume sections",
        required_inputs=["optimization_strategy", "parsed_resume"],
        produces_outputs=["draft_sections"],
        dependencies=[WorkflowPhase.RG_PHASE_3_STRATEGY],
    ),
    PhaseConfig(
        phase=WorkflowPhase.RG_PHASE_5_REFINEMENT,
        name="Refinement",
        description="Refine and polish content",
        required_inputs=["draft_sections"],
        produces_outputs=["refined_sections"],
        dependencies=[WorkflowPhase.RG_PHASE_4_GENERATION],
    ),
    PhaseConfig(
        phase=WorkflowPhase.RG_PHASE_6_VALIDATION,
        name="Validation",
        description="Validate resume quality",
        required_inputs=["refined_sections"],
        produces_outputs=["validation_result", "validated_resume"],
        dependencies=[WorkflowPhase.RG_PHASE_5_REFINEMENT],
    ),
    PhaseConfig(
        phase=WorkflowPhase.RG_PHASE_7_FINALIZATION,
        name="Finalization",
        description="Finalize and format resume",
        required_inputs=["validated_resume"],
        produces_outputs=["final_resume", "formats"],
        dependencies=[WorkflowPhase.RG_PHASE_6_VALIDATION],
    ),
]


@dataclass
class AppWorkflowOrchestratorAgent(SubatomicTestingMixin, HealerMixin, MCPHardenedMixin):
    """
    Unified application-layer orchestrator for LIC and RG workflows.
    
    Consolidates:
    - LicWorkflowOrchestratorAgent
    - OutreachPhase5OrchestratorAgent
    - Phase4/6/7OrchestratorAgent
    
    Features:
    - Configuration-driven state machine
    - Dependency gate validation
    - Phase-specific execution
    
    Usage:
        agent = AppWorkflowOrchestratorAgent(workflow_type=WorkflowType.LIC)
        state = await agent.execute_workflow({"recipient_id": "123"})
    """
    
    workflow_type: WorkflowType = WorkflowType.LIC
    custom_phase_configs: Optional[List[PhaseConfig]] = None
    phase_handlers: Dict[WorkflowPhase, Callable] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Initialize the workflow orchestrator."""
        # Load phase configs based on workflow type
        if self.custom_phase_configs:
            self._phase_configs = {pc.phase: pc for pc in self.custom_phase_configs}
        elif self.workflow_type == WorkflowType.LIC:
            self._phase_configs = {pc.phase: pc for pc in LIC_PHASE_CONFIGS}
        else:
            self._phase_configs = {pc.phase: pc for pc in RG_PHASE_CONFIGS}
        
        # Build phase order
        self._phase_order = self._build_phase_order()
        Logger.info(f"AppWorkflowOrchestratorAgent initialized for {self.workflow_type.value}")
    
    def _build_phase_order(self) -> List[WorkflowPhase]:
        """Build execution order based on dependencies."""
        # Simple topological sort
        order = []
        remaining = set(self._phase_configs.keys())
        
        while remaining:
            # Find phases with all dependencies satisfied
            ready = []
            for phase in remaining:
                config = self._phase_configs[phase]
                if all(dep in order or dep not in self._phase_configs for dep in config.dependencies):
                    ready.append(phase)
            
            if not ready:
                # Circular dependency or missing dependency
                Logger.warning(f"Could not resolve dependencies for: {remaining}")
                order.extend(remaining)
                break
            
            # Add ready phases in enum order for determinism
            ready.sort(key=lambda p: p.value)
            order.extend(ready)
            remaining -= set(ready)
        
        return order
    
    def register_phase_handler(
        self,
        phase: WorkflowPhase,
        handler: Callable[[WorkflowState, PhaseConfig], PhaseResult],
    ) -> None:
        """Register a custom handler for a phase."""
        self.phase_handlers[phase] = handler
        Logger.info(f"Registered handler for phase {phase.name}")
    
    def validate_phase_dependencies(
        self,
        phase: WorkflowPhase,
        state: WorkflowState,
    ) -> tuple[bool, Optional[str]]:
        """
        Validate that all dependencies for a phase are satisfied.
        
        Returns:
            (is_valid, error_message)
        """
        config = self._phase_configs.get(phase)
        if not config:
            return False, f"Unknown phase: {phase}"
        
        # Check phase dependencies
        for dep in config.dependencies:
            if dep not in state.completed_phases:
                return False, f"Dependency not met: {dep.name} must complete before {phase.name}"
            
            # Check if dependency succeeded
            dep_result = state.phase_results.get(dep)
            if dep_result and not dep_result.success and not dep_result.skipped:
                return False, f"Dependency failed: {dep.name}"
        
        # Check required inputs
        for required_input in config.required_inputs:
            if required_input not in state.context:
                return False, f"Missing required input: {required_input}"
        
        return True, None
    
    async def _execute_phase(
        self,
        phase: WorkflowPhase,
        state: WorkflowState,
    ) -> PhaseResult:
        """Execute a single phase."""
        config = self._phase_configs[phase]
        start_time = datetime.now()
        
        Logger.info(f"Executing phase {config.name} ({phase.name})")
        
        # Validate dependencies
        is_valid, error = self.validate_phase_dependencies(phase, state)
        if not is_valid:
            Logger.error(f"Phase {phase.name} dependency validation failed: {error}")
            return PhaseResult(
                phase=phase,
                success=False,
                error=error,
            )
        
        # Check for custom handler
        if phase in self.phase_handlers:
            try:
                result = await self.phase_handlers[phase](state, config)
                result.execution_time = (datetime.now() - start_time).total_seconds()
                return result
            except Exception as e:
                Logger.error(f"Phase {phase.name} handler failed: {e}")
                return PhaseResult(
                    phase=phase,
                    success=False,
                    error=str(e),
                    execution_time=(datetime.now() - start_time).total_seconds(),
                )
        
        # Default execution (mock for now - real handlers should be registered)
        Logger.info(f"Phase {config.name}: Using default handler")
        
        # Simulate phase execution
        result_data = {}
        for output in config.produces_outputs:
            result_data[output] = f"{output}_from_{phase.name}"
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return PhaseResult(
            phase=phase,
            success=True,
            data=result_data,
            execution_time=execution_time,
        )
    
    async def execute_workflow(
        self,
        initial_context: Dict[str, Any],
        workflow_id: Optional[str] = None,
    ) -> WorkflowState:
        """
        Execute the complete workflow.
        
        Args:
            initial_context: Initial context/inputs for the workflow
            workflow_id: Optional workflow identifier
            
        Returns:
            Final workflow state
        """
        import uuid
        
        state = WorkflowState(
            workflow_id=workflow_id or str(uuid.uuid4()),
            workflow_type=self.workflow_type,
            current_phase=WorkflowPhase.INIT,
            context=initial_context.copy(),
        )
        
        Logger.info(f"Starting {self.workflow_type.value} workflow {state.workflow_id}")
        
        try:
            for phase in self._phase_order:
                state.current_phase = phase
                config = self._phase_configs[phase]
                
                # Execute phase with retry
                result = None
                for attempt in range(config.max_retries + 1):
                    result = await self._execute_phase(phase, state)
                    
                    if result.success:
                        break
                    
                    if not config.retry_on_failure:
                        break
                    
                    if attempt < config.max_retries:
                        Logger.info(f"Retrying phase {phase.name} (attempt {attempt + 2})")
                        result.retries_used = attempt + 1
                
                # Store result
                state.phase_results[phase] = result
                
                if result.success:
                    state.completed_phases.add(phase)
                    # Add outputs to context
                    state.context.update(result.data)
                elif config.can_skip:
                    Logger.warning(f"Skipping failed phase {phase.name}")
                    result.skipped = True
                    state.completed_phases.add(phase)
                else:
                    # Phase failed and cannot skip
                    state.current_phase = WorkflowPhase.ERROR
                    state.error = result.error
                    Logger.error(f"Workflow failed at phase {phase.name}: {result.error}")
                    break
            
            if state.current_phase != WorkflowPhase.ERROR:
                state.current_phase = WorkflowPhase.COMPLETE
            
        except Exception as e:
            state.current_phase = WorkflowPhase.ERROR
            state.error = str(e)
            Logger.error(f"Workflow execution error: {e}")
        
        state.completed_at = datetime.now()
        Logger.info(f"Workflow {state.workflow_id} completed with status {state.current_phase.name}")
        
        return state
    
    def get_phase_config(self, phase: WorkflowPhase) -> Optional[PhaseConfig]:
        """Get configuration for a phase."""
        return self._phase_configs.get(phase)
    
    def get_workflow_phases(self) -> List[WorkflowPhase]:
        """Get ordered list of phases for this workflow."""
        return self._phase_order.copy()
    
    @timeout(300)
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: Optional[set] = None,
    ) -> Dict[str, int]:
        """Apps orchestration agent - operational healing."""
        if _call_path is None:
            _call_path = set()
        
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        
        _call_path.add(agent_name)
        try:
            Logger.info(f"[{agent_name}] Apps orchestration healing")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)


# =============================================================================
# BACKWARD COMPATIBILITY FACTORY METHODS
# =============================================================================

def create_legacy_lic_workflow_orchestrator(**kwargs: Any) -> AppWorkflowOrchestratorAgent:
    """
    Factory for backward compatibility with LicWorkflowOrchestratorAgent.
    
    DEPRECATED: Use AppWorkflowOrchestratorAgent directly.
    """
    warnings.warn(
        "LicWorkflowOrchestratorAgent is deprecated. Use AppWorkflowOrchestratorAgent instead. "
        "This factory will be removed after 2026-02-19.",
        DeprecationWarning,
        stacklevel=2,
    )
    return AppWorkflowOrchestratorAgent(workflow_type=WorkflowType.LIC, **kwargs)


def create_legacy_phase_orchestrator(
    phase_number: int,
    workflow_type: str = "rg",
    **kwargs: Any,
) -> AppWorkflowOrchestratorAgent:
    """
    Factory for backward compatibility with Phase4/6/7OrchestratorAgent.
    
    DEPRECATED: Use AppWorkflowOrchestratorAgent directly.
    """
    warnings.warn(
        f"Phase{phase_number}OrchestratorAgent is deprecated. Use AppWorkflowOrchestratorAgent instead. "
        "This factory will be removed after 2026-02-19.",
        DeprecationWarning,
        stacklevel=2,
    )
    wf_type = WorkflowType.LIC if workflow_type.lower() == "lic" else WorkflowType.RG
    return AppWorkflowOrchestratorAgent(workflow_type=wf_type, **kwargs)


def create_legacy_outreach_phase5_orchestrator(**kwargs: Any) -> AppWorkflowOrchestratorAgent:
    """
    Factory for backward compatibility with OutreachPhase5OrchestratorAgent.
    
    DEPRECATED: Use AppWorkflowOrchestratorAgent directly.
    """
    warnings.warn(
        "OutreachPhase5OrchestratorAgent is deprecated. Use AppWorkflowOrchestratorAgent instead. "
        "This factory will be removed after 2026-02-19.",
        DeprecationWarning,
        stacklevel=2,
    )
    return AppWorkflowOrchestratorAgent(workflow_type=WorkflowType.LIC, **kwargs)
