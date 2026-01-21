"""
UnifiedOrchestratorAgent - Strategy Pattern Orchestration Engine

This module implements the unified orchestration engine using the Strategy Pattern.
The engine handles the generic execution loop (logging, progress, error catching)
while delegating the specific "what to run" logic to injected strategies.

USAGE:
    from agentic_core.L3_orchestration.unified_orchestrator import UnifiedOrchestratorAgent
    from agentic_core.L5_safety.validators.healing_strategy import HealingStrategy

    strategy = HealingStrategy(project_root=Path.cwd())
    orchestrator = UnifiedOrchestratorAgent(strategy=strategy)
    result = orchestrator.run_mission({"dry_run": True})

SSOT PRINCIPLE:
    All orchestration should flow through this unified engine.
    Specific behaviors are encapsulated in MissionStrategy implementations.
"""

# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: guardrail, healer, memory, prompt, workflow
# This boosts alignment detection — review and integrate appropriately

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from agentic_core.utils.core_extensions.infrastructure_mixin import InfrastructureMixin

Logger = logging.getLogger(__name__)


@runtime_checkable
class MissionStrategy(Protocol):
    """
    Protocol defining the contract for mission strategies.

    Strategies encapsulate the specific logic of what agents to run
    and in what order, while the orchestrator handles the execution loop.
    """

    @property
    def name(self) -> str:
        """Return the strategy name for logging/identification."""
        ...

    def get_tiers(self) -> dict[str, list[str]]:
        """
        Return the tiered execution plan.

        Returns:
            Dictionary mapping tier names to lists of agent names.
            Example: {"Tier 1: Pre-Flight": ["SyntaxValidatorAgent"]}
        """
        ...

    def get_agent(self, agent_name: str) -> Any | None:
        """
        Get or create an agent instance by name.

        Args:
            agent_name: Name of the agent to retrieve

        Returns:
            Agent instance or None if not available
        """
        ...

    def execute_agent(
        self,
        agent: Any,
        agent_name: str,
        dry_run: bool = True,
        execute: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Execute a single agent and return results.

        Args:
            agent: The agent instance to execute
            agent_name: Name of the agent (for logging)
            dry_run: If True, only report violations
            execute: If True, apply fixes
            **kwargs: Additional agent-specific parameters

        Returns:
            Dictionary with execution results:
                - status: 'PASS', 'FAIL', 'ERROR'
                - violations_found: int
                - violations_fixed: int
                - execution_time_ms: float
                - error_message: Optional[str]
        """
        ...

    def should_abort_tier(
        self, tier_name: str, tier_results: list[dict[str, Any]], execute: bool
    ) -> bool:
        """
        Determine if execution should abort after a tier.

        Args:
            tier_name: Name of the completed tier
            tier_results: Results from all agents in the tier
            execute: Whether we're in execute mode

        Returns:
            True if execution should abort, False to continue
        """
        ...


@dataclass
class AgentExecutionResult:
    """Result from a single agent execution."""

    agent_name: str
    status: str  # 'PASS', 'FAIL', 'ERROR', 'SKIPPED'
    violations_found: int = 0
    violations_fixed: int = 0
    execution_time_ms: float = 0.0
    error_message: str | None = None
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class MissionReport:
    """Comprehensive mission execution report."""

    timestamp: str
    strategy_name: str
    total_agents_run: int
    agents_passed: int
    agents_failed: int
    agents_errored: int
    total_violations: int
    total_fixes: int
    execution_time_ms: float
    agent_results: list[AgentExecutionResult] = field(default_factory=list)
    overall_status: str = "UNKNOWN"
    aborted: bool = False
    abort_reason: str | None = None

    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_agents_run == 0:
            return 100.0
        return (self.agents_passed / self.total_agents_run) * 100

    @property
    def is_stable(self) -> bool:
        """Check if the mission result indicates stability."""
        return self.overall_status == "PASS" and not self.aborted


class UnifiedOrchestratorAgent(InfrastructureMixin):
    """
    Unified Orchestration Engine implementing IOrchestrator.

    This engine uses the Strategy Pattern to separate the generic
    execution loop from the specific mission logic. The engine handles:
    - Logging and progress tracking
    - Error catching and crash containment
    - Result aggregation and reporting

    The injected MissionStrategy handles:
    - Which agents to run
    - Tier definitions and ordering
    - Agent instantiation and execution
    - Abort conditions

    Implements IOrchestrator protocol for consistent interface.
    """

    def __init__(
        self,
        strategy: MissionStrategy,
        project_root: Path | None = None,
        name: str = "UnifiedOrchestrator",
    ) -> None:
        """
        Initialize the unified orchestrator.

        Args:
            strategy: The mission strategy defining what to execute
            project_root: Root path for the project (defaults to cwd)
            name: Name for this orchestrator instance
        """
        super().__init__()

        self.strategy = strategy
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.name = name
        self.logger = Logger

        # Verify infrastructure initialization
        self.verify_state()

        self.logger.debug(f"[{self.name}] Initialized with strategy: {strategy.name}")

    def run_mission(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        Execute a mission using the injected strategy.

        This method implements the IOrchestrator protocol and handles
        the generic execution loop with crash containment.

        Args:
            context: Mission configuration containing:
                - dry_run (bool): If True, only report without fixing
                - execute (bool): If True, execute healing actions
                - agents (List[str], optional): Specific agents to run
                - max_depth (int, optional): Maximum recursion depth

        Returns:
            Mission result dictionary containing:
                - status (str): 'SUCCESS', 'PARTIAL', 'FAILED'
                - total_violations (int): Total violations found
                - total_fixed (int): Total violations fixed
                - agent_results (List[dict]): Per-agent results
                - execution_time_ms (int): Total execution time
                - is_stable (bool): Whether repository is stable
        """
        start_time = time.time()

        # Extract context parameters with safe defaults
        dry_run = context.get("dry_run", True)
        execute = context.get("execute", False)

        self.logger.info(f"\n{'=' * 60}")
        self.logger.info(f"[{self.name}] Starting mission: {self.strategy.name}")
        self.logger.info(f"  Mode: {'EXECUTE' if execute else 'DRY-RUN'}")
        self.logger.info(f"{'=' * 60}")

        agent_results: list[AgentExecutionResult] = []
        total_violations = 0
        total_fixes = 0
        aborted = False
        abort_reason: str | None = None

        try:
            # Get tiered execution plan from strategy
            tiers = self.strategy.get_tiers()

            for tier_num, (tier_name, agent_names) in enumerate(tiers.items(), 1):
                # Check if this tier should be executed (tier filtering)
                if hasattr(self.strategy, "should_run_tier") and not self.strategy.should_run_tier(
                    tier_name
                ):
                    skip_msg = (
                        self.strategy.get_tier_skip_message(tier_name)
                        if hasattr(self.strategy, "get_tier_skip_message")
                        else f"⏭️  SKIPPING {tier_name}"
                    )
                    self.logger.info(f"\n{skip_msg}")
                    continue

                self.logger.info(f"\n[TIER {tier_num}/{len(tiers)}] {tier_name}")

                tier_results: list[dict[str, Any]] = []

                for agent_name in agent_names:
                    result = self._execute_agent_safely(
                        agent_name=agent_name, dry_run=dry_run, execute=execute
                    )

                    agent_results.append(result)
                    tier_results.append(
                        {
                            "agent_name": result.agent_name,
                            "status": result.status,
                            "violations_found": result.violations_found,
                            "violations_fixed": result.violations_fixed,
                        }
                    )

                    total_violations += result.violations_found
                    total_fixes += result.violations_fixed

                    # Log result
                    status_icon = (
                        "✅"
                        if result.status == "PASS"
                        else "⚠️"
                        if result.status == "FAIL"
                        else "❌"
                    )
                    self.logger.info(
                        f"  {status_icon} {agent_name}: {result.status} "
                        f"(violations: {result.violations_found}, fixed: {result.violations_fixed})"
                    )

                # Check if we should abort after this tier
                if self.strategy.should_abort_tier(tier_name, tier_results, execute):
                    aborted = True
                    abort_reason = f"Abort triggered after tier: {tier_name}"
                    self.logger.warning(f"🛑 {abort_reason}")
                    break

        except Exception as e:
            # Crash containment - mission never dies mid-flight
            self.logger.error(f"[{self.name}] Mission crashed: {e}")
            aborted = True
            abort_reason = f"Mission crashed: {str(e)}"

        # Calculate final metrics
        execution_time_ms = (time.time() - start_time) * 1000
        agents_passed = sum(1 for r in agent_results if r.status == "PASS")
        agents_failed = sum(1 for r in agent_results if r.status == "FAIL")
        agents_errored = sum(1 for r in agent_results if r.status == "ERROR")

        # Determine overall status
        if aborted:
            overall_status = "FAILED"
        elif agents_errored > 0 or agents_failed > 0:
            overall_status = "PARTIAL" if agents_passed > 0 else "FAILED"
        else:
            overall_status = "SUCCESS"

        report = MissionReport(
            timestamp=datetime.now().isoformat(),
            strategy_name=self.strategy.name,
            total_agents_run=len(agent_results),
            agents_passed=agents_passed,
            agents_failed=agents_failed,
            agents_errored=agents_errored,
            total_violations=total_violations,
            total_fixes=total_fixes,
            execution_time_ms=execution_time_ms,
            agent_results=agent_results,
            overall_status=overall_status,
            aborted=aborted,
            abort_reason=abort_reason,
        )

        # Log summary
        self._log_summary(report)

        # Return IOrchestrator-compliant result
        return {
            "status": report.overall_status,
            "total_violations": report.total_violations,
            "total_fixed": report.total_fixes,
            "agent_results": [
                {
                    "agent_name": r.agent_name,
                    "status": r.status,
                    "violations_found": r.violations_found,
                    "violations_fixed": r.violations_fixed,
                    "execution_time_ms": r.execution_time_ms,
                    "error_message": r.error_message,
                }
                for r in report.agent_results
            ],
            "execution_time_ms": int(report.execution_time_ms),
            "is_stable": report.is_stable,
            "aborted": report.aborted,
            "abort_reason": report.abort_reason,
            "success_rate": report.success_rate,
        }

    def validate_stability(self, result: dict[str, Any]) -> bool:
        """
        Validate whether the mission result indicates a stable repository.

        Implements IOrchestrator protocol.

        Args:
            result: Mission result from run_mission()

        Returns:
            True if repository is stable, False otherwise
        """
        # Check for explicit stability flag
        if "is_stable" in result:
            return result["is_stable"]

        # Fallback: check status and violations
        status = result.get("status", "UNKNOWN")
        total_violations = result.get("total_violations", 0)
        total_fixed = result.get("total_fixed", 0)
        aborted = result.get("aborted", False)

        # Stable if: SUCCESS status, no unfixed violations, not aborted
        return status == "SUCCESS" and total_violations <= total_fixed and not aborted

    def _execute_agent_safely(
        self, agent_name: str, dry_run: bool = True, execute: bool = False, **kwargs: Any
    ) -> AgentExecutionResult:
        """
        Execute a single agent with crash containment.

        This method wraps agent execution in a try/except to ensure
        that a single agent crash doesn't bring down the entire mission.

        Args:
            agent_name: Name of the agent to execute
            dry_run: If True, only report violations
            execute: If True, apply fixes
            **kwargs: Additional parameters

        Returns:
            AgentExecutionResult with execution details
        """
        start_time = time.time()

        try:
            # Get agent from strategy
            agent = self.strategy.get_agent(agent_name)

            if agent is None:
                return AgentExecutionResult(
                    agent_name=agent_name,
                    status="ERROR",
                    error_message=f"Agent '{agent_name}' not available",
                )

            # Execute via strategy
            result = self.strategy.execute_agent(
                agent=agent, agent_name=agent_name, dry_run=dry_run, execute=execute, **kwargs
            )

            execution_time_ms = (time.time() - start_time) * 1000

            return AgentExecutionResult(
                agent_name=agent_name,
                status=result.get("status", "UNKNOWN"),
                violations_found=result.get("violations_found", 0),
                violations_fixed=result.get("violations_fixed", 0),
                execution_time_ms=execution_time_ms,
                error_message=result.get("error_message"),
                details=result,
            )

        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000
            self.logger.error(f"[{self.name}] Agent '{agent_name}' crashed: {e}")

            return AgentExecutionResult(
                agent_name=agent_name,
                status="ERROR",
                execution_time_ms=execution_time_ms,
                error_message=str(e),
            )

    def _log_summary(self, report: MissionReport) -> None:
        """Log mission summary."""
        self.logger.info(f"\n{'=' * 60}")
        self.logger.info(f"[{self.name}] MISSION SUMMARY")
        self.logger.info(f"{'=' * 60}")
        self.logger.info(f"  Strategy: {report.strategy_name}")
        self.logger.info(f"  Status: {report.overall_status}")
        self.logger.info(f"  Agents Run: {report.total_agents_run}")
        self.logger.info(f"  Passed: {report.agents_passed}")
        self.logger.info(f"  Failed: {report.agents_failed}")
        self.logger.info(f"  Errored: {report.agents_errored}")
        self.logger.info(f"  Total Violations: {report.total_violations}")
        self.logger.info(f"  Total Fixes: {report.total_fixes}")
        self.logger.info(f"  Success Rate: {report.success_rate:.1f}%")
        self.logger.info(f"  Execution Time: {report.execution_time_ms:.0f}ms")
        if report.aborted:
            self.logger.info(f"  Aborted: {report.abort_reason}")
        self.logger.info(f"{'=' * 60}")


# Verify IOrchestrator protocol compliance at module load
def _verify_protocol_compliance() -> None:
    """Verify UnifiedOrchestratorAgent implements IOrchestrator."""
    # This will be checked at runtime when an instance is created
    # We can't check here because we need a strategy instance
    pass


__all__ = [
    "UnifiedOrchestratorAgent",
    "MissionStrategy",
    "MissionReport",
    "AgentExecutionResult",
]
