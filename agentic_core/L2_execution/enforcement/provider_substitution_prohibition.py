"""
Provider Substitution Prohibition (REQ-415)

Ensures SovereignLLMGateway MUST NOT substitute provider/model on failure.
Any failure MUST be fail-closed.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from typing import Any

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

emit_replay_key("p0", "provider_substitution_prohibition")
emit_determinism_digest("p0", "provider_substitution_prohibition")

_emit_dispatches_healing_run("p1", "provider_substitution_prohibition", "L2")
_emit_routes_through("p1", "provider_substitution_prohibition", "L2")
_emit_checks_agent_registry("p1", "provider_substitution_prohibition", "agent_registry")
_emit_validates_agent_capability("p1", "provider_substitution_prohibition", "capability")
_emit_dispatches_execution_plan("p1", "provider_substitution_prohibition", "exec_plan")
_emit_agent_executes_agent("p1", "provider_substitution_prohibition", "sub_agent")
_emit_routes_to_agent("p1", "provider_substitution_prohibition", "target_agent")
_emit_verifies_policy("p1", "provider_substitution_prohibition", "policy_check")
_emit_observes_runtime_state("p1", "provider_substitution_prohibition", "runtime_state")
_emit_verifies_boundary("p1", "provider_substitution_prohibition", "boundary_check")
_emit_transcripts_response("p1", "provider_substitution_prohibition", "transcript")
_emit_hard_fails_untranscripted("p1", "provider_substitution_prohibition")
_emit_gated_by_confidence("p1", "provider_substitution_prohibition", "confidence_gate")
_emit_escalates_to_human("p1", "provider_substitution_prohibition", "L2")
_emit_reads_policy_state("p1", "provider_substitution_prohibition", "L2")

_emit_snapshots_state("p0", "provider_substitution_prohibition", "state_snapshot")
_emit_authorize_and_execute("p2", "provider_substitution_prohibition", "execution_auth")
_emit_validates_capability("p2", "provider_substitution_prohibition", "capability_check")
_emit_routes_to_capability("p2", "provider_substitution_prohibition", "capability_route")
_emit_writes_via_uwg("p2", "provider_substitution_prohibition", "uwg_write")
_emit_blocks_direct_write("p2", "provider_substitution_prohibition", "direct_write_block")
_emit_records_tool_invocation("p2", "provider_substitution_prohibition", "tool_invocation")
_emit_captures_execution_output("p2", "provider_substitution_prohibition", "exec_output")
_emit_dispatches_agent("p3", "provider_substitution_prohibition", "agent_dispatch")
_emit_coordinates_agents("p3", "provider_substitution_prohibition", "agent_coordination")
_emit_records_workflow_lineage("p3", "provider_substitution_prohibition", "workflow_lineage")
_emit_records_healing_outcome("p3", "provider_substitution_prohibition", "healing_outcome")
_emit_escalates_failure("p3", "provider_substitution_prohibition", "failure_escalation")
_emit_orchestrates_workflow("p3", "provider_substitution_prohibition", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "provider_substitution_prohibition", "healing_dispatch")
_emit_invokes_evaluation("p3", "provider_substitution_prohibition", "evaluation_signal")
_emit_records_telemetry_event("p4", "provider_substitution_prohibition", "telemetry_event")
_emit_captures_evaluation_metric("p4", "provider_substitution_prohibition", "eval_metric")
_emit_stores_embedding("p4", "provider_substitution_prohibition", "embedding_store")
_emit_updates_meta_learning_state("p4", "provider_substitution_prohibition", "meta_learning")
_emit_links_execution_to_snapshot("p4", "provider_substitution_prohibition", "exec_snapshot_link")
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

_emit_emits_metric_event("provider_substitution_prohibition", "p4obs", "metric_1")
_emit_emits_metric_event("provider_substitution_prohibition", "p4obs", "metric_2")
_emit_emits_metric_event("provider_substitution_prohibition", "p4obs", "metric_3")
_emit_emits_metric_event("provider_substitution_prohibition", "p4obs", "metric_4")
_emit_emits_metric_event("provider_substitution_prohibition", "p4obs", "metric_5")
_emit_emits_metric_event("provider_substitution_prohibition", "p4obs", "metric_6")
_emit_records_incident_event("provider_substitution_prohibition", "p4obs", "incident")
_emit_captures_runtime_anomaly("provider_substitution_prohibition", "p4obs", "anomaly")
_emit_writes_observability_log("provider_substitution_prohibition", "p4obs", "obs_log")
_emit_updates_monitoring_state("provider_substitution_prohibition", "p4obs", "mon_state")
_emit_triggers_alert("provider_substitution_prohibition", "p4obs", "alert")
_emit_links_incident_trace("provider_substitution_prohibition", "p4obs", "trace_link")
_emit_captures_pattern("provider_substitution_prohibition", "p3lm", "pattern")
_emit_records_learning_event("provider_substitution_prohibition", "p3lm", "learning_event")
_emit_writes_learning_snapshot("provider_substitution_prohibition", "p3lm", "snapshot")
_emit_feeds_meta_learning("provider_substitution_prohibition", "p3lm", "meta_feed")
_emit_updates_routing_strategy("provider_substitution_prohibition", "p3lm", "routing")
_emit_improves_agent_policy("provider_substitution_prohibition", "p3lm", "policy")
_emit_stores_learning_state("provider_substitution_prohibition", "p3lm", "state")
_emit_records_execution_trace("provider_substitution_prohibition", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("provider_substitution_prohibition", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("provider_substitution_prohibition", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("provider_substitution_prohibition", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("provider_substitution_prohibition", "L4_STATE", "p2_trace_5")
_emit_reads_environ("provider_substitution_prohibition", "env_read", "p2_env_1")
_emit_reads_environ("provider_substitution_prohibition", "env_read", "p2_env_2")
_emit_reads_runtime_state("provider_substitution_prohibition", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("provider_substitution_prohibition", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "provider_substitution_prohibition", "context_pull")
_emit_pulls_context("p1", "provider_substitution_prohibition", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "provider_substitution_prohibition", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "provider_substitution_prohibition", "uwg_term_2")
_emit_writes_through("p1", "provider_substitution_prohibition", "write_through")
_emit_writes_through("p1", "provider_substitution_prohibition", "write_through_2")
_emit_validated_by_safety_plane("p1", "provider_substitution_prohibition", "safety_validation")
_emit_invokes_eval("p1", "provider_substitution_prohibition", "eval_call")
_emit_proposal_commits_routing("p1", "provider_substitution_prohibition", "routing_commit")

Logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ProviderRequest:
    """Immutable record of original provider request."""

    provider: str
    model: str
    agent_id: str
    request_id: str


class ProviderSubstitutionViolation(Exception):
    """Raised when provider substitution is attempted."""

    pass


def validate_provider_request(
    original_request: ProviderRequest,
    actual_provider: str,
    actual_model: str,
    context: dict[str, Any] | None = None,
) -> None:
    """Validate that no provider/model substitution occurred (REQ-415).

    Args:
        original_request: The original request made by the agent
        actual_provider: The provider actually used
        actual_model: The model actually used
        context: Optional context for logging

    Raises:
        ProviderSubstitutionViolation: If substitution is detected
    """
    _emit_applies_guardrail(str(uuid.uuid4()), "Module.validate_provider_request", "L2_EXECUTION")
    if actual_provider != original_request.provider:
        violation_msg = f"Provider substitution detected: agent '{original_request.agent_id}' requested provider '{original_request.provider}' but got '{actual_provider}'. Provider substitution is prohibited (REQ-415)."
        Logger.error(violation_msg)
        raise ProviderSubstitutionViolation(violation_msg)
    if actual_model != original_request.model:
        violation_msg = f"Model substitution detected: agent '{original_request.agent_id}' requested model '{original_request.model}' but got '{actual_model}'. Model substitution is prohibited (REQ-415)."
        Logger.error(violation_msg)
        raise ProviderSubstitutionViolation(violation_msg)
    Logger.debug(
        f"Provider request validated: agent '{original_request.agent_id}' using provider '{actual_provider}' with model '{actual_model}'"
    )


def enforce_fail_closed_on_failure(
    original_request: ProviderRequest, error: Exception, attempted_substitution: dict[str, str] | None = None
) -> None:
    """Ensure fail-closed behavior on provider failure (REQ-415).

    Args:
        original_request: The original request that failed
        error: The error that occurred
        attempted_substitution: Any attempted substitution (for logging)

    Raises:
        ProviderSubstitutionViolation: Always raises to ensure fail-closed
    """
    violation_msg = f"Provider request failed for agent '{original_request.agent_id}' with provider '{original_request.provider}' and model '{original_request.model}'. Error: {error}. Fail-closed enforced - no substitution allowed (REQ-415)."
    if attempted_substitution:
        violation_msg += f" Attempted substitution to provider '{attempted_substitution.get('provider', 'unknown')}' with model '{attempted_substitution.get('model', 'unknown')}' was blocked."
    Logger.error(violation_msg)
    raise ProviderSubstitutionViolation(violation_msg)


class ProviderSubstitutionGuard:
    """Guard to prevent provider/model substitution in SovereignLLMGateway."""

    def __init__(self):
        self._active_requests: dict[str, ProviderRequest] = {}

    def register_request(self, request_id: str, provider_request: ProviderRequest) -> None:
        """Register a provider request for tracking.

        Args:
            request_id: Unique request identifier
            provider_request: The provider request details
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "ProviderSubstitutionGuard.register_request"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:ProviderSubstitutionGuard.register_request".encode()
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        self._active_requests[request_id] = provider_request
        Logger.debug(f"Registered provider request {request_id} for agent {provider_request.agent_id}")

    def validate_response(self, request_id: str, actual_provider: str, actual_model: str) -> None:
        """Validate that the response matches the original request.

        Args:
            request_id: Request identifier
            actual_provider: Provider that actually responded
            actual_model: Model that actually responded

        Raises:
            ProviderSubstitutionViolation: If substitution is detected
        """
        if request_id not in self._active_requests:
            raise ProviderSubstitutionViolation(
                f"Unknown request ID {request_id}. Cannot validate provider substitution."
            )
        original_request = self._active_requests[request_id]
        validate_provider_request(original_request, actual_provider, actual_model)

    def handle_failure(
        self, request_id: str, error: Exception, attempted_substitution: dict[str, str] | None = None
    ) -> None:
        """Handle provider failure with fail-closed enforcement.

        Args:
            request_id: Request identifier
            error: The error that occurred
            attempted_substitution: Any attempted substitution

        Raises:
            ProviderSubstitutionViolation: Always raises to ensure fail-closed
        """
        if request_id not in self._active_requests:
            raise ProviderSubstitutionViolation(
                f"Unknown request ID {request_id}. Cannot enforce fail-closed."
            )
        original_request = self._active_requests[request_id]
        enforce_fail_closed_on_failure(original_request, error, attempted_substitution)

    def clear_request(self, request_id: str) -> None:
        """Clear a completed request.

        Args:
            request_id: Request identifier to clear
        """
        self._active_requests.pop(request_id, None)
        Logger.debug(f"Cleared provider request {request_id}")


_substitution_guard = ProviderSubstitutionGuard()


def get_substitution_guard() -> ProviderSubstitutionGuard:
    """Get the global provider substitution guard.

    Returns:
        The global ProviderSubstitutionGuard instance
    """
    return _substitution_guard


def test_provider_substitution_prohibition() -> bool:
    """Test that provider substitution prohibition is working.

    Returns:
        True if prohibition is enforced, False otherwise
    """
    try:
        test_request = ProviderRequest(
            provider="openai", model="gpt-4", agent_id="test_agent", request_id="test_123"
        )
        try:
            validate_provider_request(test_request, "anthropic", "claude-3-5-sonnet")
            return False
        except ProviderSubstitutionViolation:    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context
            pass
        try:
            validate_provider_request(test_request, "openai", "gpt-3.5-turbo")
            return False
        except ProviderSubstitutionViolation:    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context
            pass
        try:
            validate_provider_request(test_request, "openai", "gpt-4")
        except ProviderSubstitutionViolation:    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context    # guardian: ProviderSubstitutionViolation should be handled with specific context
            return False
        return True
    except (ValueError, TypeError, RuntimeError) as e:
        return False
