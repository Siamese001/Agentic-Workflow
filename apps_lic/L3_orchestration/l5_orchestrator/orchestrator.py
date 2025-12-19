"""
L5 Autonomous Orchestrator - Main Class and Convergence Loop (Outreach Engine)
"""

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

from apps_lic.L3_orchestration.l5_orchestrator.types import (
    OutreachCycleState,
    OutreachExecutionPhase,
    OutreachSnapshot,
)

from . import intervention_handler, phase_executor, reflection_handler, snapshot_manager


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
        """Initialize the L5+ outreach orchestrator."""
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
        self.dependency_map: Dict[str, set] = {
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
        """Execute outreach campaign with convergence loop."""
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
                await self.signal_bus.clear_cycle()
            
            # Take snapshot
            snapshot_manager.take_snapshot(self, recipient_context)
            
            # Execute phases
            phase_results = await phase_executor.execute_all_phases(
                self, agents, cycle_state, recipient_context
            )
            
            # Check for critical failure
            if self.signal_bus and self.signal_bus.is_critical_state():
                break
            
            # Check intervention
            if await intervention_handler.check_intervention_required(
                self, cycle_state, recipient
            ):
                if self.signal_bus and self.signal_bus.has(SignalType.VETOED):
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
                    self.convergence_reason = "escalated_to_human"
                    break
            
            # Check for convergence
            if not cycle_state.modified_items and reflection_handler.check_quality_acceptable(self, cycle_state):
                self.converged = True
                self.convergence_reason = "stable_state"
                logger.info("✅ CONVERGED - Stable state achieved")
                break
            
            # Store cycle state
            cycle_state.end_time = datetime.utcnow()
            self.cycle_history.append(cycle_state)
            
            # Track best message
            current_quality = reflection_handler.get_average_quality(self, cycle_state)
            if current_quality > best_quality:
                best_quality = current_quality
                best_message = self.outputs.get("message_generator", {})
        
        # Return best message generated
        return {
            "success": best_message is not None,
            "message": best_message or {},
            "quality_score": best_quality,
            "cycles_used": self.current_cycle,
            "recipient": recipient,
        }
    
    def _generate_campaign_results(self) -> Dict[str, Any]:
        """Generate final campaign results."""
        
        return {
            "campaign_id": self.campaign_id,
            "archetype": self.archetype,
            "total_recipients": len(self.context.get("recipients", [])),
            "messages_generated": len(self.generated_messages),
            "average_quality": sum(m.get("quality_score", 0) for m in self.generated_messages) / len(self.generated_messages) if self.generated_messages else 0,
            "convergence_rate": len(self.generated_messages) / len(self.context.get("recipients", [])) if self.context.get("recipients") else 0,
            "messages": self.generated_messages,
            "signals": [s.value for s in self.signal_bus.signals] if self.signal_bus else [],
        }
