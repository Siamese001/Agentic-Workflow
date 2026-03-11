"""
Sovereign Context for RG Sovereign Architecture.

This is the GLUE. It packages the ImmutableBuffer, TraceRegistry, and Toggles
into a single object passed to every engine.

HARDENING: Replaces the legacy 'ctx' dictionary with a type-safe container.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from apps_rg.config.ReasoningToggles import ReasoningToggles, get_toggles

from apps_rg.types.SovereignContext import ImmutableStagingBuffer, TraceRegistry


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

@dataclass
class SovereignContext:
    """
    The Single Source of Truth for runtime execution.
    Passed to every engine. Replaces the legacy 'ctx' dictionary.
    """

    buffer: ImmutableStagingBuffer = field(default_factory=ImmutableStagingBuffer)
    trace: TraceRegistry = field(default_factory=TraceRegistry)
    toggles: ReasoningToggles = field(default_factory=get_toggles)

    # Mission tracking
    mission_id: str = "default"

    # Legacy Compatibility (to prevent breaking batch 1-6 immediately)
    # These map old calls to new infra transparently
    signals: set = field(default_factory=set)

    def add_signal(self, signal: str) -> None:
        """Add a signal to the context and log it."""
        self.signals.add(signal)
        self.trace.add_trace("signal_fired", {"signal": signal})

    def record_result(self, agent: str, passed: bool, details: str, data: Any = None) -> None:
        """Legacy adapter for record_result."""
        status = "SUCCESS" if passed else "FAILURE"
        self.trace.add_trace(
            f"agent_{status.lower()}",
            {"agent": agent, "passed": passed, "details": details},
        )

        # Writing result to buffer is safer
        if data:
            try:
                self.buffer.write(f"{agent}.output", data, source_agent=agent)
            except PermissionError:
                pass  # Already written, ignore in legacy mode

    def get_signal_count(self) -> int:
        """Return the number of signals fired."""
        return len(self.signals)

    def has_signal(self, signal: str) -> bool:
        """Check if a specific signal has been fired."""
        return signal in self.signals

    def clear_signals(self) -> None:
        """Clear all signals (use with caution)."""
        self.signals.clear()
