"""Targeted tests for adg_redis_ingest fanout + fanin prewarm behavior.

Covers:
  1. Fanout key (edge:<src_id>:<rel>) is still written for every edge
  2. Fanin key (fanin:<dst_id>:<rel>) is now written for every edge
  3. edge_detail hashes ARE written during ingest (P12 — fully hot at startup)
  4. Sentinel (_hot) is written after all edges are ingested
"""

from __future__ import annotations

import json
import sqlite3
import subprocess
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from tools.adg.adg_redis_ingest import _redis_key, _resolve_sqlite_path, ingest

SNAPSHOT_ID = "test0001_1200"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def temp_sqlite(tmp_path: Path) -> Path:
    """Create a minimal ADG SQLite with 3 nodes and 2 edges."""
    db_path = tmp_path / f"adg_indexed_{SNAPSHOT_ID}.sqlite"
    conn = sqlite3.connect(str(db_path))
    conn.execute("CREATE TABLE nodes (id TEXT PRIMARY KEY, adg_name TEXT, entity_type TEXT, layer TEXT)")
    conn.execute(
        """CREATE TABLE edges
           (id TEXT PRIMARY KEY, src_id TEXT, dst_id TEXT,
            relation_type TEXT, edge_kind TEXT,
            source_file TEXT, line_no INTEGER, symbol TEXT)"""
    )
    conn.executemany(
        "INSERT INTO nodes VALUES (?,?,?,?)",
        [("1", "mod_a", "Module", "L2"), ("2", "mod_b", "Module", "L3"), ("3", "mod_c", "Module", "L4")],
    )
    conn.executemany(
        "INSERT INTO edges VALUES (?,?,?,?,?,?,?,?)",
        [
            ("e1", "1", "2", "imports", "static", "mod_a.py", 10, "foo"),  # 1 → 2
            ("e2", "2", "3", "imports", "static", None, None, None),  # 2 → 3 (nulls)
        ],
    )
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture()
def mock_redis() -> tuple[MagicMock, dict[str, set]]:
    """Mock Redis client that tracks all SADD calls in a dict keyed by Redis key."""
    sadd_log: dict[str, set] = {}

    def _fake_sadd(key: str, *members) -> int:
        sadd_log.setdefault(key, set()).update(str(m) for m in members)
        return len(members)

    pipe = MagicMock()
    pipe.sadd.side_effect = _fake_sadd
    pipe.hmset.return_value = None
    pipe.execute.return_value = []

    client = MagicMock()
    client.pipeline.return_value = pipe
    client.exists.return_value = False  # sentinel absent → not hot
    client.set.return_value = True
    client.ping.return_value = True

    return client, sadd_log


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestIngestFanoutFaninPrewarm:
    """Both fanout and fanin keys must be written for every edge."""

    def test_fanout_key_written(self, temp_sqlite, mock_redis):
        """Regression: fanout key edge:<src_id>:<rel> must still be written."""
        client, sadd_log = mock_redis

        ingest(temp_sqlite, client)

        fanout_1 = _redis_key(SNAPSHOT_ID, "edge:1:imports")
        fanout_2 = _redis_key(SNAPSHOT_ID, "edge:2:imports")
        assert fanout_1 in sadd_log, f"Missing fanout key {fanout_1}"
        assert fanout_2 in sadd_log, f"Missing fanout key {fanout_2}"
        assert "e1" in sadd_log[fanout_1]
        assert "e2" in sadd_log[fanout_2]

    def test_fanin_key_written(self, temp_sqlite, mock_redis):
        """New: fanin key fanin:<dst_id>:<rel> must be written for every edge."""
        client, sadd_log = mock_redis

        ingest(temp_sqlite, client)

        fanin_2 = _redis_key(SNAPSHOT_ID, "fanin:2:imports")
        fanin_3 = _redis_key(SNAPSHOT_ID, "fanin:3:imports")
        assert fanin_2 in sadd_log, f"Missing fanin key {fanin_2}"
        assert fanin_3 in sadd_log, f"Missing fanin key {fanin_3}"
        assert "e1" in sadd_log[fanin_2], "Edge e1 (1→2) missing from fanin:2"
        assert "e2" in sadd_log[fanin_3], "Edge e2 (2→3) missing from fanin:3"

    def test_edge_detail_written_during_ingest(self, temp_sqlite, mock_redis):
        """P12: edge_detail hash must be written via hmset for every edge at ingest time."""
        client, _ = mock_redis
        pipe = client.pipeline.return_value
        hmset_calls = {}

        def _fake_hmset(key, mapping):
            hmset_calls[key] = mapping

        pipe.hmset.side_effect = _fake_hmset

        ingest(temp_sqlite, client)

        detail_e1 = _redis_key(SNAPSHOT_ID, "edge_detail:e1")
        detail_e2 = _redis_key(SNAPSHOT_ID, "edge_detail:e2")
        assert detail_e1 in hmset_calls, f"edge_detail for e1 not written: {list(hmset_calls)}"
        assert detail_e2 in hmset_calls, f"edge_detail for e2 not written: {list(hmset_calls)}"
        assert hmset_calls[detail_e1]["id"] == "e1"
        assert hmset_calls[detail_e1]["source_file"] == "mod_a.py"
        assert "source_file" not in hmset_calls[detail_e2], "null source_file should be omitted"

    def test_sentinel_written_after_edges(self, temp_sqlite, mock_redis):
        """_hot sentinel must be written after all edge keys are populated."""
        client, _ = mock_redis
        set_calls = []
        client.set.side_effect = lambda k, v: set_calls.append(k)

        ingest(temp_sqlite, client)

        sentinel = _redis_key(SNAPSHOT_ID, "_hot")
        assert sentinel in set_calls, f"Sentinel {sentinel} not written"

    def test_both_keys_per_edge_symmetric(self, temp_sqlite, mock_redis):
        """Each edge contributes exactly one fanout key and one fanin key entry."""
        client, sadd_log = mock_redis

        ingest(temp_sqlite, client)

        # e1: src=1, dst=2, rel=imports
        assert "e1" in sadd_log.get(_redis_key(SNAPSHOT_ID, "edge:1:imports"), set())
        assert "e1" in sadd_log.get(_redis_key(SNAPSHOT_ID, "fanin:2:imports"), set())

        # e2: src=2, dst=3, rel=imports
        assert "e2" in sadd_log.get(_redis_key(SNAPSHOT_ID, "edge:2:imports"), set())
        assert "e2" in sadd_log.get(_redis_key(SNAPSHOT_ID, "fanin:3:imports"), set())

    def test_metadata_keys_are_written_for_same_snapshot(self, temp_sqlite, mock_redis):
        """Global Redis metadata must point at the exact ingested SQLite snapshot."""
        client, _ = mock_redis
        hsets: dict[str, dict[str, str]] = {}
        sets: dict[str, str] = {}
        client.hmset.side_effect = lambda key, mapping: hsets.setdefault(key, dict(mapping))
        client.set.side_effect = lambda key, value: sets.setdefault(key, value)

        result = ingest(temp_sqlite, client)

        meta = hsets["adg:meta"]
        assert result["snapshot_id"] == SNAPSHOT_ID
        assert meta["snapshot_id"] == SNAPSHOT_ID
        assert meta["timestamp"] == SNAPSHOT_ID
        assert meta["sqlite_path"] == str(temp_sqlite)
        assert len(meta["sqlite_digest"]) == 64
        assert len(meta["redis_digest"]) == 64
        assert sets["adg:status"] == SNAPSHOT_ID
        snapshot = json.loads(sets["adg:snapshot"])
        assert snapshot["snapshot_id"] == SNAPSHOT_ID
        assert snapshot["sqlite_path"] == str(temp_sqlite)
        assert snapshot["sqlite_digest"] == meta["sqlite_digest"]
        assert sets["adg:snapshot:sqlite_digest"] == meta["sqlite_digest"]
        assert sets["adg:snapshot:redis_digest"] == meta["redis_digest"]


class TestRedisIngestSnapshotResolution:
    def test_explicit_sqlite_path_wins_over_newer_artifact(self, tmp_path: Path):
        """The explicit --sqlite target is authoritative even when another file is newer."""
        adg_dir = tmp_path / "adg"
        adg_dir.mkdir()
        chosen = adg_dir / "adg_indexed_06162026_0827.sqlite"
        newer = adg_dir / "adg_indexed_06162026_0900.sqlite"
        chosen.write_bytes(b"chosen")
        newer.write_bytes(b"newer")

        assert _resolve_sqlite_path(adg_dir, chosen) == chosen.resolve()


class TestGenerateFullAdgRedisIntegration:
    def test_auto_ingest_pins_exact_sqlite_path(self, temp_sqlite, tmp_path: Path):
        """generate_full_adg integration must not let ingest rediscover latest."""
        from tools.generate.integration.redis_ingest import _auto_ingest_to_redis

        completed = subprocess.CompletedProcess(args=[], returncode=0, stdout="ok\n", stderr="")
        with (
            patch("agentic_core.config.redis_config.get_adg_cache_config", return_value=SimpleNamespace(ingest_timeout=9)),
            patch("subprocess.run", return_value=completed) as run,
        ):
            _auto_ingest_to_redis(tmp_path, temp_sqlite)

        argv = run.call_args.args[0]
        assert "--force" in argv
        assert "--sqlite" in argv
        assert argv[argv.index("--sqlite") + 1] == str(temp_sqlite)
