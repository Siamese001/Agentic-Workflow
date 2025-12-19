"""
L5 Autonomous Orchestrator - Main Class and Convergence Loop
"""

import copy
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

# Import L5+ autonomy components
try:
    from apps_shared.intervention_server import get_intervention_server
    from apps_shared.reflection_agent import ReflectionDecision, create_reflection_agent
    from apps_shared.signal_bus import SignalType, get_signal_bus
    AUTONOMY_COMPONENTS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"L5+ autonomy components not available: {e}")
    AUTONOMY_COMPONENTS_AVAILABLE = False

from apps_rg.L3_orchestration.l5_orchestrator.types import (
    CycleState,
    ExecutionPhase,
    WorkflowSnapshot,
)

from . import intervention_handler, phase_executor, reflection_handler, snapshot_manager


class L5AutonomousOrchestrator:
    """
    L5+ Autonomous Orchestrator implementing Canon Validator patterns.
    
    Key Features:
    1. Convergence Loop: Iterates until quality converges or max cycles reached
    2. Signal System: Blackboard pattern for inter-agent communication
    3. Human-in-the-Loop: Intervention server for high-risk decisions
    4. Reflection: Self-critique after each cycle
    5. Blast Radius: Dependency impact analysis
    6. Rollback: Restore previous state on regression
    7. Few-Shot Injection: Enhanced prompts with examples
    """
    
    # Default configuration
    DEFAULT_MAX_CYCLES = 5
    DEFAULT_QUALITY_THRESHOLD = 0.7
    DEFAULT_HIGH_RISK_MODIFIED_THRESHOLD = 3
    
    def __init__(
        self,
        workflow_id: str,
        max_cycles: int = DEFAULT_MAX_CYCLES,
        quality_threshold: float = DEFAULT_QUALITY_THRESHOLD,
        enable_intervention: bool = True,
        intervention_port: int = 8080,
        output_dir: str = "./pipeline_runs",
    ) -> None:
        """Initialize the L5+ autonomous orchestrator."""
        self.workflow_id = workflow_id
        self.max_cycles = max_cycles
        self.quality_threshold = quality_threshold
        self.enable_intervention = enable_intervention
        self.intervention_port = intervention_port
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize L5+ components
        if AUTONOMY_COMPONENTS_AVAILABLE:
            self.signal_bus = get_signal_bus()
            self.reflection_agent = create_reflection_agent(
                min_quality_threshold=quality_threshold
            )
            self.intervention_server = get_intervention_server(
                port=intervention_port
            ) if enable_intervention else None
        else:
            self.signal_bus = None
            self.reflection_agent = None
            self.intervention_server = None
        
        # State management
        self.current_cycle = 0
        self.cycle_history: List[CycleState] = []
        self.snapshots: List[WorkflowSnapshot] = []
        self.context: Dict[str, Any] = {}
        self.outputs: Dict[str, Any] = {}
        
        # Dependency tracking for blast radius
        self.dependency_map: Dict[str, set] = {
            "executive_summary": {"headline", "skills", "experience_bullets"},
            "experience_bullets": {"executive_summary", "skills"},
            "skills": {"experience_bullets", "executive_summary"},
            "headline": {"executive_summary"},
        }
        
        # Execution phases (Canon Validator pattern)
        self.phases = self._define_phases()
        
        # Convergence tracking
        self.converged = False
        self.convergence_reason = ""
        
        logger.info(
            f"L5AutonomousOrchestrator initialized: workflow={workflow_id}, "
            f"max_cycles={max_cycles}, quality_threshold={quality_threshold}"
        )
    
    def _define_phases(self) -> List[ExecutionPhase]:
        """Define execution phases matching Canon Validator pattern."""
        return [
            ExecutionPhase(
                name="validation",
                agents=["input_validator", "schema_validator"],
                execution_mode="sequential",
                is_hard_gate=True,
            ),
            ExecutionPhase(
                name="research",
                agents=["company_researcher", "role_analyzer"],
                execution_mode="parallel",
            ),
            ExecutionPhase(
                name="generation",
                agents=["summary_generator", "bullet_generator", "skills_extractor"],
                execution_mode="sequential",
            ),
            ExecutionPhase(
                name="quality",
                agents=["quality_critic", "metric_validator", "consistency_checker"],
                execution_mode="parallel",
            ),
            ExecutionPhase(
                name="refinement",
                agents=["tone_adjuster", "length_optimizer"],
                execution_mode="sequential",
                condition=lambda ctx: ctx.get("needs_refinement", False),
            ),
        ]
    
    async def execute_with_convergence(
        self,
        initial_context: Dict[str, Any],
        agents: Dict[str, Callable],
    ) -> Dict[str, Any]:
        """Execute workflow with convergence loop (Canon Validator pattern)."""
        logger.info(f"Starting L5+ autonomous execution: {self.workflow_id}")
        
        self.context = copy.deepcopy(initial_context)
        self.outputs = {}
        
        # Start intervention server if enabled
        if self.intervention_server and self.enable_intervention:
            await self.intervention_server.start_server()
        
        try:
            # Main convergence loop
            for cycle in range(self.max_cycles):
                self.current_cycle = cycle + 1
                
                logger.info(f"\n{'='*60}")
                logger.info(f"CONVERGENCE CYCLE {self.current_cycle}/{self.max_cycles}")
                logger.info(f"{'='*60}")
                
                # Initialize cycle state
                cycle_state = CycleState(cycle=self.current_cycle)
                
                # Clear signals for new cycle
                if self.signal_bus:
                    await self.signal_bus.clear_cycle()
                
                # Take snapshot for potential rollback
                snapshot_manager.take_snapshot(self)
                
                # Execute all phases
                phase_results = await phase_executor.execute_all_phases(
                    self, agents, cycle_state
                )
                
                # Check for critical failure
                if self.signal_bus and self.signal_bus.is_critical_state():
                    logger.error("Critical failure detected - aborting")
                    self.convergence_reason = "critical_failure"
                    break
                
                # Check for human intervention
                if await intervention_handler.check_intervention_required(
                    self, cycle_state
                ):
                    if self.signal_bus and self.signal_bus.has(SignalType.VETOED):
                        logger.warning("Human veto received - aborting")
                        self.convergence_reason = "human_veto"
                        break
                
                # Perform reflection
                reflection_result = await reflection_handler.perform_reflection(
                    self, cycle_state
                )
                
                # Handle reflection decision
                if reflection_result:
                    if reflection_result.decision == ReflectionDecision.CONVERGE_AND_COMMIT:
                        self.converged = True
                        self.convergence_reason = "quality_converged"
                        logger.info("✅ CONVERGED - Quality criteria met")
                        break
                    
                    elif reflection_result.decision == ReflectionDecision.ROLLBACK_LAST_CHANGE_AND_RETRY:
                        logger.warning("Rolling back to previous state")
                        snapshot_manager.rollback_to_snapshot(self)
                        if self.signal_bus:
                            await self.signal_bus.emit(
                                SignalType.ROLLBACK_EXECUTED,
                                "Rolled back due to regression",
                                source="L5Orchestrator"
                            )
                    
                    elif reflection_result.decision == ReflectionDecision.ESCALATE_TO_HUMAN_WITH_REPORT:
                        logger.warning("Escalating to human review")
                        await self._generate_escalation_report(cycle_state)
                        self.convergence_reason = "escalated_to_human"
                        break
                
                # Check for convergence (no modifications and good quality)
                if not cycle_state.modified_items and reflection_handler.check_quality_acceptable(self, cycle_state):
                    self.converged = True
                    self.convergence_reason = "stable_state"
                    logger.info("✅ CONVERGED - Stable state achieved")
                    break
                
                # Store cycle state
                cycle_state.end_time = datetime.utcnow()
                self.cycle_history.append(cycle_state)
                
                logger.info(f"Cycle {self.current_cycle} complete. Modified: {len(cycle_state.modified_items)}")
            
            else:
                # Max cycles reached
                logger.warning(f"Max cycles ({self.max_cycles}) reached without convergence")
                self.convergence_reason = "max_cycles_reached"
                await self._generate_escalation_report(self.cycle_history[-1] if self.cycle_history else None)
            
            # Generate final report
            return self._generate_final_results()
            
        finally:
            # Stop intervention server
            if self.intervention_server:
                await self.intervention_server.stop_server()
    
    async def _generate_escalation_report(self, cycle_state: Optional[CycleState]) -> None:
        """Generate escalation report for human review."""
        
        report_path = self.output_dir / f"escalation_{self.workflow_id}_{int(datetime.utcnow().timestamp())}.md"
        
        report = f"""# Escalation Report

**Workflow ID:** {self.workflow_id}
**Generated:** {datetime.utcnow().isoformat()}
**Cycles Completed:** {self.current_cycle}
**Convergence Status:** {self.convergence_reason}

## Summary

"""
        
        if cycle_state:
            report += f"""
- **Modified Items:** {len(cycle_state.modified_items)}
- **Average Quality:** {intervention_handler.get_average_quality(self, cycle_state):.2f}
- **Execution Log Entries:** {len(cycle_state.execution_log)}

## Quality Scores

"""
            for agent, score in cycle_state.quality_scores.items():
                report += f"- {agent}: {score:.2f}\n"
            
            report += "\n## Execution Log\n\n"
            for entry in cycle_state.execution_log[-10:]:
                status = "✅" if entry.get("success", True) else "❌"
                report += f"- {status} {entry['agent']}: {entry.get('duration_ms', 0):.0f}ms\n"
        
        if self.signal_bus:
            report += f"\n## Active Signals\n\n"
            for signal in self.signal_bus.signals:
                report += f"- {signal.value}\n"
        
        report += "\n## Recommendations\n\n"
        if cycle_state:
            for rec in intervention_handler.generate_recommendations(self, cycle_state):
                report += f"- {rec}\n"
        
        report_path.write_text(report)
        logger.info(f"Escalation report saved: {report_path}")
    
    def _generate_final_results(self) -> Dict[str, Any]:
        """Generate final execution results."""
        
        return {
            "workflow_id": self.workflow_id,
            "converged": self.converged,
            "convergence_reason": self.convergence_reason,
            "cycles_completed": self.current_cycle,
            "max_cycles": self.max_cycles,
            "outputs": self.outputs,
            "final_quality": reflection_handler.get_average_quality(
                self, self.cycle_history[-1]
            ) if self.cycle_history else None,
            "cycle_history": [
                {
                    "cycle": cs.cycle,
                    "modified_count": len(cs.modified_items),
                    "quality_scores": cs.quality_scores,
                    "duration_ms": (
                        (cs.end_time - cs.start_time).total_seconds() * 1000
                        if cs.end_time else None
                    ),
                }
                for cs in self.cycle_history
            ],
            "signals": (
                [s.value for s in self.signal_bus.signals]
                if self.signal_bus else []
            ),
            "reflection_summary": (
                self.reflection_agent.get_reflection_summary()
                if self.reflection_agent else None
            ),
        }
