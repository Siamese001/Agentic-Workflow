"""
Adapter Contract Tests — Prove Real Adapters Are Invoked with Mocked SDKs.

These tests verify that the actual Qwen and Gemini adapters are selected
and invoked correctly, with mocked SDK calls to avoid network dependencies.

Tests cover:
- Correct adapter chosen for each tier
- SDK methods called with expected arguments
- Model IDs and context passed through correctly
- Prompt payload is structured and non-empty
- Error handling and logging
"""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

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

pytestmark = pytest.mark.unit_min_deps


class TestQwenAdapterContract:
    """Contract tests for QwenInvokerAdapter with mocked OpenAI SDK."""

    def test_qwen_adapter_invokes_sdk_with_correct_args(self) -> None:
        """Qwen adapter should call OpenAI SDK with expected parameters."""
        # Setup mock OpenAI client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Fix: import missing module"
        mock_response.usage = Mock()
        mock_response.usage.prompt_tokens = 150
        mock_response.usage.completion_tokens = 75
        mock_client.chat.completions.create.return_value = mock_response

        # Create adapter with mocked client (patch openai module for lazy import)
        with patch("openai.OpenAI") as mock_openai:
            mock_openai.return_value = mock_client
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
            mock_client.chat.completions.create.assert_called_once()
            call_args = mock_client.chat.completions.create.call_args

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

    def test_qwen_adapter_handles_sdk_error(self) -> None:
        """Qwen adapter should properly handle and log SDK errors."""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        with patch("openai.OpenAI") as mock_openai:
            mock_openai.return_value = mock_client
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
    """Contract tests for GeminiInvokerAdapter with mocked Google SDK."""

    def test_gemini_adapter_invokes_sdk_with_correct_args(self) -> None:
        """Gemini adapter should call Google SDK with expected parameters."""
        # Setup mock Gemini response
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "Fix: add missing import statement"
        mock_model.generate_content.return_value = mock_response

        # Create adapter with mocked SDK (patch the lazy import)
        with patch("agentic_core.L2_execution.healers.healing_provider_adapters.google.generativeai") as mock_genai:
            # Mock the types.GenerationConfig as well
            mock_genai.types.GenerationConfig = Mock
            mock_genai.GenerativeModel.return_value = mock_model
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
            mock_genai.GenerativeModel.assert_called_once_with(config.model_gemini_2_5_pro_id)
            mock_model.generate_content.assert_called_once()

            call_args = mock_model.generate_content.call_args
            prompt = call_args.args[0]  # First positional argument

            # Verify prompt is structured and non-empty
            assert "GeminiTestAgent" in prompt
            assert "type_hint_error" in prompt
            assert "TypeError: missing_type_hint" in prompt
            assert "Retry Count: 2" in prompt
            assert "Required Tools: type_fix, ast_rewrite" in prompt
            assert "Context Files: /path/to/typed.py, /path/to/types.py" in prompt
            assert len(prompt) > 100  # Substantial content

            # Verify generation config was passed (mocked, so just check it's called)
            assert "generation_config" in call_args.kwargs

            # Verify returned record
            assert record.tier == HealingTier.GEMINI_2_5_PRO
            assert record.model_id == config.model_gemini_2_5_pro_id
            assert record.agent_name == "GeminiTestAgent"
            assert record.trace_id == "gemini-trace-789"
            assert record.method_called == "invoke_gemini"

    def test_gemini_adapter_handles_sdk_error(self) -> None:
        """Gemini adapter should properly handle and log SDK errors."""
        mock_model = Mock()
        mock_model.generate_content.side_effect = Exception("Gemini API Error")

        with patch("google.generativeai") as mock_genai:
            mock_genai.GenerativeModel.return_value = mock_model
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

            # Should raise the SDK error
            with pytest.raises(Exception, match="Gemini API Error"):
                adapter.invoke_gemini(healing_input, decision, config)

    def test_gemini_adapter_not_implemented_methods(self) -> None:
        """Gemini adapter should raise NotImplementedError for unsupported methods."""
        with patch("google.generativeai"):
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
        # Mock OpenAI SDK
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Qwen fix applied"
        mock_response.usage = Mock()
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 50
        mock_client.chat.completions.create.return_value = mock_response

        with patch("openai.OpenAI") as mock_openai:
            mock_openai.return_value = mock_client
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
            mock_client.chat.completions.create.assert_called_once()

    def test_dispatcher_with_real_gemini_adapter(self) -> None:
        """Dispatcher should correctly select and invoke real Gemini adapter."""
        # Mock Gemini SDK
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "Gemini fix applied"
        mock_model.generate_content.return_value = mock_response

        with patch("google.generativeai") as mock_genai:
            mock_genai.GenerativeModel.return_value = mock_model
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
            mock_genai.GenerativeModel.assert_called_once_with(config.model_gemini_2_5_pro_id)
            mock_model.generate_content.assert_called_once()

    def test_dispatcher_with_local_adapter(self) -> None:
        """Dispatcher should correctly select and invoke local adapter."""
        local_adapter = LocalAgentAdapter()

        from agentic_core.L2_execution.healers.healing_tier_dispatcher import dispatch_healing

        healing_input = HealingInput(
            failure_type="naming_violation",
            error_signature="NamingError: camel_case_found",
            trace_id="dispatcher-local-003",
            retry_count=0,
            blast_radius_estimate=0.1,  # Low blast radius favors local
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
