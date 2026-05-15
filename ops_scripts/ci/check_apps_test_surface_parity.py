"""TSP1 — apps_* test surface parity CI gate.

Verifies that every ``apps_<x>`` package has both canonical test surfaces:
  1. ``tests/unit/<app>/``  — unit test surface (must have __init__.py)
  2. ``tests/<app>/``       — integration test surface (must have __init__.py)

Also flags forbidden misplaced directories:
  3. ``tests/integration/apps_<x>/``  — FORBIDDEN (use ``tests/<app>/`` instead)

Exit codes:
  0 — no violations
  1 — violations found

Bypass: set env ``APPS_TEST_SURFACE_BYPASS=1`` to emit a WARNING and exit 0.
Fail-closed: set env ``APPS_TEST_SURFACE_FAIL_CLOSED=1`` to exit 1 on any violation
             (same as default; exists for parity with other gate patterns).

Plan: apps-test-surface-consolidation-11acd9-v2 W6.3.
Rule: .cursor/rules/apps-test-surface-taxonomy.md.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# Ensure the windsurf scripts helper is importable when run as a script
_WINDSURF_SCRIPTS = REPO_ROOT / ".windsurf" / "scripts"
if str(_WINDSURF_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_WINDSURF_SCRIPTS))

from _apps_test_surface_check import ALL_APPS, ViolationKind, check  # noqa: E402


def main() -> int:
    if os.environ.get("APPS_TEST_SURFACE_BYPASS") == "1":
        print(
            "WARNING: APPS_TEST_SURFACE_BYPASS=1 — skipping test surface parity check.",
            file=sys.stderr,
        )
        return 0

    violations = check(REPO_ROOT)

    if not violations:
        print(f"TSP1 test surface parity: OK — all {len(ALL_APPS)} apps have canonical surfaces")
        return 0

    # Group by kind for a clean summary
    missing_unit = [v for v in violations if v.kind in (ViolationKind.MISSING_UNIT_DIR, ViolationKind.MISSING_UNIT_INIT)]
    missing_intg = [v for v in violations if v.kind in (ViolationKind.MISSING_INTG_DIR, ViolationKind.MISSING_INTG_INIT)]
    forbidden = [v for v in violations if v.kind == ViolationKind.FORBIDDEN_INTG_SUBDIR]

    print(
        f"TSP1 test surface parity: FAIL — {len(violations)} violation(s)",
        file=sys.stderr,
    )

    if missing_unit:
        print("\n[MISSING unit surface]", file=sys.stderr)
        for v in missing_unit:
            print(f"  - {v.message}", file=sys.stderr)

    if missing_intg:
        print("\n[MISSING integration surface]", file=sys.stderr)
        for v in missing_intg:
            print(f"  - {v.message}", file=sys.stderr)

    if forbidden:
        print("\n[FORBIDDEN misplaced directory]", file=sys.stderr)
        for v in forbidden:
            print(f"  - {v.message}", file=sys.stderr)

    print(
        "\nSee .cursor/rules/apps-test-surface-taxonomy.md for remediation.",
        file=sys.stderr,
    )
    print(
        "Bypass (not recommended): APPS_TEST_SURFACE_BYPASS=1",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
