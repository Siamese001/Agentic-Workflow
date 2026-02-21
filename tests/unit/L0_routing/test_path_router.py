"""
Unit tests for L0 Path Router - deterministic path selection.
"""

import pytest

from agentic_core.L0_routing.engines.assembly_stage import AirlockAssembler, GovernedPayload
from agentic_core.L0_routing.engines.path_router import Path, PathRouter


@pytest.mark.unit
class TestPathRouter:
    """Test deterministic PathRouter implementation."""

    def test_path_enum_values(self):
        """Test Path enum has correct values."""
        assert Path.A.value == "A"
        assert Path.B.value == "B"
        assert Path.C.value == "C"
        assert Path.D.value == "D"

    def test_empty_check_ids_selects_path_a(self):
        """Test empty check_ids always selects Path.A."""
        payload = GovernedPayload(
            s0_system="System",
            i0_instructional="Instructions",
            c0_context="Context",
            u0_user_prompt="Simple prompt",
            check_ids=(),  # Empty tuple
            sanitized=False,
            d0_injections="",
        )

        router = PathRouter()
        selected = router.select_path(payload)

        assert selected == Path.A

    def test_sanitized_payload_selects_path_b(self):
        """Test sanitized payload selects Path.B."""
        payload = AirlockAssembler.assemble(
            s0_system="System",
            i0_instructional="Instructions",
            c0_context="Context",
            u0_user_prompt="Prompt with [ADMIN] marker",
        )

        # Verify payload is sanitized
        assert payload.sanitized is True
        assert payload.check_ids  # Non-empty to avoid Path.A

        router = PathRouter()
        selected = router.select_path(payload)

        assert selected == Path.B

    def test_single_check_id_selects_path_c(self):
        """Test single check_id selects Path.C."""
        payload = AirlockAssembler.assemble(
            s0_system="System",
            i0_instructional="Instructions",
            c0_context="Context",
            u0_user_prompt="Single task prompt",
        )

        # Verify single check_id and not sanitized
        assert len(payload.check_ids) == 1
        assert payload.sanitized is False

        router = PathRouter()
        selected = router.select_path(payload)

        assert selected == Path.C

    def test_multiple_check_ids_selects_path_d(self):
        """Test multiple check_ids selects Path.D."""
        prompt = """1. First task
2. Second task
3. Third task"""

        payload = AirlockAssembler.assemble(
            s0_system="System", i0_instructional="Instructions", c0_context="Context", u0_user_prompt=prompt
        )

        # Verify multiple check_ids and not sanitized
        assert len(payload.check_ids) > 1
        assert payload.sanitized is False

        router = PathRouter()
        selected = router.select_path(payload)

        assert selected == Path.D

    def test_deterministic_selection_identical_payloads(self):
        """Test identical payloads produce identical path selection."""
        payload_args = {
            "s0_system": "System",
            "i0_instructional": "Instructions",
            "c0_context": "Context",
            "u0_user_prompt": "Test prompt",
        }

        payload1 = AirlockAssembler.assemble(**payload_args)
        payload2 = AirlockAssembler.assemble(**payload_args)

        router = PathRouter()
        path1 = router.select_path(payload1)
        path2 = router.select_path(payload2)

        assert path1 == path2

    def test_priority_order_empty_check_ids_overrides_sanitized(self):
        """Test empty check_ids takes priority over sanitized flag."""
        # Create a payload that would be sanitized but with empty check_ids
        payload = GovernedPayload(
            s0_system="System",
            i0_instructional="Instructions",
            c0_context="Context",
            u0_user_prompt="Clean prompt",
            check_ids=(),  # Empty tuple
            sanitized=True,  # But empty check_ids should win
            d0_injections="",
        )

        router = PathRouter()
        selected = router.select_path(payload)

        # Should be Path.A due to empty check_ids, not Path.B
        assert selected == Path.A

    def test_priority_order_sanitized_over_single_check_id(self):
        """Test sanitized flag takes priority over single check_id."""
        payload = GovernedPayload(
            s0_system="System",
            i0_instructional="Instructions",
            c0_context="Context",
            u0_user_prompt="Sanitized prompt",
            check_ids=("single_id",),
            sanitized=True,  # Should override single check_id
            d0_injections="",
        )

        router = PathRouter()
        selected = router.select_path(payload)

        # Should be Path.B due to sanitized flag, not Path.C
        assert selected == Path.B
