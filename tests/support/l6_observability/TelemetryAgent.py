# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, prompt, state, validator, workflow
from __future__ import annotations

from dataclasses import dataclass

# This boosts alignment detection — review and integrate appropriately
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

"""
TelemetryAgent: Sovereign Structured Event Emitter

Emits structured telemetry events for observability and auditing.
Events cover:
- Compliance mission lifecycle (start, completion)
- Individual Violation detection
- Agent actions and outcomes
- System health signals

Designed for integration with:
- ComplianceOrchestratorAgent (primary emitter)
- ReportingAgent (can consume event log)
- Future: external sinks (e.g., logging backend, OpenTelemetry)

Placed in observability/telemetry per SSOT semantic registry:
  "Distributed telemetry, event emission, and structured observability events"

Depth: agentic_core/observability/telemetry/telemetry_agent.py
      → root/L1/L2/file.py → exactly 4 parts → Canon Key 3/12 compliant

In-memory buffer + optional file persistence.
Thread-safe via lock.
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Any

from agentic_core.base_agents.decorators import standard_heal

from agentic_core.utils.timeout_decorator_util import timeout

Logger = logging.getLogger(__name__)


@dataclass
class TelemetryAgent(SovereignBaseAgent):
    """
    Autonomous telemetry emission agent.
    Collects and emits structured events for sovereign observability.
    Events are JSON-serializable for future export.
    """

    EVENT_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR"}

    def __init__(
        self,
        project_root: Path | None = None,
        log_file: Path | None = None,
        max_events: int = 10_000,
    ) -> None:
        """
        Initialize telemetry buffer.

        Args:
            project_root: Optional project root directory
            log_file: If provided, append events to file (JSONL format)
            max_events: In-memory buffer limit (oldest dropped)
        """
        self.project_root: Path | None = project_root.resolve() if project_root else None
        self.log_file: Path | None = log_file
        self.max_events: int = max_events

        self._lock: Lock = Lock()
        self._events: list[dict[str, Any]] = []

        # Emit agent startup
        self.emit(
            event_type="telemetry.agent_started",
            level="INFO",
            details={"log_file": str(log_file) if log_file else None},
        )

    def emit(
        self,
        event_type: str,
        level: str = "INFO",
        agent: str = "TelemetryAgent",
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Emit a structured telemetry event.

        Args:
            event_type: Dot-separated event identifier (e.g., "compliance.scan_started")
            level: Event Severity (DEBUG, INFO, WARNING, ERROR)
            agent: Source agent name
            details: Additional structured data
        """
        if level not in self.EVENT_LEVELS:
            level = "INFO"

        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "level": level,
            "agent": agent,
            "details": details or {},
        }

        with self._lock:
            # Add to in-memory buffer
            self._events.append(event)

            # Enforce buffer limit (FIFO)
            if len(self._events) > self.max_events:
                self._events.pop(0)

        # Optional file persistence
        if self.log_file:
            self._write_to_file(event)

        # Also emit to standard Logger
        log_msg = f"[{event_type}] {agent}: {details}"
        if level == "ERROR":
            Logger.error(log_msg)
        elif level == "WARNING":
            Logger.warning(log_msg)
        elif level == "DEBUG":
            Logger.debug(log_msg)
        else:
            Logger.info(log_msg)

    def _write_to_file(self, event: dict[str, Any]) -> None:
        """Append event to log file (JSONL format)."""
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(event))
        except Exception as e:
            Logger.warning(f"[TelemetryAgent] Failed to write event to file: {e}")

    def get_events(
        self,
        event_type: str | None = None,
        level: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Query in-memory event buffer.

        Args:
            event_type: Filter by event type (prefix match)
            level: Filter by level
            limit: Max events to return (most recent)

        Returns:
            List of matching events
        """
        with self._lock:
            events = self._events.copy()

        # Filter
        if event_type:
            events = [e for e in events if e["event_type"].startswith(event_type)]
        if level:
            events = [e for e in events if e["level"] == level]

        # Limit (most recent)
        if limit:
            events = events[-limit:]

        return events

    def get_event_count(self) -> int:
        """Get total event count in buffer."""
        with self._lock:
            return len(self._events)

    def clear_events(self) -> None:
        """Clear in-memory event buffer."""
        with self._lock:
            self._events.clear()
        Logger.info("[TelemetryAgent] Event buffer cleared")

    # === Compliance-Specific Helpers ===

    def emit_compliance_scan_started(self, file_count: int) -> None:
        """Emit compliance scan start event."""
        self.emit(
            event_type="compliance.scan_started",
            level="INFO",
            agent="ComplianceOrchestratorAgent",
            details={"file_count": file_count},
        )

    def emit_compliance_scan_completed(self, violation_count: int, duration_seconds: float) -> None:
        """Emit compliance scan completion event."""
        self.emit(
            event_type="compliance.scan_completed",
            level="INFO" if violation_count == 0 else "WARNING",
            agent="ComplianceOrchestratorAgent",
            details={
                "violation_count": violation_count,
                "duration_seconds": round(duration_seconds, 2),
                "status": "clean" if violation_count == 0 else "violations_detected",
            },
        )

    def emit_violation_detected(self, file_path: str, ViolationType: str, message: str, agent: str) -> None:
        """Emit individual Violation detection event."""
        self.emit(
            event_type="compliance.violation_detected",
            level="WARNING",
            agent=agent,
            details={"file": file_path, "ViolationType": ViolationType, "message": message},
        )

    def emit_agent_action(
        self,
        agent: str,
        action: str,
        success: bool,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Emit agent action event."""
        self.emit(
            event_type=f"agent.{action}",
            level="INFO" if success else "ERROR",
            agent=agent,
            details={"action": action, "success": success, **(details or {})},
        )

    def export_to_file(self, output_path: Path) -> None:
        """
        Export all in-memory events to a file (JSONL format).
        Useful for archival or external analysis.
        """
        with self._lock:
            events = self._events.copy()

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                for event in events:
                    f.write(json.dumps(event) + "\n")
            Logger.info(f"[TelemetryAgent] Exported {len(events)} events to {output_path}")
        except Exception as e:
            Logger.error(f"[TelemetryAgent] Failed to export events: {e}")

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        Heal a specific violation (IHealerProtocol compliance).

        Args:
            violation: Dict containing violation details

        Returns:
            Dict with status, details, artifacts, errors
        """
        return {
            "status": "success",
            "details": "TelemetryAgent observability heal - no action required",
            "artifacts": [],
            "errors": [],
        }

    @timeout(300)
    @standard_heal
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
    ) -> dict[str, int]:
        """observability agent - invoke shared healing chain."""
        if _call_path is None:
            _call_path = set()
        # Invoke shared HealerMixin chain for diagnostics, rollback, MCP hardening
        super().heal_repository(
            dry_run=dry_run,
            execute=execute,
            depth=depth,
            max_depth=max_depth,
            _call_path=_call_path,
        )
        print(f"[{self.__class__.__name__}] observability agent - healing chain invoked")
        return {"skipped": 1}


# PascalCase is now the canonical name
