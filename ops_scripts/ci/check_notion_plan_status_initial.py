#!/usr/bin/env python3
"""
check_notion_plan_status_initial.py — CI gate NP-SI (Status Initial).

Detects plans created with wrong initial status (not "Not Started" or "Completed").
Queries Notion Plans DB for recent plans, validates their creation-time status.

Defense in depth for holistic-plan-status-discipline-d4e8a1 (W3).

Usage:
    python ops_scripts/ci/check_notion_plan_status_initial.py

Environment:
    NOTION_API_KEY or NOTION_TOKEN — required for Notion API access
    NOTION_PLAN_STATUS_INITIAL_FAIL_CLOSED=1 — exit 1 on violations (default: advisory/exit 0)
    NOTION_PLAN_STATUS_INITIAL_BYPASS=1 — skip gate entirely
    NOTION_PLAN_STATUS_INITIAL_DAYS=7 — lookback window (default: 7 days)

Outputs:
    artifacts/ci/plan_status_initial_violations.json — structured report
    STDERR: human-readable summary

Exit codes:
    0 = OK or advisory violations
    1 = violations found (fail-closed mode)
    2 = gate error / misconfiguration
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

_NOTION_BASE = "https://api.notion.com/v1"
_NOTION_API_VERSION = "2025-09-03"
_NOTION_TIMEOUT_S = 30

# Plans DB data_source_id
_PLANS_DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"

# Valid statuses at creation time
VALID_CREATION_STATUSES = frozenset({"Not Started", "Completed"})
FORBIDDEN_AT_CREATION = {"In Progress", "Waiting", "Lower Priority", "Retired", "Archived"}

# Output paths
_VIOLATIONS_PATH = Path("artifacts/ci/plan_status_initial_violations.json")
_REPORT_PATH = Path("artifacts/ci/plan_status_initial_report.json")


@dataclass
class Violation:
    """A plan with wrong initial status."""
    slug: str
    page_id: str
    created_time: str
    wrong_status: str
    recommended_status: str
    severity: str  # "error" for forbidden, "warning" for unknown


@dataclass
class GateReport:
    """Overall gate execution report."""
    timestamp: str
    total_plans_checked: int
    violations_found: int
    errors_found: int  # "In Progress", "Waiting", etc.
    warnings_found: int  # unknown statuses
    lookback_days: int
    fail_closed: bool
    bypassed: bool
    violations: list[dict]


def _notion_token() -> str | None:
    """Get Notion token from environment."""
    return os.environ.get("NOTION_API_KEY") or os.environ.get("NOTION_TOKEN")


def _call_notion_query(payload: dict) -> dict:
    """Execute Notion data source query."""
    token = _notion_token()
    if not token:
        raise RuntimeError("NOTION_API_KEY or NOTION_TOKEN required")
    
    url = f"{_NOTION_BASE}/data_sources/{_PLANS_DATA_SOURCE_ID}/query"
    
    try:
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=body,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Notion-Version": _NOTION_API_VERSION,
            },
            method="POST",
        )
        
        with urllib.request.urlopen(req, timeout=_NOTION_TIMEOUT_S) as resp:
            return json.loads(resp.read().decode("utf-8"))
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        raise RuntimeError(f"Notion API HTTP {e.code}: {error_body}")
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        raise RuntimeError(f"Notion API connection error: {e}")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON from Notion: {e}")


def _fetch_recent_plans(days: int) -> list[dict[str, Any]]:
    """
    Fetch plans created in the last N days.
    
    Uses created_time filter if possible, otherwise fetches all and filters client-side.
    """
    cutoff = datetime.utcnow() - timedelta(days=days)
    cutoff_iso = cutoff.isoformat() + "Z"
    
    all_results = []
    has_more = True
    start_cursor = None
    
    while has_more:
        payload: dict[str, Any] = {
            "page_size": 100,
            "sorts": [
                {
                    "timestamp": "created_time",
                    "direction": "descending",
                }
            ],
        }
        
        if start_cursor:
            payload["start_cursor"] = start_cursor
        
        # Note: Notion API doesn't support created_time filter directly in query
        # We fetch and filter client-side
        
        response = _call_notion_query(payload)
        results = response.get("results", [])
        
        for result in results:
            created_time = result.get("created_time", "")
            if created_time >= cutoff_iso:
                all_results.append(result)
            else:
                # Results are sorted by created_time descending, so we can stop
                has_more = False
                break
        
        if has_more:
            has_more = response.get("has_more", False)
            start_cursor = response.get("next_cursor")
            
            # Safety: if no more pages but we haven't hit cutoff, stop anyway
            if not has_more:
                break
    
    return all_results


def _extract_status(result: dict) -> str:
    """Extract status from Notion page result."""
    properties = result.get("properties", {})
    status_prop = properties.get("Status", {})
    
    if "select" in status_prop:
        return status_prop["select"].get("name", "")
    return ""


def _extract_slug(result: dict) -> str:
    """Extract slug from Notion page result."""
    properties = result.get("properties", {})
    slug_prop = properties.get("Slug", {})
    
    if "title" in slug_prop:
        titles = slug_prop["title"]
        if titles and isinstance(titles, list):
            return titles[0].get("text", {}).get("content", "")
    return ""


def _validate_initial_status(status: str) -> tuple[bool, str, str]:
    """
    Validate initial status of a plan.
    
    Returns (is_valid, recommended_status, severity)
    """
    if not status:
        return False, "Not Started", "warning"
    
    if status in VALID_CREATION_STATUSES:
        return True, status, "ok"
    
    if status in FORBIDDEN_AT_CREATION:
        return False, "Not Started", "error"
    
    # Unknown status
    return False, "Not Started", "warning"


def _check_plans(plans: list[dict]) -> list[Violation]:
    """Check all plans for violations."""
    violations = []
    
    for plan in plans:
        slug = _extract_slug(plan)
        page_id = plan.get("id", "")
        created_time = plan.get("created_time", "")
        status = _extract_status(plan)
        
        is_valid, recommended, severity = _validate_initial_status(status)
        
        if not is_valid:
            violations.append(Violation(
                slug=slug or "unknown",
                page_id=page_id,
                created_time=created_time,
                wrong_status=status or "(empty)",
                recommended_status=recommended,
                severity=severity,
            ))
    
    return violations


def _save_report(report: GateReport) -> None:
    """Save structured report to disk."""
    _VIOLATIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
    _REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Save full report
    with _REPORT_PATH.open("w", encoding="utf-8") as f:
        json.dumps(asdict(report), f, indent=2, default=str)
    
    # Save just violations (for easy parsing)
    violations_only = {
        "count": len(report.violations),
        "violations": report.violations,
    }
    with _VIOLATIONS_PATH.open("w", encoding="utf-8") as f:
        json.dumps(violations_only, f, indent=2, default=str)


def main() -> int:
    """Main entry point for CI gate."""
    # Check bypass
    if os.environ.get("NOTION_PLAN_STATUS_INITIAL_BYPASS") == "1":
        print(
            "[check-plan-status-initial] BYPASS: NOTION_PLAN_STATUS_INITIAL_BYPASS=1",
            file=sys.stderr,
        )
        return 0
    
    # Check fail-closed mode
    fail_closed = os.environ.get("NOTION_PLAN_STATUS_INITIAL_FAIL_CLOSED") == "1"
    
    # Get lookback window
    try:
        lookback_days = int(os.environ.get("NOTION_PLAN_STATUS_INITIAL_DAYS", "7"))
    except ValueError:
        lookback_days = 7
    
    # Check token availability
    if not _notion_token():
        print(
            "[check-plan-status-initial] SKIP: No NOTION_API_KEY/TOKEN",
            file=sys.stderr,
        )
        # Skip gracefully in CI without token
        report = GateReport(
            timestamp=datetime.utcnow().isoformat() + "Z",
            total_plans_checked=0,
            violations_found=0,
            errors_found=0,
            warnings_found=0,
            lookback_days=lookback_days,
            fail_closed=fail_closed,
            bypassed=False,
            violations=[],
        )
        _save_report(report)
        return 0
    
    print(
        f"[check-plan-status-initial] Checking plans from last {lookback_days} days...",
        file=sys.stderr,
    )
    
    try:
        # Fetch recent plans
        plans = _fetch_recent_plans(lookback_days)
        
        # Check for violations
        violations = _check_plans(plans)
        
        # Categorize
        errors = [v for v in violations if v.severity == "error"]
        warnings = [v for v in violations if v.severity == "warning"]
        
        # Build report
        report = GateReport(
            timestamp=datetime.utcnow().isoformat() + "Z",
            total_plans_checked=len(plans),
            violations_found=len(violations),
            errors_found=len(errors),
            warnings_found=len(warnings),
            lookback_days=lookback_days,
            fail_closed=fail_closed,
            bypassed=False,
            violations=[asdict(v) for v in violations],
        )
        
        _save_report(report)
        
        # Print summary
        print(
            f"[check-plan-status-initial] "
            f"Checked: {len(plans)} | "
            f"Violations: {len(violations)} ({len(errors)} errors, {len(warnings)} warnings)",
            file=sys.stderr,
        )
        
        # Print violations
        for v in violations:
            severity_emoji = "❌" if v.severity == "error" else "⚠️"
            print(
                f"  {severity_emoji} {v.slug}: '{v.wrong_status}' -> '{v.recommended_status}'",
                file=sys.stderr,
            )
        
        # Exit code
        if violations:
            if fail_closed:
                print(
                    "[check-plan-status-initial] FAIL: Violations found (fail-closed mode)",
                    file=sys.stderr,
                )
                return 1
            else:
                print(
                    "[check-plan-status-initial] WARN: Violations found (advisory mode)",
                    file=sys.stderr,
                )
                return 0
        else:
            print(
                "[check-plan-status-initial] OK: All plans have valid initial status",
                file=sys.stderr,
            )
            return 0
            
    except Exception as e:
        print(
            f"[check-plan-status-initial] ERROR: {e}",
            file=sys.stderr,
        )
        if fail_closed:
            return 2
        return 0


if __name__ == "__main__":
    sys.exit(main())
