"""EQ-13 — Gemini adapter polish tests (long-context marker)."""

from __future__ import annotations

from agentic_core.L2_execution.enforcement._adapter_gemini import (
    GeminiMessageAdapter,
)


class TestLongContextMarker:
    def test_short_c0_leaves_long_context_false(self) -> None:
        payload = GeminiMessageAdapter().render(
            final_system_string="",
            final_user_string="u",
            tools_schema=None,
            slots_map={"S0": "r", "C0": "short-context"},
        )
        assert payload.extra["long_context"] is False

    def test_long_c0_sets_long_context_true(self, monkeypatch) -> None:
        monkeypatch.setenv("GEMINI_LONG_CONTEXT_CHARS", "20")
        payload = GeminiMessageAdapter().render(
            final_system_string="",
            final_user_string="u",
            tools_schema=None,
            slots_map={"S0": "r", "C0": "x" * 50},
        )
        assert payload.extra["long_context"] is True

    def test_anthropic_env_fallback_honored(self, monkeypatch) -> None:
        monkeypatch.delenv("GEMINI_LONG_CONTEXT_CHARS", raising=False)
        monkeypatch.setenv("ANTHROPIC_LONG_CONTEXT_CHARS", "30")
        payload = GeminiMessageAdapter().render(
            final_system_string="",
            final_user_string="u",
            tools_schema=None,
            slots_map={"S0": "r", "C0": "x" * 50},
        )
        assert payload.extra["long_context"] is True

    def test_no_slots_map_does_not_crash(self) -> None:
        payload = GeminiMessageAdapter().render(
            final_system_string="flat-system",
            final_user_string="u",
            tools_schema=None,
        )
        # Passthrough path still populates long_context=False (safe default).
        assert payload.extra["long_context"] is False
