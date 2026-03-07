"""
Unit tests for L2 Re-Entry Loop - bounded deterministic retry mechanism.
"""

import pytest

from agentic_core.L2_execution.cid_registry import CIDRegistry, ExecutionCycle
from agentic_core.L2_execution.reentry_loop import ReEntryLoop


@pytest.mark.unit
class TestReEntryLoop:
    """Test deterministic ReEntryLoop implementation."""

    def test_init_with_valid_max_attempts(self):
        """Test ReEntryLoop initialization with valid max_attempts."""
        loop = ReEntryLoop(max_attempts=3)

        assert loop.max_attempts == 3
        assert loop._cid_registry is not None

    def test_init_with_custom_cid_registry(self):
        """Test ReEntryLoop initialization with custom CIDRegistry."""
        registry = CIDRegistry()
        loop = ReEntryLoop(max_attempts=5, cid_registry=registry)

        assert loop.max_attempts == 5
        assert loop._cid_registry is registry

    def test_init_with_invalid_max_attempts(self):
        """Test ReEntryLoop initialization with invalid max_attempts."""
        with pytest.raises(ValueError, match="max_attempts must be at least 1"):
            ReEntryLoop(max_attempts=0)

        with pytest.raises(ValueError, match="max_attempts must be at least 1"):
            ReEntryLoop(max_attempts=-1)

    def test_should_retry_true_when_below_max(self):
        """Test should_retry returns True when attempt < max_attempts."""
        loop = ReEntryLoop(max_attempts=3)
        cycle = ExecutionCycle(cid="test", attempt=1, status="running")

        assert loop.should_retry(cycle) is True

    def test_should_retry_false_at_max_attempts(self):
        """Test should_retry returns False when attempt == max_attempts."""
        loop = ReEntryLoop(max_attempts=3)
        cycle = ExecutionCycle(cid="test", attempt=3, status="running")

        assert loop.should_retry(cycle) is False

    def test_should_retry_false_above_max(self):
        """Test should_retry returns False when attempt > max_attempts."""
        loop = ReEntryLoop(max_attempts=3)
        cycle = ExecutionCycle(cid="test", attempt=4, status="running")

        assert loop.should_retry(cycle) is False

    def test_advance_increments_attempt(self):
        """Test advance increments attempt deterministically."""
        loop = ReEntryLoop(max_attempts=3)
        cycle = ExecutionCycle(cid="test", attempt=1, status="running")

        next_cycle = loop.advance(cycle)

        assert next_cycle.cid == "test"
        assert next_cycle.attempt == 2
        assert next_cycle.status == "retry"

    def test_advance_multiple_times(self):
        """Test advance called multiple times."""
        loop = ReEntryLoop(max_attempts=5)
        cycle = ExecutionCycle(cid="test", attempt=1, status="running")

        cycle2 = loop.advance(cycle)
        cycle3 = loop.advance(cycle2)
        cycle4 = loop.advance(cycle3)

        assert cycle.attempt == 1
        assert cycle2.attempt == 2
        assert cycle3.attempt == 3
        assert cycle4.attempt == 4

    def test_stops_at_max_attempts(self):
        """Test retry logic stops at max_attempts."""
        loop = ReEntryLoop(max_attempts=3)

        # Create initial cycle
        cycle = loop.new_cycle("test123")
        assert cycle.attempt == 1
        assert loop.should_retry(cycle) is True

        # First retry
        cycle = loop.advance(cycle)
        assert cycle.attempt == 2
        assert loop.should_retry(cycle) is True

        # Second retry (reaches max)
        cycle = loop.advance(cycle)
        assert cycle.attempt == 3
        assert loop.should_retry(cycle) is False

        # Should not retry beyond max
        assert loop.should_retry(cycle) is False

    def test_deterministic_behavior_repeated_runs(self):
        """Test deterministic behavior across repeated runs."""
        loop1 = ReEntryLoop(max_attempts=3)
        loop2 = ReEntryLoop(max_attempts=3)

        # Create same cycles in both loops
        cycle1 = loop1.new_cycle("test")
        cycle2 = loop2.new_cycle("test")

        # Should produce identical results
        assert cycle1.attempt == cycle2.attempt
        assert cycle1.status == cycle2.status

        # Advance both
        next1 = loop1.advance(cycle1)
        next2 = loop2.advance(cycle2)

        assert next1.attempt == next2.attempt
        assert next1.status == next2.status

    def test_new_cycle_creates_with_attempt_1(self):
        """Test new_cycle creates cycle with attempt=1."""
        loop = ReEntryLoop(max_attempts=5)

        cycle = loop.new_cycle("test123")

        assert cycle.cid == "test123"
        assert cycle.attempt == 1
        assert cycle.status == "new"

    def test_get_cycle_returns_current_cycle(self):
        """Test get_cycle returns most recent cycle for CID."""
        loop = ReEntryLoop(max_attempts=5)

        original = loop.new_cycle("test123")
        updated = loop.advance(original)

        retrieved = loop.get_cycle("test123")

        assert retrieved == updated
        assert retrieved.attempt == 2

    def test_get_cycle_nonexistent_returns_none(self):
        """Test get_cycle returns None for non-existent CID."""
        loop = ReEntryLoop(max_attempts=5)

        result = loop.get_cycle("nonexistent")

        assert result is None

    def test_update_status_changes_status_only(self):
        """Test update_status changes only status field."""
        loop = ReEntryLoop(max_attempts=5)

        loop.new_cycle("test123")
        updated = loop.update_status("test123", "completed")

        assert updated is not None
        assert updated.cid == "test123"
        assert updated.attempt == 1  # unchanged
        assert updated.status == "completed"

    def test_multiple_cids_independent_tracking(self):
        """Test multiple CIDs tracked independently."""
        loop = ReEntryLoop(max_attempts=5)

        # Create cycles for different CIDs
        cycle_a1 = loop.new_cycle("cid_a")
        loop.new_cycle("cid_b")
        loop.advance(cycle_a1)

        # Verify independent tracking
        assert loop.get_cycle("cid_a").attempt == 2
        assert loop.get_cycle("cid_b").attempt == 1

    def test_no_infinite_loops(self):
        """Test that loop logic cannot create infinite loops."""
        loop = ReEntryLoop(max_attempts=2)

        cycle = loop.new_cycle("test")
        retry_count = 0

        # Simulate retry logic
        while loop.should_retry(cycle) and retry_count < 10:  # safety limit
            cycle = loop.advance(cycle)
            retry_count += 1

        # Should stop after max_attempts - 1 retries
        assert retry_count == 1  # started at attempt 1, max is 2, so 1 retry
        assert cycle.attempt == 2
        assert loop.should_retry(cycle) is False
