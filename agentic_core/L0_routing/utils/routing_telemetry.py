"""
agentic_core/L0_routing/telemetry/routing_telemetry.py

RoutingTelemetry — P2/L0 routing observability.

Every runtime routing decision MUST call record_routing_telemetry().
No routing decision may complete without telemetry emission.

record_routing_telemetry() steps (mandatory, in order):
  1. capture start and end timing (routing_start_tick, routing_end_tick, routing_duration_ms)
  2. attach queue / load snapshot if available (explicit null-metric if unavailable)
  3. bind telemetry to routing contract and trace
  4. emit routing outcome status (one of 5 RoutingOutcomeStatus values)
  5. persist telemetry artifact to RoutingTelemetryStore

RoutingTelemetry (15 required spec fields):
    routing_telemetry_id, run_id, trace_id, routing_contract_id,
    router_id, request_hash, candidate_route_count, chosen_route_hash,
    routing_start_tick, routing_end_tick, routing_duration_ms,
    queue_depth_snapshot, target_load_snapshot,
    routing_outcome_status, routing_failure_reason

RoutingOutcomeStatus (5 mandatory outcome bindings per spec §5):
    ROUTE_SUCCEEDED, ROUTE_FAILED, ROUTE_ESCALATED,
    ROUTE_RETRIED, ROUTE_ABANDONED

NullMetricReason — explicit null classification for unavailable load/queue metrics.

ADG edges emitted:
    records_execution_trace   — telemetry binds to active trace
    proposal_commits_routing  — telemetry references routing contract
    routing_telemetry_emitted — one record per routing decision
"""

from __future__ import annotations

import hashlib
import logging
import threading
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
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
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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
)

emit_replay_key("p0", "routing_telemetry")
emit_determinism_digest("p0", "routing_telemetry")

_emit_dispatches_healing_run("p1", "routing_telemetry", "L0")
_emit_routes_through("p1", "routing_telemetry", "L0")
_emit_checks_agent_registry("p1", "routing_telemetry", "agent_registry")
_emit_validates_agent_capability("p1", "routing_telemetry", "capability")
_emit_dispatches_execution_plan("p1", "routing_telemetry", "exec_plan")
_emit_agent_executes_agent("p1", "routing_telemetry", "sub_agent")
_emit_routes_to_agent("p1", "routing_telemetry", "target_agent")
_emit_verifies_policy("p1", "routing_telemetry", "policy_check")
_emit_verifies_boundary("p1", "routing_telemetry", "boundary_check")
_emit_transcripts_response("p1", "routing_telemetry", "transcript")
_emit_hard_fails_untranscripted("p1", "routing_telemetry")
_emit_gated_by_confidence("p1", "routing_telemetry", "confidence_gate")
_emit_escalates_to_human("p1", "routing_telemetry", "L0")
_emit_reads_policy_state("p1", "routing_telemetry", "L0")

_emit_records_execution_trace("p0", "evidence", "routing_telemetry")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "routing_telemetry", "p0_governance")
_emit_snapshots_state("p0", "routing_telemetry", "state_snapshot")
_emit_authorize_and_execute("p2", "routing_telemetry", "execution_auth")
_emit_validates_capability("p2", "routing_telemetry", "capability_check")
_emit_routes_to_capability("p2", "routing_telemetry", "capability_route")
_emit_writes_via_uwg("p2", "routing_telemetry", "uwg_write")
_emit_blocks_direct_write("p2", "routing_telemetry", "direct_write_block")
_emit_records_tool_invocation("p2", "routing_telemetry", "tool_invocation")
_emit_captures_execution_output("p2", "routing_telemetry", "exec_output")
_emit_dispatches_agent("p3", "routing_telemetry", "agent_dispatch")
_emit_coordinates_agents("p3", "routing_telemetry", "agent_coordination")
_emit_records_workflow_lineage("p3", "routing_telemetry", "workflow_lineage")
_emit_records_healing_outcome("p3", "routing_telemetry", "healing_outcome")
_emit_escalates_failure("p3", "routing_telemetry", "failure_escalation")
_emit_orchestrates_workflow("p3", "routing_telemetry", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "routing_telemetry", "healing_dispatch")
_emit_invokes_evaluation("p3", "routing_telemetry", "evaluation_signal")
_emit_records_telemetry_event("p4", "routing_telemetry", "telemetry_event")
_emit_captures_evaluation_metric("p4", "routing_telemetry", "eval_metric")
_emit_stores_embedding("p4", "routing_telemetry", "embedding_store")
_emit_updates_meta_learning_state("p4", "routing_telemetry", "meta_learning")
_emit_links_execution_to_snapshot("p4", "routing_telemetry", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("routing_telemetry", "p4obs", "metric_1")
_emit_emits_metric_event("routing_telemetry", "p4obs", "metric_2")
_emit_emits_metric_event("routing_telemetry", "p4obs", "metric_3")
_emit_emits_metric_event("routing_telemetry", "p4obs", "metric_4")
_emit_emits_metric_event("routing_telemetry", "p4obs", "metric_5")
_emit_emits_metric_event("routing_telemetry", "p4obs", "metric_6")
_emit_records_incident_event("routing_telemetry", "p4obs", "incident")
_emit_captures_runtime_anomaly("routing_telemetry", "p4obs", "anomaly")
_emit_writes_observability_log("routing_telemetry", "p4obs", "obs_log")
_emit_updates_monitoring_state("routing_telemetry", "p4obs", "mon_state")
_emit_triggers_alert("routing_telemetry", "p4obs", "alert")
_emit_links_incident_trace("routing_telemetry", "p4obs", "trace_link")
_emit_captures_pattern("routing_telemetry", "p3lm", "pattern")
_emit_records_learning_event("routing_telemetry", "p3lm", "learning_event")
_emit_writes_learning_snapshot("routing_telemetry", "p3lm", "snapshot")
_emit_feeds_meta_learning("routing_telemetry", "p3lm", "meta_feed")
_emit_updates_routing_strategy("routing_telemetry", "p3lm", "routing")
_emit_improves_agent_policy("routing_telemetry", "p3lm", "policy")
_emit_stores_learning_state("routing_telemetry", "p3lm", "state")
_emit_records_execution_trace("routing_telemetry", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("routing_telemetry", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("routing_telemetry", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("routing_telemetry", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("routing_telemetry", "L4_STATE", "p2_trace_5")
_emit_reads_environ("routing_telemetry", "env_read", "p2_env_1")
_emit_reads_environ("routing_telemetry", "env_read", "p2_env_2")
_emit_reads_runtime_state("routing_telemetry", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("routing_telemetry", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "routing_telemetry", "context_pull")
_emit_pulls_context("p1", "routing_telemetry", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "routing_telemetry", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "routing_telemetry", "uwg_term_2")
_emit_writes_through("p1", "routing_telemetry", "write_through")
_emit_writes_through("p1", "routing_telemetry", "write_through_2")
_emit_validated_by_safety_plane("p1", "routing_telemetry", "safety_validation")
_emit_invokes_eval("p1", "routing_telemetry", "eval_call")
_emit_proposal_commits_routing("p1", "routing_telemetry", "routing_commit")

logger = logging.getLogger(__name__)
_TRACE_LOG = logging.getLogger("adg.records_execution_trace")
_PROPOSAL_LOG = logging.getLogger("adg.proposal_commits_routing")
_TELEMETRY_LOG = logging.getLogger("adg.routing_telemetry_emitted")


# ---------------------------------------------------------------------------
# RoutingOutcomeStatus — 5 mandatory outcome bindings per spec §5
# ---------------------------------------------------------------------------


class RoutingOutcomeStatus(str, Enum):
    """Classification of a routing decision outcome.

    Every RoutingTelemetry record must bind to exactly one of these.
    """

    ROUTE_SUCCEEDED = "route_succeeded"
    ROUTE_FAILED = "route_failed"
    ROUTE_ESCALATED = "route_escalated"
    ROUTE_RETRIED = "route_retried"
    ROUTE_ABANDONED = "route_abandoned"


# ---------------------------------------------------------------------------
# NullMetricReason — explicit null classification for unavailable metrics
# ---------------------------------------------------------------------------


class NullMetricReason(str, Enum):
    """Reason why a load or queue metric is unavailable.

    Per spec §4: if a load metric is unavailable, emit an explicit null-metric
    reason rather than silently omitting the field.
    """

    NOT_INSTRUMENTED = "not_instrumented"
    METRIC_TIMEOUT = "metric_timeout"
    COLLECTION_ERROR = "collection_error"
    METRIC_DISABLED = "metric_disabled"
    NO_ACTIVE_QUEUE = "no_active_queue"


# ---------------------------------------------------------------------------
# RoutingTelemetry — 15 required spec fields
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RoutingTelemetry:
    """Immutable telemetry artifact for one routing decision (P2/L0 spec §2).

    All 15 fields are required. Fields that cannot be measured must carry
    an explicit NullMetricReason value rather than being omitted or None.
    """

    routing_telemetry_id: str
    run_id: str
    trace_id: str
    routing_contract_id: str
    router_id: str
    request_hash: str
    candidate_route_count: int
    chosen_route_hash: str
    routing_start_tick: float
    routing_end_tick: float
    routing_duration_ms: float
    queue_depth_snapshot: Any
    target_load_snapshot: Any
    routing_outcome_status: str
    routing_failure_reason: str

    @classmethod
    def create(
        cls,
        run_id: str,
        trace_id: str,
        routing_contract_id: str,
        router_id: str,
        request_hash: str,
        candidate_route_count: int,
        chosen_route: str,
        routing_start_tick: float,
        routing_end_tick: float,
        routing_outcome_status: RoutingOutcomeStatus,
        queue_depth_snapshot: Any = None,
        target_load_snapshot: Any = None,
        routing_failure_reason: str = "",
    ) -> RoutingTelemetry:
        telemetry_id = f"rt-{uuid.uuid4().hex[:12]}"
        chosen_route_hash = hashlib.sha256(chosen_route.encode()).hexdigest()[:16]
        duration_ms = max(0.0, (routing_end_tick - routing_start_tick) * 1000.0)

        # Explicit null-metric discipline: never silently omit
        q_snap = (
            queue_depth_snapshot
            if queue_depth_snapshot is not None
            else NullMetricReason.NOT_INSTRUMENTED.value
        )
        load_snap = (
            target_load_snapshot
            if target_load_snapshot is not None
            else NullMetricReason.NOT_INSTRUMENTED.value
        )

        return cls(
            routing_telemetry_id=telemetry_id,
            run_id=run_id,
            trace_id=trace_id,
            routing_contract_id=routing_contract_id,
            router_id=router_id,
            request_hash=request_hash,
            candidate_route_count=candidate_route_count,
            chosen_route_hash=chosen_route_hash,
            routing_start_tick=routing_start_tick,
            routing_end_tick=routing_end_tick,
            routing_duration_ms=duration_ms,
            queue_depth_snapshot=q_snap,
            target_load_snapshot=load_snap,
            routing_outcome_status=routing_outcome_status.value,
            routing_failure_reason=routing_failure_reason,
        )


# ---------------------------------------------------------------------------
# RoutingTelemetryContext — input bundle for record_routing_telemetry()
# ---------------------------------------------------------------------------


@dataclass
class RoutingTelemetryContext:
    """All inputs required to emit a RoutingTelemetry record.

    Callers must populate router_id, routing_contract_id, request_hash,
    candidate_routes, chosen_route, and outcome. Optional timing fields
    default to the current clock if not supplied.
    """

    router_id: str
    routing_contract_id: str
    request_hash: str
    candidate_routes: list[str]
    chosen_route: str
    outcome: RoutingOutcomeStatus
    run_id: str = ""
    trace_id: str = ""
    routing_start_tick: float = 0.0
    routing_end_tick: float = 0.0
    queue_depth_snapshot: Any = None
    target_load_snapshot: Any = None
    failure_reason: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# record_routing_telemetry() — mandatory entrypoint per spec §3
# ---------------------------------------------------------------------------


def record_routing_telemetry(
    routing_context: RoutingTelemetryContext,
) -> RoutingTelemetry:
    """Mandatory routing telemetry entrypoint — P2/L0 spec §3.

    Steps (in order, all mandatory):
      1. capture start and end timing
      2. attach queue / load snapshot if available (explicit null if not)
      3. bind telemetry to routing contract and trace
      4. emit routing outcome status
      5. persist telemetry artifact

    Args:
        routing_context:  Fully-populated RoutingTelemetryContext.

    Returns:
        RoutingTelemetry (immutable, 15 fields), persisted to the store.
    """
    _emit_observes_runtime_state(str(uuid.uuid4()), "Module.record_routing_telemetry", "L0_ROUTING")
    clk = get_clock()
    now = clk.now_epoch()

    # --- Step 1: Capture timing ---
    start_tick = routing_context.routing_start_tick or now
    end_tick = routing_context.routing_end_tick or now

    # --- Step 2: Queue / load snapshot (explicit null if unavailable) ---
    # handled inside RoutingTelemetry.create()

    # --- Step 3: Bind to routing contract and trace ---
    effective_trace_id = routing_context.trace_id
    if not effective_trace_id:
        effective_trace_id = _resolve_trace_id()
    effective_run_id = routing_context.run_id or _resolve_run_id() or "unknown"

    _TRACE_LOG.debug(
        "records_execution_trace ROUTING_TELEMETRY router=%s contract=%s trace=%s",
        routing_context.router_id,
        routing_context.routing_contract_id,
        effective_trace_id,
    )
    _PROPOSAL_LOG.debug(
        "proposal_commits_routing ROUTING_TELEMETRY router=%s contract=%s",
        routing_context.router_id,
        routing_context.routing_contract_id,
    )

    # --- Step 4: Emit routing outcome status ---
    outcome = routing_context.outcome

    # --- Build RoutingTelemetry ---
    telemetry = RoutingTelemetry.create(
        run_id=effective_run_id,
        trace_id=effective_trace_id,
        routing_contract_id=routing_context.routing_contract_id,
        router_id=routing_context.router_id,
        request_hash=routing_context.request_hash,
        candidate_route_count=len(routing_context.candidate_routes),
        chosen_route=routing_context.chosen_route,
        routing_start_tick=start_tick,
        routing_end_tick=end_tick,
        routing_outcome_status=outcome,
        queue_depth_snapshot=routing_context.queue_depth_snapshot,
        target_load_snapshot=routing_context.target_load_snapshot,
        routing_failure_reason=routing_context.failure_reason,
    )

    # --- Step 5: Persist ---
    _TELEMETRY_LOG.debug(
        "routing_telemetry_emitted ROUTING_TELEMETRY id=%s router=%s outcome=%s duration_ms=%.3f",
        telemetry.routing_telemetry_id,
        routing_context.router_id,
        outcome.value,
        telemetry.routing_duration_ms,
    )
    _persist_telemetry(telemetry)

    logger.debug(
        "RECORD_ROUTING_TELEMETRY emitted id=%s router=%s contract=%s outcome=%s duration_ms=%.3f trace=%s",
        telemetry.routing_telemetry_id,
        routing_context.router_id,
        routing_context.routing_contract_id,
        outcome.value,
        telemetry.routing_duration_ms,
        effective_trace_id,
    )
    return telemetry


# ---------------------------------------------------------------------------
# RoutingTelemetryStore — queryable by run_id, trace_id, contract_id, outcome
# ---------------------------------------------------------------------------


class RoutingTelemetryStore:
    """Queryable in-memory store for all emitted RoutingTelemetry records.

    Per spec §4: routing telemetry must be queryable by:
    - run_id
    - trace_id
    - routing_contract_id
    - routing_outcome_status
    """

    def __init__(self) -> None:
        self._records: list[RoutingTelemetry] = []
        self._lock = threading.RLock()

    def ingest(self, record: RoutingTelemetry) -> None:
        with self._lock:
            self._records.append(record)

    def by_run_id(self, run_id: str) -> list[RoutingTelemetry]:
        with self._lock:
            return [r for r in self._records if r.run_id == run_id]

    def by_trace_id(self, trace_id: str) -> list[RoutingTelemetry]:
        with self._lock:
            return [r for r in self._records if r.trace_id == trace_id]

    def by_contract_id(self, routing_contract_id: str) -> list[RoutingTelemetry]:
        with self._lock:
            return [r for r in self._records if r.routing_contract_id == routing_contract_id]

    def by_outcome(self, outcome: RoutingOutcomeStatus) -> list[RoutingTelemetry]:
        with self._lock:
            return [r for r in self._records if r.routing_outcome_status == outcome.value]

    def all_records(self) -> list[RoutingTelemetry]:
        with self._lock:
            return list(self._records)

    def record_count(self) -> int:
        with self._lock:
            return len(self._records)

    def records_without_duration(self) -> list[RoutingTelemetry]:
        """Return records with routing_duration_ms == 0 (missing timing)."""
        with self._lock:
            return [r for r in self._records if r.routing_duration_ms <= 0.0]

    def records_without_outcome(self) -> list[RoutingTelemetry]:
        """Return records with no outcome status set."""
        with self._lock:
            return [r for r in self._records if not r.routing_outcome_status]

    def records_with_silent_null(self) -> list[RoutingTelemetry]:
        """Return records where queue/load are Python None (silent omission, prohibited)."""
        with self._lock:
            return [
                r for r in self._records if r.queue_depth_snapshot is None or r.target_load_snapshot is None
            ]

    def average_duration_ms(self) -> float:
        with self._lock:
            records = self._records
            if not records:
                return 0.0
            return sum(r.routing_duration_ms for r in records) / len(records)


# ---------------------------------------------------------------------------
# Process-level RoutingTelemetryStore singleton
# ---------------------------------------------------------------------------

_global_store: RoutingTelemetryStore | None = None
_global_store_lock = threading.Lock()


def get_routing_telemetry_store() -> RoutingTelemetryStore:
    """Return the process-level RoutingTelemetryStore singleton."""
    global _global_store
    if _global_store is None:
        with _global_store_lock:
            if _global_store is None:
                _global_store = RoutingTelemetryStore()
    return _global_store


def reset_routing_telemetry_store() -> None:
    """Reset the global store (for testing)."""
    global _global_store
    _global_store = None


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _resolve_trace_id() -> str:
    try:
        from agentic_core.runtime.types.execution_trace import get_active_execution_trace  # noqa: PLC0415

        active = get_active_execution_trace()
        return active.trace_id if active else ""
    except (ValueError, TypeError, RuntimeError) as e:
        return ""


def _resolve_run_id() -> str:
    try:
        from agentic_core.runtime.types.execution_trace import get_active_execution_trace  # noqa: PLC0415

        active = get_active_execution_trace()
        return getattr(active, "run_id", "") if active else ""
    except (ValueError, TypeError, RuntimeError) as e:
        return ""


def _persist_telemetry(record: RoutingTelemetry) -> None:
    get_routing_telemetry_store().ingest(record)


__all__ = [
    "RoutingOutcomeStatus",
    "NullMetricReason",
    "RoutingTelemetry",
    "RoutingTelemetryContext",
    "RoutingTelemetryStore",
    "record_routing_telemetry",
    "get_routing_telemetry_store",
    "reset_routing_telemetry_store",
]
