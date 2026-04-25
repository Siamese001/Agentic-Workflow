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
CONF04  All CANDIDATE apps (ExceptionAppEntry): exception_reason is non-empty (>= 20 chars)
CONF05  All CANDIDATE apps (ExceptionAppEntry): exception_category is one of the valid set
CONF06  All CANDIDATE apps (ExceptionAppEntry): target_phase is non-empty
CONF07  All CANDIDATE apps (ExceptionAppEntry): owner is non-empty
CONF08  No apps_* package is absent from APP_REGISTRY (silent bypass check)
EXCF01  All EXCEPTION-status apps: use FormalExceptionEntry (no ad hoc exceptions)
EXCF02  All formal exceptions: exception_reason_code is a valid ExceptionReasonCode
EXCF03  All formal exceptions: blocked_layers is non-empty
EXCF04  All formal exceptions: safe_layers is non-empty
EXCF05  All formal exceptions: compensating_controls has >= 2 entries
EXCF06  All formal exceptions: review_cadence is non-empty
EXCF07  All formal exceptions: partial_adoption_module is importable
EXCF08  All formal exceptions: partial_adoption_class.check_compensating_controls() all pass

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
_COMPENSATING_CONTROLS_MIN = 2


def _safe_import_module(module_name: str) -> tuple[object | None, bool, str]:
    try:
        return importlib.import_module(module_name), True, module_name
    except Exception as exc:  # review: CI gate must degrade to a recorded failure, not crash on import side effects  # guardian: allow-broad-exception -- offline tooling, reports failure
        return None, False, f"{type(exc).__name__}: {str(exc)[:80]}"


def _discover_apps_packages() -> list[str]:
    """Return all apps_* top-level package names found in the repo root."""
    try:
        return sorted(
            p.name
            for p in _REPO_ROOT.iterdir()
            if p.is_dir()
            and p.name.startswith("apps_")
            and p.name != "apps_shared"
            and (p / "__init__.py").exists()
        )
    except OSError as exc:
        raise RuntimeError(f"could not enumerate apps_* packages: {exc}") from exc


def _check_governed_entry(entry: "GovernedAppEntry") -> list[tuple[str, bool, str]]:  # type: ignore[name-defined]  # noqa: F821
    """Run CONF01–CONF03 for a single governed app entry."""
    results: list[tuple[str, bool, str]] = []

    # CONF01: runner module importable
    mod, conf01_pass, conf01_detail = _safe_import_module(entry.runner_module)
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
    """Run CONF04–CONF07 for a single CANDIDATE app entry (ExceptionAppEntry only)."""
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


def _check_formal_exception_entry(  # noqa: PLR0912
    entry: "FormalExceptionEntry",  # type: ignore[name-defined]  # noqa: F821
) -> list[tuple[str, bool, str]]:
    """Run EXCF01–EXCF08 for a single formal exception entry."""
    from apps_shared.integrations.app_registry import ExceptionReasonCode  # noqa: PLC0415

    results: list[tuple[str, bool, str]] = []

    # EXCF01 is checked at the registry level (no ad hoc exceptions)
    # Here we run EXCF02–EXCF08.

    # EXCF02: exception_reason_code is a valid ExceptionReasonCode
    try:
        valid_code = isinstance(entry.exception_reason_code, ExceptionReasonCode)
        excf02_pass = valid_code
        excf02_detail = repr(entry.exception_reason_code.value)
    except (AttributeError, ValueError) as exc:
        excf02_pass = False
        excf02_detail = str(exc)[:40]
    results.append((f"EXCF02 [{entry.app_name}] exception_reason_code valid", excf02_pass, excf02_detail))

    # EXCF03: blocked_layers non-empty
    excf03_pass = len(entry.blocked_layers) > 0
    results.append(
        (
            f"EXCF03 [{entry.app_name}] blocked_layers declared",
            excf03_pass,
            f"{len(entry.blocked_layers)} layers",
        )
    )

    # EXCF04: safe_layers non-empty
    excf04_pass = len(entry.safe_layers) > 0
    results.append(
        (
            f"EXCF04 [{entry.app_name}] safe_layers declared",
            excf04_pass,
            f"{len(entry.safe_layers)} surfaces",
        )
    )

    # EXCF05: compensating_controls >= 2
    excf05_pass = len(entry.compensating_controls) >= _COMPENSATING_CONTROLS_MIN
    results.append(
        (
            f"EXCF05 [{entry.app_name}] compensating_controls>={_COMPENSATING_CONTROLS_MIN}",
            excf05_pass,
            f"{len(entry.compensating_controls)} controls",
        )
    )

    # EXCF06: review_cadence non-empty
    excf06_pass = bool(entry.review_cadence.strip())
    results.append(
        (
            f"EXCF06 [{entry.app_name}] review_cadence set",
            excf06_pass,
            repr(entry.review_cadence),
        )
    )

    # EXCF07: partial_adoption_module importable
    mod, excf07_pass, excf07_detail = _safe_import_module(entry.partial_adoption_module)
    results.append(
        (f"EXCF07 [{entry.app_name}] partial_adoption_module importable", excf07_pass, excf07_detail)
    )

    # EXCF08: partial_adoption_class.check_compensating_controls() all pass
    if excf07_pass and mod is not None:
        try:
            cls = getattr(mod, entry.partial_adoption_class, None)
            if cls is None:
                excf08_pass = False
                excf08_detail = f"class {entry.partial_adoption_class!r} not found"
            else:
                handler = cls()
                cc_results = handler.check_compensating_controls()
                all_cc_pass = all(ok for _, ok, _ in cc_results)
                n_pass = sum(1 for _, ok, _ in cc_results if ok)
                excf08_pass = all_cc_pass
                excf08_detail = f"{n_pass}/{len(cc_results)} controls pass"
        except (AttributeError, TypeError, RuntimeError) as exc:
            excf08_pass = False
            excf08_detail = str(exc)[:50]
    else:
        excf08_pass = False
        excf08_detail = "skipped — module not importable"
    results.append(
        (
            f"EXCF08 [{entry.app_name}] compensating_controls verified",
            excf08_pass,
            excf08_detail,
        )
    )

    return results


def run_conformance_gate() -> bool:
    """Run all conformance checks. Returns True if all pass."""
    try:
        from apps_shared.integrations.app_registry import (  # noqa: PLC0415
            APP_REGISTRY,
            ExceptionAppEntry,
            FormalExceptionEntry,
            GovernanceStatus,
            GovernedAppEntry,
        )
    except Exception as exc:  # review: CI gate must report registry bootstrap failures as a failed gate  # guardian: allow-broad-exception -- offline tooling, reports failure
        print(
            f"[governed_app_conformance] FAIL: could not import app registry: {type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        return False

    try:
        discovered = _discover_apps_packages()
    except RuntimeError as exc:
        print(f"[governed_app_conformance] FAIL: {exc}", file=sys.stderr)
        return False
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

    # EXCF01: all EXCEPTION-status apps must use FormalExceptionEntry (no ad hoc exceptions)
    for entry in APP_REGISTRY.values():
        if entry.status == GovernanceStatus.EXCEPTION and not isinstance(entry, FormalExceptionEntry):
            all_checks.append(
                (
                    f"EXCF01 [{entry.app_name}] EXCEPTION must use FormalExceptionEntry",
                    False,
                    f"got {type(entry).__name__} — upgrade to FormalExceptionEntry",
                )
            )

    # Per-app checks
    for entry in APP_REGISTRY.values():
        if isinstance(entry, GovernedAppEntry):
            all_checks.extend(_check_governed_entry(entry))
        elif isinstance(entry, FormalExceptionEntry):
            all_checks.extend(_check_formal_exception_entry(entry))
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
        elif isinstance(entry, FormalExceptionEntry):
            detail = f"{entry.exception_reason_code.value} [formal]"
        else:
            detail = entry.exception_category
        print(f"  {name:<26} {entry.status.value:<12} {detail}")
    print(f"{'=' * 80}\n")

    return all_pass


if __name__ == "__main__":
    passed = run_conformance_gate()
    sys.exit(0 if passed else 1)
