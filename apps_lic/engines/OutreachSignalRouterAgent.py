from __future__ import annotations

"""
Outreach Engine Self-Healing Loop

Provides self-healing capabilities for outreach campaigns:
- Signal routing and strategy selection
- Healing cycles with convergence detection
- Automatic rollback on critical failures
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from agentic_core.L3_orchestration.unified.AppWorkflowOrchestratorAgent import (
    AppWorkflowOrchestratorAgent,
)
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin

from .agents import (
    LeadQualityAgent,
    OutreachTestPilot,
)
from .context import OutreachEngineContext


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
    agents_executed: list[str]
    signals_before: set[str]
    signals_after: set[str]
    passed_agents: list[str]
    failed_agents: list[str]
    rollback_triggered: bool
    converged: bool
    duration_ms: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class OutreachHealingResult:
    """Result of the complete healing process."""

    success: bool
    total_cycles: int
    final_signals: set[str]
    cycle_results: list[OutreachCycleResult]
    convergence_cycle: int | None
    budget_exhausted: bool
    total_duration_ms: float
    final_campaign: dict[str, Any]


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
    def get_agents_for_signals(cls, signals: set[str]) -> list[str]:
        """
        Get agents needed for the given signals.

        Args:
            signals: Set of signal names to route

        Returns:
            List of agent names that should handle these signals
        """
        agents: set[str] = set()
        for signal in signals:
            if signal in cls.SIGNAL_TO_AGENTS:
                agents.update(cls.SIGNAL_TO_AGENTS[signal])
        return list(agents)

    @classmethod
    def has_critical_signal(cls, signals: set[str]) -> bool:
        """
        Check if any critical signals are present.

        Args:
            signals: Set of signal names to check

        Returns:
            True if any signal is critical, False otherwise
        """
        return bool(signals & cls.CRITICAL_SIGNALS)

    @classmethod
    def determine_strategy(
        cls,
        cycle_number: int,
        signals: set[str],
        modified_sections: set[str],
    ) -> OutreachHealingStrategy:
        """
        Determine healing strategy based on context.

        Args:
            cycle_number: Current healing cycle number (1-indexed)
            signals: Set of active signals requiring attention
            modified_sections: Set of campaign sections that were modified

        Returns:
            Appropriate healing strategy for the current context
        """
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
    def create_all_agents(ctx: OutreachEngineContext) -> list[Any]:
        """
        Create all agents for full diagnostic.

        Args:
            ctx: Outreach engine context

        Returns:
            List of all outreach agents
        """
        return [
            LeadQualityAgent(ctx),
            ContactValidatorAgent(ctx),
            MessageComplianceAgent(ctx),
            RgTemplateOptimizerAgent(ctx),
            CampaignBalanceAgent(ctx),
            DeliverabilityAgent(ctx),
            OutreachTestPilot(ctx),
        ]

    @staticmethod
    def create_quality_agents(ctx: OutreachEngineContext) -> list[Any]:
        """
        Create quality-focused agents.

        Args:
            ctx: Outreach engine context

        Returns:
            List of quality-focused agents
        """
        return [
            LeadQualityAgent(ctx),
            ContactValidatorAgent(ctx),
            RgTemplateOptimizerAgent(ctx),
            OutreachTestPilot(ctx),
        ]

    @staticmethod
    def create_compliance_agents(ctx: OutreachEngineContext) -> list[Any]:
        """
        Create compliance-focused agents.

        Args:
            ctx: Outreach engine context

        Returns:
            List of compliance-focused agents
        """
        return [
            MessageComplianceAgent(ctx),
            DeliverabilityAgent(ctx),
            OutreachTestPilot(ctx),
        ]

    @staticmethod
    def create_agents_by_name(ctx: OutreachEngineContext, names: list[str]) -> list[Any]:
        """
        Create specific agents by name.

        Args:
            ctx: Outreach engine context
            names: List of agent class names to create

        Returns:
            List of requested agents
        """
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

    def __init__(self, ctx: OutreachEngineContext, cycle_number: int) -> None:
        """
        Initialize healing cycle.

        Args:
            ctx: Outreach engine context
            cycle_number: Current cycle number (1-indexed)
        """
        self.ctx: OutreachEngineContext = ctx
        self.cycle_number: int = cycle_number
        self.start_time: float | None = None
        self.end_time: float | None = None

    async def execute(self, strategy: OutreachHealingStrategy) -> OutreachCycleResult:
        """
        Execute the healing cycle with the given strategy.

        Args:
            strategy: Healing strategy to apply

        Returns:
            OutreachCycleResult with cycle execution details
        """
        import time

        self.start_time = time.time()

        signals_before = set(self.ctx.signals)

        # Build agent agenda based on strategy
        agents = self._build_agenda(strategy)

        # Execute agents
        agents_executed: list[str] = []
        passed_agents: list[str] = []
        failed_agents: list[str] = []

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

    def _build_agenda(self, strategy: OutreachHealingStrategy) -> list[Any]:
        """
        Build the agent agenda based on strategy.

        Args:
            strategy: Healing strategy to apply

        Returns:
            List of agents to execute
        """
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
        """
        Check if rollback should be triggered.

        Returns:
            True if rollback conditions are met, False otherwise
        """
        if OutreachSignalRouterAgent.has_critical_signal(self.ctx.signals):
            return True

        if (
            self.cycle_number > 1
            and self.ctx.has_signal("TEST_FAILURE")
            and self.ctx.campaign_backups
        ):
            return True

        return False

    def _execute_rollback(self) -> None:
        """
        Execute rollback of all changes.

        Reverts campaign to last backup and clears critical signals.
        """
        print(f"   🚨 Cycle {self.cycle_number}: Triggering rollback...")
        self.ctx.rollback_all()

        for signal in list(self.ctx.signals):
            if signal in OutreachSignalRouterAgent.CRITICAL_SIGNALS or signal == "TEST_FAILURE":
                self.ctx.remove_signal(signal)


async def run_outreach_healing_mission(
    campaign: dict[str, Any],
    leads: list[dict[str, Any]] = None,
    contacts: list[dict[str, Any]] = None,
    messages: list[dict[str, Any]] = None,
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

    orchestrator = AppWorkflowOrchestratorAgent(ctx, max_cycles=max_cycles)
    return await orchestrator.run()
