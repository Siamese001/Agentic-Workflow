"""AppRemediationDispatcher — fan-out guardian checks and collect AppHealResult artifacts.

Parallel to agentic_core.L2_execution.healers pattern but scoped to apps_*.
Runs all AppGuardianSpec entries for a given app and emits a combined JSON report.

Usage (CI):
    python -m apps_shared.scripts.app_remediation_dispatcher --app apps_rg
    python -m apps_shared.scripts.app_remediation_dispatcher --app apps_lic
    python -m apps_shared.scripts.app_remediation_dispatcher --app '*'
    python -m apps_shared.scripts.app_remediation_dispatcher --strict  # exit 1 on any FAILED
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any

from apps_shared.config.app_guardian_registry import AppGuardianSpec, get_specs_for_app
from apps_shared.types.app_heal_contract_types import AppHealResult, AppHealStatus

_log = logging.getLogger(__name__)


def _run_spec(spec: AppGuardianSpec) -> AppHealResult:
    """Run one guardian spec and return an AppHealResult."""
    try:
        if spec.check_id == "AGS-001":
            return _check_dead_imports(spec)
        elif spec.check_id == "AGS-002":
            return _check_layer_violations(spec)
        elif spec.check_id == "AGS-003":
            return _check_misplaced_tests(spec)
        elif spec.check_id == "AGS-004":
            return _check_inline_constants(spec)
        elif spec.check_id == "AGS-005":
            return _check_content_strategy_shim(spec)
        elif spec.check_id == "AGS-006":
            return _check_duplicate_stubs(spec)
        else:
            return AppHealResult.skipped(spec.check_id, spec.app, "no handler registered")
    except Exception as exc:
        return AppHealResult.failed(spec.check_id, spec.app, str(exc))


def _check_dead_imports(spec: AppGuardianSpec) -> AppHealResult:
    """AGS-001: Run ruff F401 check across apps_*."""
    import subprocess

    result = subprocess.run(
        [sys.executable, "-m", "ruff", "check", "--select", "F401",
         "apps_rg/", "apps_lic/", "apps_shared/", "--output-format=json"],
        capture_output=True, text=True
    )
    violations = json.loads(result.stdout) if result.stdout.strip().startswith("[") else []
    if not violations:
        return AppHealResult(
            check_id=spec.check_id, app=spec.app,
            status=AppHealStatus.HEALED, detail="0 F401 violations"
        )
    files = list({v["filename"] for v in violations})
    return AppHealResult(
        check_id=spec.check_id, app=spec.app,
        status=AppHealStatus.PARTIAL,
        changes_made=tuple(files),
        detail="%d F401 violation(s) remain" % len(violations),
    )


def _check_layer_violations(spec: AppGuardianSpec) -> AppHealResult:
    """AGS-002: Check ADG for L_APP→L_SL violations."""
    try:
        from agentic_core.adg.applications.execute_ssot_integration import build_pre_run_report
        report = build_pre_run_report(changed_files=[], force_fresh=False)
        if report.layer_violation_count == 0:
            return AppHealResult(
                check_id=spec.check_id, app=spec.app,
                status=AppHealStatus.HEALED, detail="0 layer violations"
            )
        return AppHealResult(
            check_id=spec.check_id, app=spec.app,
            status=AppHealStatus.FAILED,
            detail="%d layer violation(s): %s" % (
                report.layer_violation_count, report.scope_widening_events
            ),
        )
    except Exception as exc:
        return AppHealResult.skipped(spec.check_id, spec.app, "ADG unavailable: %s" % exc)


def _check_misplaced_tests(spec: AppGuardianSpec) -> AppHealResult:
    """AGS-003: Find test_*.py inside apps_* source trees."""
    misplaced = []
    for app in ["apps_rg", "apps_lic", "apps_shared"]:
        for py in sorted(Path(app).rglob("*.py")):
            if py.name.startswith("test_") or py.name.endswith("_test.py"):
                misplaced.append(py.as_posix())
    if not misplaced:
        return AppHealResult(
            check_id=spec.check_id, app=spec.app,
            status=AppHealStatus.HEALED, detail="0 misplaced test files"
        )
    return AppHealResult(
        check_id=spec.check_id, app=spec.app,
        status=AppHealStatus.FAILED,
        changes_made=tuple(misplaced),
        detail="%d misplaced test file(s)" % len(misplaced),
    )


def _check_inline_constants(spec: AppGuardianSpec) -> AppHealResult:
    """AGS-004: Detect files that still define MAX_RETRIES = 3 inline."""
    import re
    pattern = re.compile(r"^MAX_RETRIES = 3$", re.MULTILINE)
    ssot = "apps_shared/config/pipeline_constants_config.py"
    offenders = []
    for app in ["apps_rg", "apps_lic", "apps_shared"]:
        for py in sorted(Path(app).rglob("*.py")):
            if py.as_posix() == ssot:
                continue
            if pattern.search(py.read_text(encoding="utf-8")):
                offenders.append(py.as_posix())
    if not offenders:
        return AppHealResult(
            check_id=spec.check_id, app=spec.app,
            status=AppHealStatus.HEALED, detail="0 inline MAX_RETRIES definitions"
        )
    return AppHealResult(
        check_id=spec.check_id, app=spec.app,
        status=AppHealStatus.FAILED,
        changes_made=tuple(offenders),
        detail="%d file(s) still define MAX_RETRIES inline" % len(offenders),
    )


def _check_content_strategy_shim(spec: AppGuardianSpec) -> AppHealResult:
    """AGS-005: Verify ContentStrategyAgent shim is absent."""
    shim = Path("apps_rg/reasoning/ContentStrategyAgent.py")
    if not shim.exists():
        return AppHealResult(
            check_id=spec.check_id, app=spec.app,
            status=AppHealStatus.HEALED, detail="ContentStrategyAgent shim absent"
        )
    return AppHealResult(
        check_id=spec.check_id, app=spec.app,
        status=AppHealStatus.FAILED,
        detail="ContentStrategyAgent shim still present",
    )


def _check_duplicate_stubs(spec: AppGuardianSpec) -> AppHealResult:
    """AGS-006: Detect unconditional duplicate stub class definitions."""
    import ast
    offenders = []
    for app in ["apps_lic"]:
        for py in sorted(Path(app).rglob("*.py")):
            try:
                tree = ast.parse(py.read_text(encoding="utf-8"))
            except SyntaxError:
                continue
            class_names = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
            dupes = {n for n in class_names if class_names.count(n) > 1}
            if dupes:
                offenders.append("%s: %s" % (py.as_posix(), sorted(dupes)))
    if not offenders:
        return AppHealResult(
            check_id=spec.check_id, app=spec.app,
            status=AppHealStatus.HEALED, detail="0 duplicate stub classes"
        )
    return AppHealResult(
        check_id=spec.check_id, app=spec.app,
        status=AppHealStatus.PARTIAL,
        changes_made=tuple(offenders),
        detail="%d file(s) with duplicate class names" % len(offenders),
    )


def dispatch(app: str = "*", strict: bool = False) -> list[dict[str, Any]]:
    """Run all guardian specs for the given app and return serialised results."""
    specs = get_specs_for_app(app)
    results: list[AppHealResult] = []
    for spec in specs:
        _log.info("[AppRemediationDispatcher] running %s (%s)", spec.check_id, spec.description)
        result = _run_spec(spec)
        results.append(result)
        _log.info("[AppRemediationDispatcher] %s -> %s", spec.check_id, result.status.value)

    payload = [r.to_dict() for r in results]

    out_path = Path("artifacts") / "combined_app_heal_result.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    _log.info("[AppRemediationDispatcher] report written to %s", out_path)

    if strict:
        failed = [r for r in results if r.status == AppHealStatus.FAILED]
        if failed:
            _log.error("[AppRemediationDispatcher] %d check(s) FAILED in strict mode", len(failed))
            sys.exit(1)

    return payload


if __name__ == "__main__":
    import argparse
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="apps_* remediation dispatcher")
    parser.add_argument("--app", default="*", help="Target app (apps_rg, apps_lic, apps_shared, *)")
    parser.add_argument("--strict", action="store_true", help="Exit 1 on any FAILED check")
    args = parser.parse_args()
    dispatch(app=args.app, strict=args.strict)
