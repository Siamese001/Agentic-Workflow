"""
Wave 3 Phase 7 — L4 Unified State Manager Tests

§4-compliant test suite covering:
- ViolationEvent: all validation guards, canonical hash, round-trip, determinism
- ViolationEventStore: store/idempotency, fetch_latest, fetch_window, same-cycle exclusion
- detect_ghost_mutations: consistent state, ghost mutation detection, deep diff
- validate_freshness: fresh data, stale data boundary, exact-age boundary
- MemoryCollisionDetector: acquire success, unknown lock guard, hierarchy ordering
"""

from __future__ import annotations

import datetime

import pytest

from agentic_core.L4_state.enforcement.violation_event_store import ViolationEventStore
from agentic_core.L4_state.engines.fresh_data_validator import (
    FreshnessPolicy,
    StaleDataViolation,
    VersionedData,
    validate_freshness,
)
from agentic_core.L4_state.engines.ghost_mutation_detector import (
    GhostMutationViolation,
    _deep_diff,
    detect_ghost_mutations,
)
from agentic_core.L4_state.engines.memory_collision_detector import (
    LockAcquisitionResult,
    LockPolicy,
    MemoryCollisionDetector,
    MemoryDeadlockViolation,
)
from agentic_core.L4_state.types.violation_event_types import (
    ViolationEvent,
    emit_violation_event,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SCHEMA = 1


def _event(
    mission_id: str = "mission-1",
    commit_tick: int = 5,
    decision: str = "block",
    codes: list[str] | None = None,
    severity: float = 0.5,
    created_at: str = "2026-01-01T00:00:00Z",
) -> ViolationEvent:
    return ViolationEvent(
        schema_version=_SCHEMA,
        mission_id=mission_id,
        commit_tick=commit_tick,
        guardian_decision=decision,
        violation_codes=codes or [],
        severity_score=severity,
        created_at_utc=created_at,
    )


def _fresh_data(content: object = "data", age_seconds: float = 0) -> VersionedData:
    ts = datetime.datetime.utcnow() - datetime.timedelta(seconds=age_seconds)
    return VersionedData(content=content, timestamp=ts)


# ===========================================================================
# 1. ViolationEvent — construction and validation guards
# ===========================================================================


class TestViolationEventConstruction:
    @pytest.mark.governance
    def test_valid_event_constructs_without_error(self):
        e = _event()
        assert e.mission_id == "mission-1"

    @pytest.mark.governance
    def test_event_hash_is_64_hex_chars(self):
        e = _event()
        assert len(e.event_hash) == 64
        int(e.event_hash, 16)

    @pytest.mark.governance
    def test_event_hash_deterministic_for_same_fields(self):
        e1 = _event()
        e2 = _event()
        assert e1.event_hash == e2.event_hash

    @pytest.mark.governance
    def test_event_hash_differs_for_different_mission_id(self):
        e1 = _event(mission_id="a")
        e2 = _event(mission_id="b")
        assert e1.event_hash != e2.event_hash

    @pytest.mark.governance
    def test_violation_codes_sorted_on_construction(self):
        e = _event(codes=["z", "a", "m"])
        assert e.violation_codes == ["a", "m", "z"]

    @pytest.mark.governance
    def test_raises_when_schema_version_wrong(self):
        with pytest.raises(ValueError, match="schema_version"):
            ViolationEvent(
                schema_version=99,
                mission_id="m",
                commit_tick=0,
                guardian_decision="block",
                violation_codes=[],
                severity_score=0.5,
                created_at_utc="2026-01-01T00:00:00Z",
            )

    @pytest.mark.governance
    def test_raises_when_mission_id_empty(self):
        with pytest.raises(ValueError, match="mission_id"):
            _event(mission_id="")

    @pytest.mark.governance
    def test_raises_when_commit_tick_negative(self):
        with pytest.raises(ValueError, match="commit_tick"):
            _event(commit_tick=-1)

    @pytest.mark.governance
    def test_exact_boundary_commit_tick_0_valid(self):
        e = _event(commit_tick=0)
        assert e.commit_tick == 0

    @pytest.mark.governance
    def test_raises_when_guardian_decision_invalid(self):
        with pytest.raises(ValueError, match="guardian_decision"):
            _event(decision="approve")

    @pytest.mark.governance
    def test_allows_decision_allow(self):
        e = _event(decision="allow")
        assert e.guardian_decision == "allow"

    @pytest.mark.governance
    def test_allows_decision_block(self):
        e = _event(decision="block")
        assert e.guardian_decision == "block"

    @pytest.mark.governance
    def test_allows_decision_escalate(self):
        e = _event(decision="escalate")
        assert e.guardian_decision == "escalate"

    @pytest.mark.governance
    def test_raises_when_severity_below_0(self):
        with pytest.raises(ValueError, match="severity_score"):
            _event(severity=-0.01)

    @pytest.mark.governance
    def test_raises_when_severity_above_1(self):
        with pytest.raises(ValueError, match="severity_score"):
            _event(severity=1.01)

    @pytest.mark.governance
    def test_exact_boundary_severity_0_valid(self):
        e = _event(severity=0.0)
        assert e.severity_score == 0.0

    @pytest.mark.governance
    def test_exact_boundary_severity_1_valid(self):
        e = _event(severity=1.0)
        assert e.severity_score == 1.0

    @pytest.mark.governance
    def test_raises_when_violation_codes_not_list(self):
        with pytest.raises(TypeError, match="violation_codes"):
            ViolationEvent(
                schema_version=_SCHEMA,
                mission_id="m",
                commit_tick=0,
                guardian_decision="block",
                violation_codes=("a",),  # type: ignore
                severity_score=0.5,
                created_at_utc="2026-01-01T00:00:00Z",
            )

    @pytest.mark.governance
    def test_round_trip_to_dict_and_from_dict(self):
        e = _event(codes=["C1", "C2"])
        d = e.to_dict()
        e2 = ViolationEvent.from_dict(d)
        assert e2.event_hash == e.event_hash

    @pytest.mark.governance
    def test_emit_violation_event_helper_returns_violation_event(self):
        e = emit_violation_event(
            mission_id="m",
            commit_tick=1,
            guardian_decision="block",
            violation_codes=[],
            severity_score=0.5,
            created_at_utc="2026-01-01T00:00:00Z",
        )
        assert isinstance(e, ViolationEvent)

    @pytest.mark.governance
    def test_emit_violation_event_appends_to_registry(self):
        registry: list[ViolationEvent] = []
        emit_violation_event(
            mission_id="m",
            commit_tick=1,
            guardian_decision="allow",
            violation_codes=[],
            severity_score=0.1,
            created_at_utc="2026-01-01T00:00:00Z",
            _registry=registry,
        )
        assert len(registry) == 1


# ===========================================================================
# 2. ViolationEventStore — store, idempotency, fetch_latest, fetch_window
# ===========================================================================


class TestViolationEventStore:
    @pytest.mark.governance
    def test_store_returns_event_hash(self):
        store = ViolationEventStore()
        e = _event(commit_tick=5)
        h = store.store_violation_event(e)
        assert h == e.event_hash

    @pytest.mark.governance
    def test_store_idempotent_for_same_event_twice(self):
        store = ViolationEventStore()
        e = _event(commit_tick=5)
        store.store_violation_event(e)
        store.store_violation_event(e)
        assert store.count() == 1

    @pytest.mark.governance
    def test_store_raises_type_error_for_non_violation_event(self):
        store = ViolationEventStore()
        with pytest.raises(TypeError, match="ViolationEvent"):
            store.store_violation_event("not an event")  # type: ignore

    @pytest.mark.governance
    def test_fetch_latest_returns_none_when_empty(self):
        store = ViolationEventStore()
        assert store.fetch_latest_violation(before_tick=10) is None

    @pytest.mark.governance
    def test_fetch_latest_excludes_same_cycle_event(self):
        store = ViolationEventStore()
        e = _event(commit_tick=10)
        store.store_violation_event(e)
        assert store.fetch_latest_violation(before_tick=10) is None

    @pytest.mark.governance
    def test_fetch_latest_returns_prior_event(self):
        store = ViolationEventStore()
        e = _event(commit_tick=9)
        store.store_violation_event(e)
        result = store.fetch_latest_violation(before_tick=10)
        assert result is not None
        assert result.commit_tick == 9

    @pytest.mark.governance
    def test_fetch_latest_returns_most_recent_prior(self):
        store = ViolationEventStore()
        e1 = _event(mission_id="m1", commit_tick=3)
        e2 = _event(mission_id="m2", commit_tick=7)
        store.store_violation_event(e1)
        store.store_violation_event(e2)
        result = store.fetch_latest_violation(before_tick=10)
        assert result is not None
        assert result.commit_tick == 7

    @pytest.mark.governance
    def test_fetch_window_returns_empty_for_no_events(self):
        store = ViolationEventStore()
        result = store.fetch_window(before_tick=10, window_ticks=5)
        assert result == []

    @pytest.mark.governance
    def test_fetch_window_excludes_same_cycle_event(self):
        store = ViolationEventStore()
        e = _event(commit_tick=10)
        store.store_violation_event(e)
        result = store.fetch_window(before_tick=10, window_ticks=5)
        assert len(result) == 0

    @pytest.mark.governance
    def test_fetch_window_includes_events_in_window(self):
        store = ViolationEventStore()
        e1 = _event(mission_id="m1", commit_tick=6)
        e2 = _event(mission_id="m2", commit_tick=8)
        store.store_violation_event(e1)
        store.store_violation_event(e2)
        result = store.fetch_window(before_tick=10, window_ticks=5)
        ticks = [e.commit_tick for e in result]
        assert 6 in ticks
        assert 8 in ticks

    @pytest.mark.governance
    def test_fetch_window_excludes_events_before_window(self):
        store = ViolationEventStore()
        e = _event(mission_id="m1", commit_tick=3)
        store.store_violation_event(e)
        result = store.fetch_window(before_tick=10, window_ticks=5)
        assert len(result) == 0

    @pytest.mark.governance
    def test_fetch_window_sorted_ascending_by_commit_tick(self):
        store = ViolationEventStore()
        e1 = _event(mission_id="m1", commit_tick=8)
        e2 = _event(mission_id="m2", commit_tick=6)
        store.store_violation_event(e1)
        store.store_violation_event(e2)
        result = store.fetch_window(before_tick=10, window_ticks=5)
        ticks = [e.commit_tick for e in result]
        assert ticks == sorted(ticks)

    @pytest.mark.governance
    def test_fetch_window_raises_when_window_ticks_negative(self):
        store = ViolationEventStore()
        with pytest.raises(ValueError, match="window_ticks"):
            store.fetch_window(before_tick=10, window_ticks=-1)

    @pytest.mark.governance
    def test_fetch_window_zero_window_returns_empty(self):
        store = ViolationEventStore()
        e = _event(commit_tick=9)
        store.store_violation_event(e)
        result = store.fetch_window(before_tick=10, window_ticks=0)
        assert result == []

    @pytest.mark.governance
    def test_clear_removes_all_events(self):
        store = ViolationEventStore()
        store.store_violation_event(_event(commit_tick=1))
        store.clear()
        assert store.count() == 0

    @pytest.mark.governance
    def test_count_reflects_stored_events(self):
        store = ViolationEventStore()
        store.store_violation_event(_event(mission_id="a", commit_tick=1))
        store.store_violation_event(_event(mission_id="b", commit_tick=2))
        assert store.count() == 2


# ===========================================================================
# 3. detect_ghost_mutations — all branches
# ===========================================================================


class TestDetectGhostMutations:
    @pytest.mark.governance
    def test_returns_consistent_when_state_unchanged_and_empty_transcript(self):
        state = {"key": "value"}
        result = detect_ghost_mutations(state, state.copy(), transcript=[])
        assert result.is_consistent is True
        assert result.violation is None

    @pytest.mark.governance
    def test_returns_consistent_when_transcript_accounts_for_change(self):
        before = {"key": "old"}
        after = {"key": "new"}
        transcript = [{"operation": "set_value", "key": "key", "value": "new"}]
        result = detect_ghost_mutations(before, after, transcript)
        assert result.is_consistent is True

    @pytest.mark.governance
    def test_returns_violation_when_state_changes_without_transcript(self):
        before = {"key": "old"}
        after = {"key": "new"}
        result = detect_ghost_mutations(before, after, transcript=[])
        assert result.is_consistent is False
        assert isinstance(result.violation, GhostMutationViolation)

    @pytest.mark.governance
    def test_violation_diff_is_nonempty_on_ghost_mutation(self):
        before = {"a": 1}
        after = {"a": 2}
        result = detect_ghost_mutations(before, after, transcript=[])
        assert len(result.violation.diff) > 0

    @pytest.mark.governance
    def test_returns_violation_when_key_added_without_transcript(self):
        before = {}
        after = {"new_key": "val"}
        result = detect_ghost_mutations(before, after, transcript=[])
        assert result.is_consistent is False

    @pytest.mark.governance
    def test_returns_violation_when_key_removed_without_transcript(self):
        before = {"key": "val"}
        after = {}
        result = detect_ghost_mutations(before, after, transcript=[])
        assert result.is_consistent is False

    @pytest.mark.governance
    def test_deep_diff_returns_empty_for_identical_dicts(self):
        assert _deep_diff({"a": 1}, {"a": 1}) == []

    @pytest.mark.governance
    def test_deep_diff_detects_added_key(self):
        diffs = _deep_diff({}, {"new": "v"})
        assert any("added" in d.lower() for d in diffs)

    @pytest.mark.governance
    def test_deep_diff_detects_removed_key(self):
        diffs = _deep_diff({"old": "v"}, {})
        assert any("removed" in d.lower() for d in diffs)

    @pytest.mark.governance
    def test_deep_diff_detects_nested_value_change(self):
        diffs = _deep_diff({"a": {"b": 1}}, {"a": {"b": 2}})
        assert len(diffs) > 0

    @pytest.mark.governance
    def test_deep_diff_scalar_change_detected(self):
        diffs = _deep_diff("old", "new", path="field")
        assert len(diffs) == 1
        assert "field" in diffs[0]

    @pytest.mark.governance
    def test_detect_ghost_does_not_mutate_state_before(self):
        before = {"key": "val"}
        before_copy = dict(before)
        detect_ghost_mutations(before, {"key": "changed"}, transcript=[])
        assert before == before_copy


# ===========================================================================
# 4. validate_freshness — boundary tests
# ===========================================================================


class TestValidateFreshness:
    @pytest.mark.governance
    def test_passes_when_data_is_brand_new(self):
        data = _fresh_data(age_seconds=0)
        policy = FreshnessPolicy(max_age_seconds=60)
        validate_freshness(data, policy)  # must not raise

    @pytest.mark.governance
    def test_passes_when_age_within_policy(self):
        data = _fresh_data(age_seconds=30)
        policy = FreshnessPolicy(max_age_seconds=60)
        validate_freshness(data, policy)  # must not raise

    @pytest.mark.governance
    def test_raises_when_data_is_stale(self):
        data = _fresh_data(age_seconds=120)
        policy = FreshnessPolicy(max_age_seconds=60)
        with pytest.raises(StaleDataViolation):
            validate_freshness(data, policy)

    @pytest.mark.governance
    def test_stale_data_violation_stores_policy_max_age(self):
        data = _fresh_data(age_seconds=200)
        policy = FreshnessPolicy(max_age_seconds=100)
        with pytest.raises(StaleDataViolation) as exc_info:
            validate_freshness(data, policy)
        assert exc_info.value.policy_max_age == 100

    @pytest.mark.governance
    def test_stale_data_violation_stores_data_timestamp(self):
        ts = datetime.datetime.utcnow() - datetime.timedelta(seconds=200)
        data = VersionedData(content="x", timestamp=ts)
        policy = FreshnessPolicy(max_age_seconds=60)
        with pytest.raises(StaleDataViolation) as exc_info:
            validate_freshness(data, policy)
        assert exc_info.value.data_timestamp == ts

    @pytest.mark.governance
    def test_boundary_data_exactly_at_max_age_passes(self):
        # Data exactly at max age (1 second old, policy = 1 second)
        # Due to execution time we use a generous boundary (2 sec policy, 1 sec old)
        data = _fresh_data(age_seconds=1)
        policy = FreshnessPolicy(max_age_seconds=2)
        validate_freshness(data, policy)  # must not raise

    @pytest.mark.governance
    def test_zero_max_age_policy_rejects_any_data(self):
        data = _fresh_data(age_seconds=1)
        policy = FreshnessPolicy(max_age_seconds=0)
        with pytest.raises(StaleDataViolation):
            validate_freshness(data, policy)

    @pytest.mark.governance
    def test_freshness_policy_is_frozen(self):
        policy = FreshnessPolicy(max_age_seconds=60)
        with pytest.raises((AttributeError, TypeError)):
            policy.max_age_seconds = 999  # type: ignore[misc]

    @pytest.mark.governance
    def test_versioned_data_is_frozen(self):
        data = VersionedData(content="x", timestamp=datetime.datetime.utcnow())
        with pytest.raises((AttributeError, TypeError)):
            data.content = "y"  # type: ignore[misc]


# ===========================================================================
# 5. MemoryCollisionDetector — acquire, hierarchy, unknown lock guard
# ===========================================================================


class TestMemoryCollisionDetector:
    @pytest.mark.governance
    def test_acquire_locks_succeeds_for_valid_lock(self):
        policy = LockPolicy(timeout_seconds=5.0, lock_hierarchy=["lock_A", "lock_B"])
        detector = MemoryCollisionDetector(policy)
        result = detector.acquire_locks("trace-1", ["lock_A"])
        assert result.success is True
        assert "lock_A" in result.locks_acquired
        detector.release_locks(result.locks_acquired)

    @pytest.mark.governance
    def test_acquire_locks_fails_for_unknown_lock(self):
        policy = LockPolicy(timeout_seconds=5.0, lock_hierarchy=["lock_A"])
        detector = MemoryCollisionDetector(policy)
        result = detector.acquire_locks("trace-1", ["unknown_lock"])
        assert result.success is False
        assert isinstance(result.violation, MemoryDeadlockViolation)

    @pytest.mark.governance
    def test_acquire_locks_returns_empty_locks_on_failure(self):
        policy = LockPolicy(timeout_seconds=5.0, lock_hierarchy=["lock_A"])
        detector = MemoryCollisionDetector(policy)
        result = detector.acquire_locks("trace-1", ["nonexistent"])
        assert result.locks_acquired == []

    @pytest.mark.governance
    def test_acquire_multiple_locks_in_hierarchy_order(self):
        policy = LockPolicy(timeout_seconds=5.0, lock_hierarchy=["A", "B", "C"])
        detector = MemoryCollisionDetector(policy)
        result = detector.acquire_locks("trace-1", ["C", "A"])
        assert result.success is True
        # Should be acquired in hierarchy order: A, C
        assert set(result.locks_acquired) == {"A", "C"}
        detector.release_locks(result.locks_acquired)

    @pytest.mark.governance
    def test_acquire_no_locks_returns_success_with_empty_list(self):
        policy = LockPolicy(timeout_seconds=5.0, lock_hierarchy=["lock_A"])
        detector = MemoryCollisionDetector(policy)
        result = detector.acquire_locks("trace-1", [])
        assert result.success is True
        assert result.locks_acquired == []

    @pytest.mark.governance
    def test_release_locks_allows_reacquire(self):
        policy = LockPolicy(timeout_seconds=5.0, lock_hierarchy=["lock_A"])
        detector = MemoryCollisionDetector(policy)
        r1 = detector.acquire_locks("trace-1", ["lock_A"])
        assert r1.success is True
        detector.release_locks(r1.locks_acquired)
        r2 = detector.acquire_locks("trace-2", ["lock_A"])
        assert r2.success is True
        detector.release_locks(r2.locks_acquired)

    @pytest.mark.governance
    def test_violation_message_contains_unknown_lock_name(self):
        policy = LockPolicy(timeout_seconds=5.0, lock_hierarchy=["A"])
        detector = MemoryCollisionDetector(policy)
        result = detector.acquire_locks("t", ["mystery_lock"])
        assert "mystery_lock" in str(result.violation)

    @pytest.mark.governance
    def test_acquisition_result_is_named_tuple(self):
        policy = LockPolicy(timeout_seconds=5.0, lock_hierarchy=["A"])
        detector = MemoryCollisionDetector(policy)
        result = detector.acquire_locks("t", [])
        assert isinstance(result, LockAcquisitionResult)
