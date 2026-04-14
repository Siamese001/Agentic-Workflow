#!/usr/bin/env python3
"""ADG Redis Ingest — Bulk-load ADG SQLite snapshot into Redis hot cache.

Reads the latest adg_indexed_*.sqlite from artifacts/adg/, walks all nodes
and edges, and writes them into Redis using the same key scheme as RedisCache
so ADGService.get_node() / get_edge_fanout() get cache hits immediately.

Key scheme (mirrors tools/adg/cache/redis_cache.py):
    adg:v1:<snapshot_id>:node:<node_id>          → HSET (node fields, pre-ingested)
    adg:v1:<snapshot_id>:edge:<src_id>:<rel>     → SADD <edge_id> (fanout index, pre-ingested)
    adg:v1:<snapshot_id>:fanin:<dst_id>:<rel>    → SADD <edge_id> (fanin index, pre-ingested)
    adg:v1:<snapshot_id>:edge_detail:<edge_id>   → HSET (pre-ingested — first MCP query hits Redis directly)
    adg:v1:<snapshot_id>:_hot                    → SET 1 (sentinel — cache is populated)

Usage:
    python tools/adg/adg_redis_ingest.py           # ingest latest snapshot
    python tools/adg/adg_redis_ingest.py --force   # flush old snapshot first
    python tools/adg/adg_redis_ingest.py --check   # check if cache is hot (exit 0=hot, 1=cold)
    python tools/adg/adg_redis_ingest.py --dry-run # count rows, no writes
"""

from __future__ import annotations

import argparse
import os
import sqlite3
import sys
import time
from pathlib import Path
from typing import Any

from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[2]
CACHE_VERSION = "v1"
REDIS_URL = os.getenv("ADG_REDIS_URL", "redis://localhost:6379/0")
BATCH_SIZE = 5000  # nodes/edges per Redis pipeline flush
PROGRESS_INTERVAL = 10000  # print progress every N items


def _find_latest_sqlite(adg_dir: Path) -> Path:
    if not adg_dir.exists() or not adg_dir.is_dir():
        print(f"ERROR: ADG artifacts directory not found: {adg_dir}", file=sys.stderr)
        sys.exit(1)
    files = sorted(adg_dir.glob("adg_indexed_*.sqlite"))
    if not files:
        print(f"ERROR: No adg_indexed_*.sqlite found in {adg_dir}", file=sys.stderr)
        sys.exit(1)
    return files[-1]


def _snapshot_id_from_path(sqlite_path: Path) -> str:
    return sqlite_path.stem.replace("adg_indexed_", "")


def _redis_key(snapshot_id: str, base: str) -> str:
    return f"adg:{CACHE_VERSION}:{snapshot_id}:{base}"


def _connect_redis():
    try:
        import redis
    except ImportError:
        print("ERROR: redis package not installed. Run: pip install redis", file=sys.stderr)
        sys.exit(1)

    try:
        client = redis.from_url(
            REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=10,
        )
        client.ping()
        return client
    except (ValueError, OSError, redis.RedisError) as exc:
        print(f"ERROR: Cannot connect to Redis at {REDIS_URL}: {exc}", file=sys.stderr)
        sys.exit(1)


def _hset_mapping(pipe: Any, key: str, mapping: dict[str, str]) -> None:
    """Write a Redis hash using the modern hset(mapping=...) API."""
    pipe.hset(key, mapping=mapping)


def _flush_old_snapshots(client, current_snapshot_id: str) -> int:
    """Delete all adg:v1:* keys that belong to a different snapshot."""
    deleted = 0
    cursor = 0
    pattern = f"adg:{CACHE_VERSION}:*"
    prefix_keep = f"adg:{CACHE_VERSION}:{current_snapshot_id}:"

    while True:
        cursor, keys = client.scan(cursor=cursor, match=pattern, count=200)
        to_delete = [k for k in keys if not k.startswith(prefix_keep)]
        if to_delete:
            client.delete(*to_delete)
            deleted += len(to_delete)
        if cursor == 0:
            break

    return deleted


def _check_hot(client, snapshot_id: str) -> bool:
    """Return True if the sentinel key exists (cache is populated)."""
    sentinel = _redis_key(snapshot_id, "_hot")
    return bool(client.exists(sentinel))


def ingest(sqlite_path: Path, client, force: bool = False, dry_run: bool = False) -> dict:
    snapshot_id = _snapshot_id_from_path(sqlite_path)
    sentinel_key = _redis_key(snapshot_id, "_hot")
    print(f"[adg_redis_ingest] Snapshot : {snapshot_id}")
    print(f"[adg_redis_ingest] SQLite   : {sqlite_path}")
    print(f"[adg_redis_ingest] Redis    : {REDIS_URL}")

    if not force and not dry_run and _check_hot(client, snapshot_id):
        print("[adg_redis_ingest] Cache already HOT — skipping (use --force to re-ingest)")
        return {"status": "already_hot", "snapshot_id": snapshot_id}

    conn: sqlite3.Connection | None = None
    try:
        conn = sqlite3.connect(str(sqlite_path), timeout=10)
        conn.row_factory = sqlite3.Row

        node_count = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
        edge_count = conn.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
        print(f"[adg_redis_ingest] Nodes    : {node_count:,}")
        print(f"[adg_redis_ingest] Edges    : {edge_count:,}")

        if dry_run:
            print("[adg_redis_ingest] DRY RUN — no writes performed")
            return {"status": "dry_run", "node_count": node_count, "edge_count": edge_count}

        # Clear the hot sentinel before writing so interrupted runs never look healthy.
        client.delete(sentinel_key)

        # Flush old snapshot keys before writing new ones.
        if force:
            deleted = _flush_old_snapshots(client, snapshot_id)
            if deleted:
                print(f"[adg_redis_ingest] Flushed  : {deleted:,} stale keys")

        t0 = time.monotonic()

        # --- Ingest nodes ---
        nodes_written = 0
        cursor_nodes = conn.execute("SELECT * FROM nodes")
        pipe = client.pipeline(transaction=False)
        while True:
            batch = cursor_nodes.fetchmany(BATCH_SIZE)
            if not batch:
                break
            for row in batch:
                raw = dict(row)
                data = {k: str(v) for k, v in raw.items() if v is not None}
                if not data or "id" not in data:
                    continue
                key = _redis_key(snapshot_id, f"node:{data['id']}")
                _hset_mapping(pipe, key, data)
                nodes_written += 1
            pipe.execute()
            pipe = client.pipeline(transaction=False)
            if nodes_written and nodes_written % PROGRESS_INTERVAL == 0:
                print(f"[adg_redis_ingest]   nodes {nodes_written:,}/{node_count:,}...", end="\r")
        pipe.execute()
        print(f"[adg_redis_ingest] Nodes written : {nodes_written:,}          ")

        # --- Ingest edges (fanout + fanin indexes + edge_detail hashes — fully hot at startup) ---
        edges_written = 0
        cursor_edges = conn.execute(
            "SELECT id, src_id, dst_id, relation_type, edge_kind, source_file, line_no, symbol FROM edges"
        )
        pipe = client.pipeline(transaction=False)
        while True:
            batch = cursor_edges.fetchmany(BATCH_SIZE)
            if not batch:
                break
            for row in tqdm(batch, desc="Ingesting edges", unit="edge", leave=False):
                edge_id = str(row[0])
                src_id = str(row[1])
                dst_id = str(row[2])
                relation_type = str(row[3])
                # Fanout index (edges going out from src_id)
                fanout_key = _redis_key(snapshot_id, f"edge:{src_id}:{relation_type}")
                pipe.sadd(fanout_key, edge_id)
                # Fanin index (edges coming in to dst_id)
                fanin_key = _redis_key(snapshot_id, f"fanin:{dst_id}:{relation_type}")
                pipe.sadd(fanin_key, edge_id)
                # Edge detail hash — pre-written so first MCP query hits Redis with no SQLite round-trip
                detail_key = _redis_key(snapshot_id, f"edge_detail:{edge_id}")
                detail = {
                    "id": edge_id,
                    "src_id": src_id,
                    "dst_id": dst_id,
                    "relation_type": relation_type,
                    "edge_kind": str(row[4]),
                }
                if row[5] is not None:
                    detail["source_file"] = str(row[5])
                if row[6] is not None:
                    detail["line_no"] = str(row[6])
                if row[7] is not None:
                    detail["symbol"] = str(row[7])
                _hset_mapping(pipe, detail_key, detail)
                edges_written += 1
            pipe.execute()
            pipe = client.pipeline(transaction=False)
            if edges_written and edges_written % PROGRESS_INTERVAL == 0:
                print(f"[adg_redis_ingest]   edges {edges_written:,}/{edge_count:,}...", end="\r")
        pipe.execute()
        print(f"[adg_redis_ingest] Edges written : {edges_written:,}          ")

        # Write the sentinel only after a fully successful ingest.
        client.set(sentinel_key, "1")

        elapsed = time.monotonic() - t0
        print(f"[adg_redis_ingest] Done in {elapsed:.1f}s — cache is HOT ✓")

        return {
            "status": "ingested",
            "snapshot_id": snapshot_id,
            "nodes_written": nodes_written,
            "edges_written": edges_written,
            "elapsed_seconds": round(elapsed, 2),
        }
    finally:
        if conn is not None:
            conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest ADG SQLite into Redis hot cache")
    parser.add_argument(
        "--force", action="store_true", help="Flush old snapshot keys and re-ingest even if cache is hot"
    )
    parser.add_argument(
        "--check", action="store_true", help="Check if cache is hot (exit 0=hot, 1=cold, no writes)"
    )
    parser.add_argument("--dry-run", action="store_true", help="Count rows and report, no Redis writes")
    args = parser.parse_args()

    if args.check and (args.force or args.dry_run):
        parser.error("--check cannot be combined with --force or --dry-run")

    adg_dir = ROOT / "artifacts" / "adg"
    sqlite_path = _find_latest_sqlite(adg_dir)
    snapshot_id = _snapshot_id_from_path(sqlite_path)

    client = _connect_redis()

    if args.check:
        hot = _check_hot(client, snapshot_id)
        status = "HOT" if hot else "COLD"
        print(f"[adg_redis_ingest] Cache is {status} for snapshot {snapshot_id}")
        return 0 if hot else 1

    result = ingest(sqlite_path, client, force=args.force, dry_run=args.dry_run)
    return 0 if result["status"] in ("ingested", "already_hot", "dry_run") else 1


if __name__ == "__main__":
    sys.exit(main())
