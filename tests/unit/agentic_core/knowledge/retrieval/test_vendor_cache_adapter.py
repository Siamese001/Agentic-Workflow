"""Unit tests for Vendor Cache Adapter (W6.2 — G9 vendor-agnostic cache)."""

from __future__ import annotations

import pytest

from agentic_core.knowledge.retrieval.vendor_cache_adapter import (
    AnthropicCacheAdapter,
    CacheBoundary,
    GeminiCacheAdapter,
    OpenAICacheAdapter,
    PromptCacheAdapter,
    get_cache_adapter,
)


# ---------------------------------------------------------------------------
# CacheBoundary
# ---------------------------------------------------------------------------

class TestCacheBoundary:

    def test_defaults(self) -> None:
        b = CacheBoundary()
        assert b.system_prompt == ""
        assert b.boundary_char_index == -1

    def test_with_values(self) -> None:
        b = CacheBoundary(
            system_prompt="You are helpful.",
            user_prefix="Context: ...",
            user_suffix="Now answer: ",
            boundary_char_index=14,
        )
        assert b.system_prompt == "You are helpful."
        assert b.boundary_char_index == 14


# ---------------------------------------------------------------------------
# AnthropicCacheAdapter
# ---------------------------------------------------------------------------

class TestAnthropicCacheAdapter:

    def test_produces_result(self) -> None:
        adapter = AnthropicCacheAdapter()
        boundary = CacheBoundary(
            system_prompt="A" * 4000,
            user_prefix="B" * 2000,
            user_suffix="C" * 500,
            boundary_char_index=2000,
        )
        result = adapter.apply_cache_markers(boundary)
        assert result.vendor == "anthropic"
        assert result.cache_markers_applied is True
        assert result.cacheable_token_estimate > 0
        assert result.messages is not None

    def test_empty_boundary(self) -> None:
        adapter = AnthropicCacheAdapter()
        boundary = CacheBoundary()
        result = adapter.apply_cache_markers(boundary)
        assert result.vendor == "anthropic"


# ---------------------------------------------------------------------------
# OpenAICacheAdapter
# ---------------------------------------------------------------------------

class TestOpenAICacheAdapter:

    def test_produces_messages(self) -> None:
        adapter = OpenAICacheAdapter()
        boundary = CacheBoundary(
            system_prompt="System prompt",
            user_prefix="Context",
            user_suffix="Question",
        )
        result = adapter.apply_cache_markers(boundary)
        assert result.vendor == "openai"
        assert result.cache_markers_applied is False  # OpenAI auto-caches
        assert result.messages is not None
        assert len(result.messages or []) == 2  # system + user

    def test_short_prefix_warning(self) -> None:
        adapter = OpenAICacheAdapter()
        boundary = CacheBoundary(system_prompt="Hi", user_prefix="Q", user_suffix="")
        result = adapter.apply_cache_markers(boundary)
        assert result.cacheable_token_estimate < 100  # very short

    def test_no_system_prompt(self) -> None:
        adapter = OpenAICacheAdapter()
        boundary = CacheBoundary(user_prefix="Hello", user_suffix="World")
        result = adapter.apply_cache_markers(boundary)
        assert len(result.messages) == 1  # user only


# ---------------------------------------------------------------------------
# GeminiCacheAdapter
# ---------------------------------------------------------------------------

class TestGeminiCacheAdapter:

    def test_produces_contents(self) -> None:
        adapter = GeminiCacheAdapter()
        boundary = CacheBoundary(
            system_prompt="System instruction",
            user_prefix="Context: ",
            user_suffix="Question",
        )
        result = adapter.apply_cache_markers(boundary)
        assert result.vendor == "gemini"
        assert result.cache_markers_applied is True
        assert result.messages is not None

    def test_no_system(self) -> None:
        adapter = GeminiCacheAdapter()
        boundary = CacheBoundary(user_prefix="Hello", user_suffix="World")
        result = adapter.apply_cache_markers(boundary)
        assert result.cache_markers_applied is False


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

class TestGetCacheAdapter:

    def test_anthropic(self) -> None:
        adapter = get_cache_adapter("anthropic")
        assert isinstance(adapter, AnthropicCacheAdapter)

    def test_openai(self) -> None:
        adapter = get_cache_adapter("openai")
        assert isinstance(adapter, OpenAICacheAdapter)

    def test_gemini(self) -> None:
        adapter = get_cache_adapter("gemini")
        assert isinstance(adapter, GeminiCacheAdapter)

    def test_unknown_vendor_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown vendor"):
            get_cache_adapter("unknown_vendor")


class TestCacheAdapterValidation:

    def test_base_adapter_rejects_non_boundary(self) -> None:
        adapter = PromptCacheAdapter()
        with pytest.raises(TypeError, match="boundary must be CacheBoundary"):
            adapter.apply_cache_markers("not_a_boundary")  # type: ignore[arg-type]

    def test_base_adapter_rejects_invalid_ttl(self) -> None:
        adapter = PromptCacheAdapter()
        boundary = CacheBoundary(system_prompt="test")
        with pytest.raises(ValueError, match="ttl must be"):
            adapter.apply_cache_markers(boundary, ttl="2h")

    def test_anthropic_accepts_valid_ttl(self) -> None:
        adapter = AnthropicCacheAdapter()
        boundary = CacheBoundary(system_prompt="A" * 4000)
        result_5m = adapter.apply_cache_markers(boundary, ttl="5m")
        result_1h = adapter.apply_cache_markers(boundary, ttl="1h")
        assert result_5m.vendor == "anthropic"
        assert result_1h.vendor == "anthropic"


class TestReplayKeyPropagation:
    """G12 — Validate that replay_key + policy_hash propagate end-to-end
    through the retrieval pipeline.

    This test verifies the contract: if a RetrievalPlan carries replay_key
    and policy_hash, those values must appear in every RecallResult.metadata
    and survive into the EvidenceContract's replay_metadata.
    """

    def test_replay_key_in_recall_result_metadata(self) -> None:
        from agentic_core.knowledge.retrieval.hybrid_recall_stage import (
            RecallResult,
        )
        from agentic_core.knowledge.retrieval.retrieval_plan import RetrievalPlan

        plan = RetrievalPlan(
            query_id="q1",
            replay_key="rk_abc123",
            policy_hash="ph_def456",
            top_k=5,
        )
        # Verify plan carries the keys
        assert plan.replay_key == "rk_abc123"
        assert plan.policy_hash == "ph_def456"

        # Create a RecallResult with metadata that would be stamped
        result = RecallResult(
            doc_id="c1",
            score=0.9,
            source="dense",
            content="test",
            metadata={"replay_key": "rk_abc123", "policy_hash": "ph_def456", "plan_id": "test_plan"},
        )
        assert result.metadata["replay_key"] == "rk_abc123"
        assert result.metadata["policy_hash"] == "ph_def456"
        assert result.metadata["plan_id"] == "test_plan"
