#!/usr/bin/env python3
"""Detect (and optionally kill) orphaned MCP server processes.

Background
----------
When legacy editor restarts Codex or the user reloads the window, the OS-level
MCP server processes (``tools/mcp/*.py``, ``tools/adg/mcp/server``, etc.)
are not always terminated. They keep running with a dangling stdio pair,
and the next Codex session spawns a FRESH set. Two (or more) concurrent
MCP fleets sharing the same workspace stdio pool cause:

    * Interleaved stdout across ``run_command`` invocations
    * Phantom "Step was canceled by user" messages
    * Intermittent hangs at what looks like simple tool calls

See ``.claude/rules/mcp-serialization.md`` for the upstream race this
interacts with (``anthropics/claude-agent-sdk-typescript#41``).

Usage
-----
    py tools/debug/check_orphan_mcp_processes.py            # report only
    py tools/debug/check_orphan_mcp_processes.py --kill     # kill orphans

An "orphan" here = an MCP server process (python matching
``tools/mcp/*_server.py`` / ``tools/adg/mcp/server`` / ``tools/memory/*``
/ ``tools/otel/*``) started more than ``--stale-min`` minutes before
the most recent one.

If a single active cohort exists, none are orphans. If two or more
generations are detected (start-time gap > ``--cohort-gap-sec``), every
process older than the most recent cohort is flagged.
"""

from __future__ import annotations

import argparse
import os
import re
import signal
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable

# Patterns that identify MCP server processes by their command line.
_MCP_CMDLINE_PATTERNS = [
    re.compile(r"tools[/\\]mcp[/\\]\w+_server\.py"),
    re.compile(r"tools\.adg\.mcp\.server"),
    re.compile(r"tools[/\\]adg[/\\]mcp[/\\]server\.py"),
    re.compile(r"tools[/\\]memory[/\\]\w+_server\.py"),
    re.compile(r"tools[/\\]otel[/\\]\w+_server\.py"),
    re.compile(r"filesystem_mcp_launcher\.js"),
    re.compile(r"notion-mcp-server"),
    re.compile(r"mcp-task-manager"),
    re.compile(r"server-filesystem[/\\]dist[/\\]index\.js"),
]


@dataclass
class Proc:
    pid: int
    started: datetime
    cmdline: str

    def is_mcp(self) -> bool:
        return any(p.search(self.cmdline) for p in _MCP_CMDLINE_PATTERNS)


def _run(cmd: list[str]) -> str:
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    ).stdout


def list_processes_windows() -> list[Proc]:
    """Enumerate python/node processes via WMIC-equivalent PowerShell call."""
    ps_script = (
        "Get-CimInstance Win32_Process -Filter "
        "\"Name='python.exe' or Name='node.exe' or Name='py.exe'\" | "
        "Select-Object ProcessId, CreationDate, CommandLine | "
        "ConvertTo-Json -Depth 2 -Compress"
    )
    raw = _run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            ps_script,
        ]
    )
    if not raw.strip():
        return []
    import json

    try:
        items = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if isinstance(items, dict):
        items = [items]
    out: list[Proc] = []
    for item in items:
        pid = item.get("ProcessId")
        cmd = item.get("CommandLine") or ""
        cd = item.get("CreationDate") or ""
        # CIM CreationDate format: /Date(millis-since-epoch)/ OR WMI UTC
        started: datetime | None = None
        m = re.match(r"/Date\((\d+)\)/", cd)
        if m:
            started = datetime.fromtimestamp(int(m.group(1)) / 1000)
        elif cd and cd[:14].isdigit():
            try:
                started = datetime.strptime(cd[:14], "%Y%m%d%H%M%S")
            except ValueError:
                started = None
        if pid is None or started is None:
            continue
        out.append(Proc(pid=int(pid), started=started, cmdline=cmd))
    return out


def list_processes_posix() -> list[Proc]:
    raw = _run(["ps", "-eo", "pid,lstart,args"])
    out: list[Proc] = []
    for line in raw.splitlines()[1:]:
        parts = line.strip().split(None, 6)
        if len(parts) < 7:
            continue
        pid_s = parts[0]
        lstart = " ".join(parts[1:6])
        args = parts[6]
        try:
            pid = int(pid_s)
            started = datetime.strptime(lstart, "%a %b %d %H:%M:%S %Y")
        except ValueError:
            continue
        out.append(Proc(pid=pid, started=started, cmdline=args))
    return out


def find_orphans(
    procs: Iterable[Proc],
    *,
    cohort_gap_sec: int,
    stale_min: int,
) -> list[Proc]:
    """Identify orphan MCP processes.

    Algorithm:
      1. Filter to MCP processes only.
      2. Sort by start time descending.
      3. Find the 'active cohort' — the most recent contiguous set of
         processes whose neighbours started within ``cohort_gap_sec``.
      4. Anything older than the active cohort is an orphan IF it is
         at least ``stale_min`` minutes old.
    """
    mcp_procs = sorted(
        (p for p in procs if p.is_mcp()),
        key=lambda p: p.started,
        reverse=True,
    )
    if len(mcp_procs) <= 1:
        return []
    # Active cohort = contiguous from newest as long as gap < threshold.
    active_cutoff = mcp_procs[0].started
    for p in mcp_procs[1:]:
        if (active_cutoff - p.started).total_seconds() <= cohort_gap_sec:
            active_cutoff = p.started
            continue
        break
    min_orphan_age = timedelta(minutes=stale_min)
    now = datetime.now()
    return [p for p in mcp_procs if p.started < active_cutoff and (now - p.started) >= min_orphan_age]


def kill(pid: int) -> tuple[bool, str]:
    """Cross-platform process kill. Returns (ok, message)."""
    try:
        if os.name == "nt":
            rc = subprocess.run(
                ["taskkill", "/F", "/PID", str(pid)],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            return rc.returncode == 0, (rc.stderr or rc.stdout).strip()
        os.kill(pid, signal.SIGTERM)
        return True, "SIGTERM sent"
    except (OSError, subprocess.SubprocessError) as exc:
        return False, str(exc)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--kill",
        action="store_true",
        help="kill detected orphans (default: report only)",
    )
    parser.add_argument(
        "--cohort-gap-sec",
        type=int,
        default=60,
        help="max seconds between neighbour start-times inside a cohort",
    )
    parser.add_argument(
        "--stale-min",
        type=int,
        default=5,
        help="minimum age (minutes) for a proc to be considered orphan",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit JSON instead of human summary",
    )
    args = parser.parse_args(argv)

    listed = list_processes_windows() if os.name == "nt" else list_processes_posix()
    orphans = find_orphans(
        listed,
        cohort_gap_sec=args.cohort_gap_sec,
        stale_min=args.stale_min,
    )

    if args.json:
        import json

        print(
            json.dumps(
                {
                    "total_procs_seen": len(listed),
                    "mcp_procs": sum(1 for p in listed if p.is_mcp()),
                    "orphan_count": len(orphans),
                    "orphans": [
                        {"pid": p.pid, "started": p.started.isoformat(), "cmdline": p.cmdline}
                        for p in orphans
                    ],
                },
                indent=2,
            )
        )
        return 1 if orphans and not args.kill else 0

    print(
        f"[orphan-mcp] scanned {len(listed)} python/node procs, "
        f"{sum(1 for p in listed if p.is_mcp())} look like MCP, "
        f"{len(orphans)} are orphans"
    )
    if not orphans:
        print("[orphan-mcp] clean.")
        return 0
    for p in orphans:
        print(f"  PID {p.pid:>6} started={p.started.isoformat()} cmd={p.cmdline[:120]}")
    if not args.kill:
        print("[orphan-mcp] rerun with --kill to terminate.")
        return 1
    print("[orphan-mcp] killing orphans...")
    failures = 0
    for p in orphans:
        ok, msg = kill(p.pid)
        status = "OK" if ok else "FAIL"
        print(f"  [{status}] PID {p.pid}: {msg}")
        if not ok:
            failures += 1
    return 0 if failures == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
