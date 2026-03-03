"""
Phase 5 — Wave 2 Tests: L4 ViolationEventStore prior-only persistence.
"""

from __future__ import annotations

import pytest

from agentic_core.L4_state.enforcement.violation_event_store import ViolationEventStore
from agentic_core.L4_state.types.violation_event_types import ViolationEvent, emit_violation_event

pytestmark = pytest.mark.unit_min_deps

_TS = "2026-02-21T00:00:00Z"


def _make_event(commit_tick: int, severity: float = 0.5, decision: str = "block") -> ViolationEvent:
    return emit_violation_event(
        mission_id="mission-test",
        commit_tick=commit_tick,
        guardian_decision=decision,
        violation_codes=["CODE_A"],
        severity_score=severity,
        created_at_utc=_TS,
    )


class TestStoreAndFetch:
    def test_store_returns_event_hash(self):
        store = ViolationEventStore()
        e = _make_event(commit_tick=3)
        h = store.store_violation_event(e)
        assert h == e.event_hash
        assert len(h) == 64

    def test_store_idempotent(self):
        """Storing the same event twice does not duplicate it."""
        store = ViolationEventStore()
        e = _make_event(commit_tick=3)
        store.store_violation_event(e)
        store.store_violation_event(e)
        assert store.count() == 1

    def test_store_rejects_non_event(self):
        store = ViolationEventStore()
        with pytest.raises(TypeError):
            store.store_violation_event({"not": "an event"})  # type: ignore[arg-type]

    def test_store_and_fetch_latest_prior_only(self):
        """
        fetch_latest_violation(before_tick=T) returns the most recent event
        with commit_tick < T.
        """
        store = ViolationEventStore()
        e3 = _make_event(commit_tick=3)
        e5 = _make_event(commit_tick=5)
        e7 = _make_event(commit_tick=7)
        store.store_violation_event(e3)
        store.store_violation_event(e5)
        store.store_violation_event(e7)

        result = store.fetch_latest_violation(before_tick=6)
        assert result is not None
        assert result.commit_tick == 5

    def test_fetch_latest_returns_highest_tick_below_boundary(self):
        store = ViolationEventStore()
        for tick in [1, 2, 3, 4, 5]:
            store.store_violation_event(_make_event(commit_tick=tick))

        result = store.fetch_latest_violation(before_tick=4)
        assert result is not None
        assert result.commit_tick == 3

    def test_fetch_latest_returns_none_when_no_prior(self):
        store = ViolationEventStore()
        e = _make_event(commit_tick=10)
        store.store_violation_event(e)

        result = store.fetch_latest_violation(before_tick=5)
        assert result is None

    def test_fetch_latest_returns_none_on_empty_store(self):
        store = ViolationEventStore()
        assert store.fetch_latest_violation(before_tick=100) is None


class TestSameCycleExclusion:
    def test_fetch_disallows_same_cycle_event(self):
        """
        An event at commit_tick=T must NOT be returned by
        fetch_latest_violation(before_tick=T).
        """
        store = ViolationEventStore()
        e_same = _make_event(commit_tick=10)
        store.store_violation_event(e_same)

        result = store.fetch_latest_violation(before_tick=10)
        assert result is None

    def test_fetch_window_excludes_same_cycle(self):
        """fetch_window(before_tick=T) must not include commit_tick=T."""
        store = ViolationEventStore()
        e_same = _make_event(commit_tick=10)
        e_prior = _make_event(commit_tick=8)
        store.store_violation_event(e_same)
        store.store_violation_event(e_prior)

        window = store.fetch_window(before_tick=10, window_ticks=5)
        ticks = [e.commit_tick for e in window]
        assert 10 not in ticks
        assert 8 in ticks

    def test_same_cycle_event_stored_but_invisible_at_boundary(self):
        """
        Event at tick T is stored (count increases) but fetch at T returns None.
        This proves structural invisibility, not deletion.
        """
        store = ViolationEventStore()
        e = _make_event(commit_tick=7)
        store.store_violation_event(e)
        assert store.count() == 1
        assert store.fetch_latest_violation(before_tick=7) is None
        assert store.fetch_latest_violation(before_tick=8) is not None


class TestFetchWindow:
    def test_fetch_window_returns_sorted_by_tick_then_hash(self):
        """
        fetch_window must return events sorted ascending by
        (commit_tick, event_hash).
        """
        store = ViolationEventStore()
        ticks = [3, 7, 5, 4, 6]
        events = {}
        for t in ticks:
            e = _make_event(commit_tick=t)
            store.store_violation_event(e)
            events[t] = e

        window = store.fetch_window(before_tick=10, window_ticks=10)
        returned_ticks = [e.commit_tick for e in window]
        assert returned_ticks == sorted(returned_ticks)

    def test_fetch_window_respects_lower_bound(self):
        """Only events with commit_tick >= before_tick - window_ticks are returned."""
        store = ViolationEventStore()
        for t in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
            store.store_violation_event(_make_event(commit_tick=t))

        window = store.fetch_window(before_tick=8, window_ticks=3)
        ticks = [e.commit_tick for e in window]
        assert all(5 <= t < 8 for t in ticks)

    def test_fetch_window_empty_when_no_events_in_range(self):
        store = ViolationEventStore()
        store.store_violation_event(_make_event(commit_tick=1))
        window = store.fetch_window(before_tick=10, window_ticks=2)
        assert window == []

    def test_fetch_window_negative_window_ticks_raises(self):
        store = ViolationEventStore()
        with pytest.raises(ValueError, match="window_ticks"):
            store.fetch_window(before_tick=10, window_ticks=-1)

    def test_fetch_window_zero_ticks_returns_empty(self):
        """window_ticks=0 means [T, T) which is empty."""
        store = ViolationEventStore()
        store.store_violation_event(_make_event(commit_tick=9))
        window = store.fetch_window(before_tick=10, window_ticks=0)
        assert window == []

    def test_fetch_window_returns_all_in_range(self):
        store = ViolationEventStore()
        for t in [5, 6, 7, 8, 9]:
            store.store_violation_event(_make_event(commit_tick=t))

        window = store.fetch_window(before_tick=10, window_ticks=5)
        ticks = [e.commit_tick for e in window]
        assert sorted(ticks) == [5, 6, 7, 8, 9]
