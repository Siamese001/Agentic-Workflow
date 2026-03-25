"""RG-GAP-04 invariant tests.

RG-GAP-04: AgentExecutor._execute_internal must route through SovereignLLMGateway
  BEFORE falling back to direct SDK clients.
  Negative control: when gateway is available, direct SDK must NOT be called.
"""

from __future__ import annotations

import sys
import types
from unittest.mock import MagicMock, patch

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_agent_executor_gateway")
# REMOVED: _emit_applies_guardrail("p0", "test_agent_executor_gateway", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_agent_executor_gateway", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_agent_executor_gateway", "state_snapshot")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_emits_metric_event("test_agent_executor_gateway", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_agent_executor_gateway", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_agent_executor_gateway", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_agent_executor_gateway", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_agent_executor_gateway", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_agent_executor_gateway", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_agent_executor_gateway", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_agent_executor_gateway", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_agent_executor_gateway", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_agent_executor_gateway", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_agent_executor_gateway", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_agent_executor_gateway", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_agent_executor_gateway", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_agent_executor_gateway", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_agent_executor_gateway", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_agent_executor_gateway", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_agent_executor_gateway", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_agent_executor_gateway", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_agent_executor_gateway", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_agent_executor_gateway", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_agent_executor_gateway", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_agent_executor_gateway", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_agent_executor_gateway", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_agent_executor_gateway", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_agent_executor_gateway", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_agent_executor_gateway", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_agent_executor_gateway", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_agent_executor_gateway", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_agent_executor_gateway", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_agent_executor_gateway", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_agent_executor_gateway", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_agent_executor_gateway", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_agent_executor_gateway", "write_through")
# REMOVED: _emit_writes_through("p1", "test_agent_executor_gateway", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_agent_executor_gateway", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_agent_executor_gateway", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_agent_executor_gateway", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_agent_executor_gateway", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_agent_executor_gateway", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_agent_executor_gateway", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_agent_executor_gateway", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_agent_executor_gateway", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_agent_executor_gateway", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_agent_executor_gateway", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_agent_executor_gateway", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_agent_executor_gateway", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_agent_executor_gateway", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_agent_executor_gateway", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_agent_executor_gateway")
# REMOVED: _emit_gated_by_confidence("p1", "test_agent_executor_gateway", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_agent_executor_gateway")
# REMOVED: emit_determinism_digest("p0", "test_agent_executor_gateway")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_agent_executor_gateway", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_agent_executor_gateway", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_agent_executor_gateway", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_agent_executor_gateway", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_agent_executor_gateway", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_agent_executor_gateway", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_agent_executor_gateway", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_agent_executor_gateway", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_agent_executor_gateway", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_agent_executor_gateway", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_agent_executor_gateway", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_agent_executor_gateway", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_agent_executor_gateway", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_agent_executor_gateway", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_agent_executor_gateway", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_agent_executor_gateway", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_agent_executor_gateway", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_agent_executor_gateway", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_agent_executor_gateway", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_agent_executor_gateway", "exec_snapshot_link")


def _stub_apps_shared():
    """Stub apps_shared.utils.* modules for AgentExecutor import."""
    from enum import Enum

    class Provider(str, Enum):
        OPENAI = "openai"
        ANTHROPIC = "anthropic"
        GOOGLE = "google"

    provider_mod = types.ModuleType("apps_shared.utils.Provider")
    provider_mod.Provider = Provider
    provider_mod.get_client = MagicMock(return_value=MagicMock())
    provider_mod.get_instructor_client = MagicMock(return_value=MagicMock())
    provider_mod.get_litellm_completion = MagicMock()
    provider_mod.get_default_model = MagicMock(return_value="gpt-4")

    obs_mod = types.ModuleType("apps_shared.utils.observability_clients")
    obs_mod.create_span = MagicMock()
    obs_mod.record_exception = MagicMock()
    obs_mod.set_span_attribute = MagicMock()

    # create_span returns a context manager
    import contextlib

    obs_mod.create_span = MagicMock(return_value=contextlib.nullcontext())

    apps_shared = sys.modules.get("apps_shared") or types.ModuleType("apps_shared")
    apps_shared_utils = sys.modules.get("apps_shared.utils") or types.ModuleType("apps_shared.utils")

    sys.modules.setdefault("apps_shared", apps_shared)
    sys.modules.setdefault("apps_shared.utils", apps_shared_utils)
    sys.modules["apps_shared.utils.Provider"] = provider_mod
    sys.modules["apps_shared.utils.observability_clients"] = obs_mod

    return Provider, provider_mod, obs_mod


def _build_gateway_stub(response_text: str = "gateway response") -> tuple:
    """Build a mock SovereignLLMGateway + GenerationRequest."""
    mock_resp = MagicMock()
    mock_resp.text = response_text

    mock_gateway = MagicMock()
    mock_gateway.generate.return_value = mock_resp

    mock_gateway_cls = MagicMock(return_value=mock_gateway)

    mock_request_cls = MagicMock(side_effect=lambda **kw: MagicMock(**kw))

    gateway_mod = types.ModuleType("agentic_core.interfaces.gateway")
    gateway_mod.SovereignLLMGateway = mock_gateway_cls
    gateway_mod.GenerationRequest = mock_request_cls

    return gateway_mod, mock_gateway_cls, mock_gateway, mock_resp


class TestAgentExecutorGatewayRouting:
    def setup_method(self):
        """Ensure clean module state for each test."""
        sys.modules.pop("apps_rg.utils.agent_executor_util", None)
        self.Provider, self.provider_mod, self.obs_mod = _stub_apps_shared()

    def test_execute_internal_calls_gateway_first(self):
        """RG-GAP-04 positive: _execute_internal routes through SovereignLLMGateway."""
        gateway_mod, mock_gateway_cls, mock_gateway, mock_resp = _build_gateway_stub("from gateway")

        with patch.dict("sys.modules", {"agentic_core.interfaces.gateway": gateway_mod}):
            from apps_rg.utils.agent_executor_util import AgentConfig, AgentExecutor, AgentMessage

            config = AgentConfig(provider=self.Provider.OPENAI, model="gpt-4", enable_tracing=False)
            executor = AgentExecutor(config)

            result = executor.execute(
                messages=[AgentMessage(role="user", content="hello")],
                system_prompt=None,
            )

        assert result.content == "from gateway"
        mock_gateway_cls.assert_called_once()
        mock_gateway.generate.assert_called_once()

    def test_execute_internal_does_not_call_direct_sdk_when_gateway_available(self):
    """Test execute_internal_does_not_call_direct_sdk_when_gateway_available runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute execute_internal_does_not_call_direct_sdk_when_gateway_available
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    # TODO: Add specific execution assertions
                )

        mock_sdk.assert_not_called(), "Direct SDK must not be called when gateway is available"

    def test_execute_google_routes_via_gateway(self):
        """RG-GAP-04: Provider.GOOGLE must also route through gateway, not legacy SDK."""
        gateway_mod, mock_gateway_cls, mock_gateway, _ = _build_gateway_stub("gemini via gateway")

        with patch.dict("sys.modules", {"agentic_core.interfaces.gateway": gateway_mod}):
            from apps_rg.utils.agent_executor_util import AgentConfig, AgentExecutor, AgentMessage

            config = AgentConfig(provider=self.Provider.GOOGLE, model="gemini-2.5-pro", enable_tracing=False)
            executor = AgentExecutor(config)

            with patch.object(executor, "_execute_google_legacy") as mock_legacy:
                result = executor.execute(
                    messages=[AgentMessage(role="user", content="hello")],
                    system_prompt=None,
                )

        assert result.content == "gemini via gateway"
        mock_legacy.assert_not_called(), "Legacy Google SDK must not be called when gateway is available"

    def test_fallback_to_sdk_when_gateway_import_fails(self):
        """RG-GAP-04: When gateway is unavailable (ImportError), fallback to direct SDK."""
        # Simulate gateway not installed
        sys.modules.pop("agentic_core.interfaces.gateway", None)
        broken_gateway = types.ModuleType("agentic_core.interfaces.gateway")
        broken_gateway.SovereignLLMGateway = None
        broken_gateway.GenerationRequest = None

        with patch.dict("sys.modules", {"agentic_core.interfaces.gateway": None}):
            from apps_rg.utils.agent_executor_util import AgentConfig, AgentExecutor, AgentMessage

            config = AgentConfig(provider=self.Provider.OPENAI, model="gpt-4", enable_tracing=False)
            executor = AgentExecutor(config)

            # Patch _execute_openai to avoid real SDK calls
            mock_resp = MagicMock()
            mock_resp.content = "sdk fallback"
            mock_resp.finish_reason = "stop"

            with patch.object(executor, "_execute_openai", return_value=mock_resp) as mock_sdk:
                result = executor._execute_internal(
                    messages=[AgentMessage(role="user", content="hello")],
                    system_prompt=None,
                    tools=None,
                )

        mock_sdk.assert_called_once()

    def test_try_execute_via_gateway_returns_none_on_import_error(self):
        """RG-GAP-04: _try_execute_via_gateway returns None when gateway cannot be imported."""
        with patch.dict("sys.modules", {"agentic_core.interfaces.gateway": None}):
            from apps_rg.utils.agent_executor_util import AgentConfig, AgentExecutor

            config = AgentConfig(provider=self.Provider.OPENAI, enable_tracing=False)
            executor = AgentExecutor(config)

            result = executor._try_execute_via_gateway(
                formatted_messages=[{"role": "user", "content": "test"}],
                model="gpt-4",
                system_prompt=None,
                tools=None,
            )

        assert result is None, "_try_execute_via_gateway must return None when gateway unavailable"

    def test_try_execute_via_gateway_source_contains_gateway_import(self):
    """Test try_execute_via_gateway_source_contains_gateway_import runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute try_execute_via_gateway_source_contains_gateway_import
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    # TODO: Add specific execution assertions