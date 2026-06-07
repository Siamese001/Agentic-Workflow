#!/usr/bin/env python3
"""post_cascade_mcp_hygiene_audit.py — Unified MCP Hygiene audit hook (W2.P5)."""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
LOG_PATHS = {
    "serialization": REPO_ROOT / "artifacts" / "windsurf" / "mcp_serialization_violations.jsonl",
    "preflight": REPO_ROOT / "artifacts" / "windsurf" / "mcp_preflight_violations.jsonl",
    "orphan_reap": REPO_ROOT / "artifacts" / "windsurf" / "mcp_orphan_reap.jsonl",
}
MAX_RESPONSE_BYTES = 512 * 1024

BYPASS_VARS = {
    "serialization": "MCP_SERIALIZATION_AUDIT_BYPASS",
    "preflight": "MCP_PREFLIGHT_AUDIT_BYPASS",
    "orphan_reap": "MCP_ORPHAN_REAP_BYPASS",
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


def cmd_serialization(args) -> int:
    """MCP serialization audit - remote MCP calls must be isolated."""
    if os.environ.get(BYPASS_VARS["serialization"]) == "1" or os.environ.get("MCP_HYGIENE_BYPASS") == "1":
        return 0
    text = _read_stdin()
    if not text:
        return 0
    # Check for multiple remote MCP calls in same block (simplified detection)
    remote_mcps = ["notion", "tavily", "deepwiki", "context7", "GitKraken"]
    violations = []
    for mcp in remote_mcps:
        if text.count(f"{mcp}_") > 1:
            violations.append(mcp)
    if violations:
        _append_log(LOG_PATHS["serialization"], {"ts": _now_iso(), "violations": violations, "type": "serialization"})
        print(f"[mcp_hygiene serialization] Violation: {violations}", file=sys.stderr)
    return 0


def cmd_preflight(args) -> int:
    """MCP preflight audit - check before MCP operations."""
    if os.environ.get(BYPASS_VARS["preflight"]) == "1" or os.environ.get("MCP_HYGIENE_BYPASS") == "1":
        return 0
    _append_log(LOG_PATHS["preflight"], {"ts": _now_iso(), "event": "preflight_checked", "stub": True})
    return 0


def cmd_orphan_reap(args) -> int:
    """Reap orphan MCP server processes."""
    if os.environ.get(BYPASS_VARS["orphan_reap"]) == "1" or os.environ.get("MCP_HYGIENE_BYPASS") == "1":
        return 0
    detector = REPO_ROOT / "tools" / "debug" / "check_orphan_mcp_processes.py"
    if detector.exists():
        try:
            result = subprocess.run(
                [sys.executable, str(detector), "--kill"],
                capture_output=True,
                text=True,
                timeout=30
            )
            _append_log(LOG_PATHS["orphan_reap"], {"ts": _now_iso(), "exit_code": result.returncode, "output": result.stdout[:500]})
        except Exception as e:
            _append_log(LOG_PATHS["orphan_reap"], {"ts": _now_iso(), "error": str(e)})
    return 0


def _cmd_run_all(args) -> int:
    for subcmd in ["serialization", "preflight", "orphan_reap"]:
        try:
            globals()[f"cmd_{subcmd}"](args)
        except Exception as e:
            print(f"[mcp_hygiene] {subcmd} error: {e}", file=sys.stderr)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="post_cascade_mcp_hygiene_audit")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("serialization", help="MCP serialization audit")
    sub.add_parser("preflight", help="MCP preflight audit")
    sub.add_parser("orphan_reap", help="Orphan MCP process reaping")
    sub.add_parser("run_all", help="Run all audits")
    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        return 0
    dispatch = {"serialization": cmd_serialization, "preflight": cmd_preflight, "orphan_reap": cmd_orphan_reap, "run_all": _cmd_run_all}
    return dispatch.get(args.cmd, lambda _: 0)(args)


if __name__ == "__main__":
    sys.exit(main())
