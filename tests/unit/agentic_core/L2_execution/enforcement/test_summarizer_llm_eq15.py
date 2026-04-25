"""EQ-15 — LLM summarizer shim tests."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution.enforcement._history_summarizer_llm import (
    NullSummarizer,
    summarize_or_fallback,
    summarizer_enabled,
)


class TestFlag:
    def test_default_off(self, monkeypatch) -> None:
        monkeypatch.delenv("USE_LLM_SUMMARIZER", raising=False)
        assert summarizer_enabled() is False

    def test_on(self, monkeypatch) -> None:
        monkeypatch.setenv("USE_LLM_SUMMARIZER", "1")
        assert summarizer_enabled() is True


class TestNullSummarizer:
    def test_null_summarizer_is_deterministic(self) -> None:
        s = NullSummarizer()
        out1 = s.summarize([{"role": "user", "content": "hi"}])
        out2 = s.summarize([{"role": "user", "content": "hi"}])
        assert out1 == out2

    def test_null_summarizer_mentions_message_count(self) -> None:
        assert "2 message" in NullSummarizer().summarize(
            [{"role": "user", "content": "a"}, {"role": "user", "content": "b"}]
        )


class TestSummarizeOrFallback:
    def test_flag_off_returns_disabled_tag(self, monkeypatch) -> None:
        monkeypatch.delenv("USE_LLM_SUMMARIZER", raising=False)
        out = summarize_or_fallback([{"role": "user", "content": "hi"}])
        assert out == "[summarizer disabled]"

    def test_flag_on_uses_null_backend_by_default(self, monkeypatch) -> None:
        monkeypatch.setenv("USE_LLM_SUMMARIZER", "1")
        out = summarize_or_fallback([{"role": "user", "content": "hi"}])
        assert "1 message" in out

    def test_backend_exception_returns_fallback(self, monkeypatch) -> None:
        monkeypatch.setenv("USE_LLM_SUMMARIZER", "1")

        class _Broken:
            def summarize(self, messages: list[dict]) -> str:
                raise RuntimeError("boom")

        out = summarize_or_fallback(
            [{"role": "user", "content": "hi"}],
            summarizer=_Broken(),
            fallback="OOPS",
        )
        assert out == "OOPS"

    def test_custom_backend_passthrough(self, monkeypatch) -> None:
        monkeypatch.setenv("USE_LLM_SUMMARIZER", "1")

        class _Custom:
            def summarize(self, messages: list[dict]) -> str:
                return "CUSTOM"

        assert summarize_or_fallback([], summarizer=_Custom()) == "CUSTOM"
