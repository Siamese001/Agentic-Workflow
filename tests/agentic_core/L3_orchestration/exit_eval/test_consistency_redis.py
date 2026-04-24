"""Tests for the Redis-backed PassKStore."""

from __future__ import annotations

import pytest

from agentic_core.L3_orchestration.exit_eval.consistency import (
    BucketKey,
    TrialRecord,
)
from agentic_core.L3_orchestration.exit_eval.consistency_redis import (
    DEFAULT_KEY_PREFIX,
    RedisPassKStore,
    StoreBackendError,
)

fakeredis = pytest.importorskip("fakeredis")


@pytest.fixture
def redis_client():
    return fakeredis.FakeRedis()


@pytest.fixture
def store(redis_client):
    return RedisPassKStore(redis_client, key_prefix="test:passk")


def _key(**kw) -> BucketKey:
    base = {
        "trajectory_class": "demo",
        "rubric_version": "X1D@v1",
        "agent_version": "agent-1",
        "policy_version": "pol-1",
    }
    base.update(kw)
    return BucketKey(**base)


def _trial(run_id: str = "r1", passed: bool = True, ts: float = 1.0) -> TrialRecord:
    return TrialRecord(run_id=run_id, passed=passed, timestamp=ts)


class TestContract:
    def test_requires_client(self) -> None:
        with pytest.raises(ValueError):
            RedisPassKStore(None)  # type: ignore[arg-type]

    def test_default_prefix_constant_stable(self) -> None:
        assert DEFAULT_KEY_PREFIX == "exit_eval:passk"


class TestRecordAndHistory:
    def test_record_then_history(self, store) -> None:
        k = _key()
        store.record(k, _trial("r1", True, 1.0))
        store.record(k, _trial("r2", False, 2.0))
        hist = store.history(k)
        assert [t.run_id for t in hist] == ["r1", "r2"]
        assert [t.passed for t in hist] == [True, False]

    def test_ltrim_caps_bucket(self, store) -> None:
        k = _key()
        for i in range(10):
            store.record(k, _trial(f"r{i}", True, float(i)), max_retained=5)
        hist = store.history(k)
        assert len(hist) == 5
        # Newest 5 retained
        assert [t.run_id for t in hist] == ["r5", "r6", "r7", "r8", "r9"]

    def test_max_retained_must_be_positive(self, store) -> None:
        with pytest.raises(ValueError):
            store.record(_key(), _trial(), max_retained=0)


class TestCheck:
    def test_insufficient_history_routes_hitl(self, store) -> None:
        k = _key()
        store.record(k, _trial("r1", True, 1.0))
        result = store.check(k, k=3, theta=0.8)
        assert not result.has_history
        assert result.reason == "INSUFFICIENT_HISTORY"
        assert result.history_size == 1
        assert result.pass_k is None

    def test_pass_k_all_pass(self, store) -> None:
        k = _key()
        for i in range(5):
            store.record(k, _trial(f"r{i}", True, float(i)))
        result = store.check(k, k=5, theta=0.8)
        assert result.has_history
        assert result.passed
        assert result.pass_k == 1.0

    def test_pass_k_fraction_below_theta(self, store) -> None:
        k = _key()
        # 2 of 5 pass → pass_k = 0.4
        for i, p in enumerate([True, True, False, False, False]):
            store.record(k, _trial(f"r{i}", p, float(i)))
        result = store.check(k, k=5, theta=0.8)
        assert result.has_history
        assert not result.passed
        assert result.pass_k == pytest.approx(0.4)
        assert result.reason == "CONSISTENCY_FAIL"

    def test_uses_newest_k(self, store) -> None:
        k = _key()
        # First 10 failing, last 5 passing — window of 5 should pass.
        for i in range(10):
            store.record(k, _trial(f"old-{i}", False, float(i)), max_retained=20)
        for i in range(5):
            store.record(k, _trial(f"new-{i}", True, float(10 + i)), max_retained=20)
        result = store.check(k, k=5, theta=1.0)
        assert result.passed
        assert result.pass_k == 1.0

    def test_invalid_params(self, store) -> None:
        with pytest.raises(ValueError):
            store.check(_key(), k=0, theta=0.5)
        with pytest.raises(ValueError):
            store.check(_key(), k=3, theta=1.5)


class TestBucketIsolation:
    def test_different_agent_version_different_bucket(self, store) -> None:
        k1 = _key(agent_version="A")
        k2 = _key(agent_version="B")
        store.record(k1, _trial("a1", True, 1.0))
        store.record(k2, _trial("b1", False, 1.0))
        assert len(store.history(k1)) == 1
        assert len(store.history(k2)) == 1
        assert store.history(k1)[0].run_id == "a1"
        assert store.history(k2)[0].run_id == "b1"

    def test_clear_only_targets_one_bucket(self, store) -> None:
        k1 = _key(agent_version="A")
        k2 = _key(agent_version="B")
        store.record(k1, _trial("a1", True, 1.0))
        store.record(k2, _trial("b1", True, 1.0))
        store.clear(k1)
        assert store.history(k1) == ()
        assert len(store.history(k2)) == 1


class TestIterBuckets:
    def test_lists_distinct_buckets(self, store) -> None:
        store.record(_key(agent_version="A"), _trial())
        store.record(_key(agent_version="B"), _trial())
        store.record(_key(policy_version="P2"), _trial())
        buckets = set(store.iter_buckets())
        # 3 distinct (A/pol-1), (B/pol-1), (agent-1/P2)
        assert len(buckets) == 3


class TestErrorPropagation:
    def test_record_wraps_client_error(self, redis_client) -> None:
        broken = RedisPassKStore(redis_client, key_prefix="t:broken")

        class Boom:
            def rpush(self, *a, **kw):
                raise RuntimeError("simulated disconnect")

        broken._client = Boom()  # type: ignore[assignment]
        with pytest.raises(StoreBackendError, match="record failed"):
            broken.record(_key(), _trial())

    def test_check_wraps_client_error(self, redis_client) -> None:
        broken = RedisPassKStore(redis_client, key_prefix="t:broken")

        class Boom:
            def llen(self, *a, **kw):
                raise RuntimeError("boom")

        broken._client = Boom()  # type: ignore[assignment]
        with pytest.raises(StoreBackendError, match="check failed"):
            broken.check(_key(), k=3, theta=0.5)

    def test_corrupt_payload_raises(self, redis_client, store) -> None:
        # Inject a garbage entry directly — bypasses the encoder.
        key = _key()
        raw_key = f"test:passk:{key.trajectory_class}:{key.rubric_version}:"\
                  f"{key.agent_version}:{key.policy_version}"
        redis_client.rpush(raw_key, b"not-json")
        redis_client.rpush(raw_key, b"still-not-json")
        redis_client.rpush(raw_key, b"another")
        with pytest.raises(StoreBackendError, match="corrupt payload"):
            store.check(key, k=3, theta=0.5)
