"""Tests for GeminiClient (phase RH8B.1).

Plan: prompt-reception-followups-a7b3c4. Uses dependency-injected mock
model factories so no network / credentials are required.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

from agentic_core.L2_execution.reasoning.compiled_artifact import (
    AuthorityLevel,
    AuthoritySlot,
    CompiledPromptArtifact,
)
from infrastructure.sdks_mcps.gemini_client import (
    DEFAULT_GEMINI_MODEL,
    GeminiClient,
    GeminiResponse,
    GeminiStreamChunk,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _artifact() -> CompiledPromptArtifact:
    return CompiledPromptArtifact(
        trace_id="t-1",
        system_version_hash="h-1",
        final_system_string="SYSTEM_FLAT",
        final_user_string="USER_FLAT",
        allowed_tools_schema=[],
        tokens=0,
        slots_used=["S0", "U0"],
        signature="",
    )


def _rich_slots() -> dict[str, AuthoritySlot]:
    return {
        "S0": AuthoritySlot(
            slot_type="S0",
            content="CONSTITUTION",
            authority_level=AuthorityLevel.ABSOLUTE,
            source_layer="L0",
        ),
        "D0": AuthoritySlot(
            slot_type="D0",
            content="FENCE",
            authority_level=AuthorityLevel.BINDING,
            source_layer="L5",
        ),
        "E0": AuthoritySlot(
            slot_type="E0",
            content="USER: hi\nASSISTANT: hello",
            authority_level=AuthorityLevel.EXEMPLAR,
            source_layer="L2",
        ),
        "U0": AuthoritySlot(
            slot_type="U0",
            content="WHAT_IS_42",
            authority_level=AuthorityLevel.ZERO,
            source_layer="L1",
        ),
    }


class _MockModel:
    """Captures generate_content calls for assertion."""

    def __init__(self, response: Any) -> None:
        self.response = response
        self.calls: list[dict[str, Any]] = []

    def generate_content(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        return self.response


def _mock_response(
    text: str = "OK",
    prompt_tokens: int | None = 10,
    output_tokens: int | None = 3,
    finish_reason: Any = "STOP",
) -> SimpleNamespace:
    usage = (
        SimpleNamespace(
            prompt_token_count=prompt_tokens,
            candidates_token_count=output_tokens,
        )
        if prompt_tokens is not None or output_tokens is not None
        else None
    )
    candidate = SimpleNamespace(finish_reason=finish_reason) if finish_reason else None
    return SimpleNamespace(
        text=text,
        usage_metadata=usage,
        candidates=[candidate] if candidate else [],
    )


# ---------------------------------------------------------------------------
# Projection tests (no SDK required)
# ---------------------------------------------------------------------------


def test_project_flat_fallback_uses_synthetic_system_and_user() -> None:
    ir = _artifact().to_prompt_messages()
    request = GeminiClient.project(ir)
    assert request["system_instruction"] == "SYSTEM_FLAT"
    assert request["contents"] == [{"role": "user", "parts": ["USER_FLAT"]}]


def test_project_rich_slots_joins_system_authority_and_includes_exemplars() -> None:
    ir = _artifact().to_prompt_messages(slots=_rich_slots())
    request = GeminiClient.project(ir)

    # S0, I0, D0, C0, M0, H0 are the system codes; only S0 + D0 present here.
    # Canonical order: S0, I0, D0, C0, M0, H0 (from _SYSTEM_INSTRUCTION_CODES).
    assert request["system_instruction"] == "CONSTITUTION\n\nFENCE"

    # E0 produces leading exemplar turns, then the final user U0 turn.
    assert request["contents"] == [
        {"role": "user", "parts": ["hi"]},
        {"role": "model", "parts": ["hello"]},
        {"role": "user", "parts": ["WHAT_IS_42"]},
    ]


def test_project_handles_missing_user_turn() -> None:
    artifact = CompiledPromptArtifact(
        trace_id="t-1",
        system_version_hash="",
        final_system_string="S",
        final_user_string="",
        allowed_tools_schema=[],
        tokens=0,
        slots_used=[],
        signature="",
    )
    ir = artifact.to_prompt_messages()
    request = GeminiClient.project(ir)
    assert request["contents"] == []
    assert request["system_instruction"] == "S"


# ---------------------------------------------------------------------------
# send() + response parsing
# ---------------------------------------------------------------------------


def test_send_returns_typed_response_with_token_counts_and_finish_reason() -> None:
    mock_model = _MockModel(_mock_response(text="42"))
    client = GeminiClient(model_factory=lambda name: mock_model)
    ir = _artifact().to_prompt_messages()

    resp = client.send(ir, temperature=0.2)

    assert isinstance(resp, GeminiResponse)
    assert resp.text == "42"
    assert resp.prompt_tokens == 10
    assert resp.output_tokens == 3
    assert resp.finish_reason == "STOP"
    assert resp.metadata["trace_id"] == "t-1"


def test_send_forwards_generation_config() -> None:
    mock_model = _MockModel(_mock_response())
    client = GeminiClient(model_factory=lambda name: mock_model)
    ir = _artifact().to_prompt_messages()

    client.send(ir, temperature=0.7, max_output_tokens=100)

    assert len(mock_model.calls) == 1
    call = mock_model.calls[0]
    assert call["generation_config"] == {"temperature": 0.7, "max_output_tokens": 100}
    assert call["contents"] == [{"role": "user", "parts": ["USER_FLAT"]}]
    assert call["system_instruction"] == "SYSTEM_FLAT"


def test_send_passes_none_system_instruction_when_empty() -> None:
    mock_model = _MockModel(_mock_response())
    client = GeminiClient(model_factory=lambda name: mock_model)
    artifact = CompiledPromptArtifact(
        trace_id="t-1",
        system_version_hash="",
        final_system_string="",
        final_user_string="U",
        allowed_tools_schema=[],
        tokens=0,
        slots_used=[],
        signature="",
    )
    client.send(artifact.to_prompt_messages())
    assert mock_model.calls[0]["system_instruction"] is None


def test_send_lazily_constructs_model_once() -> None:
    construct_count = 0

    def factory(name: str) -> _MockModel:
        nonlocal construct_count
        construct_count += 1
        return _MockModel(_mock_response())

    client = GeminiClient(model_factory=factory)
    ir = _artifact().to_prompt_messages()

    client.send(ir)
    client.send(ir)

    assert construct_count == 1  # model cached across sends


def test_enum_finish_reason_stringified() -> None:
    class _FinishEnum:
        name = "MAX_TOKENS"

    mock_model = _MockModel(_mock_response(finish_reason=_FinishEnum()))
    client = GeminiClient(model_factory=lambda name: mock_model)
    resp = client.send(_artifact().to_prompt_messages())
    assert resp.finish_reason == "MAX_TOKENS"


def test_missing_usage_metadata_returns_none_counts() -> None:
    mock_model = _MockModel(_mock_response(prompt_tokens=None, output_tokens=None))
    client = GeminiClient(model_factory=lambda name: mock_model)
    resp = client.send(_artifact().to_prompt_messages())
    assert resp.prompt_tokens is None
    assert resp.output_tokens is None


def test_default_model_name_is_flash() -> None:
    assert DEFAULT_GEMINI_MODEL == "gemini-2.5-flash"
    client = GeminiClient()
    assert client.model_name == DEFAULT_GEMINI_MODEL


def test_from_env_uses_create_gemini_model(monkeypatch: pytest.MonkeyPatch) -> None:
    """from_env delegates to infrastructure.sdks_mcps.create_gemini_model."""
    mock_model = _MockModel(_mock_response())

    def fake_factory(name: str) -> Any:
        return mock_model

    monkeypatch.setattr("infrastructure.sdks_mcps.create_gemini_model", fake_factory)
    client = GeminiClient.from_env("gemini-2.5-pro")
    assert client.model_name == "gemini-2.5-pro"
    # Trigger lazy model resolution.
    client.send(_artifact().to_prompt_messages())
    assert mock_model.calls


# ---------------------------------------------------------------------------
# PRF2.B3 — tool-use schema projection
# ---------------------------------------------------------------------------


def test_project_tools_groups_declarations_under_single_block() -> None:
    """PRF2.B3: Cursor Agent tool-schema list projects to Gemini's single
    ``function_declarations`` block shape."""
    cascade_tools = [
        {
            "name": "search_web",
            "description": "Search the web.",
            "parameters": {"type": "object", "properties": {"q": {"type": "string"}}},
        },
        {
            "name": "read_file",
            "description": "Read a file.",
            "parameters": {"type": "object", "properties": {"path": {"type": "string"}}},
        },
    ]
    projected = GeminiClient.project_tools(cascade_tools)
    assert len(projected) == 1
    assert "function_declarations" in projected[0]
    decls = projected[0]["function_declarations"]
    assert [d["name"] for d in decls] == ["search_web", "read_file"]
    assert decls[0]["parameters"]["properties"]["q"]["type"] == "string"


def test_project_tools_drops_unnamed_and_non_dict_entries() -> None:
    """PRF2.B3: malformed tool entries (missing name, wrong type) are dropped."""
    projected = GeminiClient.project_tools(
        [
            {"name": "ok", "description": "fine"},
            {"description": "no name"},  # dropped
            "not a dict",  # dropped
            {"name": "", "description": "empty name"},  # dropped
        ],
    )
    assert len(projected) == 1
    decls = projected[0]["function_declarations"]
    assert [d["name"] for d in decls] == ["ok"]


def test_project_tools_accepts_input_schema_alias() -> None:
    """PRF2.B3: anthropic-style ``input_schema`` field is accepted as
    a fallback for ``parameters`` so adapters can share a schema shape."""
    projected = GeminiClient.project_tools(
        [{"name": "t", "input_schema": {"type": "object"}}],
    )
    decls = projected[0]["function_declarations"]
    assert decls[0]["parameters"] == {"type": "object"}


def test_project_tools_returns_empty_when_all_invalid() -> None:
    """PRF2.B3: empty input or all-dropped returns empty list (no empty
    ``function_declarations`` block sent to Gemini)."""
    assert GeminiClient.project_tools([]) == []
    assert GeminiClient.project_tools([{"bogus": 1}]) == []


def test_send_includes_tools_when_schema_provided() -> None:
    """PRF2.B3: ``send(allowed_tools_schema=...)`` forwards projected
    tools on the SDK call."""
    mock_model = _MockModel(_mock_response())
    client = GeminiClient(model_factory=lambda name: mock_model)
    ir = _artifact().to_prompt_messages()

    client.send(
        ir,
        allowed_tools_schema=[{"name": "foo", "description": "bar"}],
    )
    call = mock_model.calls[0]
    assert "tools" in call
    assert call["tools"][0]["function_declarations"][0]["name"] == "foo"


def test_send_omits_tools_when_no_schema_provided() -> None:
    """PRF2.B3: absent tool schema must NOT set ``tools`` kwarg
    (unnecessary arg would alter SDK semantics)."""
    mock_model = _MockModel(_mock_response())
    client = GeminiClient(model_factory=lambda name: mock_model)
    ir = _artifact().to_prompt_messages()

    client.send(ir)
    assert "tools" not in mock_model.calls[0]


# ---------------------------------------------------------------------------
# PRF2.B3 — streaming
# ---------------------------------------------------------------------------


class _MockStreamingModel:
    """Mock that returns a list/iterator of chunk objects."""

    def __init__(self, chunks: list[Any]) -> None:
        self.chunks = chunks
        self.calls: list[dict[str, Any]] = []

    def generate_content(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        return iter(self.chunks)


def _chunk(text: str, finish_reason: Any = None) -> SimpleNamespace:
    candidates = [SimpleNamespace(finish_reason=finish_reason)] if finish_reason else []
    return SimpleNamespace(text=text, candidates=candidates)


def test_send_stream_yields_typed_chunks_in_order() -> None:
    """PRF2.B3: streaming yields ``GeminiStreamChunk`` per SDK delta,
    preserving order and surfacing finish_reason on terminal chunk."""
    mock_model = _MockStreamingModel(
        [
            _chunk("The "),
            _chunk("answer "),
            _chunk("is 42.", finish_reason="STOP"),
        ]
    )
    client = GeminiClient(model_factory=lambda name: mock_model)
    ir = _artifact().to_prompt_messages()

    chunks = list(client.send_stream(ir, temperature=0.5))

    assert len(chunks) == 3
    assert all(isinstance(c, GeminiStreamChunk) for c in chunks)
    assert [c.text for c in chunks] == ["The ", "answer ", "is 42."]
    # finish_reason only on the terminal chunk.
    assert chunks[0].finish_reason is None
    assert chunks[1].finish_reason is None
    assert chunks[2].finish_reason == "STOP"


def test_send_stream_passes_stream_true_and_generation_config() -> None:
    """PRF2.B3: ``stream=True`` forwarded to SDK; generation_config honored."""
    mock_model = _MockStreamingModel([_chunk("done", finish_reason="STOP")])
    client = GeminiClient(model_factory=lambda name: mock_model)
    ir = _artifact().to_prompt_messages()

    list(client.send_stream(ir, temperature=0.1))

    call = mock_model.calls[0]
    assert call["stream"] is True
    assert call["generation_config"] == {"temperature": 0.1}


def test_send_stream_stringifies_enum_finish_reason() -> None:
    """PRF2.B3: SDK enum finish_reason is normalized to its ``.name``
    the same way ``send()`` does."""

    class _FinishEnum:
        name = "MAX_TOKENS"

    mock_model = _MockStreamingModel([_chunk("x", finish_reason=_FinishEnum())])
    client = GeminiClient(model_factory=lambda name: mock_model)
    ir = _artifact().to_prompt_messages()

    chunks = list(client.send_stream(ir))
    assert chunks[0].finish_reason == "MAX_TOKENS"


def test_send_stream_forwards_tools_schema() -> None:
    """PRF2.B3: tool schema is projected+forwarded during streaming too."""
    mock_model = _MockStreamingModel([_chunk("hi", finish_reason="STOP")])
    client = GeminiClient(model_factory=lambda name: mock_model)
    ir = _artifact().to_prompt_messages()

    list(
        client.send_stream(
            ir,
            allowed_tools_schema=[{"name": "tool_x"}],
        ),
    )
    call = mock_model.calls[0]
    assert call["tools"][0]["function_declarations"][0]["name"] == "tool_x"
