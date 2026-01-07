from __future__ import annotations
"""
Outreach Engine Self-Healing Loop

Provides self-healing capabilities for outreach campaigns:
- Signal routing and strategy selection
- Healing cycles with convergence detection
- Automatic rollback on critical failures
"""
from typing import Any, Optional, Protocol, Dict, List
from enum import Enum, auto


from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from .agents import (
    LeadQualityAgent,
    OutreachTestPilot,
)
from .TemplateOptimizerAgent import TemplateOptimizerAgent
from .context import OutreachEngineContext
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L3_orchestration.workflow_engines.l3_subatomic_testing_mixin import L3SubatomicTestingMixin


class OutreachHealingStrategy(Enum):
    """Healing strategies for outreach campaigns."""
    FULL_DIAGNOSTIC = "full_diagnostic"
    VERIFICATION_ONLY = "verification_only"
    QUALITY_FOCUS = "quality_focus"
    COMPLIANCE_FOCUS = "compliance_focus"
    SURGICAL_STRIKE = "surgical_strike"


@dataclass
class OutreachCycleResult:
    """Result of a single healing cycle."""
    cycle_number: int
    strategy: OutreachHealingStrategy
    agents_executed: List[str]
    signals_before: Set[str]
    signals_after: Set[str]
    passed_agents: List[str]
    failed_agents: List[str]
    rollback_triggered: bool
    converged: bool
    duration_ms: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class OutreachHealingResult:
    """Result of the complete healing process."""
    success: bool
    total_cycles: int
    final_signals: Set[str]
    cycle_results: List[OutreachCycleResult]
    convergence_cycle: Optional[int]
    budget_exhausted: bool
    total_duration_ms: float
    final_campaign: Dict[str, Any]


class OutreachSignalRouterAgent(MCPHardenedMixin, HealerMixin):
    """Routes signals to appropriate agents."""

    SIGNAL_TO_AGENTS = {
        "LEAD_QUALITY_ISSUE": ["LeadQualityAgent"],
        "CONTACT_VALIDATION_FAILED": ["ContactValidatorAgent"],
        "COMPLIANCE_ISSUE": ["MessageComplianceAgent"],
        "TEMPLATE_NEEDS_OPTIMIZATION": ["TemplateOptimizerAgent"],
        "CAMPAIGN_BALANCE_ISSUE": ["CampaignBalanceAgent"],
        "DELIVERABILITY_ISSUE": ["DeliverabilityAgent"],
        "TEST_FAILURE": ["OutreachTestPilot"],
    }

    CRITICAL_SIGNALS = {"COMPLIANCE_ISSUE", "DELIVERABILITY_ISSUE"}

    @classmethod
    def get_agents_for_signals(cls, signals: Set[str]) -> List[str]:
        """Get agents needed for the given signals."""
        agents = set()
        for signal in signals:
            if signal in cls.SIGNAL_TO_AGENTS:
                agents.update(cls.SIGNAL_TO_AGENTS[signal])
        return list(agents)

    @classmethod
    def has_critical_signal(cls, signals: Set[str]) -> bool:
        """Check if any critical signals are present."""
        return bool(signals & cls.CRITICAL_SIGNALS)

    @classmethod
    def determine_strategy(
        cls,
        cycle_number: int,
        signals: Set[str],
        modified_sections: Set[str],
    ) -> OutreachHealingStrategy:
        """Determine the healing strategy based on context."""
        if cycle_number == 1:
            return OutreachHealingStrategy.FULL_DIAGNOSTIC

        if not signals:
            return OutreachHealingStrategy.VERIFICATION_ONLY

        if cls.has_critical_signal(signals):
            return OutreachHealingStrategy.COMPLIANCE_FOCUS

        if len(signals) <= 2:
            return OutreachHealingStrategy.SURGICAL_STRIKE

        return OutreachHealingStrategy.QUALITY_FOCUS

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()


class OutreachAgentFactory(MCPHardenedMixin, HealerMixin):
    """Factory for creating outreach agents."""

    @staticmethod
    def create_all_agents(ctx: OutreachEngineContext) -> List[OutreachAgent]:
        """Create all agents for full diagnostic."""
        return [
            LeadQualityAgent(ctx),
            ContactValidatorAgent(ctx),
            MessageComplianceAgent(ctx),
            TemplateOptimizerAgent(ctx),
            CampaignBalanceAgent(ctx),
            DeliverabilityAgent(ctx),
            OutreachTestPilot(ctx),
        ]

    @staticmethod
    def create_quality_agents(ctx: OutreachEngineContext) -> List[OutreachAgent]:
        """Create quality-focused agents."""
        return [
            LeadQualityAgent(ctx),
            ContactValidatorAgent(ctx),
            TemplateOptimizerAgent(ctx),
            OutreachTestPilot(ctx),
        ]

    @staticmethod
    def create_compliance_agents(ctx: OutreachEngineContext) -> List[OutreachAgent]:
        """Create compliance-focused agents."""
        return [
            MessageComplianceAgent(ctx),
            DeliverabilityAgent(ctx),
            OutreachTestPilot(ctx),
        ]

    @staticmethod
    def create_agents_by_name(ctx: OutreachEngineContext, names: List[str]) -> List[OutreachAgent]:
        """Create specific agents by name."""
        agent_map = {
            "LeadQualityAgent": LeadQualityAgent,
            "ContactValidatorAgent": ContactValidatorAgent,
            "MessageComplianceAgent": MessageComplianceAgent,
            "TemplateOptimizerAgent": TemplateOptimizerAgent,
            "CampaignBalanceAgent": CampaignBalanceAgent,
            "DeliverabilityAgent": DeliverabilityAgent,
            "OutreachTestPilot": OutreachTestPilot,
            "CampaignPlannerAgent": CampaignPlannerAgent,
            "OutreachReflectionAgent": OutreachReflectionAgent,
        }

        agents = []
        for name in names:
            if name in agent_map:
                agents.append(agent_map[name](ctx))

        return agents

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()


class OutreachHealingCycle:
    """Manages a single healing cycle."""

    def __init__(self, ctx: OutreachEngineContext, cycle_number: int):
        self.ctx = ctx
        self.cycle_number = cycle_number
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

    async def execute(self, strategy: OutreachHealingStrategy) -> OutreachCycleResult:
        """Execute the healing cycle with the given strategy."""
        import time
        self.start_time = time.time()

        signals_before = set(self.ctx.signals)

        # Build agent agenda based on strategy
        agents = self._build_agenda(strategy)

        # Execute agents
        agents_executed = []
        passed_agents = []
        failed_agents = []

        for agent in agents:
            try:
                await agent.execute()
                agents_executed.append(agent.name)

                # Check result
                result = self.ctx.results.get(agent.name, {})
                if result.get("passed", True):
                    passed_agents.append(agent.name)
                else:
                    failed_agents.append(agent.name)

            except Exception as e:
                agents_executed.append(agent.name)
                failed_agents.append(agent.name)
                self.ctx.record_result(agent.name, passed=False, details=str(e))

        # Check for rollback conditions
        rollback_triggered = self._check_rollback_conditions()
        if rollback_triggered:
            self._execute_rollback()

        self.end_time = time.time()
        duration_ms = (self.end_time - self.start_time) * 1000

        signals_after = set(self.ctx.signals)
        converged = self.ctx.is_converged()

        return OutreachCycleResult(
            cycle_number=self.cycle_number,
            strategy=strategy,
            agents_executed=agents_executed,
            signals_before=signals_before,
            signals_after=signals_after,
            passed_agents=passed_agents,
            failed_agents=failed_agents,
            rollback_triggered=rollback_triggered,
            converged=converged,
            duration_ms=duration_ms,
        )

    def _build_agenda(self, strategy: OutreachHealingStrategy) -> List[OutreachAgent]:
        """Build the agent agenda based on strategy."""
        if strategy == OutreachHealingStrategy.FULL_DIAGNOSTIC:
            return OutreachAgentFactory.create_all_agents(self.ctx)

        elif strategy == OutreachHealingStrategy.VERIFICATION_ONLY:
            return [OutreachTestPilot(self.ctx)]

        elif strategy == OutreachHealingStrategy.QUALITY_FOCUS:
            return OutreachAgentFactory.create_quality_agents(self.ctx)

        elif strategy == OutreachHealingStrategy.COMPLIANCE_FOCUS:
            return OutreachAgentFactory.create_compliance_agents(self.ctx)

        elif strategy == OutreachHealingStrategy.SURGICAL_STRIKE:
            agent_names = OutreachSignalRouterAgent.get_agents_for_signals(self.ctx.signals)
            if not agent_names:
                agent_names = ["OutreachTestPilot"]
            agents = OutreachAgentFactory.create_agents_by_name(self.ctx, agent_names)
            if not any(isinstance(a, OutreachTestPilot) for a in agents):
                agents.append(OutreachTestPilot(self.ctx))
            return agents

        return OutreachAgentFactory.create_all_agents(self.ctx)

    def _check_rollback_conditions(self) -> bool:
        """Check if rollback should be triggered."""
        if OutreachSignalRouterAgent.has_critical_signal(self.ctx.signals):
            return True

        if (self.cycle_number > 1 and
            self.ctx.has_signal("TEST_FAILURE") and
            self.ctx.campaign_backups):
            return True

        return False

    def _execute_rollback(self):
        """Execute rollback of all changes."""
        print(f"   🚨 Cycle {self.cycle_number}: Triggering rollback...")
        self.ctx.rollback_all()

        for signal in list(self.ctx.signals):
            if signal in OutreachSignalRouterAgent.CRITICAL_SIGNALS or signal == "TEST_FAILURE":
                self.ctx.remove_signal(signal)


async def run_outreach_healing_mission(
    campaign: Dict[str, Any],
    leads: List[Dict[str, Any]] = None,
    contacts: List[Dict[str, Any]] = None,
    messages: List[Dict[str, Any]] = None,
    max_cycles: int = 5,
) -> OutreachHealingResult:
    """
    Run a complete outreach healing mission.

    Args:
        campaign: Campaign configuration
        leads: List of leads
        contacts: List of contacts
        messages: List of message templates
        max_cycles: Maximum healing cycles

    Returns:
        OutreachHealingResult with mission outcome
    """
    ctx = OutreachEngineContext()
    ctx.current_campaign = campaign
    ctx.leads = leads or []
    ctx.contacts = contacts or []
    ctx.messages = messages or []

    # Backup initial state
    ctx.backup_campaign("default")

    orchestrator = OutreachHealingOrchestratorAgent(ctx, max_cycles=max_cycles)
    return await orchestrator.run()