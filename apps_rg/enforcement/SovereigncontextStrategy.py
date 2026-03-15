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
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


@dataclass
class SovereignContext:
    """
    The Single Source of Truth for runtime execution.
    Passed to every engine. Replaces the legacy 'ctx' dictionary.
    """

    buffer: ImmutableStagingBuffer = field(default_factory=ImmutableStagingBuffer)
    trace: TraceRegistry = field(default_factory=TraceRegistry)
    toggles: ReasoningToggles = field(default_factory=get_toggles)
    mission_id: str = "default"
    signals: set = field(default_factory=set)

    def add_signal(self, signal: str) -> None:
        """Add a signal to the context and log it."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SovereignContext.add_signal")

        self.signals.add(signal)
        self.trace.add_trace("signal_fired", {"signal": signal})

    def record_result(self, agent: str, passed: bool, details: str, data: Any = None) -> None:
        """Legacy adapter for record_result."""
        status = "SUCCESS" if passed else "FAILURE"
        self.trace.add_trace(
            f"agent_{status.lower()}", {"agent": agent, "passed": passed, "details": details}
        )
        if data:
            try:
                self.buffer.write(f"{agent}.output", data, source_agent=agent)
            except PermissionError:
                pass

    def get_signal_count(self) -> int:
        """Return the number of signals fired."""
        return len(self.signals)

    def has_signal(self, signal: str) -> bool:
        """Check if a specific signal has been fired."""
        return signal in self.signals

    def clear_signals(self) -> None:
        """Clear all signals (use with caution)."""
        self.signals.clear()
