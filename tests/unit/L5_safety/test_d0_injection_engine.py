"""
Unit tests for L5 D0 Injection Engine - deterministic fence rendering.
"""

import pytest

from agentic_core.L5_safety.enforcement.d0_injection_engine import D0InjectionEngine, RoleFence


@pytest.mark.unit
class TestD0InjectionEngine:
    """Test deterministic D0InjectionEngine implementation."""

    def test_role_fence_dataclass(self):
        """Test RoleFence dataclass properties."""
        fence = RoleFence(fence_id="test_fence", text="Test content")

        assert fence.fence_id == "test_fence"
        assert fence.text == "Test content"
        assert fence == RoleFence(fence_id="test_fence", text="Test content")
        assert fence != RoleFence(fence_id="other_fence", text="Test content")

    def test_render_d0_single_fence(self):
        """Test D0 rendering with single fence."""
        engine = D0InjectionEngine()
        fences = (RoleFence(fence_id="fence1", text="Content 1"),)

        result = engine.render_d0(fences=fences)

        expected = "<D0>\n[fence1] Content 1\n</D0>\n"
        assert result == expected

    def test_render_d0_multiple_fences_sorted(self):
        """Test D0 rendering with multiple fences sorted by fence_id."""
        engine = D0InjectionEngine()
        fences = (
            RoleFence(fence_id="zebra", text="Zebra content"),
            RoleFence(fence_id="alpha", text="Alpha content"),
            RoleFence(fence_id="beta", text="Beta content"),
        )

        result = engine.render_d0(fences=fences)

        expected = "<D0>\n[alpha] Alpha content\n[beta] Beta content\n[zebra] Zebra content\n</D0>\n"
        assert result == expected

    def test_same_fences_different_order_identical_output(self):
        """Test same fences in different order produce identical output."""
        engine = D0InjectionEngine()

        fences1 = (
            RoleFence(fence_id="first", text="First content"),
            RoleFence(fence_id="second", text="Second content"),
        )

        fences2 = (
            RoleFence(fence_id="second", text="Second content"),
            RoleFence(fence_id="first", text="First content"),
        )

        result1 = engine.render_d0(fences=fences1)
        result2 = engine.render_d0(fences=fences2)

        assert result1 == result2

    def test_output_contains_all_fence_ids_exactly_once(self):
        """Test output contains all fence IDs exactly once."""
        engine = D0InjectionEngine()
        fences = (
            RoleFence(fence_id="fence_a", text="Content A"),
            RoleFence(fence_id="fence_b", text="Content B"),
            RoleFence(fence_id="fence_c", text="Content C"),
        )

        result = engine.render_d0(fences=fences)

        # Check each fence ID appears exactly once
        for fence in fences:
            count = result.count(f"[{fence.fence_id}]")
            assert count == 1, f"Fence ID {fence.fence_id} appears {count} times"

    def test_inject_does_not_mutate_payload_like(self):
        """Test inject method does not mutate payload_like object."""
        engine = D0InjectionEngine()

        # Create a simple payload-like object
        class SimplePayload:
            def __init__(self):
                self.some_field = "original_value"
                self.check_ids = ("id1", "id2")

        payload = SimplePayload()
        original_state = {
            "some_field": payload.some_field,
            "check_ids": payload.check_ids,
        }

        fences = (RoleFence(fence_id="test", text="Test content"),)

        result = engine.inject(payload_like=payload, fences=fences)

        # Verify payload was not mutated
        assert payload.some_field == original_state["some_field"]
        assert payload.check_ids == original_state["check_ids"]

        # Verify result is a valid D0 string
        assert result == "<D0>\n[test] Test content\n</D0>\n"

    def test_inject_returns_d0_string_only(self):
        """Test inject returns only the D0 string."""
        engine = D0InjectionEngine()
        fences = (
            RoleFence(fence_id="fence1", text="Content 1"),
            RoleFence(fence_id="fence2", text="Content 2"),
        )

        result = engine.inject(payload_like=object(), fences=fences)

        expected = "<D0>\n[fence1] Content 1\n[fence2] Content 2\n</D0>\n"
        assert result == expected

    def test_empty_fences_tuple(self):
        """Test handling of empty fences tuple."""
        engine = D0InjectionEngine()
        fences = ()

        result = engine.render_d0(fences=fences)

        expected = "<D0>\n</D0>\n"
        assert result == expected

    def test_deterministic_output_identical_calls(self):
        """Test multiple calls with same input produce identical output."""
        engine = D0InjectionEngine()
        fences = (
            RoleFence(fence_id="test1", text="Test content 1"),
            RoleFence(fence_id="test2", text="Test content 2"),
        )

        result1 = engine.render_d0(fences=fences)
        result2 = engine.render_d0(fences=fences)
        result3 = engine.render_d0(fences=fences)

        assert result1 == result2 == result3
