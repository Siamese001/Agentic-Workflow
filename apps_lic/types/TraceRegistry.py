"""
Trace Registry.

A structured audit log for tracking agent execution steps and decisions.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from agentic_core.mixins.mcp_hardened_mixin import mcp_hardened_mixin

    class MCPHardenedMixin(mcp_hardened_mixin):
        pass
except ImportError:

    class MCPHardenedMixin:
        pass


@dataclass
class TraceRegistry(MCPHardenedMixin):
    """
    Registry for execution traces. Maintains an ordered log of events.
    """

    persistence_path: Path = None
    _traces: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        if self.persistence_path:
            self.persistence_path.parent.mkdir(parents=True, exist_ok=True)
            if self.persistence_path.exists():
                self._load_from_disk()
            else:
                self._flush_to_disk()

    def _load_from_disk(self):
        """Load traces from JSONL file (one JSON object per line)."""
        if self.persistence_path and self.persistence_path.exists():
            try:
                with self.persistence_path.open("r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            self._traces.append(json.loads(line))
            except FileNotFoundError:
                self._flush_to_disk()

    def _flush_to_disk(self):
        """Initialize/clear the trace file."""
        if self.persistence_path:
            self.persistence_path.parent.mkdir(parents=True, exist_ok=True)
            with self.persistence_path.open("w", encoding="utf-8"):
                pass

    def _append_to_disk(self, trace: dict[str, Any]) -> None:
        """Append a single trace to JSONL file for crash resilience."""
        if self.persistence_path:
            with self.persistence_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(trace) + "\n")

    def add_trace(self, event_type: str, details: dict[str, Any]) -> None:
        """
        Records a trace event with optional disk persistence.

        Args:
            event_type: Category of the event (e.g., 'DECISION', 'ERROR').
            details: Contextual data for the event.
        """
        entry = {"timestamp": datetime.utcnow().isoformat(), "type": event_type, "details": details}
        self._traces.append(entry)
        if self.persistence_path:
            self._append_to_disk(entry)

    def get_traces(self) -> list[dict[str, Any]]:
        """Returns a copy of the full trace history."""
        return list(self._traces)

    def clear(self) -> None:
        """Clears the registry (use with caution)."""
        self._traces.clear()

    def count(self, trace_type: str) -> int:
        """Count occurrences of a specific trace type."""
        return sum(1 for t in self._traces if t["type"] == trace_type)
