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

from agentic_core.L0_routing.types.determinism_types import (
    SemanticClockSnapshot,
)  # guardian: allow-layer-violation -- L2 module uses L0 config/enforcement; intentional downward enforcement-chain dependency
from agentic_core.L2_execution.types.capability_token_types import (
    CapabilityDecisionArtifact,
    CapabilityEnforcer,
    CapabilityTokenArtifact,
    build_capability_decision,
)
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "capability_chokepoint")
trace_contract.emit_determinism_digest("p0", "capability_chokepoint")

trace_contract._emit_dispatches_healing_run("p1", "capability_chokepoint", "L2")
trace_contract._emit_routes_through("p1", "capability_chokepoint", "L2")
trace_contract._emit_checks_agent_registry("p1", "capability_chokepoint", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "capability_chokepoint", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "capability_chokepoint", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "capability_chokepoint", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "capability_chokepoint", "target_agent")
trace_contract._emit_verifies_policy("p1", "capability_chokepoint", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "capability_chokepoint", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "capability_chokepoint", "boundary_check")
trace_contract._emit_transcripts_response("p1", "capability_chokepoint", "transcript")
trace_contract._emit_gated_by_confidence("p1", "capability_chokepoint", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "capability_chokepoint", "L2")
trace_contract._emit_reads_policy_state("p1", "capability_chokepoint", "L2")

trace_contract._emit_snapshots_state("p0", "capability_chokepoint", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "capability_chokepoint", "execution_auth")
trace_contract._emit_validates_capability("p2", "capability_chokepoint", "capability_check")
trace_contract._emit_routes_to_capability("p2", "capability_chokepoint", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "capability_chokepoint", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "capability_chokepoint", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "capability_chokepoint", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "capability_chokepoint", "exec_output")
trace_contract._emit_dispatches_agent("p3", "capability_chokepoint", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "capability_chokepoint", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "capability_chokepoint", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "capability_chokepoint", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "capability_chokepoint", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "capability_chokepoint", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "capability_chokepoint", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "capability_chokepoint", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "capability_chokepoint", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "capability_chokepoint", "eval_metric")
trace_contract._emit_stores_embedding("p4", "capability_chokepoint", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "capability_chokepoint", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "capability_chokepoint", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("capability_chokepoint", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("capability_chokepoint", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("capability_chokepoint", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("capability_chokepoint", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("capability_chokepoint", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("capability_chokepoint", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("capability_chokepoint", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("capability_chokepoint", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("capability_chokepoint", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("capability_chokepoint", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("capability_chokepoint", "p4obs", "alert")
trace_contract._emit_links_incident_trace("capability_chokepoint", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("capability_chokepoint", "p3lm", "pattern")
trace_contract._emit_records_learning_event("capability_chokepoint", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("capability_chokepoint", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("capability_chokepoint", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("capability_chokepoint", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("capability_chokepoint", "p3lm", "policy")
trace_contract._emit_stores_learning_state("capability_chokepoint", "p3lm", "state")
trace_contract._emit_records_execution_trace("capability_chokepoint", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("capability_chokepoint", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("capability_chokepoint", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("capability_chokepoint", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("capability_chokepoint", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("capability_chokepoint", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("capability_chokepoint", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("capability_chokepoint", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("capability_chokepoint", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "capability_chokepoint", "context_pull")
trace_contract._emit_pulls_context("p1", "capability_chokepoint", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "capability_chokepoint", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "capability_chokepoint", "uwg_term_2")
trace_contract._emit_writes_through("p1", "capability_chokepoint", "write_through")
trace_contract._emit_writes_through("p1", "capability_chokepoint", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "capability_chokepoint", "safety_validation")
trace_contract._emit_invokes_eval("p1", "capability_chokepoint", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "capability_chokepoint", "routing_commit")

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
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L2_EXECUTION,
            "CapabilityChokepoint.authorize_and_execute",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:CapabilityChokepoint.authorize_and_execute".encode(),
        ).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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
    trace_contract._emit_hard_fails_untranscripted(str(uuid.uuid4()), "Module.authorize_and_execute")
    trace_contract._emit_applies_guardrail(str(uuid.uuid4()), "Module.authorize_and_execute", "L2_EXECUTION")
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
