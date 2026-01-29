"""
RgHealingOrchestratorAgent - Extracted for one-class-per-file pattern.

Originally from: SignalRouterAgent.py
Extracted: 2026-01-06 (Surgical Extraction)

Orchestrates the complete self-healing process for resume generation.
"""

from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Any

from apps_rg.shared.core.agent_base import RGAgentBase
from agentic_core.base_agents.subatomic_testing_mixin import SubatomicTestingMixin


@dataclass
class RgHealingOrchestratorAgent(SubatomicTestingMixin, RGAgentBase):
    """
    Orchestrates the complete self-healing process for resume generation.

    Manages multiple healing cycles with convergence detection, budget tracking,
    and automatic rollback on critical failures.

    Attributes:
        ctx: Resume engine context containing resume state
        max_cycles: Maximum number of healing cycles to run
        enable_reflection: Whether to run reflection agent after healing
        cycle_results: List of results from each healing cycle
    """

    max_cycles: int = 5
    enable_reflection: bool = True
    cycle_results: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Initialize healing orchestrator."""
        super().__post_init__()
        # Initialize context if needed
        if not hasattr(self, "ctx") or self.ctx is None:
            from .context import ResumeEngineContext

            self.ctx = ResumeEngineContext()

    async def run(self) -> HealingResult:
        """
        Run the complete healing process.

        Executes multiple healing cycles until convergence is achieved,
        budget is exhausted, or max cycles is reached.

        Returns:
            HealingResult with complete execution details
        """
        start_time: float = time.time()

        print("\n" + "=" * 60)
        print("🧬 SELF-HEALING ORCHESTRATOR STARTED")
        print("=" * 60)

        convergence_cycle: int | None = None
        budget_exhausted: bool = False

        for cycle_num in range(1, self.max_cycles + 1):
            self.ctx.signal_healing_cycle(cycle_num)

            print(f"\n{'=' * 40}")
            print(f"🔄 HEALING CYCLE {cycle_num}/{self.max_cycles}")
            print(f"{'=' * 40}")

            # Clear per-cycle tracking
            self.ctx.modified_sections.clear()
            self.ctx.impact_zone.clear()

            # Determine strategy
            strategy = SignalRouterAgent.determine_strategy(
                cycle_num, self.ctx.signals, self.ctx.modified_sections
            )
            print(f"   📋 Strategy: {strategy.value}")

            # Execute cycle
            cycle = HealingCycle(self.ctx, cycle_num)
            result = await cycle.execute(strategy)
            self.cycle_results.append(result)

            # Log cycle result
            print(
                f"   ✅ Passed: {len(result.passed_agents)} | ❌ Failed: {len(result.failed_agents)}"
            )
            if result.rollback_triggered:
                print("   ⏪ Rollback triggered")

            # Check convergence
            if result.converged:
                convergence_cycle = cycle_num
                print(f"\n✅ CONVERGED at cycle {cycle_num}")
                break

            # Check budget
            if not self.ctx.budget.check_budget():
                budget_exhausted = True
                print(f"\n💸 Budget exhausted at cycle {cycle_num}")
                break

            # Log remaining signals
            if self.ctx.signals:
                print(f"   📡 Remaining signals: {list(self.ctx.signals)}")

        # Run reflection if enabled
        if self.enable_reflection:
            reflection = RgReflectionAgent(self.ctx)
            await reflection.execute()

        end_time: float = time.time()
        total_duration_ms: float = (end_time - start_time) * 1000

        success: bool = convergence_cycle is not None

        print("\n" + "=" * 60)
        print(f"{'✅ HEALING SUCCESS' if success else '⚠️ HEALING INCOMPLETE'}")
        print(f"   Cycles: {len(self.cycle_results)}/{self.max_cycles}")
        print(f"   Duration: {total_duration_ms:.0f}ms")
        print(f"   Budget: ${self.ctx.budget.current_cost:.4f}")
        print("=" * 60)

        return HealingResult(
            success=success,
            total_cycles=len(self.cycle_results),
            final_signals=set(self.ctx.signals),
            cycle_results=self.cycle_results,
            convergence_cycle=convergence_cycle,
            budget_exhausted=budget_exhausted,
            total_duration_ms=total_duration_ms,
            final_resume=self.ctx.current_resume.copy(),
        )

    def heal_repository(
        self, dry_run: bool = True, execute: bool = False, **kwargs: Any
    ) -> dict[str, Any]:
        """
        Autonomous healing method (Canon Key 51 compliance).

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes
            **kwargs: Additional healing parameters

        Returns:
            Dict with healing summary (violations, fixed, errors)
        """
        return super().heal_repository(dry_run, execute, **kwargs)
