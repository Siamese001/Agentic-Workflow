from __future__ import annotations

import logging
import sys
import threading
from dataclasses import dataclass, field
from typing import Callable


logger = logging.getLogger(__name__)

try:
    from agentic_core.runtime.contracts.lifecycle_trace_contract import (
        _emit_applies_guardrail,
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
        _emit_reads_policy_state,
        _emit_records_healing_outcome,
        _emit_records_telemetry_event,
        _emit_records_tool_invocation,
        _emit_records_workflow_lineage,
        _emit_routes_to_capability,
        _emit_snapshots_state,
        _emit_stores_embedding,
        _emit_updates_meta_learning_state,
        _emit_validates_capability,
        _emit_writes_via_uwg,
        emit_determinism_digest,
        record_execution_trace,
    )

    _LIFECYCLE_AVAILABLE = True
except ImportError as exc:
    print(f"[otel_mcp] WARNING: lifecycle_trace_contract unavailable - {exc}", file=sys.stderr)
    _LIFECYCLE_AVAILABLE = False


LifecycleAction = Callable[[], None]


def _emit_all_lifecycle_edges() -> None:
    emit_determinism_digest("otel_mcp_server", "otel_mcp_server_digest")
    record_execution_trace("otel_mcp_server", "otel_mcp_server_trace")
    _emit_applies_guardrail("p0", "otel_mcp_server", "p0_governance")
    _emit_reads_policy_state("p0", "otel_mcp_server", "policy_binding")
    _emit_snapshots_state("p0", "otel_mcp_server", "state_snapshot")
    _emit_authorize_and_execute("p2", "otel_mcp_server", "execution_auth")
    _emit_validates_capability("p2", "otel_mcp_server", "capability_check")
    _emit_routes_to_capability("p2", "otel_mcp_server", "capability_route")
    _emit_writes_via_uwg("p2", "otel_mcp_server", "uwg_write")
    _emit_blocks_direct_write("p2", "otel_mcp_server", "direct_write_block")
    _emit_records_tool_invocation("p2", "otel_mcp_server", "tool_invocation")
    _emit_captures_execution_output("p2", "otel_mcp_server", "exec_output")
    _emit_dispatches_agent("p3", "otel_mcp_server", "agent_dispatch")
    _emit_coordinates_agents("p3", "otel_mcp_server", "agent_coordination")
    _emit_records_workflow_lineage("p3", "otel_mcp_server", "workflow_lineage")
    _emit_records_healing_outcome("p3", "otel_mcp_server", "healing_outcome")
    _emit_escalates_failure("p3", "otel_mcp_server", "failure_escalation")
    _emit_orchestrates_workflow("p3", "otel_mcp_server", "workflow_orchestration")
    _emit_dispatches_healing_run("p3", "otel_mcp_server", "healing_dispatch")
    _emit_invokes_evaluation("p3", "otel_mcp_server", "evaluation_signal")
    _emit_records_telemetry_event("p4", "otel_mcp_server", "telemetry_event")
    _emit_captures_evaluation_metric("p4", "otel_mcp_server", "eval_metric")
    _emit_stores_embedding("p4", "otel_mcp_server", "embedding_store")
    _emit_updates_meta_learning_state("p4", "otel_mcp_server", "meta_learning")
    _emit_links_execution_to_snapshot("p4", "otel_mcp_server", "exec_snapshot_link")


@dataclass
class LifecycleRegistrar:
    """Idempotent lifecycle registration that never blocks health tools.

    Health and process-identity surfaces must remain side-effect free and
    return current state only. Lifecycle registration therefore happens in a
    background daemon thread and can be observed via `status()`.
    """

    registered: bool = False
    started: bool = False
    last_error: str | None = None
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False, repr=False)
    _thread: threading.Thread | None = field(default=None, init=False, repr=False)
    _registration_action: LifecycleAction = field(default=_emit_all_lifecycle_edges, repr=False)

    @property
    def available(self) -> bool:
        return _LIFECYCLE_AVAILABLE

    @property
    def loading(self) -> bool:
        return self.started and not self.registered and self.last_error is None

    def start_background(self) -> None:
        if not self.available or self.registered or self.started:
            return
        with self._lock:
            if not self.available or self.registered or self.started:
                return
            self.started = True
            self._thread = threading.Thread(
                target=self._run_registration, name="otel-lifecycle-register", daemon=True
            )
            self._thread.start()
            logger.info("Lifecycle background registration started")

    def ensure_started(self) -> None:
        self.start_background()

    def register_once(self) -> None:
        """Compatibility alias for older callers.

        This method is intentionally non-blocking now.
        """
        self.start_background()

    def _run_registration(self) -> None:
        try:
            self._registration_action()
            self.registered = True
            logger.info("Lifecycle background registration completed")
        except Exception as exc:  # guardian: allow-broad-exception
            self.last_error = str(exc)
            logger.warning("Lifecycle background registration failed: %s", exc)

    def status(self) -> dict[str, bool | str | None]:
        return {
            "available": self.available,
            "started": self.started,
            "registered": self.registered,
            "loading": self.loading,
            "last_error": self.last_error,
        }
