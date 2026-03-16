"""
agentic_core/runtime/types/sovereign_events_types.py - Sovereign Event Schema

Zero-Ambiguity Standard: Renamed from SovereignEvent.py to sovereign_event_types.py
Category: TYPES (Event schema definition)
"""

import asyncio
import inspect
import json
import logging
import time
import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from agentic_core.mixins.context_propagation_mixin import span_id_var, trace_id_var
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "sovereign_events_types", "p0_governance")
_emit_reads_policy_state("p0", "sovereign_events_types", "policy_binding")
_emit_snapshots_state("p0", "sovereign_events_types", "state_snapshot")
emit_replay_key("p0", "sovereign_events_types")
emit_determinism_digest("p0", "sovereign_events_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "sovereign_events_types", "execution_auth")
_emit_validates_capability("p2", "sovereign_events_types", "capability_check")
_emit_routes_to_capability("p2", "sovereign_events_types", "capability_route")
_emit_writes_via_uwg("p2", "sovereign_events_types", "uwg_write")
_emit_blocks_direct_write("p2", "sovereign_events_types", "direct_write_block")
_emit_records_tool_invocation("p2", "sovereign_events_types", "tool_invocation")
_emit_captures_execution_output("p2", "sovereign_events_types", "exec_output")
_emit_dispatches_agent("p3", "sovereign_events_types", "agent_dispatch")
_emit_coordinates_agents("p3", "sovereign_events_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "sovereign_events_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "sovereign_events_types", "healing_outcome")
_emit_escalates_failure("p3", "sovereign_events_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "sovereign_events_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "sovereign_events_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "sovereign_events_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "sovereign_events_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "sovereign_events_types", "eval_metric")
_emit_stores_embedding("p4", "sovereign_events_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "sovereign_events_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "sovereign_events_types", "exec_snapshot_link")


class SovereignEvent(BaseModel):
    """Standardized schema for all agentic events (Report 4.3)."""

    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    event_type: str
    source_agent: str
    severity: str = "INFO"
    payload: dict[str, Any] = {}
    trace_id: str | None = None


class event_emission_mixin:
    """
    Phase 2 observability Infrastructure: Event Emission (Report 4.3).

    Standardizes how agents broadcast internal state changes to L6.
    Features:
    - Structured Event schema (Pydantic)
    - Automatic Source Attribution
    - Severity-based Filtering
    - Trace ID correlation support
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._ee_logger = logging.getLogger(self.__class__.__name__)
        self._event_buffer = []

    def emit_event(
        self,
        event_type: str,
        payload: dict[str, Any] | None = None,
        severity: str = "INFO",
        trace_id: str | None = None,
    ) -> SovereignEvent:
        """
        Broadmosts a structured event for L6 monitoring.

        Args:
            event_type: Category of the event (e.g., 'healing.success')
            payload: Data associated with the event
            severity: Impact level (INFO to CRITICAL)
            trace_id: ID for cross-agent request correlation

        Returns:
            SovereignEvent: The emitted event object
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "event_emission_mixin.emit_event")

        active_trace = trace_id or trace_id_var.get()
        active_span = span_id_var.get()
        event_payload = payload or {}
        if active_trace and "trace_id" not in event_payload:
            event_payload["trace_id"] = active_trace
        if active_span and "span_id" not in event_payload:
            event_payload["span_id"] = active_span
        event = SovereignEvent(
            event_type=event_type,
            source_agent=self.__class__.__name__,
            severity=severity.upper(),
            payload=event_payload,
            trace_id=active_trace,
        )
        log_level = getattr(logging, event.severity, logging.INFO)
        self._ee_logger.log(log_level, f"EVENT [{event.event_type}]: {event.payload}")
        self._dispatch_to_observability(event)
        return event

    def _dispatch_to_observability(self, event: SovereignEvent):
        """Internal: Routes the event to the L6 monitoring layer."""
        if not hasattr(self, "redis_client") or not self.redis_client:
            return

        async def _dispatch_async() -> None:
            """Hardened: 3 retries + 5s timeout per attempt."""
            MAX_RETRIES = 3
            TIMEOUT_SEC = 5.0
            # guardian: allow-magic-config
            base_delay = 0.8
            event_data = event.model_dump()
            stream_payload = {"event": json.dumps(event_data)}
            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    result = self.redis_client.xadd("sovereign_event_stream", stream_payload, maxlen=10000)
                    if inspect.isawaitable(result):
                        await asyncio.wait_for(result, timeout=TIMEOUT_SEC)
                    else:
                        await asyncio.wait_for(asyncio.to_thread(lambda: result), timeout=TIMEOUT_SEC)
                    self._ee_logger.debug(f"Event dispatched (attempt {attempt}): {event.event_id}")
                    return
                except asyncio.TimeoutError:
                    self._ee_logger.warning(f"Redis dispatch timeout (attempt {attempt}/{MAX_RETRIES})")
                except Exception as e:
                    raise
                    self._ee_logger.warning(f"Redis dispatch failed (attempt {attempt}/{MAX_RETRIES}): {e}")
                if attempt < MAX_RETRIES:
                    await asyncio.sleep(base_delay * 2 ** (attempt - 1))
            self._ee_logger.error(f"Failed to dispatch event {event.event_id} after {MAX_RETRIES} attempts")

        try:
            loop = asyncio.get_running_loop()
            loop.create_task(_dispatch_async())
        except RuntimeError:
            try:
                self.redis_client.xadd(
                    "sovereign_event_stream", {"event": json.dumps(event.model_dump())}, maxlen=10000
                )
            except Exception as e:
                raise
                self._ee_logger.error(f"Redis Dispatch Failed: {e}")

    @staticmethod
    def observe_execution(event_prefix: str):
        """Decorator to automatically emit start/end events for a method."""

        def decorator(func):
            from functools import wraps

            @wraps(func)
            async def wrapper(self, *args, **kwargs):
                if not isinstance(self, event_emission_mixin):
                    return await func(self, *args, **kwargs)
                self.emit_event(f"{event_prefix}.started", {"args": str(args)})
                start_time = time.time()
                try:
                    result = await func(self, *args, **kwargs)
                    duration = time.time() - start_time
                    self.emit_event(
                        f"{event_prefix}.completed", {"duration": round(duration, 4), "success": True}
                    )
                    return result
                except Exception as e:
                    raise
                    self.emit_event(
                        f"{event_prefix}.failed", {"error": str(e), "success": False}, severity="ERROR"
                    )
                    raise e

            return wrapper

        return decorator
