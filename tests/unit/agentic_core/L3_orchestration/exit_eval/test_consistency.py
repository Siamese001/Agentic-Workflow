"""Unit tests for agentic_core.L3_orchestration.exit_eval.consistency.

Wave 3.1 (plan adg-testing-hotspots-wave-plan-a7f3c1) — untested high-fan-in
exit_eval modules. ``consistency`` (fan_in=15) is the X1G ``pass^k`` store:
frozen ``TrialRecord`` / ``BucketKey`` / ``ConsistencyCheck`` carriers, the
``PassKStore`` with record/check/history/clear, and ``bucket_key_from_context``.
Covers the H6 invariant that insufficient history NEVER passes (no fallback to
a smaller k or population mean), the ValueError guard paths, and bucket reset.
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.L3_orchestration.exit_eval.consistency import (
    BucketKey,
    ConsistencyCheck,
    PassKStore,
    TrialRecord,
    bucket_key_from_context,
)


def _key(**overrides: str) -> BucketKey:
    base = {
        "trajectory_class": "answer_only",
        "rubric_version": "r1",
        "agent_version": "a1",
        "policy_version": "p1",
    }
    base.update(overrides)
    return BucketKey(**base)  # type: ignore[arg-type]


def _trial(run_id: str = "run-1", passed: bool = True, ts: float = 0.0) -> TrialRecord:
    return TrialRecord(run_id=run_id, passed=passed, timestamp=ts)


class TestFrozenCarriers:
    def test_trial_record_frozen(self) -> None:
        t = _trial()
        with pytest.raises(dataclasses.FrozenInstanceError):
            t.passed = False  # type: ignore[misc]

    def test_bucket_key_frozen_and_hashable(self) -> None:
        k = _key()
        with pytest.raises(dataclasses.FrozenInstanceError):
            k.rubric_version = "r2"  # type: ignore[misc]
        # Frozen dataclasses are hashable — usable as dict keys.
        assert {k: 1}[k] == 1

    def test_bucket_key_equality(self) -> None:
        assert _key() == _key()
        assert _key(agent_version="a2") != _key()

    def test_consistency_check_default_reason(self) -> None:
        c = ConsistencyCheck(
            passed=True, pass_k=1.0, k=3, theta=0.9, has_history=True, history_size=3,
        )
        assert c.reason == ""


class TestPassKStoreGuards:
    def test_record_rejects_nonpositive_max_retained(self) -> None:
        store = PassKStore()
        with pytest.raises(ValueError, match="max_retained must be > 0"):
            store.record(_key(), _trial(), max_retained=0)

    def test_check_rejects_nonpositive_k(self) -> None:
        store = PassKStore()
        with pytest.raises(ValueError, match="k must be > 0"):
            store.check(_key(), k=0, theta=0.5)

    @pytest.mark.parametrize("theta", [-0.01, 1.01, 2.0])
    def test_check_rejects_theta_out_of_range(self, theta: float) -> None:
        store = PassKStore()
        with pytest.raises(ValueError, match="theta must be in"):
            store.check(_key(), k=1, theta=theta)


class TestInsufficientHistory:
    def test_empty_bucket_has_no_history(self) -> None:
        store = PassKStore()
        result = store.check(_key(), k=3, theta=0.9)
        assert result.has_history is False
        assert result.passed is False
        assert result.pass_k is None
        assert result.reason == "INSUFFICIENT_HISTORY"
        assert result.history_size == 0

    def test_fewer_than_k_never_passes(self) -> None:
        store = PassKStore()
        key = _key()
        store.record(key, _trial("a", True))
        store.record(key, _trial("b", True))
        # All recorded trials passed, but only 2 < k=3 → must NOT pass.
        result = store.check(key, k=3, theta=0.5)
        assert result.has_history is False
        assert result.passed is False
        assert result.reason == "INSUFFICIENT_HISTORY"
        assert result.history_size == 2


class TestPassKComputation:
    def test_all_recent_pass_gives_pass_k_one(self) -> None:
        store = PassKStore()
        key = _key()
        for i in range(3):
            store.record(key, _trial(f"r{i}", True, ts=float(i)))
        result = store.check(key, k=3, theta=1.0)
        assert result.has_history is True
        assert result.pass_k == 1.0
        assert result.passed is True
        assert result.reason == ""

    def test_partial_passes_fraction(self) -> None:
        store = PassKStore()
        key = _key()
        store.record(key, _trial("r0", True))
        store.record(key, _trial("r1", False))
        store.record(key, _trial("r2", True))
        result = store.check(key, k=3, theta=0.9)
        assert result.pass_k == pytest.approx(2 / 3)
        assert result.passed is False
        assert result.reason == "CONSISTENCY_FAIL"

    def test_only_last_k_count(self) -> None:
        store = PassKStore()
        key = _key()
        # Older fails should not count when only the most recent k pass.
        store.record(key, _trial("old", False, ts=0.0))
        store.record(key, _trial("r1", True, ts=1.0))
        store.record(key, _trial("r2", True, ts=2.0))
        result = store.check(key, k=2, theta=1.0)
        assert result.pass_k == 1.0
        assert result.passed is True
        assert result.history_size == 2

    def test_theta_boundary_inclusive(self) -> None:
        store = PassKStore()
        key = _key()
        store.record(key, _trial("r0", True))
        store.record(key, _trial("r1", False))
        # pass_k = 0.5; theta exactly 0.5 → passed (>=).
        result = store.check(key, k=2, theta=0.5)
        assert result.pass_k == 0.5
        assert result.passed is True


class TestHistoryAndClear:
    def test_history_empty_for_unknown_key(self) -> None:
        store = PassKStore()
        assert store.history(_key()) == ()

    def test_history_snapshot_newest_last(self) -> None:
        store = PassKStore()
        key = _key()
        store.record(key, _trial("a", True, ts=0.0))
        store.record(key, _trial("b", False, ts=1.0))
        snap = store.history(key)
        assert tuple(t.run_id for t in snap) == ("a", "b")

    def test_max_retained_caps_bucket(self) -> None:
        store = PassKStore()
        key = _key()
        for i in range(5):
            store.record(key, _trial(f"r{i}", True, ts=float(i)), max_retained=3)
        snap = store.history(key)
        assert len(snap) == 3
        # Oldest two dropped — newest retained.
        assert tuple(t.run_id for t in snap) == ("r2", "r3", "r4")

    def test_clear_resets_bucket(self) -> None:
        store = PassKStore()
        key = _key()
        store.record(key, _trial("a", True))
        store.clear(key)
        assert store.history(key) == ()

    def test_clear_unknown_key_is_noop(self) -> None:
        store = PassKStore()
        store.clear(_key())  # must not raise

    def test_different_keys_isolated(self) -> None:
        store = PassKStore()
        k1 = _key(agent_version="a1")
        k2 = _key(agent_version="a2")
        store.record(k1, _trial("x", True))
        assert store.history(k1) != ()
        assert store.history(k2) == ()


class TestBucketKeyFromContext:
    def test_extracts_all_fields(self) -> None:
        ctx = {
            "trajectory_class": "with_state_diff",
            "rubric_version": "r9",
            "agent_version": "a9",
            "policy_version": "p9",
        }
        key = bucket_key_from_context(ctx)
        assert key == BucketKey("with_state_diff", "r9", "a9", "p9")

    @pytest.mark.parametrize(
        "missing",
        ["trajectory_class", "rubric_version", "agent_version", "policy_version"],
    )
    def test_missing_key_raises_keyerror(self, missing: str) -> None:
        ctx = {
            "trajectory_class": "c",
            "rubric_version": "r",
            "agent_version": "a",
            "policy_version": "p",
        }
        del ctx[missing]
        with pytest.raises(KeyError):
            bucket_key_from_context(ctx)
