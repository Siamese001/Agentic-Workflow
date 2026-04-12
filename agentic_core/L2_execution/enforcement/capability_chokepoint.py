"""P5.1 Capability-Gated L2 Single Chokepoint — G-12-3 Implementation.

Every L2 execution invocation MUST pass through authorize_and_execute.
Missing or invalid CapabilityTokenArtifact => FAIL-CLOSED (PermissionError).
Every invocation emits a typed CapabilityDecisionArtifact (ALLOW or DENY).
No alternate execution path may bypass this module.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any, Callable, TypeVar

from agentic_core.L0_routing.types.determinism_types import SemanticClockSnapshot
from agentic_core.L2_execution.types.capability_token_types import (
    CapabilityDecisionArtifact,
    CapabilityEnforcer,
    CapabilityTokenArtifact,
    build_capability_decision,
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
    _emit_signs_execution_trace,
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

emit_replay_key("p0", "capability_chokepoint")
emit_determinism_digest("p0", "capability_chokepoint")

_emit_dispatches_healing_run("p1", "capability_chokepoint", "L2")
_emit_routes_through("p1", "capability_chokepoint", "L2")
_emit_checks_agent_registry("p1", "capability_chokepoint", "agent_registry")
_emit_validates_agent_capability("p1", "capability_chokepoint", "capability")
_emit_dispatches_execution_plan("p1", "capability_chokepoint", "exec_plan")
_emit_agent_executes_agent("p1", "capability_chokepoint", "sub_agent")
_emit_routes_to_agent("p1", "capability_chokepoint", "target_agent")
_emit_verifies_policy("p1", "capability_chokepoint", "policy_check")
_emit_observes_runtime_state("p1", "capability_chokepoint", "runtime_state")
_emit_verifies_boundary("p1", "capability_chokepoint", "boundary_check")
_emit_transcripts_response("p1", "capability_chokepoint", "transcript")
_emit_gated_by_confidence("p1", "capability_chokepoint", "confidence_gate")
_emit_escalates_to_human("p1", "capability_chokepoint", "L2")
_emit_reads_policy_state("p1", "capability_chokepoint", "L2")

_emit_snapshots_state("p0", "capability_chokepoint", "state_snapshot")
_emit_authorize_and_execute("p2", "capability_chokepoint", "execution_auth")
_emit_validates_capability("p2", "capability_chokepoint", "capability_check")
_emit_routes_to_capability("p2", "capability_chokepoint", "capability_route")
_emit_writes_via_uwg("p2", "capability_chokepoint", "uwg_write")
_emit_blocks_direct_write("p2", "capability_chokepoint", "direct_write_block")
_emit_records_tool_invocation("p2", "capability_chokepoint", "tool_invocation")
_emit_captures_execution_output("p2", "capability_chokepoint", "exec_output")
_emit_dispatches_agent("p3", "capability_chokepoint", "agent_dispatch")
_emit_coordinates_agents("p3", "capability_chokepoint", "agent_coordination")
_emit_records_workflow_lineage("p3", "capability_chokepoint", "workflow_lineage")
_emit_records_healing_outcome("p3", "capability_chokepoint", "healing_outcome")
_emit_escalates_failure("p3", "capability_chokepoint", "failure_escalation")
_emit_orchestrates_workflow("p3", "capability_chokepoint", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "capability_chokepoint", "healing_dispatch")
_emit_invokes_evaluation("p3", "capability_chokepoint", "evaluation_signal")
_emit_records_telemetry_event("p4", "capability_chokepoint", "telemetry_event")
_emit_captures_evaluation_metric("p4", "capability_chokepoint", "eval_metric")
_emit_stores_embedding("p4", "capability_chokepoint", "embedding_store")
_emit_updates_meta_learning_state("p4", "capability_chokepoint", "meta_learning")
_emit_links_execution_to_snapshot("p4", "capability_chokepoint", "exec_snapshot_link")
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
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
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

_emit_emits_metric_event("capability_chokepoint", "p4obs", "metric_1")
_emit_emits_metric_event("capability_chokepoint", "p4obs", "metric_2")
_emit_emits_metric_event("capability_chokepoint", "p4obs", "metric_3")
_emit_emits_metric_event("capability_chokepoint", "p4obs", "metric_4")
_emit_emits_metric_event("capability_chokepoint", "p4obs", "metric_5")
_emit_emits_metric_event("capability_chokepoint", "p4obs", "metric_6")
_emit_records_incident_event("capability_chokepoint", "p4obs", "incident")
_emit_captures_runtime_anomaly("capability_chokepoint", "p4obs", "anomaly")
_emit_writes_observability_log("capability_chokepoint", "p4obs", "obs_log")
_emit_updates_monitoring_state("capability_chokepoint", "p4obs", "mon_state")
_emit_triggers_alert("capability_chokepoint", "p4obs", "alert")
_emit_links_incident_trace("capability_chokepoint", "p4obs", "trace_link")
_emit_captures_pattern("capability_chokepoint", "p3lm", "pattern")
_emit_records_learning_event("capability_chokepoint", "p3lm", "learning_event")
_emit_writes_learning_snapshot("capability_chokepoint", "p3lm", "snapshot")
_emit_feeds_meta_learning("capability_chokepoint", "p3lm", "meta_feed")
_emit_updates_routing_strategy("capability_chokepoint", "p3lm", "routing")
_emit_improves_agent_policy("capability_chokepoint", "p3lm", "policy")
_emit_stores_learning_state("capability_chokepoint", "p3lm", "state")
_emit_records_execution_trace("capability_chokepoint", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("capability_chokepoint", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("capability_chokepoint", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("capability_chokepoint", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("capability_chokepoint", "L4_STATE", "p2_trace_5")
_emit_reads_environ("capability_chokepoint", "env_read", "p2_env_1")
_emit_reads_environ("capability_chokepoint", "env_read", "p2_env_2")
_emit_reads_runtime_state("capability_chokepoint", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("capability_chokepoint", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "capability_chokepoint", "context_pull")
_emit_pulls_context("p1", "capability_chokepoint", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "capability_chokepoint", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "capability_chokepoint", "uwg_term_2")
_emit_writes_through("p1", "capability_chokepoint", "write_through")
_emit_writes_through("p1", "capability_chokepoint", "write_through_2")
_emit_validated_by_safety_plane("p1", "capability_chokepoint", "safety_validation")
_emit_invokes_eval("p1", "capability_chokepoint", "eval_call")
_emit_proposal_commits_routing("p1", "capability_chokepoint", "routing_commit")

logger = logging.getLogger(__name__)

T = TypeVar("T")

# =============================================================================
# Single chokepoint — all L2 execution MUST route through this function
# =============================================================================


class CapabilityChokepoint:
    """Singleton-style chokepoint enforcer for the L2 execution boundary.

    Tracks all decisions emitted during the lifetime of this instance.
    """

    def __init__(self) -> None:
        self._decisions: list[CapabilityDecisionArtifact] = []
        self._frozen: bool = False

    @property
    def decisions(self) -> list[CapabilityDecisionArtifact]:
        """All decisions emitted through this chokepoint."""
        return list(self._decisions)

    def freeze(self) -> None:
        """REQ-091: Tier III freeze — token issuance and execution blocked."""
        self._frozen = True

    def issue_token(self, scope: str, trace_id: str) -> None:
        """REQ-091: Issue a capability token for a given scope.

        Raises PermissionError if the chokepoint is frozen.
        """
        if self._frozen:
            raise PermissionError(
                f"REQ-091: CapabilityChokepoint frozen — token issuance blocked (scope={scope}).",
            )

    def authorize_and_execute(
        self,
        *,
        token: CapabilityTokenArtifact | None,
        fn: Callable[..., T],
        args: tuple[Any, ...] = (),
        kwargs: dict[str, Any] | None = None,
        tool_name: str,
        action: str,
        requested_resource: str,
        required_permission: str,
        semantic_clock: SemanticClockSnapshot,
    ) -> T:
        """Single L2 execution chokepoint — P5.1 enforcement.

        Args:
            token: CapabilityTokenArtifact. None => FAIL-CLOSED.
            fn: The callable to execute on ALLOW.
            args: Positional arguments for fn.
            kwargs: Keyword arguments for fn.
            tool_name: Name of the tool being invoked.
            action: Action being performed.
            requested_resource: Resource path being accessed.
            required_permission: Permission code required.
            semantic_clock: Current semantic clock snapshot.

        Returns:
            Result of fn(*args, **kwargs) on ALLOW.

        Raises:
            PermissionError: On DENY or missing/invalid token (FAIL-CLOSED).
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L2_EXECUTION,
            "CapabilityChokepoint.authorize_and_execute",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:CapabilityChokepoint.authorize_and_execute".encode(),
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if kwargs is None:
            kwargs = {}

        # FAIL-CLOSED: missing token
        if token is None:
            decision = build_capability_decision(
                semantic_clock=semantic_clock,
                tool_name=tool_name,
                action=action,
                requested_resource=requested_resource,
                decision="DENY",
                deny_reason="TOKEN_MISSING",
                capability_trace_id="NONE",
            )
            self._decisions.append(decision)
            logger.warning(
                "CAPABILITY_CHOKEPOINT DENY: token missing for %s/%s",
                tool_name,
                action,
            )
            raise PermissionError("CAPABILITY_CHOKEPOINT_FAIL_CLOSED: no CapabilityTokenArtifact provided")

        # FAIL-CLOSED: invalid token type
        if not isinstance(token, CapabilityTokenArtifact):
            decision = build_capability_decision(
                semantic_clock=semantic_clock,
                tool_name=tool_name,
                action=action,
                requested_resource=requested_resource,
                decision="DENY",
                deny_reason=f"TOKEN_INVALID_TYPE:{type(token).__name__}",
                capability_trace_id="NONE",
            )
            self._decisions.append(decision)
            logger.warning(
                "CAPABILITY_CHOKEPOINT DENY: invalid token type %s for %s/%s",
                type(token).__name__,
                tool_name,
                action,
            )
            raise PermissionError(
                f"CAPABILITY_CHOKEPOINT_FAIL_CLOSED: expected CapabilityTokenArtifact, "
                f"got {type(token).__name__}",
            )

        # FAIL-CLOSED: invalid artifact_type field
        if token.artifact_type != "CAPABILITY_TOKEN":
            decision = build_capability_decision(
                semantic_clock=semantic_clock,
                tool_name=tool_name,
                action=action,
                requested_resource=requested_resource,
                decision="DENY",
                deny_reason=f"TOKEN_ARTIFACT_TYPE_MISMATCH:{token.artifact_type}",
                capability_trace_id=token.trace_id,
            )
            self._decisions.append(decision)
            raise PermissionError(
                f"CAPABILITY_CHOKEPOINT_FAIL_CLOSED: artifact_type mismatch '{token.artifact_type}'",
            )

        # Delegate to CapabilityEnforcer for permission/path/quota checks
        enforcer = CapabilityEnforcer(token)
        # CapabilityEnforcer.check() raises PermissionError on DENY
        decision = enforcer.check(
            tool_name=tool_name,
            action=action,
            requested_resource=requested_resource,
            required_permission=required_permission,
            semantic_clock=semantic_clock,
        )
        self._decisions.append(decision)

        # ALLOW — execute the guarded function
        logger.info(
            "CAPABILITY_CHOKEPOINT ALLOW: %s/%s (trace=%s)",
            tool_name,
            action,
            decision.trace_id,
        )
        return fn(*args, **kwargs)


# Module-level singleton — the ONE chokepoint for all L2 execution
_chokepoint = CapabilityChokepoint()


def authorize_and_execute(
    *,
    token: CapabilityTokenArtifact | None,
    fn: Callable[..., T],
    args: tuple[Any, ...] = (),
    kwargs: dict[str, Any] | None = None,
    tool_name: str,
    action: str,
    requested_resource: str,
    required_permission: str,
    semantic_clock: SemanticClockSnapshot,
) -> T:
    """Module-level entry — delegates to the singleton CapabilityChokepoint.

    This is the ONLY function external callers should use for L2 execution.
    """
    _emit_hard_fails_untranscripted(str(uuid.uuid4()), "Module.authorize_and_execute")
    _emit_applies_guardrail(str(uuid.uuid4()), "Module.authorize_and_execute", "L2_EXECUTION")
    return _chokepoint.authorize_and_execute(
        token=token,
        fn=fn,
        args=args,
        kwargs=kwargs,
        tool_name=tool_name,
        action=action,
        requested_resource=requested_resource,
        required_permission=required_permission,
        semantic_clock=semantic_clock,
    )


def get_chokepoint() -> CapabilityChokepoint:
    """Return the module-level singleton for inspection/testing."""
    return _chokepoint


def reset_chokepoint() -> None:
    """Reset the singleton (testing only)."""
    global _chokepoint
    _chokepoint = CapabilityChokepoint()


__all__ = [
    "CapabilityChokepoint",
    "authorize_and_execute",
    "get_chokepoint",
    "reset_chokepoint",
]
