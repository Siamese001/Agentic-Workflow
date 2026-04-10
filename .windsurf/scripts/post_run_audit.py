#!/usr/bin/env python3
"""
post_run_audit.py — Windsurf post_run_command advisory audit hook (Phase 1.6).

Reads JSON payload from stdin. Payload fields:
  tool_info.command_line  — the command that was run
  tool_info.cwd           — working directory of the command

Behavior (ADVISORY ONLY — always exits 0):
  - Appends command tracking record to artifacts/windsurf/spawned_processes.jsonl
  - PID: best-effort OS process table lookup; null if unavailable
  - Windsurf does NOT provide a native PID in the post_run_command payload

Fail policy: OPEN — any error → exit 0 silently.
Zero hardcoded paths — REPO_ROOT resolved from __file__.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

FAIL_POLICY = "open"

REPO_ROOT = Path(__file__).resolve().parents[2]
PROCESS_LOG = REPO_ROOT / "artifacts" / "windsurf" / "spawned_processes.jsonl"


def _get_pid_best_effort(command_line: str, cwd: str) -> int | None:
    """
    Best-effort PID lookup via OS process table.
    Scans running processes for one matching command_line + cwd.
    Returns None if unavailable (psutil not installed, permission error, etc.).
    """
    try:
        import psutil

        try:
            proc_iter = psutil.process_iter(["pid", "cmdline", "cwd"])
        except (psutil.AccessDenied, OSError):
            return None
        for proc in proc_iter:
            try:
                proc_cmd = " ".join(proc.info.get("cmdline") or [])
                proc_cwd = proc.info.get("cwd") or ""
                if command_line and command_line in proc_cmd:
                    if not cwd or cwd in proc_cwd or proc_cwd in cwd:
                        return proc.info["pid"]
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except ImportError:
        pass
    return None


def _append_log(record: dict) -> None:
    try:
        PROCESS_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(PROCESS_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except OSError:
        pass


def main() -> int:
    raw = sys.stdin.read()
    if not raw.strip():
        return 0

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return 0

    if not isinstance(payload, dict):
        return 0

    tool_info = payload.get("tool_info", payload)
    if not isinstance(tool_info, dict):
        return 0

    command_line = tool_info.get("command_line", "")
    cwd = tool_info.get("cwd", "")

    pid = _get_pid_best_effort(command_line, cwd)

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "command": command_line,
        "cwd": cwd,
        "pid": pid,
    }
    _append_log(record)

    return 0


if __name__ == "__main__":
    sys.exit(main())
