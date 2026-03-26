"""REQ-414: SovereignLLMGateway egress audit enforcement.

Every route_generation call MUST append to the HashChainAuditLog.
Enforcement layers: Runtime + CI (REQ-416 dual-layer contract).
"""

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock, patch

import pytest

#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_egress_guard")
# REMOVED: _emit_reads_policy_state("p0", "test_egress_guard", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_egress_guard", "state_snapshot")
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
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
    _emit_writes_through,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_egress_guard", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_egress_guard", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_egress_guard", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_egress_guard", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_egress_guard", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_egress_guard", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_egress_guard", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_egress_guard", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_egress_guard", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_egress_guard", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_egress_guard", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_egress_guard", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_egress_guard", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_egress_guard", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_egress_guard", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_egress_guard", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_egress_guard", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_egress_guard", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_egress_guard", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_egress_guard", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_egress_guard", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_egress_guard", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_egress_guard", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_egress_guard", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_egress_guard", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_egress_guard", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_egress_guard", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_egress_guard", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_egress_guard", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_egress_guard", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_egress_guard", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_egress_guard", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_egress_guard", "write_through")
# REMOVED: _emit_writes_through("p1", "test_egress_guard", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_egress_guard", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_egress_guard", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_egress_guard", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_egress_guard", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_egress_guard", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_egress_guard", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_egress_guard", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_egress_guard", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_egress_guard", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_egress_guard", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_egress_guard", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_egress_guard", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_egress_guard", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_egress_guard", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_egress_guard")
# REMOVED: _emit_gated_by_confidence("p1", "test_egress_guard", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_egress_guard")
# REMOVED: emit_determinism_digest("p0", "test_egress_guard")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_egress_guard", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_egress_guard", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_egress_guard", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_egress_guard", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_egress_guard", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_egress_guard", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_egress_guard", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_egress_guard", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_egress_guard", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_egress_guard", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_egress_guard", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_egress_guard", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_egress_guard", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_egress_guard", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_egress_guard", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_egress_guard", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_egress_guard", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_egress_guard", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_egress_guard", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_egress_guard", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.governance


def test_gateway_has_egress_audit_log():
    """Gateway must expose a HashChainAuditLog as _egress_audit_log."""
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
        from agentic_core.L2_execution.audit.hash_chain_audit_log import HashChainAuditLog
        from agentic_core.L2_execution.enforcement.SovereignLLMGateway import (
        from agentic_core.L2_execution.enforcement.SovereignLLMGateway import (
        from agentic_core.L2_execution.types.gateway_types import GenerationRequest
        from agentic_core.L2_execution.enforcement.SovereignLLMGateway import (
        from agentic_core.L2_execution.types.gateway_types import GenerationRequest
        """Gateway must expose a HashChainAuditLog as _egress_audit_log."""

#  # MOVED: from agentic_core.L2_execution.audit.hash_chain_audit_log import HashChainAuditLog
#  # MOVED: from agentic_core.L2_execution.enforcement.SovereignLLMGateway import (
        SovereignLLMGateway,
    )

    SovereignLLMGateway.reset_instance()
    gw = SovereignLLMGateway()
    assert hasattr(gw, "_egress_audit_log"), "Gateway missing _egress_audit_log"
    assert isinstance(gw._egress_audit_log, HashChainAuditLog), (
        "Gateway._egress_audit_log must be a HashChainAuditLog instance"
    )
    SovereignLLMGateway.reset_instance()


def test_route_generation_writes_egress_audit():
    """route_generation must append to the egress audit log on each call."""
#  # MOVED: from agentic_core.L2_execution.enforcement.SovereignLLMGateway import (
        SovereignLLMGateway,
    )
#  # MOVED: from agentic_core.L2_execution.types.gateway_types import GenerationRequest

    SovereignLLMGateway.reset_instance()
    gw = SovereignLLMGateway()

    req = GenerationRequest(
        agent_id="test_egress_agent",
        provider="openai",
        model="gpt-4o",
        prompt="test egress audit",
    )

    mock_profile = MagicMock()
    mock_profile.execution_mode.value = "LLM_API"
    mock_profile.allowed_models = {"gpt-4o"}
    mock_profile.allowed_providers = {"openai"}
    mock_profile.reasoning_intensity.value = "HIGH"

    sentinel = object()
    mock_em = MagicMock()
    mock_em.DETERMINISTIC = sentinel  # distinct from mock_profile.execution_mode

    with (
        patch(
            "agentic_core.L2_execution.enforcement.SovereignLLMGateway.get_profile",
            return_value=mock_profile,
        ),
        patch(
            "agentic_core.L2_execution.enforcement.SovereignLLMGateway.ExecutionMode",
            mock_em,
        ),
        patch.object(
            gw,
            "_call_provider",
            return_value={"content": "ok", "tokens": 1},
        ),
        patch.object(gw._egress_audit_log, "append") as mock_append,
    ):
        asyncio.run(gw.route_generation(req))
        assert mock_append.called, "Egress audit log.append must be called by route_generation"

    SovereignLLMGateway.reset_instance()


def test_route_generation_egress_payload_contains_agent_id():
    """Egress audit payload must include agent_id and provider."""
#  # MOVED: from agentic_core.L2_execution.enforcement.SovereignLLMGateway import (
        SovereignLLMGateway,
    )
#  # MOVED: from agentic_core.L2_execution.types.gateway_types import GenerationRequest

    SovereignLLMGateway.reset_instance()
    gw = SovereignLLMGateway()

    req = GenerationRequest(
        agent_id="test_payload_agent",
        provider="openai",
        model="gpt-4o",
        prompt="payload check",
    )

    mock_profile = MagicMock()
    mock_profile.execution_mode.value = "LLM_API"
    mock_profile.allowed_models = {"gpt-4o"}
    mock_profile.allowed_providers = {"openai"}
    mock_profile.reasoning_intensity.value = "HIGH"

    sentinel = object()
    mock_em = MagicMock()
    mock_em.DETERMINISTIC = sentinel

    captured: list[dict] = []

    def _capture(**kwargs):
        captured.append(kwargs)

    with (
        patch(
            "agentic_core.L2_execution.enforcement.SovereignLLMGateway.get_profile",
            return_value=mock_profile,
        ),
        patch(
            "agentic_core.L2_execution.enforcement.SovereignLLMGateway.ExecutionMode",
            mock_em,
        ),
        patch.object(
            gw,
            "_call_provider",
            return_value={"content": "ok", "tokens": 1},
        ),
        patch.object(gw._egress_audit_log, "append", side_effect=_capture),
    ):
        asyncio.run(gw.route_generation(req))

    assert len(captured) >= 1, "Egress audit log must be written at least once"
    payload = captured[0].get("payload", {})
    assert payload.get("agent_id") == "test_payload_agent", "Egress audit payload must contain agent_id"
    assert "provider" in payload, "Egress audit payload must contain provider"

    SovereignLLMGateway.reset_instance()
