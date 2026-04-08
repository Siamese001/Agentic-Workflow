#!/usr/bin/env python3
"""
pre_prompt_classifier.py — Windsurf pre_user_prompt advisory classifier (Phase 1.4).

Reads JSON payload from stdin. Payload field:
  tool_info.prompt  — the user's prompt text

Classifies the prompt as T0/T1/T2/T3 based on keyword heuristics and writes
tier tag + any warnings to stderr for Cascade context seeding.

Exits 0 for T0/T1. Exits 2 (BLOCK) for T2/T3 when ADG health is red (hard gate).
Fail policy: OPEN for infrastructure errors (probe missing/timeout), CLOSED for T2/T3 with confirmed red ADG.
Zero hardcoded paths.
"""

import json
import socket
import subprocess
import sys
from pathlib import Path

FAIL_POLICY = "closed_for_t2t3_adg"

REPO_ROOT = Path(__file__).resolve().parents[3]

T3_KEYWORDS = {
    "architecture",
    "architectural",
    "cross-layer",
    "refactor",
    "modularize",
    "wave",
    "governance",
    "tier",
    "migration",
    "extract",
    "consolidate",
    "redesign",
    "restructure",
    "multi-file",
    "blast radius",
}

T2_KEYWORDS = {
    "update",
    "modify",
    "fix",
    "debug",
    "add test",
    "change",
    "rename",
    "move",
    "edit",
    "patch",
    "implement",
    "create",
    "write",
}

T1_KEYWORDS = {
    "typo",
    "docstring",
    "comment",
    "whitespace",
    "format",
    "rename variable",
    "single line",
    "one line",
    "trivial",
}

T0_KEYWORDS = {
    "explain",
    "what is",
    "how does",
    "describe",
    "list",
    "show me",
    "review",
    "summarize",
    "tell me",
    "what are",
}


def classify_tier(prompt: str) -> str:
    lower = prompt.lower()

    t3_hits = sum(1 for kw in T3_KEYWORDS if kw in lower)
    t2_hits = sum(1 for kw in T2_KEYWORDS if kw in lower)
    t1_hits = sum(1 for kw in T1_KEYWORDS if kw in lower)
    t0_hits = sum(1 for kw in T0_KEYWORDS if kw in lower)

    if t3_hits >= 1:
        return "T3"
    if t2_hits >= 2:
        return "T2"
    if t1_hits >= 1:
        return "T1"
    if t0_hits >= 1:
        return "T0"
    if t2_hits >= 1:
        return "T2"
    return "T1"


def check_plan_exists(tier: str) -> bool:
    """Return True if a plan file exists in .windsurf/plans/ for T2/T3."""
    if tier not in ("T2", "T3"):
        return True
    plans_dir = REPO_ROOT / ".windsurf" / "plans"
    if not plans_dir.exists():
        return False
    return any(plans_dir.glob("*.md"))


def check_redis_down() -> bool:
    """
    Return True if Redis is not reachable on localhost:6379.
    Fail-open: any socket error other than connection refused returns False.
    """
    try:
        with socket.create_connection(("localhost", 6379), timeout=2):
            return False  # connected — Redis is up
    except ConnectionRefusedError:
        return True  # Redis is down
    except OSError:
        return False  # fail-open: network unavailable, don't block


def check_adg_health_red(repo_root: Path) -> bool:
    """
    Return True if the adg_sqlite MCP server fails a real liveness probe.

    Invokes mcp_health_check.py --server adg_sqlite --json with a 5s timeout.
    Fail-open: any infrastructure error (timeout, missing script, etc.) returns
    False so the gate does not block on probe unavailability.
    """
    probe_script = repo_root / "ops_scripts" / "ci" / "mcp_health_check.py"
    if not probe_script.exists():
        return False  # fail-open: no probe script available

    try:
        result = subprocess.run(
            [sys.executable, str(probe_script), "--server", "adg_sqlite", "--json"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
            cwd=str(repo_root),
        )
    except (subprocess.TimeoutExpired, OSError):
        return False  # fail-open: probe could not run

    if result.returncode == 2:
        return False  # config error — fail-open

    try:
        # JSON block may be preceded by human-readable lines; find the first '{'
        stdout = result.stdout
        json_start = stdout.find("{")
        if json_start < 0:
            return False  # no JSON — fail-open
        data = json.loads(stdout[json_start:])
        servers = data.get("servers", [])
        for srv in servers:
            if srv.get("name") == "adg_sqlite":
                return bool(srv.get("status") != "ok")
        return False  # server not in output — fail-open
    except (json.JSONDecodeError, KeyError):
        return False  # parse error — fail-open


def main() -> int:
    raw = sys.stdin.read()
    if not raw.strip():
        return 0

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return 0

    tool_info = payload.get("tool_info", payload)
    prompt = tool_info.get("user_prompt", "") or tool_info.get("prompt", "")

    if not prompt:
        return 0

    tier = classify_tier(prompt)
    print(f"[pre_prompt_classifier] Tier: {tier}", file=sys.stderr)

    if tier in ("T2", "T3"):
        if not check_plan_exists(tier):
            print(
                f"[pre_prompt_classifier] WARNING: {tier} prompt detected but no plan file found "
                "in .windsurf/plans/ — consider creating a plan per constitutional §10.",
                file=sys.stderr,
            )
        if check_adg_health_red(REPO_ROOT):
            print(
                f"[pre_prompt_classifier] BLOCKED: {tier} prompt detected but adg_sqlite MCP is red. "
                "Run mcp1_adg_health and /mcp-failure-rca before proceeding (constitutional §13). "
                "ADG + Redis health check is MANDATORY before any T2/T3 refactoring.",
                file=sys.stderr,
            )
            return 2
        if check_redis_down():
            print(
                f"[pre_prompt_classifier] BLOCKED: {tier} prompt detected but Redis is not reachable "
                "on localhost:6379. Start Redis before proceeding (constitutional §13). "
                "ADG + Redis health check is MANDATORY before any T2/T3 refactoring.",
                file=sys.stderr,
            )
            return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
