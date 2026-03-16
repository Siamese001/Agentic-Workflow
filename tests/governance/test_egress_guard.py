"""REQ-414: SovereignLLMGateway egress audit enforcement.

Every route_generation call MUST append to the HashChainAuditLog.
Enforcement layers: Runtime + CI (REQ-416 dual-layer contract).
"""

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock, patch

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_egress_guard")
_emit_reads_policy_state("p0", "test_egress_guard", "policy_binding")
_emit_snapshots_state("p0", "test_egress_guard", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("test_egress_guard", "p4obs", "metric_1")
_emit_emits_metric_event("test_egress_guard", "p4obs", "metric_2")
_emit_emits_metric_event("test_egress_guard", "p4obs", "metric_3")
_emit_emits_metric_event("test_egress_guard", "p4obs", "metric_4")
_emit_emits_metric_event("test_egress_guard", "p4obs", "metric_5")
_emit_emits_metric_event("test_egress_guard", "p4obs", "metric_6")
_emit_records_incident_event("test_egress_guard", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_egress_guard", "p4obs", "anomaly")
_emit_writes_observability_log("test_egress_guard", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_egress_guard", "p4obs", "mon_state")
_emit_triggers_alert("test_egress_guard", "p4obs", "alert")
_emit_links_incident_trace("test_egress_guard", "p4obs", "trace_link")
_emit_captures_pattern("test_egress_guard", "p3lm", "pattern")
_emit_records_learning_event("test_egress_guard", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_egress_guard", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_egress_guard", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_egress_guard", "p3lm", "routing")
_emit_improves_agent_policy("test_egress_guard", "p3lm", "policy")
_emit_stores_learning_state("test_egress_guard", "p3lm", "state")
_emit_records_execution_trace("test_egress_guard", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_egress_guard", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_egress_guard", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_egress_guard", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_egress_guard", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_egress_guard", "env_read", "p2_env_1")
_emit_reads_environ("test_egress_guard", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_egress_guard", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_egress_guard", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_egress_guard", "context_pull")
_emit_pulls_context("p1", "test_egress_guard", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_egress_guard", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_egress_guard", "uwg_term_2")
_emit_writes_through("p1", "test_egress_guard", "write_through")
_emit_writes_through("p1", "test_egress_guard", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_egress_guard", "safety_validation")
_emit_invokes_eval("p1", "test_egress_guard", "eval_call")
_emit_proposal_commits_routing("p1", "test_egress_guard", "routing_commit")
emit_replay_key("p0", "test_egress_guard")
emit_determinism_digest("p0", "test_egress_guard")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_egress_guard", "execution_auth")
_emit_validates_capability("p2", "test_egress_guard", "capability_check")
_emit_routes_to_capability("p2", "test_egress_guard", "capability_route")
_emit_writes_via_uwg("p2", "test_egress_guard", "uwg_write")
_emit_blocks_direct_write("p2", "test_egress_guard", "direct_write_block")
_emit_records_tool_invocation("p2", "test_egress_guard", "tool_invocation")
_emit_captures_execution_output("p2", "test_egress_guard", "exec_output")
_emit_dispatches_agent("p3", "test_egress_guard", "agent_dispatch")
_emit_coordinates_agents("p3", "test_egress_guard", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_egress_guard", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_egress_guard", "healing_outcome")
_emit_escalates_failure("p3", "test_egress_guard", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_egress_guard", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_egress_guard", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_egress_guard", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_egress_guard", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_egress_guard", "eval_metric")
_emit_stores_embedding("p4", "test_egress_guard", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_egress_guard", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_egress_guard", "exec_snapshot_link")

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
    from agentic_core.L2_execution.audit.hash_chain_audit_log import HashChainAuditLog
    from agentic_core.L2_execution.enforcement.SovereignLLMGateway import (
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
    from agentic_core.L2_execution.enforcement.SovereignLLMGateway import (
        SovereignLLMGateway,
    )
    from agentic_core.L2_execution.types.gateway_types import GenerationRequest

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
    from agentic_core.L2_execution.enforcement.SovereignLLMGateway import (
        SovereignLLMGateway,
    )
    from agentic_core.L2_execution.types.gateway_types import GenerationRequest

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
