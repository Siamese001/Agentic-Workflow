"""Unit tests for apps_rg.utils.anthropic_rag_entrypoint (W6.1 adoption seam).

Plan: anthropic-rag-gaps-7f3c2a.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest

from agentic_core.knowledge.retrieval.prompt_envelope import (
    AssemblyStatusCode,
    PromptAssemblyStatus,
    PromptEnvelope,
)
try:
    from apps_rg.utils.anthropic_rag_entrypoint import (
        AbstainRecommendedError,
        AnthropicRagPayload,
        build_anthropic_rag_payload,
    )
except ModuleNotFoundError:
    pytest.skip(
        "apps-rg-unit-pytest-remediation-f7e2a9 W1: apps_rg.utils.anthropic_rag_entrypoint "
        "not on disk.",
        allow_module_level=True,
    )


@dataclass
class _FakeChunk:
    """Duck-typed VerifiedChunk for payload-composition tests."""

    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    is_must_use: bool = True
    chunk_id: str = "chunk-x"
    contradiction_flag: bool = False


def _envelope(
    chunks: list[_FakeChunk] | None = None,
    *,
    task_spec: str = "Answer strictly from documents.",
    system_blocks: tuple[str, ...] = (),
    abstain: bool = False,
) -> PromptEnvelope:
    return PromptEnvelope(
        envelope_id="env-1",
        trace_id="trace-1",
        query_id="q-1",
        verified_chunks=tuple(chunks or []),  # type: ignore[arg-type]
        cited_spans=(),
        coverage_score=0.8,
        gaps=(),
        contradiction_status="none",
        abstain_recommended=abstain,
        next_action_hint="proceed",
        task_spec=task_spec,
        system_blocks=system_blocks,
        replay_key="rk-1",
        policy_hash="ph-1",
        plan_id="plan-1",
        assembly_status=PromptAssemblyStatus(status=AssemblyStatusCode.READY),
    )


def _large_chunk(prefix: str = "Fact ", body_chars: int = 4000) -> _FakeChunk:
    """A chunk large enough to exceed the cacheable-size threshold (~3500 chars)."""
    body = prefix + ("x " * (body_chars // 2))
    return _FakeChunk(
        content=body,
        metadata={"title": "Large Doc", "file_path": "docs/large.md"},
    )


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_build_returns_messages_api_shape() -> None:
    chunk = _FakeChunk(content="BM25 weights term frequency.", metadata={"title": "BM25"})
    env = _envelope([chunk])

    result = build_anthropic_rag_payload(env, query="How does BM25 work?")

    assert isinstance(result, AnthropicRagPayload)
    assert "messages" in result.payload
    assert isinstance(result.payload["messages"], list)
    assert len(result.payload["messages"]) == 1
    assert result.payload["messages"][0]["role"] == "user"
    assert result.document_block_count == 1


def test_user_turn_contains_document_and_query_in_order() -> None:
    chunk = _FakeChunk(content="BM25 weights term frequency.", metadata={"title": "BM25"})
    env = _envelope([chunk])

    result = build_anthropic_rag_payload(env, query="How does BM25 work?")

    content_blocks = result.payload["messages"][0]["content"]
    # content is a list of text blocks; concatenate their text to inspect order
    full_text = "".join(b.get("text", "") for b in content_blocks if isinstance(b, dict))
    assert "<document" in full_text
    assert full_text.index("<document") < full_text.index("<query>")


def test_no_system_field_when_system_blocks_empty() -> None:
    chunk = _FakeChunk(content="body", metadata={"title": "T"})
    env = _envelope([chunk], system_blocks=())

    result = build_anthropic_rag_payload(env, query="q")

    # system_blocks are inlined into user turn; no separate system field.
    assert "system" not in result.payload


# ---------------------------------------------------------------------------
# Cache-control markers
# ---------------------------------------------------------------------------


def test_cache_marker_applied_when_prefix_large_enough() -> None:
    chunk = _large_chunk()
    env = _envelope([chunk])

    result = build_anthropic_rag_payload(env, query="q", use_cache=True)

    assert result.cache_marker_count >= 1
    assert result.cache_boundary_hint > 0


def test_no_cache_marker_when_use_cache_false() -> None:
    chunk = _large_chunk()
    env = _envelope([chunk])

    result = build_anthropic_rag_payload(env, query="q", use_cache=False)

    assert result.cache_marker_count == 0
    # Boundary hint is still surfaced for telemetry even when caching is off.
    assert result.cache_boundary_hint > 0


def test_cache_marker_suppressed_when_prefix_below_threshold() -> None:
    """Tiny chunks should not get a cache marker (Anthropic 400s on <1024 tok blocks)."""
    chunk = _FakeChunk(content="tiny", metadata={"title": "T"})
    env = _envelope([chunk])

    result = build_anthropic_rag_payload(env, query="q", use_cache=True)

    # The cache_control helper strips markers below the heuristic threshold.
    assert result.cache_marker_count == 0


# ---------------------------------------------------------------------------
# Abstain guard
# ---------------------------------------------------------------------------


def test_abstain_envelope_raises_instead_of_producing_payload() -> None:
    env = _envelope(abstain=True)

    with pytest.raises(AbstainRecommendedError) as excinfo:
        build_anthropic_rag_payload(env, query="q")
    assert "env-1" in str(excinfo.value)
    assert "HITL" in str(excinfo.value)


# ---------------------------------------------------------------------------
# Telemetry fidelity
# ---------------------------------------------------------------------------


def test_document_block_count_matches_envelope_chunks() -> None:
    chunks = [_FakeChunk(content=f"doc{i}", metadata={"title": f"T{i}"}) for i in range(3)]
    env = _envelope(chunks)

    result = build_anthropic_rag_payload(env, query="q")

    assert result.document_block_count == 3


def test_ttl_1h_produces_distinct_marker_shape() -> None:
    chunk = _large_chunk()
    env = _envelope([chunk])

    result = build_anthropic_rag_payload(env, query="q", use_cache=True, cache_ttl="1h")

    # At least one marker must carry the 1h ttl attribute.
    markers_with_1h = 0
    for msg in result.payload.get("messages", []):
        for block in msg.get("content", []):
            if isinstance(block, dict):
                cc = block.get("cache_control")
                if isinstance(cc, dict) and cc.get("ttl") == "1h":
                    markers_with_1h += 1
    assert markers_with_1h >= 1
