"""RG-GAP-04 invariant tests.

RG-GAP-04: AgentExecutor._execute_internal must route through SovereignLLMGateway
  BEFORE falling back to direct SDK clients.
  Negative control: when gateway is available, direct SDK must NOT be called.
"""

from __future__ import annotations

import sys
import types
from unittest.mock import MagicMock, patch


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

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
        """RG-GAP-04 negative: direct SDK must NOT be called when gateway succeeds."""
        gateway_mod, mock_gateway_cls, mock_gateway, _ = _build_gateway_stub()

        with patch.dict("sys.modules", {"agentic_core.interfaces.gateway": gateway_mod}):
            from apps_rg.utils.agent_executor_util import AgentConfig, AgentExecutor, AgentMessage

            config = AgentConfig(provider=self.Provider.OPENAI, model="gpt-4", enable_tracing=False)
            executor = AgentExecutor(config)

            with patch.object(executor, "_execute_openai") as mock_sdk:
                executor.execute(
                    messages=[AgentMessage(role="user", content="hello")],
                    system_prompt=None,
                )

        mock_sdk.assert_not_called(), "Direct SDK must not be called when gateway is available"
        assert True  # no-exception contract

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
        assert True  # no-exception contract

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
        """RG-GAP-04 source check: _try_execute_via_gateway must import SovereignLLMGateway."""
        import inspect

        from apps_rg.utils.agent_executor_util import AgentExecutor

        src = inspect.getsource(AgentExecutor._try_execute_via_gateway)
        assert "SovereignLLMGateway" in src, (
            "RG-GAP-04: _try_execute_via_gateway must reference SovereignLLMGateway"
        )
        assert "GenerationRequest" in src, "RG-GAP-04: _try_execute_via_gateway must use GenerationRequest"
