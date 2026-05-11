#!/usr/bin/env python3
"""
scan_and_repair_plan_statuses.py — Backfill scan for wrong initial plan statuses.

Scans all plans in Notion Plans DB, identifies those with incorrect initial
status (not "Not Started" or "Completed"), and optionally repairs them.

Defense in depth for holistic-plan-status-discipline-d4e8a1 (W5).

Usage:
    # Scan only (report findings)
    python ops_scripts/maintenance/scan_and_repair_plan_statuses.py --scan
    
    # Scan + repair (with confirmation)
    python ops_scripts/maintenance/scan_and_repair_plan_statuses.py --repair
    
    # Dry-run repair (show what would be fixed)
    python ops_scripts/maintenance/scan_and_repair_plan_statuses.py --repair --dry-run

Environment:
    NOTION_API_KEY or NOTION_TOKEN — required for Notion API access
    SCAN_PLAN_STATUS_REPAIR_BYPASS=1 — skip safety confirmations

Outputs:
    artifacts/maintenance/plan_status_backfill_scan.json — structured report
    STDERR: human-readable summary

Exit codes:
    0 = OK, no violations or all repaired
    1 = violations found (scan mode)
    2 = error / misconfiguration
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime
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

# Output path
_REPORT_PATH = Path("artifacts/maintenance/plan_status_backfill_scan.json")


@dataclass
class PlanIssue:
    """A plan with incorrect status."""
    slug: str
    page_id: str
    created_time: str
    current_status: str
    recommended_status: str
    issue_type: str  # "forbidden_at_creation" | "unknown_status"
    repaired: bool = False
    repair_error: str | None = None


@dataclass
class ScanReport:
    """Overall scan execution report."""
    timestamp: str
    total_plans_scanned: int
    issues_found: int
    forbidden_count: int  # "In Progress", "Waiting", etc.
    unknown_count: int    # unrecognized statuses
    repaired_count: int
    repair_failed_count: int
    scan_mode: str  # "scan_only" | "dry_run" | "repair"
    issues: list[dict]


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


def _fetch_all_plans() -> list[dict[str, Any]]:
    """Fetch all plans from Notion Plans DB."""
    all_results = []
    has_more = True
    start_cursor = None
    
    while has_more:
        payload: dict[str, Any] = {
            "page_size": 100,
        }
        
        if start_cursor:
            payload["start_cursor"] = start_cursor
        
        response = _call_notion_query(payload)
        results = response.get("results", [])
        all_results.extend(results)
        
        has_more = response.get("has_more", False)
        start_cursor = response.get("next_cursor")
    
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


def _classify_status(status: str) -> tuple[str, str]:
    """
    Classify status and recommend fix.
    
    Returns (issue_type, recommended_status)
    """
    if not status:
        return ("unknown_status", "Not Started")
    
    if status in VALID_CREATION_STATUSES:
        return ("ok", status)
    
    if status in FORBIDDEN_AT_CREATION:
        return ("forbidden_at_creation", "Not Started")
    
    # Unknown status
    return ("unknown_status", "Not Started")


def _patch_plan_status(page_id: str, new_status: str) -> tuple[bool, str | None]:
    """
    Repair plan status via Notion API.
    
    Returns (success, error_message)
    """
    token = _notion_token()
    if not token:
        return False, "No NOTION_TOKEN available for repair"
    
    url = f"{_NOTION_BASE}/pages/{page_id}"
    
    payload = {
        "properties": {
            "Status": {
                "select": {"name": new_status}
            }
        }
    }
    
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
            method="PATCH",
        )
        
        with urllib.request.urlopen(req, timeout=_NOTION_TIMEOUT_S) as resp:
            if resp.status == 200:
                return True, None
            return False, f"HTTP {resp.status}"
            
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}: {e.read().decode('utf-8')[:200]}"
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return False, f"Connection error: {e}"
    except Exception as e:
        return False, f"Unexpected error: {e}"


def _save_report(report: ScanReport) -> None:
    """Save structured report to disk."""
    _REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    with _REPORT_PATH.open("w", encoding="utf-8") as f:
        json.dump(asdict(report), f, indent=2, default=str)


def main() -> int:
    """Main entry point for backfill scan/repair."""
    parser = argparse.ArgumentParser(
        description="Scan and repair plan statuses in Notion Plans DB"
    )
    parser.add_argument(
        "--scan",
        action="store_true",
        help="Scan only (report findings, no repairs)",
    )
    parser.add_argument(
        "--repair",
        action="store_true",
        help="Scan and repair issues",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be repaired (with --repair)",
    )
    
    args = parser.parse_args()
    
    # Determine mode
    if args.repair and args.dry_run:
        mode = "dry_run"
    elif args.repair:
        mode = "repair"
    else:
        mode = "scan_only"
    
    # Check token
    if not _notion_token():
        print(
            "[scan-plan-statuses] ERROR: No NOTION_API_KEY/TOKEN",
            file=sys.stderr,
        )
        return 2
    
    print(
        f"[scan-plan-statuses] Mode: {mode} — scanning all plans...",
        file=sys.stderr,
    )
    
    try:
        # Fetch all plans
        plans = _fetch_all_plans()
        
        # Analyze each plan
        issues: list[PlanIssue] = []
        
        for plan in plans:
            slug = _extract_slug(plan)
            page_id = plan.get("id", "")
            created_time = plan.get("created_time", "")
            status = _extract_status(plan)
            
            issue_type, recommended = _classify_status(status)
            
            if issue_type != "ok":
                issues.append(PlanIssue(
                    slug=slug or "unknown",
                    page_id=page_id,
                    created_time=created_time,
                    current_status=status or "(empty)",
                    recommended_status=recommended,
                    issue_type=issue_type,
                ))
        
        # Categorize
        forbidden = [i for i in issues if i.issue_type == "forbidden_at_creation"]
        unknown = [i for i in issues if i.issue_type == "unknown_status"]
        
        print(
            f"[scan-plan-statuses] Scanned: {len(plans)} | "
            f"Issues: {len(issues)} ({len(forbidden)} forbidden, {len(unknown)} unknown)",
            file=sys.stderr,
        )
        
        # Print issues
        for issue in issues:
            emoji = "🚫" if issue.issue_type == "forbidden_at_creation" else "❓"
            print(
                f"  {emoji} {issue.slug}: '{issue.current_status}' -> '{issue.recommended_status}'",
                file=sys.stderr,
            )
        
        # Repair (if requested)
        repaired = 0
        failed = 0
        
        if mode == "repair" and issues:
            # Safety check
            if os.environ.get("SCAN_PLAN_STATUS_REPAIR_BYPASS") != "1":
                print(
                    f"\n[scan-plan-statuses] WARNING: About to repair {len(issues)} plan(s)",
                    file=sys.stderr,
                )
                print(
                    "[scan-plan-statuses] Set SCAN_PLAN_STATUS_REPAIR_BYPASS=1 to proceed",
                    file=sys.stderr,
                )
                return 2
            
            for issue in issues:
                success, error = _patch_plan_status(
                    issue.page_id,
                    issue.recommended_status,
                )
                if success:
                    issue.repaired = True
                    repaired += 1
                    print(
                        f"  ✅ Repaired: {issue.slug}",
                        file=sys.stderr,
                    )
                else:
                    issue.repair_error = error
                    failed += 1
                    print(
                        f"  ❌ Failed: {issue.slug} — {error}",
                        file=sys.stderr,
                    )
        
        elif mode == "dry_run" and issues:
            print(
                f"\n[scan-plan-statuses] DRY RUN — would repair {len(issues)} plan(s):",
                file=sys.stderr,
            )
            for issue in issues:
                print(
                    f"  → {issue.slug}: '{issue.current_status}' -> '{issue.recommended_status}'",
                    file=sys.stderr,
                )
        
        # Build report
        report = ScanReport(
            timestamp=datetime.utcnow().isoformat() + "Z",
            total_plans_scanned=len(plans),
            issues_found=len(issues),
            forbidden_count=len(forbidden),
            unknown_count=len(unknown),
            repaired_count=repaired,
            repair_failed_count=failed,
            scan_mode=mode,
            issues=[asdict(i) for i in issues],
        )
        
        _save_report(report)
        
        # Summary
        print(
            f"\n[scan-plan-statuses] Report saved: {_REPORT_PATH}",
            file=sys.stderr,
        )
        
        if mode == "repair":
            print(
                f"[scan-plan-statuses] Repaired: {repaired} | Failed: {failed}",
                file=sys.stderr,
            )
        
        # Exit code
        if issues and mode == "scan_only":
            return 1
        return 0
        
    except Exception as e:
        print(
            f"[scan-plan-statuses] ERROR: {e}",
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    sys.exit(main())
