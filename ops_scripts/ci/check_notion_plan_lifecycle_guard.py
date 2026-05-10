#!/usr/bin/env python3
"""
check_notion_plan_lifecycle_guard.py — CI gate NP-GUARD.

Validates that the wave-lifecycle Completed guard is present in:

1. ``tools/windsurf/wave_execution_state.py`` — ``_current_notion_status``
   function and the ``status_already_completed`` guard in ``_cmd_start``.

2. ``tools/notion/_wave_lifecycle_helpers.py`` — ``status_completed_guard:noop``
   branch in ``patch_for_marker``.

These guards prevent a retrospective/completed plan from having its Notion
status flipped back to "In Progress" when ``wave_execution_state.py start``
is called inadvertently.

Plan: notion-plan-status-hardening-e5f3a1 (W3.P1).

Fail-closed: NP_LIFECYCLE_GUARD_FAIL_CLOSED=1.
Bypass:      NP_LIFECYCLE_GUARD_BYPASS=1 (logs warning, exits 0).
Report:      artifacts/ci/notion_plan_lifecycle_guard.json
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = REPO_ROOT / "artifacts" / "ci" / "notion_plan_lifecycle_guard.json"

WAVE_EXEC_PATH = REPO_ROOT / "tools" / "windsurf" / "wave_execution_state.py"
HELPERS_PATH = REPO_ROOT / "tools" / "notion" / "_wave_lifecycle_helpers.py"

# Patterns that must be present in wave_execution_state.py
WAVE_EXEC_REQUIRED = [
    "_current_notion_status",
    "status_already_completed",
]

# Patterns that must be present in _wave_lifecycle_helpers.py
HELPERS_REQUIRED = [
    "status_completed_guard:noop",
    "STATUS_COMPLETED",
]

Findings = list[dict[str, str]]


def _check_file(path: Path, required_patterns: list[str]) -> Findings:
    findings: Findings = []
    if not path.exists():
        findings.append(
            {
                "severity": "ERROR",
                "file": str(path.relative_to(REPO_ROOT)),
                "check": "file_exists",
                "detail": f"File not found: {path}",
            }
        )
        return findings
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        findings.append(
            {
                "severity": "ERROR",
                "file": str(path.relative_to(REPO_ROOT)),
                "check": "file_readable",
                "detail": str(exc),
            }
        )
        return findings
    for pattern in required_patterns:
        if pattern not in text:
            findings.append(
                {
                    "severity": "ERROR",
                    "file": str(path.relative_to(REPO_ROOT)),
                    "check": "pattern_present",
                    "detail": f"Required pattern not found: {pattern!r}",
                }
            )
    return findings


def main() -> int:
    if os.environ.get("NP_LIFECYCLE_GUARD_BYPASS") == "1":
        print(
            "[NP-GUARD] NP_LIFECYCLE_GUARD_BYPASS=1 — skipping check",
            file=sys.stderr,
        )
        return 0

    findings: Findings = []
    findings.extend(_check_file(WAVE_EXEC_PATH, WAVE_EXEC_REQUIRED))
    findings.extend(_check_file(HELPERS_PATH, HELPERS_REQUIRED))

    errors = [f for f in findings if f["severity"] == "ERROR"]
    warnings = [f for f in findings if f["severity"] == "WARN"]

    report = {
        "gate": "NP-GUARD",
        "description": "Notion plan lifecycle Completed guard presence check",
        "errors": len(errors),
        "warnings": len(warnings),
        "findings": findings,
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    for f in findings:
        tag = f["severity"]
        print(f"[NP-GUARD] {tag} {f['file']}: {f['detail']}")

    if errors:
        print(f"[NP-GUARD] {len(errors)} ERROR(s) — Completed guard invariants not satisfied.")
        fail_closed = os.environ.get("NP_LIFECYCLE_GUARD_FAIL_CLOSED") == "1"
        if fail_closed:
            print("[NP-GUARD] NP_LIFECYCLE_GUARD_FAIL_CLOSED=1 — exiting 1", file=sys.stderr)
            return 1
        print("[NP-GUARD] Advisory mode — exiting 0 (set NP_LIFECYCLE_GUARD_FAIL_CLOSED=1 to enforce)")
        return 0

    print(f"[NP-GUARD] OK — {len(findings)} finding(s); 0 errors.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
