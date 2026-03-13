"""
ADG -> Redis ingest script.

Loads ADG SQLite tables into Redis for fast cross-session querying.
Key schema:
  adg:meta                    HASH  {timestamp, sqlite_path, node_count, edge_count, digest}
  adg:node:<id>               HASH  {id, label, layer, kind, file_path, ...}
  adg:nodes:by_file:<path>    SET   {node_id, ...}
  adg:nodes:by_layer:<layer>  SET   {node_id, ...}
  adg:edge:<src>:<rel>        SET   {target_id, ...}   fan-out lookup
  adg:edge:in:<tgt>:<rel>     SET   {source_id, ...}   fan-in lookup
  adg:snapshot                STRING (raw JSON of snapshot file)
  adg:violations              LIST  (JSON-encoded violation dicts)
"""

import json
import os
import sqlite3
import sys
import time

import redis

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
ADG_DIR = r"c:\Git\Agentic-Workflow\artifacts\adg"
SNAPSHOT_SUFFIX = "03132026_1424"
# guardian: allow-path-string
SQLITE_PATH = os.path.join(ADG_DIR, f"adg_indexed_{SNAPSHOT_SUFFIX}.sqlite")
# guardian: allow-path-string
SNAPSHOT_PATH = os.path.join(ADG_DIR, f"adg_snapshot_{SNAPSHOT_SUFFIX}.json")
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
BATCH_SIZE = 500

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Ingest
# ---------------------------------------------------------------------------


def ingest(force: bool = False) -> None:
    sqlite_path = get_latest_sqlite(ADG_DIR)
    snapshot_path = get_latest_snapshot(ADG_DIR)
    sqlite_mtime = os.path.getmtime(sqlite_path)

    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
    r.ping()
    print(f"[redis] connected {REDIS_HOST}:{REDIS_PORT}")

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

    # Flush existing ADG keys
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

    # -- Nodes table --
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
        print("\n[redis] nodes done")

    # -- Edges table --
    if "edges" in tables:
        cur.execute("PRAGMA table_info(edges)")
        edge_cols = [row[1] for row in cur.fetchall()]
        print(f"[sqlite] edges columns: {edge_cols}")

        cur.execute("SELECT COUNT(*) FROM edges")
        edge_count = cur.fetchone()[0]
        print(f"[sqlite] ingesting {edge_count} edges ...")

        pipe = r.pipeline(transaction=False)
        batch = 0
        cur.execute("SELECT * FROM edges")
        for i, row in enumerate(cur, 1):
            d = dict(row)
            src = str(d.get("src_id") or d.get("source") or d.get("from_id") or "")
            tgt = str(d.get("dst_id") or d.get("target") or d.get("to_id") or "")
            rel = str(d.get("relation_type") or d.get("relation") or d.get("edge_type") or "unknown")
            if src and tgt:
                pipe.sadd(f"adg:edge:{src}:{rel}", tgt)  # fan-out
                pipe.sadd(f"adg:edge:in:{tgt}:{rel}", src)  # fan-in
            batch += 1
            if batch >= BATCH_SIZE:
                pipe.execute()
                pipe = r.pipeline(transaction=False)
                batch = 0
                print(f"  edges ... {i}/{edge_count}", end="\r")
        if batch:
            pipe.execute()
        print("\n[redis] edges done")

    # -- Violations (if present) --
    for vtable in ("violations", "layer_violations"):
        if vtable in tables:
            cur.execute(f"SELECT * FROM {vtable}")
            rows = [dict(r) for r in cur.fetchall()]
            if rows:
                pipe = r.pipeline(transaction=False)
                for row in rows:
                    pipe.rpush("adg:violations", json.dumps(row))
                pipe.execute()
                print(f"[redis] {len(rows)} violations stored")

    # -- Snapshot JSON --
    with open(snapshot_path, encoding="utf-8") as f:
        snap_raw = f.read()
    r.set("adg:snapshot", snap_raw)
    snap = json.loads(snap_raw)
    print("[redis] snapshot stored")

    # -- Meta sentinel --
    r.hmset(
        "adg:meta",
        {
            "sqlite_path": sqlite_path,
            "sqlite_mtime": str(sqlite_mtime),
            "timestamp": SNAPSHOT_SUFFIX,
            "ingested_at": str(time.time()),
            "node_count": str(snap.get("counts", {}).get("module_count", 0)),
            "edge_count": str(snap.get("counts", {}).get("total_relations", 0)),
            "digest": snap.get("artifact_digest", ""),
        },
    )
    print("[redis] meta written")

    conn.close()
    print("[done] ADG -> Redis ingest complete")


if __name__ == "__main__":
    force = "--force" in sys.argv
    ingest(force=force)
