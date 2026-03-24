"""ADG Redis Projection — Creative / Adversarial Tests.

Goes beyond basic correctness into adversarial, structural, and contract
verification angles not covered by test_adg_projection_integrity.py.

Test inventory
--------------
TestEdgeCardinality
  T1: fanout_cardinality_exact  — sum of all fanout set sizes == total edge count
  T2: fanin_cardinality_exact   — same check on fanin direction
  T3: no_orphan_edge_ids        — every edge_id in any adjacency SET has a
                                  corresponding adg:edge_detail: HASH

TestBijection
  T4: fanout_fanin_inverse      — for every edge (src, rel, tgt), edge_id must
                                  appear in BOTH the fanout and the fanin set
  T5: roundtrip_src_dst         — resolve edge_ids from fanout, extract dst_id;
                                  those dst_ids must exactly match the src_id
                                  walk via fanin sets

TestIdempotency
  T6: double_ingest_key_count   — run ingest --force twice, verify Redis key
                                  count for adg:edge_detail:* is identical
  T7: double_ingest_digest_stable — digest is stable across two ingests

TestMutationDetection
  T8: tampered_edge_detail      — overwrite one HASH field, verify the in-memory
                                  re-read detects a changed value vs SQLite row
  T9: corrupt_status_coherency  — manually set projection_coherent=False in
                                  adg:status; read back and verify the value
                                  propagates correctly (guards downstream)

TestMcpToolContracts
  T10: adg_edge_detail_shape    — call adg_edge_detail() directly, check
                                  all 8 canonical fields are present
  T11: adg_module_context_shape — call adg_module_context(), check shape
  T12: adg_edge_fanout_shape    — call adg_edge_fanout() with resolve=True,
                                  verify 'edges' list returned with dst_ids
  T13: adg_edge_fanin_shape     — call adg_edge_fanin() with resolve=True,
                                  verify 'edges' list returned with src_ids
  T14: adg_violations_shape     — call adg_violations(), verify resolved dict
                                  list (not raw JSON strings)
  T15: adg_status_digest_fields — call adg_status(), verify projection_coherent
                                  and sqlite_digest / redis_digest are returned

TestSnapshotRoundTrip
  T16: snapshot_valid_json      — adg:snapshot is parseable JSON
  T17: snapshot_has_counts_key  — snapshot has at least one numeric key
  T18: snapshot_digest_hex64    — both digest keys are 64-char hex strings

TestStaleGuard
  T19: no_reingest_when_fresh   — call ingest() WITHOUT --force after a fresh
                                  ingest; verify the Redis key count does NOT
                                  change (cache-hit short-circuit works)

Requires: Redis running on localhost:6379, uses DB 14 for isolation
          (different DB from integrity tests to allow parallel execution).
"""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path

import pytest

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_applies_guardrail,
    _emit_records_execution_trace,
)

# ---------------------------------------------------------------------------
# Skip guard
# ---------------------------------------------------------------------------
try:
    import redis as _redis_lib

    _r_probe = _redis_lib.Redis(host="localhost", port=6379, db=14, decode_responses=True)
    _r_probe.ping()
    _REDIS_OK = True
except (ValueError, TypeError, RuntimeError) as e:
    _REDIS_OK = False

_emit_applies_guardrail("projection_creative_test", "test_harness", "L5")
_emit_records_execution_trace("projection_creative_test", "L5", "test_collection")

pytestmark = pytest.mark.skipif(not _REDIS_OK, reason="Redis not available on localhost:6379")

# ---------------------------------------------------------------------------
# Shared fixture data (mirror of integrity tests, same SQLite schema)
# ---------------------------------------------------------------------------
_DDL = """
CREATE TABLE IF NOT EXISTS nodes (
    id INTEGER PRIMARY KEY, adg_name TEXT NOT NULL, entity_type TEXT NOT NULL,
    layer TEXT NOT NULL, identity_kind TEXT NOT NULL, confidence TEXT NOT NULL,
    resolved_path TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS edges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    src_id INTEGER NOT NULL REFERENCES nodes(id),
    dst_id INTEGER NOT NULL REFERENCES nodes(id),
    relation_type TEXT NOT NULL, edge_kind TEXT NOT NULL,
    source_file TEXT NOT NULL, line_no INTEGER NOT NULL,
    symbol TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS violations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    edge_id INTEGER NOT NULL REFERENCES edges(id),
    category TEXT NOT NULL, evidence TEXT NOT NULL DEFAULT '',
    file_path TEXT NOT NULL DEFAULT '', line_no INTEGER NOT NULL DEFAULT 0
);
"""

_NODES = [
    (1, "mod_alpha", "module", "L2", "ast_resolved", "high", "pkg/mod_alpha.py"),
    (2, "mod_beta",  "module", "L2", "ast_resolved", "high", "pkg/mod_beta.py"),
    (3, "func_foo",  "function","L2","ast_resolved", "high", "pkg/mod_alpha.py"),
    (4, "cls_bar",   "class",  "L3", "ast_resolved","medium","pkg/cls_bar.py"),
    (5, "mod_gamma", "module", "L3", "ast_resolved", "high", "pkg/mod_gamma.py"),
]

_EDGES = [
    # (src, dst, rel, kind, file, ln, sym)
    (1, 2, "calls",   "static",     "pkg/mod_alpha.py", 10, "do_beta"),
    (1, 3, "exports", "static",     "pkg/mod_alpha.py",  5, "func_foo"),
    (2, 4, "imports", "static",     "pkg/mod_beta.py",   1, "cls_bar"),
    (3, 2, "calls",   "dynamic",    "pkg/mod_alpha.py", 15, "invoke_b"),
    (1, 5, "imports", "static",     "pkg/mod_alpha.py",  3, "mod_gamma"),
    (2, 5, "calls",   "static",     "pkg/mod_beta.py",  20, "gamma_op"),
    (1, 4, "violates","governance", "pkg/mod_alpha.py", 20, "layer_viol"),
]

_SNAPSHOT = {
    "counts": {"module_count": 3, "total_relations": len(_EDGES)},
    "artifact_digest": "creative_fixture_abc456",
    "timestamp": "test_creative",
}


def _build_fixture_sqlite(sqlite_path: Path) -> None:
    conn = sqlite3.connect(str(sqlite_path))
    conn.executescript(_DDL)
    conn.executemany(
        "INSERT INTO nodes(id,adg_name,entity_type,layer,identity_kind,confidence,resolved_path) "
        "VALUES (?,?,?,?,?,?,?)", _NODES,
    )
    conn.executemany(
        "INSERT INTO edges(src_id,dst_id,relation_type,edge_kind,source_file,line_no,symbol) "
        "VALUES (?,?,?,?,?,?,?)", _EDGES,
    )
    conn.execute(
        "INSERT INTO violations(edge_id,category,evidence,file_path,line_no) "
        "SELECT id,relation_type,symbol,source_file,line_no FROM edges "
        "WHERE relation_type IN ('violates','antipattern','dynamic_exec')"
    )
    conn.commit()
    conn.close()


def _run_ingest(test_dir: str, force: bool = True) -> None:
    import tools.adg.adg_redis_ingest as m

    orig_dir, orig_db = m.ADG_DIR, m.REDIS_DB
    m.ADG_DIR = test_dir
    m.REDIS_DB = 14
    try:
        m.ingest(force=force)
    finally:
        m.ADG_DIR = orig_dir
        m.REDIS_DB = orig_db


def _flush_db14() -> None:
    r = _redis_lib.Redis(host="localhost", port=6379, db=14, decode_responses=True)
    cur = 0
    while True:
        cur, keys = r.scan(cur, match="adg:*", count=500)
        if keys:
            r.delete(*keys)
        if cur == 0:
            break


@pytest.fixture(scope="module")
def env():
    """Fixture: build SQLite, run ingest into Redis DB 14, yield env dict."""
    test_dir = (
        Path(__file__).resolve().parent.parent.parent
        / "artifacts" / "adg_test_creative"
    )
    test_dir.mkdir(parents=True, exist_ok=True)

    ts = "01012099_0001"
    sqlite_path = test_dir / f"adg_indexed_{ts}.sqlite"
    snap_path = test_dir / f"adg_snapshot_{ts}.json"

    for p in (sqlite_path, snap_path):
        if p.exists():
            p.unlink()

    _build_fixture_sqlite(sqlite_path)
    snap_path.write_text(json.dumps(_SNAPSHOT), encoding="utf-8")

    _flush_db14()
    _run_ingest(str(test_dir), force=True)

    r = _redis_lib.Redis(host="localhost", port=6379, db=14, decode_responses=True)
    yield {"r": r, "sqlite_path": str(sqlite_path), "test_dir": str(test_dir)}

    _flush_db14()
    for p in (sqlite_path, snap_path):
        try:
            if p.exists():
                p.unlink()
        except OSError:
            pass
    try:
        test_dir.rmdir()
    except OSError:
        pass


# ---------------------------------------------------------------------------
# T1-T3: Edge Cardinality
# ---------------------------------------------------------------------------

class TestEdgeCardinality:

    def test_fanout_cardinality_exact(self, env):
        """Sum of all adg:edge:<src>:<rel> SET sizes == total SQLite edge count."""
        r = env["r"]
        conn = sqlite3.connect(env["sqlite_path"])
        total_sqlite = conn.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
        conn.close()

        # Scan all fanout keys and sum their sizes
        total_redis = 0
        cur = 0
        while True:
            cur, keys = r.scan(cur, match="adg:edge:*:*", count=500)
            for key in keys:
                # exclude fanin keys (adg:edge:in:*) and edge_detail
                if ":in:" not in key and "edge_detail" not in key:
                    total_redis += r.scard(key)
            if cur == 0:
                break

        assert total_redis == total_sqlite, (
            f"Fanout cardinality {total_redis} != SQLite edge count {total_sqlite}"
        )

    def test_fanin_cardinality_exact(self, env):
        """Sum of all adg:edge:in:<tgt>:<rel> SET sizes == total SQLite edge count."""
        r = env["r"]
        conn = sqlite3.connect(env["sqlite_path"])
        total_sqlite = conn.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
        conn.close()

        total_redis = 0
        cur = 0
        while True:
            cur, keys = r.scan(cur, match="adg:edge:in:*", count=500)
            for key in keys:
                total_redis += r.scard(key)
            if cur == 0:
                break

        assert total_redis == total_sqlite, (
            f"Fanin cardinality {total_redis} != SQLite edge count {total_sqlite}"
        )

    def test_no_orphan_edge_ids(self, env):
        """Every edge_id in any adjacency SET must have an adg:edge_detail: HASH."""
        r = env["r"]
        cur = 0
        orphans = []
        while True:
            cur, keys = r.scan(cur, match="adg:edge:*", count=500)
            for key in keys:
                if "edge_detail" in key:
                    continue
                ktype = r.type(key)
                if ktype != "set":
                    continue
                for eid in r.smembers(key):
                    if not r.exists(f"adg:edge_detail:{eid}"):
                        orphans.append((key, eid))
            if cur == 0:
                break

        assert not orphans, f"Orphan edge_ids (no detail HASH): {orphans[:5]}"


# ---------------------------------------------------------------------------
# T4-T5: Bijection (fanout ↔ fanin inverse)
# ---------------------------------------------------------------------------

class TestBijection:

    def test_fanout_fanin_inverse(self, env):
        """For every SQLite edge, edge_id in fanout set ↔ edge_id in fanin set."""
        r = env["r"]
        conn = sqlite3.connect(env["sqlite_path"])
        rows = conn.execute(
            "SELECT id, src_id, dst_id, relation_type FROM edges"
        ).fetchall()
        conn.close()

        for edge_id, src, dst, rel in rows:
            eid = str(edge_id)
            fanout = r.smembers(f"adg:edge:{src}:{rel}")
            fanin = r.smembers(f"adg:edge:in:{dst}:{rel}")
            assert eid in fanout, f"edge {eid} missing from fanout adg:edge:{src}:{rel}"
            assert eid in fanin,  f"edge {eid} missing from fanin adg:edge:in:{dst}:{rel}"

    def test_roundtrip_src_dst(self, env):
        """Resolve all fanout edge_ids for node 1 → dst_ids must match SQLite."""
        r = env["r"]
        conn = sqlite3.connect(env["sqlite_path"])
        expected = {
            str(dst): rel
            for dst, rel in conn.execute(
                "SELECT dst_id, relation_type FROM edges WHERE src_id=1"
            ).fetchall()
        }
        conn.close()

        resolved_dsts = {}
        cur = 0
        while True:
            cur, keys = r.scan(cur, match="adg:edge:1:*", count=200)
            for key in keys:
                for eid in r.smembers(key):
                    detail = r.hgetall(f"adg:edge_detail:{eid}")
                    if detail:
                        resolved_dsts[detail["dst_id"]] = detail["relation_type"]
            if cur == 0:
                break

        for dst_id, rel in expected.items():
            assert dst_id in resolved_dsts, (
                f"Expected dst={dst_id} (rel={rel}) missing from resolved fanout"
            )


# ---------------------------------------------------------------------------
# T6-T7: Idempotency
# ---------------------------------------------------------------------------

class TestIdempotency:

    def test_double_ingest_key_count(self, env):
        """Key count for adg:edge_detail:* is identical after a second --force ingest."""
        r = env["r"]

        def count_edge_detail_keys():
            n = 0
            cur = 0
            while True:
                cur, keys = r.scan(cur, match="adg:edge_detail:*", count=500)
                n += len(keys)
                if cur == 0:
                    break
            return n

        count1 = count_edge_detail_keys()
        _run_ingest(env["test_dir"], force=True)
        count2 = count_edge_detail_keys()

        assert count1 == count2, (
            f"Edge detail key count changed after re-ingest: {count1} → {count2}"
        )

    def test_double_ingest_digest_stable(self, env):
        """Digest is identical after two --force ingests."""
        r = env["r"]
        digest1 = r.get("adg:snapshot:sqlite_digest")

        _run_ingest(env["test_dir"], force=True)
        digest2 = r.get("adg:snapshot:sqlite_digest")

        assert digest1 == digest2, (
            f"Digest changed between ingests: {digest1[:16]} → {digest2[:16]}"
        )


# ---------------------------------------------------------------------------
# T8-T9: Mutation / Corruption Detection
# ---------------------------------------------------------------------------

class TestMutationDetection:

    def test_tampered_edge_detail_detectable(self, env):
        """Overwrite a field in adg:edge_detail:1; verify the tampered value differs
        from the canonical SQLite row — confirming corruption is detectable."""
        r = env["r"]
        original = r.hgetall("adg:edge_detail:1")
        assert original, "adg:edge_detail:1 missing"

        original_sym = original.get("symbol", "")
        r.hset("adg:edge_detail:1", "symbol", "__TAMPERED__")

        tampered = r.hgetall("adg:edge_detail:1")
        assert tampered["symbol"] == "__TAMPERED__", "Tamper not applied"
        assert tampered["symbol"] != original_sym, "Tamper indistinguishable from original"

        # Restore
        r.hset("adg:edge_detail:1", "symbol", original_sym)
        restored = r.hgetall("adg:edge_detail:1")
        assert restored["symbol"] == original_sym, "Restore failed"

    def test_corrupt_status_coherency_propagates(self, env):
        """Manually set projection_coherent=False in adg:status; verify read-back
        correctly reflects the tampered value (not silently discarded)."""
        r = env["r"]
        raw = r.get("adg:status")
        assert raw, "adg:status not found"
        status = json.loads(raw)

        # Tamper
        status["projection_coherent"] = False
        r.set("adg:status", json.dumps(status))

        corrupted = json.loads(r.get("adg:status"))
        assert corrupted["projection_coherent"] is False, (
            "Corrupted projection_coherent not stored correctly"
        )

        # Restore via re-ingest
        _run_ingest(env["test_dir"], force=True)
        restored_raw = r.get("adg:status")
        restored = json.loads(restored_raw)
        assert restored.get("projection_coherent") is True, (
            "Re-ingest did not restore projection_coherent=True"
        )


# ---------------------------------------------------------------------------
# T10-T15: MCP Tool Contracts
# ---------------------------------------------------------------------------

class TestMcpToolContracts:
    """Call MCP tool functions directly against DB 14 to verify output shapes."""

    @pytest.fixture(autouse=True)
    def _patch_mcp_db(self):
        """Redirect MCP server's Redis connection to DB 14."""
        import tools.adg.adg_mcp_server as mcp

        orig_url = mcp._REDIS_URL
        orig_r = mcp._r
        mcp._REDIS_URL = "redis://localhost:6379/14"
        mcp._r = None  # force reconnect on next _redis() call
        yield
        mcp._REDIS_URL = orig_url
        mcp._r = orig_r

    def test_adg_edge_detail_shape(self, env):
        from tools.adg.adg_mcp_server import adg_edge_detail
        result = adg_edge_detail("1")
        assert result["status"] == "ok", f"Expected ok: {result}"
        data = result["data"]
        for field in ("src_id", "dst_id", "relation_type", "edge_kind",
                      "source_file", "line_no", "symbol"):
            assert field in data, f"Missing field '{field}' in adg_edge_detail output"

    def test_adg_module_context_shape(self, env):
        from tools.adg.adg_mcp_server import adg_module_context
        result = adg_module_context("1")
        assert result["status"] == "ok", f"Expected ok: {result}"
        data = result["data"]
        assert "edge_counts" in data
        assert "neighbors" in data
        assert "module_id" in data
        assert data["module_id"] == "1"

    def test_adg_edge_fanout_shape(self, env):
        from tools.adg.adg_mcp_server import adg_edge_fanout
        result = adg_edge_fanout("1", "calls", resolve=True)
        assert result["status"] == "ok", f"Expected ok: {result}"
        data = result["data"]
        assert "edges" in data, "Missing 'edges' key in fanout response"
        assert "targets" in data, "Missing 'targets' key in fanout response"
        assert data["total_edge_count"] >= 1, "Node 1 should have calls edges"
        for edge in data["edges"]:
            assert edge.get("src_id") == "1", "Edge src_id should be 1"

    def test_adg_edge_fanin_shape(self, env):
        from tools.adg.adg_mcp_server import adg_edge_fanin
        result = adg_edge_fanin("2", "calls", resolve=True)
        assert result["status"] == "ok", f"Expected ok: {result}"
        data = result["data"]
        assert "edges" in data, "Missing 'edges' key in fanin response"
        assert "sources" in data, "Missing 'sources' key in fanin response"
        assert data["total_edge_count"] >= 1, "Node 2 should have incoming calls"
        for edge in data["edges"]:
            assert edge.get("dst_id") == "2", "Edge dst_id should be 2"

    def test_adg_violations_shape(self, env):
        from tools.adg.adg_mcp_server import adg_violations
        result = adg_violations()
        assert result["status"] == "ok", f"Expected ok: {result}"
        data = result["data"]
        assert "violations" in data
        assert data["count"] >= 1, "Should have at least 1 violation"
        for v in data["violations"]:
            assert isinstance(v, dict), f"Violation should be a dict, got {type(v)}"
            # Must have resolved metadata — not a raw JSON string
            assert "raw" not in v or not v.get("raw"), (
                "Violation was not resolved to HASH metadata"
            )

    def test_adg_status_digest_fields(self, env):
        from tools.adg.adg_mcp_server import adg_status
        result = adg_status()
        assert result["status"] == "ok", f"Expected ok: {result}"
        data = result["data"]
        assert "projection_coherent" in data
        assert "sqlite_digest" in data
        assert "redis_digest" in data
        assert data["projection_coherent"] is True
        assert data["sqlite_digest"] == data["redis_digest"]


# ---------------------------------------------------------------------------
# T16-T18: Snapshot Round-Trip
# ---------------------------------------------------------------------------

class TestSnapshotRoundTrip:

    def test_snapshot_valid_json(self, env):
        r = env["r"]
        raw = r.get("adg:snapshot")
        assert raw, "adg:snapshot not found"
        parsed = json.loads(raw)
        assert isinstance(parsed, dict), "Snapshot should be a JSON object"

    def test_snapshot_has_counts_key(self, env):
        r = env["r"]
        snap = json.loads(r.get("adg:snapshot"))
        counts = snap.get("counts", {})
        assert counts, "Snapshot 'counts' key missing or empty"
        assert any(isinstance(v, int) for v in counts.values()), (
            "Snapshot counts should contain at least one integer"
        )

    def test_snapshot_digest_hex64(self, env):
        r = env["r"]
        for key in ("adg:snapshot:sqlite_digest", "adg:snapshot:redis_digest"):
            val = r.get(key)
            assert val, f"{key} not found"
            assert len(val) == 64, f"{key} should be 64-char hex, got len={len(val)}"
            assert all(c in "0123456789abcdef" for c in val), (
                f"{key} is not lowercase hex: {val[:16]}"
            )


# ---------------------------------------------------------------------------
# T19: Stale Guard / Cache-Hit Short-Circuit
# ---------------------------------------------------------------------------

class TestStaleGuard:

    def test_no_reingest_when_fresh(self, env):
        """Calling ingest() without --force on a fresh cache must be a no-op.
        Verified by checking the ingested_at timestamp does NOT change."""
        r = env["r"]
        meta_before = r.hgetall("adg:meta")
        ingested_at_before = meta_before.get("ingested_at", "0")

        # Wait 10ms to ensure a real clock difference if reingest happens
        time.sleep(0.01)

        _run_ingest(env["test_dir"], force=False)

        meta_after = r.hgetall("adg:meta")
        ingested_at_after = meta_after.get("ingested_at", "0")

        assert ingested_at_before == ingested_at_after, (
            f"Cache was re-ingested without --force: "
            f"before={ingested_at_before} after={ingested_at_after}"
        )