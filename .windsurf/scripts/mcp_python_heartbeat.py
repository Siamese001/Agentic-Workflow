"""MCP heartbeat probe — detect dead Python MCP servers at session start.

Deferred from `docs/reports/plans/rca-otel-mcp-transport-closed-2026-04-23.md`.

Problem
-------
Windsurf's MCP supervisor does not auto-respawn dead stdio subprocess
servers. Once an `adg_sqlite` / `otel_mcp` / `redis` / `memory` / `pytest_mcp` /
`vector_db` server dies (OOM, GUARD_CLEAN cascade, unhandled exception),
the client-side handle stays registered but points to a corpse. The next
tool call surfaces `transport closed` seemingly out of nowhere.

Behavior
--------
Scans the live process table for each Python MCP server marker defined in
`.windsurf/mcp_config.json`. Reports which are alive, which are dead, and
prints a one-line remediation hint when any are dead. Exit code:

    0 - all configured Python MCP servers have at least one live process
    1 - at least one configured Python MCP server has zero live processes
    2 - config unreadable

This is ADVISORY only; it never kills or restarts anything. It is safe
to run repeatedly and is intended to be invoked at Cursor Agent session
start (or before any T2/T3 MCP-dependent work).

Usage
-----
    python .windsurf/scripts/mcp_python_heartbeat.py
    python .windsurf/scripts/mcp_python_heartbeat.py --json
    python .windsurf/scripts/mcp_python_heartbeat.py --quiet
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[2]
_MCP_CONFIG = _REPO / ".windsurf" / "mcp_config.json"


def _load_python_mcp_servers() -> dict[str, str]:
    """Return {server_id: script_marker} for Python-launched MCP servers.

    Non-Python MCP servers (GitKraken, notion, task_manager) are skipped —
    they have different restart behavior and are tracked independently.
    """
    try:
        data = json.loads(_MCP_CONFIG.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    out: dict[str, str] = {}
    for server_id, cfg in (data.get("mcpServers", {}) or {}).items():
        if cfg.get("disabled"):
            continue
        if cfg.get("command") not in ("python", "python.exe"):
            continue
        args = cfg.get("args", [])
        marker: str | None = None
        # Pattern 1: python -u <path/to/script.py>
        for arg in args:
            if isinstance(arg, str) and arg.endswith(".py"):
                marker = re.sub(r"\$\{env:[^}]+\}/?", "", arg).strip("/\\")
                break
        # Pattern 2: python -u -m tools.adg.mcp.something
        if marker is None:
            for idx, arg in enumerate(args):
                if arg == "-m" and idx + 1 < len(args):
                    marker = str(args[idx + 1])
                    break
        if marker:
            out[server_id] = marker
    return out


def _list_python_processes() -> list[str]:
    """Return each python.exe process's command line (one string per PID)."""
    if sys.platform != "win32":
        # POSIX fallback — best-effort; not exercised in the Windsurf config
        # where this is used, but keeps the probe portable.
        try:
            out = subprocess.run(
                ["ps", "-eo", "pid,command"],
                capture_output=True, text=True, timeout=10, check=False,
            )
            return [line for line in out.stdout.splitlines() if "python" in line]
        except (OSError, subprocess.SubprocessError):
            return []
    try:
        out = subprocess.run(
            [
                "powershell", "-NoProfile", "-Command",
                "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\""
                " | Select-Object -ExpandProperty CommandLine"
            ],
            capture_output=True, text=True, timeout=10, check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    return [line for line in out.stdout.splitlines() if line.strip()]


def check() -> dict[str, Any]:
    """Return a report of which MCP servers are alive / dead."""
    servers = _load_python_mcp_servers()
    if not servers:
        return {"ok": False, "reason": "mcp_config_unreadable_or_no_python_servers"}
    cmdlines = _list_python_processes()
    alive: list[str] = []
    dead: list[str] = []
    for server_id, marker in servers.items():
        found = any(marker in line for line in cmdlines)
        (alive if found else dead).append(server_id)
    return {
        "ok": len(dead) == 0,
        "alive": sorted(alive),
        "dead": sorted(dead),
        "total_checked": len(servers),
        "python_proc_count": len(cmdlines),
    }


def _format_human(report: dict[str, Any]) -> str:
    if "reason" in report:
        return f"MCP heartbeat: FAILED to probe ({report['reason']})"
    lines = [
        f"MCP Python heartbeat  ({len(report['alive'])}/{report['total_checked']} alive)",
    ]
    for s in report.get("alive", []):
        lines.append(f"  [ALIVE] {s}")
    for s in report.get("dead", []):
        lines.append(f"  [DEAD ] {s}")
    if report.get("dead"):
        lines.append("")
        lines.append(
            "HINT: reload the Windsurf window to respawn dead MCP servers. "
            "See docs/reports/plans/rca-otel-mcp-transport-closed-2026-04-23.md."
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="MCP Python heartbeat probe")
    ap.add_argument("--json", action="store_true", help="Emit JSON instead of text")
    ap.add_argument("--quiet", action="store_true", help="Suppress text output; exit code only")
    args = ap.parse_args(argv)
    report = check()
    if args.quiet:
        pass
    elif args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(_format_human(report))
    if "reason" in report:
        return 2
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
