"""Tests for ChangeTracker - state change tracking."""
import pytest
from agentic_core.L4_state.enforcement.change_tracker import ChangeTracker


class TestChangeTracker:
    def test_init(self):
        ct = ChangeTracker()
        assert ct is not None

    def test_track_change(self):
        ct = ChangeTracker()
        ct.track(key="x", old_value=1, new_value=2)
        changes = ct.get_changes()
        assert len(changes) == 1

    def test_track_no_op(self):
        ct = ChangeTracker()
        ct.track(key="x", old_value=1, new_value=1)
        # No actual change
        changes = ct.get_changes()
        assert len(changes) == 0

    def test_clear_changes(self):
        ct = ChangeTracker()
        ct.track(key="x", old_value=1, new_value=2)
        ct.clear()
        assert len(ct.get_changes()) == 0

    def test_get_changes_for_key(self):
        ct = ChangeTracker()
        ct.track(key="x", old_value=1, new_value=2)
        ct.track(key="y", old_value=3, new_value=4)
        x_changes = ct.get_changes_for_key("x")
        assert len(x_changes) == 1

    def test_change_count(self):
        ct = ChangeTracker()
        ct.track(key="x", old_value=1, new_value=2)
        ct.track(key="y", old_value=3, new_value=4)
        assert ct.count() == 2

    def test_diff_summary(self):
        ct = ChangeTracker()
        ct.track(key="x", old_value=1, new_value=2)
        summary = ct.get_diff_summary()
        assert "x" in summary
