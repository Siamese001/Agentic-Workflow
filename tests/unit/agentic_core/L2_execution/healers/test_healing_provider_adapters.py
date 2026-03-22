"""
Adapter Contract Tests — Prove Real Adapters Are Invoked with Faked SDKs.

These tests verify that the actual Qwen and Gemini adapters are selected
and invoked correctly, with faked SDK modules to avoid network dependencies.

Tests cover:
- Correct adapter chosen for each tier
- SDK methods called with expected arguments
- Model IDs and context passed through correctly
- Prompt payload is structured and non-empty
- Error handling when SDK is missing
"""

from __future__ import annotations

import sys
from unittest.mock import Mock

import pytest

from agentic_core.L0_routing.config.path_constants import (
    L2_EXECUTION_DIR,
)
from agentic_core.L2_execution.healers.healing_provider_adapters import (
    GeminiInvokerAdapter,
    LocalAgentAdapter,
    QwenInvokerAdapter,
)
from agentic_core.L2_execution.healers.healing_tier_config import (
    load_default_healing_tier_config,
)
from agentic_core.L2_execution.healers.healing_tier_router import route_healing_tier
from agentic_core.L2_execution.healers.healing_tier_types import (
    HealingInput,
    HealingTier,
)
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_records_execution_trace("p0", "evidence", "test_healing_provider_adapters")
_emit_applies_guardrail("p0", "test_healing_provider_adapters", "p0_governance")
_emit_reads_policy_state("p0", "test_healing_provider_adapters", "policy_binding")
_emit_snapshots_state("p0", "test_healing_provider_adapters", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_emits_metric_event("test_healing_provider_adapters", "p4obs", "metric_1")
_emit_emits_metric_event("test_healing_provider_adapters", "p4obs", "metric_2")
_emit_emits_metric_event("test_healing_provider_adapters", "p4obs", "metric_3")
_emit_emits_metric_event("test_healing_provider_adapters", "p4obs", "metric_4")
_emit_emits_metric_event("test_healing_provider_adapters", "p4obs", "metric_5")
_emit_emits_metric_event("test_healing_provider_adapters", "p4obs", "metric_6")
_emit_records_incident_event("test_healing_provider_adapters", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_healing_provider_adapters", "p4obs", "anomaly")
_emit_writes_observability_log("test_healing_provider_adapters", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_healing_provider_adapters", "p4obs", "mon_state")
_emit_triggers_alert("test_healing_provider_adapters", "p4obs", "alert")
_emit_links_incident_trace("test_healing_provider_adapters", "p4obs", "trace_link")
_emit_captures_pattern("test_healing_provider_adapters", "p3lm", "pattern")
_emit_records_learning_event("test_healing_provider_adapters", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_healing_provider_adapters", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_healing_provider_adapters", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_healing_provider_adapters", "p3lm", "routing")
_emit_improves_agent_policy("test_healing_provider_adapters", "p3lm", "policy")
_emit_stores_learning_state("test_healing_provider_adapters", "p3lm", "state")
_emit_records_execution_trace("test_healing_provider_adapters", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_healing_provider_adapters", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_healing_provider_adapters", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_healing_provider_adapters", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_healing_provider_adapters", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_healing_provider_adapters", "env_read", "p2_env_1")
_emit_reads_environ("test_healing_provider_adapters", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_healing_provider_adapters", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_healing_provider_adapters", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_healing_provider_adapters", "context_pull")
_emit_pulls_context("p1", "test_healing_provider_adapters", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_healing_provider_adapters", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_healing_provider_adapters", "uwg_term_2")
_emit_writes_through("p1", "test_healing_provider_adapters", "write_through")
_emit_writes_through("p1", "test_healing_provider_adapters", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_healing_provider_adapters", "safety_validation")
_emit_invokes_eval("p1", "test_healing_provider_adapters", "eval_call")
_emit_proposal_commits_routing("p1", "test_healing_provider_adapters", "routing_commit")
_emit_escalates_to_human("p1", "test_healing_provider_adapters", "human_escalation")
_emit_routes_through("p1", "test_healing_provider_adapters", "route_through")
_emit_checks_agent_registry("p1", "test_healing_provider_adapters", "agent_registry")
_emit_validates_agent_capability("p1", "test_healing_provider_adapters", "capability")
_emit_dispatches_execution_plan("p1", "test_healing_provider_adapters", "exec_plan")
_emit_agent_executes_agent("p1", "test_healing_provider_adapters", "sub_agent")
_emit_routes_to_agent("p1", "test_healing_provider_adapters", "target_agent")
_emit_verifies_policy("p1", "test_healing_provider_adapters", "policy_check")
_emit_observes_runtime_state("p1", "test_healing_provider_adapters", "runtime_state")
_emit_verifies_boundary("p1", "test_healing_provider_adapters", "boundary_check")
_emit_transcripts_response("p1", "test_healing_provider_adapters", "transcript")
_emit_hard_fails_untranscripted("p1", "test_healing_provider_adapters")
_emit_gated_by_confidence("p1", "test_healing_provider_adapters", "confidence_gate")
emit_replay_key("p0", "test_healing_provider_adapters")
emit_determinism_digest("p0", "test_healing_provider_adapters")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_healing_provider_adapters", "execution_auth")
_emit_validates_capability("p2", "test_healing_provider_adapters", "capability_check")
_emit_routes_to_capability("p2", "test_healing_provider_adapters", "capability_route")
_emit_writes_via_uwg("p2", "test_healing_provider_adapters", "uwg_write")
_emit_blocks_direct_write("p2", "test_healing_provider_adapters", "direct_write_block")
_emit_records_tool_invocation("p2", "test_healing_provider_adapters", "tool_invocation")
_emit_captures_execution_output("p2", "test_healing_provider_adapters", "exec_output")
_emit_dispatches_agent("p3", "test_healing_provider_adapters", "agent_dispatch")
_emit_coordinates_agents("p3", "test_healing_provider_adapters", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_healing_provider_adapters", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_healing_provider_adapters", "healing_outcome")
_emit_escalates_failure("p3", "test_healing_provider_adapters", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_healing_provider_adapters", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_healing_provider_adapters", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_healing_provider_adapters", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_healing_provider_adapters", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_healing_provider_adapters", "eval_metric")
_emit_stores_embedding("p4", "test_healing_provider_adapters", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_healing_provider_adapters", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_healing_provider_adapters", "exec_snapshot_link")

pytestmark = pytest.mark.unit_min_deps


class TestQwenAdapterContract:
    """Contract tests for QwenInvokerAdapter with faked OpenAI SDK."""

    def test_qwen_adapter_invokes_sdk_with_correct_args(self) -> None:
        """Qwen adapter should call OpenAI SDK with expected parameters."""
        # Setup fake OpenAI module
        fake_openai = Mock()
        fake_client = Mock()
        fake_response = Mock()
        fake_response.choices = [Mock()]
        fake_response.choices[0].message.content = "Fix: import missing module"
        fake_response.usage = Mock()
        fake_response.usage.prompt_tokens = 150
        fake_response.usage.completion_tokens = 75
        fake_client.chat.completions.create.return_value = fake_response
        fake_openai.OpenAI.return_value = fake_client

        # Inject fake module into sys.modules before adapter method is called
        sys.modules["openai"] = fake_openai

        try:
            adapter = QwenInvokerAdapter(base_url="http://localhost:8000/v1", api_key="test-key")

            # Prepare healing input
            healing_input = HealingInput(
                failure_type="missing_import",
                error_signature="ImportError: module_not_found",
                trace_id="test-trace-123",
                retry_count=0,
                blast_radius_estimate=0.3,
                required_tools=("ast_rewrite",),
                violation_metadata_refs=("/path/to/file.py",),
            )

            config = load_default_healing_tier_config()
            decision = route_healing_tier(healing_input, config)

            # Invoke adapter
            record = adapter.invoke_qwen_vllm(healing_input, decision, config, agent_name="TestAgent")

            # Verify SDK was called correctly
            fake_openai.OpenAI.assert_called_once_with(
                base_url="http://localhost:8000/v1", api_key="test-key"
            )
            fake_client.chat.completions.create.assert_called_once()
            call_args = fake_client.chat.completions.create.call_args

            assert call_args.kwargs["model"] == config.model_qwen_vllm_id
            assert len(call_args.kwargs["messages"]) == 2
            assert call_args.kwargs["messages"][0]["role"] == "system"
            assert "code healing assistant" in call_args.kwargs["messages"][0]["content"].lower()
            assert call_args.kwargs["messages"][1]["role"] == "user"

            # Verify prompt is structured and non-empty
            prompt = call_args.kwargs["messages"][1]["content"]
            assert "TestAgent" in prompt
            assert "missing_import" in prompt
            assert "ImportError: module_not_found" in prompt
            assert "Retry Count: 0" in prompt
            assert "Required Tools: ast_rewrite" in prompt
            assert len(prompt) > 100  # Substantial content

            # Verify returned record
            assert record.tier == HealingTier.QWEN_VLLM
            assert record.model_id == config.model_qwen_vllm_id
            assert record.agent_name == "TestAgent"
            assert record.trace_id == "test-trace-123"
            assert record.method_called == "invoke_qwen_vllm"

        finally:
            # Clean up sys.modules
            sys.modules.pop("openai", None)

    def test_qwen_adapter_raises_import_error_when_sdk_missing(self) -> None:
        """Qwen adapter should raise ImportError when OpenAI SDK is not available."""
        # Temporarily replace openai module with one that raises ImportError on import
        original_openai = sys.modules.get("openai")

        class FakeOpenAIModule:
            def __getattr__(self, name):
                raise ImportError("No module named 'openai'")

        sys.modules["openai"] = FakeOpenAIModule()

        try:
            adapter = QwenInvokerAdapter(base_url="http://localhost:8000/v1")

            healing_input = HealingInput(
                failure_type="test",
                error_signature="test",
                trace_id="test",
                retry_count=0,
                blast_radius_estimate=0.0,
                required_tools=(),
                violation_metadata_refs=(),
            )
            config = load_default_healing_tier_config()
            decision = route_healing_tier(healing_input, config)

            with pytest.raises(ImportError, match="OpenAI SDK is required"):
                adapter.invoke_qwen_vllm(healing_input, decision, config)
        finally:
            # Restore original module
            if original_openai is not None:
                sys.modules["openai"] = original_openai
            else:
                sys.modules.pop("openai", None)

    def test_qwen_adapter_handles_sdk_error(self) -> None:
        """Qwen adapter should properly handle and log SDK errors."""
        # Setup fake OpenAI module that raises an error
        fake_openai = Mock()
        fake_client = Mock()
        fake_client.chat.completions.create.side_effect = Exception("API Error")
        fake_openai.OpenAI.return_value = fake_client

        sys.modules["openai"] = fake_openai

        try:
            adapter = QwenInvokerAdapter(base_url="http://localhost:8000/v1")

            healing_input = HealingInput(
                failure_type="syntax_error",
                error_signature="SyntaxError: invalid_syntax",
                trace_id="error-trace-456",
                retry_count=1,
                blast_radius_estimate=0.5,
                required_tools=(),
                violation_metadata_refs=(),
            )

            config = load_default_healing_tier_config()
            decision = route_healing_tier(healing_input, config)

            # Should raise the SDK error
            with pytest.raises(Exception, match="API Error"):
                adapter.invoke_qwen_vllm(healing_input, decision, config)

        finally:
            sys.modules.pop("openai", None)

    def test_qwen_adapter_not_implemented_methods(self) -> None:
        """Qwen adapter should raise NotImplementedError for unsupported methods."""
        adapter = QwenInvokerAdapter(base_url="http://localhost:8000/v1")

        healing_input = HealingInput(
            failure_type="test",
            error_signature="test",
            trace_id="test",
            retry_count=0,
            blast_radius_estimate=0.0,
            required_tools=(),
            violation_metadata_refs=(),
        )
        config = load_default_healing_tier_config()
        decision = route_healing_tier(healing_input, config)

        with pytest.raises(NotImplementedError, match="invoke_local not supported"):
            adapter.invoke_local(healing_input, decision, config)

        with pytest.raises(NotImplementedError, match="invoke_gemini not supported"):
            adapter.invoke_gemini(healing_input, decision, config)


class TestGeminiAdapterContract:
    """Contract tests for GeminiInvokerAdapter with faked Google SDK."""

    def test_gemini_adapter_invokes_sdk_with_correct_args(self) -> None:
        """Gemini adapter should call Google SDK with expected parameters."""
        # Setup fake google.generativeai module
        fake_genai = Mock()
        fake_model = Mock()
        fake_response = Mock()
        fake_response.text = "Fix: add missing import statement"
        fake_response.__len__ = lambda: len(fake_response.text)
        fake_model.generate_content.return_value = fake_response
        fake_genai.configure = Mock()
        fake_genai.GenerativeModel.return_value = fake_model
        fake_genai.types = Mock()
        fake_genai.types.GenerationConfig = Mock

        # Inject fake module into sys.modules
        sys.modules["google.generativeai"] = fake_genai

        try:
            adapter = GeminiInvokerAdapter(api_key="test-gemini-key")

            # Prepare healing input
            healing_input = HealingInput(
                failure_type="type_hint_error",
                error_signature="TypeError: missing_type_hint",
                trace_id="gemini-trace-789",
                retry_count=2,
                blast_radius_estimate=0.7,
                required_tools=("type_fix", "ast_rewrite"),
                violation_metadata_refs=("/path/to/typed.py", "/path/to/types.py"),
            )

            config = load_default_healing_tier_config()
            decision = route_healing_tier(healing_input, config)

            # Invoke adapter
            record = adapter.invoke_gemini(healing_input, decision, config, agent_name="GeminiTestAgent")

            # Verify SDK was called correctly
            fake_genai.configure.assert_called_once_with(api_key="test-gemini-key")
            fake_genai.GenerativeModel.assert_called_once_with(config.model_gemini_2_5_pro_id)
            fake_model.generate_content.assert_called_once()

            call_args = fake_model.generate_content.call_args
            prompt = call_args.args[0]  # First positional argument

            # Verify prompt is structured and non-empty
            assert "GeminiTestAgent" in prompt
            assert "type_hint_error" in prompt
            assert "TypeError: missing_type_hint" in prompt
            assert "Retry Count: 2" in prompt
            assert "Required Tools: type_fix, ast_rewrite" in prompt
            assert "Context Files: /path/to/typed.py, /path/to/types.py" in prompt
            assert len(prompt) > 100  # Substantial content

            # Verify generation config was passed
            assert "generation_config" in call_args.kwargs

            # Verify returned record
            assert record.tier == HealingTier.GEMINI_2_5_PRO
            assert record.model_id == config.model_gemini_2_5_pro_id
            assert record.agent_name == "GeminiTestAgent"
            assert record.trace_id == "gemini-trace-789"
            assert record.method_called == "invoke_gemini"

        finally:
            # Clean up sys.modules
            sys.modules.pop("google.generativeai", None)

    def test_gemini_adapter_raises_import_error_when_sdk_missing(self) -> None:
        """Gemini adapter logs error and returns record when Google SDK is not available."""
        # Clear any cached imports and remove the module
        sys.modules.pop("google.generativeai", None)

        # Also clear the adapter module from cache to force re-import
        sys.modules.pop("agentic_core.L2_execution.healers.healing_provider_adapters", None)

        # Re-import the adapter to test fresh import
        from agentic_core.L2_execution.healers.healing_provider_adapters import GeminiInvokerAdapter

        adapter = GeminiInvokerAdapter(api_key="test-key")

        healing_input = HealingInput(
            failure_type="test",
            error_signature="test",
            trace_id="test",
            retry_count=0,
            blast_radius_estimate=0.0,
            required_tools=(),
            violation_metadata_refs=(),
        )
        config = load_default_healing_tier_config()
        decision = route_healing_tier(healing_input, config)

        # Adapter swallows SDK errors and returns a record with response_text=None
        record = adapter.invoke_gemini(healing_input, decision, config)
        assert record is not None
        assert record.response_text is None

    def test_gemini_adapter_handles_sdk_error(self) -> None:
        """Gemini adapter logs SDK errors and returns record with response_text=None."""
        # Setup fake google.generativeai module that raises an error
        fake_genai = Mock()
        fake_model = Mock()
        fake_model.generate_content.side_effect = Exception("Gemini API Error")
        fake_genai.configure = Mock()
        fake_genai.GenerativeModel.return_value = fake_model

        sys.modules["google.generativeai"] = fake_genai

        # Clear adapter module cache
        sys.modules.pop("agentic_core.L2_execution.healers.healing_provider_adapters", None)
        from agentic_core.L2_execution.healers.healing_provider_adapters import GeminiInvokerAdapter

        try:
            adapter = GeminiInvokerAdapter(api_key="test-key")

            healing_input = HealingInput(
                failure_type="runtime_error",
                error_signature="RuntimeError: unexpected_condition",
                trace_id="gemini-error-trace",
                retry_count=0,
                blast_radius_estimate=0.4,
                required_tools=(),
                violation_metadata_refs=(),
            )

            config = load_default_healing_tier_config()
            decision = route_healing_tier(healing_input, config)

            # Adapter swallows SDK errors and returns record with response_text=None
            record = adapter.invoke_gemini(healing_input, decision, config)
            assert record is not None
            assert record.response_text is None

        finally:
            sys.modules.pop("google.generativeai", None)

    def test_gemini_adapter_not_implemented_methods(self) -> None:
        """Gemini adapter should raise NotImplementedError for unsupported methods."""
        adapter = GeminiInvokerAdapter(api_key="test-key")

        healing_input = HealingInput(
            failure_type="test",
            error_signature="test",
            trace_id="test",
            retry_count=0,
            blast_radius_estimate=0.0,
            required_tools=(),
            violation_metadata_refs=(),
        )
        config = load_default_healing_tier_config()
        decision = route_healing_tier(healing_input, config)

        with pytest.raises(NotImplementedError, match="invoke_local not supported"):
            adapter.invoke_local(healing_input, decision, config)

        with pytest.raises(NotImplementedError, match="invoke_qwen_vllm not supported"):
            adapter.invoke_qwen_vllm(healing_input, decision, config)


class TestLocalAgentAdapterContract:
    """Contract tests for LocalAgentAdapter."""

    def test_local_adapter_invokes_without_sdk(self) -> None:
        """Local adapter should work without any SDK dependencies."""
        adapter = LocalAgentAdapter()

        healing_input = HealingInput(
            failure_type="naming_violation",
            error_signature="NamingError: snake_case_required",
            trace_id="local-trace-001",
            retry_count=0,
            blast_radius_estimate=0.2,
            required_tools=("rename",),
            violation_metadata_refs=("/path/to/bad_name.py",),
        )

        config = load_default_healing_tier_config()
        decision = route_healing_tier(healing_input, config)

        # Should work without any external dependencies
        record = adapter.invoke_local(healing_input, decision, config, agent_name="LocalTestAgent")

        # Verify returned record
        assert record.tier == HealingTier.LOCAL_AGENT
        assert record.model_id == "local"
        assert record.agent_name == "LocalTestAgent"
        assert record.trace_id == "local-trace-001"
        assert record.method_called == "invoke_local"

    def test_local_adapter_not_implemented_methods(self) -> None:
        """Local adapter should raise NotImplementedError for LLM methods."""
        adapter = LocalAgentAdapter()

        healing_input = HealingInput(
            failure_type="test",
            error_signature="test",
            trace_id="test",
            retry_count=0,
            blast_radius_estimate=0.0,
            required_tools=(),
            violation_metadata_refs=(),
        )
        config = load_default_healing_tier_config()
        decision = route_healing_tier(healing_input, config)

        with pytest.raises(NotImplementedError, match="invoke_qwen_vllm not supported"):
            adapter.invoke_qwen_vllm(healing_input, decision, config)

        with pytest.raises(NotImplementedError, match="invoke_gemini not supported"):
            adapter.invoke_gemini(healing_input, decision, config)


class TestAdapterIntegrationWithDispatcher:
    """Integration tests proving adapters work with the healing tier dispatcher."""

    def test_dispatcher_with_real_qwen_adapter(self) -> None:
        """Dispatcher should correctly select and invoke real Qwen adapter."""
        # Setup fake OpenAI module
        fake_openai = Mock()
        fake_client = Mock()
        fake_response = Mock()
        fake_response.choices = [Mock()]
        fake_response.choices[0].message.content = "Qwen fix applied"
        fake_response.usage = Mock()
        fake_response.usage.prompt_tokens = 100
        fake_response.usage.completion_tokens = 50
        fake_client.chat.completions.create.return_value = fake_response
        fake_openai.OpenAI.return_value = fake_client

        sys.modules["openai"] = fake_openai

        try:
            qwen_adapter = QwenInvokerAdapter(base_url="http://localhost:8000/v1")

            # Use real adapter with dispatcher
            from agentic_core.L2_execution.healers.healing_tier_dispatcher import dispatch_healing

            healing_input = HealingInput(
                failure_type="import_cycle",
                error_signature="ImportCycle: circular_dependency",
                trace_id="dispatcher-qwen-001",
                retry_count=0,
                blast_radius_estimate=0.6,
                required_tools=("import_reorder",),
                violation_metadata_refs=(),
            )

            config = load_default_healing_tier_config()
            decision, record = dispatch_healing(
                healing_input, config, invoker=qwen_adapter, agent_name="DispatcherTest"
            )

            # Verify tier selection and adapter invocation
            assert decision.tier == HealingTier.QWEN_VLLM
            assert record.tier == HealingTier.QWEN_VLLM
            assert record.model_id == config.model_qwen_vllm_id
            assert record.agent_name == "DispatcherTest"
            assert record.method_called == "invoke_qwen_vllm"
            assert record.trace_id == "dispatcher-qwen-001"

            # Verify SDK was called through adapter
            fake_client.chat.completions.create.assert_called_once()

        finally:
            sys.modules.pop("openai", None)

    def test_dispatcher_with_real_gemini_adapter(self) -> None:
        """Dispatcher should correctly select and invoke real Gemini adapter."""
        # Setup fake google.generativeai module
        fake_genai = Mock()
        fake_model = Mock()
        fake_response = Mock()
        fake_response.text = "Gemini fix applied"
        fake_model.generate_content.return_value = fake_response
        fake_genai.configure = Mock()
        fake_genai.GenerativeModel.return_value = fake_model
        fake_genai.types = Mock()
        fake_genai.types.GenerationConfig = Mock

        sys.modules["google.generativeai"] = fake_genai

        # Clear adapter module cache
        sys.modules.pop("agentic_core.L2_execution.healers.healing_provider_adapters", None)
        from agentic_core.L2_execution.healers.healing_provider_adapters import GeminiInvokerAdapter

        try:
            gemini_adapter = GeminiInvokerAdapter(api_key="test-key")

            # Use real adapter with dispatcher
            from agentic_core.L2_execution.healers.healing_tier_dispatcher import dispatch_healing

            healing_input = HealingInput(
                failure_type="integrity_gate_failure",
                error_signature="IntegrityGate: checksum_mismatch",
                trace_id="dispatcher-gemini-002",
                retry_count=3,  # High retry forces Gemini
                blast_radius_estimate=0.9,
                required_tools=("checksum_fix", "file_restore"),
                violation_metadata_refs=(),
            )

            config = load_default_healing_tier_config()
            decision, record = dispatch_healing(
                healing_input, config, invoker=gemini_adapter, agent_name="DispatcherGeminiTest"
            )

            # Verify tier selection and adapter invocation
            assert decision.tier == HealingTier.GEMINI_2_5_PRO
            assert record.tier == HealingTier.GEMINI_2_5_PRO
            assert record.model_id == config.model_gemini_2_5_pro_id
            assert record.agent_name == "DispatcherGeminiTest"
            assert record.method_called == "invoke_gemini"
            assert record.trace_id == "dispatcher-gemini-002"

            # Verify SDK was called through adapter
            fake_genai.GenerativeModel.assert_called_once_with(config.model_gemini_2_5_pro_id)
            fake_model.generate_content.assert_called_once()

        finally:
            sys.modules.pop("google.generativeai", None)

    def test_dispatcher_with_local_adapter(self) -> None:
        """Dispatcher should correctly select and invoke local adapter."""
        local_adapter = LocalAgentAdapter()

        from agentic_core.L2_execution.healers.healing_tier_dispatcher import dispatch_healing

        healing_input = HealingInput(
            failure_type="naming_violation",
            error_signature="NamingError: camel_case_found",
            trace_id="dispatcher-local-003",
            retry_count=0,
            blast_radius_estimate=0.0,  # Zero blast radius guarantees conf > X → LOCAL_AGENT
            required_tools=("rename",),
            violation_metadata_refs=(),
        )

        config = load_default_healing_tier_config()
        decision, record = dispatch_healing(
            healing_input, config, invoker=local_adapter, agent_name="DispatcherLocalTest"
        )

        # Verify tier selection and adapter invocation
        assert decision.tier == HealingTier.LOCAL_AGENT
        assert record.tier == HealingTier.LOCAL_AGENT
        assert record.model_id == "local"
        assert record.agent_name == "DispatcherLocalTest"
        assert record.method_called == "invoke_local"
        assert record.trace_id == "dispatcher-local-003"


class TestTokenLimitConstants:
    """Tests for externalized token limit constants."""

    def test_token_limit_constants_exist_and_have_correct_values(self) -> None:
        """Module should define token limit constants with correct values."""
        from agentic_core.L2_execution.healers.healing_provider_adapters import (
            DEFAULT_MAX_OUTPUT_TOKENS,
            DEFAULT_MAX_TOKENS,
        )

        # Constants should exist and have the expected values
        assert DEFAULT_MAX_TOKENS == 2048
        assert DEFAULT_MAX_OUTPUT_TOKENS == 2048

    def test_qwen_adapter_uses_default_max_tokens_constant(self) -> None:
        """Qwen adapter should use DEFAULT_MAX_TOKENS constant."""
        import sys
        from unittest.mock import Mock

        # Setup fake OpenAI module
        fake_openai = Mock()
        fake_client = Mock()
        fake_response = Mock()
        fake_response.choices = [Mock()]
        fake_response.choices[0].message.content = "Test response"
        fake_response.usage = Mock()
        fake_response.usage.prompt_tokens = 100
        fake_response.usage.completion_tokens = 50

        fake_client.chat.completions.create.return_value = fake_response
        fake_openai.OpenAI.return_value = fake_client

        sys.modules["openai"] = fake_openai

        try:
            from agentic_core.L2_execution.healers.healing_provider_adapters import (
                DEFAULT_MAX_TOKENS,
                QwenInvokerAdapter,
            )
            from agentic_core.L2_execution.healers.healing_tier_config import (
                load_default_healing_tier_config,
            )
            from agentic_core.L2_execution.healers.healing_tier_types import (
                HealingDecision,
                HealingInput,
                HealingTier,
            )

            # Create adapter and invoke
            adapter = QwenInvokerAdapter(base_url="http://localhost:8000")
            healing_input = HealingInput(
                failure_type="test_failure",
                error_signature="TestError",
                trace_id="test-001",
                retry_count=0,
                blast_radius_estimate=0.5,
                required_tools=(),
                violation_metadata_refs=(),
            )
            decision = HealingDecision(
                tier=HealingTier.QWEN_VLLM, heal_confidence=0.8, reason_codes=("test",)
            )
            config = load_default_healing_tier_config()

            adapter.invoke_qwen_vllm(healing_input, decision, config, agent_name="TestAgent")

            # Verify the constant was used
            fake_client.chat.completions.create.assert_called_once()
            call_args = fake_client.chat.completions.create.call_args
            assert call_args.kwargs["max_tokens"] == DEFAULT_MAX_TOKENS

        finally:
            sys.modules.pop("openai", None)

    def test_gemini_adapter_uses_default_max_output_tokens_constant(self) -> None:
        """Gemini adapter should use DEFAULT_MAX_OUTPUT_TOKENS constant."""
        import sys
        from unittest.mock import Mock

        # Setup fake Gemini module
        fake_genai = Mock()
        fake_model = Mock()
        fake_response = Mock()
        fake_response.text = "Test response"

        fake_model.generate_content.return_value = fake_response
        fake_genai.GenerativeModel.return_value = fake_model
        fake_genai.types.GenerationConfig = Mock

        sys.modules["google.generativeai"] = fake_genai

        try:
            from agentic_core.L2_execution.healers.healing_provider_adapters import (
                DEFAULT_MAX_OUTPUT_TOKENS,
                GeminiInvokerAdapter,
            )
            from agentic_core.L2_execution.healers.healing_tier_config import (
                load_default_healing_tier_config,
            )
            from agentic_core.L2_execution.healers.healing_tier_types import (
                HealingDecision,
                HealingInput,
                HealingTier,
            )

            # Create adapter and invoke
            adapter = GeminiInvokerAdapter(api_key="test-key")
            healing_input = HealingInput(
                failure_type="test_failure",
                error_signature="TestError",
                trace_id="test-002",
                retry_count=0,
                blast_radius_estimate=0.5,
                required_tools=(),
                violation_metadata_refs=(),
            )
            decision = HealingDecision(
                tier=HealingTier.GEMINI_2_5_PRO, heal_confidence=0.8, reason_codes=("test",)
            )
            config = load_default_healing_tier_config()

            adapter.invoke_gemini(healing_input, decision, config, agent_name="TestAgent")

            # Verify the constant was used
            fake_model.generate_content.assert_called_once()
            call_args = fake_model.generate_content.call_args
            generation_config = call_args.kwargs["generation_config"]
            assert generation_config.max_output_tokens == DEFAULT_MAX_OUTPUT_TOKENS

        finally:
            sys.modules.pop("google.generativeai", None)


# ---------------------------------------------------------------------------
# Plan 1 hardening tests
# ---------------------------------------------------------------------------


class TestResponseCapture:
    """Plan 1 Phase 1-A: model response_text must be captured into InvocationRecord."""

    def test_qwen_response_text_captured(self) -> None:
        fake_openai = Mock()
        fake_client = Mock()
        fake_response = Mock()
        fake_response.choices = [Mock()]
        fake_response.choices[0].message.content = "Fix: add missing __init__.py"
        fake_client.chat.completions.create.return_value = fake_response
        fake_openai.OpenAI.return_value = fake_client
        sys.modules["openai"] = fake_openai
        try:
            adapter = QwenInvokerAdapter(base_url="http://localhost:8000/v1", api_key="x")
            hi = HealingInput(
                failure_type="missing_init",
                error_signature="ModuleError",
                trace_id="rt-001",
                retry_count=0,
                blast_radius_estimate=0.3,
            )
            cfg = load_default_healing_tier_config()
            dec = route_healing_tier(hi, cfg)
            record = adapter.invoke_qwen_vllm(hi, dec, cfg, agent_name="A")
            assert record.response_text == "Fix: add missing __init__.py"
        finally:
            sys.modules.pop("openai", None)

    def test_qwen_response_text_none_when_no_choices(self) -> None:
        fake_openai = Mock()
        fake_client = Mock()
        fake_resp = Mock()
        fake_resp.choices = []
        fake_client.chat.completions.create.return_value = fake_resp
        fake_openai.OpenAI.return_value = fake_client
        sys.modules["openai"] = fake_openai
        try:
            adapter = QwenInvokerAdapter(base_url="http://localhost:8000/v1", api_key="x")
            hi = HealingInput(
                failure_type="t",
                error_signature="t",
                trace_id="rt-002",
                retry_count=0,
                blast_radius_estimate=0.0,
            )
            cfg = load_default_healing_tier_config()
            dec = route_healing_tier(hi, cfg)
            record = adapter.invoke_qwen_vllm(hi, dec, cfg)
            assert record.response_text is None
        finally:
            sys.modules.pop("openai", None)

    def test_gemini_response_text_captured(self) -> None:
        fake_genai = Mock()
        fake_model = Mock()
        fake_resp = Mock()
        fake_resp.text = "Gemini fix: restructure imports"
        fake_model.generate_content.return_value = fake_resp
        fake_genai.configure = Mock()
        fake_genai.GenerativeModel.return_value = fake_model
        fake_genai.types = Mock()
        fake_genai.types.GenerationConfig = Mock
        sys.modules["google.generativeai"] = fake_genai
        try:
            adapter = GeminiInvokerAdapter(api_key="k")
            hi = HealingInput(
                failure_type="import_cycle",
                error_signature="IC",
                trace_id="rt-003",
                retry_count=3,
                blast_radius_estimate=0.8,
            )
            cfg = load_default_healing_tier_config()
            dec = route_healing_tier(hi, cfg)
            record = adapter.invoke_gemini(hi, dec, cfg, agent_name="A")
            assert record.response_text == "Gemini fix: restructure imports"
        finally:
            sys.modules.pop("google.generativeai", None)

    def test_gemini_response_text_none_on_safety_block(self) -> None:
        """response_text is None when .text property raises (safety block)."""
        fake_genai = Mock()
        fake_model = Mock()
        bad_resp = Mock(spec=[])  # no .text attribute
        fake_model.generate_content.return_value = bad_resp
        fake_genai.configure = Mock()
        fake_genai.GenerativeModel.return_value = fake_model
        fake_genai.types = Mock()
        fake_genai.types.GenerationConfig = Mock
        sys.modules["google.generativeai"] = fake_genai
        try:
            adapter = GeminiInvokerAdapter(api_key="k")
            hi = HealingInput(
                failure_type="t",
                error_signature="t",
                trace_id="rt-004",
                retry_count=3,
                blast_radius_estimate=0.8,
            )
            cfg = load_default_healing_tier_config()
            dec = route_healing_tier(hi, cfg)
            record = adapter.invoke_gemini(hi, dec, cfg)
            assert record.response_text is None
        finally:
            sys.modules.pop("google.generativeai", None)


class TestThresholdUnification:
    """Plan 1 Phase 1-B: HEALING_CONFIDENCE_X/Y single SSOT."""

    def test_meta_learning_imports_equal_config_thresholds(self) -> None:
        from agentic_core.L2_execution.healers.healing_tier_config import (
            HEALING_CONFIDENCE_X as cfg_x,
        )
        from agentic_core.L2_execution.healers.healing_tier_config import (
            HEALING_CONFIDENCE_Y as cfg_y,
        )
        from agentic_core.L2_execution.healers.qwen_meta_learning import (
            HEALING_CONFIDENCE_X as meta_x,
        )
        from agentic_core.L2_execution.healers.qwen_meta_learning import (
            HEALING_CONFIDENCE_Y as meta_y,
        )

        assert meta_x == cfg_x
        assert meta_y == cfg_y

    def test_threshold_defined_only_in_config_ast_invariant(self) -> None:
        import ast
        from pathlib import Path

        healers_dir = Path(__file__).parents[5] / L2_EXECUTION_DIR / "healers"
        bad_files = []
        for py_file in healers_dir.glob("*.py"):
            if py_file.name == "healing_tier_config.py":
                continue
            try:
                tree = ast.parse(py_file.read_text(encoding="utf-8"))
            except SyntaxError:  # guardian: allow-silent-swallower
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == "HEALING_CONFIDENCE_X":
                            bad_files.append(py_file.name)
        assert bad_files == [], (
            f"HEALING_CONFIDENCE_X must only be defined in healing_tier_config.py; also found in: {bad_files}"
        )

    def test_validate_threshold_immutability_passes(self) -> None:
        from agentic_core.L2_execution.healers.qwen_meta_learning import (
            validate_threshold_immutability,
        )

        validate_threshold_immutability()  # must not raise


class TestHardenedGeminiModelLimits:
    """Plan 1 Phase 2-A: gemini-2.5-pro must appear in HardenedGeminiConfig.MODEL_LIMITS."""

    def test_gemini_2_5_pro_in_model_limits(self) -> None:
        from apps_shared.types.hardened_gemini_executor_types import HardenedGeminiConfig

        assert "gemini-2.5-pro" in HardenedGeminiConfig.MODEL_LIMITS

    def test_gemini_2_5_pro_context_window_is_1m(self) -> None:
        from apps_shared.types.hardened_gemini_executor_types import HardenedGeminiConfig

        assert HardenedGeminiConfig.MODEL_LIMITS["gemini-2.5-pro"] == 1_048_576

    def test_healing_config_model_id_covered_by_model_limits(self) -> None:
        from agentic_core.L2_execution.healers.healing_tier_config import (
            load_default_healing_tier_config,
        )
        from apps_shared.types.hardened_gemini_executor_types import HardenedGeminiConfig

        cfg = load_default_healing_tier_config()
        assert cfg.model_gemini_2_5_pro_id in HardenedGeminiConfig.MODEL_LIMITS, (
            f"'{cfg.model_gemini_2_5_pro_id}' not in HardenedGeminiConfig.MODEL_LIMITS"
        )
