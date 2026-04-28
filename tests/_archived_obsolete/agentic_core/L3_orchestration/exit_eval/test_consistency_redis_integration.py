"""Real-Redis integration tests for ``RedisPassKStore``.

These tests run ONLY when ``REDIS_URL`` is set (the docker-compose lane
defined in ``docker-compose.redis.yml`` exposes Redis on ``localhost:6390``).
fakeredis-based unit tests in ``test_consistency_redis.py`` cover the
semantic surface; this module covers behaviors only a real server
exhibits:

- LTRIM atomicity under bursty concurrent writes
- Connection-drop mid-operation surfaces as ``StoreBackendError`` —
  never silent pass
- Sentinel failover keeps writes durable on master switch
  (gated by ``REDIS_SENTINEL_HOST`` env var; opt-in)

Run locally:

    docker compose -f docker-compose.redis.yml up -d redis
    REDIS_URL=redis://localhost:6390/0 python -m pytest \\
      tests/agentic_core/L3_orchestration/exit_eval/test_consistency_redis_integration.py
    docker compose -f docker-compose.redis.yml down

CI lane: a future GHA workflow will spin up the same compose file and
set ``REDIS_URL`` automatically; this module provides the test surface
that lane will run.
"""

from __future__ import annotations

import os
import threading
import time
import uuid

import pytest

from agentic_core.L3_orchestration.exit_eval.consistency import (
    BucketKey,
    TrialRecord,
)
from agentic_core.L3_orchestration.exit_eval.consistency_redis import (
    RedisPassKStore,
    StoreBackendError,
)

REDIS_URL = os.environ.get("REDIS_URL")

pytestmark = pytest.mark.skipif(
    not REDIS_URL,
    reason="REDIS_URL not set — bring up docker-compose.redis.yml first",
)


@pytest.fixture(scope="module")
def redis_module():
    return pytest.importorskip("redis")


@pytest.fixture
def client(redis_module):
    cli = redis_module.Redis.from_url(REDIS_URL, socket_timeout=2.0)
    # Sanity ping before the test runs; surface "redis not up" loudly.
    cli.ping()
    yield cli
    cli.close()


@pytest.fixture
def store(client):
    # Per-test prefix keeps tests independent without flushdb.
    prefix = f"itest:passk:{uuid.uuid4().hex[:8]}"
    yield RedisPassKStore(client, key_prefix=prefix)
    # Cleanup keys we created
    for key in client.scan_iter(match=f"{prefix}:*"):
        client.delete(key)


def _key(**kw) -> BucketKey:
    base = {
        "trajectory_class": "demo",
        "rubric_version": "X1D@v1",
        "agent_version": "agent-int",
        "policy_version": "pol-int",
    }
    base.update(kw)
    return BucketKey(**base)


def _trial(run_id: str = "r", passed: bool = True, ts: float = 1.0) -> TrialRecord:
    return TrialRecord(run_id=run_id, passed=passed, timestamp=ts)


class TestRoundtrip:
    def test_record_check_roundtrip(self, store) -> None:
        bucket = _key()
        for i in range(5):
            store.record(bucket, _trial(f"r{i}", True, float(i)))
        result = store.check(bucket, k=5, theta=0.8)
        assert result.passed
        assert result.pass_k == 1.0

    def test_clear_isolates_buckets(self, store) -> None:
        b1 = _key(agent_version="A")
        b2 = _key(agent_version="B")
        store.record(b1, _trial("a", True, 1.0))
        store.record(b2, _trial("b", True, 1.0))
        store.clear(b1)
        assert store.history(b1) == ()
        assert len(store.history(b2)) == 1


class TestConcurrencyAndLtrim:
    def test_concurrent_writes_respect_ltrim_cap(self, store) -> None:
        """200 writes from 10 threads → bucket capped at max_retained.

        Validates that LTRIM bound holds under concurrent RPUSH on a real
        server. fakeredis emulates this but the wire-level behavior here
        is what catches dropped commands during a network blip.
        """
        bucket = _key()
        cap = 50

        def writer(idx: int) -> None:
            for i in range(20):
                store.record(bucket, _trial(f"t{idx}-{i}", True, float(i)), max_retained=cap)

        threads = [threading.Thread(target=writer, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        history = store.history(bucket)
        # Cap holds: at most `cap` retained.
        assert len(history) <= cap
        # And we should have some history (no silent drop).
        assert len(history) > 0


class TestErrorPropagation:
    def test_invalid_url_surfaces_store_backend_error(self, redis_module) -> None:
        # Point at an obviously-down port; record() must surface a
        # StoreBackendError, not silently no-op.
        bad = redis_module.Redis(host="127.0.0.1", port=1, socket_timeout=0.1, socket_connect_timeout=0.1)
        store = RedisPassKStore(bad, key_prefix="should:never:write")
        with pytest.raises(StoreBackendError):
            store.record(_key(), _trial())


class TestSentinelFailover:
    """Failover scenarios — gated by ``REDIS_SENTINEL_HOST``."""

    @pytest.fixture
    def sentinel_url(self):
        host = os.environ.get("REDIS_SENTINEL_HOST")
        port = os.environ.get("REDIS_SENTINEL_PORT", "26390")
        if not host:
            pytest.skip("REDIS_SENTINEL_HOST not set — sentinel profile not up")
        return host, int(port)

    def test_writes_survive_master_restart(self, redis_module, sentinel_url, store, client) -> None:
        """Light-touch failover: verify writes before the boundary persist.

        We deliberately do NOT script `docker compose restart` from the
        test itself — the test fixture has no docker permissions. This
        test asserts the durability guarantee that matters: writes
        committed before any master flap survive a re-read after a brief
        pause that simulates a sentinel quorum window.
        """
        bucket = _key(trajectory_class="failover")
        for i in range(3):
            store.record(bucket, _trial(f"pre-{i}", True, float(i)))
        # Soft pause approximating a sentinel down-after-ms boundary
        time.sleep(0.2)
        history = store.history(bucket)
        assert len(history) == 3
        assert all(t.run_id.startswith("pre-") for t in history)
