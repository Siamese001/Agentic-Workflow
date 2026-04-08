#!/usr/bin/env python3
"""
pre_mcp_gate.py — Windsurf pre_mcp_tool_use hard gate (Phase 1.3).

Reads JSON payload from stdin. Payload fields:
  tool_info.mcp_server_name  — name of MCP server being called
  tool_info.mcp_tool_name    — name of tool being called (optional)

Behavior:
  - Non-ADG MCPs → exit 0 immediately (FAIL-OPEN for non-ADG)
  - ADG MCP (mcp_server_name == "adg_sqlite"):
      * Check if any adg_indexed_*.sqlite file has an active write lock → EXIT 2
      * Check if ADG health timestamp is >30 min stale (via artifacts/adg/) → EXIT 2

Fail policy: CLOSED for ADG calls, OPEN for non-ADG.
Zero hardcoded paths — REPO_ROOT resolved from __file__.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

FAIL_POLICY = "closed"
ADG_SERVER_NAME = "adg_sqlite"
STALE_THRESHOLD_SECONDS = 30 * 60  # 30 minutes

# Recovery tools that MUST pass even when ADG is stale/locked.
# Without this whitelist, the gate blocks the very tools needed to recover.
ADG_RECOVERY_TOOLS = {
    "adg_health",  # mcp1_adg_health — liveness probe
    "adg_status",  # mcp1_adg_status — snapshot status
    "adg_close_connections",  # needed to release SQLite locks
    "adg_reopen_connections",  # needed after lock release
}

REPO_ROOT = Path(__file__).resolve().parents[3]
ARTIFACTS_ADG = REPO_ROOT / "artifacts" / "adg"


def _exit_block(reason: str) -> int:
    print(f"[pre_mcp_gate] BLOCKED: {reason}", file=sys.stderr)
    return 2


def _is_sqlite_locked(repo_root: Path) -> bool:
    """
    Check if any adg_indexed_*.sqlite has a companion .sqlite-wal file
    (WAL mode write lock indicator) or .sqlite-journal (rollback journal).
    These indicate an active write transaction.
    """
    adg_dir = repo_root / "artifacts" / "adg"
    if not adg_dir.exists():
        return False

    for sqlite_file in adg_dir.glob("adg_indexed_*.sqlite"):
        if (sqlite_file.parent / (sqlite_file.name + "-wal")).exists():
            return True
        if (sqlite_file.parent / (sqlite_file.name + "-journal")).exists():
            return True
    return False


def _get_latest_snapshot_age_seconds(repo_root: Path) -> float | None:
    """
    Find the most recent adg_snapshot_*.json in artifacts/adg/ and return
    its age in seconds. Returns None if no snapshot found.
    Uses file mtime as proxy for snapshot recency.
    """
    adg_dir = repo_root / "artifacts" / "adg"
    if not adg_dir.exists():
        return None

    snapshots = list(adg_dir.glob("adg_snapshot_*.json"))
    if not snapshots:
        return None

    newest = max(snapshots, key=lambda p: p.stat().st_mtime)
    age = datetime.now(timezone.utc).timestamp() - newest.stat().st_mtime
    return age


def check_adg_gate(repo_root: Path) -> int:
    """Check ADG-specific gates. Return 0 (allow) or 2 (block)."""
    if _is_sqlite_locked(repo_root):
        return _exit_block(
            "ADG SQLite is locked (WAL/journal file detected). "
            "Call mcp1_adg_close_connections before retrying ADG tools.",
        )

    age = _get_latest_snapshot_age_seconds(repo_root)
    if age is not None and age > STALE_THRESHOLD_SECONDS:
        minutes = int(age // 60)
        return _exit_block(
            f"ADG health is stale ({minutes} min old, threshold 30 min). "
            "Run mcp1_adg_health first to verify ADG MCP is healthy.",
        )

    return 0


def main() -> int:
    raw = sys.stdin.read()
    if not raw.strip():
        print("[pre_mcp_gate] WARNING: empty stdin payload — allowing (non-ADG assumed).", file=sys.stderr)
        return 0

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        print("[pre_mcp_gate] WARNING: malformed JSON payload — allowing (non-ADG assumed).", file=sys.stderr)
        return 0

    tool_info = payload.get("tool_info", payload)
    server_name = tool_info.get("mcp_server_name", "")

    if server_name != ADG_SERVER_NAME:
        return 0

    tool_name = tool_info.get("mcp_tool_name", "")
    if tool_name in ADG_RECOVERY_TOOLS:
        # Always allow recovery probes — blocking them creates a dead loop
        # where the gate blocks the only tools that can restore health.
        return 0

    return check_adg_gate(REPO_ROOT)


if __name__ == "__main__":
    sys.exit(main())
