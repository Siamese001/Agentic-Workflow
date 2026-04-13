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
import os
import sqlite3
import subprocess
import sys
import time
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
GITKRAKEN_SERVER_NAME = "GitKraken"
NOTION_SERVER_NAME = "notion"

# Recovery tools that MUST pass even when MCP is unhealthy.
# Without this whitelist, the gate blocks the very tools needed to recover.
ADG_RECOVERY_TOOLS = {
    "adg_health",  # mcp1_adg_health — liveness probe
    "adg_status",  # mcp1_adg_status — snapshot status
    "adg_close_connections",  # needed to release SQLite locks
    "adg_reopen_connections",  # needed after lock release
}

PYTEST_RECOVERY_TOOLS = {
    "list_pytest_config",  # mcp8_list_pytest_config — health probe
    "discover_tests",  # mcp8_discover_tests — basic discovery
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
    "update_task",  # lifecycle transitions (in_progress, done) — must not be blocked by probe failure
    "decompose_task",  # T3 decomposition gate — must not be blocked by probe failure
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
# move_file included: rename/relocate operations mutate the filesystem and
# bypass pre_write_code just as write_file and edit_file do.
FILESYSTEM_WRITE_TOOLS = {
    "write_file",  # mcp5_write_file — full overwrite
    "edit_file",  # mcp5_edit_file  — line-based edits
    "move_file",  # mcp4_move_file  — rename/relocate; mutates filesystem
}

REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS_ADG = REPO_ROOT / "artifacts" / "adg"
# Session-state isolation boundary
#
# Current isolation unit: one IDE window / one VS Code process.
# We derive _SESSION_ID from VSCODE_PID when present, with os.getppid()
# as the fallback for pytest / CLI contexts.
#
# This solves:
# - multiple Windsurf / VS Code windows clobbering each other
# - parallel pytest workers sharing one session_state file
#
# This does NOT solve:
# - per-chat / per-tab isolation inside the same IDE window
#
# Per-chat isolation requires Windsurf to expose a conversation-scoped
# identifier, for example WINDSURF_CHAT_ID. If such an ID becomes available,
# replace VSCODE_PID in the _SESSION_ID derivation and keep the rest of the
# session-state mechanism unchanged.
_SESSION_ID = os.environ.get("VSCODE_PID") or str(os.getppid())
SESSION_STATE = REPO_ROOT / "artifacts" / "windsurf" / f"session_state_{_SESSION_ID}.json"

# After this many consecutive blocks without a successful memory recall,
# the gate degrades to open so Cascade is never permanently stuck.
MAX_MEMORY_BLOCK_ATTEMPTS = 3

# Stale session-state files older than this are removed on each gate startup.
_SESSION_STATE_MAX_AGE_HOURS = 24

# Launcher script path — validated by check_filesystem_startup_gate() on first use.
# The launcher resolves node + npm global prefix dynamically; no version-pinned paths.
_FS_LAUNCHER = REPO_ROOT / ".windsurf" / "scripts" / "filesystem_mcp_launcher.js"
_FS_ALLOWED_DIR = Path(r"C:/Git/Agentic-Workflow")

# ---------------------------------------------------------------------------
# GitKraken MCP hardening constants
# ---------------------------------------------------------------------------

# Canonical workspace root — GitKraken tool `directory` args must resolve
# to this path or a subdirectory of it. Blocks cross-repo accidental mutation.
GITKRAKEN_WORKSPACE_ROOT = REPO_ROOT

# Tools that mutate LOCAL git state (stage, commit, checkout, stash, worktree add, branch create)
GITKRAKEN_LOCAL_WRITE_TOOLS: set[str] = {
    "git_add_or_commit",
    "git_checkout",
    "git_stash",
    "git_worktree",  # add action is a write; list action is safe
    "git_branch",  # create action is a write; list action is safe
    "gitlens_commit_composer",
    "gitlens_start_work",
}

# Tools that mutate REMOTE state (push, PR creation, issue comments)
GITKRAKEN_REMOTE_WRITE_TOOLS: set[str] = {
    "git_push",
    "pull_request_create",
    "pull_request_create_review",
    "issues_add_comment",
    "gitlens_start_review",
}

# All write-capable tools (local + remote)
GITKRAKEN_ALL_WRITE_TOOLS: set[str] = GITKRAKEN_LOCAL_WRITE_TOOLS | GITKRAKEN_REMOTE_WRITE_TOOLS

# These remote-write tools additionally require upstream tracking validation
GITKRAKEN_PUSH_TOOLS: set[str] = {"git_push", "pull_request_create"}


def _exit_block(reason: str) -> int:
    print(f"[pre_mcp_gate] BLOCKED: {reason}", file=sys.stderr)
    return 2


def _read_session_state() -> dict:
    """Read session_state.json and return its contents. Return {} on any error (fail-open)."""
    try:
        if SESSION_STATE.exists():
            data = json.loads(SESSION_STATE.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        pass
    return {}


def _increment_memory_block_attempts() -> int:
    """
    Increment max_memory_block_attempts in session state and return the new count.
    Fail-open: returns MAX_MEMORY_BLOCK_ATTEMPTS on any I/O error so the gate
    immediately degrades rather than looping.
    """
    try:
        state = _read_session_state()
        count = int(state.get("max_memory_block_attempts", 0)) + 1
        state["max_memory_block_attempts"] = count
        SESSION_STATE.parent.mkdir(parents=True, exist_ok=True)
        SESSION_STATE.write_text(json.dumps(state), encoding="utf-8")
        return count
    except (OSError, json.JSONDecodeError):
        return MAX_MEMORY_BLOCK_ATTEMPTS  # fail-open: treat counter as exhausted


def check_memory_first_gate(server_name: str, tool_name: str) -> int:
    """
    Hard gate: block non-memory MCP tool calls until mem_recall_session_start
    has been called this session.

    Rules (checked in order):
    1. memory server calls always pass — never deadlock recall itself.
    2. memory_recalled=True in session state → gate satisfied, allow.
    3. Memory MCP unhealthy → degrade-open to avoid full-system blockage.
    4. max_memory_block_attempts >= MAX_MEMORY_BLOCK_ATTEMPTS → degrade-open.
    5. Otherwise: increment attempt counter and block with redirect message.

    Return 0 (allow) or 2 (block).
    """
    # Rule 1: never block the memory server itself
    if server_name == MEMORY_SERVER_NAME:
        return 0

    state = _read_session_state()

    # Rule 2: memory already recalled this session — gate satisfied.
    # Also check the plain session_state.json written by pre_prompt_classifier +
    # post_mcp_audit, because PPID instability gives each hook spawn a fresh
    # PID-namespaced file that never carries memory_recalled from the audit path.
    if state.get("memory_recalled", False):
        return 0
    _plain = REPO_ROOT / "artifacts" / "windsurf" / "session_state.json"
    try:
        if _plain.exists():
            _ps = json.loads(_plain.read_text(encoding="utf-8"))
            if isinstance(_ps, dict) and _ps.get("memory_recalled", False):
                return 0
    except (OSError, json.JSONDecodeError):
        pass

    # Rule 3: degrade-open if memory MCP is unhealthy (SQLite inaccessible)
    if check_memory_gate(REPO_ROOT) != 0:
        print(
            "[pre_mcp_gate] memory-first gate: memory MCP unhealthy — degrading to open.",
            file=sys.stderr,
        )
        return 0

    # Rule 4: degrade-open after too many consecutive blocks (prevent infinite loop)
    current_attempts = state.get("max_memory_block_attempts", 0)
    if current_attempts >= MAX_MEMORY_BLOCK_ATTEMPTS:
        print(
            f"[pre_mcp_gate] memory-first gate: max_memory_block_attempts={current_attempts} "
            f">= {MAX_MEMORY_BLOCK_ATTEMPTS} — degrading to open.",
            file=sys.stderr,
        )
        return 0

    # Rule 5: block and redirect
    attempts = _increment_memory_block_attempts()
    return _exit_block(
        f"memory-first gate: call mem_recall_session_start (memory MCP) before any other "
        f"MCP tool [attempt {attempts}/{MAX_MEMORY_BLOCK_ATTEMPTS}]. "
        "Server: memory | Tool: mem_recall_session_start | Parameters: none."
    )


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

    sqlite_files = sorted(adg_dir.glob("adg_indexed_*.sqlite"))
    if not sqlite_files:
        return False, "no_sqlite_files"

    # Probe only the latest snapshot — older files may be locked/corrupt from prior runs
    # and must not block access to the active snapshot.
    canonical = sqlite_files[-1].resolve()
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
    diag["snapshot"] = canonical.name

    if not read_ok:
        diag["decision"] = "BLOCK"
        print(f"[pre_mcp_gate] DIAG: {json.dumps(diag)}", file=sys.stderr)
        return True, f"read probe failed on latest snapshot {canonical.name}: {read_reason}"

    if needs_write:
        write_ok, write_reason = _probe_sqlite_write(canonical)
        diag["write_probe"] = write_reason
        if not write_ok:
            diag["decision"] = "BLOCK"
            print(f"[pre_mcp_gate] DIAG: {json.dumps(diag)}", file=sys.stderr)
            return True, f"write contention on latest snapshot {canonical.name}: {write_reason}"
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


def check_filesystem_startup_gate() -> int:
    """
    Verify the filesystem MCP can actually start:
      1. 'node' is resolvable in PATH (checked via subprocess).
      2. The repo-local launcher script exists.
      3. The allowed directory exists.

    Cached per process — probes run once per gate process.
    Returns 0 (allow) or 2 (block with actionable message).
    """
    cache_key = "filesystem_startup_ok"
    if cache_key not in _PROBE_CACHE:
        # Probe 1: node in PATH
        node_ok = False
        try:
            result = subprocess.run(
                ["node", "--version"],
                capture_output=True,
                timeout=5,
                check=False,
            )
            node_ok = result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            node_ok = False

        # Probe 2: launcher script exists in repo
        launcher_ok = _FS_LAUNCHER.exists()

        # Probe 3: allowed directory exists
        allowed_ok = _FS_ALLOWED_DIR.exists()

        _PROBE_CACHE[cache_key] = node_ok and launcher_ok and allowed_ok

        if not node_ok:
            print(
                "[pre_mcp_gate] Filesystem MCP startup check FAILED: "
                "'node' not found in PATH. "
                "Ensure Node.js is installed and fnm has activated the correct version. "
                "Operator note: docs/guides/filesystem_mcp_operations.md",
                file=sys.stderr,
            )
        if not launcher_ok:
            print(
                f"[pre_mcp_gate] Filesystem MCP startup check FAILED: "
                f"launcher not found at {_FS_LAUNCHER}. "
                "Ensure the repo is intact (git status). "
                "Operator note: docs/guides/filesystem_mcp_operations.md",
                file=sys.stderr,
            )
        if not allowed_ok:
            print(
                f"[pre_mcp_gate] Filesystem MCP startup check FAILED: "
                f"allowed directory not found: {_FS_ALLOWED_DIR}.",
                file=sys.stderr,
            )

    if not _PROBE_CACHE["filesystem_startup_ok"]:
        return _exit_block(
            "Filesystem MCP cannot start — node, launcher, or allowed directory check failed. "
            "See stderr above for which check failed. "
            "Operator note: docs/guides/filesystem_mcp_operations.md"
        )
    return 0


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
    print("[pre_mcp_gate] PYTEST_MCP_TRACE: entered check_pytest_gate", file=sys.stderr)
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
        print(
            "[pre_mcp_gate] PYTEST_MCP_TRACE: REJECT reason=pytest_not_importable",
            file=sys.stderr,
        )
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
    print(
        "[pre_mcp_gate] PYTEST_MCP_TRACE: ALLOW reason=pytest_importable "
        f"pytest_ini={pytest_ini.exists()} pyproject_toml={pyproject_toml.exists()}",
        file=sys.stderr,
    )
    return 0


def check_redis_gate(repo_root: Path) -> int:
    """
    Check Redis MCP health with ADG SQLite fallback.

    Constitutional §13 MCP Green Light:
    1. Check Redis hot cache first (fast path ~75ms)
    2. If Redis cold/down, fallback to ADG SQLite (canonical source)
    3. Only block if BOTH Redis AND SQLite are unavailable

    Return 0 (allow) or 2 (block).
    """
    host = os.getenv("REDIS_HOST", "localhost")
    port = int(os.getenv("REDIS_PORT", "6379"))
    db = int(os.getenv("REDIS_DB", "0"))
    timeout = int(os.getenv("REDIS_TIMEOUT", "5"))

    redis_ok = False
    redis_error = ""

    try:
        import redis as redis_lib

        client = redis_lib.Redis(
            host=host,
            port=port,
            db=db,
            socket_connect_timeout=timeout,
            socket_timeout=timeout,
            decode_responses=True,
        )
        if client.ping():
            redis_ok = True
        else:
            redis_error = f"Redis at {host}:{port} not responding to PING"
    except ImportError:
        redis_error = "redis package not installed"
    except redis_lib.ConnectionError as exc:
        redis_error = f"Cannot connect to Redis at {host}:{port}: {exc}"
    except Exception as exc:  # guardian: allow-broad-exception -- probe must not crash the gate
        redis_error = f"Unexpected error: {exc}"

    if redis_ok:
        return 0  # Redis hot — fast path success

    # Redis cold/down → Fallback to ADG SQLite (Constitutional §13)
    print(
        f"[pre_mcp_gate] Redis unavailable ({redis_error}) — falling back to ADG SQLite (canonical source)",
        file=sys.stderr,
    )

    if not _has_adg_sqlite(repo_root):
        print(
            "[pre_mcp_gate] ADG SQLite not found — attempting auto-generation",
            file=sys.stderr,
        )
        if not _auto_generate_adg(repo_root):
            return _exit_block(
                f"Redis unavailable ({redis_error}) AND ADG SQLite missing "
                "(auto-generation failed). Run 'python tools/generate_full_adg.py' manually.",
            )

    # Check SQLite accessibility (read-only probe)
    blocked, reason = _check_sqlite_access(repo_root, needs_write=False)
    if blocked:
        return _exit_block(
            f"Redis unavailable ({redis_error}) AND ADG SQLite inaccessible ({reason}). "
            "Both ADG backends are down — cannot proceed safely.",
        )

    print(
        "[pre_mcp_gate] ADG SQLite accessible — proceeding with degraded performance "
        "(Redis cache unavailable, using canonical SQLite)",
        file=sys.stderr,
    )
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


def _run_git(args: list[str], cwd: Path, timeout: int = 10) -> tuple[int, str, str]:
    """
    Run a git subprocess safely. Returns (returncode, stdout, stderr).
    Constitutional §14: timeout= required. §0: shell=False.
    """
    try:
        result = subprocess.run(
            ["git"] + args,
            shell=False,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(cwd),
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return 1, "", f"git {' '.join(args)} timed out after {timeout}s"
    except (OSError, FileNotFoundError) as exc:
        return 1, "", f"git executable error: {exc}"


def _resolve_gitkraken_repo(payload: dict) -> Path:  # pylint: disable=unused-argument
    """
    Resolve the target repository from the GitKraken tool payload.

    GitKraken tools pass the repo root as a `directory` field in tool arguments.
    Windsurf's pre_mcp_tool_use hook does NOT expose tool arguments, so we
    cannot read the `directory` value directly. We resolve the workspace root
    from GITKRAKEN_WORKSPACE_ROOT (= REPO_ROOT from mcp_config.json cwd binding).

    Returns the canonical workspace root Path.
    """
    # Tool arguments are not available in pre_mcp_tool_use hooks. Fall back to
    # the workspace root anchored by the cwd setting in mcp_config.json.
    return GITKRAKEN_WORKSPACE_ROOT.resolve()


def _check_gitkraken_repo_confinement(repo: Path) -> tuple[bool, str]:
    """
    Verify `repo` is a git repository and is confined to the workspace root.
    Returns (blocked, reason). blocked=True → deny.
    """
    workspace = GITKRAKEN_WORKSPACE_ROOT.resolve()

    # Ensure repo resolves within the workspace (prevents cross-repo drift)
    try:
        repo.relative_to(workspace)
    except ValueError:
        return True, (
            f"GitKraken target repo '{repo}' is outside workspace root '{workspace}'. "
            "Cross-repo mutations are blocked."
        )

    # Confirm it is an actual git repo
    rc, _, _ = _run_git(["rev-parse", "--git-dir"], repo)
    if rc != 0:
        return True, (
            f"GitKraken target '{repo}' is not a git repository. "
            "Ensure cwd is set correctly in mcp_config.json."
        )

    return False, "repo_confined"


def _check_gitkraken_detached_head(repo: Path) -> tuple[bool, str]:
    """
    Return (is_detached, description). is_detached=True means HEAD is not on a branch.
    """
    rc, stdout, _ = _run_git(["symbolic-ref", "--quiet", "HEAD"], repo)
    if rc != 0:
        return True, "HEAD is detached — not on any branch"
    branch = stdout.removeprefix("refs/heads/")
    return False, f"on branch '{branch}'"


def _check_gitkraken_dirty_tree(repo: Path) -> tuple[bool, str]:
    """
    Return (is_dirty, description).
    Uses `git status --porcelain` — non-empty output = dirty tree.
    """
    rc, stdout, _ = _run_git(["status", "--porcelain"], repo)
    if rc != 0:
        return False, "status probe failed — treating as clean"
    if stdout:
        lines = stdout.splitlines()
        return True, f"working tree has {len(lines)} uncommitted change(s)"
    return False, "working tree clean"


def _check_gitkraken_missing_upstream(repo: Path) -> tuple[bool, str]:
    """
    Return (missing, description). missing=True when current branch has no remote tracking.
    """
    rc, stdout, _ = _run_git(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"], repo)
    if rc != 0:
        return True, "current branch has no upstream tracking branch"
    return False, f"upstream is '{stdout}'"


def check_gitkraken_gate(tool_name: str, payload: dict) -> int:
    """
    GitKraken MCP preflight gate.

    P0-2: Convert GitKraken from fail-open to fail-closed for write tools.
    P0-3: Dirty-tree, detached-HEAD, and missing-upstream checks.
    P0-4: Repo confinement — block operations outside workspace root.

    Read-only tools always pass (exit 0).
    Write tools require repo confinement + specific safety checks per risk level.

    Return 0 (allow) or 2 (block).
    """
    repo = _resolve_gitkraken_repo(payload)

    # Read-only tools: only require repo confinement check
    if tool_name not in GITKRAKEN_ALL_WRITE_TOOLS:
        # For read tools, repo confinement is advisory (fail-open) to avoid
        # blocking legitimate cross-repo reads (e.g. issues_get_detail targets GitHub)
        return 0

    # All write tools: require repo confinement
    blocked, reason = _check_gitkraken_repo_confinement(repo)
    if blocked:
        return _exit_block(f"GitKraken repo confinement: {reason}")

    # --- Detached HEAD check (blocks checkout, commit, push) ---
    if tool_name in {
        "git_checkout",
        "git_add_or_commit",
        "git_push",
        "pull_request_create",
        "gitlens_commit_composer",
    }:
        detached, head_desc = _check_gitkraken_detached_head(repo)
        if detached:
            return _exit_block(
                f"GitKraken '{tool_name}' blocked: {head_desc}. "
                "Checkout a branch before performing this operation."
            )
        print(
            f"[pre_mcp_gate] GitKraken HEAD check: {head_desc}",
            file=sys.stderr,
        )

    # --- Dirty-tree check (blocks checkout — prevents silent file clobber) ---
    if tool_name == "git_checkout":
        dirty, tree_desc = _check_gitkraken_dirty_tree(repo)
        if dirty:
            return _exit_block(
                f"GitKraken 'git_checkout' blocked: {tree_desc}. "
                "Stash or commit changes before switching branches."
            )

    # --- Missing-upstream check (blocks push and PR creation) ---
    if tool_name in GITKRAKEN_PUSH_TOOLS:
        missing, upstream_desc = _check_gitkraken_missing_upstream(repo)
        if missing:
            return _exit_block(
                f"GitKraken '{tool_name}' blocked: {upstream_desc}. "
                "Set a remote tracking branch before pushing "
                "(git push --set-upstream origin <branch>)."
            )
        print(
            f"[pre_mcp_gate] GitKraken upstream check: {upstream_desc}",
            file=sys.stderr,
        )

    # All checks passed — log for audit trail (P0-5 complement at gate layer)
    print(
        f"[pre_mcp_gate] GitKraken ALLOW: tool='{tool_name}' repo='{repo}'",
        file=sys.stderr,
    )
    return 0


def check_notion_gate() -> int:
    """
    Check Notion MCP auth gate.

    The notion MCP subprocess (@notionhq/notion-mcp-server) inherits NOTION_TOKEN
    from the OS environment.  An empty or absent token causes the server to start
    normally (green) but every API call returns HTTP 401 — a silent failure.
    This gate makes the failure loud and actionable before any tool call fires.

    Return 0 (allow) or 2 (block with actionable message).
    """
    token = os.environ.get("NOTION_TOKEN", "").strip()
    if not token:
        return _exit_block(
            "Notion MCP auth gate failed: NOTION_TOKEN is not set or is empty. "
            "Create an Internal integration token at https://www.notion.so/my-integrations "
            "and register it as a Windows environment variable: "
            "  setx NOTION_TOKEN secret_...  (then restart Windsurf). "
            "See .env for the expected format (NOTION_TOKEN=secret_... or ntn_...)."
        )
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


def _purge_stale_session_states() -> None:
    """Delete session_state_{pid}.json files older than _SESSION_STATE_MAX_AGE_HOURS."""
    windsurf_dir = REPO_ROOT / "artifacts" / "windsurf"
    if not windsurf_dir.exists():
        return
    cutoff = time.time() - _SESSION_STATE_MAX_AGE_HOURS * 3600
    for f in windsurf_dir.glob("session_state_*.json"):
        try:
            if f.stat().st_mtime < cutoff:
                f.unlink(missing_ok=True)
        except OSError:
            pass  # best-effort cleanup — never block the gate


def main() -> int:
    _purge_stale_session_states()
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

    # Memory-first gate: blocks non-memory tools until mem_recall_session_start is called.
    # Degrades to open if memory MCP is unhealthy or attempt limit is reached.
    rc = check_memory_first_gate(server_name, tool_name)
    if rc != 0:
        return rc

    # Filesystem MCP: startup health check then write-tool block
    if server_name == FILESYSTEM_SERVER_NAME:
        rc = check_filesystem_startup_gate()
        if rc != 0:
            return rc
        return check_filesystem_write_gate(tool_name)

    # ADG SQLite MCP: health, lock, and staleness checks
    if server_name == ADG_SERVER_NAME:
        if tool_name in ADG_RECOVERY_TOOLS:
            # Always allow recovery probes — blocking them creates a dead loop
            return 0
        return check_adg_gate(REPO_ROOT, tool_name)

    # Pytest MCP: verify pytest is available
    if server_name == PYTEST_SERVER_NAME:
        print(
            f"[pre_mcp_gate] PYTEST_MCP_TRACE: candidate=entered server={server_name!r} "
            f"tool={tool_name!r} recovery={tool_name in PYTEST_RECOVERY_TOOLS}",
            file=sys.stderr,
        )
        if tool_name in PYTEST_RECOVERY_TOOLS:
            print(
                "[pre_mcp_gate] PYTEST_MCP_TRACE: ALLOW reason=recovery_tool",
                file=sys.stderr,
            )
            return 0
        return check_pytest_gate(REPO_ROOT)

    # Redis MCP: verify Redis connectivity with ADG SQLite fallback
    if server_name == REDIS_SERVER_NAME:
        if tool_name in REDIS_RECOVERY_TOOLS:
            return 0
        return check_redis_gate(REPO_ROOT)

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

    # GitKraken MCP: write-tool preflight + repo confinement
    if server_name == GITKRAKEN_SERVER_NAME:
        return check_gitkraken_gate(tool_name, payload)

    # Notion MCP: verify NOTION_TOKEN is set in OS env before any API call
    if server_name == NOTION_SERVER_NAME:
        return check_notion_gate()

    # All other MCPs (enhanced_http, etc.): fail-open
    return 0


if __name__ == "__main__":
    sys.exit(main())
