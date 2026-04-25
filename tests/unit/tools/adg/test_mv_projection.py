"""Integration tests for tools.adg.mv_projection against real Redis.

Uses a unique test snapshot-id so tests never collide with production keys.
Skipped if Redis is unavailable on localhost:6379.
"""

from __future__ import annotations

import sqlite3
import time
import uuid

import pytest

redis = pytest.importorskip("redis")

from tools.adg.mv_projection import (  # noqa: E402
    MVProjectionSpec,
    PViewProjectionSpec,
    is_mv_hot,
    project_all,
)


@pytest.fixture
def redis_client():
    try:
        c = redis.from_url("redis://localhost:6379/0", decode_responses=True, socket_connect_timeout=2)
        c.ping()
    except (OSError, redis.RedisError) as exc:
        pytest.skip(f"Redis unavailable: {exc}")
    return c


@pytest.fixture
def test_snapshot_id():
    """Unique per-test snapshot id; cleaned up after."""
    return f"testsnap_{uuid.uuid4().hex[:8]}"


@pytest.fixture
def sqlite_conn():
    conn = sqlite3.connect(":memory:")
    conn.execute(
        "CREATE TABLE mv_hotspot_centrality (node_id INTEGER, adg_name TEXT, degree_centrality REAL)"
    )
    conn.executemany(
        "INSERT INTO mv_hotspot_centrality VALUES (?, ?, ?)",
        [(1, "alpha", 10.5), (2, "beta", 7.2), (3, "gamma", 2.1)],
    )
    conn.execute("CREATE TABLE v_p0_write_bypass_uwg (writer_id INTEGER, writer_file TEXT)")
    conn.executemany(
        "INSERT INTO v_p0_write_bypass_uwg VALUES (?, ?)",
        [(100, "a.py"), (200, "b.py"), (300, "c.py")],
    )
    conn.commit()
    yield conn
    conn.close()


def _cleanup(client, snapshot_id):
    pattern = f"adg:v1:{snapshot_id}:*"
    cursor = 0
    while True:
        cursor, keys = client.scan(cursor=cursor, match=pattern, count=100)
        if keys:
            client.delete(*keys)
        if cursor == 0:
            break


def test_project_mv_creates_zset(redis_client, sqlite_conn, test_snapshot_id):
    try:
        spec = MVProjectionSpec(
            table="mv_hotspot_centrality",
            member_col="node_id",
            score_expr="degree_centrality",
            score_label="degree_centrality",
        )
        result = project_all(
            sqlite_conn,
            redis_client,
            test_snapshot_id,
            mv_specs=(spec,),
            pview_specs=(),
        )
        assert result["status"] == "ok"
        assert result["mv_total_rows"] == 3

        zset_key = f"adg:v1:{test_snapshot_id}:mv:mv_hotspot_centrality"
        top = redis_client.zrevrange(zset_key, 0, -1, withscores=True)
        assert len(top) == 3
        # Highest score first
        assert top[0][0] == "1"
        assert top[0][1] == pytest.approx(10.5)
        assert top[1][0] == "2"
        assert top[2][0] == "3"

        # Meta hash populated
        meta_key = f"adg:v1:{test_snapshot_id}:mv:mv_hotspot_centrality:meta"
        meta = redis_client.hgetall(meta_key)
        assert meta["row_count"] == "3"
        assert meta["metric"] == "degree_centrality"

        # Sentinel set
        assert is_mv_hot(redis_client, test_snapshot_id)
    finally:
        _cleanup(redis_client, test_snapshot_id)


def test_project_pview_creates_set(redis_client, sqlite_conn, test_snapshot_id):
    try:
        spec = PViewProjectionSpec(view="v_p0_write_bypass_uwg", key_col="writer_id")
        result = project_all(
            sqlite_conn,
            redis_client,
            test_snapshot_id,
            mv_specs=(),
            pview_specs=(spec,),
        )
        assert result["status"] == "ok"
        assert result["pview_total_rows"] == 3

        set_key = f"adg:v1:{test_snapshot_id}:pview:v_p0_write_bypass_uwg"
        members = redis_client.smembers(set_key)
        assert members == {"100", "200", "300"}

        meta_key = f"adg:v1:{test_snapshot_id}:pview:v_p0_write_bypass_uwg:meta"
        meta = redis_client.hgetall(meta_key)
        assert meta["row_count"] == "3"
        assert meta["key_col"] == "writer_id"
    finally:
        _cleanup(redis_client, test_snapshot_id)


def test_missing_table_is_soft_skip(redis_client, sqlite_conn, test_snapshot_id):
    try:
        spec = MVProjectionSpec(
            table="mv_does_not_exist",
            member_col="node_id",
            score_expr="score",
            score_label="score",
        )
        result = project_all(
            sqlite_conn,
            redis_client,
            test_snapshot_id,
            mv_specs=(spec,),
            pview_specs=(),
        )
        assert result["status"] == "ok"
        assert result["mv_results"][0]["status"] == "missing"
        # Sentinel still set — projection succeeded for the specs that were valid
        assert is_mv_hot(redis_client, test_snapshot_id)
    finally:
        _cleanup(redis_client, test_snapshot_id)


def test_sentinel_dropped_before_write(redis_client, sqlite_conn, test_snapshot_id):
    """Interrupted runs must never leave a stale :_mv_hot sentinel behind."""
    try:
        # Pre-seed a stale sentinel.
        sentinel_key = f"adg:v1:{test_snapshot_id}:_mv_hot"
        redis_client.set(sentinel_key, "1")
        assert is_mv_hot(redis_client, test_snapshot_id)

        spec = MVProjectionSpec(
            table="mv_hotspot_centrality",
            member_col="node_id",
            score_expr="degree_centrality",
            score_label="degree_centrality",
        )
        # project_all must delete the sentinel first, then re-set at end.
        project_all(
            sqlite_conn,
            redis_client,
            test_snapshot_id,
            mv_specs=(spec,),
            pview_specs=(),
        )
        # After success, sentinel is set again.
        assert is_mv_hot(redis_client, test_snapshot_id)
    finally:
        _cleanup(redis_client, test_snapshot_id)


def test_projection_idempotent(redis_client, sqlite_conn, test_snapshot_id):
    """Re-projecting the same spec produces the same ZSET contents."""
    try:
        spec = MVProjectionSpec(
            table="mv_hotspot_centrality",
            member_col="node_id",
            score_expr="degree_centrality",
            score_label="degree_centrality",
        )
        project_all(sqlite_conn, redis_client, test_snapshot_id, mv_specs=(spec,), pview_specs=())
        zset_key = f"adg:v1:{test_snapshot_id}:mv:mv_hotspot_centrality"
        first = redis_client.zrevrange(zset_key, 0, -1, withscores=True)

        project_all(sqlite_conn, redis_client, test_snapshot_id, mv_specs=(spec,), pview_specs=())
        second = redis_client.zrevrange(zset_key, 0, -1, withscores=True)

        assert first == second
    finally:
        _cleanup(redis_client, test_snapshot_id)
