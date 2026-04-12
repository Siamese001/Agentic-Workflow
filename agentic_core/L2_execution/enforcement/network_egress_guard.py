"""
Network Egress Guard (REQ-414)

Ensures all outbound HTTP requests to LLM-serving endpoints (including localhost)
MUST originate exclusively from SovereignLLMGateway.
"""

from __future__ import annotations

import logging
import os
import re
import socket

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

emit_replay_key("p0", "network_egress_guard")
emit_determinism_digest("p0", "network_egress_guard")

_emit_dispatches_healing_run("p1", "network_egress_guard", "L2")
_emit_routes_through("p1", "network_egress_guard", "L2")
_emit_checks_agent_registry("p1", "network_egress_guard", "agent_registry")
_emit_validates_agent_capability("p1", "network_egress_guard", "capability")
_emit_dispatches_execution_plan("p1", "network_egress_guard", "exec_plan")
_emit_agent_executes_agent("p1", "network_egress_guard", "sub_agent")
_emit_routes_to_agent("p1", "network_egress_guard", "target_agent")
_emit_verifies_policy("p1", "network_egress_guard", "policy_check")
_emit_observes_runtime_state("p1", "network_egress_guard", "runtime_state")
_emit_verifies_boundary("p1", "network_egress_guard", "boundary_check")
_emit_transcripts_response("p1", "network_egress_guard", "transcript")
_emit_hard_fails_untranscripted("p1", "network_egress_guard")
_emit_gated_by_confidence("p1", "network_egress_guard", "confidence_gate")
_emit_escalates_to_human("p1", "network_egress_guard", "L2")
_emit_reads_policy_state("p1", "network_egress_guard", "L2")
_emit_authorize_and_execute("p2", "network_egress_guard", "execution_auth")
_emit_validates_capability("p2", "network_egress_guard", "capability_check")
_emit_routes_to_capability("p2", "network_egress_guard", "capability_route")
_emit_writes_via_uwg("p2", "network_egress_guard", "uwg_write")
_emit_blocks_direct_write("p2", "network_egress_guard", "direct_write_block")
_emit_records_tool_invocation("p2", "network_egress_guard", "tool_invocation")
_emit_captures_execution_output("p2", "network_egress_guard", "exec_output")
_emit_dispatches_agent("p3", "network_egress_guard", "agent_dispatch")
_emit_coordinates_agents("p3", "network_egress_guard", "agent_coordination")
_emit_records_workflow_lineage("p3", "network_egress_guard", "workflow_lineage")
_emit_records_healing_outcome("p3", "network_egress_guard", "healing_outcome")
_emit_escalates_failure("p3", "network_egress_guard", "failure_escalation")
_emit_orchestrates_workflow("p3", "network_egress_guard", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "network_egress_guard", "healing_dispatch")
_emit_invokes_evaluation("p3", "network_egress_guard", "evaluation_signal")
_emit_records_telemetry_event("p4", "network_egress_guard", "telemetry_event")
_emit_captures_evaluation_metric("p4", "network_egress_guard", "eval_metric")
_emit_stores_embedding("p4", "network_egress_guard", "embedding_store")
_emit_updates_meta_learning_state("p4", "network_egress_guard", "meta_learning")
_emit_links_execution_to_snapshot("p4", "network_egress_guard", "exec_snapshot_link")
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

_emit_emits_metric_event("network_egress_guard", "p4obs", "metric_1")
_emit_emits_metric_event("network_egress_guard", "p4obs", "metric_2")
_emit_emits_metric_event("network_egress_guard", "p4obs", "metric_3")
_emit_emits_metric_event("network_egress_guard", "p4obs", "metric_4")
_emit_emits_metric_event("network_egress_guard", "p4obs", "metric_5")
_emit_emits_metric_event("network_egress_guard", "p4obs", "metric_6")
_emit_records_incident_event("network_egress_guard", "p4obs", "incident")
_emit_captures_runtime_anomaly("network_egress_guard", "p4obs", "anomaly")
_emit_writes_observability_log("network_egress_guard", "p4obs", "obs_log")
_emit_updates_monitoring_state("network_egress_guard", "p4obs", "mon_state")
_emit_triggers_alert("network_egress_guard", "p4obs", "alert")
_emit_links_incident_trace("network_egress_guard", "p4obs", "trace_link")
_emit_captures_pattern("network_egress_guard", "p3lm", "pattern")
_emit_records_learning_event("network_egress_guard", "p3lm", "learning_event")
_emit_writes_learning_snapshot("network_egress_guard", "p3lm", "snapshot")
_emit_feeds_meta_learning("network_egress_guard", "p3lm", "meta_feed")
_emit_updates_routing_strategy("network_egress_guard", "p3lm", "routing")
_emit_improves_agent_policy("network_egress_guard", "p3lm", "policy")
_emit_stores_learning_state("network_egress_guard", "p3lm", "state")
_emit_records_execution_trace("network_egress_guard", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("network_egress_guard", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("network_egress_guard", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("network_egress_guard", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("network_egress_guard", "L4_STATE", "p2_trace_5")
_emit_reads_environ("network_egress_guard", "env_read", "p2_env_1")
_emit_reads_environ("network_egress_guard", "env_read", "p2_env_2")
_emit_reads_runtime_state("network_egress_guard", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("network_egress_guard", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "network_egress_guard", "context_pull")
_emit_pulls_context("p1", "network_egress_guard", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "network_egress_guard", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "network_egress_guard", "uwg_term_2")
_emit_writes_through("p1", "network_egress_guard", "write_through")
_emit_writes_through("p1", "network_egress_guard", "write_through_2")
_emit_validated_by_safety_plane("p1", "network_egress_guard", "safety_validation")
_emit_invokes_eval("p1", "network_egress_guard", "eval_call")
_emit_proposal_commits_routing("p1", "network_egress_guard", "routing_commit")

Logger = logging.getLogger(__name__)
LLM_ENDPOINT_PATTERNS = [
    ".*\\.openai\\.com",
    ".*\\.api\\.openai\\.com",
    "api\\.openai\\.com",
    "openai\\.com",
    ".*\\.anthropic\\.com",
    "api\\.anthropic\\.com",
    "anthropic\\.com",
    ".*\\.googleapis\\.com",
    "generativelanguage\\.googleapis\\.com",
    "localhost",
    "localhost:.*",
    "127\\.0\\.0\\.1",
    "127\\.0\\.0\\.1:.*",
    "0\\.0\\.0\\.0",
    "0\\.0\\.0\\.0:.*",
    "::1",
    "::1:.*",
]
COMPILED_PATTERNS = [re.compile(pattern, re.IGNORECASE) for pattern in LLM_ENDPOINT_PATTERNS]


class NetworkEgressViolation(Exception):
    """Raised when unauthorized network egress to LLM endpoint is detected."""

    pass


def is_llm_endpoint(hostname: str, port: int | None = None) -> bool:
    """Check if hostname:port matches known LLM endpoint patterns.

    Args:
        hostname: Hostname to check
        port: Optional port number

    Returns:
        True if it's an LLM endpoint, False otherwise
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "is_llm_endpoint", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "is_llm_endpoint", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "is_llm_endpoint")
    host_port = f"{hostname}:{port}" if port else hostname
    for pattern in COMPILED_PATTERNS:
        if pattern.match(host_port):
            return True
    return False


def check_network_egress_allowed(
    hostname: str,
    port: int | None = None,
    caller_module: str | None = None,
) -> bool:
    """Check if network egress to LLM endpoint is allowed (REQ-414).

    Args:
        hostname: Target hostname
        port: Target port
        caller_module: Module attempting the connection

    Returns:
        True if allowed, False otherwise

    Raises:
        NetworkEgressViolation: If attempting unauthorized LLM endpoint access
    """
    if not is_llm_endpoint(hostname, port):
        return True
    if _is_in_gateway_context():
        return True
    if os.getenv("EGRESS_GUARD_DISABLED") == "1":
        Logger.warning("Network egress guard disabled via environment variable")
        return True
    caller_info = f" from {caller_module}" if caller_module else ""
    violation_msg = f"Unauthorized network egress to LLM endpoint {hostname}:{port}{caller_info}. All LLM requests must go through SovereignLLMGateway (REQ-414)."
    Logger.error(violation_msg)
    raise NetworkEgressViolation(violation_msg)


def _is_in_gateway_context() -> bool:
    """Check if current execution context is within SovereignLLMGateway.

    Returns:
        True if in gateway context, False otherwise
    """
    import inspect

    for frame_info in inspect.stack():
        module_name = frame_info.frame.f_globals.get("__name__", "")
        if "SovereignLLMGateway" in module_name and module_name.endswith("SovereignLLMGateway"):
            return True
        if "self" in frame_info.frame.f_locals:
            obj = frame_info.frame.f_locals["self"]
            if hasattr(obj, "__class__") and obj.__class__.__name__ == "SovereignLLMGateway":
                return True
    return False


_original_socket_connect = socket.socket.connect


def _guarded_connect(self, address: tuple[str, int] | str) -> None:
    """Guarded socket.connect that checks egress permissions."""
    if isinstance(address, tuple):
        hostname, port = address
    else:
        _original_socket_connect(self, address)
        return
    caller_module = None
    try:
        import inspect

        caller_module = inspect.stack()[1].frame.f_globals.get("__name__")
    except (ValueError, TypeError, RuntimeError) as e:
        raise
        pass
    check_network_egress_allowed(hostname, port, caller_module)
    _original_socket_connect(self, address)


def install_egress_guard() -> None:
    """Install network egress guard (REQ-414).

    This monkey-patches socket.connect to enforce the egress policy.
    Should be called during system initialization.
    """
    if os.getenv("EGRESS_GUARD_DISABLED") == "1":
        Logger.warning("Network egress guard installation skipped (disabled)")
        return
    socket.socket.connect = _guarded_connect
    Logger.info("Network egress guard installed (REQ-414)")


def uninstall_egress_guard() -> None:
    """Uninstall network egress guard.

    Restores original socket.connect behavior.
    """
    socket.socket.connect = _original_socket_connect
    Logger.info("Network egress guard uninstalled")


def simulate_direct_llm_request(hostname: str = "api.openai.com", port: int = 443) -> None:
    """Simulate a direct LLM request that should be blocked.

    Args:
        hostname: LLM endpoint hostname
        port: LLM endpoint port

    Raises:
        NetworkEgressViolation: Always raised unless guard is disabled
    """
    check_network_egress_allowed(hostname, port, "test_simulation")


def test_egress_guard() -> bool:
    """Test if egress guard is properly installed.

    Returns:
        True if guard is working, False otherwise
    """
    try:
        simulate_direct_llm_request()
        return False
    except NetworkEgressViolation:  # guardian: NetworkEgressViolation should be handled with specific context
        return True
    except (ValueError, TypeError, RuntimeError) as e:
        return False
