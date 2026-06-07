#!/usr/bin/env python3
"""Advisory gate: deprecated Windsurf surface health.

Checks:
  - .cursor/ remains the active governance SSOT
  - docs/archive/windsurf/legacy-tree/ is not required as a mirror peer
  - compatibility copies, when present, live under .cursor/windsurf_compat/

Exit 0 advisory by default. Fail-closed: CURSOR_MIRROR_HEALTH_FAIL_CLOSED=1.
Bypass: CURSOR_MIRROR_HEALTH_BYPASS=1.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CURSOR_PLANS = REPO_ROOT / ".cursor" / "plans"
CURSOR_RULES = REPO_ROOT / ".cursor" / "rules"
CURSOR_HOOKS = REPO_ROOT / ".cursor" / "hooks.json"
CURSOR_MCP = REPO_ROOT / ".cursor" / "mcp.json"
WINDSURF_COMPAT = REPO_ROOT / ".cursor" / "windsurf_compat"


def main() -> int:
    if os.environ.get("CURSOR_MIRROR_HEALTH_BYPASS") == "1":
        print("[cursor_mirror_health] BYPASS")
        return 0

    fail_closed = os.environ.get("CURSOR_MIRROR_HEALTH_FAIL_CLOSED") == "1"
    violations: list[str] = []

    required = (
        (CURSOR_PLANS, ".cursor/plans"),
        (CURSOR_RULES, ".cursor/rules"),
        (CURSOR_HOOKS, ".cursor/hooks.json"),
        (CURSOR_MCP, ".cursor/mcp.json"),
    )
    for path, label in required:
        if not path.exists():
            violations.append(f"missing Cursor SSOT path: {label}")

    if WINDSURF_COMPAT.exists():
        compat_files = [p for p in WINDSURF_COMPAT.rglob("*") if p.is_file()]
        print(
            f"[cursor_mirror_health] info: {len(compat_files)} deprecated compatibility file(s) "
            "under .cursor/windsurf_compat",
            file=sys.stderr,
        )

    if violations:
        for v in violations:
            print(f"[cursor_mirror_health] WARN: {v}", file=sys.stderr)
        return 1 if fail_closed else 0

    print("[cursor_mirror_health] OK — Cursor governance SSOT present; Windsurf mirror not required")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
