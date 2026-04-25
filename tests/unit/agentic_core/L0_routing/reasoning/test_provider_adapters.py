"""PA.6 provider adapter tests — Anthropic / OpenAI / Gemini / Passthrough."""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.reasoning.provider_adapters import (
    AnthropicAdapter,
    GeminiAdapter,
    OpenAIAdapter,
    PassthroughAdapter,
    RenderedPrompt,
    get_adapter,
    render_for_provider,
)


@pytest.fixture
def basic_slots() -> dict[str, str]:
    return {
        "S0": "You are a careful assistant.",
        "D0": "Do not invent facts.",
        "I0": "Use the provided context.",
        "C0": "Earth orbits the Sun.",
        "M0": "Think step by step.",
        "E0": "<example>...</example>",
        "Y0": "no_tools",
        "R0": '{"type": "object"}',
        "U0": "What does Earth orbit?",
        "H0": "",
    }


# ----- AnthropicAdapter ----------------------------------------------------


class TestAnthropicAdapter:
    def test_renders_xml_tags_for_system_slots(self, basic_slots):
        result = AnthropicAdapter().render(basic_slots)
        assert isinstance(result, RenderedPrompt)
        assert result.provider == "anthropic"
        assert "<identity>" in result.system
        assert "<domain_constraints>" in result.system
        assert "<instructions>" in result.system

    def test_c0_wrapped_in_documents_when_no_existing_tags(self, basic_slots):
        result = AnthropicAdapter().render(basic_slots)
        assert "<documents>" in result.system
        assert "<document " in result.system
        assert "Earth orbits the Sun." in result.system

    def test_c0_passthrough_when_documents_already_present(self):
        slots = {
            "S0": "x",
            "C0": "<documents><document index='1'>pre-wrapped</document></documents>",
            "U0": "q",
        }
        result = AnthropicAdapter().render(slots)
        # Should not double-wrap
        assert result.system.count("<documents>") == 1
        assert "pre-wrapped" in result.system

    def test_h0_renders_in_user_plane(self, basic_slots):
        slots = {**basic_slots, "H0": "Heal: retry with smaller scope."}
        result = AnthropicAdapter().render(slots)
        assert "<healing_reentry>" in result.user
        assert "What does Earth orbit?" in result.user

    def test_h0_alone_when_u0_empty(self):
        slots = {"S0": "x", "U0": "", "H0": "heal text"}
        result = AnthropicAdapter().render(slots)
        assert result.user == "heal text"

    def test_empty_slots_skipped(self):
        slots = {"S0": "ident", "D0": "", "I0": "  ", "U0": "u"}
        result = AnthropicAdapter().render(slots)
        assert "<identity>" in result.system
        assert "<domain_constraints>" not in result.system
        assert "<instructions>" not in result.system

    def test_deterministic_rendering(self, basic_slots):
        a = AnthropicAdapter().render(basic_slots)
        b = AnthropicAdapter().render(basic_slots)
        assert a.system == b.system
        assert a.user == b.user

    def test_rendered_chars_matches_payload(self, basic_slots):
        result = AnthropicAdapter().render(basic_slots)
        assert result.rendered_chars == len(result.system) + len(result.user)


# ----- OpenAIAdapter -------------------------------------------------------


class TestOpenAIAdapter:
    def test_gpt_family_uses_system_role(self, basic_slots):
        result = OpenAIAdapter(model_family="gpt-4").render(basic_slots)
        assert result.provider == "openai"
        roles = [m["role"] for m in result.messages]
        assert "system" in roles
        assert "user" in roles
        assert "developer" not in roles

    def test_o_series_uses_developer_role(self, basic_slots):
        result = OpenAIAdapter(model_family="o-series").render(basic_slots)
        roles = [m["role"] for m in result.messages]
        assert "developer" in roles
        assert "system" not in roles

    def test_o_series_with_markdown_prepends_formatting_header(self, basic_slots):
        result = OpenAIAdapter(model_family="o-series", markdown_output=True).render(basic_slots)
        dev_msg = next((m for m in result.messages if m["role"] == "developer"), None)
        assert dev_msg is not None
        # The dev message bundle should contain the marker for o-series with md
        bundle = "\n".join(m["content"] for m in result.messages if m["role"] == "developer")
        assert "Formatting re-enabled" in bundle

    def test_markdown_section_headers(self, basic_slots):
        result = OpenAIAdapter().render(basic_slots)
        # Combined system text should have markdown sections
        assert "## Domain Constraints" in result.system
        assert "## Instructions" in result.system
        assert "## Output Format" in result.system

    def test_user_message_contains_u0(self, basic_slots):
        result = OpenAIAdapter().render(basic_slots)
        user_msgs = [m for m in result.messages if m["role"] == "user"]
        assert len(user_msgs) == 1
        assert "Earth" in user_msgs[0]["content"]

    def test_h0_appended_to_user(self):
        slots = {"S0": "x", "U0": "user q", "H0": "heal"}
        result = OpenAIAdapter().render(slots)
        user_msgs = [m for m in result.messages if m["role"] == "user"]
        assert "heal" in user_msgs[0]["content"]

    def test_empty_s0_drops_identity_message(self):
        slots = {"S0": "", "D0": "rule", "U0": "q"}
        result = OpenAIAdapter().render(slots)
        # Only system (with D0) and user — no identity-only message
        contents = [m["content"] for m in result.messages]
        assert all("rule" not in c or "## Domain Constraints" in c for c in contents)

    def test_deterministic_rendering(self, basic_slots):
        a = OpenAIAdapter().render(basic_slots)
        b = OpenAIAdapter().render(basic_slots)
        assert a.messages == b.messages


# ----- GeminiAdapter -------------------------------------------------------


class TestGeminiAdapter:
    def test_renders_markdown_sections(self, basic_slots):
        result = GeminiAdapter().render(basic_slots)
        assert result.provider == "gemini"
        assert "## Identity" in result.system
        assert "## Constraints" in result.system
        assert "## Context" in result.system

    def test_u0_alone_when_no_h0(self, basic_slots):
        result = GeminiAdapter().render(basic_slots)
        assert result.user == "What does Earth orbit?"

    def test_h0_renders_as_section(self):
        slots = {"S0": "x", "U0": "q", "H0": "heal"}
        result = GeminiAdapter().render(slots)
        assert "## Healing Re-entry" in result.user
        assert "heal" in result.user

    def test_deterministic_rendering(self, basic_slots):
        a = GeminiAdapter().render(basic_slots)
        b = GeminiAdapter().render(basic_slots)
        assert a.system == b.system


# ----- PassthroughAdapter --------------------------------------------------


class TestPassthroughAdapter:
    def test_passthrough_concats_with_double_newline(self, basic_slots):
        result = PassthroughAdapter().render(basic_slots)
        assert result.provider == "passthrough"
        # No XML, no markdown headers
        assert "<identity>" not in result.system
        assert "## Identity" not in result.system

    def test_legacy_h0_user_format_preserved(self):
        slots = {"S0": "x", "U0": "q", "H0": "heal"}
        result = PassthroughAdapter().render(slots)
        assert "<H0>" in result.user


# ----- Factory & registry --------------------------------------------------


class TestGetAdapter:
    def test_none_returns_passthrough(self):
        assert isinstance(get_adapter(None), PassthroughAdapter)
        assert isinstance(get_adapter(""), PassthroughAdapter)

    def test_anthropic_aliases(self):
        assert isinstance(get_adapter("anthropic"), AnthropicAdapter)
        assert isinstance(get_adapter("claude"), AnthropicAdapter)
        assert isinstance(get_adapter("claude-3.5-sonnet"), AnthropicAdapter)

    def test_openai_aliases(self):
        a1 = get_adapter("openai")
        a2 = get_adapter("gpt-4")
        a3 = get_adapter("o1")
        assert isinstance(a1, OpenAIAdapter)
        assert isinstance(a2, OpenAIAdapter)
        assert isinstance(a3, OpenAIAdapter)
        # o-series should auto-detect
        assert a3.model_family == "o-series"
        assert a2.model_family == "gpt-4"

    def test_gemini_aliases(self):
        assert isinstance(get_adapter("gemini"), GeminiAdapter)
        assert isinstance(get_adapter("google"), GeminiAdapter)

    def test_unknown_provider_falls_back_to_passthrough(self):
        assert isinstance(get_adapter("mystery-llm"), PassthroughAdapter)


class TestRenderForProvider:
    def test_convenience_wrapper(self, basic_slots):
        result = render_for_provider(basic_slots, provider="claude")
        assert result.provider == "anthropic"

    def test_passthrough_default(self, basic_slots):
        result = render_for_provider(basic_slots)
        assert result.provider == "passthrough"
