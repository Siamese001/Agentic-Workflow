"""MCP restart supervisor — respawn dead Python MCP servers (F5.2).

Closes the remediation half of `docs/reports/plans/
rca-otel-mcp-transport-closed-2026-04-23.md`. The companion heartbeat
probe (`mcp_python_heartbeat.py`) *detects* dead servers; this script
*respawns* them using the argv and env declared in `.mcp.json`.

Design invariants
-----------------
1. **Opt-in only.** Refuses to respawn anything unless
   ``MCP_SUPERVISOR_ENABLED=1`` is set in the environment. Hooks never
   invoke this script automatically.
2. **Idempotent.** Already-alive servers are never touched.
3. **Debounced.** Tracks last-spawn timestamp per server in
   ``artifacts/mcp_supervisor/state.json``; refuses to respawn the same
   server more often than ``--min-interval`` seconds (default 30s).
4. **Never fights the host.** When the host respawns a server itself, the
   supervisor sees it alive on the next tick and does nothing.
5. **No PowerShell.** All subprocess calls use ``shell=False`` + explicit
   ``timeout=`` per constitutional §0/§14.
6. **Precise exceptions.** Catches ``OSError`` / ``subprocess.SubprocessError``;
   no bare ``except`` / ``except Exception``.

Usage::

    MCP_SUPERVISOR_ENABLED=1 python .codex/governance/scripts/mcp_python_supervisor.py
    python .codex/governance/scripts/mcp_python_supervisor.py --dry-run
    python .codex/governance/scripts/mcp_python_supervisor.py --json --min-interval 60

Exit codes::

    0  — all servers alive OR respawns attempted
    1  — dry-run detected respawns that would have occurred
    2  — configuration error (config missing / unreadable)
    3  — MCP_SUPERVISOR_ENABLED is not set (fail-closed)
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[3]
_MCP_CONFIG = _REPO / ".mcp.json"
_STATE_PATH = _REPO / "artifacts" / "mcp_supervisor" / "state.json"
_ENV_PLACEHOLDER_RE = re.compile(r"\$\{(?:env:)?([A-Za-z_][A-Za-z0-9_]*)\}")

# Ensure sibling heartbeat probe is importable by path (the scripts dir is
# not a Python package, so we load it as a path-based module).
import importlib.util  # noqa: E402

_HEARTBEAT_PATH = Path(__file__).resolve().parent / "mcp_python_heartbeat.py"
_spec = importlib.util.spec_from_file_location("_mcp_heartbeat_probe", _HEARTBEAT_PATH)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"Cannot load heartbeat probe at {_HEARTBEAT_PATH}")
heartbeat = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(heartbeat)

logger = logging.getLogger("mcp_supervisor")


# ---------------------------------------------------------------------------
# State (debounce ledger)
# ---------------------------------------------------------------------------

def _load_state(state_path: Path) -> dict[str, float]:
    try:
        raw = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if not isinstance(raw, dict):
        return {}
    return {str(k): float(v) for k, v in raw.items() if isinstance(v, (int, float))}


def _save_state(state_path: Path, state: dict[str, float]) -> None:
    try:
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
    except OSError as exc:
        logger.warning("supervisor_state_save_failed path=%s error=%s", state_path, exc)


# ---------------------------------------------------------------------------
# Config extraction
# ---------------------------------------------------------------------------

def _load_server_specs(config_path: Path) -> dict[str, dict[str, Any]]:
    """Return {server_id: {command, args, env}} for every enabled Python server."""
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        logger.error("config_unreadable path=%s error=%s", config_path, exc)
        return {}
    out: dict[str, dict[str, Any]] = {}
    for server_id, cfg in (data.get("mcpServers", {}) or {}).items():
        if cfg.get("disabled"):
            continue
        if cfg.get("command") not in ("python", "python.exe"):
            continue
        out[server_id] = {
            "command": cfg.get("command"),
            "args": list(cfg.get("args", []) or []),
            "env": dict(cfg.get("env", {}) or {}),
        }
    return out


def _expand_env_vars(value: str) -> str:
    """Resolve ``${NAME}`` and ``${env:NAME}`` placeholders against the current process env."""

    def _replace(match: re.Match[str]) -> str:
        return os.environ.get(match.group(1), "")

    return _ENV_PLACEHOLDER_RE.sub(_replace, value)


# ---------------------------------------------------------------------------
# Decide & respawn
# ---------------------------------------------------------------------------

def decide(
    dead_servers: list[str],
    state: dict[str, float],
    now: float,
    min_interval: float,
) -> list[tuple[str, str]]:
    """Return [(server_id, action)] where action is 'respawn' or 'debounced'."""
    decisions: list[tuple[str, str]] = []
    for server_id in dead_servers:
        last = state.get(server_id, 0.0)
        if (now - last) < min_interval:
            decisions.append((server_id, "debounced"))
        else:
            decisions.append((server_id, "respawn"))
    return decisions


def _spawn(server_id: str, spec: dict[str, Any], dry_run: bool) -> dict[str, Any]:
    """Spawn a single MCP server detached from the supervisor."""
    command = spec.get("command") or "python"
    args = [_expand_env_vars(str(a)) for a in spec.get("args", [])]
    env = {**os.environ, **{k: _expand_env_vars(str(v)) for k, v in spec.get("env", {}).items()}}
    argv = [command, *args]
    if dry_run:
        return {"server_id": server_id, "argv": argv, "status": "dry_run"}
    try:
        # Detached so supervisor can exit without killing the child.
        kwargs: dict[str, Any] = {
            "stdin": subprocess.DEVNULL,
            "stdout": subprocess.DEVNULL,
            "stderr": subprocess.DEVNULL,
            "env": env,
            "cwd": str(_REPO),
            "close_fds": True,
        }
        if sys.platform == "win32":
            # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP.
            kwargs["creationflags"] = 0x00000008 | 0x00000200
        else:
            kwargs["start_new_session"] = True
        # guardian: allow-popen-leak -- deliberate detached MCP server process; supervisor must not reap it.
        proc = subprocess.Popen(argv, **kwargs)  # noqa: S603  # argv is config-sourced, shell=False
        return {"server_id": server_id, "argv": argv, "pid": proc.pid, "status": "spawned"}
    except (OSError, subprocess.SubprocessError) as exc:
        return {"server_id": server_id, "argv": argv, "status": "failed", "error": str(exc)}


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def supervise(
    config_path: Path = _MCP_CONFIG,
    state_path: Path = _STATE_PATH,
    min_interval: float = 30.0,
    dry_run: bool = False,
    now: float | None = None,
    heartbeat_report: dict[str, Any] | None = None,
    spec_override: dict[str, dict[str, Any]] | None = None,
    spawn_fn: Any = None,
) -> dict[str, Any]:
    """Run one supervision pass. Returns a structured report."""
    resolved_now = now if now is not None else time.time()
    report = heartbeat_report if heartbeat_report is not None else heartbeat.check()
    if "reason" in report:
        return {"ok": False, "reason": report["reason"]}
    dead: list[str] = list(report.get("dead", []))
    specs = spec_override if spec_override is not None else _load_server_specs(config_path)
    state = _load_state(state_path)
    decisions = decide(dead, state, resolved_now, min_interval)
    spawn = spawn_fn if spawn_fn is not None else _spawn

    results: list[dict[str, Any]] = []
    for server_id, action in decisions:
        if action == "debounced":
            results.append({"server_id": server_id, "status": "debounced"})
            continue
        spec = specs.get(server_id)
        if spec is None:
            results.append({"server_id": server_id, "status": "no_spec"})
            continue
        outcome = spawn(server_id, spec, dry_run)
        results.append(outcome)
        if outcome.get("status") in ("spawned", "dry_run"):
            state[server_id] = resolved_now

    if not dry_run:
        _save_state(state_path, state)

    return {
        "ok": True,
        "dry_run": dry_run,
        "alive": list(report.get("alive", [])),
        "dead": dead,
        "results": results,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="MCP restart supervisor")
    ap.add_argument("--config", type=Path, default=_MCP_CONFIG)
    ap.add_argument("--state", type=Path, default=_STATE_PATH)
    ap.add_argument("--min-interval", type=float, default=30.0,
                    help="Debounce window in seconds (default 30)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    logging.basicConfig(level=logging.INFO, stream=sys.stderr,
                        format="%(levelname)s %(name)s: %(message)s")

    if not args.dry_run and os.environ.get("MCP_SUPERVISOR_ENABLED") != "1":
        logger.error("refusing to respawn: MCP_SUPERVISOR_ENABLED is not set "
                     "(use --dry-run to preview actions)")
        return 3

    report = supervise(
        config_path=args.config,
        state_path=args.state,
        min_interval=args.min_interval,
        dry_run=args.dry_run,
    )
    if not report.get("ok"):
        logger.error("supervise_failed reason=%s", report.get("reason"))
        return 2
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        for r in report["results"]:
            print(f"{r['status']:12s} {r['server_id']}")
        if report["dead"] and args.dry_run:
            print(f"\n(dry-run: {len(report['dead'])} dead server(s) would be respawned)")
    # In dry-run mode, exit 1 when any respawn would have occurred (CI signal).
    if args.dry_run and any(r["status"] == "dry_run" for r in report["results"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
