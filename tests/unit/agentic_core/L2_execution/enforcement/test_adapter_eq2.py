"""EQ-2 — provider-adapter extensions.

Covers the ADR-PROMPT-ASSEMBLY-001 Q2/Q3 surface that landed in EQ-2:

- OpenAI o-series adapter (developer-role D0, dropped M0, Formatting
  re-enabled marker).
- Anthropic long-context hoist + ``<document>`` multi-doc wrapping.
- OpenAI GPT-4.1 long-context tail ``# Final instructions`` block.
- Model-aware registry dispatch via ``get_adapter_for_model``.

Plan: ``.windsurf/plans/eq1-compiled-artifact-schema-d9a3e7.md``
ADR:  ``docs/architecture/adr/ADR-PROMPT-ASSEMBLY-001-provider-aware-structured-prompt-rendering.md``
"""

from __future__ import annotations

import os

import pytest

from agentic_core.L2_execution.enforcement._adapter_anthropic import (
    AnthropicMessageAdapter,
)
from agentic_core.L2_execution.enforcement._adapter_openai import (
    OpenAIMessageAdapter,
)
from agentic_core.L2_execution.enforcement._adapter_openai_oseries import (
    OSeriesMessageAdapter,
)
from agentic_core.L2_execution.enforcement._adapter_registry import (
    get_adapter,
    get_adapter_for_model,
)
from agentic_core.L2_execution.enforcement.SovereignLLMGateway import (
    ProviderType,
)


# --------------------------------------------------------------------------
# o-series adapter.
# --------------------------------------------------------------------------


class TestOSeriesAdapter:
    def test_developer_role_lifts_d0(self) -> None:
        adapter = OSeriesMessageAdapter()
        payload = adapter.render(
            final_system_string="",
            final_user_string="Solve x.",
            tools_schema=None,
            slots_used=["S0", "I0", "D0", "U0"],
            slots_map={
                "S0": "You are a reasoning model.",
                "I0": "Be precise.",
                "D0": "Never output code fences.",
                "U0": "ignored-by-adapter",
            },
        )
        assert payload.extra["adapter"] == "openai_oseries"
        # D0 content goes to the developer role, NOT the system markdown.
        assert payload.extra["developer_prompt"] == "Never output code fences."
        assert "Never output code fences." not in payload.system_prompt

    def test_m0_is_dropped_and_flagged(self) -> None:
        adapter = OSeriesMessageAdapter()
        payload = adapter.render(
            final_system_string="",
            final_user_string="Q.",
            tools_schema=None,
            slots_map={
                "S0": "Role",
                "I0": "Instructions",
                "M0": "Think step by step...",
            },
        )
        assert payload.extra["m0_dropped"] is True
        assert "Think step by step" not in payload.system_prompt

    def test_markdown_output_marker_prepends_formatting_re_enabled(self) -> None:
        adapter = OSeriesMessageAdapter()
        payload = adapter.render(
            final_system_string="",
            final_user_string="Q.",
            tools_schema=None,
            slots_map={
                "S0": "Role",
                "_markdown_output": "1",
            },
        )
        assert payload.system_prompt.startswith("Formatting re-enabled")

    def test_no_markdown_marker_no_prefix(self) -> None:
        adapter = OSeriesMessageAdapter()
        payload = adapter.render(
            final_system_string="",
            final_user_string="Q.",
            tools_schema=None,
            slots_map={"S0": "Role"},
        )
        assert not payload.system_prompt.startswith("Formatting re-enabled")

    def test_empty_d0_means_no_developer_role(self) -> None:
        adapter = OSeriesMessageAdapter()
        payload = adapter.render(
            final_system_string="",
            final_user_string="Q.",
            tools_schema=None,
            slots_map={"S0": "Role", "I0": "Instr"},
        )
        assert payload.extra["developer_prompt"] == ""


# --------------------------------------------------------------------------
# Anthropic long-context hoist + <document> wrapping.
# --------------------------------------------------------------------------


class TestAnthropicLongContextHoist:
    def test_short_c0_does_not_trigger_hoist(self) -> None:
        adapter = AnthropicMessageAdapter()
        payload = adapter.render(
            final_system_string="",
            final_user_string="Q.",
            tools_schema=None,
            slots_map={"S0": "Role", "I0": "Instr", "C0": "short context"},
        )
        assert payload.extra["long_context_hoisted"] is False

    def test_long_c0_triggers_hoist_and_tail_reminder(self, monkeypatch) -> None:
        # Lower the threshold to make the test cheap.
        monkeypatch.setenv("ANTHROPIC_LONG_CONTEXT_CHARS", "100")
        adapter = AnthropicMessageAdapter()
        big_c0 = "context-chunk " * 50  # > 100 chars
        payload = adapter.render(
            final_system_string="",
            final_user_string="Q.",
            tools_schema=None,
            slots_map={
                "S0": "You are helpful.",
                "I0": "Answer using the context only.",
                "C0": big_c0,
            },
        )
        assert payload.extra["long_context_hoisted"] is True
        # Context should appear before the instructions in the final system
        # string (hoist invariant).
        ctx_idx = payload.system_prompt.find("<context>")
        instr_idx = payload.system_prompt.find("<instructions>")
        assert ctx_idx != -1 and instr_idx != -1
        assert ctx_idx < instr_idx
        # Tail task_reminder appears at the end.
        assert "<task_reminder>" in payload.system_prompt
        assert payload.system_prompt.rstrip().endswith("</task_reminder>")

    def test_document_boundary_wraps_multi_doc_c0(self, monkeypatch) -> None:
        monkeypatch.setenv("ANTHROPIC_LONG_CONTEXT_CHARS", "50")
        adapter = AnthropicMessageAdapter()
        c0 = "first doc content\n---DOC---\nsecond doc content\n---DOC---\nthird doc content"
        # Pad to clear threshold.
        c0 = c0 + " " + ("x" * 100)
        payload = adapter.render(
            final_system_string="",
            final_user_string="Q.",
            tools_schema=None,
            slots_map={"S0": "Role", "I0": "Instr", "C0": c0},
        )
        sys = payload.system_prompt
        assert "<documents>" in sys
        assert '<document index="1">' in sys
        assert '<document index="2">' in sys
        assert '<document index="3">' in sys
        assert "<document_content>" in sys
        assert "</documents>" in sys


# --------------------------------------------------------------------------
# OpenAI long-context tail reminder.
# --------------------------------------------------------------------------


class TestOpenAIFinalInstructionsTail:
    def test_short_c0_no_tail(self) -> None:
        adapter = OpenAIMessageAdapter()
        payload = adapter.render(
            final_system_string="",
            final_user_string="Q.",
            tools_schema=None,
            slots_map={"S0": "Role", "I0": "Instr", "C0": "short"},
        )
        assert payload.extra["long_context_tail_reminder"] is False
        assert "# Final instructions" not in payload.system_prompt

    def test_long_c0_appends_final_instructions(self, monkeypatch) -> None:
        monkeypatch.setenv("OPENAI_LONG_CONTEXT_CHARS", "100")
        adapter = OpenAIMessageAdapter()
        big_c0 = "context-chunk " * 50
        payload = adapter.render(
            final_system_string="",
            final_user_string="Q.",
            tools_schema=None,
            slots_map={
                "S0": "Role",
                "I0": "Answer using context only.\nMore detail here.",
                "C0": big_c0,
            },
        )
        assert payload.extra["long_context_tail_reminder"] is True
        sys = payload.system_prompt
        assert sys.count("# Final instructions") == 1
        # Tail is last.
        assert sys.rstrip().endswith("Answer using context only.")

    def test_no_i0_means_no_tail_even_when_c0_long(self, monkeypatch) -> None:
        monkeypatch.setenv("OPENAI_LONG_CONTEXT_CHARS", "100")
        adapter = OpenAIMessageAdapter()
        big_c0 = "x" * 500
        payload = adapter.render(
            final_system_string="",
            final_user_string="Q.",
            tools_schema=None,
            slots_map={"S0": "Role", "C0": big_c0},  # no I0
        )
        assert payload.extra["long_context_tail_reminder"] is False


# --------------------------------------------------------------------------
# Registry — model-aware dispatch.
# --------------------------------------------------------------------------


class TestRegistryModelAwareDispatch:
    @pytest.mark.parametrize(
        "model_id", ["o1", "o1-preview", "o1-mini", "o3", "o3-pro", "o4", "o4-mini"]
    )
    def test_oseries_model_ids_route_to_oseries_adapter(
        self, model_id: str
    ) -> None:
        adapter = get_adapter_for_model(ProviderType.OPENAI, model_id)
        assert adapter.name == "openai_oseries"

    @pytest.mark.parametrize(
        "model_id", ["gpt-4.1", "gpt-4.1-mini", "gpt-4o", "gpt-4", "openai-compat"]
    )
    def test_non_oseries_openai_routes_to_default_adapter(
        self, model_id: str
    ) -> None:
        adapter = get_adapter_for_model(ProviderType.OPENAI, model_id)
        assert adapter.name == "openai"

    def test_azure_openai_oseries_routes_to_oseries(self) -> None:
        adapter = get_adapter_for_model(ProviderType.AZURE_OPENAI, "o3-pro")
        assert adapter.name == "openai_oseries"

    def test_anthropic_never_routes_to_oseries(self) -> None:
        # Even if someone named a Claude model "o1-like", Anthropic routes stay.
        adapter = get_adapter_for_model(ProviderType.ANTHROPIC, "o1-something")
        assert adapter.name == "anthropic"

    def test_none_model_id_falls_back_to_default(self) -> None:
        adapter = get_adapter_for_model(ProviderType.OPENAI, None)
        assert adapter.name == "openai"

    def test_get_adapter_still_works_without_model(self) -> None:
        # Back-compat: plain get_adapter() by provider_type unchanged.
        assert get_adapter(ProviderType.OPENAI).name == "openai"
        assert get_adapter(ProviderType.ANTHROPIC).name == "anthropic"
        assert get_adapter(ProviderType.VERTEX_AI).name == "gemini"
