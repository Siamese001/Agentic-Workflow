"""ADG-driven tests for embeddings/tokenization_adapter.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.embeddings.tokenization_adapter import TokenCountAdapter


class TestTokenCountAdapter:
    def test_count_tokens_returns_int(self):
        result = TokenCountAdapter.count_tokens("hello world foo", "gpt-4")
        assert isinstance(result, int)

    def test_count_tokens_empty_string(self):
        result = TokenCountAdapter.count_tokens("", "gpt-4")
        assert result == 0

    def test_count_tokens_single_word(self):
        result = TokenCountAdapter.count_tokens("hello", "gpt-4")
        assert result == 1

    def test_count_tokens_multiple_words(self):
        result = TokenCountAdapter.count_tokens("hello world", "gpt-4")
        assert result == 2

    def test_is_static_method(self):
        assert callable(TokenCountAdapter.count_tokens)
