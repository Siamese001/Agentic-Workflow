"""Unit tests for tools.ingestion.anthropic_context_gateway.

Covers the G1-residual adapter wiring per plan
``.windsurf/plans/c0-context-assembly-best-practices-b7c3a1.md`` §2a.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Make repo root importable when this test runs standalone.
_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tools.ingestion.anthropic_context_gateway import (
    AnthropicContextGateway,
    build_from_env,
)
from tools.ingestion.contextual_chunk_builder import (
    ContextualChunkBuilder,
    ContextualizationRequest,
)


# ---------------------------------------------------------------------------
# build_from_env
# ---------------------------------------------------------------------------


def test_build_from_env_returns_none_when_key_absent(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert build_from_env() is None


def test_build_from_env_returns_gateway_when_key_present(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    gw = build_from_env()
    assert isinstance(gw, AnthropicContextGateway)


# ---------------------------------------------------------------------------
# generate — success and failure routing
# ---------------------------------------------------------------------------


def test_generate_delegates_to_run_llm_anthropic():
    """Happy path: adapter forwards all kwargs and returns the result."""
    captured: dict = {}

    def fake_run_llm_anthropic(model, prompt, *, temperature, max_tokens, timeout_s):
        captured["model"] = model
        captured["prompt"] = prompt
        captured["temperature"] = temperature
        captured["max_tokens"] = max_tokens
        captured["timeout_s"] = timeout_s
        return "situated context about the chunk"

    with patch(
        "apps_rg.utils.providers_anthropic_client_util.run_llm_anthropic",
        fake_run_llm_anthropic,
    ):
        gw = AnthropicContextGateway()
        result = gw.generate(
            "<document>doc</document>\n<chunk>c</chunk>",
            model="claude-haiku-4-5",
            max_tokens=150,
            temperature=0.0,
            timeout_s=30,
        )

    assert result == "situated context about the chunk"
    assert captured["model"] == "claude-haiku-4-5"
    assert "<document>" in captured["prompt"]
    assert captured["temperature"] == 0.0
    assert captured["max_tokens"] == 150
    assert captured["timeout_s"] == 30


def test_generate_without_model_or_default_raises():
    gw = AnthropicContextGateway()
    with pytest.raises(RuntimeError, match="no model"):
        gw.generate(
            "prompt",
            model="",
            max_tokens=10,
            temperature=0.0,
            timeout_s=5,
        )


def test_generate_uses_default_model_when_caller_passes_empty():
    captured: dict = {}

    def fake_run_llm_anthropic(model, prompt, *, temperature, max_tokens, timeout_s):
        captured["model"] = model
        return "ok"

    with patch(
        "apps_rg.utils.providers_anthropic_client_util.run_llm_anthropic",
        fake_run_llm_anthropic,
    ):
        gw = AnthropicContextGateway(default_model="claude-haiku-4-5")
        gw.generate(
            "prompt",
            model="",  # empty -> default
            max_tokens=10,
            temperature=0.0,
            timeout_s=5,
        )
    assert captured["model"] == "claude-haiku-4-5"


def test_generate_wraps_runtime_errors_and_reraises():
    def fail(*_args, **_kwargs):
        raise RuntimeError("upstream boom")

    with patch(
        "apps_rg.utils.providers_anthropic_client_util.run_llm_anthropic",
        fail,
    ):
        gw = AnthropicContextGateway()
        with pytest.raises(RuntimeError, match="Anthropic gateway generation failed"):
            gw.generate(
                "p",
                model="claude-haiku-4-5",
                max_tokens=10,
                temperature=0.0,
                timeout_s=5,
            )


def test_generate_wraps_value_errors_and_reraises():
    def fail(*_args, **_kwargs):
        raise ValueError("bad response")

    with patch(
        "apps_rg.utils.providers_anthropic_client_util.run_llm_anthropic",
        fail,
    ):
        gw = AnthropicContextGateway()
        with pytest.raises(RuntimeError, match="Anthropic gateway generation failed"):
            gw.generate(
                "p",
                model="claude-haiku-4-5",
                max_tokens=10,
                temperature=0.0,
                timeout_s=5,
            )


# ---------------------------------------------------------------------------
# Integration: ContextualChunkBuilder + adapter end-to-end
# ---------------------------------------------------------------------------


def test_builder_uses_gateway_path_when_adapter_injected():
    """This is the test that would have caught the G1-residual gap earlier.

    With the adapter injected AND ANTHROPIC_API_KEY set, the builder's
    gateway path executes and the result carries source='gateway'.
    """
    stub_output = "This chunk defines the RetrievalPrefilter class."

    def fake_run_llm_anthropic(*_args, **_kwargs):
        return stub_output

    with (
        patch(
            "apps_rg.utils.providers_anthropic_client_util.run_llm_anthropic",
            fake_run_llm_anthropic,
        ),
        patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}),
    ):
        gw = AnthropicContextGateway()
        builder = ContextualChunkBuilder(gateway=gw)
        result = builder.build(
            ContextualizationRequest(
                document="Full document text about the C0 retrieval pipeline.",
                chunk="class RetrievalPrefilter: ...",
                metadata={"file_path": "retrieval_plan.py"},
            )
        )

    assert result.source == "gateway"
    assert result.context == stub_output


def test_builder_falls_back_to_heuristic_when_gateway_raises():
    """If generate() raises, the builder must fall back to heuristic — never
    hard-fail ingestion."""

    def fail(*_args, **_kwargs):
        raise RuntimeError("service unavailable")

    with (
        patch(
            "apps_rg.utils.providers_anthropic_client_util.run_llm_anthropic",
            fail,
        ),
        patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}),
    ):
        gw = AnthropicContextGateway()
        builder = ContextualChunkBuilder(gateway=gw)
        result = builder.build(
            ContextualizationRequest(
                document="doc",
                chunk="chunk",
                metadata={"title": "Example"},
            )
        )

    assert result.source == "heuristic"
    assert result.context  # non-empty heuristic string
