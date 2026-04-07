#!/usr/bin/env python3
"""
pre_prompt_classifier.py — Windsurf pre_user_prompt advisory classifier (Phase 1.4).

Reads JSON payload from stdin. Payload field:
  tool_info.prompt  — the user's prompt text

Classifies the prompt as T0/T1/T2/T3 based on keyword heuristics and writes
tier tag + any warnings to stderr for Cascade context seeding.

ALWAYS exits 0 — this is a classifier, not a gate. It never blocks prompts.
Fail policy: OPEN — any error → exit 0 silently.
Zero hardcoded paths.
"""

import json
import sys
from pathlib import Path

FAIL_POLICY = "open"

REPO_ROOT = Path(__file__).resolve().parents[3]

T3_KEYWORDS = {
    "architecture", "architectural", "cross-layer", "refactor", "modularize",
    "wave", "governance", "tier", "migration", "extract", "consolidate",
    "redesign", "restructure", "multi-file", "blast radius",
}

T2_KEYWORDS = {
    "update", "modify", "fix", "debug", "add test", "change", "rename",
    "move", "edit", "patch", "implement", "create", "write",
}

T1_KEYWORDS = {
    "typo", "docstring", "comment", "whitespace", "format", "rename variable",
    "single line", "one line", "trivial",
}

T0_KEYWORDS = {
    "explain", "what is", "how does", "describe", "list", "show me",
    "review", "summarize", "tell me", "what are",
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


def check_adg_health_stale(repo_root: Path) -> bool:
    """Return True if ADG snapshots are absent (health unknown/stale proxy)."""
    adg_dir = repo_root / "artifacts" / "adg"
    if not adg_dir.exists():
        return True
    return not any(adg_dir.glob("adg_snapshot_*.json"))


def main() -> int:
    raw = sys.stdin.read()
    if not raw.strip():
        return 0

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return 0

    tool_info = payload.get("tool_info", payload)
    prompt = tool_info.get("prompt", "")

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
        if check_adg_health_stale(REPO_ROOT):
            print(
                f"[pre_prompt_classifier] WARNING: {tier} prompt detected but no ADG snapshot found — "
                "run mcp1_adg_health per constitutional §13.",
                file=sys.stderr,
            )

    return 0


if __name__ == "__main__":
    sys.exit(main())
