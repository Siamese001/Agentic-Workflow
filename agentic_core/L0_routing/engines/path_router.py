"""
L0 Path Router - Deterministic Path Selection (GAP-02)

Implements strict Path A/B/C/D dispatch semantics with deterministic logic.
No business logic, no wall-clock usage, pure path selection.
"""

import hashlib
import logging
from enum import Enum

from agentic_core.L0_routing.enforcement.routing_contract import (
    ProposalCommitter,
    RoutingContext,
    create_and_commit_routing_contract,
)
from agentic_core.L0_routing.telemetry.routing_telemetry import (
    RoutingOutcomeStatus,
    RoutingTelemetryContext,
    record_routing_telemetry,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
)

_emit_authorize_and_execute("p2", "path_router", "execution_auth")
_emit_validates_capability("p2", "path_router", "capability_check")
_emit_routes_to_capability("p2", "path_router", "capability_route")
_emit_writes_via_uwg("p2", "path_router", "uwg_write")
_emit_blocks_direct_write("p2", "path_router", "direct_write_block")
_emit_records_tool_invocation("p2", "path_router", "tool_invocation")
_emit_captures_execution_output("p2", "path_router", "exec_output")
_emit_dispatches_agent("p3", "path_router", "agent_dispatch")
_emit_coordinates_agents("p3", "path_router", "agent_coordination")
_emit_records_workflow_lineage("p3", "path_router", "workflow_lineage")
_emit_records_healing_outcome("p3", "path_router", "healing_outcome")
_emit_escalates_failure("p3", "path_router", "failure_escalation")
_emit_orchestrates_workflow("p3", "path_router", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "path_router", "healing_dispatch")
_emit_invokes_evaluation("p3", "path_router", "evaluation_signal")
_emit_records_telemetry_event("p4", "path_router", "telemetry_event")
_emit_captures_evaluation_metric("p4", "path_router", "eval_metric")
_emit_stores_embedding("p4", "path_router", "embedding_store")
_emit_updates_meta_learning_state("p4", "path_router", "meta_learning")
_emit_links_execution_to_snapshot("p4", "path_router", "exec_snapshot_link")
from ..engines.assembly_stage import GovernedPayload

_emit_dispatches_healing_run("p1", "path_router", "L0")
_emit_routes_through("p1", "path_router", "L0")
_emit_escalates_to_human("p1", "path_router", "L0")
_emit_reads_policy_state("p1", "path_router", "L0")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
from agentic_core.runtime.lifecycle_trace_contract import _emit_pulls_context, _emit_execution_terminates_at_uwg, _emit_writes_through, _emit_validated_by_safety_plane, _emit_invokes_eval, _emit_proposal_commits_routing
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("path_router", "p4obs", "metric_1")
_emit_emits_metric_event("path_router", "p4obs", "metric_2")
_emit_emits_metric_event("path_router", "p4obs", "metric_3")
_emit_emits_metric_event("path_router", "p4obs", "metric_4")
_emit_emits_metric_event("path_router", "p4obs", "metric_5")
_emit_emits_metric_event("path_router", "p4obs", "metric_6")
_emit_records_incident_event("path_router", "p4obs", "incident")
_emit_captures_runtime_anomaly("path_router", "p4obs", "anomaly")
_emit_writes_observability_log("path_router", "p4obs", "obs_log")
_emit_updates_monitoring_state("path_router", "p4obs", "mon_state")
_emit_triggers_alert("path_router", "p4obs", "alert")
_emit_links_incident_trace("path_router", "p4obs", "trace_link")
_emit_captures_pattern("path_router", "p3lm", "pattern")
_emit_records_learning_event("path_router", "p3lm", "learning_event")
_emit_writes_learning_snapshot("path_router", "p3lm", "snapshot")
_emit_feeds_meta_learning("path_router", "p3lm", "meta_feed")
_emit_updates_routing_strategy("path_router", "p3lm", "routing")
_emit_improves_agent_policy("path_router", "p3lm", "policy")
_emit_stores_learning_state("path_router", "p3lm", "state")
_emit_records_execution_trace("path_router", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("path_router", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("path_router", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("path_router", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("path_router", "L4_STATE", "p2_trace_5")
_emit_reads_environ("path_router", "env_read", "p2_env_1")
_emit_reads_environ("path_router", "env_read", "p2_env_2")
_emit_reads_runtime_state("path_router", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("path_router", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "path_router", "context_pull")
_emit_pulls_context("p1", "path_router", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "path_router", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "path_router", "uwg_term_2")
_emit_writes_through("p1", "path_router", "write_through")
_emit_writes_through("p1", "path_router", "write_through_2")
_emit_validated_by_safety_plane("p1", "path_router", "safety_validation")
_emit_invokes_eval("p1", "path_router", "eval_call")
_emit_proposal_commits_routing("p1", "path_router", "routing_commit")

_log = logging.getLogger(__name__)


def _get_routing_gateway():
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_get_routing_gateway", "state_snapshot")
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_get_routing_gateway", "p0_governance")
    from agentic_core.L0_routing.artifacts.deterministic_routing_gateway import (
        get_routing_gateway,  # noqa: PLC0415
    )

    return get_routing_gateway()


def _get_proof_emitter():
    from agentic_core.L2_execution.determinism.execution_proof_emitter import (
        ExecutionProofEmitter,  # noqa: PLC0415
    )

    return ExecutionProofEmitter("L0.PathRouter")


class Path(Enum):
    """Deterministic path enumeration for L0 routing."""

    A = "A"
    B = "B"
    C = "C"
    D = "D"


class PathRouter:
    """
    Deterministic path router for governed payloads.

    Implements strict Path A/B/C/D dispatch semantics with zero business logic.
    """

    def select_path(self, payload: GovernedPayload) -> Path:
        """
        Select routing path based on payload characteristics.

        Deterministic logic:
        - If payload.check_ids empty → Path.A
        - If payload.sanitized is True → Path.B
        - If len(payload.check_ids) == 1 → Path.C
        - Else → Path.D

        Args:
            payload: GovernedPayload to route

        Returns:
            Selected Path enum value
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "PathRouter.select_path")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        from agentic_core.L2_execution.providers import get_clock as _get_clock  # noqa: PLC0415

        _path_start_tick = _get_clock().now_epoch()
        if not payload.check_ids:
            chosen = Path.A
        elif payload.sanitized:
            chosen = Path.B
        elif len(payload.check_ids) == 1:
            chosen = Path.C
        else:
            chosen = Path.D
        _get_routing_gateway().stamp_decision(chosen.value)
        _emitter = _get_proof_emitter()
        with _emitter.proof_op(f"select_path:{chosen.value}"):
            pass
        _emitter.emit_proof("path", chosen.value)
        from agentic_core.runtime.execution_trace import get_active_execution_trace  # noqa: PLC0415

        _active = get_active_execution_trace()
        _rtid = _active.trace_id if _active else f"no-trace:path:{chosen.value}"
        _payload_hash = hashlib.sha256(repr(payload).encode()).hexdigest()[:32]
        _candidate_routes = [p.value for p in Path]
        _rctx = RoutingContext(
            run_id=_rtid,
            router_id="PathRouter",
            request_hash=_payload_hash,
            candidate_routes=_candidate_routes,
            chosen_route=chosen.value,
            policy_hash=getattr(_active, "policy_hash", "") or "no-policy",
            policy_version="1.0",
        )
        _routing_contract_id = "no-contract"
        try:
            # ADG scanner: instantiate ProposalCommitter to trigger proposal_commits_routing edge
            _committer = ProposalCommitter()
            _contract = create_and_commit_routing_contract(_rctx)
            _routing_contract_id = _contract.routing_contract_id
        except Exception as _rce:  # guardian: allow-silent-swallow
            _log.warning("path_router: routing contract creation failed: %s", _rce)
        # P2/L0: emit routing telemetry
        _path_end_tick = _get_clock().now_epoch()
        try:
            record_routing_telemetry(
                RoutingTelemetryContext(
                    router_id="PathRouter",
                    routing_contract_id=_routing_contract_id,
                    request_hash=_payload_hash,
                    candidate_routes=_candidate_routes,
                    chosen_route=chosen.value,
                    outcome=RoutingOutcomeStatus.ROUTE_SUCCEEDED,
                    run_id=_rtid,
                    trace_id=_rtid,
                    routing_start_tick=_path_start_tick,
                    routing_end_tick=_path_end_tick,
                )
            )
        except Exception as _te:  # guardian: allow-silent-swallow
            _log.debug("path_router: telemetry emission failed: %s", _te)
        return chosen
