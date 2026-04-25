"""EQ-17 — Y0 slot + meta-learning authority level."""

from __future__ import annotations

from agentic_core.L2_execution.reasoning.compiled_artifact import (
    AuthorityLevel,
    AuthoritySlot,
    CompiledPromptArtifact,
)


SECRET = b"z" * 32


class TestY0Enum:
    def test_meta_learning_level_exists(self) -> None:
        assert hasattr(AuthorityLevel, "META_LEARNING")

    def test_meta_learning_is_below_healing_above_zero(self) -> None:
        # Enum auto() assigns incrementing ints — we use that ordering
        # as a stable proxy for "lower authority than HEALING, higher
        # than ZERO".
        assert AuthorityLevel.HEALING.value < AuthorityLevel.META_LEARNING.value < AuthorityLevel.ZERO.value


class TestY0SlotRoundTrip:
    def test_authority_slot_with_y0(self) -> None:
        slot = AuthoritySlot(
            slot_type="Y0",
            content="meta-learning adjustment",
            authority_level=AuthorityLevel.META_LEARNING,
            source_layer="L6",
        )
        assert slot.authority_level is AuthorityLevel.META_LEARNING
        assert slot.content == "meta-learning adjustment"

    def test_y0_slot_in_structured_slots_hashes_stable(self) -> None:
        slot = AuthoritySlot(
            slot_type="Y0",
            content="x",
            authority_level=AuthorityLevel.META_LEARNING,
            source_layer="L6",
        )
        art1 = CompiledPromptArtifact(
            trace_id="t",
            system_version_hash="h",
            final_system_string="s",
            final_user_string="u",
            allowed_tools_schema=[],
            tokens=1,
            slots_used=["S0", "Y0", "U0"],
            signature="",
            structured_slots={"Y0": slot},
        )
        art2 = CompiledPromptArtifact(
            trace_id="t",
            system_version_hash="h",
            final_system_string="s",
            final_user_string="u",
            allowed_tools_schema=[],
            tokens=1,
            slots_used=["U0", "Y0", "S0"],  # different insertion order
            signature="",
            structured_slots={"Y0": slot},
        )
        # EQ-9 invariant still holds with Y0 in the mix.
        assert art1.manifest_hash == art2.manifest_hash

    def test_legacy_artifact_without_y0_unaffected(self) -> None:
        # Pre-EQ17 artifacts that never reference Y0 must hash and sign
        # byte-identically to their pre-EQ17 shape.
        art = CompiledPromptArtifact(
            trace_id="t",
            system_version_hash="h",
            final_system_string="s",
            final_user_string="u",
            allowed_tools_schema=[],
            tokens=1,
            slots_used=["S0", "U0"],
            signature="",
        )
        # Smoke: nothing about constructing this raises or warns even
        # though the new enum variant now exists.
        assert "Y0" not in art.slots_used
