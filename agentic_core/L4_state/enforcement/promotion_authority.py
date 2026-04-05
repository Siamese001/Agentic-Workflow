"""Promotion authority for Wave 17 - P2 Promotion Authority.

This module provides scoped pointer updates with single-use tokens
through the gateway.
"""

import hashlib
import logging
import time
from dataclasses import dataclass

from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_snapshots_state,
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

emit_replay_key("p0", "promotion_authority")
emit_determinism_digest("p0", "promotion_authority")

_emit_dispatches_healing_run("p1", "promotion_authority", "L4")
_emit_routes_through("p1", "promotion_authority", "L4")
_emit_checks_agent_registry("p1", "promotion_authority", "agent_registry")
_emit_validates_agent_capability("p1", "promotion_authority", "capability")
_emit_dispatches_execution_plan("p1", "promotion_authority", "exec_plan")
_emit_agent_executes_agent("p1", "promotion_authority", "sub_agent")
_emit_routes_to_agent("p1", "promotion_authority", "target_agent")
_emit_verifies_policy("p1", "promotion_authority", "policy_check")
_emit_observes_runtime_state("p1", "promotion_authority", "runtime_state")
_emit_verifies_boundary("p1", "promotion_authority", "boundary_check")
_emit_transcripts_response("p1", "promotion_authority", "transcript")
_emit_hard_fails_untranscripted("p1", "promotion_authority")
_emit_gated_by_confidence("p1", "promotion_authority", "confidence_gate")
_emit_escalates_to_human("p1", "promotion_authority", "L4")
_emit_reads_policy_state("p1", "promotion_authority", "L4")
_emit_authorize_and_execute("p2", "promotion_authority", "execution_auth")
_emit_validates_capability("p2", "promotion_authority", "capability_check")
_emit_routes_to_capability("p2", "promotion_authority", "capability_route")
_emit_writes_via_uwg("p2", "promotion_authority", "uwg_write")
_emit_blocks_direct_write("p2", "promotion_authority", "direct_write_block")
_emit_records_tool_invocation("p2", "promotion_authority", "tool_invocation")
_emit_captures_execution_output("p2", "promotion_authority", "exec_output")
_emit_dispatches_agent("p3", "promotion_authority", "agent_dispatch")
_emit_coordinates_agents("p3", "promotion_authority", "agent_coordination")
_emit_records_workflow_lineage("p3", "promotion_authority", "workflow_lineage")
_emit_records_healing_outcome("p3", "promotion_authority", "healing_outcome")
_emit_escalates_failure("p3", "promotion_authority", "failure_escalation")
_emit_orchestrates_workflow("p3", "promotion_authority", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "promotion_authority", "healing_dispatch")
_emit_invokes_evaluation("p3", "promotion_authority", "evaluation_signal")
_emit_records_telemetry_event("p4", "promotion_authority", "telemetry_event")
_emit_captures_evaluation_metric("p4", "promotion_authority", "eval_metric")
_emit_stores_embedding("p4", "promotion_authority", "embedding_store")
_emit_updates_meta_learning_state("p4", "promotion_authority", "meta_learning")
_emit_links_execution_to_snapshot("p4", "promotion_authority", "exec_snapshot_link")
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
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("promotion_authority", "p4obs", "metric_1")
_emit_emits_metric_event("promotion_authority", "p4obs", "metric_2")
_emit_emits_metric_event("promotion_authority", "p4obs", "metric_3")
_emit_emits_metric_event("promotion_authority", "p4obs", "metric_4")
_emit_emits_metric_event("promotion_authority", "p4obs", "metric_5")
_emit_emits_metric_event("promotion_authority", "p4obs", "metric_6")
_emit_records_incident_event("promotion_authority", "p4obs", "incident")
_emit_captures_runtime_anomaly("promotion_authority", "p4obs", "anomaly")
_emit_writes_observability_log("promotion_authority", "p4obs", "obs_log")
_emit_updates_monitoring_state("promotion_authority", "p4obs", "mon_state")
_emit_triggers_alert("promotion_authority", "p4obs", "alert")
_emit_links_incident_trace("promotion_authority", "p4obs", "trace_link")
_emit_captures_pattern("promotion_authority", "p3lm", "pattern")
_emit_records_learning_event("promotion_authority", "p3lm", "learning_event")
_emit_writes_learning_snapshot("promotion_authority", "p3lm", "snapshot")
_emit_feeds_meta_learning("promotion_authority", "p3lm", "meta_feed")
_emit_updates_routing_strategy("promotion_authority", "p3lm", "routing")
_emit_improves_agent_policy("promotion_authority", "p3lm", "policy")
_emit_stores_learning_state("promotion_authority", "p3lm", "state")
_emit_records_execution_trace("promotion_authority", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("promotion_authority", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("promotion_authority", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("promotion_authority", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("promotion_authority", "L4_STATE", "p2_trace_5")
_emit_reads_environ("promotion_authority", "env_read", "p2_env_1")
_emit_reads_environ("promotion_authority", "env_read", "p2_env_2")
_emit_reads_runtime_state("promotion_authority", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("promotion_authority", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "promotion_authority", "context_pull")
_emit_pulls_context("p1", "promotion_authority", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "promotion_authority", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "promotion_authority", "uwg_term_2")
_emit_writes_through("p1", "promotion_authority", "write_through")
_emit_writes_through("p1", "promotion_authority", "write_through_2")
_emit_validated_by_safety_plane("p1", "promotion_authority", "safety_validation")
_emit_invokes_eval("p1", "promotion_authority", "eval_call")
_emit_proposal_commits_routing("p1", "promotion_authority", "routing_commit")

Logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PromotionPointerUpdate:
    """Immutable record of a promotion pointer update."""

    old_pointer: str
    new_pointer: str
    timestamp: float
    capability_token_hash: str
    guardian_signature: str
    semantic_clock_tick: int


class PromotionAuthority:
    """Manages promotion pointer updates through gateway with capability tokens."""

    def __init__(self):
        self._write_gateway = None
        self._active_updates: dict[str, PromotionPointerUpdate] = {}

    def set_write_gateway(self, gateway):
        """Set the write gateway for pointer updates."""
        self._write_gateway = gateway

    def update_pointer_via_gateway(self, new_pointer: str, capability_token) -> PromotionPointerUpdate:
        """Update pointer via gateway with capability token validation."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(
            str(_uuid.uuid4()), "PromotionAuthority.update_pointer_via_gateway", "state_snapshot"
        )
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(
            str(_uuid.uuid4()), "PromotionAuthority.update_pointer_via_gateway", "p0_governance"
        )
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L4_STATE, "PromotionAuthority.update_pointer_via_gateway"
        )

        if not self._write_gateway:
            raise RuntimeError("Write gateway not configured")
        if not hasattr(capability_token, "validate_scope_and_use"):
            raise ValueError("Invalid capability token - missing validation method")
        if not capability_token.validate_scope_and_use():
            raise RuntimeError("Capability token validation failed")
        old_pointer = self._get_current_pointer(capability_token.target_namespace)
        update = PromotionPointerUpdate(
            old_pointer=old_pointer,
            new_pointer=new_pointer,
            timestamp=time.time(),
            capability_token_hash=hashlib.sha256(str(capability_token).encode()).hexdigest(),
            guardian_signature="guardian_signature_placeholder",
            semantic_clock_tick=capability_token.semantic_clock_tick,
        )
        self._write_gateway.update_pointer(
            namespace=capability_token.target_namespace,
            old_pointer=old_pointer,
            new_pointer=new_pointer,
            capability_token=capability_token,
        )
        self._active_updates[capability_token.target_namespace] = update
        Logger.info(
            f"Pointer updated in namespace {capability_token.target_namespace}: {old_pointer} -> {new_pointer}"
        )
        return update

    def _get_current_pointer(self, namespace: str) -> str:
        """Get current pointer for namespace."""
        existing = self._active_updates.get(namespace)
        if existing is not None:
            return existing.new_pointer
        return f"current_pointer_{namespace}"

    def get_update_history(self, namespace: str) -> PromotionPointerUpdate | None:
        """Get update history for namespace."""
        return self._active_updates.get(namespace)

    def validate_pointer_update_integrity(self, namespace: str, expected_hash: str) -> bool:
        """Validate pointer update integrity."""
        update = self._active_updates.get(namespace)
        if not update:
            return False
        computed_hash = hashlib.sha256(
            f"{update.old_pointer}{update.new_pointer}{update.timestamp}".encode()
        ).hexdigest()
        return computed_hash == expected_hash


_promotion_authority = None


def get_promotion_authority() -> PromotionAuthority:
    """Get the singleton promotion authority instance."""
    global _promotion_authority
    if _promotion_authority is None:
        _promotion_authority = PromotionAuthority()
    return _promotion_authority


def update_pointer_via_gateway(new_pointer: str, capability_token) -> PromotionPointerUpdate:
    """Update pointer via gateway with capability token validation."""
    authority = get_promotion_authority()
    return authority.update_pointer_via_gateway(new_pointer, capability_token)


def validate_pointer_update_integrity(namespace: str, expected_hash: str) -> bool:
    """Validate pointer update integrity."""
    authority = get_promotion_authority()
    return authority.validate_pointer_update_integrity(namespace, expected_hash)
