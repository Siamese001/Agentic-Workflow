"""Supervised ADG SQLite MCP launcher and out-of-band transport checker.

The MCP stdio channel cannot repair itself once the client reports
``transport closed``. This module keeps the stability contract outside the
transport: validate process environment before startup, preserve the shared
heartbeat-aware sibling guard, write launcher state to disk, and expose a
checker that can run even when the MCP tool channel is unavailable.
"""

from __future__ import annotations

import argparse
from collections.abc import MutableMapping, Sequence
from contextlib import suppress
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sqlite3
import sys
from typing import Any

from tools.mcp import mcp_heartbeat

LAUNCHER_MARKER = "tools.mcp.launch_adg_sqlite_mcp"
ADG_SERVER_MARKERS: tuple[str, str, str] = (
    LAUNCHER_MARKER,
    "tools.adg.mcp.server",
    "tools/adg/mcp/server",
)
DEFAULT_STATE_RELATIVE_PATH = Path("artifacts/mcp_heartbeat/adg_sqlite_launcher.json")
REDIS_PROBE_TIMEOUT_SECONDS = 0.25
CALLABLE_PROOF_ENV = "CODEX_MCP_CALLABLE_ADG_SQLITE"
CALLABLE_PROOF_HEALTHY = "healthy"
ATTACHED_PID_ENV = "CODEX_MCP_ATTACHED_ADG_SQLITE_PID"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _repo_root_from_this_file() -> Path:
    return Path(__file__).resolve().parents[3]


def normalize_optional_env_value(value: str | None) -> str | None:
    """Return a usable env value, ignoring empty/unexpanded placeholders."""
    if value is None:
        return None
    normalized = value.strip().strip('"').strip("'")
    if not normalized:
        return None
    if "$" in normalized or normalized.startswith("{") or normalized.endswith("}"):
        return None
    return normalized


def resolve_repo_root(env: MutableMapping[str, str] | None = None) -> Path:
    """Resolve the ADG repo root without trusting unresolved MCP placeholders."""
    resolved_env = env if env is not None else os.environ
    for key in ("ADG_REPO_ROOT", "AGENTIC_REPO_ROOT"):
        raw = normalize_optional_env_value(resolved_env.get(key))
        if raw:
            candidate = Path(raw).expanduser().resolve()
            if candidate.exists():
                return candidate
    return _repo_root_from_this_file()


def resolve_state_path(
    state_path: str | Path | None = None,
    *,
    repo_root: Path | None = None,
) -> Path:
    if state_path is not None:
        candidate = Path(state_path)
        if candidate.is_absolute():
            return candidate
        return (repo_root or resolve_repo_root()) / candidate
    return (repo_root or resolve_repo_root()) / DEFAULT_STATE_RELATIVE_PATH


def configure_process_environment(
    repo_root: Path,
    env: MutableMapping[str, str] | None = None,
) -> dict[str, str | None]:
    """Normalize environment values needed by the ADG MCP process."""
    resolved_env = env if env is not None else os.environ
    before = {
        "ADG_REPO_ROOT": resolved_env.get("ADG_REPO_ROOT"),
        "AGENTIC_REPO_ROOT": resolved_env.get("AGENTIC_REPO_ROOT"),
        "ADG_REDIS_URL": resolved_env.get("ADG_REDIS_URL"),
        "PYTHONPATH": resolved_env.get("PYTHONPATH"),
    }

    root_text = str(repo_root)
    resolved_env["ADG_REPO_ROOT"] = root_text
    resolved_env["AGENTIC_REPO_ROOT"] = root_text

    redis_url = normalize_optional_env_value(resolved_env.get("ADG_REDIS_URL"))
    if redis_url:
        resolved_env["ADG_REDIS_URL"] = redis_url
    else:
        resolved_env.pop("ADG_REDIS_URL", None)

    pythonpath = resolved_env.get("PYTHONPATH", "")
    parts = [p for p in pythonpath.split(os.pathsep) if p]
    if root_text not in parts:
        resolved_env["PYTHONPATH"] = os.pathsep.join([root_text, *parts])

    return before


def _snapshot_id(sqlite_path: Path) -> str:
    return sqlite_path.stem.replace("adg_indexed_", "")


def _table_count(sqlite_path: Path, table: str) -> int | None:
    conn: sqlite3.Connection | None = None
    try:
        uri = f"file:{sqlite_path.resolve().as_posix()}?mode=ro&immutable=1"
        conn = sqlite3.connect(uri, uri=True, timeout=2.0)
        exists = conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
            (table,),
        ).fetchone()
        if exists is None:
            return None
        row = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
        return int(row[0]) if row else 0
    except (sqlite3.Error, OSError, ValueError):
        return None
    finally:
        if conn is not None:
            conn.close()


def latest_snapshot_status() -> dict[str, Any]:
    from tools.adg.shared_modules.path_resolver import latest_sqlite

    sqlite_path = latest_sqlite(require_nodes_table=True)
    if sqlite_path is None:
        return {
            "status": "critical",
            "available": False,
            "reason": "no valid ADG SQLite snapshot with a nodes table",
        }

    nodes = _table_count(sqlite_path, "nodes")
    edges = _table_count(sqlite_path, "edges")
    return {
        "status": "ok",
        "available": True,
        "sqlite_path": str(sqlite_path.resolve()),
        "snapshot_id": _snapshot_id(sqlite_path),
        "node_count": nodes,
        "edge_count": edges,
    }


def resolved_adg_redis_url(env: MutableMapping[str, str] | None = None) -> str | None:
    resolved_env = env if env is not None else os.environ
    return normalize_optional_env_value(resolved_env.get("ADG_REDIS_URL"))


def redis_probe_status(redis_url: str | None) -> dict[str, Any]:
    """Probe Redis when configured; disabled Redis is not a launcher failure."""
    if not redis_url:
        return {"status": "disabled", "configured": False}

    try:
        import redis  # type: ignore[import-not-found]
    except ImportError:
        return {
            "status": "unavailable",
            "configured": True,
            "error": "redis package is not installed",
        }

    client: Any | None = None
    try:
        client = redis.from_url(
            redis_url,
            socket_connect_timeout=REDIS_PROBE_TIMEOUT_SECONDS,
            socket_timeout=REDIS_PROBE_TIMEOUT_SECONDS,
            decode_responses=True,
        )
        client.ping()
        return {"status": "healthy", "configured": True}
    except (OSError, TimeoutError, ValueError, redis.RedisError) as exc:
        return {
            "status": "unavailable",
            "configured": True,
            "error": f"{type(exc).__name__}: {exc}",
        }
    finally:
        if client is not None:
            with suppress(OSError, redis.RedisError):
                client.close()


def preflight_status(
    *,
    require_redis: bool = False,
    env: MutableMapping[str, str] | None = None,
) -> dict[str, Any]:
    resolved_env = env if env is not None else os.environ
    repo_root = resolve_repo_root(resolved_env)
    configure_process_environment(repo_root, resolved_env)
    sqlite = latest_snapshot_status()
    redis_status = redis_probe_status(resolved_adg_redis_url(resolved_env))

    issues: list[str] = []
    if sqlite.get("status") != "ok":
        issues.append(str(sqlite.get("reason") or "sqlite snapshot unavailable"))
    if require_redis and redis_status.get("status") != "healthy":
        issues.append(str(redis_status.get("error") or "Redis is required but unavailable"))

    status = "ok" if not issues else "critical"
    if status == "ok" and redis_status.get("status") == "unavailable":
        status = "degraded"

    return {
        "status": status,
        "checked_at": _utc_now(),
        "repo_root": str(repo_root),
        "sqlite": sqlite,
        "redis": redis_status,
        "issues": issues,
    }


def write_launcher_state(
    payload: dict[str, Any],
    *,
    state_path: str | Path | None = None,
    repo_root: Path | None = None,
) -> Path:
    path = resolve_state_path(state_path, repo_root=repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(f"{path.suffix}.tmp")
    tmp_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp_path.replace(path)
    return path


def read_launcher_state(
    *,
    state_path: str | Path | None = None,
    repo_root: Path | None = None,
) -> dict[str, Any] | None:
    path = resolve_state_path(state_path, repo_root=repo_root)
    try:
        if not path.exists():
            return None
        raw = json.loads(path.read_text(encoding="utf-8"))
        return raw if isinstance(raw, dict) else None
    except (OSError, json.JSONDecodeError, TypeError):
        return None


def _process_alive(pid: int | None) -> bool | None:
    if not pid or pid <= 0:
        return None
    try:
        import psutil  # type: ignore[import-not-found]
    except ImportError:
        return None
    try:
        proc = psutil.Process(pid)
        if not proc.is_running():
            return False
        return proc.status() not in (
            psutil.STATUS_ZOMBIE,
            psutil.STATUS_STOPPED,
            psutil.STATUS_DEAD,
        )
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, OSError):
        return False


def heartbeat_status(markers: Sequence[str] = ADG_SERVER_MARKERS) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for marker in markers:
        hb = mcp_heartbeat.read_heartbeat(marker)
        if hb is None:
            rows.append(
                {
                    "marker": marker,
                    "present": False,
                    "fresh": False,
                    "authoritative": False,
                    "pid": None,
                }
            )
            continue
        ts, pid = hb
        rows.append(
            {
                "marker": marker,
                "present": True,
                "timestamp": ts,
                "pid": pid,
                "fresh": mcp_heartbeat.is_heartbeat_fresh(marker),
                "authoritative": mcp_heartbeat.is_heartbeat_authoritative(marker),
                "process_alive": _process_alive(pid),
            }
        )
    return rows


def _normalize_marker_text(value: str) -> str:
    return value.strip().strip("\"'").lower().replace("\\", "/")


def _cmdline_matches_marker(cmdline: Sequence[Any], markers: Sequence[str]) -> bool:
    """Return True when cmdline has a direct module/script marker argument."""
    normalized_markers = tuple(_normalize_marker_text(marker) for marker in markers)
    for raw_part in cmdline:
        part = _normalize_marker_text(str(raw_part))
        for marker in normalized_markers:
            if not marker:
                continue
            if "/" in marker:
                part_without_suffix = part[:-3] if part.endswith(".py") else part
                marker_without_suffix = marker[:-3] if marker.endswith(".py") else marker
                if part_without_suffix == marker_without_suffix or part_without_suffix.endswith(
                    f"/{marker_without_suffix}"
                ):
                    return True
                continue
            if part == marker or part.endswith(f"/{marker}"):
                return True
    return False


def _same_parent_older_sibling_pids(
    process_rows: Sequence[dict[str, Any]],
    *,
    current_pid: int,
    current_ppid: int,
    current_create_time: float,
    markers: Sequence[str] = ADG_SERVER_MARKERS,
) -> list[int]:
    """Select older ADG launch siblings owned by the same Codex parent."""
    selected: list[tuple[float, int]] = []
    for row in process_rows:
        pid = row.get("pid")
        if not isinstance(pid, int) or pid == current_pid:
            continue
        if row.get("ppid") != current_ppid:
            continue
        create_time = row.get("create_time")
        if not isinstance(create_time, (int, float)):
            continue
        if create_time >= current_create_time:
            continue
        if not _cmdline_matches_marker(row.get("cmdline") or [], markers):
            continue
        selected.append((float(create_time), pid))
    return [pid for _create_time, pid in sorted(selected)]


def terminate_same_parent_older_siblings(
    markers: Sequence[str] = ADG_SERVER_MARKERS,
) -> list[int]:
    """Terminate older ADG launchers under the same parent process.

    The shared heartbeat guard intentionally preserves any fresh sibling to
    avoid cross-window split-brain. Codex restarts, however, can leave multiple
    launchers under the same parent. In that same-parent case the newest
    launcher is the one the host just spawned and should be the serving
    transport; older same-parent launchers are stale competitors.
    """
    try:
        import psutil  # type: ignore[import-not-found]
    except ImportError:
        return []

    current = psutil.Process(os.getpid())
    current_pid = current.pid
    current_ppid = current.ppid()
    current_create_time = current.create_time()
    rows: list[dict[str, Any]] = []
    for proc in psutil.process_iter(["pid", "ppid", "cmdline", "create_time"]):
        info = proc.info
        rows.append(
            {
                "pid": info.get("pid"),
                "ppid": info.get("ppid"),
                "cmdline": info.get("cmdline") or [],
                "create_time": info.get("create_time"),
            }
        )

    target_pids = _same_parent_older_sibling_pids(
        rows,
        current_pid=current_pid,
        current_ppid=current_ppid,
        current_create_time=current_create_time,
        markers=markers,
    )
    terminated: list[int] = []
    for pid in target_pids:
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except psutil.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=2)
            terminated.append(pid)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, OSError):
            continue
    return terminated


def _parse_pid(raw: str | None) -> int | None:
    if raw is None or not raw.strip():
        return None
    try:
        pid = int(raw.strip())
    except ValueError:
        return None
    return pid if pid > 0 else None


def callable_proof_status(env: MutableMapping[str, str] | None = None) -> dict[str, Any]:
    """Return whether the active Codex host proved ADG MCP callability.

    A fresh heartbeat only proves that a Python MCP process is alive. It does
    not prove that the current Codex stdio route can call tools on that process.
    The proof bit is deliberately supplied out-of-band after a live
    mcp__adg_sqlite tool call succeeds in the active session.
    """
    resolved_env = env if env is not None else os.environ
    raw = (resolved_env.get(CALLABLE_PROOF_ENV) or "").strip().lower()
    attached_pid_raw = resolved_env.get(ATTACHED_PID_ENV)
    attached_pid = _parse_pid(attached_pid_raw)
    attached_pid_alive = _process_alive(attached_pid)
    callable_ok = (
        raw == CALLABLE_PROOF_HEALTHY
        and attached_pid is not None
        and attached_pid_alive is True
    )
    return {
        "env_key": CALLABLE_PROOF_ENV,
        "status": raw or "absent",
        "callable": callable_ok,
        "required_value": CALLABLE_PROOF_HEALTHY,
        "attached_pid_env_key": ATTACHED_PID_ENV,
        "attached_pid": attached_pid,
        "attached_pid_alive": attached_pid_alive,
        "proof_required": (
            "Set CODEX_MCP_CALLABLE_ADG_SQLITE=healthy and "
            "CODEX_MCP_ATTACHED_ADG_SQLITE_PID=<pid> only after a live "
            "mcp__adg_sqlite.adg_health or adg_runtime_info call succeeds "
            "in the active Codex session; use adg_process_identity or "
            "adg_runtime_info for the attached PID."
        ),
    }


def transport_status(
    *,
    state_path: str | Path | None = None,
    require_redis: bool = False,
    env: MutableMapping[str, str] | None = None,
) -> dict[str, Any]:
    resolved_env = env if env is not None else os.environ
    preflight = preflight_status(require_redis=require_redis, env=resolved_env)
    repo_root = Path(str(preflight["repo_root"]))
    state = read_launcher_state(state_path=state_path, repo_root=repo_root)
    heartbeats = heartbeat_status()
    callable_proof = callable_proof_status(resolved_env)
    heartbeat_authoritative = any(row.get("authoritative") for row in heartbeats)
    heartbeat_authoritative_pids = {
        int(row["pid"])
        for row in heartbeats
        if row.get("authoritative") and isinstance(row.get("pid"), int)
    }
    fresh_transport = any(row.get("fresh") for row in heartbeats)
    proof_pid = callable_proof.get("attached_pid")
    proof_pid_matches_heartbeat = (
        isinstance(proof_pid, int) and proof_pid in heartbeat_authoritative_pids
    )
    open_transport = (
        heartbeat_authoritative
        and bool(callable_proof["callable"])
        and proof_pid_matches_heartbeat
    )

    if open_transport:
        status = "open"
    elif preflight["status"] == "critical":
        status = "blocked"
    elif heartbeat_authoritative or fresh_transport:
        if callable_proof["status"] == "closed_transport":
            status = "closed_transport"
        elif callable_proof["status"] == CALLABLE_PROOF_HEALTHY:
            status = "stale_callable_proof"
        else:
            status = "callability_unproven"
    else:
        status = "closed"

    return {
        "status": status,
        "checked_at": _utc_now(),
        "preflight": preflight,
        "state": state,
        "heartbeats": heartbeats,
        "open": open_transport,
        "heartbeat_authoritative": heartbeat_authoritative,
        "heartbeat_authoritative_pids": sorted(heartbeat_authoritative_pids),
        "proof_pid_matches_heartbeat": proof_pid_matches_heartbeat,
        "callable_proof": callable_proof,
    }


def _json_exit_code(status: str) -> int:
    if status in {"ok", "open"}:
        return 0
    if status == "degraded":
        return 1
    return 2


def _emit(payload: dict[str, Any], *, as_json: bool, stream: Any = sys.stdout) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True), file=stream)
        return
    print(f"status: {payload.get('status')}", file=stream)
    for issue in payload.get("issues", []) or []:
        print(f"- {issue}", file=stream)


def main_launcher(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Launch ADG SQLite MCP with preflight supervision.")
    parser.add_argument("--preflight-only", action="store_true", help="validate startup inputs and exit")
    parser.add_argument("--json", action="store_true", help="emit JSON for preflight/status output")
    parser.add_argument("--require-redis", action="store_true", help="fail startup if configured Redis is down")
    parser.add_argument("--state-path", help="launcher state path; defaults under artifacts/mcp_heartbeat")
    parser.add_argument("--skip-guard", action="store_true", help="do not run sibling process guard")
    args = parser.parse_args(argv)

    preflight = preflight_status(require_redis=args.require_redis)
    if args.preflight_only:
        _emit(preflight, as_json=args.json)
        return _json_exit_code(preflight["status"])

    repo_root = Path(str(preflight["repo_root"]))
    if preflight["status"] == "critical":
        _emit(preflight, as_json=True, stream=sys.stderr)
        return 2

    same_parent_terminated_pids = [] if args.skip_guard else terminate_same_parent_older_siblings()
    state_base = {
        "pid": os.getpid(),
        "started_at": _utc_now(),
        "repo_root": str(repo_root),
        "preflight": preflight,
        "launcher_marker": LAUNCHER_MARKER,
        "same_parent_terminated_pids": same_parent_terminated_pids,
    }
    write_launcher_state(
        {**state_base, "status": "starting"},
        state_path=args.state_path,
        repo_root=repo_root,
    )

    try:
        if not args.skip_guard:
            from tools.mcp.mcp_bootstrap import guard_single_instance

            guard_single_instance(ADG_SERVER_MARKERS, skip_env="ADG_SKIP_ZOMBIE_KILL")

        write_launcher_state(
            {**state_base, "status": "running", "running_at": _utc_now()},
            state_path=args.state_path,
            repo_root=repo_root,
        )
        from tools.adg.mcp.server import mcp

        mcp.run(transport="stdio")
        return 0
    finally:
        write_launcher_state(
            {**state_base, "status": "stopped", "stopped_at": _utc_now()},
            state_path=args.state_path,
            repo_root=repo_root,
        )


def main_check(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check ADG SQLite MCP transport without using MCP.")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    parser.add_argument("--require-redis", action="store_true", help="treat Redis unavailability as blocked")
    parser.add_argument("--state-path", help="launcher state path; defaults under artifacts/mcp_heartbeat")
    args = parser.parse_args(argv)

    result = transport_status(state_path=args.state_path, require_redis=args.require_redis)
    _emit(result, as_json=args.json)
    return _json_exit_code(result["status"])


__all__ = [
    "ADG_SERVER_MARKERS",
    "ATTACHED_PID_ENV",
    "CALLABLE_PROOF_ENV",
    "CALLABLE_PROOF_HEALTHY",
    "LAUNCHER_MARKER",
    "callable_proof_status",
    "configure_process_environment",
    "heartbeat_status",
    "latest_snapshot_status",
    "main_check",
    "main_launcher",
    "normalize_optional_env_value",
    "preflight_status",
    "read_launcher_state",
    "redis_probe_status",
    "resolve_repo_root",
    "resolve_state_path",
    "transport_status",
    "write_launcher_state",
]
