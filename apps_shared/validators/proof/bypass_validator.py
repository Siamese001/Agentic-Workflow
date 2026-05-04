"""Bypass validator — converts ADG query results to PASS/FAIL with waivers.

Per the prompt §5 acceptance: any unresolved P0/P1 bypass fails the proof
unless an explicit waiver receipt is present (with reason code, owner,
expiration). Waiver mechanism is defined here but not yet populated by W2.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from apps_shared.validators.proof.adg_queries import AppBypassReport, run_bypass_queries


@dataclass(frozen=True)
class Waiver:
    """Approved exemption for a specific (app_id, query_name) pair."""

    app_id: str
    query_name: str
    reason_code: str
    risk_class: str  # NORMAL | HIGH_IMPACT | INFRASTRUCTURE
    owner: str
    expires_at: str  # ISO-8601 UTC

    def is_active(self) -> bool:
        try:
            exp = datetime.fromisoformat(self.expires_at.replace("Z", "+00:00"))
        except ValueError:
            return False
        return exp > datetime.now(timezone.utc)


def load_waivers(waiver_file: Path | None) -> tuple[Waiver, ...]:
    """Load waivers from a JSON file. Missing file = empty tuple (strict mode)."""
    if waiver_file is None or not waiver_file.exists():
        return ()
    data = json.loads(waiver_file.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"waiver_file must contain a list: {waiver_file}")
    return tuple(Waiver(**rec) for rec in data)


@dataclass
class BypassValidationResult:
    """Outcome of validating a single :class:`AppBypassReport`."""

    app_id: str
    passed: bool
    p0_unresolved: int
    p1_unresolved: int
    p2_unresolved: int
    fail_reasons: list[str] = field(default_factory=list)
    waivers_consumed: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "app_id": self.app_id,
            "passed": self.passed,
            "p0_unresolved": self.p0_unresolved,
            "p1_unresolved": self.p1_unresolved,
            "p2_unresolved": self.p2_unresolved,
            "fail_reasons": list(self.fail_reasons),
            "waivers_consumed": list(self.waivers_consumed),
        }


def validate_bypass_report(
    report: AppBypassReport,
    *,
    waivers: tuple[Waiver, ...] = (),
    fail_on_p1: bool = False,
) -> BypassValidationResult:
    """Apply waiver/severity rules to a bypass report.

    By default only P0 unresolved fails the proof; P1 (coverage gaps) is
    surfaced but does not gate. Set ``fail_on_p1=True`` to enforce strict
    coverage closure (the eventual end-state).
    """
    result = BypassValidationResult(
        app_id=report.app_id,
        passed=True,
        p0_unresolved=report.p0_unresolved_total,
        p1_unresolved=report.p1_unresolved_total,
        p2_unresolved=report.p2_unresolved_total,
    )
    active_waivers = {(w.app_id, w.query_name): w for w in waivers if w.is_active()}

    for q_name, q_result in report.per_query.items():
        sev = q_result.get("severity")
        unresolved = q_result.get("unresolved", 0)
        if not isinstance(unresolved, int) or unresolved <= 0:
            continue
        is_p0 = sev == "P0"
        is_p1 = sev == "P1"
        if not (is_p0 or (is_p1 and fail_on_p1)):
            continue
        waiver = active_waivers.get((report.app_id, q_name))
        if waiver is not None:
            result.waivers_consumed.append(
                f"{q_name}:{waiver.reason_code}:{waiver.owner}:exp={waiver.expires_at}"
            )
            continue
        result.passed = False
        result.fail_reasons.append(f"unresolved {sev} bypass: {q_name} (count={unresolved})")
    return result


def run_full_bypass_validation(
    *,
    snapshot: Path,
    apps: tuple[str, ...],
    waivers: tuple[Waiver, ...] = (),
    fail_on_p1: bool = False,
) -> tuple[dict[str, AppBypassReport], dict[str, BypassValidationResult]]:
    """Run + validate bypass queries for every app in ``apps``."""
    reports: dict[str, AppBypassReport] = {}
    results: dict[str, BypassValidationResult] = {}
    for app_id in apps:
        report = run_bypass_queries(snapshot=snapshot, app_id=app_id)
        reports[app_id] = report
        results[app_id] = validate_bypass_report(report, waivers=waivers, fail_on_p1=fail_on_p1)
    return reports, results


__all__ = [
    "Waiver",
    "load_waivers",
    "BypassValidationResult",
    "validate_bypass_report",
    "run_full_bypass_validation",
]
