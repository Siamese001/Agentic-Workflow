"""_apps_test_surface_check.py — apps_* test surface parity helper.

Pure logic. No I/O at import. Shared by:
  - ops_scripts/ci/check_apps_test_surface_parity.py  (CI gate TSP1)
  - tests/unit/cursor_scripts/test_apps_test_surface_check.py (unit tests)

Checks that every apps_<x> package has both canonical test surfaces:
  1. tests/unit/<app>/   — must contain __init__.py
  2. tests/<app>/        — must contain __init__.py

Also checks for forbidden misplaced directories:
  3. tests/integration/apps_<x>/  — forbidden (use tests/<app>/ instead)

Contract:
    check(repo_root: str | Path, apps: list[str] | None = None) -> list[Violation]
        repo_root — absolute path to repository root
        apps      — list of app names to check (default: ALL_APPS)
        returns   — list of Violation dataclasses (empty = clean)

    Violation fields:
        app       — app package name (e.g. "apps_rg")
        kind      — violation kind (see ViolationKind)
        path      — repo-relative path that is missing or forbidden
        message   — human-readable description

Bypass: callers honour APPS_TEST_SURFACE_BYPASS=1 themselves; this helper
is pure and does not read the environment.

Constitutional tie-in: plan apps-test-surface-consolidation-11acd9-v2 W6.
Rule: .claude/rules/apps-test-surface-taxonomy.md.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Sequence


ALL_APPS: tuple[str, ...] = (
    "apps_eval",
    "apps_exec",
    "apps_lic",
    "apps_qna",
    "apps_repo_brief",
    "apps_research",
    "apps_rfp",
    "apps_rg",
    "apps_shared",
    "apps_underwriting_ai",
)


class ViolationKind(str, Enum):
    MISSING_UNIT_DIR = "missing_unit_dir"
    MISSING_UNIT_INIT = "missing_unit_init"
    MISSING_INTG_DIR = "missing_intg_dir"
    MISSING_INTG_INIT = "missing_intg_init"
    FORBIDDEN_INTG_SUBDIR = "forbidden_intg_subdir"


@dataclass(frozen=True)
class Violation:
    app: str
    kind: ViolationKind
    path: str
    message: str


def check(
    repo_root: str | Path,
    apps: Sequence[str] | None = None,
) -> list[Violation]:
    """Return list of test-surface parity violations (empty = clean).

    Args:
        repo_root: absolute path to repository root.
        apps: app package names to check. Defaults to ALL_APPS.
    """
    root = Path(repo_root)
    app_list: Sequence[str] = apps if apps is not None else ALL_APPS
    violations: list[Violation] = []

    for app in app_list:
        # --- 1. tests/unit/<app>/ must exist and contain __init__.py ---
        unit_dir = root / "tests" / "unit" / app
        if not unit_dir.is_dir():
            violations.append(Violation(
                app=app,
                kind=ViolationKind.MISSING_UNIT_DIR,
                path=f"tests/unit/{app}/",
                message=(
                    f"{app}: missing unit test surface at tests/unit/{app}/. "
                    f"Create the directory with __init__.py."
                ),
            ))
        else:
            if not (unit_dir / "__init__.py").is_file():
                violations.append(Violation(
                    app=app,
                    kind=ViolationKind.MISSING_UNIT_INIT,
                    path=f"tests/unit/{app}/__init__.py",
                    message=(
                        f"{app}: tests/unit/{app}/__init__.py is missing. "
                        f"Add an empty __init__.py to make it a package."
                    ),
                ))

        # --- 2. tests/<app>/ must exist and contain __init__.py ---
        intg_dir = root / "tests" / app
        if not intg_dir.is_dir():
            violations.append(Violation(
                app=app,
                kind=ViolationKind.MISSING_INTG_DIR,
                path=f"tests/{app}/",
                message=(
                    f"{app}: missing integration test surface at tests/{app}/. "
                    f"Create the directory with __init__.py and conftest.py."
                ),
            ))
        else:
            if not (intg_dir / "__init__.py").is_file():
                violations.append(Violation(
                    app=app,
                    kind=ViolationKind.MISSING_INTG_INIT,
                    path=f"tests/{app}/__init__.py",
                    message=(
                        f"{app}: tests/{app}/__init__.py is missing. "
                        f"Add an empty __init__.py to make it a package."
                    ),
                ))

        # --- 3. tests/integration/apps_<x>/ must NOT exist ---
        forbidden_dir = root / "tests" / "integration" / app
        if forbidden_dir.is_dir():
            violations.append(Violation(
                app=app,
                kind=ViolationKind.FORBIDDEN_INTG_SUBDIR,
                path=f"tests/integration/{app}/",
                message=(
                    f"{app}: tests/integration/{app}/ is a forbidden location. "
                    f"Move files to tests/{app}/ and remove this directory."
                ),
            ))

    return violations
