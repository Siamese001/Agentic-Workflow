from __future__ import annotations
"""
Self-Healing Engine - Phase 2 Implementation

This module provides the core self-healing capabilities:
- HealingCycle: Manages individual healing cycles
- HealingStrategy: Determines which agents to run based on signals
- RgHealingOrchestratorAgent: Coordinates multiple healing cycles
- AutomaticRollback: Handles rollback on critical failures
"""
from typing import Any, Optional, Protocol, Dict, List
from enum import Enum, auto


from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from .agents import (
    ATSCompatibilityAgent,
    BrandComplianceAgent,
    ContentQualityAgent,
    FactCheckAgent,
    ReflectionAgent,
    SectionBalanceAgent,
    StrategicPlannerAgent,
    TemplateOptimizerAgent,
    TestPilot,
)
from .resume_base import ResumeAgent
from .context import ResumeEngineContext
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L3_orchestration.workflow_engines.l3_subatomic_testing_mixin import L3SubatomicTestingMixin


class HealingStrategy(Enum):
    """Strategy for selecting agents in a healing cycle."""
    FULL_DIAGNOSTIC = "full_diagnostic"  # Run all agents
    SURGICAL_STRIKE = "surgical_strike"  # Run only agents for specific signals
    VERIFICATION_ONLY = "verification_only"  # Run only TestPilot
    QUALITY_FOCUS = "quality_focus"  # Focus on quality agents
    COMPLIANCE_FOCUS = "compliance_focus"  # Focus on compliance agents


@dataclass
class CycleResult:
    """Result of a single healing cycle."""
    cycle_number: int
    strategy: HealingStrategy
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
class HealingResult:
    """Result of the complete healing process."""
    success: bool
    total_cycles: int
    final_signals: Set[str]
    cycle_results: List[CycleResult]
    convergence_cycle: Optional[int]
    budget_exhausted: bool
    total_duration_ms: float
    final_resume: Dict[str, Any]


class SignalRouterAgent(MCPHardenedMixin, HealerMixin):
    """Routes signals to appropriate agents."""

    # Signal to agent mapping
    SIGNAL_AGENT_MAP = {
        "QUALITY_FAILURE": ["ContentQualityAgent", "FactCheckAgent"],
        "HALLUCINATION_DETECTED": ["FactCheckAgent"],
        "BRAND_VIOLATION": ["BrandComplianceAgent"],
        "ATS_FAILURE": ["ATSCompatibilityAgent"],
        "BALANCE_ISSUE": ["SectionBalanceAgent"],
        "TEST_FAILURE": ["TestPilot"],
        "TEMPLATE_MISMATCH": ["TemplateOptimizerAgent"],
    }

    # Critical signals that trigger rollback
    CRITICAL_SIGNALS = {"CRITICAL_FAILURE", "DATA_CORRUPTION", "SCHEMA_VIOLATION"}

    @classmethod
    def get_agents_for_signals(cls, signals: Set[str]) -> List[str]:
        """
        Get list of agent names that should handle the given signals.

        Args:
            signals: Set of signal names to route

        Returns:
            List of agent class names that should handle these signals
        """
        agents: Set[str] = set()
        for signal in signals:
            if signal in cls.SIGNAL_AGENT_MAP:
                agents.update(cls.SIGNAL_AGENT_MAP[signal])
        return list(agents)

    @classmethod
    def has_critical_signal(cls, signals: Set[str]) -> bool:
        """
        Check if any critical signals are present.

        Args:
            signals: Set of signal names to check

        Returns:
            True if any signal is critical (requires rollback), False otherwise
        """
        return bool(signals & cls.CRITICAL_SIGNALS)

    @classmethod
    def determine_strategy(cls, cycle: int, signals: Set[str], modified_sections: Set[str]) -> HealingStrategy:
        """
        Determine the healing strategy based on current state.

        Args:
            cycle: Current healing cycle number (1-indexed)
            signals: Set of active signals requiring attention
            modified_sections: Set of resume sections that were modified

        Returns:
            Appropriate healing strategy for the current context
        """
        if cycle == 1:
            return HealingStrategy.FULL_DIAGNOSTIC

        if not signals and not modified_sections:
            return HealingStrategy.VERIFICATION_ONLY

        quality_signals: Set[str] = {"QUALITY_FAILURE", "HALLUCINATION_DETECTED"}
        compliance_signals: Set[str] = {"BRAND_VIOLATION", "ATS_FAILURE", "BALANCE_ISSUE"}

        if signals & quality_signals and not (signals & compliance_signals):
            return HealingStrategy.QUALITY_FOCUS

        if signals & compliance_signals and not (signals & quality_signals):
            return HealingStrategy.COMPLIANCE_FOCUS

        return HealingStrategy.SURGICAL_STRIKE

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()


class AgentFactory(MCPHardenedMixin, HealerMixin):
    """Factory for creating agent instances."""

    @staticmethod
    def create_all_agents(ctx: ResumeEngineContext) -> List[ResumeAgent]:
        """
        Create all available agents.

        Args:
            ctx: Resume engine context

        Returns:
            List of all resume agents
        """
        return [
            ContentQualityAgent(ctx),
            FactCheckAgent(ctx),
            BrandComplianceAgent(ctx),
            RgTemplateOptimizerAgent(ctx),
            SectionBalanceAgent(ctx),
            ATSCompatibilityAgent(ctx),
            TestPilot(ctx),
        ]

    @staticmethod
    def create_agents_by_name(ctx: ResumeEngineContext, names: List[str]) -> List[ResumeAgent]:
        """
        Create specific agents by name.

        Args:
            ctx: Resume engine context
            names: List of agent class names to create

        Returns:
            List of requested agents
        """
        agent_map = {
            "ContentQualityAgent": ContentQualityAgent,
            "FactCheckAgent": FactCheckAgent,
            "BrandComplianceAgent": BrandComplianceAgent,
            "TemplateOptimizerAgent": TemplateOptimizerAgent,
            "SectionBalanceAgent": SectionBalanceAgent,
            "ATSCompatibilityAgent": ATSCompatibilityAgent,
            "TestPilot": TestPilot,
            "StrategicPlannerAgent": StrategicPlannerAgent,
            "ReflectionAgent": ReflectionAgent,
        }

        agents = []
        for name in names:
            if name in agent_map:
                agents.append(agent_map[name](ctx))
        return agents

    @staticmethod
    def create_quality_agents(ctx: ResumeEngineContext) -> List[ResumeAgent]:
        """
        Create quality-focused agents.

        Args:
            ctx: Resume engine context

        Returns:
            List of quality-focused agents
        """
        return [
            ContentQualityAgent(ctx),
            FactCheckAgent(ctx),
            TestPilot(ctx),
        ]

    @staticmethod
    def create_compliance_agents(ctx: ResumeEngineContext) -> List[ResumeAgent]:
        """
        Create compliance-focused agents.

        Args:
            ctx: Resume engine context

        Returns:
            List of compliance-focused agents
        """
        return [
            BrandComplianceAgent(ctx),
            SectionBalanceAgent(ctx),
            ATSCompatibilityAgent(ctx),
            TestPilot(ctx),
        ]

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()


class HealingCycle:
    """Manages a single healing cycle."""

    def __init__(self, ctx: ResumeEngineContext, cycle_number: int) -> None:
        """
        Initialize healing cycle.

        Args:
            ctx: Resume engine context
            cycle_number: Current cycle number (1-indexed)
        """
        self.ctx: ResumeEngineContext = ctx
        self.cycle_number: int = cycle_number
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

    async def execute(self, strategy: HealingStrategy) -> CycleResult:
        """
        Execute the healing cycle with the given strategy.

        Args:
            strategy: Healing strategy to apply

        Returns:
            CycleResult with cycle execution details
        """
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

        return CycleResult(
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

    def _build_agenda(self, strategy: HealingStrategy) -> List[ResumeAgent]:
        """
        Build the agent agenda based on strategy.

        Args:
            strategy: Healing strategy to apply

        Returns:
            List of agents to execute
        """
        if strategy == HealingStrategy.FULL_DIAGNOSTIC:
            return AgentFactory.create_all_agents(self.ctx)

        elif strategy == HealingStrategy.VERIFICATION_ONLY:
            return [TestPilot(self.ctx)]

        elif strategy == HealingStrategy.QUALITY_FOCUS:
            return AgentFactory.create_quality_agents(self.ctx)

        elif strategy == HealingStrategy.COMPLIANCE_FOCUS:
            return AgentFactory.create_compliance_agents(self.ctx)

        elif strategy == HealingStrategy.SURGICAL_STRIKE:
            # Get agents based on current signals
            agent_names = SignalRouterAgent.get_agents_for_signals(self.ctx.signals)
            if not agent_names:
                agent_names = ["TestPilot"]  # Default to verification
            agents = AgentFactory.create_agents_by_name(self.ctx, agent_names)
            # Always include TestPilot for verification
            if not any(isinstance(a, TestPilot) for a in agents):
                agents.append(TestPilot(self.ctx))
            return agents

        return AgentFactory.create_all_agents(self.ctx)

    def _check_rollback_conditions(self) -> bool:
        """
        Check if rollback should be triggered.

        Returns:
            True if rollback conditions are met, False otherwise
        """
        # Rollback on critical signals
        if SignalRouterAgent.has_critical_signal(self.ctx.signals):
            return True

        # Rollback on test failure after cycle 1 with modifications
        if (self.cycle_number > 1 and
            self.ctx.has_signal("TEST_FAILURE") and
            self.ctx.section_backups):
            return True

        return False

    def _execute_rollback(self) -> None:
        """
        Execute rollback of all changes.

        Reverts resume to last backup and clears critical signals.
        """
        print(f"   🚨 Cycle {self.cycle_number}: Triggering rollback...")
        self.ctx.rollback_all()

        # Clear critical signals after rollback
        for signal in list(self.ctx.signals):
            if signal in SignalRouterAgent.CRITICAL_SIGNALS or signal == "TEST_FAILURE":
                self.ctx.remove_signal(signal)


async def run_self_healing_mission(
    JobDescription: str,
    master_resume: Dict[str, Any],
    user_profile: Optional[Dict[str, Any]] = None,
    max_cycles: int = 5,
    enable_reflection: bool = True,
) -> HealingResult:
    """
    Run a self-healing resume generation mission.

    This is the main entry point for Phase 2 self-healing functionality.

    Args:
        JobDescription: Target job description
        master_resume: User's master resume data
        user_profile: Optional user profile for fact-checking
        max_cycles: Maximum healing cycles (default 5)
        enable_reflection: Whether to run reflection agent at end

    Returns:
        HealingResult with complete execution details
    """
    # Initialize context
    ctx = ResumeEngineContext()
    ctx.JobDescription = JobDescription
    ctx.current_resume = master_resume.copy()
    ctx.user_profile = user_profile or {}
    ctx.max_cycles = max_cycles

    # Create and run orchestrator
    orchestrator = RgHealingOrchestratorAgent(
        ctx=ctx,
        max_cycles=max_cycles,
        enable_reflection=enable_reflection,
    )

    return await orchestrator.run()


class AutomaticRollback:
    """Handles automatic rollback on critical failures."""

    def __init__(self, ctx: ResumeEngineContext) -> None:
        """
        Initialize automatic rollback handler.

        Args:
            ctx: Resume engine context
        """
        self.ctx: ResumeEngineContext = ctx
        self.rollback_count: int = 0
        self.max_rollbacks: int = 3

    def should_rollback(self) -> bool:
        """
        Determine if rollback should be triggered.

        Returns:
            True if rollback should be triggered, False otherwise
        """
        if self.rollback_count >= self.max_rollbacks:
            return False  # Prevent infinite rollback loop

        return SignalRouterAgent.has_critical_signal(self.ctx.signals)

    def execute_rollback(self) -> bool:
        """
        Execute rollback and return success status.

        Returns:
            True if rollback was executed, False otherwise
        """
        if not self.should_rollback():
            return False

        self.ctx.rollback_all()
        self.rollback_count += 1

        # Clear critical signals
        for signal in list(self.ctx.signals):
            if signal in SignalRouterAgent.CRITICAL_SIGNALS:
                self.ctx.remove_signal(signal)

        return True

    def reset(self) -> Any:
        """Reset rollback counter."""
        self.rollback_count = 0
