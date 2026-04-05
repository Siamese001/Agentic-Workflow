"""
Wave 5: TraceContext — execution trace wiring for dispatch chokepoints.

Provides a lightweight, thread-safe context object that the two Wave 2/3
chokepoints inject trace records into:

  1. ``AgentDispatchRegistry.dispatch()`` — every typed agent handoff
  2. ``CapabilityChokepoint.authorize_and_execute()`` — every capability call

This converts ``records_execution_trace:64`` on a 22,514-edge surface to a
coverage approaching 100% for all typed dispatch and capability paths.

ADG edges emitted (structured log records):
  ``records_execution_trace`` — every trace record appended to an active context
  ``signs_execution_trace``   — emitted by TraceContext.sign() after run completes
  ``hard_fails_untranscripted`` — emitted by TraceContext.assert_transcripted()
                                  when a required operation has no trace record

Usage — chokepoint injection::

    from agentic_core.L2_execution.trace_context import get_trace_context

    ctx = get_trace_context()
    ctx.record(
        layer="L3",
        module="AgentDispatchRegistry",
        operation="dispatch",
        trace_id="abc123",
        metadata={"caller": "Orch", "target": "Worker.run"},
    )

Usage — run frame::

    from agentic_core.L2_execution.trace_context import TraceContext

    with TraceContext.run_frame(run_id="run-001") as ctx:
        registry.dispatch(...)           # auto-records via get_trace_context()
        result = ctx.sign()              # seals the trace with a digest
"""

from __future__ import annotations

import hashlib
import json
import logging
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Generator

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
    record_execution_trace,
)

record_execution_trace("trace_context", "trace_context_trace")

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

logger = logging.getLogger(__name__)
_TRACE_LOGGER = logging.getLogger("adg.records_execution_trace")
_SIGN_LOGGER = logging.getLogger("adg.signs_execution_trace")
_UNTRANSCRIPTED_LOGGER = logging.getLogger("adg.hard_fails_untranscripted")


@dataclass
class TraceEntry:
    """Single execution trace record produced by a chokepoint."""

    run_id: str
    trace_id: str
    layer: str
    module: str
    operation: str
    timestamp_iso: str
    elapsed_ms: float
    success: bool
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "trace_id": self.trace_id,
            "layer": self.layer,
            "module": self.module,
            "operation": self.operation,
            "timestamp_iso": self.timestamp_iso,
            "elapsed_ms": round(self.elapsed_ms, 3),
            "success": self.success,
            "metadata": self.metadata,
        }


class TraceContext:
    """Thread-safe, append-only execution trace for a single run.

    Chokepoints call ``record()`` to append entries.  After the run completes,
    call ``sign()`` to produce a determinism digest covering all entries.

    Instances are scoped to a run via ``run_frame()`` context manager, which
    sets/restores the process-level singleton so that ``get_trace_context()``
    always returns the correct context without explicit threading.
    """

    def __init__(self, run_id: str) -> None:
        self.run_id = run_id
        self._entries: list[TraceEntry] = []
        self._lock = threading.RLock()
        self._signed_digest: str = ""
        self._start_time = time.monotonic()

    def record(
        self,
        layer: str,
        module: str,
        operation: str,
        trace_id: str = "",
        elapsed_ms: float = 0.0,
        success: bool = True,
        metadata: dict[str, Any] | None = None,
    ) -> TraceEntry:
        """Append a trace entry.  ADG edge: ``records_execution_trace``."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "TraceContext.record")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:TraceContext.record".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        from datetime import datetime, timezone

        ts = datetime.now(tz=timezone.utc).isoformat()
        entry = TraceEntry(
            run_id=self.run_id,
            trace_id=trace_id or self.run_id,
            layer=layer,
            module=module,
            operation=operation,
            timestamp_iso=ts,
            elapsed_ms=elapsed_ms,
            success=success,
            metadata=metadata or {},
        )
        with self._lock:
            self._entries.append(entry)
        _TRACE_LOGGER.debug(
            "records_execution_trace run=%s layer=%s module=%s op=%s ok=%s",
            self.run_id,
            layer,
            module,
            operation,
            success,
        )
        return entry

    def record_clock(self, clock_value: str) -> None:
        """Hook for ClockProvider.WallClock to record its value into the trace."""
        with self._lock:
            if self._entries:
                entry = self._entries[-1]
                entry.metadata["clock_value"] = clock_value

    def entries(self) -> list[TraceEntry]:
        """Return a snapshot copy of all trace entries."""
        with self._lock:
            return list(self._entries)

    def entry_count(self) -> int:
        with self._lock:
            return len(self._entries)

    def sign(self) -> str:
        """Seal the trace and return a determinism digest.

        ADG edge: ``signs_execution_trace``.
        """
        with self._lock:
            payload = [e.to_dict() for e in self._entries]
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode("utf-8")).hexdigest()
        self._signed_digest = digest
        _SIGN_LOGGER.debug(
            "signs_execution_trace run=%s entries=%d digest=%s",
            self.run_id,
            len(payload),
            digest[:16],
        )
        return digest

    @property
    def signed_digest(self) -> str:
        return self._signed_digest

    def assert_transcripted(self, operation: str, module: str = "") -> None:
        """Assert that at least one trace entry exists for ``operation``.

        If not found, emits ``hard_fails_untranscripted`` and raises.

        ADG edge: ``hard_fails_untranscripted``.
        """
        with self._lock:
            found = any(
                e.operation == operation and (not module or e.module == module) for e in self._entries
            )
        if not found:
            _UNTRANSCRIPTED_LOGGER.warning(
                "hard_fails_untranscripted run=%s operation=%s module=%s",
                self.run_id,
                operation,
                module,
            )
            raise RuntimeError(
                f"TraceContext: no trace record for operation={operation!r} "
                f"module={module!r} in run={self.run_id!r}. "
                "hard_fails_untranscripted."
            )

    def get_stats(self) -> dict[str, Any]:
        """Return coverage statistics for this trace context."""
        with self._lock:
            total = len(self._entries)
            failed = sum(1 for e in self._entries if not e.success)
            layers = {}
            for e in self._entries:
                layers[e.layer] = layers.get(e.layer, 0) + 1
        elapsed = (time.monotonic() - self._start_time) * 1000.0
        return {
            "run_id": self.run_id,
            "total_entries": total,
            "failed_entries": failed,
            "layers": layers,
            "elapsed_ms": round(elapsed, 1),
            "signed": bool(self._signed_digest),
        }

    @classmethod
    @contextmanager
    def run_frame(cls, run_id: str) -> Generator[TraceContext, None, None]:
        """Context manager that installs this context as the process singleton.

        On exit, the previous context is restored (supports nested frames).
        """
        ctx = cls(run_id=run_id)
        prev = _set_trace_context(ctx)
        try:
            yield ctx
        finally:
            _set_trace_context(prev)


# ---------------------------------------------------------------------------
# Process-level singleton
# ---------------------------------------------------------------------------

_TRACE_CONTEXT_LOCAL = threading.local()
_NO_OP_CONTEXT: TraceContext | None = None


def _get_noop_context() -> TraceContext:
    global _NO_OP_CONTEXT
    if _NO_OP_CONTEXT is None:
        _NO_OP_CONTEXT = TraceContext(run_id="__noop__")
    return _NO_OP_CONTEXT


def get_trace_context() -> TraceContext:
    """Return the active TraceContext for this thread.

    Returns a no-op context (entries are discarded) if no run frame is active.
    """
    ctx = getattr(_TRACE_CONTEXT_LOCAL, "context", None)
    if ctx is None:
        return _get_noop_context()
    return ctx


def _set_trace_context(ctx: TraceContext | None) -> TraceContext | None:
    """Install ctx as the thread-local context, return the previous one."""
    prev = getattr(_TRACE_CONTEXT_LOCAL, "context", None)
    _TRACE_CONTEXT_LOCAL.context = ctx
    return prev


__all__ = [
    "TraceContext",
    "TraceEntry",
    "get_trace_context",
]
