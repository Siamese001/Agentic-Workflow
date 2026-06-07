#!/usr/bin/env python3
"""
post_run_audit.py — Cursor post_run_command advisory audit hook (Phase 1.6).

Reads JSON payload from stdin. Payload fields:
  tool_info.command_line  — the command that was run
  tool_info.cwd           — working directory of the command

Behavior (ADVISORY ONLY — always exits 0):
  - Appends command tracking record to artifacts/governance/spawned_processes.jsonl
  - PID: best-effort OS process table lookup; null if unavailable
  - Cursor does NOT provide a native PID in the post_run_command payload

Fail policy: OPEN — any error → exit 0 silently.
Zero hardcoded paths — repo_root resolved from __file__.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

fail_policy = "open"

repo_root = Path(__file__).resolve().parents[3]
process_log = repo_root / "artifacts" / "governance" / "spawned_processes.jsonl"


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
        except (psutil.AccessDenied, OSError):  # guardian: allow-return-none-swallow -- psutil access denied: non-fatal, caller handles None
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
    except ImportError:  # guardian: allow-silent-swallow -- psutil optional: non-fatal, PID lookup skipped
        pass
    return None


def _append_log(record: dict) -> None:
    try:
        process_log.parent.mkdir(parents=True, exist_ok=True)
        with open(process_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except OSError:  # guardian: allow-silent-swallow -- process log write: non-fatal, fail-open
        pass


def main() -> int:
    # Standalone-invocation guard: avoid indefinite hang when invoked via
    # `run_command` / pwsh (inherited stdin never receives EOF). Hook path
    # pipes stdin, which is never a TTY, so hook behavior is unaffected.
    if sys.stdin.isatty():
        return 0
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

    # W4.4 — test_selection ledger: when the command is a pytest invocation,
    # capture the selected tests as a triage-selection event. Actual outcome
    # binding (pass/fail counts) happens later via post-commit or CI parsing.
    try:
        lower_cmd = (command_line or "").lower()
        if "pytest" in lower_cmd:
            from tools.ledgers.hook_helpers import emit_ledger_event
            # Extract -k keyword expression or explicit test paths (best effort)
            import shlex as _shlex
            try:
                tokens = _shlex.split(command_line)
            except ValueError:
                tokens = command_line.split()
            selected_paths = [t for t in tokens if t.endswith(".py") or "::" in t]
            emit_ledger_event(
                ledger="test_selection",
                event_kind="triage_selection",
                prediction={
                    "command": command_line,
                    "selected_paths": selected_paths,
                    "selection_rationale": "cli_explicit" if selected_paths else "full_suite",
                },
                repo_area=cwd or "",
            )
    except Exception:  # noqa: BLE001
        # guardian: allow-broad-except -- hook fail-soft contract
        pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
