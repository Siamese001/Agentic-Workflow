#!/usr/bin/env python3
"""post_cursor_agent_resource_budget_audit.py — Unified Resource Budget audit hook (W2.P4)."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
VIOLATIONS_LOGS = {
    "grep": REPO_ROOT / "artifacts" / "windsurf" / "grep_budget_violations.jsonl",
    "read": REPO_ROOT / "artifacts" / "windsurf" / "read_budget_violations.jsonl",
    "token": REPO_ROOT / "artifacts" / "windsurf" / "token_telemetry.jsonl",
}
SOFT_CAPS = {"grep": 3, "read": 10}
MAX_RESPONSE_BYTES = 2 * 1024 * 1024

BYPASS_VARS = {
    "grep": "GREP_BUDGET_BYPASS",
    "read": "READ_BUDGET_BYPASS",
    "token": "TOKEN_TELEMETRY_BYPASS",
}


def _read_stdin() -> str:
    try:
        return sys.stdin.read(MAX_RESPONSE_BYTES)
    except Exception:
        return ""


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _append_log(path: Path, row: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def cmd_grep(args) -> int:
    if os.environ.get(BYPASS_VARS["grep"]) == "1" or os.environ.get("RESOURCE_BUDGET_BYPASS") == "1":
        return 0
    text = _read_stdin()
    if not text:
        return 0
    grep_count = len(re.findall(r'<invoke[^>]*name="[^"]*(?:grep_search|code_search)[^"]*"', text, re.IGNORECASE))
    if grep_count > SOFT_CAPS["grep"]:
        _append_log(VIOLATIONS_LOGS["grep"], {"ts": _now_iso(), "count": grep_count, "cap": SOFT_CAPS["grep"], "violation": True})
        print(f"[resource_budget grep] Violation: {grep_count} > {SOFT_CAPS['grep']}", file=sys.stderr)
    return 0


def cmd_read(args) -> int:
    if os.environ.get(BYPASS_VARS["read"]) == "1" or os.environ.get("RESOURCE_BUDGET_BYPASS") == "1":
        return 0
    text = _read_stdin()
    if not text:
        return 0
    read_count = len(re.findall(r'<invoke[^>]*name="[^"]*(?:read_file|read_text_file|read_multiple_files|read_notebook)[^"]*"', text, re.IGNORECASE))
    if read_count > SOFT_CAPS["read"]:
        _append_log(VIOLATIONS_LOGS["read"], {"ts": _now_iso(), "count": read_count, "cap": SOFT_CAPS["read"], "violation": True})
        print(f"[resource_budget read] Violation: {read_count} > {SOFT_CAPS['read']}", file=sys.stderr)
    return 0


def cmd_token(args) -> int:
    if os.environ.get(BYPASS_VARS["token"]) == "1" or os.environ.get("RESOURCE_BUDGET_BYPASS") == "1":
        return 0
    _append_log(VIOLATIONS_LOGS["token"], {"ts": _now_iso(), "event": "token_audit", "stub": True})
    return 0


def _cmd_run_all(args) -> int:
    for subcmd in ["grep", "read", "token"]:
        try:
            globals()[f"cmd_{subcmd}"](args)
        except Exception as e:
            print(f"[resource_budget] {subcmd} error: {e}", file=sys.stderr)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="post_cursor_agent_resource_budget_audit")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("grep", help="Grep budget audit")
    sub.add_parser("read", help="Read budget audit")
    sub.add_parser("token", help="Token telemetry")
    sub.add_parser("run_all", help="Run all audits")
    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        return 0
    dispatch = {"grep": cmd_grep, "read": cmd_read, "token": cmd_token, "run_all": _cmd_run_all}
    return dispatch.get(args.cmd, lambda _: 0)(args)


if __name__ == "__main__":
    sys.exit(main())
