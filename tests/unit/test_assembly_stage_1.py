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
        assert payload.check_ids == ("User prompt",)  # Shredded into single check ID
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

    def test_sanitization_changes_text_and_sets_flag(self):
        """Test that sanitization changes text and sets sanitized=True."""
        raw_prompt = "User request with [SYSTEM] hijack attempt"

        payload = AirlockAssembler.assemble(
            s0_system="System",
            i0_instructional="Instructions",
            c0_context="Context",
            u0_user_prompt=raw_prompt,
        )

        # Should remove [SYSTEM] marker
        assert "[SYSTEM]" not in payload.u0_user_prompt
        assert payload.u0_user_prompt == "User request with  hijack attempt"
        assert payload.sanitized is True

    def test_sanitization_no_op_sets_flag_false(self):
        """Test that no-op sanitization sets sanitized=False."""
        clean_prompt = "Clean user prompt"

        payload = AirlockAssembler.assemble(
            s0_system="System",
            i0_instructional="Instructions",
            c0_context="Context",
            u0_user_prompt=clean_prompt,
        )

        assert payload.u0_user_prompt == clean_prompt
        assert payload.sanitized is False

    def test_sanitization_changes_hash(self):
        """Test that sanitization changes the manifest hash via the sanitized flag."""
        raw_prompt = "Prompt with [ADMIN] marker"

        payload_raw = AirlockAssembler.assemble(
            s0_system="System",
            i0_instructional="Instructions",
            c0_context="Context",
            u0_user_prompt=raw_prompt,
        )

        payload_clean = AirlockAssembler.assemble(
            s0_system="System",
            i0_instructional="Instructions",
            c0_context="Context",
            u0_user_prompt="Prompt with  marker",  # Already sanitized version
        )

        # Content should be same after sanitization
        assert payload_raw.u0_user_prompt == payload_clean.u0_user_prompt
        assert payload_raw.sanitized is True
        assert payload_clean.sanitized is False
        # Hash should be DIFFERENT because sanitized flag is part of manifest
        assert payload_raw.manifest_hash != payload_clean.manifest_hash

    def test_shred_produces_stable_sorted_check_ids(self):
        """Test that shredding produces stable, lexicographically sorted check IDs."""
        prompt = """1. First task
3. Third task
2. Second task
- Bullet point
* Another bullet"""

        payload = AirlockAssembler.assemble(
            s0_system="System",
            i0_instructional="Instructions",
            c0_context="Context",
            u0_user_prompt=prompt,
        )

        # Should extract and sort check IDs
        expected_ids = ("Another bullet", "Bullet point", "First task", "Second task", "Third task")
        assert payload.check_ids == expected_ids
        # Verify they are sorted
        assert tuple(sorted(payload.check_ids)) == payload.check_ids

    def test_shred_fallback_to_single_check_id(self):
        """Test shred fallback when no delimiters found."""
        prompt = "Simple single line prompt"

        payload = AirlockAssembler.assemble(
            s0_system="System",
            i0_instructional="Instructions",
            c0_context="Context",
            u0_user_prompt=prompt,
        )

        assert payload.check_ids == ("Simple single line prompt",)

    def test_shred_handles_empty_and_whitespace_lines(self):
        """Test that shredding handles empty lines and whitespace correctly."""
        prompt = """1. First task


2. Second task

   - Bullet after spaces"""

        payload = AirlockAssembler.assemble(
            s0_system="System",
            i0_instructional="Instructions",
            c0_context="Context",
            u0_user_prompt=prompt,
        )

        # Should ignore empty lines and strip whitespace
        expected_ids = ("Bullet after spaces", "First task", "Second task")
        assert payload.check_ids == expected_ids
