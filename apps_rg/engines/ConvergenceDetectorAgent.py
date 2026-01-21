from dataclasses import dataclass
"""
ConvergenceDetectorAgent - Extracted for one-class-per-file pattern.

Originally from: SignalRouterAgent.py
Extracted: 2026-01-06 (Surgical Extraction)
"""


from __future__ import annotations
from typing import List, Set, Dict, Any
from agentic_core.L3_orchestration.workflow_engines.l3_subatomic_testing_mixin import L3SubatomicTestingMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin

@dataclass
class ConvergenceDetectorAgent(MCPHardenedMixin, HealerMixin, L3SubatomicTestingMixin):
    """
    Detects when the system has converged (Resume Generator app-specific).

    Tracks signal state history to detect convergence and oscillation patterns.

    Attributes:
        ctx: Resume engine context
        history: List of signal states from previous cycles
    """

    def __init__(self, ctx: 'ResumeEngineContext') -> None:
        """
        Initialize convergence detector.

        Args:
            ctx: Resume engine context
        """
        self.ctx = ctx
        self.history: List[Set[str]] = []

    def record_state(self) -> None:
        """
        Record current signal state to history.

        Appends a snapshot of current signals for convergence analysis.
        """
        self.history.append(set(self.ctx.signals))

    def is_converged(self) -> bool:
        """
        Check if system has converged.

        Returns:
            True if system has reached stable state, False otherwise
        """
        return self.ctx.is_converged()

    def is_oscillating(self, window: int = 3) -> bool:
        """
        Check if signals are oscillating (stuck in a loop).

        Args:
            window: Number of cycles to check for oscillation (default: 3)

        Returns:
            True if signals are repeating in a pattern, False otherwise
        """
        if len(self.history) < window * 2:
            return False

        recent: List[Set[str]] = self.history[-window:]
        earlier: List[Set[str]] = self.history[-window * 2:-window]

        # Check if recent states match earlier states
        for i, state in enumerate(recent):
            if i < len(earlier) and state == earlier[i]:
                return True

        return False

    def get_stuck_signals(self) -> Set[str]:
        """
        Get signals that have persisted across multiple cycles.

        Returns:
            Set of signals present in both last two cycles
        """
        if len(self.history) < 2:
            return set()

        return self.history[-1] & self.history[-2]

    def heal_repository(self, dry_run: bool = True, execute: bool = False, **kwargs: Any) -> Dict[str, Any]:
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
