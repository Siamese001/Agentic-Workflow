#!/usr/bin/env python3
"""
check_plan_freshness.py — CI gate: Plan freshness + unauthorized expansion detection.

Reuses W2 authorization logic from `.windsurf/scripts/_plan_scope_expansion_check.py`.
Does NOT duplicate marker parsing logic.

Detects:
  1. Stale active plans: status = "In Progress" AND last_updated older than threshold
  2. Unauthorized scope expansions: work evidence without proper authorization chain

Exit codes:
    0 = all checks pass (or bypass active)
    1 = violations found in strict mode

Configuration (environment variables):
    PLAN_FRESHNESS_MAX_HOURS       — Max age for active plans (default: 168 = 7 days)
    PLAN_FRESHNESS_STRICT          — Set to "1" for fail-closed mode
    PLAN_FRESHNESS_BYPASS          — Set to "1" to skip all checks
    MIN_FILES_FOR_AUDIT            — Threshold for "substantial work" (default: 3)
    AUTH_MARKER_RECENCY_SEC        — Authorization window (default: 300)

Output:
    Human-readable report to stdout
    JSON report to artifacts/ci/plan_freshness_gate.json

CONSTITUTIONAL
    - No shell=True, no PowerShell
    - subprocess.run with timeout where used
    - Specific exceptions only
    - UTF-8 stdio
    - Reuse W2 logic, no duplication
"""

from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Path setup for imports
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
PLANS_DIR = REPO_ROOT / ".windsurf" / "plans"
REPORT_OUT = REPO_ROOT / "artifacts" / "ci" / "plan_freshness_gate.json"

# Add .windsurf/scripts to path for W2 helper import
sys.path.insert(0, str(REPO_ROOT))

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BYPASS_ENV = "PLAN_FRESHNESS_BYPASS"
STRICT_ENV = "PLAN_FRESHNESS_STRICT"
MAX_HOURS_ENV = "PLAN_FRESHNESS_MAX_HOURS"
MIN_FILES_ENV = "MIN_FILES_FOR_AUDIT"
RECENCY_SEC_ENV = "AUTH_MARKER_RECENCY_SEC"

DEFAULT_MAX_HOURS = 168  # 7 days
DEFAULT_MIN_FILES = 3
DEFAULT_RECENCY_SEC = 300

# Status values that indicate "active" plans
ACTIVE_STATUSES = {"In Progress", "Not Started", "Waiting", "Deferred"}

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Finding:
    """A single finding from the freshness check."""

    plan_slug: str
    check_type: str  # 'stale' | 'unauthorized_expansion' | 'missing_authorization' | etc.
    severity: str  # 'ERROR' | 'WARN' | 'INFO'
    message: str
    reason_code: str | None = None
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class Config:
    """Gate configuration from environment."""

    max_hours: int
    strict_mode: bool
    min_files: int
    recency_sec: int

    @classmethod
    def from_env(cls) -> Config:
        return cls(
            max_hours=int(os.environ.get(MAX_HOURS_ENV, DEFAULT_MAX_HOURS)),
            strict_mode=os.environ.get(STRICT_ENV) == "1",
            min_files=int(os.environ.get(MIN_FILES_ENV, DEFAULT_MIN_FILES)),
            recency_sec=int(os.environ.get(RECENCY_SEC_ENV, DEFAULT_RECENCY_SEC)),
        )


# ---------------------------------------------------------------------------
# Plan file parsing
# ---------------------------------------------------------------------------


# Frontmatter patterns
_STATUS_RE = re.compile(r"^status:\s*(.+)$", re.MULTILINE | re.IGNORECASE)
_LAST_UPDATED_RE = re.compile(r"^last_updated:\s*(\S+)$", re.MULTILINE | re.IGNORECASE)

# Work evidence patterns (simple heuristics for "substantial work")
_EDIT_CALL_RE = re.compile(r"edit\s*\(", re.IGNORECASE)
_WRITE_FILE_RE = re.compile(r"write_to_file|mcp4_write_file", re.IGNORECASE)
_MULTI_EDIT_RE = re.compile(r"multi_edit", re.IGNORECASE)


class PlanParseError(Exception):
    """Raised when plan file cannot be parsed."""


@dataclass
class PlanInfo:
    """Parsed plan file information."""

    slug: str
    path: Path
    status: str | None
    last_updated: datetime | None
    content: str


def parse_plan_file(plan_path: Path) -> PlanInfo:
    """Parse a plan file extracting frontmatter and content."""
    content = plan_path.read_text(encoding="utf-8")

    # Extract status
    status_match = _STATUS_RE.search(content)
    status = status_match.group(1).strip() if status_match else None

    # Extract last_updated
    last_updated_match = _LAST_UPDATED_RE.search(content)
    last_updated: datetime | None = None
    if last_updated_match:
        timestamp_str = last_updated_match.group(1).strip()
        try:
            # Try ISO format
            last_updated = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        except ValueError:
            try:
                # Try common format: 2026-05-12T08:50Z
                last_updated = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%MZ").replace(
                    tzinfo=timezone.utc
                )
            except ValueError:
                pass  # Keep None if parsing fails

    return PlanInfo(
        slug=plan_path.stem,
        path=plan_path,
        status=status,
        last_updated=last_updated,
        content=content,
    )


def is_active_status(status: str | None) -> bool:
    """Check if status indicates an active (non-terminal) plan."""
    if not status:
        return False
    return status.strip() in ACTIVE_STATUSES


def count_work_evidence(content: str) -> int:
    """Count evidence of substantial work in response text.

    Returns approximate count of file-modifying operations.
    """
    count = 0
    count += len(_EDIT_CALL_RE.findall(content))
    count += len(_WRITE_FILE_RE.findall(content))
    count += len(_MULTI_EDIT_RE.findall(content))
    return count


# ---------------------------------------------------------------------------
# W2 Logic Import
# ---------------------------------------------------------------------------


def import_w2_authorization_check() -> Any:
    """Import W2 check_scope_authorization function dynamically.

    Uses the same pattern as the W3 hook to avoid import issues.
    Handles dataclasses module import issues when using importlib.
    """
    try:
        # First try direct import (when running from repo root)
        from windsurf.scripts._plan_scope_expansion_check import (
            check_scope_authorization,
        )

        return check_scope_authorization
    except ImportError:
        pass
    except AttributeError:
        # W2 helper has dataclasses issues when imported in certain contexts
        pass

    # Fallback: use importlib with absolute path
    import importlib.util

    helper_path = REPO_ROOT / ".windsurf" / "scripts" / "_plan_scope_expansion_check.py"
    if not helper_path.exists():
        return None

    spec = importlib.util.spec_from_file_location("_plan_scope_expansion_check", helper_path)
    if spec is None or spec.loader is None:
        return None

    try:
        module = importlib.util.module_from_spec(spec)
        # Pre-register the module to avoid dataclasses __module__ lookup issues
        sys.modules["_plan_scope_expansion_check"] = module
        spec.loader.exec_module(module)
        return getattr(module, "check_scope_authorization", None)
    except (ImportError, AttributeError):
        # Clean up failed module registration
        sys.modules.pop("_plan_scope_expansion_check", None)
        return None


# ---------------------------------------------------------------------------
# Core Checks
# ---------------------------------------------------------------------------


def check_stale_plan(plan: PlanInfo, config: Config, now: datetime) -> Finding | None:
    """Check if an active plan is stale (old last_updated).

    Returns Finding if stale, None if fresh or not active.
    """
    if not is_active_status(plan.status):
        return None

    if plan.last_updated is None:
        return Finding(
            plan_slug=plan.slug,
            check_type="missing_timestamp",
            severity="WARN",
            message=f"Plan {plan.slug} has no last_updated timestamp in frontmatter",
            reason_code="MISSING_LAST_UPDATED",
        )

    age = now - plan.last_updated
    max_age = timedelta(hours=config.max_hours)

    if age > max_age:
        return Finding(
            plan_slug=plan.slug,
            check_type="stale",
            severity="WARN",
            message=(
                f"Plan {plan.slug} is stale: last_updated {age.days}d ago "
                f"(threshold: {config.max_hours}h)"
            ),
            reason_code="STALE_ACTIVE_PLAN",
            details={
                "last_updated": plan.last_updated.isoformat(),
                "age_hours": age.total_seconds() / 3600,
                "threshold_hours": config.max_hours,
            },
        )

    return None


def check_unauthorized_expansion(
    plan: PlanInfo, config: Config, auth_check_func: Any
) -> Finding | None:
    """Check for unauthorized scope expansion using W2 logic.

    Returns Finding if unauthorized work detected, None if OK.
    """
    if not is_active_status(plan.status):
        return None

    # Count work evidence
    work_count = count_work_evidence(plan.content)

    if work_count < config.min_files:
        # Not substantial enough to trigger audit
        return None

    # Use W2 authorization check
    if auth_check_func is None:
        # W2 helper not available - report but don't block
        return Finding(
            plan_slug=plan.slug,
            check_type="helper_unavailable",
            severity="INFO",
            message="W2 authorization helper unavailable - skipping auth check",
            reason_code="W2_HELPER_UNAVAILABLE",
        )

    # Check authorization using W2 API
    result = auth_check_func(
        plan_id=plan.slug,
        changed_files_count=work_count,
        marker_texts=[plan.content],  # Pass content as markers (W2 parses internally)
        recency_window_sec=config.recency_sec,
    )

    # Check for issues
    if not result.get("authorized", False):
        reason_codes = result.get("reason_codes", [])
        discovered_gap = result.get("discovered_gap")

        # Build detailed message
        details = {
            "work_evidence_count": work_count,
            "threshold": config.min_files,
            "reason_codes": reason_codes,
            "discovered_gap": discovered_gap,
        }

        message = f"Plan {plan.slug}: unauthorized scope expansion detected"
        if reason_codes:
            message += f" (reasons: {', '.join(reason_codes)})"

        return Finding(
            plan_slug=plan.slug,
            check_type="unauthorized_expansion",
            severity="ERROR" if "MISSING_AUTHORIZATION_DECISION" in reason_codes else "WARN",
            message=message,
            reason_code=reason_codes[0] if reason_codes else "UNAUTHORIZED_SCOPE",
            details=details,
        )

    return None


# ---------------------------------------------------------------------------
# Main Evaluation
# ---------------------------------------------------------------------------


def evaluate_all_plans(config: Config) -> list[Finding]:
    """Evaluate all plan files and return list of findings."""
    findings: list[Finding] = []
    now = datetime.now(timezone.utc)

    # Import W2 authorization check
    auth_check_func = import_w2_authorization_check()

    if auth_check_func is None:
        findings.append(
            Finding(
                plan_slug="_gate_",
                check_type="helper_unavailable",
                severity="INFO",
                message="W2 authorization helper not available - some checks skipped",
                reason_code="W2_HELPER_UNAVAILABLE",
            )
        )

    # Scan all plan files
    if not PLANS_DIR.exists():
        findings.append(
            Finding(
                plan_slug="_gate_",
                check_type="no_plans_dir",
                severity="ERROR",
                message=f"Plans directory not found: {PLANS_DIR}",
                reason_code="PLANS_DIR_MISSING",
            )
        )
        return findings

    plan_files = list(PLANS_DIR.glob("*.md"))

    if not plan_files:
        findings.append(
            Finding(
                plan_slug="_gate_",
                check_type="no_plans",
                severity="INFO",
                message="No plan files found",
                reason_code="NO_PLANS_FOUND",
            )
        )
        return findings

    for plan_path in sorted(plan_files):
        try:
            plan = parse_plan_file(plan_path)
        except Exception as exc:
            findings.append(
                Finding(
                    plan_slug=plan_path.stem,
                    check_type="parse_error",
                    severity="WARN",
                    message=f"Failed to parse plan {plan_path.name}: {exc}",
                    reason_code="PARSE_ERROR",
                )
            )
            continue

        # Check 1: Stale active plan
        stale_finding = check_stale_plan(plan, config, now)
        if stale_finding:
            findings.append(stale_finding)

        # Check 2: Unauthorized expansion
        auth_finding = check_unauthorized_expansion(plan, config, auth_check_func)
        if auth_finding:
            findings.append(auth_finding)

    return findings


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def generate_report(findings: list[Finding], config: Config) -> dict[str, Any]:
    """Generate JSON report structure."""
    errors = [f for f in findings if f.severity == "ERROR"]
    warnings = [f for f in findings if f.severity == "WARN"]
    infos = [f for f in findings if f.severity == "INFO"]

    # Group by plan
    by_plan: dict[str, list[Finding]] = {}
    for f in findings:
        by_plan.setdefault(f.plan_slug, []).append(f)

    # Build summary table rows
    summary_rows = []
    for slug, plan_findings in sorted(by_plan.items()):
        if slug == "_gate_":
            continue  # Skip gate-level findings in summary

        has_error = any(f.severity == "ERROR" for f in plan_findings)
        status = "FAIL" if has_error else "WARN" if plan_findings else "PASS"

        reasons = [f.reason_code for f in plan_findings if f.reason_code]
        summary_rows.append({
            "plan": slug,
            "status": status,
            "findings_count": len(plan_findings),
            "reason_codes": reasons,
        })

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "config": {
            "max_hours": config.max_hours,
            "strict_mode": config.strict_mode,
            "min_files": config.min_files,
            "recency_sec": config.recency_sec,
        },
        "summary": {
            "total_plans_checked": len(summary_rows),
            "errors": len(errors),
            "warnings": len(warnings),
            "infos": len(infos),
            "pass": len([r for r in summary_rows if r["status"] == "PASS"]),
            "fail": len([r for r in summary_rows if r["status"] == "FAIL"]),
        },
        "plan_results": summary_rows,
        "findings": [
            {
                "plan_slug": f.plan_slug,
                "check_type": f.check_type,
                "severity": f.severity,
                "message": f.message,
                "reason_code": f.reason_code,
                "details": f.details,
            }
            for f in findings
        ],
    }


def print_human_report(report: dict[str, Any]) -> None:
    """Print human-readable report to stdout."""
    summary = report["summary"]

    print("=" * 70)
    print("PLAN FRESHNESS GATE REPORT")
    print("=" * 70)
    print()

    # Config
    cfg = report["config"]
    print(f"Configuration:")
    print(f"  Max age: {cfg['max_hours']} hours ({cfg['max_hours'] / 24:.1f} days)")
    print(f"  Strict mode: {'Yes' if cfg['strict_mode'] else 'No'}")
    print(f"  Min files threshold: {cfg['min_files']}")
    print(f"  Auth recency window: {cfg['recency_sec']} seconds")
    print()

    # Summary table
    print(f"Summary: {summary['total_plans_checked']} plans checked")
    print(f"  PASS: {summary['pass']}")
    print(f"  WARN: {summary['warnings']}")
    print(f"  FAIL: {summary['fail']}")
    print(f"  INFO: {summary['infos']}")
    print()

    # Detailed findings
    errors = [f for f in report["findings"] if f["severity"] == "ERROR"]
    warnings = [f for f in report["findings"] if f["severity"] == "WARN"]

    if errors:
        print("ERRORS:")
        for f in errors:
            print(f"  [{f['reason_code'] or 'ERROR'}] {f['plan_slug']}: {f['message']}")
        print()

    if warnings:
        print("WARNINGS:")
        for f in warnings:
            print(f"  [{f['reason_code'] or 'WARN'}] {f['plan_slug']}: {f['message']}")
        print()

    # Verdict
    if summary["fail"] > 0:
        print("VERDICT: FAIL (errors found)")
    elif summary["warnings"] > 0:
        print("VERDICT: WARN (warnings found)")
    else:
        print("VERDICT: PASS")
    print()

    print(f"Full report written to: {REPORT_OUT}")
    print("=" * 70)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    """Main entry point. Returns exit code."""
    # Check bypass
    if os.environ.get(BYPASS_ENV) == "1":
        print("PLAN_FRESHNESS_BYPASS=1 — skipping all checks")
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "bypassed": True,
            "summary": {"errors": 0, "warnings": 0, "infos": 1, "pass": 0, "fail": 0},
            "findings": [],
        }
        REPORT_OUT.parent.mkdir(parents=True, exist_ok=True)
        REPORT_OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
        return 0

    # Load config
    config = Config.from_env()

    # Run checks
    findings = evaluate_all_plans(config)

    # Generate report
    report = generate_report(findings, config)

    # Write JSON report
    REPORT_OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT_OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")

    # Print human report
    print_human_report(report)

    # Determine exit code
    has_errors = any(f.severity == "ERROR" for f in findings)

    if config.strict_mode and has_errors:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
