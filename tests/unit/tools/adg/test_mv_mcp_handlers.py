"""Unit tests for MV/P-view MCP tool handlers (W4).

Uses a temp isolated snapshot-id with a seeded projection so tests never collide
with the live production projection.
"""

from __future__ import annotations

import sqlite3
import uuid
from unittest.mock import patch

import pytest

redis = pytest.importorskip("redis")

from tools.adg.mv_projection import (  # noqa: E402
    MVProjectionSpec,
    PViewProjectionSpec,
    project_all,
)
from tools.adg.mv_reader import MVRedisReader  # noqa: E402


@pytest.fixture
def redis_client():
    try:
        c = redis.from_url("redis://localhost:6379/0", decode_responses=True, socket_connect_timeout=2)
        c.ping()
    except (OSError, redis.RedisError) as exc:
        pytest.skip(f"Redis unavailable: {exc}")
    return c


@pytest.fixture
def seeded_snapshot(redis_client):
    """Seed an isolated snapshot with one MV and one P-view; yield snap-id."""
    snap = f"testsnap_{uuid.uuid4().hex[:8]}"
    conn = sqlite3.connect(":memory:")
    conn.execute(
        "CREATE TABLE mv_hotspot_centrality (node_id INTEGER, adg_name TEXT, degree_centrality REAL)"
    )
    conn.executemany(
        "INSERT INTO mv_hotspot_centrality VALUES (?, ?, ?)",
        [(10, "alpha", 5.5), (20, "beta", 3.3), (30, "gamma", 1.1)],
    )
    conn.execute("CREATE TABLE v_p0_write_bypass_uwg (writer_id INTEGER, writer_file TEXT)")
    conn.executemany(
        "INSERT INTO v_p0_write_bypass_uwg VALUES (?, ?)",
        [(100, "a.py"), (200, "b.py")],
    )
    conn.commit()

    project_all(
        conn,
        redis_client,
        snap,
        mv_specs=(
            MVProjectionSpec(
                table="mv_hotspot_centrality",
                member_col="node_id",
                score_expr="degree_centrality",
                score_label="degree_centrality",
            ),
        ),
        pview_specs=(PViewProjectionSpec(view="v_p0_write_bypass_uwg", key_col="writer_id"),),
    )
    conn.close()
    yield snap
    # cleanup
    pattern = f"adg:v1:{snap}:*"
    cursor = 0
    while True:
        cursor, keys = redis_client.scan(cursor=cursor, match=pattern, count=100)
        if keys:
            redis_client.delete(*keys)
        if cursor == 0:
            break


def _with_patched_snapshot(snap, fn, *args, **kwargs):
    """Run an MCP handler with `_current_snapshot_id` patched to `snap`."""
    from tools.adg.mcp import tool_handlers as h

    # Also reset the module-level reader so it reconnects cleanly for each test.
    h._mv_reader = MVRedisReader()
    with patch.object(h, "_current_snapshot_id", return_value=snap):
        return fn(*args, **kwargs)


def test_adg_mv_top_returns_ranked_results(seeded_snapshot):
    from tools.adg.mcp import tool_handlers as h

    result = _with_patched_snapshot(seeded_snapshot, h.adg_mv_top, "mv_hotspot_centrality", 10)
    assert result["status"] == "ok"
    assert result["backend_used"] == "redis_cache"
    data = result["data"]
    assert data["mv_name"] == "mv_hotspot_centrality"
    assert data["metric"] == "degree_centrality"
    results = data["results"]
    assert len(results) == 3
    assert results[0]["member"] == "10"
    assert results[0]["score"] == pytest.approx(5.5)
    assert results[1]["member"] == "20"
    assert results[2]["member"] == "30"


def test_adg_mv_top_empty_mv_returns_empty_list(seeded_snapshot):
    from tools.adg.mcp import tool_handlers as h

    # Query an MV name that was not projected in this snapshot.
    result = _with_patched_snapshot(seeded_snapshot, h.adg_mv_top, "mv_nonexistent", 5)
    assert result["status"] == "ok"
    assert result["data"]["results"] == []


def test_adg_pview_members_returns_full_set(seeded_snapshot):
    from tools.adg.mcp import tool_handlers as h

    result = _with_patched_snapshot(seeded_snapshot, h.adg_pview_members, "v_p0_write_bypass_uwg", 500)
    assert result["status"] == "ok"
    assert result["data"]["total_members"] == 2
    assert set(result["data"]["members"]) == {"100", "200"}


def test_adg_pview_members_respects_limit(seeded_snapshot):
    from tools.adg.mcp import tool_handlers as h

    result = _with_patched_snapshot(seeded_snapshot, h.adg_pview_members, "v_p0_write_bypass_uwg", 1)
    assert result["status"] == "ok"
    assert result["data"]["total_members"] == 2
    assert result["data"]["returned"] == 1
    assert len(result["data"]["members"]) == 1


def test_adg_pview_contains_hit(seeded_snapshot):
    from tools.adg.mcp import tool_handlers as h

    result = _with_patched_snapshot(seeded_snapshot, h.adg_pview_contains, "v_p0_write_bypass_uwg", "100")
    assert result["status"] == "ok"
    assert result["data"]["contained"] is True


def test_adg_pview_contains_miss(seeded_snapshot):
    from tools.adg.mcp import tool_handlers as h

    result = _with_patched_snapshot(seeded_snapshot, h.adg_pview_contains, "v_p0_write_bypass_uwg", "999")
    assert result["status"] == "ok"
    assert result["data"]["contained"] is False


def test_adg_mv_projection_status_reports_state(seeded_snapshot):
    from tools.adg.mcp import tool_handlers as h

    result = _with_patched_snapshot(seeded_snapshot, h.adg_mv_projection_status)
    assert result["status"] == "ok"
    data = result["data"]
    assert data["hot"] is True
    mv_names = {mv["name"] for mv in data["mvs"]}
    pview_names = {pv["name"] for pv in data["pviews"]}
    assert "mv_hotspot_centrality" in mv_names
    assert "v_p0_write_bypass_uwg" in pview_names
    mv_row = next(mv for mv in data["mvs"] if mv["name"] == "mv_hotspot_centrality")
    assert mv_row["size"] == 3
    assert mv_row["metric"] == "degree_centrality"
    pv_row = next(pv for pv in data["pviews"] if pv["name"] == "v_p0_write_bypass_uwg")
    assert pv_row["size"] == 2


def test_adg_mv_top_errors_when_snapshot_missing():
    from tools.adg.mcp import tool_handlers as h

    with patch.object(h, "_current_snapshot_id", return_value=None):
        result = h.adg_mv_top("mv_hotspot_centrality", 10)
    assert result["status"] == "error"
    assert "snapshot" in result["message"].lower()
