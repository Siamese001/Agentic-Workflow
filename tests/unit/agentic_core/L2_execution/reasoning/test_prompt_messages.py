"""Unit tests for PromptMessages IR (phase RH2B.3).

Plan: prompt-reception-followups-a7b3c4.
"""

from __future__ import annotations

import pytest

from agentic_core.L2_execution.reasoning.compiled_artifact import (
    AuthorityLevel,
    AuthoritySlot,
    CompiledPromptArtifact,
)
from agentic_core.L2_execution.reasoning.prompt_messages import (
    PromptMessages,
    _parse_exemplar_turns,
)


@pytest.fixture()
def artifact() -> CompiledPromptArtifact:
    return CompiledPromptArtifact(
        trace_id="t-1",
        system_version_hash="h-1",
        final_system_string="SYS_BODY",
        final_user_string="USER_BODY",
        allowed_tools_schema=[],
        tokens=42,
        slots_used=["S0", "I0", "U0"],
        signature="",
    )


def test_from_artifact_without_slots_uses_flat_fallback(
    artifact: CompiledPromptArtifact,
) -> None:
    ir = PromptMessages.from_artifact(artifact)
    assert ir.slot_map == {"SYSTEM": "SYS_BODY", "USER": "USER_BODY"}
    assert ir.ordered_slots == ("S0", "I0", "U0")
    assert ir.exemplars == ()
    assert ir.metadata["trace_id"] == "t-1"
    assert ir.metadata["system_version_hash"] == "h-1"
    assert "provider_hint" not in ir.metadata


def test_from_artifact_with_provider_hint_normalized(
    artifact: CompiledPromptArtifact,
) -> None:
    ir = PromptMessages.from_artifact(artifact, provider_hint="Anthropic")
    assert ir.metadata["provider_hint"] == "anthropic"


def test_from_artifact_with_slots_keys_by_code(
    artifact: CompiledPromptArtifact,
) -> None:
    slots = {
        "S0": AuthoritySlot(
            slot_type="S0",
            content="ABSOLUTE",
            authority_level=AuthorityLevel.ABSOLUTE,
            source_layer="L0",
        ),
        "U0": AuthoritySlot(
            slot_type="U0",
            content="INTENT",
            authority_level=AuthorityLevel.ZERO,
            source_layer="L1",
        ),
    }
    ir = PromptMessages.from_artifact(artifact, slots=slots)
    assert ir.slot_map == {"S0": "ABSOLUTE", "U0": "INTENT"}
    # No synthetic SYSTEM/USER keys when slots provided.
    assert "SYSTEM" not in ir.slot_map
    assert "USER" not in ir.slot_map


def test_system_text_joins_system_authority_slots(
    artifact: CompiledPromptArtifact,
) -> None:
    slots = {
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
        "U0": AuthoritySlot(
            slot_type="U0",
            content="USER_ASK",
            authority_level=AuthorityLevel.ZERO,
            source_layer="L1",
        ),
    }
    ir = PromptMessages.from_artifact(artifact, slots=slots)
    # ordered_slots from artifact is ["S0", "I0", "U0"]; D0 is not in ordered
    # so it is filtered out. This is correct: PromptMessages respects the
    # canonical render order declared on the artifact.
    text = ir.system_text()
    assert "CONSTITUTION" in text
    assert "USER_ASK" not in text  # U0 is a user slot, not system


def test_user_text_prefers_u0_over_synthetic(
    artifact: CompiledPromptArtifact,
) -> None:
    slots = {
        "U0": AuthoritySlot(
            slot_type="U0",
            content="REAL_U0",
            authority_level=AuthorityLevel.ZERO,
            source_layer="L1",
        ),
    }
    ir = PromptMessages.from_artifact(artifact, slots=slots)
    assert ir.user_text() == "REAL_U0"


def test_user_text_falls_back_to_synthetic(
    artifact: CompiledPromptArtifact,
) -> None:
    ir = PromptMessages.from_artifact(artifact)
    assert ir.user_text() == "USER_BODY"


def test_to_flat_preserves_legacy_shape(artifact: CompiledPromptArtifact) -> None:
    ir = PromptMessages.from_artifact(artifact)
    system, user = ir.to_flat()
    assert system == "SYS_BODY"
    assert user == "USER_BODY"


def test_as_dict_is_plain_serializable(artifact: CompiledPromptArtifact) -> None:
    ir = PromptMessages.from_artifact(artifact)
    payload = ir.as_dict()
    assert isinstance(payload["slot_map"], dict)
    assert isinstance(payload["ordered_slots"], list)
    assert isinstance(payload["exemplars"], list)
    assert isinstance(payload["metadata"], dict)


def test_parse_exemplar_turns_two_turn_conversation() -> None:
    content = (
        "USER: What is 2+2?\n"
        "ASSISTANT: 4\n"
        "USER: And 3+3?\n"
        "ASSISTANT: 6\n"
    )
    turns = _parse_exemplar_turns(content)
    assert turns == (
        ("user", "What is 2+2?"),
        ("assistant", "4"),
        ("user", "And 3+3?"),
        ("assistant", "6"),
    )


def test_parse_exemplar_turns_empty_returns_empty_tuple() -> None:
    assert _parse_exemplar_turns("") == ()
    assert _parse_exemplar_turns("   ") == ()


def test_parse_exemplar_turns_unstructured_returns_empty() -> None:
    # No USER:/ASSISTANT: markers -> unparseable -> empty tuple
    assert _parse_exemplar_turns("just a free-form exemplar blob") == ()


def test_exemplars_populated_when_e0_slot_present(
    artifact: CompiledPromptArtifact,
) -> None:
    slots = {
        "E0": AuthoritySlot(
            slot_type="E0",
            content="USER: hi\nASSISTANT: hello",
            authority_level=AuthorityLevel.EXEMPLAR,
            source_layer="L2",
        ),
    }
    ir = PromptMessages.from_artifact(artifact, slots=slots)
    assert ir.exemplars == (("user", "hi"), ("assistant", "hello"))


def test_artifact_to_prompt_messages_roundtrip(
    artifact: CompiledPromptArtifact,
) -> None:
    """The convenience method on the artifact must produce an equivalent IR."""
    ir = artifact.to_prompt_messages(provider_hint="openai")
    assert isinstance(ir, PromptMessages)
    assert ir.metadata["provider_hint"] == "openai"
    assert ir.to_flat() == ("SYS_BODY", "USER_BODY")
