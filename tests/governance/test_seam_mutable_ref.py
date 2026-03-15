"""REQ-270/273: Seam mutable reference enforcement.

Prove seam passes only immutable (frozen dataclass / tuple) references;
prove seam replay stable.
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.L2_execution.enforcement.runtime_interceptor import (
    MutableReferenceError,
    MutableReferenceTracker,
    assert_immutable_reference,
    clear_mutable_ref_violations,
    get_mutable_ref_violations,
    immutable_references,
)


@pytest.mark.governance
def test_req270_immutable_reference_enforcement():
    """REQ-270: Seam passes only immutable references."""
    # Test immutable types pass
    assert_immutable_reference(42, "test context")
    assert_immutable_reference("hello", "test context")
    assert_immutable_reference((1, 2, 3), "test context")
    assert_immutable_reference(frozenset([1, 2, 3]), "test context")
    assert_immutable_reference(True, "test context")
    assert_immutable_reference(None, "test context")

    # Test hashable objects pass
    class CustomHashable:
        def __hash__(self):
            return 42

    assert_immutable_reference(CustomHashable(), "test context")


@pytest.mark.governance
def test_req270_mutable_reference_detection():
    """REQ-270: Mutable references are detected and rejected."""
    clear_mutable_ref_violations()

    # Test mutable types fail
    with pytest.raises(MutableReferenceError, match="Mutable reference detected"):
        assert_immutable_reference([1, 2, 3], "test context")

    with pytest.raises(MutableReferenceError, match="Mutable reference detected"):
        assert_immutable_reference({"a": 1}, "test context")

    with pytest.raises(MutableReferenceError, match="Mutable reference detected"):
        assert_immutable_reference({1, 2, 3}, "test context")

    with pytest.raises(MutableReferenceError, match="Mutable reference detected"):
        assert_immutable_reference(bytearray(b"test"), "test context")


@pytest.mark.governance
def test_req270_frozen_dataclass_allowed():
    """REQ-270: Frozen dataclasses are allowed as immutable."""

    @dataclasses.dataclass(frozen=True)
    class FrozenData:
        value: int
        name: str

    frozen_obj = FrozenData(42, "test")
    assert_immutable_reference(frozen_obj, "test context")

    # Non-frozen dataclass should fail
    @dataclasses.dataclass
    class MutableData:
        value: int
        name: str

    mutable_obj = MutableData(42, "test")
    with pytest.raises(MutableReferenceError, match="Mutable reference detected"):
        assert_immutable_reference(mutable_obj, "test context")


@pytest.mark.governance
def test_req270_allowed_seam_contexts():
    """REQ-270: Mutable references allowed in specific seam contexts."""
    # Test that allowed contexts permit mutable references
    assert_immutable_reference([1, 2, 3], "sovereign_gateway_processing")
    assert_immutable_reference({"a": 1}, "embedding_factory_call")
    assert_immutable_reference([1, 2, 3], "capability_token_validation")

    # Test that non-allowed contexts reject mutable references
    with pytest.raises(MutableReferenceError):
        assert_immutable_reference([1, 2, 3], "random_context")

    with pytest.raises(MutableReferenceError):
        assert_immutable_reference({"a": 1}, "user_function")


@pytest.mark.governance
def test_req273_seam_replay_stability():
    """REQ-273: Seam replay is stable with immutable references."""

    # Simulate seam execution with immutable references
    def seam_execution(data: tuple[int, ...]) -> int:
        """Simulated seam that only accepts immutable data."""
        assert_immutable_reference(data, "seam_execution")
        return sum(data)

    # First execution
    immutable_data = (1, 2, 3, 4, 5)
    result1 = seam_execution(immutable_data)

    # Replay execution (should be identical)
    result2 = seam_execution(immutable_data)

    assert result1 == result2
    assert result1 == 15


@pytest.mark.governance
def test_req273_mutable_reference_breaks_replay():
    """REQ-273: Mutable references break replay stability."""

    def seam_with_mutable(data: list[int]) -> int:
        """Seam that incorrectly accepts mutable data."""
        # This would normally be caught by assert_immutable_reference
        # but we're testing the replay stability concept
        return sum(data)

    mutable_data = [1, 2, 3, 4, 5]
    result1 = seam_with_mutable(mutable_data)

    # Modify mutable data between executions
    mutable_data.append(6)
    result2 = seam_with_mutable(mutable_data)

    # Results differ - replay not stable
    assert result1 != result2
    assert result1 == 15
    assert result2 == 21


@pytest.mark.governance
def test_req270_273_decorator_enforcement():
    """REQ-270/273: Decorator enforces immutable references."""

    @immutable_references
    def process_data(values: tuple[int, ...], multiplier: int) -> tuple[int, ...]:
        return tuple(v * multiplier for v in values)

    # Should work with immutable arguments
    result = process_data((1, 2, 3), 2)
    assert result == (2, 4, 6)

    # Should fail with mutable arguments
    with pytest.raises(MutableReferenceError):
        process_data([1, 2, 3], 2)

    with pytest.raises(MutableReferenceError):
        process_data((1, 2, 3), [2])  # mutable keyword arg


@pytest.mark.governance
def test_req270_violation_tracking():
    """REQ-270: Mutable reference violations are tracked."""
    clear_mutable_ref_violations()

    with MutableReferenceTracker():
        # Generate some violations
        with pytest.raises(MutableReferenceError):
            assert_immutable_reference([1, 2, 3], "test1")

        with pytest.raises(MutableReferenceError):
            assert_immutable_reference({"a": 1}, "test2")

        # Check violations were recorded
        violations = get_mutable_ref_violations()
        assert len(violations) == 2
        assert "test1" in violations[0]
        assert "test2" in violations[1]

    # Violations should still be available after context exit
    violations = get_mutable_ref_violations()
    assert len(violations) == 2


@pytest.mark.governance
def test_req270_complex_object_immutability():
    """REQ-270: Complex object immutability detection."""
    # Nested immutable structures
    nested_immutable = ((1, 2), (3, 4), (5, 6))
    assert_immutable_reference(nested_immutable, "nested test")

    # Nested mutable structures
    nested_mutable = ([1, 2], [3, 4], [5, 6])
    with pytest.raises(MutableReferenceError):
        assert_immutable_reference(nested_mutable, "nested test")

    # Mixed structures (should fail due to mutable component)
    mixed = (1, [2, 3], 4)
    with pytest.raises(MutableReferenceError):
        assert_immutable_reference(mixed, "mixed test")
