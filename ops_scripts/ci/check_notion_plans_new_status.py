#!/usr/bin/env python3
"""
Notion Plans New-Plan Status Enforcement (NP6)

Validates that newly-created plans in Notion Plans DB use status "Not Started",
not "Lower Priority" or "Waiting". Catches PLAN_CREATED marker errors where incorrect
status flows through to Notion.

Detection window: 24 hours from creation time. Allows intentional "Lower Priority"
transitions on older plans.

Canonical new-plan status: "Not Started"
Forbidden statuses for new plans: "Lower Priority", "Waiting", "In Progress", "Completed"

Usage:
    python ops_scripts/ci/check_notion_plans_new_status.py [--fail-closed]

Exit codes:
    0 = All new plans use "Not Started" (or advisory mode)
    1 = Violations found (fail-closed mode)

Environment:
    NOTION_TOKEN or NOTION_API_KEY required for API access
    NOTION_PLANS_NEW_STATUS_BYPASS=1 → skip check
    NOTION_PLANS_NEW_STATUS_FAIL_CLOSED=1 → exit 1 on violations

Output:
    artifacts/ci/notion_plans_new_status.json

Rule: .cursor/rules/notion-plans-taxonomy.md > "New plans MUST use Not Started"
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "ci"
ARTIFACT_PATH = ARTIFACTS_DIR / "notion_plans_new_status.json"

NOTION_BASE = "https://api.notion.com/v1"
NOTION_API_VERSION = "2025-09-03"
NOTION_HTTP_TIMEOUT_S = 30
PLANS_DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"

# Detection window for "new" plans (hours)
DETECTION_WINDOW_HOURS = 24

# Only this status is allowed for new plans
CANONICAL_NEW_PLAN_STATUS = "Not Started"

# Statuses that violate the new-plan rule
VIOLATION_STATUSES = {"Lower Priority", "Waiting", "In Progress", "Completed"}


@dataclass(frozen=True)
class Violation:
    page_id: str
    slug: str
    status: str
    created_time: str
    violation_type: str


def _notion_token() -> str | None:
    return os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY")


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _parse_iso8601(ts: str) -> datetime | None:
    """Parse Notion ISO8601 timestamp (with microseconds and Z)."""
    try:
        # Handle both "2026-05-10T18:14:00.000Z" and "2026-05-10T18:14:00Z"
        ts = ts.replace("Z", "+00:00")
        return datetime.fromisoformat(ts)
    except (ValueError, TypeError):
        return None


def _query_plans_db(token: str) -> list[dict[str, Any]]:
    """Query Plans DB for recent rows. Returns raw results list."""
    url = f"{NOTION_BASE}/data_sources/{PLANS_DATA_SOURCE_ID}/query"
    
    # Query for rows created within last 48h (generous buffer)
    cutoff = (_now_utc() - timedelta(hours=48)).isoformat()
    
    query = {
        "filter": {
            "property": "Created time",
            "date": {"after": cutoff}
        },
        "page_size": 100,
    }
    
    try:
        body = json.dumps(query).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Notion-Version": NOTION_API_VERSION,
            },
        )
        with urllib.request.urlopen(req, timeout=NOTION_HTTP_TIMEOUT_S) as resp:
            data = json.loads(resp.read().decode("utf-8") or "{}")
        return data.get("results", [])
    except (
        urllib.error.HTTPError,
        urllib.error.URLError,
        TimeoutError,
        OSError,
        json.JSONDecodeError,
        ValueError,
    ) as exc:
        print(f"[check_notion_plans_new_status] API error: {exc}", file=sys.stderr)
        return []


def _extract_slug(page: dict[str, Any]) -> str | None:
    """Extract slug from page properties."""
    props = page.get("properties", {})
    slug_prop = props.get("Slug", {})
    title_items = slug_prop.get("title", []) if isinstance(slug_prop, dict) else []
    if title_items:
        return title_items[0].get("text", {}).get("content", "").strip()
    return None


def _extract_status(page: dict[str, Any]) -> str | None:
    """Extract status from page properties."""
    props = page.get("properties", {})
    status_prop = props.get("Status", {})
    if isinstance(status_prop, dict):
        select = status_prop.get("select")
        if isinstance(select, dict):
            return select.get("name", "").strip()
    return None


def _extract_created_time(page: dict[str, Any]) -> str | None:
    """Extract created_time from page."""
    return page.get("created_time", "").strip()


def _is_newly_created(created_time: str) -> bool:
    """Check if plan was created within detection window."""
    created = _parse_iso8601(created_time)
    if not created:
        return False
    cutoff = _now_utc() - timedelta(hours=DETECTION_WINDOW_HOURS)
    return created >= cutoff


def check_new_plans_status(token: str | None) -> dict[str, Any]:
    """Main check logic. Returns report dict."""
    report: dict[str, Any] = {
        "checked_at": _now_utc().isoformat(),
        "detection_window_hours": DETECTION_WINDOW_HOURS,
        "canonical_new_plan_status": CANONICAL_NEW_PLAN_STATUS,
        "violations": [],
        "passed": [],
        "skipped": [],
        "errors": [],
    }
    
    if not token:
        report["errors"].append("NOTION_TOKEN / NOTION_API_KEY not set")
        return report
    
    results = _query_plans_db(token)
    if not results:
        report["errors"].append("No results from Notion API (check token / network)")
        return report
    
    violations: list[Violation] = []
    passed: list[dict[str, str]] = []
    skipped: list[dict[str, str]] = []
    
    for page in results:
        page_id = page.get("id", "unknown")
        slug = _extract_slug(page)
        status = _extract_status(page)
        created_time = _extract_created_time(page)
        
        if not slug:
            skipped.append({"page_id": page_id, "reason": "no_slug"})
            continue
        if not status:
            skipped.append({"page_id": page_id, "slug": slug, "reason": "no_status"})
            continue
        if not created_time:
            skipped.append({"page_id": page_id, "slug": slug, "reason": "no_created_time"})
            continue
        
        # Only check plans created within detection window
        if not _is_newly_created(created_time):
            skipped.append({
                "page_id": page_id,
                "slug": slug,
                "reason": "outside_detection_window",
                "created_time": created_time,
            })
            continue
        
        if status in VIOLATION_STATUSES:
            violations.append(Violation(
                page_id=page_id,
                slug=slug,
                status=status,
                created_time=created_time,
                violation_type="NEW_PLAN_WRONG_STATUS",
            ))
        elif status == CANONICAL_NEW_PLAN_STATUS:
            passed.append({
                "page_id": page_id,
                "slug": slug,
                "status": status,
                "created_time": created_time,
            })
        else:
            # Unknown status (e.g., Retired, Archived — unlikely for new)
            violations.append(Violation(
                page_id=page_id,
                slug=slug,
                status=status,
                created_time=created_time,
                violation_type="NEW_PLAN_UNEXPECTED_STATUS",
            ))
    
    report["violations"] = [
        {
            "page_id": v.page_id,
            "slug": v.slug,
            "status": v.status,
            "created_time": v.created_time,
            "violation_type": v.violation_type,
        }
        for v in violations
    ]
    report["passed"] = passed
    report["skipped"] = skipped
    report["violation_count"] = len(violations)
    report["passed_count"] = len(passed)
    
    return report


def write_report(report: dict[str, Any]) -> None:
    """Write report to artifact path."""
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    with ARTIFACT_PATH.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="NP6: Notion Plans new-plan status enforcement")
    parser.add_argument("--fail-closed", action="store_true", help="Exit 1 on violations")
    args = parser.parse_args(argv)
    
    # Environment overrides
    if os.environ.get("NOTION_PLANS_NEW_STATUS_BYPASS") == "1":
        print("[check_notion_plans_new_status] BYPASS=1 — skipping", file=sys.stderr)
        return 0
    
    fail_closed = args.fail_closed or (os.environ.get("NOTION_PLANS_NEW_STATUS_FAIL_CLOSED") == "1")
    
    token = _notion_token()
    report = check_new_plans_status(token)
    write_report(report)
    
    violation_count = report.get("violation_count", 0)
    error_count = len(report.get("errors", []))
    
    # Summary output
    if violation_count == 0 and error_count == 0:
        print(f"[check_notion_plans_new_status] OK — {report.get('passed_count', 0)} new plans use '{CANONICAL_NEW_PLAN_STATUS}'")
        return 0
    
    if violation_count > 0:
        print(
            f"[check_notion_plans_new_status] VIOLATIONS: {violation_count} new plan(s) with wrong status",
            file=sys.stderr,
        )
        for v in report["violations"]:
            print(f"  - {v['slug']}: status='{v['status']}' (should be '{CANONICAL_NEW_PLAN_STATUS}')", file=sys.stderr)
    
    if error_count > 0:
        for e in report["errors"]:
            print(f"[check_notion_plans_new_status] ERROR: {e}", file=sys.stderr)
    
    if fail_closed and (violation_count > 0 or error_count > 0):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
