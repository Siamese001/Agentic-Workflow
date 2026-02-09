"""
Enforcement Result Types — Shared typed contracts for all enforcement modules.

Every enforcement module returns an EnforcementResult from its check() function.
The orchestrator (_verify.py) aggregates these into an EnforcementReport and
emits a deterministic JSON artifact.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, TypedDict


class Violation(TypedDict):
    """A single enforcement violation."""

    type: str
    path: str
    severity: str  # "error" or "warning"
    detail: str


class EnforcementResult(TypedDict):
    """Result from a single enforcement module's check() call."""

    name: str
    passed: bool
    violations: list[Violation]
    stats: dict[str, int]


class EnforcementReport(TypedDict):
    """Aggregated report from all enforcement modules."""

    timestamp: str
    verifier_version: str
    overall_passed: bool
    checks: list[EnforcementResult]
    summary: dict[str, int]


VERIFIER_VERSION = "4.5.0"


def make_result(
    name: str,
    violations: list[Violation],
    stats: dict[str, int],
) -> EnforcementResult:
    """Create an EnforcementResult with computed passed status."""
    has_errors = any(v["severity"] == "error" for v in violations)
    return EnforcementResult(
        name=name,
        passed=not has_errors,
        violations=violations,
        stats=stats,
    )


BUDGETED_WARNING_TYPES: frozenset[str] = frozenset(
    {
        "missing_optional_subfolder",
        # Known-debt violations are budgeted only when explicitly listed in
        # known_debt_baseline.json with ceiling enforcement. The violation type
        # is config_execution_violation (for gateway_config.py lazy imports).
        # All other cross-layer violations are errors by default.
        "config_execution_violation",
    },
)


def make_report(results: list[EnforcementResult]) -> EnforcementReport:
    """Aggregate individual results into a full report."""
    passed_count = sum(1 for r in results if r["passed"])
    failed_count = len(results) - passed_count
    all_violations = [v for r in results for v in r["violations"]]
    total_violations = len(all_violations)

    warnings = [v for v in all_violations if v["severity"] == "warning"]
    errors = [v for v in all_violations if v["severity"] == "error"]
    budgeted = [w for w in warnings if w["type"] in BUDGETED_WARNING_TYPES]
    unbudgeted = [w for w in warnings if w["type"] not in BUDGETED_WARNING_TYPES]

    return EnforcementReport(
        timestamp=datetime.now(timezone.utc).isoformat(),
        verifier_version=VERIFIER_VERSION,
        overall_passed=all(r["passed"] for r in results),
        checks=results,
        summary={
            "total_checks": len(results),
            "passed": passed_count,
            "failed": failed_count,
            "total_violations": total_violations,
            "errors": len(errors),
            "warnings_budgeted": len(budgeted),
            "warnings_unbudgeted": len(unbudgeted),
        },
    )


def emit_report_json(report: EnforcementReport) -> dict[str, Any]:
    """Convert report to JSON-serializable dict (identity for TypedDict)."""
    return dict(report)
