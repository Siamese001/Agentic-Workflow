"""Tests for X1G pass^k consistency store."""

from __future__ import annotations

import pytest

from agentic_core.L3_orchestration.exit_eval.consistency import (
    BucketKey,
    PassKStore,
    TrialRecord,
)


def _key(**kw: str) -> BucketKey:
    return BucketKey(
        trajectory_class=kw.get("trajectory_class", "tc"),
        rubric_version=kw.get("rubric_version", "X1D@v1"),
        agent_version=kw.get("agent_version", "a1"),
        policy_version=kw.get("policy_version", "p1"),
    )


def test_insufficient_history_reports_no_history() -> None:
    store = PassKStore()
    key = _key()
    store.record(key, TrialRecord(run_id="r1", passed=True, timestamp=0.0))
    check = store.check(key, k=5, theta=0.95)
    assert not check.passed
    assert not check.has_history
    assert check.reason == "INSUFFICIENT_HISTORY"


def test_passes_when_all_recent_pass() -> None:
    store = PassKStore()
    key = _key()
    for i in range(5):
        store.record(key, TrialRecord(run_id=f"r{i}", passed=True, timestamp=float(i)))
    check = store.check(key, k=5, theta=0.95)
    assert check.passed
    assert check.pass_k == 1.0
    assert check.has_history


def test_fails_when_below_theta() -> None:
    store = PassKStore()
    key = _key()
    # 4 of 5 passed = 0.8, theta=0.95
    for passed in [True, True, True, False, True]:
        store.record(key, TrialRecord(run_id="r", passed=passed, timestamp=0.0))
    check = store.check(key, k=5, theta=0.95)
    assert not check.passed
    assert check.reason == "CONSISTENCY_FAIL"
    assert check.pass_k == pytest.approx(0.8)


def test_only_most_recent_k_count() -> None:
    store = PassKStore()
    key = _key()
    # Old failures, then k=3 recent passes
    for passed in [False, False, True, True, True]:
        store.record(key, TrialRecord(run_id="r", passed=passed, timestamp=0.0))
    check = store.check(key, k=3, theta=1.0)
    assert check.passed  # last 3 all passed


def test_bucket_reset_on_version_change() -> None:
    store = PassKStore()
    k1 = _key(rubric_version="X1D@v1")
    k2 = _key(rubric_version="X1D@v2")
    for _ in range(5):
        store.record(k1, TrialRecord(run_id="r", passed=True, timestamp=0.0))
    # New rubric version = new bucket = no history
    check = store.check(k2, k=5, theta=0.95)
    assert not check.has_history


def test_explicit_clear() -> None:
    store = PassKStore()
    key = _key()
    for _ in range(5):
        store.record(key, TrialRecord(run_id="r", passed=True, timestamp=0.0))
    store.clear(key)
    assert store.history(key) == ()


def test_bad_k_and_theta_rejected() -> None:
    store = PassKStore()
    key = _key()
    with pytest.raises(ValueError):
        store.check(key, k=0, theta=0.5)
    with pytest.raises(ValueError):
        store.check(key, k=5, theta=1.5)


def test_record_max_retained_caps_memory() -> None:
    store = PassKStore()
    key = _key()
    for i in range(20):
        store.record(
            key,
            TrialRecord(run_id=f"r{i}", passed=True, timestamp=0.0),
            max_retained=5,
        )
    hist = store.history(key)
    assert len(hist) == 5
    # Last 5 kept (r15..r19)
    assert hist[-1].run_id == "r19"


def test_thread_safe_concurrent_record() -> None:
    import threading

    store = PassKStore()
    key = _key()

    def worker() -> None:
        for _ in range(100):
            store.record(key, TrialRecord(run_id="r", passed=True, timestamp=0.0))

    threads = [threading.Thread(target=worker) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    # 400 records with default max_retained=100
    assert len(store.history(key)) == 100
