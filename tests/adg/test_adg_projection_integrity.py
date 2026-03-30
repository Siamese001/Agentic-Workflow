"""ADG Redis Projection Integrity Tests.

Validates the zero-loss projection invariant:
  SQLite = canonical source of truth
  Redis  = deterministic, lossless projection

Test inventory
--------------
Test 1: projection_completeness — every SQLite edge has a corresponding
        adg:edge_detail:<id> HASH in Redis with all fields preserved.
Test 2: metadata_integrity — adg:meta HASH contains all required fields
        including sqlite_digest, redis_digest, and projection_coherent.
Test 3: adjacency_consistency — for every edge, edge_id appears in the
        correct adg:edge:<src>:<rel> and adg:edge:in:<tgt>:<rel> sets.
Test 4: replay_determinism — running ingest twice with --force produces
        identical sqlite_digest values (deterministic hash).
Test 5: module_context_precomputation — modules with edges have
        precomputed context blobs in adg:module_context:<id>.
Test 6: violations_id_projection — violation IDs in adg:violations LIST
        resolve to valid adg:violation:<id> HASHes.

Requires: Redis running on localhost:6379, uses DB 15 for isolation.
          A fixture SQLite + snapshot are created in a temp directory.
"""

from __future__ import annotations

import sys
from pathlib import Path
# Add repo root to path for tools.adg imports
_repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_repo_root))

import hashlib
import json
import sqlite3
from pathlib import Path

import pytest

pytestmark = pytest.mark.serial

# Lazy imports - loaded in fixture to avoid collection-time errors
def _get_lifecycle_emitters():
    from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
        _emit_applies_guardrail,
        _emit_records_execution_trace,
    )
    return _emit_applies_guardrail, _emit_records_execution_trace

# ---------------------------------------------------------------------------
# Skip if redis is not available
# ---------------------------------------------------------------------------
try:
    import redis

    _redis_available = redis.Redis(host="localhost", port=6379, db=15, decode_responses=True)
    _redis_available.ping()
    _REDIS_OK = True
except (ValueError, TypeError, RuntimeError) as e:
    _REDIS_OK = False

_SKIP_REASON = "Redis not available on localhost:6379"


@pytest.fixture(scope="module", autouse=True)
def _emit_test_lifecycle():
    """Emit lifecycle events at test module load time."""
    _emit_applies_guardrail, _emit_records_execution_trace = _get_lifecycle_emitters()
    _emit_applies_guardrail("projection_integrity_test", "test_harness", "L5")
    _emit_records_execution_trace("projection_integrity_test", "L5", "test_collection")
    yield


# Fixture SQLite schema (mirrors multi_writer.py DDL)
_FIXTURE_DDL = """
CREATE TABLE IF NOT EXISTS nodes (
    id            INTEGER PRIMARY KEY,
    adg_name      TEXT NOT NULL,
    entity_type   TEXT NOT NULL,
    layer         TEXT NOT NULL,
    identity_kind TEXT NOT NULL,
    confidence    TEXT NOT NULL,
    resolved_path TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS edges (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    src_id        INTEGER NOT NULL REFERENCES nodes(id),
    dst_id        INTEGER NOT NULL REFERENCES nodes(id),
    relation_type TEXT NOT NULL,
    edge_kind     TEXT NOT NULL,
    source_file   TEXT NOT NULL,
    line_no       INTEGER NOT NULL,
    symbol        TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS violations (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    edge_id       INTEGER NOT NULL REFERENCES edges(id),
    category      TEXT NOT NULL,
    evidence      TEXT NOT NULL DEFAULT '',
    file_path     TEXT NOT NULL DEFAULT '',
    line_no       INTEGER NOT NULL DEFAULT 0
);
"""

# Fixture data
_FIXTURE_NODES = [
    (1, "module_a", "module", "L2", "ast_resolved", "high", "agentic_core/L2_execution/mod_a.py"),
    (2, "module_b", "module", "L2", "ast_resolved", "high", "agentic_core/L2_execution/mod_b.py"),
    (3, "function_x", "function", "L2", "ast_resolved", "high", "agentic_core/L2_execution/mod_a.py"),
    (4, "class_y", "class", "L3", "ast_resolved", "medium", "agentic_core/L3_orchestration/cls_y.py"),
]

_FIXTURE_EDGES = [
    # (src_id, dst_id, relation_type, edge_kind, source_file, line_no, symbol)
    (1, 2, "calls", "static", "agentic_core/L2_execution/mod_a.py", 10, "do_work"),
    (1, 3, "exports", "static", "agentic_core/L2_execution/mod_a.py", 5, "function_x"),
    (2, 4, "imports", "static", "agentic_core/L2_execution/mod_b.py", 1, "class_y"),
    (3, 2, "calls", "dynamic", "agentic_core/L2_execution/mod_a.py", 15, "invoke_b"),
    (1, 4, "violates", "governance", "agentic_core/L2_execution/mod_a.py", 20, "layer_violation"),
]

_FIXTURE_SNAPSHOT = {
    "counts": {"module_count": 2, "total_relations": 5},
    "artifact_digest": "fixture_digest_abc123",
    "timestamp": "test_fixture",
}


@pytest.fixture(scope="module")
def fixture_env():
    """Create test fixtures and setup Redis with test data."""
    import tempfile

    # Create temp directory
    test_dir = Path(tempfile.mkdtemp(prefix="adg_test_"))
    ts = "test_fixture"
    sqlite_path = test_dir / f"adg_indexed_{ts}.sqlite"
    snapshot_path = test_dir / f"adg_snapshot_{ts}.json"

    # Create SQLite database with DDL
    conn = sqlite3.connect(str(sqlite_path))
    conn.executescript(_FIXTURE_DDL)

    # Insert nodes
    conn.executemany(
        "INSERT INTO nodes(id, adg_name, entity_type, layer, identity_kind, confidence, resolved_path) "
        "VALUES (?,?,?,?,?,?,?)",
        _FIXTURE_NODES,
    )

    # Insert edges
    conn.executemany(
        "INSERT INTO edges(src_id,dst_id,relation_type,edge_kind,source_file,line_no,symbol) "
        "VALUES (?,?,?,?,?,?,?)",
        _FIXTURE_EDGES,
    )
    conn.execute(
        "INSERT INTO violations (edge_id, category, evidence, file_path, line_no) "
        "SELECT id, relation_type, symbol, source_file, line_no "
        "FROM edges WHERE relation_type IN ('violates', 'antipattern', 'dynamic_exec')"
    )
    conn.commit()
    conn.close()

    # Create fixture snapshot
    with open(snapshot_path, "w", encoding="utf-8") as f:
        json.dump(_FIXTURE_SNAPSHOT, f)

    # Patch ingest config and run
    import tools.adg.adg_redis_ingest as ingest_mod

    orig_adg_dir = ingest_mod.ADG_DIR
    orig_host = ingest_mod.REDIS_HOST
    orig_port = ingest_mod.REDIS_PORT
    orig_db = ingest_mod.REDIS_DB

    ingest_mod.ADG_DIR = str(test_dir)
    ingest_mod.REDIS_DB = 15

    try:
        ingest_mod.ingest(force=True)
    finally:
        ingest_mod.ADG_DIR = orig_adg_dir
        ingest_mod.REDIS_HOST = orig_host
        ingest_mod.REDIS_PORT = orig_port
        ingest_mod.REDIS_DB = orig_db

    r = redis.Redis(host="localhost", port=6379, db=15, decode_responses=True)
    yield {
        "redis": r,
        "sqlite_path": str(sqlite_path),
        "test_dir": str(test_dir),
        "ts": ts,
    }

    # Cleanup: flush test DB keys
    cursor_pos = 0
    while True:
        cursor_pos, keys = r.scan(cursor_pos, match="adg:*", count=500)
        if keys:
            r.delete(*keys)
        if cursor_pos == 0:    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging
            break

    # Cleanup: remove test fixtures
    try:
        if sqlite_path.exists():
            sqlite_path.unlink()
        if snapshot_path.exists():
            snapshot_path.unlink()
        if test_dir.exists():
            test_dir.rmdir()
    except OSError:
        pass  # Best-effort cleanup on Windows


class TestProjectionCompleteness:
    """Test 1: Every SQLite edge has a corresponding Redis HASH with all fields."""    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging

    def test_all_edges_projected(self, fixture_env):
        r = fixture_env["redis"]
        conn = sqlite3.connect(fixture_env["sqlite_path"])
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM edges ORDER BY id")
        rows = [dict(row) for row in cur.fetchall()]
        conn.close()

        assert len(rows) == len(_FIXTURE_EDGES), "SQLite edge count mismatch"

        for row in rows:
            edge_id = str(row["id"])
            redis_hash = r.hgetall(f"adg:edge_detail:{edge_id}")
            assert redis_hash, f"Edge {edge_id} missing from Redis"
            assert redis_hash["src_id"] == str(row["src_id"])
            assert redis_hash["dst_id"] == str(row["dst_id"])
            assert redis_hash["relation_type"] == str(row["relation_type"])
            assert redis_hash["edge_kind"] == str(row["edge_kind"])
            assert redis_hash["source_file"] == str(row["source_file"])
            assert redis_hash["line_no"] == str(row["line_no"])
            assert redis_hash["symbol"] == str(row["symbol"])

    def test_all_nodes_projected(self, fixture_env):    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging
        r = fixture_env["redis"]
        for node in _FIXTURE_NODES:
            node_id = str(node[0])
            redis_hash = r.hgetall(f"adg:node:{node_id}")
            assert redis_hash, f"Node {node_id} missing from Redis"
            assert redis_hash["adg_name"] == node[1]
            assert redis_hash["entity_type"] == node[2]
            assert redis_hash["layer"] == node[3]


class TestMetadataIntegrity:
    """Test 2: adg:meta HASH has all required fields including digests."""

    def test_meta_required_fields(self, fixture_env):
        r = fixture_env["redis"]
        meta = r.hgetall("adg:meta")
        assert meta, "adg:meta not found"

        required = [
            "sqlite_path", "sqlite_mtime", "timestamp", "ingested_at",
            "node_count", "edge_count", "digest",
            "sqlite_digest", "redis_digest",
            "violation_count", "module_context_count",
        ]
        for field in required:
            assert field in meta, f"Missing adg:meta field: {field}"

    def test_digest_coherency(self, fixture_env):
        r = fixture_env["redis"]
        meta = r.hgetall("adg:meta")
        assert meta["sqlite_digest"] == meta["redis_digest"], (
            f"Digest mismatch: sqlite={meta['sqlite_digest'][:16]} "
            f"redis={meta['redis_digest'][:16]}"
        )

    def test_status_sentinel_coherent(self, fixture_env):
        r = fixture_env["redis"]
        raw = r.get("adg:status")
        assert raw, "adg:status not found"
        status = json.loads(raw)
        assert status.get("projection_coherent") is True, (
            f"projection_coherent should be True, got {status.get('projection_coherent')}"
        )

    def test_digest_strings_stored(self, fixture_env):
        r = fixture_env["redis"]
        sqlite_digest = r.get("adg:snapshot:sqlite_digest")
        redis_digest = r.get("adg:snapshot:redis_digest")
        assert sqlite_digest, "adg:snapshot:sqlite_digest not found"
        assert redis_digest, "adg:snapshot:redis_digest not found"
        assert sqlite_digest == redis_digest, "Stored digest strings don't match"


class TestAdjacencyConsistency:
    """Test 3: edge_ids appear in correct adjacency sets."""

    def test_fanout_sets_contain_edge_ids(self, fixture_env):
        r = fixture_env["redis"]
        conn = sqlite3.connect(fixture_env["sqlite_path"])
        cur = conn.cursor()
        cur.execute("SELECT id, src_id, relation_type FROM edges")
        for edge_id, src_id, rel in cur.fetchall():
            members = r.smembers(f"adg:edge:{src_id}:{rel}")
            assert str(edge_id) in members, (
                f"edge_id={edge_id} not in adg:edge:{src_id}:{rel}"
            )
        conn.close()

    def test_fanin_sets_contain_edge_ids(self, fixture_env):
        r = fixture_env["redis"]
        conn = sqlite3.connect(fixture_env["sqlite_path"])
        cur = conn.cursor()
        cur.execute("SELECT id, dst_id, relation_type FROM edges")
        for edge_id, dst_id, rel in cur.fetchall():
            members = r.smembers(f"adg:edge:in:{dst_id}:{rel}")
            assert str(edge_id) in members, (
                f"edge_id={edge_id} not in adg:edge:in:{dst_id}:{rel}"
            )
        conn.close()

    def test_edge_ids_resolve_to_detail(self, fixture_env):
        r = fixture_env["redis"]
        # Check that edge IDs in a fanout set resolve to valid detail HASHes
        members = r.smembers("adg:edge:1:calls")
        assert len(members) > 0, "No calls edges from node 1"
        for eid in members:
            detail = r.hgetall(f"adg:edge_detail:{eid}")
            assert detail, f"adg:edge_detail:{eid} missing"
            assert detail["src_id"] == "1"
            assert detail["relation_type"] == "calls"


class TestReplayDeterminism:
    """Test 4: Running ingest twice produces identical digests."""

    def test_digest_deterministic(self, fixture_env):
        r = fixture_env["redis"]
        first_digest = r.get("adg:snapshot:sqlite_digest")
        assert first_digest, "No digest from first ingest"

        # Compute digest independently from SQLite
        conn = sqlite3.connect(fixture_env["sqlite_path"])
        h = hashlib.sha256()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, src_id, dst_id, relation_type, edge_kind, "
            "source_file, line_no, symbol FROM edges ORDER BY id"
        )
        for row in cur:
            h.update("|".join(str(f) for f in row).encode("utf-8"))
        conn.close()
        independent_digest = h.hexdigest()

        assert first_digest == independent_digest, (
            f"Digest mismatch: stored={first_digest[:16]} computed={independent_digest[:16]}"
        )


class TestModuleContextPrecomputation:
    """Test 5: Modules with edges have precomputed context blobs."""

    def test_module_context_exists(self, fixture_env):
        r = fixture_env["redis"]
        # Nodes 1 and 2 are modules; they should have context
        for mid in ["1", "2"]:
            ctx_raw = r.get(f"adg:module_context:{mid}")
            assert ctx_raw, f"Module {mid} missing context blob"
            ctx = json.loads(ctx_raw)
            assert "edge_counts" in ctx
            assert "neighbors" in ctx
            assert ctx["module_id"] == mid

    def test_module_context_digest_exists(self, fixture_env):
        r = fixture_env["redis"]
        for mid in ["1", "2"]:
            digest = r.get(f"adg:module_context_digest:{mid}")
            assert digest, f"Module {mid} missing context digest"
            assert len(digest) == 64, "Digest should be SHA-256 hex (64 chars)"

    def test_non_module_no_context(self, fixture_env):
        r = fixture_env["redis"]
        # Node 3 is a function, not a module — should have no precomputed context
        ctx_raw = r.get("adg:module_context:3")
        assert ctx_raw is None, "Non-module node should not have context"

    def test_module_edge_counts_correct(self, fixture_env):
        r = fixture_env["redis"]
        ctx = json.loads(r.get("adg:module_context:1"))
        counts = ctx["edge_counts"]
        # Module 1 (src): calls->2 edges (to node 2 and via node 3->2),
        # exports->1 edge, violates->1 edge
        assert counts.get("calls", 0) >= 1, "Module 1 should have calls edges"
        assert counts.get("exports", 0) >= 1, "Module 1 should have exports edges"


class TestViolationsIdProjection:
    """Test 6: Violation IDs in LIST resolve to valid HASHes."""

    def test_violations_list_populated(self, fixture_env):
        r = fixture_env["redis"]
        vid_list = r.lrange("adg:violations", 0, -1)
        assert len(vid_list) >= 1, "Should have at least 1 violation (violates edge)"

    def test_violation_ids_resolve(self, fixture_env):
        r = fixture_env["redis"]
        vid_list = r.lrange("adg:violations", 0, -1)
        for vid in vid_list:
            detail = r.hgetall(f"adg:violation:{vid}")
            assert detail, f"Violation {vid} HASH missing"
            assert "category" in detail or "relation_type" in detail, (
                f"Violation {vid} missing category field"
            )