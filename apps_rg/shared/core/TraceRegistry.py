"""
Trace Registry for RG Sovereign Architecture.

A structured audit log for tracking agent execution steps and decisions.
Aligned with LIC TraceRegistry pattern.

HARDENING: Upgrades from simple logging to Span Tracing (Start/End)
to measure performance latency and token usage.
"""

from __future__ import annotations

import time
import json
import logging
from dataclasses import dataclass, field
from typing import Any
from pathlib import Path
from datetime import datetime

from agentic_core.L2_execution.mcp.mcp_hardened_mixin import mcp_hardened_mixin

Logger = logging.getLogger(__name__)


@dataclass
class AgentTrace:
    """A single execution span."""

    trace_id: str
    agent_name: str
    action: str
    start_time: float
    end_time: float = 0.0
    status: str = "RUNNING"
    error: str | None = None
    tokens_used: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def duration_ms(self) -> float:
        end = self.end_time if self.end_time > 0 else time.time()
        return (end - self.start_time) * 1000


@dataclass
class TraceRegistry(MCPHardenedMixin):
    """
    Centralized Telemetry Aggregator.
    Tracks execution spans, latency, and cost.

    RG-Specific Trace Types:
    - PHASE_START: Agent phase beginning
    - PHASE_COMPLETE: Agent phase completion
    - PHASE_ERROR: Agent phase failure
    - PHASE_STEP: Intermediate step within a phase
    - DATA_ERROR: Data validation failure
    - EXTRACTION_START: Clerk extraction beginning
    - ENRICHMENT_START: Enrichment beginning
    - GENERATION_START: Resume generation beginning
    - VALIDATION_PASS: Quality validation passed
    - VALIDATION_FAIL: Quality validation failed
    - GATE_DECISION: Pass/fail gate decision
    - ORCHESTRATOR_START: Workflow beginning
    - ORCHESTRATOR_RETRY: Retry loop triggered
    - ORCHESTRATOR_ERROR: Workflow failure
    """

    persistence_path: Path | None = None
    _traces: list[AgentTrace] = field(default_factory=list)
    _active_spans: dict[str, AgentTrace] = field(default_factory=dict)

    def start_span(self, trace_id: str, agent_name: str, action: str) -> str:
        """Begin tracking an action."""
        span_key = f"{trace_id}:{agent_name}:{action}:{time.time()}"
        trace = AgentTrace(
            trace_id=trace_id, agent_name=agent_name, action=action, start_time=time.time()
        )
        self._traces.append(trace)
        self._active_spans[span_key] = trace
        return span_key

    def end_span(
        self, span_key: str, status: str = "SUCCESS", error: str = None, tokens: int = 0
    ) -> None:
        """Complete an active action."""
        if span_key not in self._active_spans:
            Logger.warning(f"Attempted to close unknown span: {span_key}")
            return

        trace = self._active_spans.pop(span_key)
        trace.end_time = time.time()
        trace.status = status
        trace.error = error
        trace.tokens_used = tokens

        if self.persistence_path:
            self._persist_trace(trace)

    def add_trace(self, event_type: str, details: dict[str, Any]) -> None:
        """
        Legacy API: Records a trace event.
        Creates a completed span for backward compatibility.

        Args:
            event_type: Category of the event (e.g., 'DECISION', 'ERROR').
            details: Contextual data for the event.
        """
        trace = AgentTrace(
            trace_id=f"legacy_{time.time()}",
            agent_name=details.get("agent", "SYSTEM"),
            action=event_type,
            start_time=time.time(),
            end_time=time.time(),
            status="COMPLETE",
            metadata=details,
        )
        self._traces.append(trace)

    def get_summary(self) -> dict[str, Any]:
        """Performance report."""
        completed = [t for t in self._traces if t.end_time > 0]
        failures = [t for t in completed if t.status == "FAILURE"]
        avg_latency = sum(t.duration_ms for t in completed) / max(len(completed), 1)

        return {
            "total_spans": len(self._traces),
            "completed": len(completed),
            "failures": len(failures),
            "avg_latency_ms": round(avg_latency, 2),
            "total_tokens": sum(t.tokens_used for t in completed),
        }

    def get_traces(self) -> list[dict[str, Any]]:
        """Returns a list of trace dictionaries for backward compatibility."""
        return [
            {
                "trace_id": t.trace_id,
                "agent_name": t.agent_name,
                "action": t.action,
                "status": t.status,
                "duration_ms": t.duration_ms,
                "tokens_used": t.tokens_used,
                "error": t.error,
                "metadata": t.metadata,
            }
            for t in self._traces
        ]

    def clear(self) -> None:
        """Clears the registry (use with caution)."""
        self._traces.clear()
        self._active_spans.clear()

    def count(self, trace_type: str) -> int:
        """Count occurrences of a specific action type."""
        return sum(1 for t in self._traces if t.action == trace_type)

    def get_by_type(self, trace_type: str) -> list[dict[str, Any]]:
        """Get all traces of a specific action type."""
        return [
            {
                "trace_id": t.trace_id,
                "agent_name": t.agent_name,
                "action": t.action,
                "status": t.status,
                "duration_ms": t.duration_ms,
            }
            for t in self._traces
            if t.action == trace_type
        ]

    def get_latest(self, trace_type: str) -> dict[str, Any] | None:
        """Get the most recent trace of a specific action type."""
        matches = [t for t in self._traces if t.action == trace_type]
        if not matches:
            return None
        t = matches[-1]
        return {
            "trace_id": t.trace_id,
            "agent_name": t.agent_name,
            "action": t.action,
            "status": t.status,
            "duration_ms": t.duration_ms,
        }

    def _persist_trace(self, trace: AgentTrace) -> None:
        """Write trace details to disk."""
        try:
            if self.persistence_path:
                entry = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "agent": trace.agent_name,
                    "action": trace.action,
                    "status": trace.status,
                    "error": trace.error,
                    "duration": trace.duration_ms,
                    "tokens_used": trace.tokens_used,
                }
                with open(self.persistence_path, "a") as f:
                    f.write(json.dumps(entry) + "\n")
        except Exception as e:
            Logger.error(f"Failed to persist trace: {e}")

    def _persist_failure(self, trace: AgentTrace) -> None:
        """Write failure details to disk (legacy method)."""
        self._persist_trace(trace)
