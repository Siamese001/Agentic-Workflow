"""EQ-8 — deterministic history compressor tests."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution.enforcement._history_compressor import (
    compress_history,
    compression_enabled,
)


def _msg(role: str, content: str) -> dict:
    return {"role": role, "content": content}


class TestFeatureFlag:
    def test_default_off_passes_through(self, monkeypatch) -> None:
        monkeypatch.delenv("USE_DETERMINISTIC_EVICTION", raising=False)
        messages = [_msg("user", "a" * 1000)]
        # budget_tokens=1 would evict but the flag is off, so passthrough.
        assert compress_history(
            messages, budget_tokens=1, provider="openai"
        ) == messages

    def test_flag_on_respects_budget(self, monkeypatch) -> None:
        monkeypatch.setenv("USE_DETERMINISTIC_EVICTION", "1")
        messages = [_msg("user", "a" * 1000)]
        out = compress_history(messages, budget_tokens=1, provider="openai")
        # 1000 chars / ~4 chars-per-token => well over 1. Message evicted.
        assert out == []

    def test_force_bypasses_flag(self, monkeypatch) -> None:
        monkeypatch.delenv("USE_DETERMINISTIC_EVICTION", raising=False)
        messages = [_msg("user", "a" * 1000)]
        out = compress_history(
            messages, budget_tokens=1, provider="openai", force=True
        )
        assert out == []


class TestDeterminism:
    def test_same_input_yields_identical_output(self, monkeypatch) -> None:
        monkeypatch.setenv("USE_DETERMINISTIC_EVICTION", "1")
        messages = [
            _msg("system", "you are helpful"),
            _msg("user", "a" * 40),
            _msg("assistant", "b" * 40),
            _msg("user", "c" * 40),
        ]
        first = compress_history(messages, budget_tokens=15, provider="openai")
        second = compress_history(messages, budget_tokens=15, provider="openai")
        assert first == second


class TestEvictionOrder:
    def test_oldest_first_eviction(self, monkeypatch) -> None:
        monkeypatch.setenv("USE_DETERMINISTIC_EVICTION", "1")
        # Use an unknown provider so count_tokens uses the deterministic
        # 4-chars/token heuristic — tiktoken on repeated chars would
        # underestimate and skew the test. Each message here is 40 chars
        # = 10 tokens under the heuristic.
        messages = [
            _msg("user", "oldest" + "x" * 34),  # idx 0, evictable
            _msg("user", "middle" + "y" * 34),  # idx 1, evictable
            _msg("user", "newest" + "z" * 34),  # idx 2, evictable
        ]
        # Budget 25 fits exactly 2 messages (20 tokens) then blocks.
        out = compress_history(
            messages, budget_tokens=25, provider="unknown-heuristic"
        )
        contents = [m["content"] for m in out]
        assert all(not c.startswith("oldest") for c in contents)
        assert any(c.startswith("middle") for c in contents)
        assert any(c.startswith("newest") for c in contents)

    def test_system_messages_never_evicted(self, monkeypatch) -> None:
        monkeypatch.setenv("USE_DETERMINISTIC_EVICTION", "1")
        messages = [
            _msg("system", "s" * 4000),
            _msg("user", "u" * 40),
        ]
        out = compress_history(messages, budget_tokens=5, provider="openai")
        # System stays even though it blows the budget; user gets cut.
        assert any(m.get("role") == "system" for m in out)

    def test_zero_budget_evicts_all_non_system(self, monkeypatch) -> None:
        monkeypatch.setenv("USE_DETERMINISTIC_EVICTION", "1")
        messages = [
            _msg("system", "sys"),
            _msg("user", "hello"),
            _msg("assistant", "hi"),
        ]
        out = compress_history(messages, budget_tokens=0, provider="openai")
        assert [m["role"] for m in out] == ["system"]


class TestInputSafety:
    def test_does_not_mutate_input(self, monkeypatch) -> None:
        monkeypatch.setenv("USE_DETERMINISTIC_EVICTION", "1")
        messages = [_msg("user", "a" * 100)]
        snapshot = [dict(m) for m in messages]
        compress_history(messages, budget_tokens=1, provider="openai")
        assert messages == snapshot

    def test_negative_budget_raises(self) -> None:
        with pytest.raises(ValueError, match="budget_tokens"):
            compress_history([], budget_tokens=-1, provider="openai")

    def test_non_dict_entries_pass_through(self, monkeypatch) -> None:
        monkeypatch.setenv("USE_DETERMINISTIC_EVICTION", "1")
        messages = [_msg("system", "s"), "stray string", _msg("user", "u")]
        # Stray entries count as 0 tokens and are preserved in position.
        out = compress_history(messages, budget_tokens=100, provider="openai")
        assert "stray string" in out


class TestCompressionEnabled:
    def test_flag_on(self, monkeypatch) -> None:
        monkeypatch.setenv("USE_DETERMINISTIC_EVICTION", "1")
        assert compression_enabled() is True

    def test_flag_off(self, monkeypatch) -> None:
        monkeypatch.delenv("USE_DETERMINISTIC_EVICTION", raising=False)
        assert compression_enabled() is False
