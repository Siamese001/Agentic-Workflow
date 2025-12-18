"""
L5+ Autonomous Orchestrator for Outreach Engine.

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
class OutreachExecutionPhase:
    """Definition of an outreach execution phase."""
    
    name: str
    agents: List[str]
    execution_mode: str = "sequential"  # sequential, parallel
    is_hard_gate: bool = False
    condition: Optional[Callable] = None


@dataclass
class OutreachCycleState:
    """State for a single convergence cycle."""
    
    cycle: int
    modified_items: Set[str] = field(default_factory=set)
    quality_scores: Dict[str, float] = field(default_factory=dict)
    execution_log: List[Dict[str, Any]] = field(default_factory=list)
    messages_generated: int = 0
    personalization_score: float = 0.0
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None


@dataclass
class OutreachSnapshot:
    """Snapshot of outreach state for rollback."""
    
    cycle: int
    context: Dict[str, Any]
    outputs: Dict[str, Any]
    messages: List[Dict[str, Any]]
    timestamp: datetime = field(default_factory=datetime.utcnow)


class L5OutreachOrchestrator:
    """
    L5+ Autonomous Orchestrator for Outreach Engine.
    
    Key Features:
    1. Convergence Loop: Iterates until message quality converges
    2. Signal System: Blackboard pattern for inter-agent communication
    3. Human-in-the-Loop: Intervention for high-risk personalization
    4. Reflection: Self-critique on message effectiveness
    5. Blast Radius: Impact analysis for message changes
    6. Rollback: Restore previous message state on regression
    7. Few-Shot Injection: Enhanced prompts with outreach examples
    
    Outreach-Specific Considerations:
    - Archetype-aware message generation (C-Level, VP, Recruiter, etc.)
    - Personalization depth tracking
    - Metric binding validation
    - Tone consistency across message sections
    """
    
    # Default configuration
    DEFAULT_MAX_CYCLES = 5
    DEFAULT_QUALITY_THRESHOLD = 0.75  # Higher threshold for outreach
    DEFAULT_HIGH_RISK_THRESHOLD = 3
    
    # Archetype-specific quality thresholds
    ARCHETYPE_THRESHOLDS = {
        "C_LEVEL": 0.85,
        "VP_LEVEL": 0.80,
        "DIRECTOR": 0.75,
        "MANAGER": 0.70,
        "RECRUITER": 0.70,
    }
    
    def __init__(
        self,
        campaign_id: str,
        archetype: str = "RECRUITER",
        max_cycles: int = DEFAULT_MAX_CYCLES,
        quality_threshold: Optional[float] = None,
        enable_intervention: bool = True,
        intervention_port: int = 8081,
        output_dir: str = "./outreach_runs",
    ) -> None:
        """
        Initialize the L5+ outreach orchestrator.
        
        Args:
            campaign_id: Unique identifier for this campaign
            archetype: Target archetype (C_LEVEL, VP_LEVEL, etc.)
            max_cycles: Maximum convergence cycles
            quality_threshold: Minimum acceptable quality (auto-set by archetype if None)
            enable_intervention: Enable human-in-the-loop
            intervention_port: Port for intervention server
            output_dir: Directory for outputs and reports
        """
        self.campaign_id = campaign_id
        self.archetype = archetype
        self.max_cycles = max_cycles
        self.quality_threshold = quality_threshold or self.ARCHETYPE_THRESHOLDS.get(
            archetype, self.DEFAULT_QUALITY_THRESHOLD
        )
        self.enable_intervention = enable_intervention
        self.intervention_port = intervention_port
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize L5+ components
        if AUTONOMY_COMPONENTS_AVAILABLE:
            self.signal_bus = get_signal_bus()
            self.reflection_agent = create_reflection_agent(
                min_quality_threshold=self.quality_threshold
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
        self.cycle_history: List[OutreachCycleState] = []
        self.snapshots: List[OutreachSnapshot] = []
        self.context: Dict[str, Any] = {}
        self.outputs: Dict[str, Any] = {}
        self.generated_messages: List[Dict[str, Any]] = []
        
        # Dependency tracking for blast radius (message sections)
        self.dependency_map: Dict[str, Set[str]] = {
            "subject_line": {"hook", "cta"},
            "hook": {"subject_line", "value_proposition"},
            "value_proposition": {"hook", "cta", "metrics"},
            "metrics": {"value_proposition"},
            "cta": {"value_proposition", "signature"},
            "signature": {"cta"},
        }
        
        # Execution phases
        self.phases = self._define_phases()
        
        # Convergence tracking
        self.converged = False
        self.convergence_reason = ""
        
        logger.info(
            f"L5OutreachOrchestrator initialized: campaign={campaign_id}, "
            f"archetype={archetype}, quality_threshold={self.quality_threshold}"
        )
    
    def _define_phases(self) -> List[OutreachExecutionPhase]:
        """Define outreach execution phases."""
        return [
            OutreachExecutionPhase(
                name="context_gathering",
                agents=["recipient_analyzer", "company_researcher", "history_retriever"],
                execution_mode="parallel",
            ),
            OutreachExecutionPhase(
                name="personalization",
                agents=["personalization_engine", "archetype_matcher"],
                execution_mode="sequential",
                is_hard_gate=True,
            ),
            OutreachExecutionPhase(
                name="message_generation",
                agents=["hook_generator", "value_composer", "cta_generator"],
                execution_mode="sequential",
            ),
            OutreachExecutionPhase(
                name="quality_validation",
                agents=["tone_validator", "metric_binder", "length_checker"],
                execution_mode="parallel",
            ),
            OutreachExecutionPhase(
                name="refinement",
                agents=["tone_adjuster", "personalization_enhancer"],
                execution_mode="sequential",
                condition=lambda ctx: ctx.get("needs_refinement", False),
            ),
        ]
    
    async def execute_outreach_campaign(
        self,
        recipients: List[Dict[str, Any]],
        campaign_context: Dict[str, Any],
        agents: Dict[str, Callable],
    ) -> Dict[str, Any]:
        """
        Execute outreach campaign with convergence loop.
        
        Args:
            recipients: List of recipient profiles
            campaign_context: Campaign configuration and context
            agents: Dictionary of agent name -> async callable
            
        Returns:
            Campaign execution results with generated messages
        """
        logger.info(f"Starting L5+ outreach campaign: {self.campaign_id}")
        
        self.context = {
            **campaign_context,
            "archetype": self.archetype,
            "recipients": recipients,
        }
        self.outputs = {}
        self.generated_messages = []
        
        # Start intervention server if enabled
        if self.intervention_server and self.enable_intervention:
            await self.intervention_server.start_server()
        
        try:
            # Process each recipient with convergence
            for recipient_idx, recipient in enumerate(recipients):
                logger.info(f"\nProcessing recipient {recipient_idx + 1}/{len(recipients)}")
                
                message_result = await self._process_recipient_with_convergence(
                    recipient, agents
                )
                
                if message_result.get("success"):
                    self.generated_messages.append(message_result)
                else:
                    logger.warning(f"Failed to generate message for recipient {recipient_idx + 1}")
                
                # Check for campaign-level abort
                if self.signal_bus and self.signal_bus.is_critical_state():
                    logger.error("Campaign aborted due to critical failure")
                    break
            
            # Generate campaign report
            return self._generate_campaign_results()
            
        finally:
            if self.intervention_server:
                await self.intervention_server.stop_server()
    
    async def _process_recipient_with_convergence(
        self,
        recipient: Dict[str, Any],
        agents: Dict[str, Callable],
    ) -> Dict[str, Any]:
        """Process a single recipient with convergence loop."""
        
        recipient_context = {
            **self.context,
            "current_recipient": recipient,
        }
        
        best_message = None
        best_quality = 0.0
        
        for cycle in range(self.max_cycles):
            self.current_cycle = cycle + 1
            
            logger.info(f"  Cycle {self.current_cycle}/{self.max_cycles}")
            
            # Initialize cycle state
            cycle_state = OutreachCycleState(cycle=self.current_cycle)
            
            # Clear signals
            if self.signal_bus:
                self.signal_bus.clear_cycle()
            
            # Take snapshot
            self._take_snapshot(recipient_context)
            
            # Execute phases
            phase_results = await self._execute_all_phases(
                agents, cycle_state, recipient_context
            )
            
            # Check for critical failure
            if self.signal_bus and self.signal_bus.is_critical_state():
                break
            
            # Check intervention
            if await self._check_intervention_required(cycle_state, recipient):
                if self.signal_bus and self.signal_bus.has(SignalType.VETOED):
                    break
            
            # Perform reflection
            reflection_result = await self._perform_reflection(cycle_state)
            
            # Track best message
            current_quality = self._get_average_quality(cycle_state)
            if current_quality > best_quality:
                best_quality = current_quality
                best_message = self._extract_message(phase_results, recipient_context)
            
            # Handle reflection decision
            if reflection_result:
                if reflection_result.decision == ReflectionDecision.CONVERGE_AND_COMMIT:
                    logger.info("  ✅ Message quality converged")
                    break
                elif reflection_result.decision == ReflectionDecision.ROLLBACK_LAST_CHANGE_AND_RETRY:
                    self._rollback_to_snapshot()
                elif reflection_result.decision == ReflectionDecision.ESCALATE_TO_HUMAN_WITH_REPORT:
                    await self._generate_escalation_report(cycle_state, recipient)
                    break
            
            # Check convergence
            if current_quality >= self.quality_threshold:
                logger.info(f"  ✅ Quality threshold met: {current_quality:.2f}")
                break
            
            cycle_state.end_time = datetime.utcnow()
            self.cycle_history.append(cycle_state)
        
        return {
            "success": best_message is not None,
            "recipient": recipient,
            "message": best_message,
            "quality_score": best_quality,
            "cycles_used": self.current_cycle,
        }
    
    async def _execute_all_phases(
        self,
        agents: Dict[str, Callable],
        cycle_state: OutreachCycleState,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute all outreach phases."""
        
        results = {}
        
        for phase in self.phases:
            if phase.condition and not phase.condition(context):
                continue
            
            logger.debug(f"    Phase: {phase.name}")
            
            try:
                if phase.execution_mode == "parallel":
                    phase_result = await self._execute_phase_parallel(
                        phase, agents, cycle_state, context
                    )
                else:
                    phase_result = await self._execute_phase_sequential(
                        phase, agents, cycle_state, context
                    )
                
                results[phase.name] = phase_result
                
                # Update context with phase outputs
                for agent_name, agent_result in phase_result.get("agents", {}).items():
                    if agent_result.get("output"):
                        context[f"{agent_name}_output"] = agent_result["output"]
                
                if phase.is_hard_gate and not phase_result.get("success", True):
                    if self.signal_bus:
                        self.signal_bus.signal_critical_failure(
                            f"Hard gate {phase.name} failed",
                            source="L5OutreachOrchestrator"
                        )
                    break
                    
            except Exception as e:
                logger.error(f"    Phase {phase.name} error: {e}")
                if phase.is_hard_gate:
                    break
        
        return results
    
    async def _execute_phase_sequential(
        self,
        phase: OutreachExecutionPhase,
        agents: Dict[str, Callable],
        cycle_state: OutreachCycleState,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute phase agents sequentially."""
        
        results = {"success": True, "agents": {}}
        
        for agent_name in phase.agents:
            if agent_name not in agents:
                continue
            
            try:
                agent_result = await self._execute_agent(
                    agent_name, agents[agent_name], cycle_state, context
                )
                results["agents"][agent_name] = agent_result
                
                if not agent_result.get("success", True):
                    results["success"] = False
                    
            except Exception as e:
                results["agents"][agent_name] = {"success": False, "error": str(e)}
                results["success"] = False
        
        return results
    
    async def _execute_phase_parallel(
        self,
        phase: OutreachExecutionPhase,
        agents: Dict[str, Callable],
        cycle_state: OutreachCycleState,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute phase agents in parallel."""
        
        tasks = []
        agent_names = []
        
        for agent_name in phase.agents:
            if agent_name not in agents:
                continue
            agent_names.append(agent_name)
            tasks.append(
                self._execute_agent(agent_name, agents[agent_name], cycle_state, context)
            )
        
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
        cycle_state: OutreachCycleState,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute a single agent with tracking."""
        
        start_time = datetime.utcnow()
        
        try:
            # Inject outreach-specific few-shots
            enhanced_context = self._inject_few_shots(agent_name, context)
            
            result = await agent_callable(enhanced_context)
            
            # Track execution
            cycle_state.execution_log.append({
                "agent": agent_name,
                "success": result.get("success", True),
                "duration_ms": (datetime.utcnow() - start_time).total_seconds() * 1000,
                "quality_score": result.get("quality_score"),
                "timestamp": start_time.isoformat(),
            })
            
            if result.get("modified"):
                for item in result.get("modified", []):
                    cycle_state.modified_items.add(item)
            
            if result.get("quality_score"):
                cycle_state.quality_scores[agent_name] = result["quality_score"]
            
            if result.get("personalization_score"):
                cycle_state.personalization_score = max(
                    cycle_state.personalization_score,
                    result["personalization_score"]
                )
            
            return result
            
        except Exception as e:
            cycle_state.execution_log.append({
                "agent": agent_name,
                "success": False,
                "error": str(e),
                "timestamp": start_time.isoformat(),
            })
            return {"success": False, "error": str(e)}
    
    def _inject_few_shots(self, agent_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Inject outreach-specific few-shot examples."""
        
        if not AUTONOMY_COMPONENTS_AVAILABLE:
            return context
        
        enhanced = copy.deepcopy(context)
        
        # Map agents to outreach patterns
        agent_patterns = {
            "personalization_engine": ["outreach_personalization"],
            "hook_generator": ["outreach_hooks"],
            "cta_generator": ["outreach_cta"],
            "value_composer": ["outreach_personalization", "metric_binding"],
            "tone_validator": ["quality_critique"],
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
    
    async def _check_intervention_required(
        self,
        cycle_state: OutreachCycleState,
        recipient: Dict[str, Any],
    ) -> bool:
        """Check if human intervention is required."""
        
        if not self.enable_intervention or not self.intervention_server:
            return False
        
        if not self.signal_bus:
            return False
        
        # Higher-risk for C-level outreach
        threshold = 2 if self.archetype == "C_LEVEL" else self.DEFAULT_HIGH_RISK_THRESHOLD
        
        intervention_needed, risk_factors = check_intervention_required(
            cycle=self.current_cycle,
            modified_count=len(cycle_state.modified_items),
            signals=[s.value for s in self.signal_bus.signals],
            quality_score=self._get_average_quality(cycle_state),
            high_risk_threshold=threshold,
        )
        
        if not intervention_needed:
            return False
        
        intervention_ctx = InterventionContext(
            workflow_id=f"{self.campaign_id}_{recipient.get('id', 'unknown')}",
            cycle=self.current_cycle,
            reason=f"High-risk {self.archetype} outreach",
            risk_factors=risk_factors,
            modified_items=list(cycle_state.modified_items),
            signals=[s.value for s in self.signal_bus.signals],
            quality_score=self._get_average_quality(cycle_state),
        )
        
        approved = await self.intervention_server.request_intervention(
            intervention_ctx, timeout=300
        )
        
        if not approved:
            self.signal_bus.emit(SignalType.VETOED, "Human vetoed", source="Intervention")
        
        return True
    
    async def _perform_reflection(self, cycle_state: OutreachCycleState) -> Optional[Any]:
        """Perform reflection on outreach quality."""
        
        if not self.reflection_agent:
            return None
        
        signals_summary = self.signal_bus.get_summary() if self.signal_bus else {}
        
        return await self.reflection_agent.reflect_on_execution(
            execution_log=cycle_state.execution_log,
            signals_summary=signals_summary,
            cycle=self.current_cycle,
            quality_scores=cycle_state.quality_scores,
        )
    
    def _take_snapshot(self, context: Dict[str, Any]) -> None:
        """Take snapshot for rollback."""
        
        snapshot = OutreachSnapshot(
            cycle=self.current_cycle,
            context=copy.deepcopy(context),
            outputs=copy.deepcopy(self.outputs),
            messages=copy.deepcopy(self.generated_messages),
        )
        self.snapshots.append(snapshot)
        
        if len(self.snapshots) > 3:
            self.snapshots = self.snapshots[-3:]
    
    def _rollback_to_snapshot(self) -> bool:
        """Rollback to previous snapshot."""
        
        if len(self.snapshots) < 2:
            return False
        
        snapshot = self.snapshots[-2]
        self.outputs = copy.deepcopy(snapshot.outputs)
        self.generated_messages = copy.deepcopy(snapshot.messages)
        
        logger.info(f"Rolled back to cycle {snapshot.cycle}")
        return True
    
    def _extract_message(
        self,
        phase_results: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Extract generated message from phase results."""
        
        message = {
            "subject": context.get("hook_generator_output", {}).get("subject", ""),
            "hook": context.get("hook_generator_output", {}).get("hook", ""),
            "value_proposition": context.get("value_composer_output", {}).get("value", ""),
            "cta": context.get("cta_generator_output", {}).get("cta", ""),
            "archetype": self.archetype,
            "personalization_score": context.get("personalization_score", 0),
        }
        
        if any(message.values()):
            return message
        return None
    
    def _get_average_quality(self, cycle_state: OutreachCycleState) -> float:
        """Get average quality score."""
        
        if not cycle_state.quality_scores:
            return 0.0
        
        scores = list(cycle_state.quality_scores.values())
        return sum(scores) / len(scores)
    
    async def _generate_escalation_report(
        self,
        cycle_state: OutreachCycleState,
        recipient: Dict[str, Any],
    ) -> None:
        """Generate escalation report."""
        
        report_path = self.output_dir / f"escalation_{self.campaign_id}_{int(datetime.utcnow().timestamp())}.md"
        
        report = f"""# Outreach Escalation Report

**Campaign ID:** {self.campaign_id}
**Archetype:** {self.archetype}
**Recipient:** {recipient.get('name', 'Unknown')}
**Generated:** {datetime.utcnow().isoformat()}

## Quality Scores

"""
        for agent, score in cycle_state.quality_scores.items():
            report += f"- {agent}: {score:.2f}\n"
        
        report += f"\n**Personalization Score:** {cycle_state.personalization_score:.2f}\n"
        
        report_path.write_text(report)
        logger.info(f"Escalation report: {report_path}")
    
    def _generate_campaign_results(self) -> Dict[str, Any]:
        """Generate final campaign results."""
        
        successful = [m for m in self.generated_messages if m.get("success")]
        
        return {
            "campaign_id": self.campaign_id,
            "archetype": self.archetype,
            "total_recipients": len(self.context.get("recipients", [])),
            "messages_generated": len(successful),
            "success_rate": len(successful) / max(len(self.context.get("recipients", [])), 1),
            "average_quality": (
                sum(m.get("quality_score", 0) for m in successful) / len(successful)
                if successful else 0
            ),
            "messages": self.generated_messages,
            "signals": [s.value for s in self.signal_bus.signals] if self.signal_bus else [],
        }


def create_l5_outreach_orchestrator(
    campaign_id: str,
    archetype: str = "RECRUITER",
    max_cycles: int = 5,
    enable_intervention: bool = True,
) -> L5OutreachOrchestrator:
    """Factory function to create L5+ outreach orchestrator."""
    return L5OutreachOrchestrator(
        campaign_id=campaign_id,
        archetype=archetype,
        max_cycles=max_cycles,
        enable_intervention=enable_intervention,
    )
