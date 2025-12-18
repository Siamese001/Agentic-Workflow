"""
L5+ Autonomous Orchestrator for Resume Engine.

Implements full Canon Validator autonomy patterns:
- Convergence loop with max cycles
- Signal-based blackboard communication
- Human-in-the-loop intervention
- Reflection and self-critique
- Blast radius analysis
- Rollback on regression
- Few-shot injection

This orchestrator achieves parity with canon_validator_agentic.py autonomy level.
"""

import asyncio
import copy
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set

logger = logging.getLogger(__name__)

# Import L5+ autonomy components
try:
    from apps_shared.signal_bus import (
        SignalBus,
        SignalType,
        get_signal_bus,
    )
    from apps_shared.reflection_agent import (
        ReflectionAgent,
        ReflectionDecision,
        create_reflection_agent,
    )
    from apps_shared.intervention_server import (
        InterventionServer,
        InterventionContext,
        check_intervention_required,
        get_intervention_server,
    )
    from apps_shared.few_shot_library import FewShotLibrary
    AUTONOMY_COMPONENTS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"L5+ autonomy components not available: {e}")
    AUTONOMY_COMPONENTS_AVAILABLE = False


@dataclass
class ExecutionPhase:
    """Definition of an execution phase."""
    
    name: str
    agents: List[str]
    execution_mode: str = "sequential"  # sequential, parallel
    is_hard_gate: bool = False
    condition: Optional[Callable] = None


@dataclass
class CycleState:
    """State for a single convergence cycle."""
    
    cycle: int
    modified_items: Set[str] = field(default_factory=set)
    quality_scores: Dict[str, float] = field(default_factory=dict)
    execution_log: List[Dict[str, Any]] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None


@dataclass
class WorkflowSnapshot:
    """Snapshot of workflow state for rollback."""
    
    cycle: int
    context: Dict[str, Any]
    outputs: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)


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
    
    Canon Validator Pattern:
        max_cycles = 10
        for cycle in range(max_cycles):
            ctx.modified_files.clear()
            ctx.signals.clear()
            converged = await self._execute_all_phases()
            if converged:
                break
            if "CRITICAL_FAIL" in ctx.signals:
                break
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
        """
        Initialize the L5+ autonomous orchestrator.
        
        Args:
            workflow_id: Unique identifier for this workflow
            max_cycles: Maximum convergence cycles
            quality_threshold: Minimum acceptable quality score
            enable_intervention: Enable human-in-the-loop
            intervention_port: Port for intervention server
            output_dir: Directory for outputs and reports
        """
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
        self.dependency_map: Dict[str, Set[str]] = {
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
        """
        Execute workflow with convergence loop (Canon Validator pattern).
        
        Args:
            initial_context: Initial execution context
            agents: Dictionary of agent name -> async callable
            
        Returns:
            Final execution results
        """
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
                    self.signal_bus.clear_cycle()
                
                # Take snapshot for potential rollback
                self._take_snapshot()
                
                # Execute all phases
                phase_results = await self._execute_all_phases(agents, cycle_state)
                
                # Check for critical failure
                if self.signal_bus and self.signal_bus.is_critical_state():
                    logger.error("Critical failure detected - aborting")
                    self.convergence_reason = "critical_failure"
                    break
                
                # Check for human intervention
                if await self._check_intervention_required(cycle_state):
                    if self.signal_bus and self.signal_bus.has(SignalType.VETOED):
                        logger.warning("Human veto received - aborting")
                        self.convergence_reason = "human_veto"
                        break
                
                # Perform reflection
                reflection_result = await self._perform_reflection(cycle_state)
                
                # Handle reflection decision
                if reflection_result:
                    if reflection_result.decision == ReflectionDecision.CONVERGE_AND_COMMIT:
                        self.converged = True
                        self.convergence_reason = "quality_converged"
                        logger.info("✅ CONVERGED - Quality criteria met")
                        break
                    
                    elif reflection_result.decision == ReflectionDecision.ROLLBACK_LAST_CHANGE_AND_RETRY:
                        logger.warning("Rolling back to previous state")
                        self._rollback_to_snapshot()
                        if self.signal_bus:
                            self.signal_bus.emit(
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
                if not cycle_state.modified_items and self._check_quality_acceptable(cycle_state):
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
    
    async def _execute_all_phases(
        self,
        agents: Dict[str, Callable],
        cycle_state: CycleState,
    ) -> Dict[str, Any]:
        """Execute all phases in order."""
        
        results = {}
        
        for phase in self.phases:
            # Check phase condition
            if phase.condition and not phase.condition(self.context):
                logger.debug(f"Skipping phase {phase.name} - condition not met")
                continue
            
            logger.info(f"Executing phase: {phase.name}")
            
            try:
                if phase.execution_mode == "parallel":
                    phase_result = await self._execute_phase_parallel(
                        phase, agents, cycle_state
                    )
                else:
                    phase_result = await self._execute_phase_sequential(
                        phase, agents, cycle_state
                    )
                
                results[phase.name] = phase_result
                
                # Check for hard gate failure
                if phase.is_hard_gate and not phase_result.get("success", True):
                    logger.error(f"Hard gate {phase.name} failed - aborting")
                    if self.signal_bus:
                        self.signal_bus.signal_critical_failure(
                            f"Hard gate {phase.name} failed",
                            source="L5Orchestrator"
                        )
                    break
                    
            except Exception as e:
                logger.error(f"Phase {phase.name} failed: {e}")
                if self.signal_bus:
                    self.signal_bus.emit(
                        SignalType.VALIDATION_FAILURE,
                        f"Phase {phase.name} error: {e}",
                        source="L5Orchestrator",
                        severity="error"
                    )
                if phase.is_hard_gate:
                    break
        
        return results
    
    async def _execute_phase_sequential(
        self,
        phase: ExecutionPhase,
        agents: Dict[str, Callable],
        cycle_state: CycleState,
    ) -> Dict[str, Any]:
        """Execute phase agents sequentially."""
        
        results = {"success": True, "agents": {}}
        
        for agent_name in phase.agents:
            if agent_name not in agents:
                logger.warning(f"Agent {agent_name} not found - skipping")
                continue
            
            try:
                agent_result = await self._execute_agent(
                    agent_name, agents[agent_name], cycle_state
                )
                results["agents"][agent_name] = agent_result
                
                if not agent_result.get("success", True):
                    results["success"] = False
                    
            except Exception as e:
                logger.error(f"Agent {agent_name} failed: {e}")
                results["agents"][agent_name] = {"success": False, "error": str(e)}
                results["success"] = False
        
        return results
    
    async def _execute_phase_parallel(
        self,
        phase: ExecutionPhase,
        agents: Dict[str, Callable],
        cycle_state: CycleState,
    ) -> Dict[str, Any]:
        """Execute phase agents in parallel."""
        
        tasks = []
        agent_names = []
        
        for agent_name in phase.agents:
            if agent_name not in agents:
                continue
            agent_names.append(agent_name)
            tasks.append(self._execute_agent(agent_name, agents[agent_name], cycle_state))
        
        results = {"success": True, "agents": {}}
        
        if tasks:
            agent_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for agent_name, result in zip(agent_names, agent_results):
                if isinstance(result, Exception):
                    results["agents"][agent_name] = {"success": False, "error": str(result)}
                    results["success"] = False
                else:
                    results["agents"][agent_name] = result
                    if not result.get("success", True):
                        results["success"] = False
        
        return results
    
    async def _execute_agent(
        self,
        agent_name: str,
        agent_callable: Callable,
        cycle_state: CycleState,
    ) -> Dict[str, Any]:
        """Execute a single agent with tracking."""
        
        start_time = datetime.utcnow()
        
        try:
            # Inject few-shot examples if available
            enhanced_context = self._inject_few_shots(agent_name, self.context)
            
            # Execute agent
            result = await agent_callable(enhanced_context)
            
            # Track execution
            execution_entry = {
                "agent": agent_name,
                "success": result.get("success", True),
                "duration_ms": (datetime.utcnow() - start_time).total_seconds() * 1000,
                "quality_score": result.get("quality_score"),
                "timestamp": start_time.isoformat(),
            }
            cycle_state.execution_log.append(execution_entry)
            
            # Track modifications
            if result.get("modified"):
                for item in result.get("modified", []):
                    cycle_state.modified_items.add(item)
            
            # Track quality scores
            if result.get("quality_score"):
                cycle_state.quality_scores[agent_name] = result["quality_score"]
            
            # Emit signals based on result
            if self.signal_bus and not result.get("success", True):
                self.signal_bus.emit(
                    SignalType.VALIDATION_FAILURE,
                    f"Agent {agent_name} reported failure",
                    source=agent_name
                )
            
            # Update outputs
            if result.get("output"):
                self.outputs[agent_name] = result["output"]
            
            return result
            
        except Exception as e:
            logger.error(f"Agent {agent_name} execution error: {e}")
            cycle_state.execution_log.append({
                "agent": agent_name,
                "success": False,
                "error": str(e),
                "duration_ms": (datetime.utcnow() - start_time).total_seconds() * 1000,
                "timestamp": start_time.isoformat(),
            })
            return {"success": False, "error": str(e)}
    
    def _inject_few_shots(self, agent_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Inject relevant few-shot examples into context."""
        
        if not AUTONOMY_COMPONENTS_AVAILABLE:
            return context
        
        enhanced = copy.deepcopy(context)
        
        # Map agents to relevant few-shot patterns
        agent_patterns = {
            "bullet_generator": ["resume_bullets", "metric_binding"],
            "summary_generator": ["executive_summary"],
            "quality_critic": ["quality_critique"],
            "tone_adjuster": ["resume_bullets"],
        }
        
        patterns = agent_patterns.get(agent_name, [])
        if patterns:
            few_shots = {}
            for pattern in patterns:
                few_shot = FewShotLibrary.get_all_patterns().get(pattern)
                if few_shot:
                    few_shots[pattern] = few_shot
            
            if few_shots:
                enhanced["few_shot_examples"] = few_shots
        
        return enhanced
    
    async def _check_intervention_required(self, cycle_state: CycleState) -> bool:
        """Check if human intervention is required and handle it."""
        
        if not self.enable_intervention or not self.intervention_server:
            return False
        
        if not self.signal_bus:
            return False
        
        # Check intervention conditions
        intervention_needed, risk_factors = check_intervention_required(
            cycle=self.current_cycle,
            modified_count=len(cycle_state.modified_items),
            signals=[s.value for s in self.signal_bus.signals],
            quality_score=self._get_average_quality(cycle_state),
            high_risk_threshold=self.DEFAULT_HIGH_RISK_MODIFIED_THRESHOLD,
        )
        
        if not intervention_needed:
            return False
        
        logger.warning(f"🚨 INTERVENTION REQUIRED: {risk_factors}")
        
        # Create intervention context
        intervention_ctx = InterventionContext(
            workflow_id=self.workflow_id,
            cycle=self.current_cycle,
            reason="High-risk state detected",
            risk_factors=risk_factors,
            modified_items=list(cycle_state.modified_items),
            signals=[s.value for s in self.signal_bus.signals],
            quality_score=self._get_average_quality(cycle_state),
            recommendations=self._generate_recommendations(cycle_state),
        )
        
        # Request intervention
        approved = await self.intervention_server.request_intervention(
            intervention_ctx,
            timeout=300,  # 5 minute timeout
        )
        
        if not approved:
            self.signal_bus.emit(
                SignalType.VETOED,
                "Human vetoed continuation",
                source="InterventionServer"
            )
        
        return True
    
    async def _perform_reflection(self, cycle_state: CycleState) -> Optional[Any]:
        """Perform self-critique reflection."""
        
        if not self.reflection_agent:
            return None
        
        signals_summary = {}
        if self.signal_bus:
            signals_summary = self.signal_bus.get_summary()
        
        return await self.reflection_agent.reflect_on_execution(
            execution_log=cycle_state.execution_log,
            signals_summary=signals_summary,
            cycle=self.current_cycle,
            quality_scores=cycle_state.quality_scores,
        )
    
    def _take_snapshot(self) -> None:
        """Take a snapshot of current state for potential rollback."""
        
        snapshot = WorkflowSnapshot(
            cycle=self.current_cycle,
            context=copy.deepcopy(self.context),
            outputs=copy.deepcopy(self.outputs),
        )
        self.snapshots.append(snapshot)
        
        # Keep only last 3 snapshots
        if len(self.snapshots) > 3:
            self.snapshots = self.snapshots[-3:]
    
    def _rollback_to_snapshot(self) -> bool:
        """Rollback to the previous snapshot."""
        
        if len(self.snapshots) < 2:
            logger.warning("No previous snapshot available for rollback")
            return False
        
        # Get the snapshot before the current one
        snapshot = self.snapshots[-2]
        
        self.context = copy.deepcopy(snapshot.context)
        self.outputs = copy.deepcopy(snapshot.outputs)
        
        logger.info(f"Rolled back to cycle {snapshot.cycle} state")
        return True
    
    def _calculate_blast_radius(self, modified_items: Set[str]) -> Set[str]:
        """Calculate blast radius of modifications."""
        
        impacted = set(modified_items)
        
        for item in modified_items:
            dependents = self.dependency_map.get(item, set())
            impacted.update(dependents)
        
        return impacted
    
    def _check_quality_acceptable(self, cycle_state: CycleState) -> bool:
        """Check if quality scores meet threshold."""
        
        if not cycle_state.quality_scores:
            return True
        
        avg_quality = self._get_average_quality(cycle_state)
        return avg_quality >= self.quality_threshold
    
    def _get_average_quality(self, cycle_state: CycleState) -> float:
        """Get average quality score from cycle."""
        
        if not cycle_state.quality_scores:
            return 1.0
        
        scores = list(cycle_state.quality_scores.values())
        return sum(scores) / len(scores)
    
    def _generate_recommendations(self, cycle_state: CycleState) -> List[str]:
        """Generate recommendations based on current state."""
        
        recommendations = []
        
        avg_quality = self._get_average_quality(cycle_state)
        if avg_quality < self.quality_threshold:
            recommendations.append(
                f"Quality score ({avg_quality:.2f}) below threshold ({self.quality_threshold})"
            )
        
        if len(cycle_state.modified_items) > self.DEFAULT_HIGH_RISK_MODIFIED_THRESHOLD:
            recommendations.append(
                f"Many modifications ({len(cycle_state.modified_items)}) - review carefully"
            )
        
        # Check for failed agents
        failed_agents = [
            e["agent"] for e in cycle_state.execution_log
            if not e.get("success", True)
        ]
        if failed_agents:
            recommendations.append(f"Failed agents: {', '.join(failed_agents)}")
        
        return recommendations
    
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
- **Average Quality:** {self._get_average_quality(cycle_state):.2f}
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
            for rec in self._generate_recommendations(cycle_state):
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
            "final_quality": self._get_average_quality(
                self.cycle_history[-1]
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


def create_l5_orchestrator(
    workflow_id: str,
    max_cycles: int = 5,
    quality_threshold: float = 0.7,
    enable_intervention: bool = True,
) -> L5AutonomousOrchestrator:
    """Factory function to create L5+ orchestrator."""
    return L5AutonomousOrchestrator(
        workflow_id=workflow_id,
        max_cycles=max_cycles,
        quality_threshold=quality_threshold,
        enable_intervention=enable_intervention,
    )
