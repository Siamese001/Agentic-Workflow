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
      * Snapshot age is advisory only — ADG is valid until user manually refreshes it
  - Vector DB MCP: chromadb library probe (hard block) + HTTP instance probe (advisory)
  - OpenTelemetry MCP: SDK library probe (hard block) + OTLP collector probe (advisory)
  - Redis MCP: TCP PING connectivity check (hard block)
  - Memory MCP: SQLite knowledge_graph.sqlite accessibility check (hard block)
  - Task Manager MCP: Node.js availability check (hard block)
  - Pytest MCP: pytest import + pytest.ini check (hard block)
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

# Additional MCP servers requiring health gates
# These names MUST match the keys in .windsurf/mcp_config.json exactly.
PYTEST_SERVER_NAME = "pytest_mcp"
REDIS_SERVER_NAME = "redis"  # mcp_config.json key is "redis", not "redis_mcp"
MEMORY_SERVER_NAME = "memory"
TASK_MANAGER_SERVER_NAME = "task_manager"
VECTOR_DB_SERVER_NAME = "vector_db"
OTEL_MCP_SERVER_NAME = "otel_mcp"
DEEPWIKI_SERVER_NAME = "deepwiki"

# Recovery tools that MUST pass even when MCP is unhealthy.
# Without this whitelist, the gate blocks the very tools needed to recover.
ADG_RECOVERY_TOOLS = {
    "adg_health",  # mcp1_adg_health — liveness probe
    "adg_status",  # mcp1_adg_status — snapshot status
    "adg_close_connections",  # needed to release SQLite locks
    "adg_reopen_connections",  # needed after lock release
}

PYTEST_RECOVERY_TOOLS = {
    "list_pytest_config",  # mcp12_list_pytest_config — health probe
    "discover_tests",  # mcp12_discover_tests — basic discovery
}

REDIS_RECOVERY_TOOLS = {
    "redis_health",  # mcp11_redis_health — liveness probe
}

MEMORY_RECOVERY_TOOLS = {
    "mem_recall_session_start",  # mcp6_mem_recall_session_start — session context
    "mem_get_stats",  # mcp6_mem_get_stats — health metrics
    "search_nodes",  # mcp6_search_nodes — lightweight query probe
}

TASK_MANAGER_RECOVERY_TOOLS = {
    # Real tool names from @blizzy/mcp-task-manager — verified against MCP registry
    "task_info",  # lightweight read — used as health probe
    "create_task",  # first call in any T2/T3 session — must always be allowed
}

VECTOR_DB_RECOVERY_TOOLS = {
    "vector_stats",  # mcp10_vector_stats — health probe
    "list_collections",  # mcp10_list_collections — lightweight check
}

OTEL_MCP_RECOVERY_TOOLS = {
    "otel_status",  # liveness probe — must bypass gate to diagnose otel_mcp itself
}

# Write-affecting ADG tools that mutate DB state.
# These require a BEGIN IMMEDIATE probe to detect real write contention.
ADG_WRITE_TOOLS = {
    "adg_rebuild",
    "adg_checkpoint",
    "adg_compact",
}

SQLITE_PROBE_TIMEOUT_MS = 500  # busy_timeout for probe connections

# Module-level cache: subprocess probes are run once per process lifetime.
# Gate checks (pytest, node, chromadb, otel) are expensive if re-run on every
# tool call — cache the result for the lifetime of the hook process.
_PROBE_CACHE: dict[str, bool] = {}

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
    if age is not None and age > 3600:
        minutes = int(age // 60)
        print(
            f"[pre_mcp_gate] INFO: ADG snapshot is {minutes} min old — "
            "refresh when convenient: python tools/generate_full_adg.py",
            file=sys.stderr,
        )

    return 0


def check_pytest_gate(repo_root: Path) -> int:
    """
    Check Pytest MCP health by verifying pytest is importable.
    Result is cached per process — subprocess only runs once.
    Return 0 (allow) or 2 (block).
    """
    cache_key = "pytest_importable"
    if cache_key not in _PROBE_CACHE:
        try:
            result = subprocess.run(
                [sys.executable, "-c", "import pytest"],
                shell=False,
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            _PROBE_CACHE[cache_key] = result.returncode == 0
        except (subprocess.TimeoutExpired, OSError):
            _PROBE_CACHE[cache_key] = False

    if not _PROBE_CACHE[cache_key]:
        return _exit_block(
            "Pytest MCP health check failed: pytest not installed or importable. "
            "Install with: pip install pytest",
        )

    pytest_ini = repo_root / "pytest.ini"
    pyproject_toml = repo_root / "pyproject.toml"
    if not pytest_ini.exists() and not pyproject_toml.exists():
        print(
            "[pre_mcp_gate] WARNING: No pytest.ini or pyproject.toml found — "
            "pytest configuration may be incomplete.",
            file=sys.stderr,
        )
    return 0


def check_redis_gate() -> int:
    """
    Check Redis MCP health by attempting a connection to Redis.
    Return 0 (allow) or 2 (block).
    """
    import os

    host = os.getenv("REDIS_HOST", "localhost")
    port = int(os.getenv("REDIS_PORT", "6379"))
    db = int(os.getenv("REDIS_DB", "0"))
    timeout = int(os.getenv("REDIS_TIMEOUT", "5"))

    try:
        import redis as redis_lib
    except ImportError:
        return _exit_block(
            "Redis MCP health check failed: redis package not installed. Install with: pip install redis",
        )

    try:
        client = redis_lib.Redis(
            host=host,
            port=port,
            db=db,
            socket_timeout=timeout,
            socket_connect_timeout=timeout,
        )
        if not client.ping():
            return _exit_block(
                f"Redis MCP health check failed: Redis at {host}:{port} not responding to PING.",
            )
    except redis_lib.ConnectionError as exc:
        return _exit_block(
            f"Redis MCP health check failed: Cannot connect to Redis at {host}:{port}. Error: {exc}",
        )
    except Exception as exc:  # guardian: allow-broad-exception -- probe must not crash the gate
        return _exit_block(f"Redis MCP health check unexpected error: {exc}")

    return 0


def check_memory_gate(repo_root: Path) -> int:
    """
    Check Memory MCP health by verifying SQLite DB is accessible.
    Return 0 (allow) or 2 (block).
    """
    memory_db = repo_root / "artifacts" / "memory" / "knowledge_graph.sqlite"

    # Check if DB file exists (it's created on first use, so non-existence is OK)
    if not memory_db.exists():
        # Directory should exist
        memory_dir = memory_db.parent
        if not memory_dir.exists():
            try:
                memory_dir.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                return _exit_block(
                    f"Memory MCP health check failed: Cannot create memory directory: {exc}",
                )
        return 0  # DB will be created on first use — this is normal

    # Probe that DB is readable
    try:
        conn = sqlite3.connect(
            str(memory_db),
            timeout=SQLITE_PROBE_TIMEOUT_MS / 1000.0,
        )
        try:
            conn.execute("SELECT 1")
        finally:
            conn.close()
    except sqlite3.OperationalError as exc:
        return _exit_block(
            f"Memory MCP health check failed: SQLite DB inaccessible: {exc}",
        )
    except Exception as exc:  # guardian: allow-broad-exception -- probe must not crash the gate
        return _exit_block(f"Memory MCP health check unexpected error: {exc}")

    return 0


def check_task_manager_gate() -> int:
    """
    Check Task Manager MCP health.
    Task Manager is npx-based (@blizzy/mcp-task-manager); verify Node.js is in PATH.
    Result is cached per process — subprocess only runs once.
    Return 0 (allow) or 2 (block).
    """
    cache_key = "node_available"
    if cache_key not in _PROBE_CACHE:
        try:
            result = subprocess.run(
                ["node", "--version"],
                shell=False,
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            _PROBE_CACHE[cache_key] = result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            _PROBE_CACHE[cache_key] = False

    if not _PROBE_CACHE[cache_key]:
        return _exit_block(
            "Task Manager MCP health check failed: Node.js not found in PATH. "
            "Task Manager requires Node.js (npx @blizzy/mcp-task-manager).",
        )
    return 0


def check_vector_db_gate() -> int:
    """
    Check Vector DB MCP (ChromaDB) health.

    Two-stage probe (library probe cached per process):
    1. Verify chromadb package is importable — hard block if missing
    2. Probe ChromaDB HTTP instance at CHROMA_HOST:CHROMA_PORT — fail-open
       (embedded mode has no HTTP endpoint; server mode does)

    Return 0 (allow) or 2 (block).
    """
    import os
    import socket as _socket

    # Stage 1: library importable? (cached)
    cache_key = "chromadb_importable"
    if cache_key not in _PROBE_CACHE:
        try:
            result = subprocess.run(
                [sys.executable, "-c", "import chromadb"],
                shell=False,
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            _PROBE_CACHE[cache_key] = result.returncode == 0
        except (subprocess.TimeoutExpired, OSError):
            _PROBE_CACHE[cache_key] = False

    if not _PROBE_CACHE[cache_key]:
        return _exit_block(
            "Vector DB MCP health check failed: chromadb not installed. Install with: pip install chromadb",
        )

    # Stage 2: HTTP instance probe — fail-open (embedded mode is valid)
    host = os.getenv("CHROMA_HOST", "localhost")
    port = int(os.getenv("CHROMA_PORT", "8000"))
    try:
        with _socket.create_connection((host, port), timeout=2):
            pass
    except ConnectionRefusedError:
        print(
            f"[pre_mcp_gate] INFO: ChromaDB HTTP instance not detected at {host}:{port} — "
            "using embedded mode. For server mode: chroma run --path ./artifacts/chroma",
            file=sys.stderr,
        )
    except OSError:
        pass  # network unavailable — fail-open

    return 0


def check_otel_gate() -> int:
    """
    Check OpenTelemetry MCP health.

    Two-stage probe (library probe cached per process):
    1. Verify opentelemetry SDK is importable — hard block if missing
    2. Probe OTLP/HTTP collector endpoint — fail-open (otel_mcp reads from
       runtime_adg SQLite even without a live collector)

    OTEL_EXPORTER_OTLP_ENDPOINT is a full URL (e.g. http://localhost:4318) —
    hostname is extracted before TCP probe.

    Return 0 (allow) or 2 (block).
    """
    import os
    import socket as _socket

    # Stage 1: SDK importable? (cached)
    cache_key = "otel_importable"
    if cache_key not in _PROBE_CACHE:
        try:
            result = subprocess.run(
                [sys.executable, "-c", "from opentelemetry import trace"],
                shell=False,
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            _PROBE_CACHE[cache_key] = result.returncode == 0
        except (subprocess.TimeoutExpired, OSError):
            _PROBE_CACHE[cache_key] = False

    if not _PROBE_CACHE[cache_key]:
        return _exit_block(
            "OpenTelemetry MCP health check failed: opentelemetry SDK not installed. "
            "Install with: pip install opentelemetry-api opentelemetry-sdk",
        )

    # Stage 2: OTLP/HTTP collector probe — fail-open
    # OTEL_EXPORTER_OTLP_ENDPOINT is a full URL; extract hostname only
    raw_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")
    port = int(os.getenv("OTEL_COLLECTOR_PORT", "4318"))
    # Strip scheme (http:// or https://) and path to get just the host
    host = raw_endpoint.split("//")[-1].split("/")[0].split(":")[0] or "localhost"
    try:
        with _socket.create_connection((host, port), timeout=2):
            pass
    except ConnectionRefusedError:
        print(
            f"[pre_mcp_gate] INFO: OTLP/HTTP collector not detected at {host}:{port} — "
            "otel_mcp will read from runtime_adg SQLite only. "
            "For live tracing: start OpenTelemetry Collector.",
            file=sys.stderr,
        )
    except OSError:
        pass  # network unavailable — fail-open

    return 0


def check_deepwiki_gate() -> int:
    """
    Check DeepWiki MCP health (remote URL MCP).

    DeepWiki is accessed via HTTPS to mcp.deepwiki.com — advisory connectivity
    check only (fail-open). Cannot hard-block since DNS/firewall is user-env
    dependent, but warn so Cascade knows remote queries will fail.

    Return 0 always (fail-open — remote availability is not Cascade's fault).
    """
    import socket as _socket

    cache_key = "deepwiki_reachable"
    if cache_key not in _PROBE_CACHE:
        try:
            with _socket.create_connection(("mcp.deepwiki.com", 443), timeout=3):
                _PROBE_CACHE[cache_key] = True
        except OSError:
            _PROBE_CACHE[cache_key] = False

    if not _PROBE_CACHE[cache_key]:
        print(
            "[pre_mcp_gate] WARNING: mcp.deepwiki.com not reachable — "
            "DeepWiki queries will fail. Check network/firewall.",
            file=sys.stderr,
        )
    return 0  # always fail-open — remote availability is not Cascade's fault


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

    # Filesystem MCP: block write tools (must go through pre_write_code)
    if server_name == FILESYSTEM_SERVER_NAME:
        return check_filesystem_write_gate(tool_name)

    # ADG SQLite MCP: health, lock, and staleness checks
    if server_name == ADG_SERVER_NAME:
        if tool_name in ADG_RECOVERY_TOOLS:
            # Always allow recovery probes — blocking them creates a dead loop
            return 0
        return check_adg_gate(REPO_ROOT, tool_name)

    # Pytest MCP: verify pytest is available
    if server_name == PYTEST_SERVER_NAME:
        if tool_name in PYTEST_RECOVERY_TOOLS:
            return 0
        return check_pytest_gate(REPO_ROOT)

    # Redis MCP: verify Redis connectivity
    if server_name == REDIS_SERVER_NAME:
        if tool_name in REDIS_RECOVERY_TOOLS:
            return 0
        return check_redis_gate()

    # Memory MCP: verify SQLite DB is accessible
    if server_name == MEMORY_SERVER_NAME:
        if tool_name in MEMORY_RECOVERY_TOOLS:
            return 0
        return check_memory_gate(REPO_ROOT)

    # Task Manager MCP: verify Node.js is available
    if server_name == TASK_MANAGER_SERVER_NAME:
        if tool_name in TASK_MANAGER_RECOVERY_TOOLS:
            return 0
        return check_task_manager_gate()

    # Vector DB MCP: verify ChromaDB is available
    if server_name == VECTOR_DB_SERVER_NAME:
        if tool_name in VECTOR_DB_RECOVERY_TOOLS:
            return 0
        return check_vector_db_gate()

    # OpenTelemetry MCP: verify opentelemetry SDK is available
    if server_name == OTEL_MCP_SERVER_NAME:
        if tool_name in OTEL_MCP_RECOVERY_TOOLS:
            return 0
        return check_otel_gate()

    # DeepWiki MCP: remote URL — advisory connectivity check only
    if server_name == DEEPWIKI_SERVER_NAME:
        return check_deepwiki_gate()

    # All other MCPs (GitKraken, enhanced_http): fail-open
    return 0


if __name__ == "__main__":
    sys.exit(main())
