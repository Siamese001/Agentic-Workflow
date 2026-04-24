"""Unit tests for tools.ingestion.qwen_context_gateway.

Covers the local-GPU Qwen vLLM adapter that replaces the paid Anthropic
contextualization path per user direction 2026-04-24. See
``.windsurf/plans/c0-context-assembly-best-practices-b7c3a1.md`` §2a.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Make repo root importable when this test runs standalone.
_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tools.ingestion import qwen_context_gateway as qcg_module
from tools.ingestion.qwen_context_gateway import (
    QwenContextGateway,
    _resolve_defaults,
    _vllm_server_reachable,
    build_from_env,
)


@pytest.fixture(autouse=True)
def _reset_module_singletons():
    """Reset the module-level singletons between tests.

    ``qwen_context_gateway`` caches the gateway and event loop at module scope
    to amortize init cost across chunks in a single ingest run. Tests must
    reset these between cases so one test's mock doesn't leak into the next.
    """
    yield
    qcg_module._GATEWAY_INSTANCE = None
    if qcg_module._EVENT_LOOP is not None and not qcg_module._EVENT_LOOP.is_closed():
        qcg_module._EVENT_LOOP.close()
    qcg_module._EVENT_LOOP = None


# ---------------------------------------------------------------------------
# _resolve_defaults — SSOT delegation
# ---------------------------------------------------------------------------


def test_resolve_defaults_returns_registry_ssot_values():
    """Must delegate to L0 model_registry — no hardcoded defaults."""
    model_id, base_url = _resolve_defaults()
    # Exact values are env-driven, but must be non-empty strings matching the
    # documented defaults at agentic_core/L0_routing/config/model_registry.py.
    assert isinstance(model_id, str) and model_id
    assert isinstance(base_url, str) and base_url.startswith("http")


# ---------------------------------------------------------------------------
# _vllm_server_reachable — probe behavior
# ---------------------------------------------------------------------------


def test_vllm_probe_returns_false_on_unreachable_host():
    """Probe must not raise when vLLM is down; returns False for graceful
    fallback. Uses a deliberately-unused high port to guarantee no server."""
    assert _vllm_server_reachable("http://127.0.0.1:59999/v1", timeout_s=0.5) is False


def test_vllm_probe_returns_false_on_malformed_url():
    """Malformed URLs must not raise — probe returns False and caller falls
    back to heuristic. Protects the ingest pipeline from env-var typos."""
    assert _vllm_server_reachable("not-a-url", timeout_s=0.5) is False


def test_vllm_probe_returns_true_on_200_response():
    """Happy path: server responds 200, probe returns True."""
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.__enter__ = MagicMock(return_value=mock_resp)
    mock_resp.__exit__ = MagicMock(return_value=False)
    with patch(
        "tools.ingestion.qwen_context_gateway.urllib.request.urlopen",
        return_value=mock_resp,
    ):
        assert _vllm_server_reachable("http://localhost:8000/v1") is True


# ---------------------------------------------------------------------------
# build_from_env — factory behavior
# ---------------------------------------------------------------------------


def test_build_from_env_returns_none_when_server_unreachable(monkeypatch):
    """Default path when vLLM isn't running: factory returns None so callers
    fall back to heuristic, mirroring AnthropicContextGateway.build_from_env
    when ANTHROPIC_API_KEY is absent."""
    monkeypatch.delenv("QWEN_CONTEXT_GATEWAY_DISABLED", raising=False)
    with patch(
        "tools.ingestion.qwen_context_gateway._vllm_server_reachable",
        return_value=False,
    ):
        assert build_from_env() is None


def test_build_from_env_returns_none_when_disabled_flag_set(monkeypatch):
    """Explicit disable flag short-circuits even if vLLM would be reachable.
    CI and offline scenarios use this to guarantee heuristic-only runs."""
    monkeypatch.setenv("QWEN_CONTEXT_GATEWAY_DISABLED", "1")
    with patch(
        "tools.ingestion.qwen_context_gateway._vllm_server_reachable",
        return_value=True,
    ):
        assert build_from_env() is None


def test_build_from_env_returns_gateway_when_reachable(monkeypatch):
    """Happy path: server probe succeeds, factory returns a gateway instance."""
    monkeypatch.delenv("QWEN_CONTEXT_GATEWAY_DISABLED", raising=False)
    with patch(
        "tools.ingestion.qwen_context_gateway._vllm_server_reachable",
        return_value=True,
    ):
        gw = build_from_env()
        assert isinstance(gw, QwenContextGateway)


# ---------------------------------------------------------------------------
# QwenContextGateway.generate — success and failure routing
# ---------------------------------------------------------------------------


class _FakeVLLMResponse:
    """Minimal duck-type of QwenInferenceResponse for tests."""

    def __init__(self, *, success: bool, response: str | None, error: str | None = None):
        self.success = success
        self.response = response
        self.error_message = error
        self.confidence = 0.85 if success else 0.0
        self.model_used = "Qwen/Qwen2.5-14B-Instruct-AWQ"
        self.latency_ms = 42.0
        self.cached = False
        self.tokens_used = 100


def _patch_gateway_factory(fake_infer_impl):
    """Install a fake QwenInferenceGateway whose infer() calls fake_infer_impl."""
    fake_gateway = MagicMock()

    async def _fake_infer(request):
        return fake_infer_impl(request)

    fake_gateway.infer = _fake_infer
    qcg_module._GATEWAY_INSTANCE = fake_gateway
    return fake_gateway


def test_generate_success_returns_response_text():
    """Happy path: gateway returns non-empty text, adapter returns it verbatim."""
    def _ok(_request):
        return _FakeVLLMResponse(success=True, response="This chunk defines X within module Y.")
    _patch_gateway_factory(_ok)

    adapter = QwenContextGateway()
    result = adapter.generate(
        "prompt",
        model="Qwen/Qwen2.5-14B-Instruct-AWQ",
        max_tokens=150,
        temperature=0.0,
        timeout_s=30,
    )
    assert result == "This chunk defines X within module Y."


def test_generate_forwards_prompt_and_sampling_kwargs():
    """Adapter must forward prompt, max_tokens, and temperature unchanged."""
    captured: dict = {}

    def _capture(request):
        captured["prompt"] = request.prompt
        captured["max_tokens"] = request.max_tokens
        captured["temperature"] = request.temperature
        captured["app_name"] = request.app_name
        return _FakeVLLMResponse(success=True, response="ok")

    _patch_gateway_factory(_capture)

    adapter = QwenContextGateway()
    adapter.generate(
        "hello world",
        model="Qwen/Qwen2.5-14B-Instruct-AWQ",
        max_tokens=150,
        temperature=0.0,
        timeout_s=30,
    )
    assert captured["prompt"] == "hello world"
    assert captured["max_tokens"] == 150
    assert captured["temperature"] == 0.0
    assert captured["app_name"] == "contextual_chunk_builder"


def test_generate_raises_runtime_error_on_unsuccessful_response():
    """When vLLM returns success=False, adapter must raise RuntimeError so
    ContextualChunkBuilder catches it and falls back to heuristic."""
    def _fail(_request):
        return _FakeVLLMResponse(success=False, response=None, error="model OOM")
    _patch_gateway_factory(_fail)

    adapter = QwenContextGateway()
    with pytest.raises(RuntimeError, match="inference unsuccessful.*model OOM"):
        adapter.generate(
            "prompt",
            model="Qwen/Qwen2.5-14B-Instruct-AWQ",
            max_tokens=150,
            temperature=0.0,
            timeout_s=30,
        )


def test_generate_wraps_transport_exceptions_as_runtime_error():
    """Any transport/timeout error from the underlying gateway must surface as
    RuntimeError so the builder's catch list (ImportError, RuntimeError,
    ValueError, OSError) picks it up and falls back to heuristic."""
    def _raise(_request):
        raise OSError("connection refused")
    _patch_gateway_factory(_raise)

    adapter = QwenContextGateway()
    with pytest.raises(RuntimeError, match="generation failed.*connection refused"):
        adapter.generate(
            "prompt",
            model="Qwen/Qwen2.5-14B-Instruct-AWQ",
            max_tokens=150,
            temperature=0.0,
            timeout_s=30,
        )


def test_generate_returns_empty_string_on_empty_success_response():
    """Edge case: vLLM returns success=True but empty text. Adapter returns ""
    (not None, not an exception). Builder treats "" as "no context" and keeps
    the raw chunk — same contract as AnthropicContextGateway."""
    def _empty(_request):
        return _FakeVLLMResponse(success=True, response=None)
    _patch_gateway_factory(_empty)

    adapter = QwenContextGateway()
    result = adapter.generate(
        "prompt",
        model="Qwen/Qwen2.5-14B-Instruct-AWQ",
        max_tokens=150,
        temperature=0.0,
        timeout_s=30,
    )
    assert result == ""
