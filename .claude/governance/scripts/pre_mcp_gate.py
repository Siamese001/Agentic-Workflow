#!/usr/bin/env python3
"""
pre_mcp_gate.py — Cursor pre_mcp_tool_use hard gate (Phase 1.3).

Reads JSON payload from stdin. Payload fields:
  tool_info.mcp_server_name  — name of MCP server being called
  tool_info.mcp_tool_name    — name of tool being called (optional)

Behavior:
  - Filesystem MCP (mcp_server_name == "filesystem") write tools → EXIT 2
      * write_file and edit_file are BLOCKED — Cursor does not pass tool
        arguments to pre_mcp_tool_use hooks, so content validation is impossible
        at this layer. Writes must go through Cursor Agent's native write tools
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
Zero hardcoded paths — repo_root resolved from __file__.
"""

import importlib.util
import json
import os
import sqlite3
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

fail_policy = "closed"
adg_server_name = "adg_sqlite"

# ---------------------------------------------------------------------------
# Destructive-call preflight (constitutional §13, plan
# mcp-destructive-gate-preflight-e9a14b W1 Phase P1). Requires a recent
# successful health probe against the same logical server before honoring
# a destructive MCP call. Heartbeat is maintained by the companion
# post_agent_mcp_preflight_audit.py hook.
#
# Keyed on tool short-name (after stripping the unstable mcp<digits>_
# prefix) to stay resilient across Cursor MCP reorderings.
# ---------------------------------------------------------------------------
_DESTRUCTIVE_PREFLIGHT_TOOLS: dict[str, str] = {
    "adg_close_connections": "adg_sqlite",
    "adg_reopen_connections": "adg_sqlite",
    "adg_reload": "adg_sqlite",
    "redis_flush_namespace": "redis",
    "redis_del_key": "redis",
    "mem_cleanup_stale": "memory",
}

# Must match the constant in post_agent_mcp_preflight_audit.py.
_PREFLIGHT_MAX_AGE_S: int = 60

# Grace period after hook startup: allows the very first destructive call of
# a new session to pass through without a heartbeat (which cannot exist yet
# because no post-response hook has run). Caller is still expected to call
# a health tool in the same response to populate the heartbeat going forward.
_PREFLIGHT_STARTUP_GRACE_S: int = 60

# Additional MCP servers requiring health gates
# These names MUST match the keys in .cursor/mcp.json exactly.
pytest_server_name = "pytest_mcp"
redis_server_name = "redis"  # mcp.json key is "redis", not "redis_mcp"
memory_server_name = "memory"
task_manager_server_name = "task_manager"
vector_db_server_name = "vector_db"
otel_mcp_server_name = "otel_mcp"
deepwiki_server_name = "deepwiki"
gitkraken_server_name = "GitKraken"
notion_server_name = "notion"
tavily_server_name = "tavily"
context7_server_name = "context7"

# Recovery tools that MUST pass even when MCP is unhealthy.
# Without this whitelist, the gate blocks the very tools needed to recover.
adg_recovery_tools = {
    "adg_health",  # mcp1_adg_health — liveness probe
    "adg_status",  # mcp1_adg_status — snapshot status
    "adg_close_connections",  # needed to release SQLite locks
    "adg_reopen_connections",  # needed after lock release
}

pytest_recovery_tools = {
    "list_pytest_config",  # mcp8_list_pytest_config — health probe
    "discover_tests",  # mcp8_discover_tests — basic discovery
}

redis_recovery_tools = {
    "redis_health",  # mcp11_redis_health — liveness probe
}

memory_recovery_tools = {
    "mem_recall_session_start",  # mcp6_mem_recall_session_start — session context
    "mem_get_stats",  # mcp6_mem_get_stats — health metrics
    "search_nodes",  # mcp6_search_nodes — lightweight query probe
}

task_manager_recovery_tools = {
    # Real tool names from @blizzy/mcp-task-manager — verified against MCP registry
    "task_info",  # lightweight read — used as health probe
    "create_task",  # first call in any T2/T3 session — must always be allowed
    "update_task",  # lifecycle transitions (in_progress, done) — must not be blocked by probe failure
    "decompose_task",  # T3 decomposition gate — must not be blocked by probe failure
}

vector_db_recovery_tools = {
    "vector_stats",  # mcp10_vector_stats — health probe
    "list_collections",  # mcp10_list_collections — lightweight check
}

otel_mcp_recovery_tools = {
    "otel_status",  # liveness probe — must bypass gate to diagnose otel_mcp itself
}

# Write-affecting ADG tools that mutate DB state.
# These require a BEGIN IMMEDIATE probe to detect real write contention.
adg_write_tools = {
    "adg_rebuild",
    "adg_checkpoint",
    "adg_compact",
}

sqlite_probe_timeout_ms = 500  # busy_timeout for probe connections

# Module-level cache: subprocess probes are run once per process lifetime.
# Gate checks (pytest, node, chromadb, otel) are expensive if re-run on every
# tool call — cache the result for the lifetime of the hook process.
_probe_cache: dict[str, bool] = {}

filesystem_server_name = "filesystem"
# Write tools on the filesystem MCP that bypass pre_write_code. Blocked here
# so all .py writes are forced through Cursor Agent's native tools and the
# constitutional anti-pattern + syntax gates.
# move_file included: rename/relocate operations mutate the filesystem and
# bypass pre_write_code just as write_file and edit_file do.
filesystem_write_tools = {
    "write_file",  # mcp5_write_file — full overwrite
    "edit_file",  # mcp5_edit_file  — line-based edits
    "move_file",  # mcp4_move_file  — rename/relocate; mutates filesystem
}

repo_root = Path(__file__).resolve().parents[3]
artifacts_adg = repo_root / "artifacts" / "adg"
# Session-state isolation boundary
#
# Current isolation unit: one IDE window / one VS Code process.
# We derive _SESSION_ID from VSCODE_PID when present, with os.getppid()
# as the fallback for pytest / CLI contexts.
#
# This solves:
# - multiple Cursor / VS Code windows clobbering each other
# - parallel pytest workers sharing one session_state file
#
# This does NOT solve:
# - per-chat / per-tab isolation inside the same IDE window
#
# Per-chat isolation requires Cursor to expose a conversation-scoped
# identifier, for example cursor_chat_id. If such an ID becomes available,
# replace vscode_pid in the _session_id derivation and keep the rest of the
# session-state mechanism unchanged.
_session_id = os.environ.get("VSCODE_PID") or str(os.getppid())
session_state = repo_root / "artifacts" / "governance" / f"session_state_{_session_id}.json"

# After this many consecutive blocks without a successful memory recall,
# the gate degrades to open so Cursor Agent is never permanently stuck.
max_memory_block_attempts = 3

# Stale session-state files older than this are removed on each gate startup.
_session_state_max_age_hours = 24

# Launcher script path — validated by check_filesystem_startup_gate() on first use.
# The launcher resolves node + npm global prefix dynamically; no version-pinned paths.
_fs_launcher = repo_root / ".claude" / "governance/scripts" / "filesystem_mcp_launcher.js"
_fs_allowed_dir = repo_root

# ---------------------------------------------------------------------------
# GitKraken MCP hardening constants
# ---------------------------------------------------------------------------

# Canonical workspace root — GitKraken tool `directory` args must resolve
# to this path or a subdirectory of it. Blocks cross-repo accidental mutation.
gitkraken_workspace_root = repo_root

# Tools that mutate LOCAL git state (stage, commit, checkout, stash, worktree add, branch create)
gitkraken_local_write_tools: set[str] = {
    "git_add_or_commit",
    "git_checkout",
    "git_stash",
    "git_worktree",  # add action is a write; list action is safe
    "git_branch",  # create action is a write; list action is safe
    "gitlens_commit_composer",
    "gitlens_start_work",
}

# Tools that mutate REMOTE state (push, PR creation, issue comments)
gitkraken_remote_write_tools: set[str] = {
    "git_push",
    "pull_request_create",
    "pull_request_create_review",
    "issues_add_comment",
    "gitlens_start_review",
}

# All write-capable tools (local + remote)
gitkraken_all_write_tools: set[str] = gitkraken_local_write_tools | gitkraken_remote_write_tools

# These remote-write tools additionally require upstream tracking validation
gitkraken_push_tools: set[str] = {"git_push", "pull_request_create"}


def _exit_block(reason: str) -> int:
    print(f"[pre_mcp_gate] BLOCKED: {reason}", file=sys.stderr)
    return 2


# Module-level cache of approved MCP server names (populated lazily).
_mcp_whitelist_cache: set[str] | None = None


def _load_mcp_whitelist() -> set[str]:
    """Return the set of mcpServers declared in repo .cursor/mcp.json.

    Cached after first load. Returns empty set on any error (caller treats
    as fail-open to avoid breaking sessions when config is temporarily invalid).
    """
    global _mcp_whitelist_cache
    if _mcp_whitelist_cache is not None:
        return _mcp_whitelist_cache
    config_path = repo_root / ".mcp.json"
    try:
        with config_path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        servers = data.get("mcpServers", {})
        if isinstance(servers, dict):
            # Include only servers that are NOT disabled.
            allowed = {
                name
                for name, cfg in servers.items()
                if isinstance(cfg, dict) and not cfg.get("disabled", False)
            }
        else:
            allowed = set()
        _mcp_whitelist_cache = allowed
        return allowed
    except (
        OSError,
        json.JSONDecodeError,
        ValueError,
    ):  # guardian: allow-log-and-swallow -- MCP whitelist load: fail-open on OSError/JSON parse/value errors means gate allows all MCP calls when config is unreadable
        _mcp_whitelist_cache = set()
        return set()


# Claude Code harness-provided MCP servers are environment-managed (session
# management, scheduling, directory, registry, computer-use, etc.) — they are NOT
# declared in the repo .mcp.json and must never be repo-gated. Allow by exact name
# or by the `ccd_` (Claude Code daemon) prefix.
_BUILTIN_MCP_SERVERS: frozenset[str] = frozenset(
    {
        "ccd_session",
        "ccd_session_mgmt",
        "ccd_directory",
        "scheduled-tasks",
        "mcp-registry",
        "computer-use",
    }
)


def check_mcp_whitelist(server_name: str, tool_name: str) -> int:
    """Block calls to MCP servers not declared in repo .mcp.json.

    Fail-open when whitelist cannot be loaded (empty set → every call passes).
    Claude Code harness built-in servers bypass the gate (not repo-managed).
    Hard-block only on explicit violations.
    """
    if server_name in _BUILTIN_MCP_SERVERS or server_name.startswith("ccd_"):
        return 0
    allowed = _load_mcp_whitelist()
    if not allowed:
        # Unable to load config → don't risk bricking the session.
        return 0
    if server_name not in allowed:
        return _exit_block(
            f"MCP server {server_name!r} is not in the repo whitelist "
            f"(.mcp.json mcpServers keys). "
            f"Tool {tool_name!r} refused. "
            f"Add the server to .mcp.json (via .claude/governance/scripts/sync_mcp_config.py) "
            f"or verify you are not invoking a rogue user-home config override."
        )
    return 0


def _read_session_state() -> dict:
    """Read session_state.json and return its contents. Return {} on any error (fail-open)."""
    try:
        if session_state.exists():
            data = json.loads(session_state.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
    except (
        OSError,
        json.JSONDecodeError,
    ):  # guardian: allow-silent-swallow -- session state read: non-fatal, empty dict returned
        pass
    return {}


def _increment_memory_block_attempts() -> int:
    """
    Increment max_memory_block_attempts in session state and return the new count.
    Fail-open: returns max_memory_block_attempts on any I/O error so the gate
    immediately degrades rather than looping.
    """
    try:
        state = _read_session_state()
        count = int(state.get("max_memory_block_attempts", 0)) + 1
        state["max_memory_block_attempts"] = count
        session_state.parent.mkdir(parents=True, exist_ok=True)
        session_state.write_text(json.dumps(state), encoding="utf-8")
        return count
    except (OSError, json.JSONDecodeError):
        return max_memory_block_attempts  # fail-open: treat counter as exhausted


def _mark_memory_recalled() -> None:
    """Set memory_recalled=True and reset block counter in session state."""
    try:
        state = _read_session_state()
        state["memory_recalled"] = True
        state["max_memory_block_attempts"] = 0
        session_state.parent.mkdir(parents=True, exist_ok=True)
        session_state.write_text(json.dumps(state), encoding="utf-8")
    except (
        OSError,
        json.JSONDecodeError,
    ):  # guardian: allow-silent-swallow -- memory recalled state: non-fatal, fail-open
        pass  # fail-open: worst case we block again next call


# Recovery/health tools across ALL servers that should never be blocked
# by the memory-first gate. These are precondition-free probes.
_memory_gate_exempt_tools: set[str] = (
    adg_recovery_tools
    | pytest_recovery_tools
    | redis_recovery_tools
    | memory_recovery_tools
    | task_manager_recovery_tools
    | vector_db_recovery_tools
    | otel_mcp_recovery_tools
)


def check_memory_first_gate(server_name: str, tool_name: str) -> int:
    """
    Hard gate: block non-memory MCP tool calls until mem_recall_session_start
    has been called this session.

    Rules (checked in order):
    1. memory server calls always pass — never deadlock recall itself.
    1a. filesystem read tools always pass — pure stateless reads need no session context.
    1b. Recovery/health tools on any MCP server always pass — these are
        precondition-free probes and must not consume retry budget.
    2. memory_recalled=True in session state → gate satisfied, allow.
    3. Memory MCP unhealthy → degrade-open (auto-mark recalled) to avoid blockage.
    4. max_memory_block_attempts >= max_memory_block_attempts → degrade-open
       (auto-mark recalled) to prevent permanent blocking.
    5. Otherwise: increment attempt counter and block with redirect message.

    Return 0 (allow) or 2 (block).
    """
    # Rule 1: never block the memory server itself
    if server_name == memory_server_name:
        return 0

    # Rule 1a: never block filesystem read tools — pure stateless reads need no session context.
    # Write tools (write_file, edit_file, move_file) are still blocked by check_filesystem_write_gate.
    if server_name == filesystem_server_name and tool_name not in filesystem_write_tools:
        return 0

    # Rule 1b: never block recovery/health tools on any server — these are
    # precondition-free probes and blocking them wastes retry budget on non-work.
    if tool_name in _memory_gate_exempt_tools:
        return 0

    state = _read_session_state()

    # Rule 2: memory already recalled this session — gate satisfied.
    if state.get("memory_recalled", False):
        return 0

    # Rule 3: degrade-open if memory MCP is unhealthy (SQLite inaccessible)
    if check_memory_gate(repo_root) != 0:
        print(
            "[pre_mcp_gate] memory-first gate: memory MCP unhealthy — degrading to open "
            "(auto-marking recalled to prevent retry burn).",
            file=sys.stderr,
        )
        _mark_memory_recalled()
        return 0

    # Rule 4: degrade-open after too many consecutive blocks (prevent infinite loop)
    current_attempts = state.get("max_memory_block_attempts", 0)
    if current_attempts >= max_memory_block_attempts:
        print(
            f"[pre_mcp_gate] memory-first gate: max_memory_block_attempts={current_attempts} "
            f">= {max_memory_block_attempts} — degrading to open "
            "(auto-marking recalled to prevent further blocking).",
            file=sys.stderr,
        )
        _mark_memory_recalled()
        return 0

    # Rule 5: block and redirect
    attempts = _increment_memory_block_attempts()
    return _exit_block(
        f"memory-first gate: call mem_recall_session_start (memory MCP) before any other "
        f"MCP tool [attempt {attempts}/{max_memory_block_attempts}]. "
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
    Invoke ``python tools/generate/generate_full_adg.py`` synchronously to bootstrap the
    ADG SQLite when none exists.  Returns True on success, False on failure.

    Constitutional §3.2: shell=False.  §14: timeout= is mandatory.
    """
    script = repo_root / "tools" / "generate" / "generate_full_adg.py"
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
            timeout=sqlite_probe_timeout_ms / 1000.0,
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
    except (AttributeError, OSError, RuntimeError, TypeError, ValueError) as exc:
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
            timeout=sqlite_probe_timeout_ms / 1000.0,
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
    except (AttributeError, OSError, RuntimeError, TypeError, ValueError) as exc:
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
        c = sqlite3.connect(str(canonical), timeout=sqlite_probe_timeout_ms / 1000.0)
        row = c.execute("PRAGMA journal_mode").fetchone()
        journal_mode = row[0] if row else "unknown"
        c.close()
    except (
        AttributeError,
        OSError,
        RuntimeError,
        TypeError,
        ValueError,
    ):  # guardian: allow-silent-swallow -- SQLite journal probe: non-fatal, diagnostics best-effort
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
    if cache_key not in _probe_cache:
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
        launcher_ok = _fs_launcher.exists()

        # Probe 3: allowed directory exists
        allowed_ok = _fs_allowed_dir.exists()

        _probe_cache[cache_key] = node_ok and launcher_ok and allowed_ok

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
                f"launcher not found at {_fs_launcher}. "
                "Ensure the repo is intact (git status). "
                "Operator note: docs/guides/filesystem_mcp_operations.md",
                file=sys.stderr,
            )
        if not allowed_ok:
            print(
                f"[pre_mcp_gate] Filesystem MCP startup check FAILED: "
                f"allowed directory not found: {_fs_allowed_dir}.",
                file=sys.stderr,
            )

    if not _probe_cache["filesystem_startup_ok"]:
        return _exit_block(
            "Filesystem MCP cannot start — node, launcher, or allowed directory check failed. "
            "See stderr above for which check failed. "
            "Operator note: docs/guides/filesystem_mcp_operations.md"
        )
    return 0


def check_filesystem_write_gate(tool_name: str) -> int:
    """
    Block filesystem MCP write tools (write_file, edit_file).

    Cursor does not expose tool arguments to pre_mcp_tool_use hooks, so
    content-level validation is impossible here. The only safe option is to
    redirect writes to Cursor Agent's native write tools (write_to_file / edit /
    multi_edit) which DO fire pre_write_code and the constitutional gates.
    """
    if tool_name in filesystem_write_tools:
        return _exit_block(
            f"filesystem MCP tool '{tool_name}' is blocked — "
            "use Cursor Agent's native write_to_file / edit / multi_edit tools instead. "
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
                "Run 'python tools/generate/generate_full_adg.py' manually to bootstrap ADG.",
            )

    needs_write = tool_name in adg_write_tools
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
            "refresh when convenient: python tools/generate/generate_full_adg.py",
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
    if cache_key not in _probe_cache:
        try:
            result = subprocess.run(
                [sys.executable, "-c", "import pytest"],
                shell=False,
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            _probe_cache[cache_key] = result.returncode == 0
        except (subprocess.TimeoutExpired, OSError):
            _probe_cache[cache_key] = False

    if not _probe_cache[cache_key]:
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
    except (AttributeError, OSError, RuntimeError, TypeError, ValueError) as exc:
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
                "(auto-generation failed). Run 'python tools/generate/generate_full_adg.py' manually.",
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
            timeout=sqlite_probe_timeout_ms / 1000.0,
        )
        try:
            conn.execute("SELECT 1")
        finally:
            conn.close()
    except sqlite3.OperationalError as exc:
        return _exit_block(
            f"Memory MCP health check failed: SQLite DB inaccessible: {exc}",
        )
    except (AttributeError, OSError, RuntimeError, TypeError, ValueError) as exc:
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
    if cache_key not in _probe_cache:
        try:
            result = subprocess.run(
                ["node", "--version"],
                shell=False,
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            _probe_cache[cache_key] = result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            _probe_cache[cache_key] = False

    if not _probe_cache[cache_key]:
        return _exit_block(
            "Task Manager MCP health check failed: Node.js not found in PATH. "
            "Task Manager requires Node.js (npx @blizzy/mcp-task-manager).",
        )
    return 0


def check_vector_db_gate() -> int:
    """
    Check Vector DB MCP health cheaply for embedded Chroma usage.

    Best-practice change:
    - Do not spawn a subprocess to `import chromadb` on every hook invocation.
      Cursor launches this hook as a fresh process per MCP call, so process-local
      caches provide no cross-call benefit.
    - Do not probe localhost:8000 for Chroma HTTP health when the MCP server uses
      embedded PersistentClient mode against the local persist directory.

    Return 0 (allow) or 2 (block).
    """
    if importlib.util.find_spec("chromadb") is None:
        return _exit_block(
            "Vector DB MCP health check failed: chromadb not installed. Install with: pip install chromadb",
        )
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
    if cache_key not in _probe_cache:
        try:
            result = subprocess.run(
                [sys.executable, "-c", "from opentelemetry import trace"],
                shell=False,
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            _probe_cache[cache_key] = result.returncode == 0
        except (subprocess.TimeoutExpired, OSError):
            _probe_cache[cache_key] = False

    if not _probe_cache[cache_key]:
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
    except OSError:  # guardian: allow-silent-swallow -- otel health check: non-fatal, fail-open
        pass  # network unavailable — fail-open

    return 0


def _run_git(args: list[str], cwd: Path, timeout: int = 5) -> tuple[int, str, str]:
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
    Cursor's pre_mcp_tool_use hook does NOT expose tool arguments, so we
    cannot read the `directory` value directly. We resolve the workspace root
    from gitkraken_workspace_root (= repo_root from mcp.json cwd binding).

    Returns the canonical workspace root Path.
    """
    # Tool arguments are not available in pre_mcp_tool_use hooks. Fall back to
    # the workspace root anchored by the cwd setting in mcp.json.
    return gitkraken_workspace_root.resolve()


def _check_gitkraken_repo_confinement(repo: Path) -> tuple[bool, str]:
    """
    Verify `repo` is a git repository and is confined to the workspace root.
    Returns (blocked, reason). blocked=True → deny.
    """
    workspace = gitkraken_workspace_root.resolve()

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
            "Ensure cwd is set correctly in mcp.json."
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
    rc, stdout, _ = _run_git(["status", "--porcelain", "--no-optional-locks"], repo)
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
    if tool_name not in gitkraken_all_write_tools:
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
    if tool_name in gitkraken_push_tools:
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


def check_notion_wave_deferral(tool_name: str) -> int:
    """
    Block Notion MCP calls while a multi-wave plan is actively executing.

    Rationale: remote MCPs serialize per constitutional §25, so any Notion
    call mid-plan stalls the response and fragments multi-wave execution.
    All Notion plan/backlog writes must batch at plan completion.

    Active state is set/cleared by ``tools/cursor/wave_execution_state.py``
    (start|complete). Absent state => no active plan => allow.

    Bypass: NOTION_WAVE_DEFERRAL_BYPASS=1 env var (for authored batch scripts
    or intentional mid-plan reads).

    Returns 0 (allow) or 2 (block).
    """
    if os.getenv("NOTION_WAVE_DEFERRAL_BYPASS") == "1":
        return 0
    try:
        import _wave_execution_state as _wes  # type: ignore[import-not-found]
    except ImportError:
        # Helper missing — fail-open rather than brick Notion globally.
        return 0
    state = _wes.is_active()
    if state is None:
        return 0
    return _exit_block(
        f"Notion MCP tool {tool_name!r} blocked: multi-wave plan "
        f"{state.get('plan')!r} is active (started {state.get('started_at')}). "
        "Per .claude/rules/notion-plan-wave-deferral.md, batch ALL Notion "
        "writes at end of plan. Complete remaining waves, then run: "
        "python tools/cursor/wave_execution_state.py complete "
        f"--plan {state.get('plan')} -- then reissue the Notion call. "
        "Bypass (exceptional): NOTION_WAVE_DEFERRAL_BYPASS=1"
    )


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
            "  setx NOTION_TOKEN secret_...  (then restart Cursor). "
            "See .env for the expected format (NOTION_TOKEN=secret_... or ntn_...)."
        )
    return 0


def check_tavily_gate() -> int:
    """
    Check Tavily MCP auth gate.

    The tavily MCP subprocess (tavily-mcp) inherits TAVILY_API_KEY from the OS
    environment. An empty or absent key causes the server to start normally
    (green) but every search call returns HTTP 401 — a silent failure. This
    gate makes the failure loud and actionable before any tool call fires.

    Mirrors check_notion_gate() — same invisibility-failure pattern.

    Return 0 (allow) or 2 (block with actionable message).
    """
    token = os.environ.get("TAVILY_API_KEY", "").strip()
    if not token:
        return _exit_block(
            "Tavily MCP auth gate failed: TAVILY_API_KEY is not set or is empty. "
            "Create an API key at https://app.tavily.com/home (free tier: 1000 "
            "credits/month) and register it as a Windows environment variable: "
            "  setx TAVILY_API_KEY tvly-...  (then restart Cursor). "
            "Key format: tvly-<alphanumeric>."
        )
    return 0


def check_context7_gate() -> int:
    """
    Check Context7 MCP gate.

    Context7 (upstash/context7-mcp) has a free tier with no API key required,
    so the gate is fail-open. An optional CONTEXT7_API_KEY (from
    https://context7.com/dashboard) raises rate limits but is not required for
    basic resolve-library-id / get-library-docs calls.

    Return 0 always (fail-open — missing optional key is not a failure).
    """
    return 0


def check_deepwiki_gate() -> int:
    """
    Check DeepWiki MCP health (remote URL MCP).

    DeepWiki is accessed via HTTPS to mcp.deepwiki.com — fail-open always.
    No TCP probe is performed: socket.create_connection timeout= only guards the
    TCP handshake, NOT DNS resolution. On Windows, getaddrinfo() for external
    hostnames can block for 30+ seconds with no Python-level interrupt, causing
    a gate-level hang on every DeepWiki call (before the probe is cached).
    Since this gate always returns 0, the probe risk outweighs any advisory value.

    Return 0 always (fail-open — remote availability is not Cursor Agent's fault).
    """
    return 0  # always fail-open — no DNS probe to avoid Windows getaddrinfo hang


def _purge_stale_session_states() -> None:
    """Delete session_state_{pid}.json files older than _session_state_max_age_hours."""
    cursor_dir = repo_root / "artifacts" / "governance"
    if not cursor_dir.exists():
        return
    cutoff = time.time() - _session_state_max_age_hours * 3600
    for f in cursor_dir.glob("session_state_*.json"):
        try:
            if f.stat().st_mtime < cutoff:
                f.unlink(missing_ok=True)
        except OSError:  # guardian: allow-silent-swallow -- stale state purge: non-fatal, best-effort cleanup
            pass  # best-effort cleanup — never block the gate


def check_destructive_preflight(tool_name: str) -> int:
    """Block destructive MCP calls lacking a recent health heartbeat.

    A destructive call is one that mutates MCP-server or cache state
    (connection teardown, Redis key deletion, stale-memory purge). These
    calls are the ones implicated in the 2026-04-24 client-side hang RCA:
    issued against a server whose health was never verified in-session,
    they trigger the MCP-client transport race that the user perceives
    as a stuck turn.

    Returns 0 to allow, 2 to block. Fail-open on any unexpected error
    (missing heartbeat file is EXPECTED and handled by the grace window).
    """

    destructive_server = _DESTRUCTIVE_PREFLIGHT_TOOLS.get(tool_name)
    if destructive_server is None:
        return 0

    if os.environ.get("MCP_PREFLIGHT_BYPASS", "").strip() == "1":
        return 0

    heartbeat_path = repo_root / "artifacts" / "governance" / "mcp_health_heartbeat.json"

    now = time.time()

    # Grace window — if the hook process is brand-new (first call of the
    # session and the heartbeat file has never been written), allow one
    # destructive call through so the user is not permanently locked out
    # when a fresh session starts by trying to close/reopen ADG.
    heartbeat: dict[str, float] = {}
    if heartbeat_path.exists():
        try:
            raw_hb = heartbeat_path.read_text(encoding="utf-8")
            parsed = json.loads(raw_hb) if raw_hb.strip() else {}
            if isinstance(parsed, dict):
                heartbeat = {k: float(v) for k, v in parsed.items() if isinstance(v, (int, float))}
        except (OSError, ValueError, TypeError):
            heartbeat = {}
    else:
        # No heartbeat file yet — session-startup grace. Allow, but stamp
        # a synthetic entry so a SECOND destructive call in the same
        # grace period still has to pass the freshness check.
        try:
            heartbeat_path.parent.mkdir(parents=True, exist_ok=True)
            heartbeat_path.write_text(
                json.dumps({destructive_server: now - (_PREFLIGHT_MAX_AGE_S + 1)}, indent=2),
                encoding="utf-8",
            )
        except OSError:  # guardian: allow-silent-swallow -- synthetic heartbeat write is best-effort; fail-open preserves turn availability
            pass
        print(
            f"[pre_mcp_gate] PREFLIGHT_GRACE: no heartbeat yet — allowing first "
            f"{tool_name} call; next destructive call requires a recent health probe.",
            file=sys.stderr,
        )
        return 0

    last_ok = heartbeat.get(destructive_server)
    if last_ok is None:
        age_display = "never"
    else:
        age_display = f"{round(now - last_ok, 1)}s"

    if last_ok is not None and (now - last_ok) <= _PREFLIGHT_MAX_AGE_S:
        return 0

    print(
        f"[pre_mcp_gate] BLOCKED: destructive MCP call {tool_name} on server "
        f"{destructive_server} without a recent health preflight "
        f"(heartbeat age: {age_display}; max: {_PREFLIGHT_MAX_AGE_S}s). "
        f"Run the server's health tool (adg_health / redis_health / "
        f"mem_get_stats) first, then retry. This prevents the MCP-client "
        f"transport hang pattern documented in plan "
        f"mcp-destructive-gate-preflight-e9a14b. Bypass: set "
        f"MCP_PREFLIGHT_BYPASS=1 (logged).",
        file=sys.stderr,
    )
    return 2


def main() -> int:
    # Standalone-invocation guard: avoid indefinite hang when invoked via
    # `run_command` / pwsh (inherited stdin never receives EOF). Hook path
    # pipes stdin, which is never a TTY, so hook behavior is unaffected.
    if sys.stdin.isatty():
        return 0
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

    # MCP whitelist — reject any server not declared in .cursor/mcp.json.
    # Mitigates rogue server injection (e.g., user home config override leaking
    # an unapproved server into Cursor Agent's tool surface).
    if server_name:
        rc = check_mcp_whitelist(server_name, tool_name)
        if rc != 0:
            return rc

    # Destructive-call preflight — block state-mutating MCP calls that lack a
    # recent health heartbeat. See plan mcp-destructive-gate-preflight-e9a14b
    # W1 P1 and constitutional §13. Keyed on tool short-name so the check is
    # independent of which numeric mcp<N>_ prefix the server currently holds.
    if tool_name:
        rc = check_destructive_preflight(tool_name)
        if rc != 0:
            return rc

    # [W3 claude-native-supersession-9d3f7a] Memory-first MCP gate RETIRED.
    # Native file-based memory (memory/MEMORY.md) replaces the mandatory
    # mem_recall_session_start ritual; MCP calls are no longer gated on it. (ADR-095)

    # Filesystem MCP: startup health check then write-tool block
    if server_name == filesystem_server_name:
        rc = check_filesystem_startup_gate()
        if rc != 0:
            return rc
        return check_filesystem_write_gate(tool_name)

    # ADG SQLite MCP: health, lock, and staleness checks
    if server_name == adg_server_name:
        if tool_name in adg_recovery_tools:
            # Always allow recovery probes — blocking them creates a dead loop
            return 0
        return check_adg_gate(repo_root, tool_name)

    # Pytest MCP: verify pytest is available
    if server_name == pytest_server_name:
        print(
            f"[pre_mcp_gate] PYTEST_MCP_TRACE: candidate=entered server={server_name!r} "
            f"tool={tool_name!r} recovery={tool_name in pytest_recovery_tools}",
            file=sys.stderr,
        )
        if tool_name in pytest_recovery_tools:
            print(
                "[pre_mcp_gate] PYTEST_MCP_TRACE: ALLOW reason=recovery_tool",
                file=sys.stderr,
            )
            return 0
        return check_pytest_gate(repo_root)

    # Redis MCP: verify Redis connectivity with ADG SQLite fallback
    if server_name == redis_server_name:
        if tool_name in redis_recovery_tools:
            return 0
        return check_redis_gate(repo_root)

    # Memory MCP: verify SQLite DB is accessible
    if server_name == memory_server_name:
        if tool_name in MEMORY_RECOVERY_TOOLS:
            return 0
        return check_memory_gate(repo_root)

    # Task Manager MCP: verify Node.js is available
    if server_name == task_manager_server_name:
        if tool_name in task_manager_recovery_tools:
            return 0
        return check_task_manager_gate()

    # Vector DB MCP: verify ChromaDB is available
    if server_name == vector_db_server_name:
        if tool_name in vector_db_recovery_tools:
            return 0
        return check_vector_db_gate()

    # OpenTelemetry MCP: verify opentelemetry SDK is available
    if server_name == otel_mcp_server_name:
        if tool_name in otel_mcp_recovery_tools:
            return 0
        return check_otel_gate()

    # DeepWiki MCP: remote URL — advisory connectivity check only
    if server_name == deepwiki_server_name:
        return check_deepwiki_gate()

    # GitKraken MCP: write-tool preflight + repo confinement
    if server_name == gitkraken_server_name:
        return check_gitkraken_gate(tool_name, payload)

    # Notion MCP: verify NOTION_TOKEN is set in OS env before any API call
    if server_name == notion_server_name:
        rc = check_notion_wave_deferral(tool_name)
        if rc != 0:
            return rc
        return check_notion_gate()

    # Tavily MCP: verify TAVILY_API_KEY is set in OS env before any API call
    if server_name == tavily_server_name:
        return check_tavily_gate()

    # Context7 MCP: free tier requires no key — fail-open advisory
    if server_name == context7_server_name:
        return check_context7_gate()

    # All other MCPs: fail-open
    return 0


if __name__ == "__main__":
    sys.exit(main())
