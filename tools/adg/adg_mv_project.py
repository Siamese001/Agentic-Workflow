#!/usr/bin/env python3
"""ADG MV Redis Projection CLI — Project materialized views + P-views into Redis.

Standalone companion to `adg_redis_ingest.py`. Keeps the canonical node/edge
ingest untouched and projects the ADG graph-layer MVs (`mv_*`) and P-views
(`v_p*`) from the latest SQLite snapshot into Redis as ZSETs/SETs for sub-ms
top-K and O(1) membership queries.

SSOT: SQLite. Redis is a deterministic read-only projection.

Usage:
    python tools/adg/adg_mv_project.py           # project latest snapshot (idempotent)
    python tools/adg/adg_mv_project.py --force   # re-project even if already hot
    python tools/adg/adg_mv_project.py --check   # exit 0=hot / 1=cold
    python tools/adg/adg_mv_project.py --sqlite <path>  # explicit snapshot path

See .windsurf/plans/redis-mv-projections-9262a6.md for design & rationale.
"""

from __future__ import annotations

import argparse
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.adg.mv_projection import is_mv_hot, project_all  # noqa: E402

REDIS_URL = os.getenv("ADG_REDIS_URL", "redis://localhost:6379/0")


def _find_latest_sqlite(adg_dir: Path) -> Path:
    if not adg_dir.exists() or not adg_dir.is_dir():
        print(f"ERROR: ADG artifacts directory not found: {adg_dir}", file=sys.stderr)
        sys.exit(1)
    files = list(adg_dir.glob("adg_indexed_*.sqlite"))
    if not files:
        print(f"ERROR: No adg_indexed_*.sqlite found in {adg_dir}", file=sys.stderr)
        sys.exit(1)

    def _valid(p: Path) -> bool:
        try:
            datetime.strptime(p.stem.replace("adg_indexed_", ""), "%m%d%Y_%H%M")
            return True
        except ValueError:
            return False

    valid = [p for p in files if _valid(p)]
    if not valid:
        print(f"ERROR: No valid timestamped snapshots in {adg_dir}", file=sys.stderr)
        sys.exit(1)
    return max(valid, key=lambda p: p.stat().st_mtime)


def _snapshot_id(path: Path) -> str:
    return path.stem.replace("adg_indexed_", "")


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


def project(sqlite_path: Path, client, force: bool = False) -> dict:
    snap = _snapshot_id(sqlite_path)
    print(f"[adg_mv_project] snapshot={snap}")
    print(f"[adg_mv_project] sqlite={sqlite_path}")
    print(f"[adg_mv_project] redis={REDIS_URL}")

    if not force and is_mv_hot(client, snap):
        print("[adg_mv_project] MV cache already HOT — skipping (use --force)")
        return {"status": "already_hot", "snapshot_id": snap}

    conn: sqlite3.Connection | None = None
    try:
        conn = sqlite3.connect(str(sqlite_path), timeout=10)
        conn.row_factory = sqlite3.Row
        result = project_all(conn, client, snap)
        print(
            f"[adg_mv_project] projected {result['mv_total_rows']:,} MV rows + "
            f"{result['pview_total_rows']:,} P-view rows in "
            f"{result['elapsed_seconds']}s — MV cache HOT ✓"
        )
        for r in result["mv_results"]:
            print(f"  mv: {r['table']:<45} status={r['status']:<10} rows={r['rows']:,}")
        for r in result["pview_results"]:
            print(f"  pv: {r['view']:<45} status={r['status']:<10} rows={r['rows']:,}")
        return result
    finally:
        if conn is not None:
            conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Project ADG MVs + P-views into Redis")
    parser.add_argument("--force", action="store_true", help="Re-project even if MV cache already hot")
    parser.add_argument("--check", action="store_true", help="Exit 0 if MV cache hot, 1 if cold")
    parser.add_argument("--sqlite", type=str, default=None, help="Explicit snapshot path (default: latest)")
    args = parser.parse_args()

    adg_dir = ROOT / "artifacts" / "adg"
    sqlite_path = Path(args.sqlite) if args.sqlite else _find_latest_sqlite(adg_dir)
    snap = _snapshot_id(sqlite_path)
    client = _connect_redis()

    if args.check:
        hot = is_mv_hot(client, snap)
        status = "HOT" if hot else "COLD"
        print(f"[adg_mv_project] MV cache is {status} for snapshot {snap}")
        return 0 if hot else 1

    result = project(sqlite_path, client, force=args.force)
    return 0 if result["status"] in ("ok", "already_hot") else 1


if __name__ == "__main__":
    sys.exit(main())
