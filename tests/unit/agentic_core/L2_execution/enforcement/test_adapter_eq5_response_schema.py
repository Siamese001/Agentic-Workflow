"""EQ-5 — response_schema threading through provider adapters.

Plan: ``docs/archive/windsurf/legacy-tree/plans/eq1-compiled-artifact-schema-d9a3e7.md``
ADR:  ADR-PROMPT-ASSEMBLY-001 Q4 (response-schema threading)

Verifies the structured-output config landing on ``ProviderPayload.extra``
is provider-idiomatic for each adapter:

| Adapter | Extra key(s) emitted |
|---|---|
| OpenAI GPT      | ``response_format`` (json_schema, strict=True)   |
| OpenAI o-series | ``response_format`` (json_schema, strict=True)   |
| Anthropic       | ``forced_tool_use`` (synthetic ``emit_response``) |
| Gemini          | ``response_mime_type`` + ``response_schema``      |

Also covers:
- Back-compat: ``response_schema=None`` (the default) leaves the
  provider-specific keys ABSENT from extra — old callers see no churn.
- Identity preservation: schemas are passed through, not deep-copied or
  mutated, so callers can detect no-op cases via ``is`` comparisons.
"""

from __future__ import annotations

import pytest

from agentic_core.L2_execution.enforcement._adapter_anthropic import (
    AnthropicMessageAdapter,
)
from agentic_core.L2_execution.enforcement._adapter_gemini import (
    GeminiMessageAdapter,
)
from agentic_core.L2_execution.enforcement._adapter_openai import (
    OpenAIMessageAdapter,
)
from agentic_core.L2_execution.enforcement._adapter_openai_oseries import (
    OSeriesMessageAdapter,
)


SAMPLE_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "answer": {"type": "string"},
        "confidence": {"type": "number"},
    },
    "required": ["answer", "confidence"],
    "additionalProperties": False,
}


# --------------------------------------------------------------------------
# OpenAI GPT — response_format json_schema.
# --------------------------------------------------------------------------


class TestOpenAIResponseSchema:
    def test_emits_response_format_json_schema(self) -> None:
        payload = OpenAIMessageAdapter().render(
            final_system_string="s",
            final_user_string="u",
            tools_schema=None,
            response_schema=SAMPLE_SCHEMA,
        )
        rf = payload.extra["response_format"]
        assert rf["type"] == "json_schema"
        assert rf["json_schema"]["name"] == "Response"
        assert rf["json_schema"]["strict"] is True
        # Schema must be passed by reference — no defensive copy.
        assert rf["json_schema"]["schema"] is SAMPLE_SCHEMA

    def test_response_schema_none_omits_response_format(self) -> None:
        payload = OpenAIMessageAdapter().render(
            final_system_string="s",
            final_user_string="u",
            tools_schema=None,
            response_schema=None,
        )
        assert "response_format" not in payload.extra

    def test_default_call_omits_response_format(self) -> None:
        # Pre-EQ5 callers don't pass response_schema at all.
        payload = OpenAIMessageAdapter().render(
            final_system_string="s",
            final_user_string="u",
            tools_schema=None,
        )
        assert "response_format" not in payload.extra


# --------------------------------------------------------------------------
# OpenAI o-series — response_format json_schema (same wire shape).
# --------------------------------------------------------------------------


class TestOSeriesResponseSchema:
    def test_emits_response_format_json_schema(self) -> None:
        payload = OSeriesMessageAdapter().render(
            final_system_string="s",
            final_user_string="u",
            tools_schema=None,
            response_schema=SAMPLE_SCHEMA,
        )
        rf = payload.extra["response_format"]
        assert rf["type"] == "json_schema"
        assert rf["json_schema"]["strict"] is True
        assert rf["json_schema"]["schema"] is SAMPLE_SCHEMA

    def test_response_schema_none_omits_response_format(self) -> None:
        payload = OSeriesMessageAdapter().render(
            final_system_string="s",
            final_user_string="u",
            tools_schema=None,
        )
        assert "response_format" not in payload.extra


# --------------------------------------------------------------------------
# Anthropic — forced tool use with synthetic emit_response tool.
# --------------------------------------------------------------------------


class TestAnthropicResponseSchema:
    def test_emits_forced_tool_use_block(self) -> None:
        payload = AnthropicMessageAdapter().render(
            final_system_string="s",
            final_user_string="u",
            tools_schema=None,
            response_schema=SAMPLE_SCHEMA,
        )
        forced = payload.extra["forced_tool_use"]
        assert forced["tool"]["name"] == "emit_response"
        # Schema becomes the tool's input_schema — same reference.
        assert forced["tool"]["input_schema"] is SAMPLE_SCHEMA
        # Tool choice forces Anthropic to emit exactly this tool.
        assert forced["tool_choice"] == {
            "type": "tool",
            "name": "emit_response",
        }

    def test_response_schema_none_omits_forced_tool_use(self) -> None:
        payload = AnthropicMessageAdapter().render(
            final_system_string="s",
            final_user_string="u",
            tools_schema=None,
        )
        assert "forced_tool_use" not in payload.extra


# --------------------------------------------------------------------------
# Gemini — response_mime_type + response_schema.
# --------------------------------------------------------------------------


class TestGeminiResponseSchema:
    def test_emits_response_mime_type_and_schema(self) -> None:
        payload = GeminiMessageAdapter().render(
            final_system_string="s",
            final_user_string="u",
            tools_schema=None,
            response_schema=SAMPLE_SCHEMA,
        )
        assert payload.extra["response_mime_type"] == "application/json"
        assert payload.extra["response_schema"] is SAMPLE_SCHEMA

    def test_response_schema_none_omits_both_keys(self) -> None:
        payload = GeminiMessageAdapter().render(
            final_system_string="s",
            final_user_string="u",
            tools_schema=None,
        )
        assert "response_mime_type" not in payload.extra
        assert "response_schema" not in payload.extra


# --------------------------------------------------------------------------
# Cross-adapter back-compat invariants.
# --------------------------------------------------------------------------


class TestCrossAdapterBackCompat:
    @pytest.mark.parametrize(
        "adapter",
        [
            AnthropicMessageAdapter(),
            OpenAIMessageAdapter(),
            OSeriesMessageAdapter(),
            GeminiMessageAdapter(),
        ],
        ids=["anthropic", "openai", "oseries", "gemini"],
    )
    def test_pre_eq5_call_signature_still_works(self, adapter) -> None:
        # Old callers do not pass response_schema. Adapter must accept
        # the unchanged kwargs and produce a payload — no TypeError.
        payload = adapter.render(
            final_system_string="s",
            final_user_string="u",
            tools_schema=None,
            slots_used=["S0"],
            slots_map=None,
        )
        assert payload.system_prompt == "s"
        assert payload.user_prompt == "u"

    @pytest.mark.parametrize(
        "adapter",
        [
            AnthropicMessageAdapter(),
            OpenAIMessageAdapter(),
            OSeriesMessageAdapter(),
            GeminiMessageAdapter(),
        ],
        ids=["anthropic", "openai", "oseries", "gemini"],
    )
    def test_response_schema_does_not_mutate_input(self, adapter) -> None:
        schema_in = {"type": "object", "properties": {"x": {"type": "string"}}}
        snapshot = dict(schema_in)
        adapter.render(
            final_system_string="s",
            final_user_string="u",
            tools_schema=None,
            response_schema=schema_in,
        )
        # Adapter must not mutate the caller's schema dict in place.
        assert schema_in == snapshot


# --------------------------------------------------------------------------
# Artifact threading (CompiledPromptArtifact carries the schema).
# --------------------------------------------------------------------------


class TestArtifactThreading:
    def test_artifact_accepts_response_schema_field(self) -> None:
        from agentic_core.L2_execution.reasoning.compiled_artifact import (
            CompiledPromptArtifact,
        )

        artifact = CompiledPromptArtifact(
            trace_id="t",
            system_version_hash="h",
            final_system_string="s",
            final_user_string="u",
            allowed_tools_schema=[],
            tokens=1,
            slots_used=["S0"],
            signature="",
            response_schema=SAMPLE_SCHEMA,
        )
        assert artifact.response_schema is SAMPLE_SCHEMA

    def test_response_schema_defaults_to_none(self) -> None:
        from agentic_core.L2_execution.reasoning.compiled_artifact import (
            CompiledPromptArtifact,
        )

        artifact = CompiledPromptArtifact(
            trace_id="t",
            system_version_hash="h",
            final_system_string="s",
            final_user_string="u",
            allowed_tools_schema=[],
            tokens=1,
            slots_used=["S0"],
            signature="",
        )
        assert artifact.response_schema is None

    def test_response_schema_does_not_change_manifest_hash(self) -> None:
        # Two artifacts identical except for response_schema MUST hash the
        # same — schema is request metadata, not prompt content. Replay
        # determinism depends on this.
        from agentic_core.L2_execution.reasoning.compiled_artifact import (
            CompiledPromptArtifact,
        )

        base = CompiledPromptArtifact(
            trace_id="t",
            system_version_hash="h",
            final_system_string="hello",
            final_user_string="world",
            allowed_tools_schema=[],
            tokens=2,
            slots_used=["S0", "U0"],
            signature="",
        )
        with_schema = CompiledPromptArtifact(
            trace_id="t",
            system_version_hash="h",
            final_system_string="hello",
            final_user_string="world",
            allowed_tools_schema=[],
            tokens=2,
            slots_used=["S0", "U0"],
            signature="",
            response_schema=SAMPLE_SCHEMA,
        )
        assert base.manifest_hash == with_schema.manifest_hash
