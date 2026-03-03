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
        """Gemini adapter should raise ImportError when Google SDK is not available."""
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

        with pytest.raises(ImportError, match="google-generativeai SDK is required"):
            adapter.invoke_gemini(healing_input, decision, config)

    def test_gemini_adapter_handles_sdk_error(self) -> None:
        """Gemini adapter should properly handle and log SDK errors."""
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

            # Should raise the SDK error
            with pytest.raises(Exception, match="Gemini API Error"):
                adapter.invoke_gemini(healing_input, decision, config)

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
