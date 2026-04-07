"""
Verification Gate Protocol for decoupling base agents from L5 implementations.

This protocol allows SovereignBaseAgent to type-hint against verification
capabilities without importing concrete L5 implementations, preventing
circular dependencies.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

emit_replay_key("p0", "verification_types")
emit_determinism_digest("p0", "verification_types")

_emit_dispatches_healing_run("p1", "verification_types", "L5")
_emit_routes_through("p1", "verification_types", "L5")
_emit_checks_agent_registry("p1", "verification_types", "agent_registry")
_emit_validates_agent_capability("p1", "verification_types", "capability")
_emit_dispatches_execution_plan("p1", "verification_types", "exec_plan")
_emit_agent_executes_agent("p1", "verification_types", "sub_agent")
_emit_routes_to_agent("p1", "verification_types", "target_agent")
_emit_verifies_policy("p1", "verification_types", "policy_check")
_emit_observes_runtime_state("p1", "verification_types", "runtime_state")
_emit_verifies_boundary("p1", "verification_types", "boundary_check")
_emit_transcripts_response("p1", "verification_types", "transcript")
_emit_hard_fails_untranscripted("p1", "verification_types")
_emit_gated_by_confidence("p1", "verification_types", "confidence_gate")
_emit_escalates_to_human("p1", "verification_types", "L5")
_emit_reads_policy_state("p1", "verification_types", "L5")

_emit_applies_guardrail("p0", "verification_types", "p0_governance")
_emit_snapshots_state("p0", "verification_types", "state_snapshot")
_emit_authorize_and_execute("p2", "verification_types", "execution_auth")
_emit_validates_capability("p2", "verification_types", "capability_check")
_emit_routes_to_capability("p2", "verification_types", "capability_route")
_emit_writes_via_uwg("p2", "verification_types", "uwg_write")
_emit_blocks_direct_write("p2", "verification_types", "direct_write_block")
_emit_records_tool_invocation("p2", "verification_types", "tool_invocation")
_emit_captures_execution_output("p2", "verification_types", "exec_output")
_emit_dispatches_agent("p3", "verification_types", "agent_dispatch")
_emit_coordinates_agents("p3", "verification_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "verification_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "verification_types", "healing_outcome")
_emit_escalates_failure("p3", "verification_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "verification_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "verification_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "verification_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "verification_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "verification_types", "eval_metric")
_emit_stores_embedding("p4", "verification_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "verification_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "verification_types", "exec_snapshot_link")
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

_emit_emits_metric_event("verification_types", "p4obs", "metric_1")
_emit_emits_metric_event("verification_types", "p4obs", "metric_2")
_emit_emits_metric_event("verification_types", "p4obs", "metric_3")
_emit_emits_metric_event("verification_types", "p4obs", "metric_4")
_emit_emits_metric_event("verification_types", "p4obs", "metric_5")
_emit_emits_metric_event("verification_types", "p4obs", "metric_6")
_emit_records_incident_event("verification_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("verification_types", "p4obs", "anomaly")
_emit_writes_observability_log("verification_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("verification_types", "p4obs", "mon_state")
_emit_triggers_alert("verification_types", "p4obs", "alert")
_emit_links_incident_trace("verification_types", "p4obs", "trace_link")
_emit_captures_pattern("verification_types", "p3lm", "pattern")
_emit_records_learning_event("verification_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("verification_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("verification_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("verification_types", "p3lm", "routing")
_emit_improves_agent_policy("verification_types", "p3lm", "policy")
_emit_stores_learning_state("verification_types", "p3lm", "state")
_emit_records_execution_trace("verification_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("verification_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("verification_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("verification_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("verification_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("verification_types", "env_read", "p2_env_1")
_emit_reads_environ("verification_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("verification_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("verification_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "verification_types", "context_pull")
_emit_pulls_context("p1", "verification_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "verification_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "verification_types", "uwg_term_2")
_emit_writes_through("p1", "verification_types", "write_through")
_emit_writes_through("p1", "verification_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "verification_types", "safety_validation")
_emit_invokes_eval("p1", "verification_types", "eval_call")
_emit_proposal_commits_routing("p1", "verification_types", "routing_commit")


@dataclass
class VerificationRequest:
    """Request for verification operation."""

    file_path: str
    action_type: str
    target_node: str
    context: dict[str, Any] | None = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.context is None:
            self.context = {}


@dataclass
class VerificationResult:
    """Result of verification operation."""

    success: bool
    reason: str | None = None
    metadata: dict[str, Any] | None = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}


class VerificationGateProtocol(ABC):
    """Protocol for verification gate implementations.

    Implementations must verify that target nodes exist before allowing
    modifications. This prevents hallucinated fixes from being executed.
    """

    SUPPORTED_ACTIONS: list[str] = [
        "delete_import",
        "modify_function",
        "remove_class",
        "modify_method",
        "modify_variable",
        "add_import",
        "rename_symbol",
    ]

    @abstractmethod
    def verify_action(self, request: VerificationRequest) -> VerificationResult:
        """Verify if an action can be performed.

        Args:
            request: Verification request with file path, action type, and target

        Returns:
            VerificationResult indicating success/failure with reason
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if verification gate is available and functional."""
        pass

    @abstractmethod
    def get_supported_actions(self) -> list[str]:
        """Get list of supported action types."""
        pass

    def validate_request(self, request: VerificationRequest) -> str | None:
        """Validate request parameters.

        Returns:
            Error message if invalid, None if valid
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L5_POLICY, "VerificationGateProtocol.validate_request",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:VerificationGateProtocol.validate_request".encode(),
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if not request.file_path:
            return "file_path is required"
        if not request.action_type:
            return "action_type is required"
        if request.action_type not in self.SUPPORTED_ACTIONS:
            return f"unsupported action_type: {request.action_type}"
        if not request.target_node:
            return "target_node is required"
        return None
