"""
Governed-App Conformance Gate.

Enforces the repo-wide governed-app standard defined in:
  docs/architecture/governed-app-contract.md
  apps_shared/integrations/app_registry.py

Checks
------
CONF01  All governed apps: runner module is importable
CONF02  All governed apps: runner class is a GovernedAppRunner subclass
CONF03  All governed apps: capability_token is non-empty and versioned (contains ".")
CONF04  All exception/candidate apps: exception_reason is non-empty (>= 20 chars)
CONF05  All exception/candidate apps: exception_category is one of the valid set
CONF06  All exception/candidate apps: target_phase is non-empty
CONF07  All exception/candidate apps: owner is non-empty
CONF08  No apps_* package is absent from APP_REGISTRY (silent bypass check)

Exit 0 = all checks pass.
Exit 1 = one or more checks fail (table printed to stdout).

Usage:
    python ops_scripts/ci/check_governed_app_conformance.py
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

# Ensure repo root is on the path
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

PASS_MARK = "PASS"
FAIL_MARK = "FAIL"

_VALID_EXCEPTION_CATEGORIES = frozenset({"pending_migration", "circular_dependency", "regulatory_domain"})

_EXCEPTION_REASON_MIN_LEN = 20


def _discover_apps_packages() -> list[str]:
    """Return all apps_* top-level package names found in the repo root."""
    return sorted(
        p.name
        for p in _REPO_ROOT.iterdir()
        if p.is_dir()
        and p.name.startswith("apps_")
        and p.name != "apps_shared"
        and (p / "__init__.py").exists()
    )


def _check_governed_entry(entry: "GovernedAppEntry") -> list[tuple[str, bool, str]]:  # type: ignore[name-defined]  # noqa: F821
    """Run CONF01–CONF03 for a single governed app entry."""
    results: list[tuple[str, bool, str]] = []

    # CONF01: runner module importable
    try:
        mod = importlib.import_module(entry.runner_module)
        conf01_pass = True
        conf01_detail = entry.runner_module
    except ImportError as exc:
        mod = None
        conf01_pass = False
        conf01_detail = str(exc)[:60]
    results.append((f"CONF01 [{entry.app_name}] runner module importable", conf01_pass, conf01_detail))

    # CONF02: runner class is GovernedAppRunner subclass
    if conf01_pass and mod is not None:
        try:
            from apps_shared.integrations.governed_app_runner import GovernedAppRunner  # noqa: PLC0415

            cls = getattr(mod, entry.runner_class, None)
            if cls is None:
                conf02_pass = False
                conf02_detail = f"class {entry.runner_class!r} not found in module"
            elif not (isinstance(cls, type) and issubclass(cls, GovernedAppRunner)):
                conf02_pass = False
                conf02_detail = f"{entry.runner_class} does not subclass GovernedAppRunner"
            else:
                conf02_pass = True
                conf02_detail = f"{entry.runner_class} -> {cls.__mro__[1].__name__}"
        except (ImportError, AttributeError) as exc:
            conf02_pass = False
            conf02_detail = str(exc)[:60]
    else:
        conf02_pass = False
        conf02_detail = "skipped — module not importable"
    results.append(
        (f"CONF02 [{entry.app_name}] runner is GovernedAppRunner subclass", conf02_pass, conf02_detail)
    )

    # CONF03: capability_token is non-empty and versioned
    token = entry.capability_token.strip()
    conf03_pass = bool(token) and "." in token
    results.append(
        (
            f"CONF03 [{entry.app_name}] capability_token versioned",
            conf03_pass,
            repr(token[:40]) if token else "empty",
        )
    )

    return results


def _check_exception_entry(entry: "ExceptionAppEntry") -> list[tuple[str, bool, str]]:  # type: ignore[name-defined]  # noqa: F821
    """Run CONF04–CONF07 for a single exception/candidate app entry."""
    results: list[tuple[str, bool, str]] = []

    # CONF04: exception_reason >= 20 chars
    reason = entry.exception_reason.strip()
    conf04_pass = len(reason) >= _EXCEPTION_REASON_MIN_LEN
    results.append(
        (
            f"CONF04 [{entry.app_name}] exception_reason length>={_EXCEPTION_REASON_MIN_LEN}",
            conf04_pass,
            f"len={len(reason)}",
        )
    )

    # CONF05: exception_category is valid
    conf05_pass = entry.exception_category in _VALID_EXCEPTION_CATEGORIES
    results.append(
        (
            f"CONF05 [{entry.app_name}] exception_category valid",
            conf05_pass,
            repr(entry.exception_category),
        )
    )

    # CONF06: target_phase non-empty
    conf06_pass = bool(entry.target_phase.strip())
    results.append(
        (
            f"CONF06 [{entry.app_name}] target_phase set",
            conf06_pass,
            repr(entry.target_phase[:30]),
        )
    )

    # CONF07: owner non-empty
    conf07_pass = bool(entry.owner.strip())
    results.append(
        (
            f"CONF07 [{entry.app_name}] owner set",
            conf07_pass,
            repr(entry.owner[:30]),
        )
    )

    return results


def run_conformance_gate() -> bool:
    """Run all conformance checks. Returns True if all pass."""
    from apps_shared.integrations.app_registry import (  # noqa: PLC0415
        APP_REGISTRY,
        ExceptionAppEntry,
        GovernedAppEntry,
    )

    discovered = _discover_apps_packages()
    all_checks: list[tuple[str, bool, str]] = []

    # CONF08: no apps_* absent from registry
    for pkg in discovered:
        in_registry = pkg in APP_REGISTRY
        all_checks.append(
            (
                f"CONF08 [{pkg}] registered in APP_REGISTRY",
                in_registry,
                "present" if in_registry else "MISSING — add entry or exception",
            )
        )

    # Per-app checks
    for entry in APP_REGISTRY.values():
        if isinstance(entry, GovernedAppEntry):
            all_checks.extend(_check_governed_entry(entry))
        elif isinstance(entry, ExceptionAppEntry):
            all_checks.extend(_check_exception_entry(entry))

    # Print table
    print(f"\n{'=' * 80}")
    print("  GOVERNED-APP CONFORMANCE GATE")
    print("  Contract: docs/architecture/governed-app-contract.md")
    print("  Registry: apps_shared/integrations/app_registry.py")
    print(f"{'=' * 80}")
    print(f"\n  {'Check':<56} {'Status':>6}  {'Detail'}")
    print(f"  {'-' * 56} {'-' * 6}  {'-' * 24}")
    for label, ok, detail in all_checks:
        mark = PASS_MARK if ok else FAIL_MARK
        print(f"  {label:<56} {mark}  {detail}")

    total = len(all_checks)
    n_passed = sum(1 for _, ok, _ in all_checks if ok)
    n_failed = total - n_passed
    all_pass = n_failed == 0

    verdict = PASS_MARK if all_pass else FAIL_MARK
    print(f"\n  VERDICT: {verdict}  {n_passed}/{total} checks pass  |  {n_failed} failed")

    # Summary table
    print(f"\n{'=' * 80}")
    print("  REGISTRY SUMMARY")
    print(f"  {'App':<26} {'Status':<12} {'Category / Runner'}")
    print(f"  {'-' * 26} {'-' * 12} {'-' * 30}")
    for name, entry in sorted(APP_REGISTRY.items()):
        if isinstance(entry, GovernedAppEntry):
            detail = entry.runner_class
        else:
            detail = entry.exception_category
        print(f"  {name:<26} {entry.status.value:<12} {detail}")
    print(f"{'=' * 80}\n")

    return all_pass


if __name__ == "__main__":
    passed = run_conformance_gate()
    sys.exit(0 if passed else 1)
