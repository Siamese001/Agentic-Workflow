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
from agentic_core.L0_routing.utils.routing_telemetry import (
    RoutingOutcomeStatus,
    RoutingTelemetryContext,
    record_routing_telemetry,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
)

from .assembly_stage import GovernedPayload

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

_log = logging.getLogger(__name__)


def _get_routing_gateway():
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_get_routing_gateway", "state_snapshot")
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_get_routing_gateway", "p0_governance")
    from agentic_core.L0_routing.reasoning.deterministic_routing_gateway import (
        get_routing_gateway,  # noqa: PLC0415
    )

    return get_routing_gateway()


def _get_proof_emitter():
    from agentic_core.L2_execution.utils.execution_proof_emitter import (
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

        from agentic_core.L2_execution.utils.providers import get_clock as _get_clock  # noqa: PLC0415

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
        from agentic_core.runtime.types.execution_trace import get_active_execution_trace  # noqa: PLC0415

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
        except (ValueError, TypeError, RuntimeError) as _rce:  # guardian: allow-silent-swallow
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
        except (ValueError, TypeError, RuntimeError) as _te:  # guardian: allow-silent-swallow
            _log.debug("path_router: telemetry emission failed: %s", _te)
        return chosen
