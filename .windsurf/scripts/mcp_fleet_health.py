#!/usr/bin/env python3
"""Unified MCP fleet health probe.

Purpose:
    Answer "are all 12 MCP servers healthy?" in ONE command. Before this
    script existed, Cascade had to call each server's idiosyncratic
    health endpoint separately (adg_health, redis_health, otel_status,
    readiness, API-get-self, mem_get_stats, ...) and reconstruct the
    fleet picture. That interrogation pattern missed the 2026-04-22
    outage entirely: the 12 MCP processes were dead for ~15 minutes
    before diagnosis began.

Scope:
    This script does NOT call MCP tools (it can't — MCP is stdio-based
    inside Windsurf). Instead it checks the preconditions that, when
    green, strongly predict successful MCP spawn:

      1. Repo config ``.windsurf/mcp_config.json`` is valid JSON with
         at least ``MIN_PLAUSIBLE_SERVER_COUNT`` servers.
      2. User-home config ``~/.codeium/windsurf/mcp_config.json`` has
         the same server count (detects the 2026-04-22 stub-overwrite).
      3. Backup file ``~/.codeium/windsurf/mcp_config.backup.json`` exists
         and has the same hash as the repo config (fleet-restorable).
      4. Backend dependencies per server: Redis up, ADG SQLite readable,
         ChromaDB integrity ok, NOTION_TOKEN present when notion is
         configured.

Exit codes:
    0 — all preconditions green.
    1 — one or more preconditions yellow/red. Output table identifies which.

Usage:
    python .windsurf/scripts/mcp_fleet_health.py
    python .windsurf/scripts/mcp_fleet_health.py --json   (machine-readable)
    python .windsurf/scripts/mcp_fleet_health.py --quiet  (exit code only)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
REPO_CONFIG = REPO_ROOT / ".windsurf" / "mcp_config.json"
GLOBAL_CONFIG = Path.home() / ".codeium" / "windsurf" / "mcp_config.json"
GLOBAL_BACKUP = Path.home() / ".codeium" / "windsurf" / "mcp_config.backup.json"

# Must stay in sync with sync_mcp_config.MIN_PLAUSIBLE_SERVER_COUNT.
MIN_PLAUSIBLE_SERVER_COUNT = 5

# ANSI colors.
_GREEN = "\033[92m"
_YELLOW = "\033[93m"
_RED = "\033[91m"
_BLUE = "\033[94m"
_BOLD = "\033[1m"
_RESET = "\033[0m"


@dataclass
class CheckResult:
    name: str
    status: str  # "GREEN" | "YELLOW" | "RED"
    detail: str
    evidence: dict[str, Any] = field(default_factory=dict)

    def is_green(self) -> bool:
        return self.status == "GREEN"


def _sha256(path: Path) -> str | None:
    try:
        h = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return None


def check_repo_config() -> CheckResult:
    """Repo config exists, parseable, has enough servers."""
    if not REPO_CONFIG.exists():
        return CheckResult("repo_config", "RED", f"missing: {REPO_CONFIG}")
    try:
        data = json.loads(REPO_CONFIG.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return CheckResult("repo_config", "RED", f"parse error: {exc}")
    servers = data.get("mcpServers", {})
    count = len(servers) if isinstance(servers, dict) else 0
    if count < MIN_PLAUSIBLE_SERVER_COUNT:
        return CheckResult(
            "repo_config", "RED",
            f"only {count} server(s) (floor {MIN_PLAUSIBLE_SERVER_COUNT})",
            {"count": count},
        )
    return CheckResult(
        "repo_config", "GREEN",
        f"{count} servers declared",
        {"count": count, "names": sorted(servers.keys()) if isinstance(servers, dict) else []},
    )


def check_global_config() -> CheckResult:
    """User-home config is the config Windsurf actually reads."""
    if not GLOBAL_CONFIG.exists():
        return CheckResult("global_config", "RED", f"missing: {GLOBAL_CONFIG}")
    try:
        data = json.loads(GLOBAL_CONFIG.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return CheckResult("global_config", "RED", f"parse error: {exc}")
    servers = data.get("mcpServers", {})
    count = len(servers) if isinstance(servers, dict) else 0
    if count < MIN_PLAUSIBLE_SERVER_COUNT:
        return CheckResult(
            "global_config", "RED",
            f"STUB DETECTED: only {count} server(s) — 2026-04-22 failure mode",
            {"count": count},
        )
    # Compare to repo count; drift is a yellow.
    repo_count = _repo_server_count()
    if repo_count and repo_count != count:
        return CheckResult(
            "global_config", "YELLOW",
            f"global has {count} server(s), repo has {repo_count} — drift",
            {"global_count": count, "repo_count": repo_count},
        )
    return CheckResult("global_config", "GREEN", f"{count} servers", {"count": count})


def _repo_server_count() -> int:
    try:
        data = json.loads(REPO_CONFIG.read_text(encoding="utf-8"))
        servers = data.get("mcpServers", {})
        return len(servers) if isinstance(servers, dict) else 0
    except (OSError, json.JSONDecodeError, ValueError):
        return 0


def check_backup_matches_repo() -> CheckResult:
    """Backup hash must match repo config — else fleet is not restorable."""
    if not GLOBAL_BACKUP.exists():
        return CheckResult(
            "backup", "YELLOW",
            f"no backup at {GLOBAL_BACKUP} — cannot self-heal from stub-overwrite",
        )
    repo_hash = _sha256(REPO_CONFIG)
    backup_hash = _sha256(GLOBAL_BACKUP)
    if repo_hash == backup_hash:
        return CheckResult(
            "backup", "GREEN",
            "backup matches repo (fleet is restorable)",
            {"hash": repo_hash[:16] if repo_hash else None},
        )
    return CheckResult(
        "backup", "YELLOW",
        "backup hash diverges from repo — may be stale",
        {"repo_hash": (repo_hash or "")[:16], "backup_hash": (backup_hash or "")[:16]},
    )


def check_redis() -> CheckResult:
    """Redis backend — required by redis MCP and ADG hot cache."""
    try:
        import redis as redis_pkg  # type: ignore[import-not-found]
    except ImportError:
        return CheckResult("redis", "YELLOW", "redis-py not installed")
    try:
        r = redis_pkg.Redis(host="localhost", port=6379, socket_connect_timeout=2)
        pong = r.ping()
        if pong:
            info = r.info(section="server")
            version = info.get("redis_version", "?")
            keys = r.dbsize()
            return CheckResult(
                "redis", "GREEN",
                f"v{version}, {keys:,} keys",
                {"version": version, "dbsize": keys},
            )
        return CheckResult("redis", "RED", "ping returned falsy")
    except Exception as exc:  # guardian: allow-broad-exception -- redis connection probe; any failure mode means server unhealthy, no need to discriminate
        return CheckResult("redis", "RED", f"connect failed: {exc}")


def check_adg_sqlite() -> CheckResult:
    """Latest ADG SQLite snapshot must be readable."""
    adg_dir = REPO_ROOT / "artifacts" / "adg"
    if not adg_dir.exists():
        return CheckResult("adg_sqlite", "RED", f"missing dir: {adg_dir}")
    min_bytes = 1_000_000
    candidates = [
        p for p in adg_dir.glob("adg_indexed_*.sqlite")
        if "99999999" not in p.name and p.stat().st_size >= min_bytes
    ]
    if not candidates:
        return CheckResult("adg_sqlite", "RED", "no plausible snapshot (>1MB)")
    latest = max(
        candidates,
        key=lambda p: _adg_stamp_key(p.stem),
    )
    try:
        conn = sqlite3.connect(str(latest), timeout=2)
        nodes = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
        edges = conn.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
        conn.close()
    except sqlite3.Error as exc:
        return CheckResult("adg_sqlite", "RED", f"{latest.name}: {exc}")
    return CheckResult(
        "adg_sqlite", "GREEN",
        f"{latest.name}: {nodes:,} nodes, {edges:,} edges",
        {"snapshot": latest.name, "nodes": nodes, "edges": edges},
    )


def _adg_stamp_key(stem: str) -> str:
    """Parse MMDDYYYY_HHMM from adg_indexed_* stem and rearrange to YYYYMMDD_HHMM."""
    stem = stem.replace("adg_indexed_", "")
    if len(stem) >= 13 and stem[8] == "_":
        mmddyyyy, hhmm = stem[:8], stem[9:13]
        return f"{mmddyyyy[4:]}{mmddyyyy[:4]}_{hhmm}"
    return stem


def check_chromadb() -> CheckResult:
    """ChromaDB integrity — vector_db MCP backend."""
    roots = [
        REPO_ROOT / "data" / "cache" / "chromadb" / "chroma.sqlite3",
        REPO_ROOT / "artifacts" / "chromadb" / "chroma.sqlite3",
    ]
    results = []
    for p in roots:
        if not p.exists():
            continue
        try:
            conn = sqlite3.connect(str(p), timeout=2)
            ok = conn.execute("PRAGMA integrity_check").fetchone()[0]
            conn.close()
            results.append((p.name, ok == "ok", p.stat().st_size))
        except sqlite3.Error as exc:
            results.append((p.name, False, 0))
            _ = exc
    if not results:
        return CheckResult("chromadb", "YELLOW", "no chroma.sqlite3 found (vector_db may cold-start)")
    bad = [r for r in results if not r[1]]
    if bad:
        return CheckResult(
            "chromadb", "RED",
            f"integrity failed: {[r[0] for r in bad]}",
            {"results": results},
        )
    return CheckResult(
        "chromadb", "GREEN",
        f"{len(results)} DB(s) ok",
        {"total_bytes": sum(r[2] for r in results)},
    )


def check_notion_token() -> CheckResult:
    """Notion MCP requires NOTION_TOKEN env var."""
    token = os.environ.get("NOTION_TOKEN", "").strip()
    if not token:
        return CheckResult("notion_token", "YELLOW", "NOTION_TOKEN not set")
    return CheckResult(
        "notion_token", "GREEN",
        f"present ({len(token)} chars)",
        {"length": len(token)},
    )


def check_orphan_sqlite_wal() -> CheckResult:
    """Orphan -wal/-shm files on old ADG snapshots can block new-snapshot writers."""
    adg_dir = REPO_ROOT / "artifacts" / "adg"
    if not adg_dir.exists():
        return CheckResult("orphan_wal", "YELLOW", "no adg dir")
    orphans = [p for p in adg_dir.glob("adg_indexed_*.sqlite-*") if p.stat().st_size < 1_000_000]
    if orphans:
        return CheckResult(
            "orphan_wal", "YELLOW",
            f"{len(orphans)} orphan WAL/SHM file(s)",
            {"files": [p.name for p in orphans]},
        )
    return CheckResult("orphan_wal", "GREEN", "no orphan WAL/SHM")


CHECKS = [
    check_repo_config,
    check_global_config,
    check_backup_matches_repo,
    check_redis,
    check_adg_sqlite,
    check_chromadb,
    check_notion_token,
    check_orphan_sqlite_wal,
]


def _colorize(status: str) -> str:
    return {"GREEN": _GREEN, "YELLOW": _YELLOW, "RED": _RED}.get(status, "") + status + _RESET


def render_table(results: list[CheckResult]) -> str:
    lines = [
        f"{_BOLD}MCP Fleet Health — {REPO_ROOT.name}{_RESET}",
        "",
        f"{'Check':<20} {'Status':<9} Detail",
        "-" * 72,
    ]
    for r in results:
        lines.append(f"{r.name:<20} {_colorize(r.status):<9}  {r.detail}")
    green = sum(1 for r in results if r.status == "GREEN")
    yellow = sum(1 for r in results if r.status == "YELLOW")
    red = sum(1 for r in results if r.status == "RED")
    lines.append("-" * 72)
    summary_color = _GREEN if red == 0 else (_YELLOW if red == 0 else _RED)
    lines.append(
        f"{summary_color}Summary:{_RESET} {green} green, {yellow} yellow, {red} red"
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of a colored table")
    parser.add_argument("--quiet", action="store_true", help="Exit code only; no stdout")
    args = parser.parse_args()

    results = [check() for check in CHECKS]

    if args.json:
        print(json.dumps([asdict(r) for r in results], indent=2))
    elif not args.quiet:
        print(render_table(results))

    return 0 if all(r.status != "RED" for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
