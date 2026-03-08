"""
Unit tests for Meta-Learning Bus - queue-backed deterministic change conduit.
"""

import pytest

from agentic_core.L0_routing.meta_control.meta_learning_bus import (
    MetaLearningBus,
    MetaLearningChangePackage,
)


@pytest.mark.unit
class TestMetaLearningChangePackage:
    """Test MetaLearningChangePackage dataclass and hashing."""

    def test_create_package_with_deterministic_hash(self):
        """Test package creation with deterministic hash computation."""
        pkg = MetaLearningChangePackage.create(
            trace_id="trace123", kind="test_change", payload={"key": "value", "number": 42}
        )

        assert pkg.trace_id == "trace123"
        assert pkg.kind == "test_change"
        assert pkg.payload == {"key": "value", "number": 42}
        assert pkg.package_hash is not None
        assert len(pkg.package_hash) == 64  # SHA-256 hex length

    def test_package_hash_deterministic_across_identical_inputs(self):
        """Test package hash is deterministic across identical inputs."""
        pkg1 = MetaLearningChangePackage.create(
            trace_id="trace123", kind="test_change", payload={"key": "value", "number": 42}
        )

        pkg2 = MetaLearningChangePackage.create(
            trace_id="trace456",  # Different trace_id shouldn't affect hash
            kind="test_change",
            payload={"key": "value", "number": 42},
        )

        # Hash should be same for same kind+payload regardless of trace_id
        assert pkg1.package_hash == pkg2.package_hash

    def test_package_hash_different_for_different_payloads(self):
        """Test package hash differs for different payloads."""
        pkg1 = MetaLearningChangePackage.create(
            trace_id="trace123", kind="test_change", payload={"key": "value1"}
        )

        pkg2 = MetaLearningChangePackage.create(
            trace_id="trace123", kind="test_change", payload={"key": "value2"}
        )

        assert pkg1.package_hash != pkg2.package_hash

    def test_package_hash_different_for_different_kinds(self):
        """Test package hash differs for different kinds."""
        payload = {"key": "value"}

        pkg1 = MetaLearningChangePackage.create(trace_id="trace123", kind="kind1", payload=payload)

        pkg2 = MetaLearningChangePackage.create(trace_id="trace123", kind="kind2", payload=payload)

        assert pkg1.package_hash != pkg2.package_hash

    def test_package_hash_ignores_payload_key_order(self):
        """Test package hash ignores payload key order (canonical JSON)."""
        pkg1 = MetaLearningChangePackage.create(
            trace_id="trace123", kind="test_change", payload={"z": 1, "a": 2, "m": 3}
        )

        pkg2 = MetaLearningChangePackage.create(
            trace_id="trace123", kind="test_change", payload={"a": 2, "m": 3, "z": 1}
        )

        assert pkg1.package_hash == pkg2.package_hash

    def test_package_immutability(self):
        """Test package is immutable."""
        pkg = MetaLearningChangePackage.create(
            trace_id="trace123", kind="test_change", payload={"key": "value"}
        )

        # Should be frozen dataclass
        with pytest.raises(AttributeError):
            pkg.trace_id = "changed"

        with pytest.raises(AttributeError):
            pkg.kind = "changed"

        with pytest.raises(AttributeError):
            pkg.payload = {"changed": "value"}


@pytest.mark.unit
class TestMetaLearningBus:
    """Test MetaLearningBus queue operations."""

    def test_bus_initialization_empty(self):
        """Test bus initializes with empty queue."""
        bus = MetaLearningBus()

        assert bus.size() == 0
        assert bus.dequeue() is None

    def test_enqueue_and_dequeue_single_package(self):
        """Test enqueue and dequeue of single package."""
        bus = MetaLearningBus()
        pkg = MetaLearningChangePackage.create(
            trace_id="trace123", kind="test_change", payload={"key": "value"}
        )

        bus.enqueue(pkg)
        assert bus.size() == 1

        dequeued = bus.dequeue()
        assert dequeued == pkg
        assert bus.size() == 0

    def test_fifo_ordering_preserved(self):
        """Test FIFO ordering is preserved."""
        bus = MetaLearningBus()

        pkg1 = MetaLearningChangePackage.create("trace1", "kind1", {"seq": 1})
        pkg2 = MetaLearningChangePackage.create("trace2", "kind2", {"seq": 2})
        pkg3 = MetaLearningChangePackage.create("trace3", "kind3", {"seq": 3})

        # Enqueue in order
        bus.enqueue(pkg1)
        bus.enqueue(pkg2)
        bus.enqueue(pkg3)

        # Should dequeue in same order
        assert bus.dequeue() == pkg1
        assert bus.dequeue() == pkg2
        assert bus.dequeue() == pkg3
        assert bus.dequeue() is None

    def test_dequeue_returns_none_when_empty(self):
        """Test dequeue returns None when queue is empty."""
        bus = MetaLearningBus()

        assert bus.dequeue() is None

        # Add and remove a package
        pkg = MetaLearningChangePackage.create("trace", "kind", {})
        bus.enqueue(pkg)
        bus.dequeue()

        # Should still return None
        assert bus.dequeue() is None

    def test_size_tracking(self):
        """Test size tracking works correctly."""
        bus = MetaLearningBus()

        assert bus.size() == 0

        pkg = MetaLearningChangePackage.create("trace", "kind", {})
        bus.enqueue(pkg)
        assert bus.size() == 1

        bus.enqueue(pkg)
        assert bus.size() == 2

        bus.dequeue()
        assert bus.size() == 1

        bus.dequeue()
        assert bus.size() == 0

    def test_apply_next_calls_injected_function(self):
        """Test apply_next calls injected apply_fn exactly once."""
        bus = MetaLearningBus()
        pkg = MetaLearningChangePackage.create("trace123", "test_change", {"key": "value"})

        # Track calls to apply_fn
        calls = []

        def mock_apply_fn(package):
            calls.append(package)
            return "result_" + package.trace_id

        bus.enqueue(pkg)

        result = bus.apply_next(apply_fn=mock_apply_fn)

        assert result is not None
        returned_pkg, returned_result = result
        assert returned_pkg == pkg
        assert returned_result == "result_trace123"
        assert len(calls) == 1
        assert calls[0] == pkg

    def test_apply_next_returns_deterministic_tuple(self):
        """Test apply_next returns deterministic tuple."""
        bus = MetaLearningBus()
        pkg = MetaLearningChangePackage.create("trace123", "test_change", {"key": "value"})

        def mock_apply_fn(package):
            return {"applied": True, "trace": package.trace_id}

        bus.enqueue(pkg)

        result1 = bus.apply_next(apply_fn=mock_apply_fn)
        result2 = bus.apply_next(apply_fn=mock_apply_fn)

        # First call should return tuple, second should return None
        assert result1 is not None
        assert result1[0] == pkg
        assert result1[1] == {"applied": True, "trace": "trace123"}

        assert result2 is None

    def test_apply_next_empty_queue_does_not_call_apply_fn(self):
        """Test apply_next returns None and does not call apply_fn when queue empty."""
        bus = MetaLearningBus()

        calls = []

        def mock_apply_fn(package):
            calls.append(package)
            return "result"

        result = bus.apply_next(apply_fn=mock_apply_fn)

        assert result is None
        assert len(calls) == 0

    def test_apply_next_multiple_packages(self):
        """Test apply_next with multiple packages."""
        bus = MetaLearningBus()

        pkg1 = MetaLearningChangePackage.create("trace1", "kind1", {"seq": 1})
        pkg2 = MetaLearningChangePackage.create("trace2", "kind2", {"seq": 2})

        results = []

        def mock_apply_fn(package):
            results.append(package.trace_id)
            return f"processed_{package.trace_id}"

        bus.enqueue(pkg1)
        bus.enqueue(pkg2)

        # Apply first package
        result1 = bus.apply_next(apply_fn=mock_apply_fn)
        assert result1 is not None
        assert result1[0] == pkg1
        assert result1[1] == "processed_trace1"

        # Apply second package
        result2 = bus.apply_next(apply_fn=mock_apply_fn)
        assert result2 is not None
        assert result2[0] == pkg2
        assert result2[1] == "processed_trace2"

        # No more packages
        result3 = bus.apply_next(apply_fn=mock_apply_fn)
        assert result3 is None

        # Verify apply_fn was called exactly twice
        assert results == ["trace1", "trace2"]
