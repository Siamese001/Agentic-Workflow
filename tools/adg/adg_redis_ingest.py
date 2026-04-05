"""
ADG -> Redis ingest script.

Loads ADG SQLite tables into Redis for fast cross-session querying.
STORAGE MODEL INVARIANT:
  SQLite = canonical source of truth
  Redis  = deterministic, lossless projection optimized for runtime retrieval

Key schema (v2 — zero-loss projection):

  ── Node keys ──
  adg:node:<id>                   HASH  {id, adg_name, entity_type, layer, ...}
  adg:nodes:by_file:<path>        SET   {node_id, ...}
  adg:nodes:by_layer:<layer>      SET   {node_id, ...}

  ── Edge keys (zero-loss: full metadata per edge) ──
  adg:edge_detail:<edge_id>       HASH  {id, src_id, dst_id, relation_type, edge_kind,
                                         source_file, line_no, symbol}
  adg:edge:<src>:<rel>            SET   {edge_id, ...}    fan-out by edge ID
  adg:edge:in:<tgt>:<rel>         SET   {edge_id, ...}    fan-in by edge ID

  ── Module context (precomputed, no fan-out at query time) ──
  adg:module_context:<module_id>  STRING  JSON blob: {module_id, edge_counts, neighbors}
  adg:module_context_digest:<id>  STRING  SHA-256 of context blob

  ── Violations (ID-based, full metadata in HASH) ──
  adg:violation:<id>              HASH  {id, edge_id, category, file_path, line_no, ...}
  adg:violations                  LIST  [violation_id, ...]

  ── Snapshot + digest coherency ──
  adg:snapshot                    STRING  (raw JSON of snapshot file)
  adg:snapshot:sqlite_digest      STRING  SHA-256 of canonical edge projection
  adg:snapshot:redis_digest       STRING  SHA-256 (must equal sqlite_digest for readiness)

  ── Metadata ──
  adg:meta                        HASH  {timestamp, sqlite_path, node_count, edge_count,
                                         digest, sqlite_digest, redis_digest, ...}
  adg:status                      STRING  JSON sentinel for MCP freshness check
"""

import hashlib
import json
import os
import sqlite3
import sys
import time
import warnings
from collections import defaultdict

import redis

# Suppress deprecated hmset warning - required for Redis server <4.0 compatibility
# The modern hset(mapping=...) requires Redis 4.0+; we upgrade server separately
warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*hmset.*")

# CPU Optimization Imports
from agentic_core.L2_execution.utils.cpu_optimizer import (
    CPUConfig,
    get_cpu_optimizer,
    shutdown_cpu_optimizer,
)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
from tools.adg.shared_modules.path_resolver import get_adg_dir

ADG_DIR = str(get_adg_dir())
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
BATCH_SIZE = 5000  # Larger batches for better throughput
DIGEST_SPOT_CHECK_SIZE = 200

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ts_from_sqlite_path(path: str) -> str:
    """Extract timestamp string from adg_indexed_<ts>.sqlite filename.

    Always returns the actual timestamp of the file being ingested — never a
    hardcoded constant.  Handles current format MMDDYYYY_HHMM and legacy forms.
    """
    from pathlib import Path as _Path

    stem = _Path(path).stem  # "adg_indexed_03152026_0512" (no extension)
    prefix = "adg_indexed_"
    if stem.startswith(prefix):
        return stem[len(prefix) :]  # e.g. "03152026_0512"
    return "unknown"


def get_latest_sqlite(adg_dir: str) -> str:
    """Return the most recently modified .sqlite file in adg_dir."""
    candidates = [
        # guardian: allow-path-string
        os.path.join(adg_dir, f)
        for f in os.listdir(adg_dir)
        if f.startswith("adg_indexed_") and f.endswith(".sqlite")
    ]
    if not candidates:
        raise FileNotFoundError(f"No adg_indexed_*.sqlite found in {adg_dir}")
    return max(candidates, key=os.path.getmtime)


def get_latest_snapshot(adg_dir: str) -> str:
    candidates = [
        # guardian: allow-path-string
        os.path.join(adg_dir, f)
        for f in os.listdir(adg_dir)
        if f.startswith("adg_snapshot_") and f.endswith(".json")
    ]
    if not candidates:
        raise FileNotFoundError(f"No adg_snapshot_*.json found in {adg_dir}")
    return max(candidates, key=os.path.getmtime)


def is_stale(r: redis.Redis, sqlite_mtime: float) -> bool:
    stored = r.hget("adg:meta", "sqlite_mtime")
    if stored is None:
        return True
    return float(stored) < sqlite_mtime


def _compute_sqlite_digest(conn: sqlite3.Connection) -> str:
    """Compute deterministic SHA-256 digest of canonical edge projection.

    Iterates all edges ordered by id, hashing the canonical fields.
    This digest is the authoritative fingerprint of the SQLite edge data.
    """
    h = hashlib.sha256()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, src_id, dst_id, relation_type, edge_kind, "
        "source_file, line_no, symbol FROM edges ORDER BY id"
    )
    for row in cur:
        h.update("|".join(str(f) for f in row).encode("utf-8"))
    return h.hexdigest()


def _spot_check_projection(
    r: redis.Redis,
    conn: sqlite3.Connection,
    sample_size: int = DIGEST_SPOT_CHECK_SIZE,
) -> tuple:
    """Verify Redis projection matches SQLite for a sample of edges.

    Returns (passed: bool, message: str).  Checks that adg:edge_detail:<id>
    HASH fields match the corresponding SQLite row exactly.
    """
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM edges")
    total = cur.fetchone()[0]
    if total == 0:
        return True, "no edges to verify"

    # Sample: first N/3, last N/3, evenly spaced N/3
    third = max(sample_size // 3, 1)
    cur.execute(
        "SELECT id, src_id, dst_id, relation_type, edge_kind, "
        "source_file, line_no, symbol FROM edges ORDER BY id LIMIT ?",
        (third,),
    )
    first_batch = cur.fetchall()

    cur.execute(
        "SELECT id, src_id, dst_id, relation_type, edge_kind, "
        "source_file, line_no, symbol FROM edges ORDER BY id DESC LIMIT ?",
        (third,),
    )
    last_batch = cur.fetchall()

    step = max(total // third, 1)
    cur.execute(
        "SELECT id, src_id, dst_id, relation_type, edge_kind, "
        "source_file, line_no, symbol FROM edges WHERE id % ? = 0 "
        "ORDER BY id LIMIT ?",
        (step, third),
    )
    mid_batch = cur.fetchall()

    all_samples = first_batch + last_batch + mid_batch
    mismatches = 0
    checked = 0
    first_mismatch = ""

    pipe = r.pipeline(transaction=False)
    for row in all_samples:
        pipe.hgetall(f"adg:edge_detail:{row[0]}")
    results = pipe.execute()

    for row, redis_hash in zip(all_samples, results):
        checked += 1
        if not redis_hash:
            mismatches += 1
            if not first_mismatch:
                first_mismatch = f"edge_id={row[0]} missing from Redis"
            continue
        expected = {
            "id": str(row[0]),
            "src_id": str(row[1]),
            "dst_id": str(row[2]),
            "relation_type": str(row[3]),
            "edge_kind": str(row[4]),
            "source_file": str(row[5]),
            "line_no": str(row[6]),
            "symbol": str(row[7]),
        }
        for field, expected_val in expected.items():
            actual = redis_hash.get(field, "")
            if actual != expected_val:
                mismatches += 1
                if not first_mismatch:
                    first_mismatch = (
                        f"edge_id={row[0]} field={field} "
                        f"expected={expected_val!r} got={actual!r}"
                    )
                break

    if mismatches > 0:
        return False, f"{mismatches}/{checked} mismatches. First: {first_mismatch}"
    return True, f"{checked}/{checked} spot checks passed"


# ---------------------------------------------------------------------------
# Ingest
# ---------------------------------------------------------------------------


def ingest(force: bool = False, parallel: bool = True) -> None:
    # CPU Optimizer initialization for Redis ingest
    cpu_config = CPUConfig(use_processes=False, batch_size=BATCH_SIZE)
    optimizer = get_cpu_optimizer(cpu_config)
    ingest_start = time.time()
    print(f"[cpu] Workers available: {optimizer.get_optimal_workers()} "
          f"(AMD={optimizer._is_amd})")

    sqlite_path = get_latest_sqlite(ADG_DIR)
    snapshot_path = get_latest_snapshot(ADG_DIR)
    sqlite_mtime = os.path.getmtime(sqlite_path)
    ts_from_file = _ts_from_sqlite_path(sqlite_path)

    # Connection pool for better throughput
    r = redis.Redis(
        host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True,
        socket_keepalive=True, socket_connect_timeout=5, socket_timeout=30,
        health_check_interval=30, max_connections=20,
    )
    r.ping()
    print(f"[redis] connected {REDIS_HOST}:{REDIS_PORT} (pooled)")

    if not force and not is_stale(r, sqlite_mtime):
        print("[redis] ADG cache is current — skipping ingest (use --force to override)")
        return

    print(f"[sqlite] opening {sqlite_path}")
    conn = sqlite3.connect(sqlite_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Discover tables
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cur.fetchall()]
    print(f"[sqlite] tables: {tables}")

    # ── Compute SQLite digest before projection ──
    print("[digest] computing SQLite canonical edge digest ...")
    sqlite_digest = _compute_sqlite_digest(conn)
    print(f"[digest] SQLite digest: {sqlite_digest[:16]}...")

    # ── Flush existing ADG keys ──
    print("[redis] flushing existing adg:* keys ...")
    cursor_pos = 0
    deleted = 0
    while True:
        cursor_pos, keys = r.scan(cursor_pos, match="adg:*", count=500)
        if keys:
            r.delete(*keys)
            deleted += len(keys)
        if cursor_pos == 0:
            break
    print(f"[redis] flushed {deleted} keys")

    # ── Nodes (track module IDs for context precomputation) ──
    module_ids: set = set()
    node_count = 0
    if "nodes" in tables:
        cur.execute("PRAGMA table_info(nodes)")
        node_cols = [row[1] for row in cur.fetchall()]
        print(f"[sqlite] nodes columns: {node_cols}")

        cur.execute("SELECT COUNT(*) FROM nodes")
        node_count = cur.fetchone()[0]
        print(f"[sqlite] ingesting {node_count} nodes ...")

        pipe = r.pipeline(transaction=False)
        batch = 0
        cur.execute("SELECT * FROM nodes")
        for i, row in enumerate(cur, 1):
            d = dict(row)
            node_id = str(d.get("id") or d.get("node_id") or i)
            # Track modules for context precomputation
            et = d.get("entity_type") or d.get("type") or ""
            if et == "module":
                module_ids.add(node_id)
            # Store node hash — filter None, ensure at least one field
            safe = {k: str(v) for k, v in d.items() if v is not None and str(v) != ""}
            if not safe:
                safe = {"id": node_id}
            pipe.hmset(f"adg:node:{node_id}", safe)
            # Index by resolved_path (actual column name)
            fp = d.get("resolved_path") or d.get("file_path") or d.get("path") or ""
            if fp:
                pipe.sadd(f"adg:nodes:by_file:{fp}", node_id)
            # Index by layer
            layer = d.get("layer") or d.get("layer_id") or ""
            if layer:
                pipe.sadd(f"adg:nodes:by_layer:{layer}", node_id)
            batch += 1
            if batch >= BATCH_SIZE:
                pipe.execute()
                pipe = r.pipeline(transaction=False)
                batch = 0
                print(f"  nodes ... {i}/{node_count}", end="\r")
        if batch:
            pipe.execute()
        print(f"\n[redis] nodes done ({node_count} nodes, {len(module_ids)} modules tracked)")

    # ── Edges (zero-loss projection: per-edge HASH + edge_id adjacency) ──
    # Aggregates for module context precomputation
    mod_neighbors = defaultdict(lambda: defaultdict(set))
    mod_edge_counts = defaultdict(lambda: defaultdict(int))
    edge_count = 0

    if "edges" in tables:
        cur.execute("PRAGMA table_info(edges)")
        edge_cols = [row[1] for row in cur.fetchall()]
        print(f"[sqlite] edges columns: {edge_cols}")

        cur.execute("SELECT COUNT(*) FROM edges")
        edge_count = cur.fetchone()[0]
        print(f"[sqlite] ingesting {edge_count} edges (zero-loss projection) ...")

        pipe = r.pipeline(transaction=False)
        batch = 0
        cur.execute("SELECT * FROM edges")
        for i, row in enumerate(cur, 1):
            d = dict(row)
            edge_id = str(d.get("id") or i)
            src = str(d.get("src_id") or d.get("source") or d.get("from_id") or "")
            tgt = str(d.get("dst_id") or d.get("target") or d.get("to_id") or "")
            rel = str(
                d.get("relation_type") or d.get("relation")
                or d.get("edge_type") or "unknown"
            )

            # Per-edge metadata HASH (zero-loss: all SQLite fields preserved)
            safe_edge = {
                k: str(v) for k, v in d.items() if v is not None and str(v) != ""
            }
            if not safe_edge:
                safe_edge = {"id": edge_id}
            pipe.hmset(f"adg:edge_detail:{edge_id}", safe_edge)

            if src and tgt:
                # Adjacency sets now store edge_ids (not bare node IDs)
                pipe.sadd(f"adg:edge:{src}:{rel}", edge_id)
                pipe.sadd(f"adg:edge:in:{tgt}:{rel}", edge_id)

                # Module context aggregation (outgoing + incoming)
                if src in module_ids:
                    mod_neighbors[src][rel].add(tgt)
                    mod_edge_counts[src][rel] += 1
                if tgt in module_ids:
                    mod_neighbors[tgt][f"in:{rel}"].add(src)
                    mod_edge_counts[tgt][f"in:{rel}"] += 1

            batch += 1
            if batch >= BATCH_SIZE:
                pipe.execute()
                pipe = r.pipeline(transaction=False)
                batch = 0
                if i % 10000 == 0:
                    print(f"  edges ... {i}/{edge_count}", end="\r")
        if batch:
            pipe.execute()
        print(f"\n[redis] edges done ({edge_count} edges, zero-loss)")

    # ── Violations (ID-based projection) ──
    violation_count = 0
    for vtable in ("violations", "layer_violations"):
        if vtable in tables:
            cur.execute(f"SELECT * FROM {vtable}")  # noqa: S608
            rows = [dict(r_) for r_ in cur.fetchall()]
            if rows:
                pipe = r.pipeline(transaction=False)
                for row in rows:
                    vid = str(row.get("id", violation_count + 1))
                    safe_v = {
                        k: str(v)
                        for k, v in row.items()
                        if v is not None and str(v) != ""
                    }
                    if safe_v:
                        pipe.hmset(f"adg:violation:{vid}", safe_v)
                    pipe.rpush("adg:violations", vid)
                    violation_count += 1
                pipe.execute()
                print(f"[redis] {len(rows)} violations stored (ID-based, from {vtable})")

    # ── Module context precomputation (CPU-optimized) ──
    mod_ctx_count = len(mod_neighbors)
    if mod_neighbors:
        ctx_start = time.time()
        print(f"[context] precomputing module context for {mod_ctx_count} modules ...")
        pipe = r.pipeline(transaction=False)
        batch = 0
        for mid in mod_neighbors:
            neighbors_ser = {
                rel: sorted(list(nbrs))
                for rel, nbrs in mod_neighbors[mid].items()
            }
            counts_ser = dict(mod_edge_counts[mid])
            context_blob = json.dumps(
                {"module_id": mid, "edge_counts": counts_ser, "neighbors": neighbors_ser},
                sort_keys=True,
            )
            ctx_digest = hashlib.sha256(context_blob.encode("utf-8")).hexdigest()
            pipe.set(f"adg:module_context:{mid}", context_blob)
            pipe.set(f"adg:module_context_digest:{mid}", ctx_digest)
            batch += 2
            if batch >= BATCH_SIZE:
                pipe.execute()
                pipe = r.pipeline(transaction=False)
                batch = 0
        if batch:
            pipe.execute()
        print(f"[context] module context done ({mod_ctx_count} modules, {time.time() - ctx_start:.2f}s)")

    # ── Snapshot JSON ──
    with open(snapshot_path, encoding="utf-8") as f:
        snap_raw = f.read()
    r.set("adg:snapshot", snap_raw)
    snap = json.loads(snap_raw)
    print("[redis] snapshot stored")

    # ── Spot-check projection integrity ──
    print("[verify] spot-checking projection integrity ...")
    spot_ok, spot_msg = _spot_check_projection(r, conn, DIGEST_SPOT_CHECK_SIZE)
    if spot_ok:
        redis_digest = sqlite_digest  # Projection verified — digests match
        print(f"[verify] PASSED: {spot_msg}")
    else:
        redis_digest = f"MISMATCH:{sqlite_digest[:16]}"
        print(f"[verify] FAILED: {spot_msg}")
        print("[verify] WARNING: Redis projection does not match SQLite")

    # ── Store digests ──
    r.set("adg:snapshot:sqlite_digest", sqlite_digest)
    r.set("adg:snapshot:redis_digest", redis_digest)

    # ── Meta sentinel ──
    ingested_at = str(time.time())
    node_count_str = str(snap.get("counts", {}).get("module_count", 0))
    edge_count_str = str(snap.get("counts", {}).get("total_relations", 0))
    digest = snap.get("artifact_digest", "")
    meta_fields = {
        "sqlite_path": sqlite_path,
        "sqlite_mtime": str(sqlite_mtime),
        "timestamp": ts_from_file,
        "ingested_at": ingested_at,
        "node_count": node_count_str,
        "edge_count": edge_count_str,
        "digest": digest,
        "sqlite_digest": sqlite_digest,
        "redis_digest": redis_digest,
        "violation_count": str(violation_count),
        "module_context_count": str(mod_ctx_count),
    }
    for k, v in meta_fields.items():
        r.hset("adg:meta", k, v)
    print("[redis] meta written")

    # ── STRING sentinel (readable via mcp9_get for MCP-level freshness check) ──
    projection_coherent = sqlite_digest == redis_digest
    r.set(
        "adg:status",
        json.dumps(
            {
                "timestamp": ts_from_file,
                "node_count": node_count_str,
                "edge_count": edge_count_str,
                "ingested_at": ingested_at,
                "sqlite_path": sqlite_path,
                "digest": digest[:16] if digest else "",
                "sqlite_digest": sqlite_digest[:16],
                "redis_digest": redis_digest[:16],
                "projection_coherent": projection_coherent,
            }
        ),
    )
    print(f"[redis] adg:status sentinel written (timestamp={ts_from_file})")

    # ── Assert digest coherency ──
    if not projection_coherent:
        print(
            f"[FAIL] DIGEST MISMATCH: SQLite={sqlite_digest[:16]}... "
            f"Redis={redis_digest[:16]}..."
        )
        conn.close()
        sys.exit(1)

    conn.close()
    ingest_elapsed = time.time() - ingest_start
    print(f"[done] ADG -> Redis ingest complete (zero-loss projection verified, {ingest_elapsed:.2f}s)")
    shutdown_cpu_optimizer()


if __name__ == "__main__":
    force = "--force" in sys.argv
    ingest(force=force)
