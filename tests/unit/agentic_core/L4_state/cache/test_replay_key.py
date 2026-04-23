"""Tests for structured-slot replay-key digest (phase RH2B.1).

Plan: prompt-reception-followups-a7b3c4.
"""

from __future__ import annotations

from agentic_core.L2_execution.reasoning.compiled_artifact import (
    AuthorityLevel,
    AuthoritySlot,
    CompiledPromptArtifact,
)
from agentic_core.L4_state.cache.replay_key import (
    LEGACY_FLAT_PREFIX,
    SLOT_DIGEST_PREFIX,
    compute_slot_digest_key,
    is_legacy_flat_key,
    is_slot_digest_key,
    legacy_flat_key,
)


def _artifact() -> CompiledPromptArtifact:
    return CompiledPromptArtifact(
        trace_id="t-1",
        system_version_hash="h-1",
        final_system_string="SYS",
        final_user_string="USR",
        allowed_tools_schema=[],
        tokens=5,
        slots_used=["S0", "U0"],
        signature="",
    )


def test_slot_digest_key_is_scheme_prefixed() -> None:
    artifact = _artifact()
    ir = artifact.to_prompt_messages()
    key = compute_slot_digest_key(ir)
    assert key.startswith(SLOT_DIGEST_PREFIX)
    assert is_slot_digest_key(key)
    assert not is_legacy_flat_key(key)


def test_legacy_flat_key_is_scheme_prefixed() -> None:
    key = legacy_flat_key("SYS", "USR")
    assert key.startswith(LEGACY_FLAT_PREFIX)
    assert is_legacy_flat_key(key)
    assert not is_slot_digest_key(key)


def test_slot_digest_deterministic_for_same_slot_map() -> None:
    artifact = _artifact()
    k1 = compute_slot_digest_key(artifact.to_prompt_messages())
    k2 = compute_slot_digest_key(artifact.to_prompt_messages())
    assert k1 == k2


def test_slot_digest_key_insensitive_to_slot_code_case() -> None:
    """Slot codes are canonicalized to upper-case before hashing."""
    artifact = _artifact()
    slots_upper = {
        "S0": AuthoritySlot(
            slot_type="S0",
            content="ABS",
            authority_level=AuthorityLevel.ABSOLUTE,
            source_layer="L0",
        ),
        "U0": AuthoritySlot(
            slot_type="U0",
            content="ASK",
            authority_level=AuthorityLevel.ZERO,
            source_layer="L1",
        ),
    }
    slots_lower = {
        "s0": AuthoritySlot(
            slot_type="S0",
            content="ABS",
            authority_level=AuthorityLevel.ABSOLUTE,
            source_layer="L0",
        ),
        "u0": AuthoritySlot(
            slot_type="U0",
            content="ASK",
            authority_level=AuthorityLevel.ZERO,
            source_layer="L1",
        ),
    }
    k_upper = compute_slot_digest_key(
        artifact.to_prompt_messages(slots=slots_upper)
    )
    k_lower = compute_slot_digest_key(
        artifact.to_prompt_messages(slots=slots_lower)
    )
    assert k_upper == k_lower


def test_slot_digest_differs_when_slot_content_changes() -> None:
    artifact_a = CompiledPromptArtifact(
        trace_id="t-1",
        system_version_hash="h-1",
        final_system_string="SYS_A",
        final_user_string="USR",
        allowed_tools_schema=[],
        tokens=0,
        slots_used=[],
        signature="",
    )
    artifact_b = CompiledPromptArtifact(
        trace_id="t-1",
        system_version_hash="h-1",
        final_system_string="SYS_B",
        final_user_string="USR",
        allowed_tools_schema=[],
        tokens=0,
        slots_used=[],
        signature="",
    )
    assert compute_slot_digest_key(
        artifact_a.to_prompt_messages()
    ) != compute_slot_digest_key(artifact_b.to_prompt_messages())


def test_slot_digest_ignores_trailing_whitespace() -> None:
    """Trailing whitespace is semantically irrelevant -> same key."""
    artifact_clean = CompiledPromptArtifact(
        trace_id="t-1",
        system_version_hash="h-1",
        final_system_string="SYS",
        final_user_string="USR",
        allowed_tools_schema=[],
        tokens=0,
        slots_used=[],
        signature="",
    )
    artifact_trailing = CompiledPromptArtifact(
        trace_id="t-1",
        system_version_hash="h-1",
        final_system_string="SYS   \n",
        final_user_string="USR\t ",
        allowed_tools_schema=[],
        tokens=0,
        slots_used=[],
        signature="",
    )
    k_clean = compute_slot_digest_key(artifact_clean.to_prompt_messages())
    k_trail = compute_slot_digest_key(artifact_trailing.to_prompt_messages())
    assert k_clean == k_trail


def test_slot_digest_differs_from_legacy_key_for_same_content() -> None:
    """The two schemes MUST produce different keys to avoid mid-migration collisions."""
    artifact = _artifact()
    ir = artifact.to_prompt_messages()
    slot_key = compute_slot_digest_key(ir)
    flat_key = legacy_flat_key(
        artifact.final_system_string, artifact.final_user_string
    )
    assert slot_key != flat_key


def test_is_slot_digest_key_rejects_non_strings() -> None:
    assert is_slot_digest_key("") is False
    assert is_slot_digest_key(123) is False  # type: ignore[arg-type]


def test_is_legacy_flat_key_rejects_non_strings() -> None:
    assert is_legacy_flat_key("") is False
    assert is_legacy_flat_key(None) is False  # type: ignore[arg-type]
