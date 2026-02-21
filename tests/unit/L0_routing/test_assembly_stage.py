"""
Unit tests for Assembly Stage - GAP-03 Implementation.
Tests deterministic composition and manifest hashing.
"""

import pytest

from agentic_core.L0_routing.engines.assembly_stage import AirlockAssembler, GovernedPayload


@pytest.mark.unit
class TestAssemblyStage:
    """Test Suite for Assembly Stage deterministic composition."""

    def test_assemble_creates_governed_payload(self):
        """Test that assemble creates a valid GovernedPayload."""
        payload = AirlockAssembler.assemble(
            s0_system="System prompt",
            i0_instructional="Instructions",
            c0_context="Context",
            u0_user_prompt="User prompt",
        )

        assert isinstance(payload, GovernedPayload)
        assert payload.s0_system == "System prompt"
        assert payload.i0_instructional == "Instructions"
        assert payload.c0_context == "Context"
        assert payload.u0_user_prompt == "User prompt"
        assert payload.d0_injections == ""
        assert payload.sanitized is False
        assert payload.check_ids == ()
        assert payload.manifest_hash != ""

    def test_same_inputs_produce_identical_manifest_hash(self):
        """Test deterministic hashing - same inputs produce same hash."""
        payload1 = AirlockAssembler.assemble(
            s0_system="System",
            i0_instructional="Instructions",
            c0_context="Context",
            u0_user_prompt="User",
        )

        payload2 = AirlockAssembler.assemble(
            s0_system="System",
            i0_instructional="Instructions",
            c0_context="Context",
            u0_user_prompt="User",
        )

        assert payload1.manifest_hash == payload2.manifest_hash

    def test_changing_any_slot_changes_manifest_hash(self):
        """Test that changing any slot changes the manifest hash."""
        base_payload = AirlockAssembler.assemble(
            s0_system="System",
            i0_instructional="Instructions",
            c0_context="Context",
            u0_user_prompt="User",
        )

        # Test each slot change
        test_cases = [
            {"s0_system": "Changed System"},
            {"d0_injections": "Injection"},
            {"i0_instructional": "Changed Instructions"},
            {"c0_context": "Changed Context"},
            {"u0_user_prompt": "Changed User"},
        ]

        for change in test_cases:
            # Build arguments with the change applied
            args = {
                "s0_system": "System",
                "i0_instructional": "Instructions",
                "c0_context": "Context",
                "u0_user_prompt": "User",
            }
            args.update(change)

            modified_payload = AirlockAssembler.assemble(**args)
            assert modified_payload.manifest_hash != base_payload.manifest_hash

    def test_manifest_hash_is_sha256_hex(self):
        """Test that manifest hash is a valid SHA256 hex string."""
        payload = AirlockAssembler.assemble(
            s0_system="System",
            i0_instructional="Instructions",
            c0_context="Context",
            u0_user_prompt="User",
        )

        # SHA256 hex should be 64 characters of hex
        assert len(payload.manifest_hash) == 64
        assert all(c in "0123456789abcdef" for c in payload.manifest_hash.lower())

    def test_payload_is_immutable(self):
        """Test that GovernedPayload is frozen/immutable."""
        payload = AirlockAssembler.assemble(
            s0_system="System",
            i0_instructional="Instructions",
            c0_context="Context",
            u0_user_prompt="User",
        )

        # Attempting to modify should fail
        with pytest.raises((AttributeError, TypeError)):  # Frozen dataclass errors
            payload.s0_system = "Changed"

    def test_d0_injections_default_and_custom(self):
        """Test d0_injections slot behavior."""
        # Default empty
        payload1 = AirlockAssembler.assemble(
            s0_system="S",
            i0_instructional="I",
            c0_context="C",
            u0_user_prompt="U",
        )
        assert payload1.d0_injections == ""

        # Custom value
        payload2 = AirlockAssembler.assemble(
            s0_system="S",
            d0_injections="Injection",
            i0_instructional="I",
            c0_context="C",
            u0_user_prompt="U",
        )
        assert payload2.d0_injections == "Injection"
        assert payload2.manifest_hash != payload1.manifest_hash
