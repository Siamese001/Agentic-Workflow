#!/usr/bin/env python3
"""Assess whether full ``.windsurf/`` tree deletion is CI-safe (W1.D1 deferred scope).

Does NOT delete anything. Emits a JSON report of required mirror paths and exits:
  0 — readiness assessment complete (deletion still blocked if blockers listed)
  1 — fail-closed and blockers present

Deletion is blocked while constitutional gates still require:
  - .windsurf/hooks.json (check_windsurf_config_schema)
  - .windsurf/mcp_config.json (MCP parity)
  - artifacts/windsurf/ hook logs (dual-write transition)

Report: artifacts/cursor/windsurf_deletion_readiness.json
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT = REPO_ROOT / "artifacts" / "cursor" / "windsurf_deletion_readiness.json"

REQUIRED_PATHS = (
    ".windsurf/hooks.json",
    ".windsurf/mcp_config.json",
    ".windsurf/rules/README.md",
)


def main() -> int:
    blockers: list[str] = []
    for rel in REQUIRED_PATHS:
        if not (REPO_ROOT / rel).is_file():
            blockers.append(f"missing required mirror file: {rel}")

    blockers.append(
        "policy: full .windsurf/ deletion deferred — use mirror-only mode per governance_two_tier_closeout"
    )

    report = {
        "deletion_safe": False,
        "blockers": blockers,
        "recommendation": "Keep .windsurf/ as read-only mirror; active SSOT is .cursor/",
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))

    if os.environ.get("WINDSURF_DELETION_READINESS_FAIL_CLOSED") == "1" and blockers:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
