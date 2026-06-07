"""EQ-7 — provider-aware token counter.

Plan: ``docs/archive/windsurf/legacy-tree/plans/eq1-compiled-artifact-schema-d9a3e7.md``
ADR:  ADR-PROMPT-ASSEMBLY-002 §6 (provider-aware token accounting)
"""

from __future__ import annotations

import math

import pytest

from agentic_core.L2_execution.enforcement import _token_counter as tc
from agentic_core.L2_execution.enforcement._token_counter import (
    HEURISTIC_CHARS_PER_TOKEN_CLAUDE,
    HEURISTIC_CHARS_PER_TOKEN_GEMINI,
    HEURISTIC_CHARS_PER_TOKEN_OPENAI,
    count_tokens,
    count_tokens_for_messages,
)


# --------------------------------------------------------------------------
# Basic contract.
# --------------------------------------------------------------------------


class TestCountTokensContract:
    def test_empty_string_returns_zero(self) -> None:
        assert count_tokens("", "openai") == 0
        assert count_tokens("", "anthropic") == 0
        assert count_tokens("", "gemini") == 0

    def test_none_returns_zero(self) -> None:
        assert count_tokens(None, "openai") == 0  # type: ignore[arg-type]

    def test_never_raises_on_weird_provider(self) -> None:
        # Unknown providers fall back silently, never raise.
        assert count_tokens("hello", "proprietary-future-model") >= 1
        assert count_tokens("hello", "") >= 1
        assert count_tokens("hello", "   ") >= 1


# --------------------------------------------------------------------------
# Heuristic math.
# --------------------------------------------------------------------------


class TestHeuristics:
    def test_openai_heuristic_rounds_up(self) -> None:
        # Unknown provider falls back to the OpenAI-family heuristic.
        # 10 chars / 4 = 2.5 → ceil → 3 tokens.
        assert count_tokens("a" * 10, "unknown-provider") == 3

    def test_anthropic_heuristic_is_denser(self) -> None:
        text = "a" * 14
        fallback = count_tokens(text, "unknown-provider")  # 4-chars/token
        anthropic = count_tokens(text, "anthropic")  # 3.5-chars/token
        # Claude tokenizer is denser => estimate is HIGHER for same text.
        assert anthropic >= fallback
        assert anthropic == math.ceil(14 / HEURISTIC_CHARS_PER_TOKEN_CLAUDE)

    def test_gemini_uses_openai_heuristic(self) -> None:
        text = "a" * 16
        assert count_tokens(text, "gemini") == math.ceil(16 / HEURISTIC_CHARS_PER_TOKEN_GEMINI)

    def test_minimum_floor_is_one_for_any_nonempty(self) -> None:
        # 1 char under any provider MUST count as at least 1 token.
        for provider in ("openai", "anthropic", "gemini", "unknown"):
            assert count_tokens("a", provider) >= 1


# --------------------------------------------------------------------------
# Provider normalization.
# --------------------------------------------------------------------------


class TestProviderNormalization:
    @pytest.mark.parametrize(
        "alias",
        ["openai", "OpenAI", "OPENAI", "azure_openai", "azure-openai"],
    )
    def test_openai_aliases(self, alias: str) -> None:
        assert count_tokens("hello world", alias) >= 1

    @pytest.mark.parametrize(
        "alias",
        ["anthropic", "Anthropic", "claude", "claude-opus-4"],
    )
    def test_anthropic_aliases_use_claude_heuristic(self, alias: str) -> None:
        text = "a" * 21
        expected = math.ceil(21 / HEURISTIC_CHARS_PER_TOKEN_CLAUDE)
        assert count_tokens(text, alias) == expected

    @pytest.mark.parametrize("alias", ["gemini", "vertex_ai", "google-gemini"])
    def test_gemini_aliases(self, alias: str) -> None:
        text = "a" * 16
        assert count_tokens(text, alias) == math.ceil(16 / HEURISTIC_CHARS_PER_TOKEN_GEMINI)


# --------------------------------------------------------------------------
# OpenAI + tiktoken.
# --------------------------------------------------------------------------


class TestOpenAITiktoken:
    def test_uses_tiktoken_when_available(self, monkeypatch) -> None:
        """When tiktoken is present the count matches the encoder output."""
        pytest.importorskip("tiktoken")
        # Clear the encoder cache so our explicit model pull is fresh.
        tc._tiktoken_encoder.cache_clear()
        text = "hello world"
        out = count_tokens(text, "openai", model="gpt-4")
        # Tiktoken on "hello world" for cl100k_base-compatible models
        # yields 2 tokens, not the heuristic's ceil(11/4) = 3.
        assert out == 2

    def test_heuristic_fallback_when_tiktoken_missing(self, monkeypatch) -> None:
        """If the tiktoken import fails the heuristic path is used."""
        tc._tiktoken_encoder.cache_clear()
        # Force _tiktoken_encoder to behave as if tiktoken is missing.
        monkeypatch.setattr(tc, "_tiktoken_encoder", lambda model: None)
        text = "a" * 20
        assert count_tokens(text, "openai", model="gpt-4") == math.ceil(20 / HEURISTIC_CHARS_PER_TOKEN_OPENAI)

    def test_encoder_error_falls_back_to_heuristic(self, monkeypatch) -> None:
        """A tiktoken runtime error must not crash the caller."""

        class _BrokenEncoder:
            def encode(self, text: str) -> list[int]:
                raise ValueError("unencodable")

        tc._tiktoken_encoder.cache_clear()
        monkeypatch.setattr(tc, "_tiktoken_encoder", lambda model: _BrokenEncoder())
        text = "a" * 20
        assert count_tokens(text, "openai", model="gpt-4") == math.ceil(20 / HEURISTIC_CHARS_PER_TOKEN_OPENAI)


# --------------------------------------------------------------------------
# Messages-array helper.
# --------------------------------------------------------------------------


class TestCountTokensForMessages:
    def test_sums_message_contents(self) -> None:
        messages = [
            {"role": "system", "content": "a" * 12},
            {"role": "user", "content": "a" * 8},
        ]
        expected = count_tokens("a" * 12, "anthropic") + count_tokens("a" * 8, "anthropic")
        assert count_tokens_for_messages(messages, "anthropic") == expected

    def test_ignores_non_string_content(self) -> None:
        messages = [
            {"role": "system", "content": "hello"},
            {"role": "user", "content": None},  # type: ignore[dict-item]
            {"role": "tool", "content": {"json": "blob"}},  # type: ignore[dict-item]
        ]
        # Non-string content is silently skipped — never raises.
        assert count_tokens_for_messages(messages, "unknown-provider") >= 1

    def test_empty_list_returns_zero(self) -> None:
        assert count_tokens_for_messages([], "openai") == 0

    def test_ignores_non_dict_entries(self) -> None:
        messages = ["bare string", 42, None]  # type: ignore[list-item]
        assert count_tokens_for_messages(messages, "openai") == 0  # type: ignore[arg-type]
