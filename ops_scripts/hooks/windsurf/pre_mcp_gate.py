#!/usr/bin/env python3
"""
pre_mcp_gate.py — Windsurf pre_mcp_tool_use hard gate (Phase 1.3).

Reads JSON payload from stdin. Payload fields:
  tool_info.mcp_server_name  — name of MCP server being called
  tool_info.mcp_tool_name    — name of tool being called (optional)

Behavior:
  - Filesystem MCP (mcp_server_name == "filesystem") write tools → EXIT 2
      * write_file and edit_file are BLOCKED — Windsurf does not pass tool
        arguments to pre_mcp_tool_use hooks, so content validation is impossible
        at this layer. Writes must go through Cascade's native write tools
        (write_to_file, edit, multi_edit) which DO invoke pre_write_code and
        the constitutional anti-pattern + syntax gates.
      * Read-only tools (read_text_file, list_directory, etc.) → exit 0.
  - ADG MCP (mcp_server_name == "adg_sqlite"):
      * No adg_indexed_*.sqlite file found → auto-run generate_full_adg.py; EXIT 2 if it fails
      * Check if any adg_indexed_*.sqlite file has an active write lock → EXIT 2
      * Check if ADG health timestamp is >30 min stale (via artifacts/adg/) → EXIT 2
  - All other MCPs → exit 0 (FAIL-OPEN).

Fail policy: CLOSED for ADG and filesystem-write calls, OPEN for everything else.
Zero hardcoded paths — REPO_ROOT resolved from __file__.
"""

import json
import sqlite3
import subprocess
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

# Write-affecting ADG tools that mutate DB state.
# These require a BEGIN IMMEDIATE probe to detect real write contention.
ADG_WRITE_TOOLS = {
    "adg_rebuild",
    "adg_checkpoint",
    "adg_compact",
}

SQLITE_PROBE_TIMEOUT_MS = 500  # busy_timeout for probe connections

FILESYSTEM_SERVER_NAME = "filesystem"
# Write tools on the filesystem MCP that bypass pre_write_code. Blocked here
# so all .py writes are forced through Cascade's native tools and the
# constitutional anti-pattern + syntax gates.
FILESYSTEM_WRITE_TOOLS = {
    "write_file",  # mcp5_write_file — full overwrite
    "edit_file",  # mcp5_edit_file  — line-based edits
}

REPO_ROOT = Path(__file__).resolve().parents[3]
ARTIFACTS_ADG = REPO_ROOT / "artifacts" / "adg"


def _exit_block(reason: str) -> int:
    print(f"[pre_mcp_gate] BLOCKED: {reason}", file=sys.stderr)
    return 2


def _has_adg_sqlite(repo_root: Path) -> bool:
    """
    Return True if at least one adg_indexed_*.sqlite file exists in artifacts/adg/.
    An empty (no-sqlite) state means ADG has never been generated or was wiped.
    """
    adg_dir = repo_root / "artifacts" / "adg"
    if not adg_dir.exists():
        return False
    return any(adg_dir.glob("adg_indexed_*.sqlite"))


def _auto_generate_adg(repo_root: Path) -> bool:
    """
    Invoke ``python tools/generate_full_adg.py`` synchronously to bootstrap the
    ADG SQLite when none exists.  Returns True on success, False on failure.

    Constitutional §3.2: shell=False.  §14: timeout= is mandatory.
    """
    script = repo_root / "tools" / "generate_full_adg.py"
    try:
        result = subprocess.run(
            [sys.executable, str(script)],
            shell=False,
            check=False,
            timeout=300,
            capture_output=True,
            text=True,
            cwd=str(repo_root),
        )
        if result.returncode != 0:
            print(
                f"[pre_mcp_gate] ADG auto-generation failed (exit {result.returncode}): "
                f"{result.stderr.strip()}",
                file=sys.stderr,
            )
            return False
        print("[pre_mcp_gate] ADG auto-generation succeeded.", file=sys.stderr)
        return True
    except subprocess.TimeoutExpired:
        print("[pre_mcp_gate] ADG auto-generation timed out (300 s).", file=sys.stderr)
        return False
    except OSError as exc:
        print(f"[pre_mcp_gate] ADG auto-generation OSError: {exc}", file=sys.stderr)
        return False


def _get_sidecar_diagnostics(db_path: Path) -> dict:
    """
    Gather diagnostic info about WAL/SHM/journal sidecars.
    Used for logging only — NOT for lock decisions.
    """
    diag: dict = {"db": str(db_path)}
    for suffix in ("-wal", "-shm", "-journal"):
        sidecar = db_path.parent / (db_path.name + suffix)
        if sidecar.exists():
            diag[suffix.lstrip("-")] = sidecar.stat().st_size
        else:
            diag[suffix.lstrip("-")] = None
    return diag


def _probe_sqlite_read(db_path: Path) -> tuple[bool, str]:
    """
    Attempt to open the DB and execute a trivial read.
    Returns (ok, reason).  ok=True means reads are fine.
    """
    canonical = str(db_path.resolve())
    try:
        conn = sqlite3.connect(
            f"file:{canonical}?mode=ro",
            uri=True,
            timeout=SQLITE_PROBE_TIMEOUT_MS / 1000.0,
        )
        try:
            conn.execute("SELECT 1")
            return True, "read_ok"
        except sqlite3.OperationalError as exc:
            return False, f"read_failed: {exc}"
        finally:
            conn.close()
    except sqlite3.OperationalError as exc:
        return False, f"open_failed: {exc}"
    except Exception as exc:  # guardian: allow-broad-exception -- probe must not crash the gate
        return False, f"unexpected: {exc}"


def _probe_sqlite_write(db_path: Path) -> tuple[bool, str]:
    """
    Probe for actual write contention using BEGIN IMMEDIATE.
    Returns (ok, reason).  ok=True means no active writer.
    """
    canonical = str(db_path.resolve())
    try:
        conn = sqlite3.connect(
            canonical,
            timeout=SQLITE_PROBE_TIMEOUT_MS / 1000.0,
        )
        try:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute("ROLLBACK")
            return True, "write_ok"
        except sqlite3.OperationalError as exc:
            msg = str(exc).lower()
            if "locked" in msg or "busy" in msg:
                return False, f"SQLITE_BUSY: {exc}"
            return False, f"write_probe_failed: {exc}"
        finally:
            conn.close()
    except sqlite3.OperationalError as exc:
        return False, f"open_failed: {exc}"
    except Exception as exc:  # guardian: allow-broad-exception -- probe must not crash the gate
        return False, f"unexpected: {exc}"


def _check_sqlite_access(repo_root: Path, needs_write: bool) -> tuple[bool, str]:
    """
    Check SQLite accessibility using real connection probes.
    Returns (blocked, reason).  blocked=True means the tool should be denied.

    For read-only tools: allow if DB opens and a trivial read succeeds.
    For write tools: additionally probe BEGIN IMMEDIATE for contention.

    WAL/SHM/journal sidecar existence is logged but NEVER used as the
    lock verdict — these files are normal in WAL mode.
    """
    adg_dir = repo_root / "artifacts" / "adg"
    if not adg_dir.exists():
        return False, "no_artifacts_dir"

    sqlite_files = list(adg_dir.glob("adg_indexed_*.sqlite"))
    if not sqlite_files:
        return False, "no_sqlite_files"

    for db_path in sqlite_files:
        canonical = db_path.resolve()
        diag = _get_sidecar_diagnostics(canonical)

        # Read probe (required for all tools)
        read_ok, read_reason = _probe_sqlite_read(canonical)

        # Determine journal_mode for diagnostics
        journal_mode = "unknown"
        try:
            c = sqlite3.connect(str(canonical), timeout=SQLITE_PROBE_TIMEOUT_MS / 1000.0)
            row = c.execute("PRAGMA journal_mode").fetchone()
            journal_mode = row[0] if row else "unknown"
            c.close()
        except Exception:  # guardian: allow-broad-exception -- diagnostic only, must not crash
            pass

        diag["journal_mode"] = journal_mode
        diag["read_probe"] = read_reason

        if not read_ok:
            diag["decision"] = "BLOCK"
            print(f"[pre_mcp_gate] DIAG: {json.dumps(diag)}", file=sys.stderr)
            return True, f"read probe failed on {canonical.name}: {read_reason}"

        if needs_write:
            write_ok, write_reason = _probe_sqlite_write(canonical)
            diag["write_probe"] = write_reason
            if not write_ok:
                diag["decision"] = "BLOCK"
                print(f"[pre_mcp_gate] DIAG: {json.dumps(diag)}", file=sys.stderr)
                return True, f"write contention on {canonical.name}: {write_reason}"
            diag["decision"] = "ALLOW"
        else:
            diag["write_probe"] = "skipped (read-only tool)"
            diag["decision"] = "ALLOW"

        print(f"[pre_mcp_gate] DIAG: {json.dumps(diag)}", file=sys.stderr)

    return False, "all_probes_passed"


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


def check_filesystem_write_gate(tool_name: str) -> int:
    """
    Block filesystem MCP write tools (write_file, edit_file).

    Windsurf does not expose tool arguments to pre_mcp_tool_use hooks, so
    content-level validation is impossible here. The only safe option is to
    redirect writes to Cascade's native write tools (write_to_file / edit /
    multi_edit) which DO fire pre_write_code and the constitutional gates.
    """
    if tool_name in FILESYSTEM_WRITE_TOOLS:
        return _exit_block(
            f"filesystem MCP tool '{tool_name}' is blocked — "
            "use Cascade's native write_to_file / edit / multi_edit tools instead. "
            "Those tools invoke pre_write_code and the constitutional anti-pattern "
            "and syntax gates that mcp5 bypasses.",
        )
    return 0


def check_adg_gate(repo_root: Path, tool_name: str = "") -> int:
    """Check ADG-specific gates. Return 0 (allow) or 2 (block)."""
    if not _has_adg_sqlite(repo_root):
        print(
            "[pre_mcp_gate] No ADG SQLite file found — triggering auto-generation.",
            file=sys.stderr,
        )
        if not _auto_generate_adg(repo_root):
            return _exit_block(
                "ADG SQLite is missing and auto-generation failed. "
                "Run 'python tools/generate_full_adg.py' manually to bootstrap ADG.",
            )

    needs_write = tool_name in ADG_WRITE_TOOLS
    blocked, reason = _check_sqlite_access(repo_root, needs_write=needs_write)
    if blocked:
        if needs_write:
            return _exit_block(
                f"ADG SQLite write contention detected ({reason}). "
                "An active writer holds the database. Wait or call "
                "mcp1_adg_close_connections first.",
            )
        return _exit_block(
            f"ADG SQLite is inaccessible ({reason}). "
            "The database may be corrupted or locked by another process.",
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

    if not isinstance(payload, dict):
        print("[pre_mcp_gate] WARNING: non-dict payload — allowing (non-ADG assumed).", file=sys.stderr)
        return 0

    tool_info = payload.get("tool_info", payload)
    if not isinstance(tool_info, dict):
        return 0

    server_name = tool_info.get("mcp_server_name", "")
    tool_name = tool_info.get("mcp_tool_name", "")

    if server_name == FILESYSTEM_SERVER_NAME:
        return check_filesystem_write_gate(tool_name)

    if server_name != ADG_SERVER_NAME:
        return 0
    if tool_name in ADG_RECOVERY_TOOLS:
        # Always allow recovery probes — blocking them creates a dead loop
        # where the gate blocks the only tools that can restore health.
        return 0

    return check_adg_gate(REPO_ROOT, tool_name)


if __name__ == "__main__":
    sys.exit(main())
