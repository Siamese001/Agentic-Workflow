"""Tests for SqlitePassKStore — durable PassKStore backend (ADR-054)."""

from __future__ import annotations

import threading
from pathlib import Path

import pytest

from agentic_core.L3_orchestration.exit_eval.consistency import (
    BucketKey,
    TrialRecord,
)
from agentic_core.L3_orchestration.exit_eval.consistency_sqlite import (
    SqlitePassKStore,
)


def _key(**kw: str) -> BucketKey:
    return BucketKey(
        trajectory_class=kw.get("trajectory_class", "tc"),
        rubric_version=kw.get("rubric_version", "X1D@v1"),
        agent_version=kw.get("agent_version", "a1"),
        policy_version=kw.get("policy_version", "p1"),
    )


def test_insufficient_history(tmp_path: Path) -> None:
    with SqlitePassKStore(tmp_path / "s.sqlite") as store:
        store.record(_key(), TrialRecord("r1", True, 0.0))
        check = store.check(_key(), k=5, theta=0.95)
        assert not check.passed
        assert not check.has_history
        assert check.reason == "INSUFFICIENT_HISTORY"


def test_pass_k_all_pass(tmp_path: Path) -> None:
    with SqlitePassKStore(tmp_path / "s.sqlite") as store:
        for i in range(5):
            store.record(_key(), TrialRecord(f"r{i}", True, float(i)))
        check = store.check(_key(), k=5, theta=0.95)
        assert check.passed
        assert check.pass_k == 1.0


def test_fail_below_theta(tmp_path: Path) -> None:
    with SqlitePassKStore(tmp_path / "s.sqlite") as store:
        for passed in [True, True, True, False, True]:
            store.record(_key(), TrialRecord("r", passed, 0.0))
        check = store.check(_key(), k=5, theta=0.95)
        assert not check.passed
        assert check.reason == "CONSISTENCY_FAIL"
        assert check.pass_k == pytest.approx(0.8)


def test_only_most_recent_k_count(tmp_path: Path) -> None:
    with SqlitePassKStore(tmp_path / "s.sqlite") as store:
        for passed in [False, False, True, True, True]:
            store.record(_key(), TrialRecord("r", passed, 0.0))
        check = store.check(_key(), k=3, theta=1.0)
        assert check.passed  # last 3 all passed


def test_bucket_reset_on_version_change(tmp_path: Path) -> None:
    with SqlitePassKStore(tmp_path / "s.sqlite") as store:
        k1 = _key(rubric_version="v1")
        k2 = _key(rubric_version="v2")
        for _ in range(5):
            store.record(k1, TrialRecord("r", True, 0.0))
        check = store.check(k2, k=5, theta=0.95)
        assert not check.has_history


def test_history_persists_across_reopen(tmp_path: Path) -> None:
    """The whole point of the durable backend: survives restarts."""
    path = tmp_path / "s.sqlite"
    key = _key()
    with SqlitePassKStore(path) as store:
        for i in range(5):
            store.record(key, TrialRecord(f"r{i}", True, float(i)))
    # Reopen — simulates a process restart
    with SqlitePassKStore(path) as store2:
        check = store2.check(key, k=5, theta=0.95)
        assert check.passed
        assert check.pass_k == 1.0
        hist = store2.history(key)
        assert len(hist) == 5
        assert hist[0].run_id == "r0"
        assert hist[-1].run_id == "r4"


def test_clear_removes_bucket(tmp_path: Path) -> None:
    with SqlitePassKStore(tmp_path / "s.sqlite") as store:
        key = _key()
        for _ in range(5):
            store.record(key, TrialRecord("r", True, 0.0))
        store.clear(key)
        assert store.history(key) == ()
        assert not store.check(key, k=5, theta=0.95).has_history


def test_max_retained_caps_rows(tmp_path: Path) -> None:
    with SqlitePassKStore(tmp_path / "s.sqlite") as store:
        key = _key()
        for i in range(20):
            store.record(key, TrialRecord(f"r{i}", True, 0.0), max_retained=5)
        hist = store.history(key)
        assert len(hist) == 5
        # Newest kept (r15..r19)
        ids = {h.run_id for h in hist}
        assert ids == {"r15", "r16", "r17", "r18", "r19"}


def test_bad_k_and_theta(tmp_path: Path) -> None:
    with SqlitePassKStore(tmp_path / "s.sqlite") as store:
        with pytest.raises(ValueError):
            store.check(_key(), k=0, theta=0.5)
        with pytest.raises(ValueError):
            store.check(_key(), k=5, theta=1.5)


def test_all_buckets_enumeration(tmp_path: Path) -> None:
    with SqlitePassKStore(tmp_path / "s.sqlite") as store:
        k1 = _key(trajectory_class="tc1")
        k2 = _key(trajectory_class="tc2")
        store.record(k1, TrialRecord("r", True, 0.0))
        store.record(k2, TrialRecord("r", True, 0.0))
        buckets = set(store.all_buckets())
        assert k1 in buckets and k2 in buckets


def test_concurrent_record_thread_safe(tmp_path: Path) -> None:
    """Serialized writes under threading.Lock; no 'database is locked'."""
    store = SqlitePassKStore(tmp_path / "s.sqlite")
    key = _key()

    errors: list[Exception] = []

    def worker(tag: str) -> None:
        try:
            for i in range(50):
                store.record(
                    key,
                    TrialRecord(f"{tag}-{i}", True, float(i)),
                    max_retained=1000,
                )
        except (RuntimeError, OSError, ValueError) as exc:
            errors.append(exc)

    threads = [threading.Thread(target=worker, args=(f"t{t}",)) for t in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert errors == []
    # 4 threads × 50 = 200 records
    assert len(store.history(key)) == 200
    store.close()


def test_close_is_idempotent(tmp_path: Path) -> None:
    store = SqlitePassKStore(tmp_path / "s.sqlite")
    store.close()
    store.close()  # must not raise


def test_read_after_close_raises(tmp_path: Path) -> None:
    """After close, the backend must fail closed (not silently succeed)."""
    store = SqlitePassKStore(tmp_path / "s.sqlite")
    store.record(_key(), TrialRecord("r", True, 0.0))
    store.close()
    with pytest.raises(RuntimeError, match="check"):
        store.check(_key(), k=5, theta=0.95)
