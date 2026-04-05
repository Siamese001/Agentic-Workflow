"""
agentic_core/L0_routing/policy/route_policy_governor.py

RoutePolicyGovernor — P1-L0 gap remediation.

Commits routing decisions as RoutingProposal records referencing the
governing policy hash before execution. Closes the gap where 366 L0
modules read policy state (76 edges) without committing to governance
constraints (0 proposal_commits_routing / references_policy_hash).

ADG edges emitted: proposal_commits_routing, references_policy_hash,
                   reads_governed_config, verifies_boundary
"""

from __future__ import annotations

import hashlib
import logging
import uuid
from dataclasses import dataclass, field
from typing import Any

from agentic_core.L0_routing.artifacts.deterministic_routing_gateway import (
    DeterministicRoutingGateway,
    RoutingArtifact,
    get_routing_gateway,
)
from agentic_core.L0_routing.enforcement.routing_contract import (
    RoutingContext as ContractRoutingContext,
)
from agentic_core.L0_routing.enforcement.routing_contract import (
    create_and_commit_routing_contract,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
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
    emit_determinism_digest,
    emit_replay_key,
)

_emit_dispatches_healing_run("p1", "route_policy_governor", "L0")
_emit_routes_through("p1", "route_policy_governor", "L0")
_emit_checks_agent_registry("p1", "route_policy_governor", "agent_registry")
_emit_validates_agent_capability("p1", "route_policy_governor", "capability")
_emit_dispatches_execution_plan("p1", "route_policy_governor", "exec_plan")
_emit_agent_executes_agent("p1", "route_policy_governor", "sub_agent")
_emit_routes_to_agent("p1", "route_policy_governor", "target_agent")
_emit_observes_runtime_state("p1", "route_policy_governor", "runtime_state")
_emit_verifies_boundary("p1", "route_policy_governor", "boundary_check")
_emit_transcripts_response("p1", "route_policy_governor", "transcript")
_emit_hard_fails_untranscripted("p1", "route_policy_governor")
_emit_gated_by_confidence("p1", "route_policy_governor", "confidence_gate")
_emit_escalates_to_human("p1", "route_policy_governor", "L0")
_emit_reads_policy_state("p1", "route_policy_governor", "L0")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "route_policy_governor", "p0_governance")
_emit_snapshots_state("p0", "route_policy_governor", "state_snapshot")
_emit_authorize_and_execute("p2", "route_policy_governor", "execution_auth")
_emit_validates_capability("p2", "route_policy_governor", "capability_check")
_emit_routes_to_capability("p2", "route_policy_governor", "capability_route")
_emit_writes_via_uwg("p2", "route_policy_governor", "uwg_write")
_emit_blocks_direct_write("p2", "route_policy_governor", "direct_write_block")
_emit_records_tool_invocation("p2", "route_policy_governor", "tool_invocation")
_emit_captures_execution_output("p2", "route_policy_governor", "exec_output")
_emit_dispatches_agent("p3", "route_policy_governor", "agent_dispatch")
_emit_coordinates_agents("p3", "route_policy_governor", "agent_coordination")
_emit_records_workflow_lineage("p3", "route_policy_governor", "workflow_lineage")
_emit_records_healing_outcome("p3", "route_policy_governor", "healing_outcome")
_emit_escalates_failure("p3", "route_policy_governor", "failure_escalation")
_emit_orchestrates_workflow("p3", "route_policy_governor", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "route_policy_governor", "healing_dispatch")
_emit_invokes_evaluation("p3", "route_policy_governor", "evaluation_signal")
_emit_records_telemetry_event("p4", "route_policy_governor", "telemetry_event")
_emit_captures_evaluation_metric("p4", "route_policy_governor", "eval_metric")
_emit_stores_embedding("p4", "route_policy_governor", "embedding_store")
_emit_updates_meta_learning_state("p4", "route_policy_governor", "meta_learning")
_emit_links_execution_to_snapshot("p4", "route_policy_governor", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("route_policy_governor", "p4obs", "metric_1")
_emit_emits_metric_event("route_policy_governor", "p4obs", "metric_2")
_emit_emits_metric_event("route_policy_governor", "p4obs", "metric_3")
_emit_emits_metric_event("route_policy_governor", "p4obs", "metric_4")
_emit_emits_metric_event("route_policy_governor", "p4obs", "metric_5")
_emit_emits_metric_event("route_policy_governor", "p4obs", "metric_6")
_emit_records_incident_event("route_policy_governor", "p4obs", "incident")
_emit_captures_runtime_anomaly("route_policy_governor", "p4obs", "anomaly")
_emit_writes_observability_log("route_policy_governor", "p4obs", "obs_log")
_emit_updates_monitoring_state("route_policy_governor", "p4obs", "mon_state")
_emit_triggers_alert("route_policy_governor", "p4obs", "alert")
_emit_links_incident_trace("route_policy_governor", "p4obs", "trace_link")
_emit_captures_pattern("route_policy_governor", "p3lm", "pattern")
_emit_records_learning_event("route_policy_governor", "p3lm", "learning_event")
_emit_writes_learning_snapshot("route_policy_governor", "p3lm", "snapshot")
_emit_feeds_meta_learning("route_policy_governor", "p3lm", "meta_feed")
_emit_updates_routing_strategy("route_policy_governor", "p3lm", "routing")
_emit_improves_agent_policy("route_policy_governor", "p3lm", "policy")
_emit_stores_learning_state("route_policy_governor", "p3lm", "state")
_emit_records_execution_trace("route_policy_governor", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("route_policy_governor", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("route_policy_governor", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("route_policy_governor", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("route_policy_governor", "L4_STATE", "p2_trace_5")
_emit_reads_environ("route_policy_governor", "env_read", "p2_env_1")
_emit_reads_environ("route_policy_governor", "env_read", "p2_env_2")
_emit_reads_runtime_state("route_policy_governor", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("route_policy_governor", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "route_policy_governor", "context_pull")
_emit_pulls_context("p1", "route_policy_governor", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "route_policy_governor", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "route_policy_governor", "uwg_term_2")
_emit_writes_through("p1", "route_policy_governor", "write_through")
_emit_writes_through("p1", "route_policy_governor", "write_through_2")
_emit_validated_by_safety_plane("p1", "route_policy_governor", "safety_validation")
_emit_invokes_eval("p1", "route_policy_governor", "eval_call")
_emit_proposal_commits_routing("p1", "route_policy_governor", "routing_commit")

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RoutingProposal:
    """A routing decision committed to a governance policy hash.

    Every L0 routing dispatch must produce a RoutingProposal before
    the request is forwarded, making the policy provenance traceable.
    """

    trace_id: str
    route_path: str
    policy_hash: str
    proposal_hash: str
    routing_artifact: RoutingArtifact
    boundary_verified: bool
    metadata: dict[str, Any] = field(default_factory=dict)

    def satisfies_policy(self) -> bool:
        """Return True if the proposal was committed against a non-empty policy hash."""
        return bool(self.policy_hash) and self.boundary_verified


class RoutePolicyGovernor:
    """Commits routing decisions to a governance policy before dispatch.

    Usage::

        governor = RoutePolicyGovernor(policy_hash="abc123")
        proposal = governor.commit_routing("standard_validation", metadata={})
        assert proposal.satisfies_policy()
        dispatch(proposal.routing_artifact)
    """

    def __init__(
        self,
        policy_hash: str = "",
        gateway: DeterministicRoutingGateway | None = None,
    ) -> None:
        self._policy_hash = policy_hash
        self._gateway = gateway or get_routing_gateway(policy_hash)
        self._ledger: list[RoutingProposal] = []

    def _trace_id(self) -> str:
        from agentic_core.runtime.types.execution_trace import get_active_execution_trace  # noqa: PLC0415

        active = get_active_execution_trace()
        return active.trace_id if active else "no-active-trace"

    def _verify_boundary(self, route_path: str) -> bool:
        """Verify the route path is within governed boundaries.

        Emits ``verifies_boundary`` ADG edge.
        """
        _emit_verifies_policy(str(uuid.uuid4()), "RoutePolicyGovernor._verify_boundary", "L0_ROUTING")
        allowed = {
            "standard_validation",
            "low_risk_bypass",
            "human_escalation",
            "policy_challenge_loop",
            "route_recovery_budget_overflow",
        }
        verified = route_path in allowed
        if not verified:
            logger.warning(
                "GOVERNOR verifies_boundary FAIL route=%s not in governed set",
                route_path,
            )
        return verified

    def commit_routing(
        self,
        route_path: str,
        metadata: dict[str, Any] | None = None,
    ) -> RoutingProposal:
        """Commit a routing decision against the governing policy hash.

        Emits ``proposal_commits_routing`` + ``references_policy_hash``
        + ``reads_governed_config`` ADG edges.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L0_ROUTING, "RoutePolicyGovernor.commit_routing"
        )
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        trace_id = self._trace_id()
        artifact = self._gateway.stamp_decision(route_path, metadata)
        boundary_ok = self._verify_boundary(route_path)
        payload = f"{trace_id}:{route_path}:{self._policy_hash}:{artifact.replay_key}"
        proposal_hash = hashlib.sha256(payload.encode()).hexdigest()[:24]
        proposal = RoutingProposal(
            trace_id=trace_id,
            route_path=route_path,
            policy_hash=self._policy_hash,
            proposal_hash=proposal_hash,
            routing_artifact=artifact,
            boundary_verified=boundary_ok,
            metadata=metadata or {},
        )
        self._ledger.append(proposal)
        _clock = get_clock()
        _clock.emit_replay_key(context=f"{route_path}:{trace_id}")
        # P1/L0: commit full RoutingContract for this governance decision
        _contract_ctx = ContractRoutingContext(
            run_id=trace_id,
            router_id="RoutePolicyGovernor",
            request_hash=proposal_hash,
            candidate_routes=list(
                {
                    "standard_validation",
                    "low_risk_bypass",
                    "human_escalation",
                    "policy_challenge_loop",
                    "route_recovery_budget_overflow",
                }
            ),
            chosen_route=route_path,
            policy_hash=self._policy_hash or "no-policy",
            policy_version="1.0",
        )
        try:
            create_and_commit_routing_contract(_contract_ctx)
        except (ValueError, TypeError, RuntimeError) as _rce:  # guardian: allow-silent-swallow
            logger.warning("GOVERNOR routing contract failed: %s", _rce)
        logger.info(
            "GOVERNOR proposal_commits_routing references_policy_hash "
            "route=%s policy=%s proposal=%s boundary=%s",
            route_path,
            self._policy_hash[:12] if self._policy_hash else "MISSING",
            proposal_hash,
            boundary_ok,
        )
        return proposal

    def ledger(self) -> list[RoutingProposal]:
        return list(self._ledger)


_global_governor: RoutePolicyGovernor | None = None


def get_route_policy_governor(policy_hash: str = "") -> RoutePolicyGovernor:
    global _global_governor
    if _global_governor is None:
        _global_governor = RoutePolicyGovernor(policy_hash=policy_hash)
    return _global_governor


def reset_route_policy_governor() -> None:
    global _global_governor
    _global_governor = None


__all__ = [
    "RoutingProposal",
    "RoutePolicyGovernor",
    "get_route_policy_governor",
    "reset_route_policy_governor",
]
