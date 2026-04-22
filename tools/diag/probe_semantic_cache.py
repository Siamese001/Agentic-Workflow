"""CLI probe: report operational status of the L0→L4 semantic cache stack.

Outputs flag state, L2 SQLite row count, Chroma collection presence, Redis
``memory:*`` key count, and live ``SemanticCacheManager`` stats. Exits 0 if
both L1 and L2 are enabled and reachable, 1 otherwise.

Run::

    python tools/diag/probe_semantic_cache.py
"""

from __future__ import annotations

import json
import os
import sqlite3
import sys
from pathlib import Path
from typing import Any


def _probe_env() -> dict[str, str]:
    keys = [
        "SEMANTIC_CACHE_D2_ENABLED",
        "SEMANTIC_CACHE_PROMOTE_ENABLED",
        "SEMANTIC_CACHE_L1_WARMUP_LIMIT",
        "HIVE_MIND_STRICT_MODE",
        "HIVE_MIND_PROMOTION_THRESHOLD",
        "REDIS_URL",
    ]
    return {k: os.environ.get(k, "<unset>") for k in keys}


def _probe_l2_sqlite(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False, "path": str(path)}
    conn = sqlite3.connect(str(path))
    try:
        count = conn.execute("SELECT COUNT(*) FROM l2_cache").fetchone()[0]
    except sqlite3.Error as err:
        return {"exists": True, "path": str(path), "rows": None, "error": str(err)}
    finally:
        conn.close()
    return {"exists": True, "path": str(path), "rows": count, "size_bytes": path.stat().st_size}


def _probe_chroma(path: Path) -> dict[str, Any]:
    return {"exists": path.exists(), "path": str(path)}


def _probe_redis() -> dict[str, Any]:
    try:
        import redis  # noqa: PLC0415
    except ImportError as err:
        return {"available": False, "error": f"redis package missing: {err}"}
    url = os.environ.get("REDIS_URL", "redis://localhost:6379")
    try:
        client = redis.from_url(url, decode_responses=True)
        client.ping()
    except (ConnectionError, TimeoutError, OSError, ValueError) as err:
        return {"available": False, "url": url, "error": str(err)}
    keys = list(client.scan_iter(match="memory:*", count=1000))
    return {"available": True, "url": url, "memory_keys": len(keys), "sample": keys[:5]}


def _probe_manager() -> dict[str, Any]:
    try:
        from agentic_core.L4_state.utils.memory.semantic_cache_manager import (  # noqa: PLC0415
            SemanticCacheManager,
        )
    except ImportError as err:
        return {"available": False, "error": f"import failed: {err}"}
    try:
        mgr = SemanticCacheManager.get_instance()
    except (RuntimeError, ValueError, OSError) as err:
        return {"available": False, "error": f"init failed: {err}"}
    stats = mgr.get_statistics()
    return {
        "available": True,
        "redis_enabled": mgr.redis_enabled,
        "gptcache_enabled": mgr.gptcache_enabled,
        "stateless_mode": mgr.stateless_mode,
        "stats": stats,
    }


def main() -> int:
    report: dict[str, Any] = {
        "env": _probe_env(),
        "l2_sqlite": _probe_l2_sqlite(Path("artifacts/gptcache/l2_cache.db")),
        "l2_chroma": _probe_chroma(Path("artifacts/gptcache/chroma")),
        "redis": _probe_redis(),
        "manager": _probe_manager(),
    }
    print(json.dumps(report, indent=2, default=str))
    operational = (
        report["env"]["SEMANTIC_CACHE_D2_ENABLED"] == "1"
        and report["redis"].get("available")
        and report["manager"].get("available")
        and report["manager"].get("redis_enabled")
    )
    print(f"\n[PROBE] operational={operational}", file=sys.stderr)
    return 0 if operational else 1


if __name__ == "__main__":
    raise SystemExit(main())
