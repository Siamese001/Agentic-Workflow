"""
Unit tests for L2 CID Registry - immutable execution cycle tracking.
"""

import pytest

from agentic_core.L2_execution.cid_registry import CIDRegistry, ExecutionCycle


@pytest.mark.unit
class TestExecutionCycle:
    """Test ExecutionCycle dataclass properties."""

    def test_execution_cycle_creation(self):
        """Test ExecutionCycle creation and properties."""
        cycle = ExecutionCycle(cid="test123", attempt=1, status="new")

        assert cycle.cid == "test123"
        assert cycle.attempt == 1
        assert cycle.status == "new"
        assert cycle == ExecutionCycle(cid="test123", attempt=1, status="new")

    def test_execution_cycle_immutability(self):
        """Test ExecutionCycle is immutable."""
        cycle = ExecutionCycle(cid="test123", attempt=1, status="new")

        # Should be frozen dataclass
        with pytest.raises(AttributeError):
            cycle.attempt = 2

        with pytest.raises(AttributeError):
            cycle.status = "changed"


@pytest.mark.unit
class TestCIDRegistry:
    """Test deterministic CIDRegistry implementation."""

    def test_new_cycle_creates_with_attempt_1(self):
        """Test new_cycle creates cycle with attempt=1 and status='new'."""
        registry = CIDRegistry()

        cycle = registry.new_cycle("test123")

        assert cycle.cid == "test123"
        assert cycle.attempt == 1
        assert cycle.status == "new"

    def test_same_cid_independent_cycles_allowed(self):
        """Test same CID creates independent cycles when called multiple times."""
        registry = CIDRegistry()

        cycle1 = registry.new_cycle("same_cid")
        cycle2 = registry.new_cycle("same_cid")

        # Should create new cycles, not return existing
        assert cycle1.attempt == 1
        assert cycle2.attempt == 1
        assert cycle1.status == "new"
        assert cycle2.status == "new"
        assert cycle1 is not cycle2

    def test_next_attempt_increments_deterministically(self):
        """Test next_attempt increments attempt deterministically."""
        registry = CIDRegistry()

        cycle = registry.new_cycle("test123")
        next_cycle = registry.next_attempt(cycle)

        assert next_cycle.cid == "test123"
        assert next_cycle.attempt == 2
        assert next_cycle.status == "retry"

    def test_next_attempt_multiple_increments(self):
        """Test multiple next_attempt calls increment correctly."""
        registry = CIDRegistry()

        cycle = registry.new_cycle("test123")
        cycle2 = registry.next_attempt(cycle)
        cycle3 = registry.next_attempt(cycle2)
        cycle4 = registry.next_attempt(cycle3)

        assert cycle.attempt == 1
        assert cycle2.attempt == 2
        assert cycle3.attempt == 3
        assert cycle4.attempt == 4

    def test_get_cycle_returns_current_cycle(self):
        """Test get_cycle returns the most recent cycle for CID."""
        registry = CIDRegistry()

        original = registry.new_cycle("test123")
        updated = registry.next_attempt(original)

        retrieved = registry.get_cycle("test123")

        assert retrieved == updated
        assert retrieved.attempt == 2

    def test_get_cycle_nonexistent_returns_none(self):
        """Test get_cycle returns None for non-existent CID."""
        registry = CIDRegistry()

        result = registry.get_cycle("nonexistent")

        assert result is None

    def test_update_status_changes_status_only(self):
        """Test update_status changes only status field."""
        registry = CIDRegistry()

        _ = registry.new_cycle("test123")
        updated = registry.update_status("test123", "completed")

        assert updated is not None
        assert updated.cid == "test123"
        assert updated.attempt == 1  # unchanged
        assert updated.status == "completed"

    def test_update_status_nonexistent_returns_none(self):
        """Test update_status returns None for non-existent CID."""
        registry = CIDRegistry()

        result = registry.update_status("nonexistent", "status")

        assert result is None

    def test_deterministic_behavior_same_inputs(self):
        """Test deterministic behavior with same inputs."""
        registry1 = CIDRegistry()
        registry2 = CIDRegistry()

        # Create same cycles in both registries
        cycle1a = registry1.new_cycle("test")
        cycle1b = registry1.next_attempt(cycle1a)
        cycle1c = registry1.update_status("test", "done")

        cycle2a = registry2.new_cycle("test")
        cycle2b = registry2.next_attempt(cycle2a)
        cycle2c = registry2.update_status("test", "done")

        # Should produce identical results
        assert cycle1a.attempt == cycle2a.attempt
        assert cycle1b.attempt == cycle2b.attempt
        assert cycle1c.status == cycle2c.status

    def test_multiple_cids_independent_tracking(self):
        """Test multiple CIDs tracked independently."""
        registry = CIDRegistry()

        # Create cycles for different CIDs
        cycle_a1 = registry.new_cycle("cid_a")
        registry.new_cycle("cid_b")
        registry.next_attempt(cycle_a1)

        # Verify independent tracking
        assert registry.get_cycle("cid_a").attempt == 2
        assert registry.get_cycle("cid_b").attempt == 1
