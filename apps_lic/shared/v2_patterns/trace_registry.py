"""
Trace Registry.

A structured audit log for tracking agent execution steps and decisions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from agentic_core.L2_execution.mcp.mcp_hardened_mixin import MCPHardenedMixin


@dataclass
class TraceRegistry(MCPHardenedMixin):
    """
    Registry for execution traces. Maintains an ordered log of events.
    """

    _traces: list[dict[str, Any]] = field(default_factory=list)

    def add_trace(self, event_type: str, details: dict[str, Any]) -> None:
        """
        Records a trace event.

        Args:
            event_type: Category of the event (e.g., 'DECISION', 'ERROR').
            details: Contextual data for the event.
        """
        entry = {"timestamp": datetime.utcnow().isoformat(), "type": event_type, "details": details}
        self._traces.append(entry)
        # Optional: Log to console via Mixin if needed, keeping it silent for now

    def get_traces(self) -> list[dict[str, Any]]:
        """Returns a copy of the full trace history."""
        return list(self._traces)

    def clear(self) -> None:
        """Clears the registry (use with caution)."""
        self._traces.clear()
