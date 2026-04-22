"""Unit tests for tools.ingestion.contextual_chunk_builder."""

from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from tools.ingestion.contextual_chunk_builder import (
    ContextualChunkBuilder,
    ContextualizationRequest,
    prepend_context,
)


@dataclass
class _StubGateway:
    """Test gateway adapter — captures calls and returns a canned response."""

    response: str = "This chunk defines the widget retry policy within the orders service."
    calls: list = field(default_factory=list)

    def generate(
        self,
        prompt: str,
        *,
        model: str,
        max_tokens: int,
        temperature: float,
        timeout_s: int,
    ) -> str:
        self.calls.append(
            {
                "prompt": prompt,
                "model": model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "timeout_s": timeout_s,
            }
        )
        return self.response


# ---------------------------------------------------------------------------
# Offline / heuristic path
# ---------------------------------------------------------------------------


def test_disabled_builder_returns_heuristic_with_metadata():
    builder = ContextualChunkBuilder(enabled=False)
    req = ContextualizationRequest(
        document="Full document text about retry policies.",
        chunk="def retry(): pass",
        metadata={"module": "orders.retry", "name": "retry", "entity_type": "function"},
    )
    result = builder.build(req)
    assert result.source == "heuristic"
    assert "retry" in result.context.lower()
    assert "orders.retry" in result.context


def test_heuristic_prefers_title_over_module():
    builder = ContextualChunkBuilder(enabled=False)
    req = ContextualizationRequest(
        document="Anthropic RAG best practices document content.",
        chunk="Use BM25 for exact matches.",
        metadata={"title": "Anthropic RAG Best Practices", "heading_path": "3. Retrieval Stack"},
    )
    result = builder.build(req)
    assert "Anthropic RAG Best Practices" in result.context
    assert "3. Retrieval Stack" in result.context


def test_heuristic_falls_back_to_first_sentence_when_no_metadata():
    builder = ContextualChunkBuilder(enabled=False)
    req = ContextualizationRequest(
        document="doc",
        chunk="This chunk describes something. Second sentence.",
        metadata=None,
    )
    result = builder.build(req)
    assert result.source == "heuristic"
    assert "This chunk describes something" in result.context


def test_empty_inputs_produce_empty_result():
    builder = ContextualChunkBuilder(enabled=False)
    req = ContextualizationRequest(document="", chunk="")
    result = builder.build(req)
    assert result.source == "empty"
    assert result.context == ""


# ---------------------------------------------------------------------------
# Gateway path
# ---------------------------------------------------------------------------


def test_gateway_path_calls_adapter_with_expected_prompt():
    gateway = _StubGateway()
    builder = ContextualChunkBuilder(gateway=gateway, enabled=True)
    req = ContextualizationRequest(
        document="FULL_DOC_CONTENT",
        chunk="CHUNK_CONTENT",
    )
    result = builder.build(req)
    assert result.source == "gateway"
    assert result.context == gateway.response
    assert len(gateway.calls) == 1
    call = gateway.calls[0]
    assert "<document>\nFULL_DOC_CONTENT\n</document>" in call["prompt"]
    assert "<chunk>\nCHUNK_CONTENT\n</chunk>" in call["prompt"]
    assert call["temperature"] == 0.0


def test_gateway_failure_falls_back_to_heuristic():
    class _FailingGateway:
        def generate(self, *_args, **_kwargs):
            raise RuntimeError("upstream failure")

    builder = ContextualChunkBuilder(gateway=_FailingGateway(), enabled=True)
    req = ContextualizationRequest(
        document="doc",
        chunk="chunk",
        metadata={"module": "fallback.test", "name": "f", "entity_type": "function"},
    )
    result = builder.build(req)
    assert result.source == "heuristic"
    assert "fallback.test" in result.context


def test_gateway_empty_response_falls_back_to_heuristic():
    class _EmptyGateway:
        def generate(self, *_args, **_kwargs):
            return ""

    builder = ContextualChunkBuilder(gateway=_EmptyGateway(), enabled=True)
    req = ContextualizationRequest(
        document="doc",
        chunk="chunk body.",
        metadata={"title": "Test Doc"},
    )
    result = builder.build(req)
    assert result.source == "heuristic"


def test_enabled_without_gateway_falls_back_to_heuristic():
    # Programming error path: enabled=True but no gateway wired
    builder = ContextualChunkBuilder(gateway=None, enabled=True)
    req = ContextualizationRequest(
        document="doc",
        chunk="chunk",
        metadata={"module": "m", "name": "n", "entity_type": "class"},
    )
    result = builder.build(req)
    assert result.source == "heuristic"


# ---------------------------------------------------------------------------
# Determinism & bounds
# ---------------------------------------------------------------------------


def test_heuristic_is_deterministic():
    builder = ContextualChunkBuilder(enabled=False)
    req = ContextualizationRequest(
        document="doc",
        chunk="x",
        metadata={"module": "a.b", "name": "fn", "entity_type": "function"},
    )
    r1 = builder.build(req)
    r2 = builder.build(req)
    assert r1.context == r2.context


def test_context_output_is_length_bounded():
    gateway = _StubGateway(response="x " * 500)  # 1000 chars
    builder = ContextualChunkBuilder(gateway=gateway, enabled=True)
    req = ContextualizationRequest(document="d", chunk="c")
    result = builder.build(req)
    assert len(result.context) <= 400
    assert result.context.endswith("...")


# ---------------------------------------------------------------------------
# prepend_context helper
# ---------------------------------------------------------------------------


def test_prepend_context_separates_with_blank_line():
    combined = prepend_context("chunk body", "This is the context.")
    assert combined == "This is the context.\n\nchunk body"


def test_prepend_context_noop_on_empty_context():
    assert prepend_context("chunk body", "") == "chunk body"


@pytest.mark.parametrize(
    "context,chunk,expected_prefix",
    [
        ("  padded  ", "body", "padded\n\nbody"),
        ("ctx", "  body  ", "ctx\n\n  body  "),
    ],
)
def test_prepend_context_strips_context_not_chunk(context, chunk, expected_prefix):
    assert prepend_context(chunk, context) == expected_prefix
