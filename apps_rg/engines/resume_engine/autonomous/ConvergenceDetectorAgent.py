"""
ConvergenceDetectorAgent - Extracted for one-class-per-file pattern.

Originally from: SignalRouterAgent.py
Extracted: 2026-01-06 (Surgical Extraction)
"""


from __future__ import annotations

class ConvergenceDetectorAgent:
    """Detects when the system has converged."""

    def __init__(self, ctx: ResumeEngineContext):
        self.ctx = ctx
        self.history: List[Set[str]] = []

    def record_state(self):
        """Record current signal state."""
        self.history.append(set(self.ctx.signals))

    def is_converged(self) -> bool:
        """Check if system has converged."""
        return self.ctx.is_converged()

    def is_oscillating(self, window: int = 3) -> bool:
        """Check if signals are oscillating (stuck in a loop)."""
        if len(self.history) < window * 2:
            return False

        recent = self.history[-window:]
        earlier = self.history[-window * 2:-window]

        # Check if recent states match earlier states
        for i, state in enumerate(recent):
            if i < len(earlier) and state == earlier[i]:
                return True

        return False

    def get_stuck_signals(self) -> Set[str]:
        """Get signals that have persisted across multiple cycles."""
        if len(self.history) < 2:
            return set()

        return self.history[-1] & self.history[-2]

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()
