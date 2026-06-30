"""W7 conformance gate — every ``apps_*`` package MUST be in APP_REGISTRY.

Enforces the GOVERNED-or-EXCEPTION binary documented in
``docs/architecture/adr/ADR-076-governed-or-exception-binary.md``:

    Every ``apps_*`` package on disk MUST appear in
    ``apps_shared.integrations.app_registry.APP_REGISTRY`` as either a
    ``GovernedAppEntry`` (fully adopted substrate) or a
    ``FormalExceptionEntry`` (permanent exception with reason code +
    compensating controls).

Failure modes the gate prevents
-------------------------------
1. New ``apps_<name>/`` package added without any registry entry.
2. ``APP_REGISTRY`` entry removed without removing the package.
3. Registry entry exists but is the legacy ``ExceptionAppEntry`` shape
   (deprecated — must upgrade to ``FormalExceptionEntry``).

Exit codes
----------
0 — every apps_* package is properly classified
2 — at least one apps_* package is missing or improperly classified

Usage
-----
    python ops_scripts/ci/check_app_registry_conformance.py

Wired into pre-commit and the contract-gate CI run.
"""

from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


# Documented infrastructure packages that are NOT subject to the
# GOVERNED-or-EXCEPTION binary because they ARE the substrate / shared
# library, not governed apps. Adding to this set requires an ADR.
INFRASTRUCTURE_PACKAGES: frozenset[str] = frozenset({
    "apps_shared",  # the substrate library itself (provides GovernedAppRunner)
})


def _discover_apps_packages() -> list[str]:
    """Return all ``apps_*`` directory names at the repo root that contain
    real Python source AND are NOT in ``INFRASTRUCTURE_PACKAGES``.

    Infrastructure packages (currently only ``apps_shared``) provide the
    governance substrate and library code consumed by governed apps; they
    are not themselves apps and have no ``APP_REGISTRY`` row.
    """
    apps: list[str] = []
    for entry in REPO_ROOT.iterdir():
        if not entry.is_dir():
            continue
        if not entry.name.startswith("apps_"):
            continue
        if entry.name in INFRASTRUCTURE_PACKAGES:
            continue
        # Must contain real Python source, not just metadata.
        has_python = any(entry.rglob("*.py"))
        if has_python:
            apps.append(entry.name)
    return sorted(apps)


def _check_conformance() -> tuple[bool, list[str]]:
    """Return ``(ok, error_lines)`` describing any conformance violations."""
    # Import lazily so this module imports cleanly even when the registry
    # is itself broken (in which case the import raises a more specific
    # ImportError that surfaces as a CI failure).
    from apps_shared.integrations.app_registry import (
        APP_REGISTRY,
        FormalExceptionEntry,
        GovernedAppEntry,
    )

    errors: list[str] = []

    discovered = _discover_apps_packages()
    registered = set(APP_REGISTRY.keys())

    # 1. Every apps_* on disk must have a registry entry.
    missing = [app for app in discovered if app not in registered]
    if missing:
        errors.append(
            "The following apps_* packages exist on disk but are NOT in "
            "APP_REGISTRY (must add as GovernedAppEntry or FormalExceptionEntry):"
        )
        for app in missing:
            errors.append(f"  - {app}")
        errors.append(
            "  See docs/architecture/adr/ADR-076-governed-or-exception-binary.md"
        )

    # 2. Every registry entry must reference a real on-disk package.
    orphaned = [name for name in registered if name not in discovered]
    if orphaned:
        errors.append(
            "The following APP_REGISTRY entries reference packages that do NOT "
            "exist on disk (must remove from registry or restore the package):"
        )
        for app in orphaned:
            errors.append(f"  - {app}")

    # 3. Every entry must be a valid type (GovernedAppEntry or FormalExceptionEntry).
    #    The legacy ExceptionAppEntry shape is deprecated by ADR-076.
    for name, entry in APP_REGISTRY.items():
        if not isinstance(entry, (GovernedAppEntry, FormalExceptionEntry)):
            errors.append(
                f"  - {name}: registry entry is {type(entry).__name__}; "
                f"must be GovernedAppEntry or FormalExceptionEntry "
                f"(legacy ExceptionAppEntry deprecated by ADR-076)"
            )

    return (not errors, errors)


def main() -> int:
    """CLI entrypoint: print verdict and return exit code."""
    print("[check_app_registry_conformance] scanning apps_* packages...")
    discovered = _discover_apps_packages()
    print(f"  found {len(discovered)} apps_* packages: {discovered}")

    ok, errors = _check_conformance()

    if ok:
        print("[check_app_registry_conformance] OK \u2014 GOVERNED-or-EXCEPTION binary holds.")
        return 0

    print("[check_app_registry_conformance] FAIL \u2014 ADR-076 violation:")
    for line in errors:
        print(line)
    return 2


if __name__ == "__main__":
    sys.exit(main())
