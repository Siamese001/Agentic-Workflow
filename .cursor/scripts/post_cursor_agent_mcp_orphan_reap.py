#!/usr/bin/env python3
"""Post-cursor-agent hook: reap orphan MCP server processes from stale sessions.

Context
-------
Even with ``guard_single_instance()`` adopted in all Python MCP servers,
there is a window between Windsurf window reloads where stale cohorts
survive:

    1. Cohort A spawned at T0.
    2. User reloads the IDE window.
    3. Cohort B starts at T1. Each B-server's startup guard terminates the
       matching A-server — BUT third-party node/npx MCPs (filesystem,
       notion, task_manager) cannot self-guard.
    4. A's node processes linger until this hook reaps them.

This hook runs after every Cursor Agent response. It shells out to the shared
detector at ``tools/debug/check_orphan_mcp_processes.py --kill`` with the
existing cohort-gap and stale-min defaults, so behavior is identical to a
manual invocation. It NEVER blocks Cursor Agent: on any failure the hook logs
and exits 0.

Bypass: set ``MCP_ORPHAN_REAP_BYPASS=1`` in the environment.

Audit trail: ``artifacts/cursor/mcp_orphan_reap.jsonl`` — one JSON line
per invocation with scan counts, orphan PIDs (if any), and kill results.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DETECTOR = REPO_ROOT / "tools" / "debug" / "check_orphan_mcp_processes.py"
LOG_PATH = REPO_ROOT / "artifacts" / "windsurf" / "mcp_orphan_reap.jsonl"

# Cohort-gap of 60s and stale-min of 5 minutes mean: a freshly-spawned
# cohort B needs to wait at least 5 minutes before any A-process is
# eligible for reaping. This avoids killing a slow-starter in cohort B
# by mistake. Keep aligned with the detector's defaults.
COHORT_GAP_SEC = "60"
STALE_MIN = "5"


def _log(record: dict) -> None:
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, separators=(",", ":")) + "\n")
    except OSError:
        # Logging must never block the hook.
        pass


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def main() -> int:
    if os.environ.get("MCP_ORPHAN_REAP_BYPASS") == "1":
        _log({"ts": _utc_now(), "action": "bypass",
              "reason": "MCP_ORPHAN_REAP_BYPASS=1"})
        return 0

    if not DETECTOR.exists():
        _log({"ts": _utc_now(), "action": "skip",
              "reason": f"detector missing: {DETECTOR}"})
        return 0

    cmd = [
        sys.executable,
        str(DETECTOR),
        "--kill",
        "--json",
        "--cohort-gap-sec", COHORT_GAP_SEC,
        "--stale-min", STALE_MIN,
    ]

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(REPO_ROOT),
            shell=False,
            check=False,
        )
    except subprocess.TimeoutExpired:
        _log({"ts": _utc_now(), "action": "error", "reason": "timeout"})
        return 0
    except (OSError, subprocess.SubprocessError) as exc:
        _log({"ts": _utc_now(), "action": "error",
              "reason": f"spawn failed: {exc!s}"})
        return 0

    # Detector emits JSON to stdout when --json is set.
    parsed: dict = {}
    try:
        parsed = json.loads(proc.stdout) if proc.stdout.strip() else {}
    except json.JSONDecodeError:
        pass

    record = {
        "ts": _utc_now(),
        "action": "scan",
        "returncode": proc.returncode,
        "total_procs_seen": parsed.get("total_procs_seen"),
        "mcp_procs": parsed.get("mcp_procs"),
        "orphan_count": parsed.get("orphan_count"),
    }
    if parsed.get("orphans"):
        record["action"] = "reaped" if parsed.get("orphan_count") else "scan"
        record["orphans"] = [
            {"pid": o["pid"], "cmdline": o["cmdline"][:200]}
            for o in parsed["orphans"]
        ]
    _log(record)
    # Always succeed — we must never block Cursor Agent.
    return 0


if __name__ == "__main__":
    sys.exit(main())
