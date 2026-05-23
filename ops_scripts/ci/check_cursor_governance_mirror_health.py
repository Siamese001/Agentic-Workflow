#!/usr/bin/env python3
"""Advisory gate: .windsurf/ mirror health (replaces removed T7.7 / check_windsurf_governance).

Checks:
  - .windsurf/rules/README.md declares read-only mirror policy
  - .windsurf/hooks.json and mcp_config.json exist (constitutional §27 peers)
  - No new top-level plan files under .windsurf/plans/ outside _archive paths on disk

Exit 0 advisory by default. Fail-closed: CURSOR_MIRROR_HEALTH_FAIL_CLOSED=1.
Bypass: CURSOR_MIRROR_HEALTH_BYPASS=1.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WINDSURF_RULES_README = REPO_ROOT / ".windsurf" / "rules" / "README.md"
WINDSURF_HOOKS = REPO_ROOT / ".windsurf" / "hooks.json"
WINDSURF_MCP = REPO_ROOT / ".windsurf" / "mcp_config.json"
WINDSURF_PLANS = REPO_ROOT / ".windsurf" / "plans"
CURSOR_PLANS = REPO_ROOT / ".cursor" / "plans"


def main() -> int:
    if os.environ.get("CURSOR_MIRROR_HEALTH_BYPASS") == "1":
        print("[cursor_mirror_health] BYPASS")
        return 0

    fail_closed = os.environ.get("CURSOR_MIRROR_HEALTH_FAIL_CLOSED") == "1"
    violations: list[str] = []

    if not WINDSURF_RULES_README.is_file():
        violations.append("missing .windsurf/rules/README.md mirror policy file")
    else:
        text = WINDSURF_RULES_README.read_text(encoding="utf-8", errors="replace")
        if "read-only" not in text.lower() and "do not author" not in text.lower():
            violations.append(".windsurf/rules/README.md missing read-only mirror declaration")

    for path, label in ((WINDSURF_HOOKS, "hooks.json"), (WINDSURF_MCP, "mcp_config.json")):
        if not path.is_file():
            violations.append(f"missing .windsurf/{label}")

    if WINDSURF_PLANS.is_dir() and CURSOR_PLANS.is_dir():
        legacy = CURSOR_PLANS / "_archive" / "windsurf_legacy"
        ws_top = {p.name for p in WINDSURF_PLANS.glob("*.md") if p.is_file()}
        cur_top = {p.name for p in CURSOR_PLANS.glob("*.md") if p.is_file()}
        legacy_top = {p.name for p in legacy.glob("*.md") if p.is_file()} if legacy.is_dir() else set()
        unmirrored = sorted(ws_top - cur_top - legacy_top)
        if unmirrored:
            print(
                f"[cursor_mirror_health] info: {len(unmirrored)} windsurf-only top-level plans "
                f"(legacy archive covers {len(legacy_top)})",
                file=sys.stderr,
            )

    if violations:
        for v in violations:
            print(f"[cursor_mirror_health] WARN: {v}", file=sys.stderr)
        return 1 if fail_closed else 0

    print("[cursor_mirror_health] OK — mirror policy and config peers present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
