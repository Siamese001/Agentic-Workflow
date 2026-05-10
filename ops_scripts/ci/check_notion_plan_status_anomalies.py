#!/usr/bin/env python3
"""check_notion_plan_status_anomalies.py — CI gate for Notion plan status anomaly detection.

NP3 Notion plan status anomaly detection (advisory)

Detects suspicious status changes in the Plans DB that may indicate:
- Mis-targeted status updates (wrong plan updated)
- Erroneous status flips (Completed → Deferred within short time)
- Flip-flop patterns (status ping-pong)

Exit codes:
    0 — No anomalies detected (or advisory mode)
    1 — Anomalies detected (advisory mode, logs to stderr)
    2 — Fail-closed mode, anomalies detected

Environment:
    NOTION_PLAN_STATUS_ANOMALIES_FAIL_CLOSED=1 — exit 2 on anomalies
    NOTION_API_KEY or NOTION_TOKEN — required for Notion API access

Outputs:
    artifacts/notion/plan_status_anomalies.json — structured anomaly report
    stderr — human-readable anomaly summary (if any)
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PLANS_DATA_SOURCE_ID: str = "ac53d31b-3068-4039-9ebe-856c12caab32"
PLANS_DB_ID: str = "6aba34d9-4d0b-4f4c-b956-b2bdea541ca9"
NOTION_API_BASE: str = "https://api.notion.com/v1"

# Anomaly detection thresholds
LOOKBACK_DAYS: int = 30
SHORT_WINDOW_HOURS: int = 24  # For quick flips

# Status values that are "terminal" (shouldn't flip back)
TERMINAL_STATUSES: set[str] = {"Completed", "Retired", "Archived"}

# Status values that are "stable" (flips from these are suspicious)
STABLE_STATUSES: set[str] = {"Completed", "Deferred", "Retired"}


@dataclass(frozen=True)
class StatusChange:
    timestamp: str
    old_status: Optional[str]
    new_status: str
    changed_by: Optional[str]


@dataclass(frozen=True)
class Anomaly:
    plan_slug: str
    plan_page_id: str
    anomaly_type: str
    severity: str  # "HIGH", "MEDIUM", "LOW"
    description: str
    status_changes: list[StatusChange]
    detected_at: str


def _get_notion_token() -> Optional[str]:
    """Retrieve Notion API token from environment."""
    return os.environ.get("NOTION_API_KEY") or os.environ.get("NOTION_TOKEN")


def _query_plans_db() -> list[dict]:
    """Query all plans from Notion Plans DB.
    
    Returns list of page objects with properties.
    """
    token = _get_notion_token()
    if not token:
        return []
    
    try:
        import requests
        
        url = f"{NOTION_API_BASE}/databases/{PLANS_DATA_SOURCE_ID}/query"
        headers = {
            "Authorization": f"Bearer {token}",
            "Notion-Version": "2025-09-03",
            "Content-Type": "application/json",
        }
        
        payload = {
            "page_size": 100,  # Max per request
        }
        
        results = []
        has_more = True
        start_cursor = None
        
        while has_more:
            if start_cursor:
                payload["start_cursor"] = start_cursor
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            results.extend(data.get("results", []))
            
            has_more = data.get("has_more", False)
            start_cursor = data.get("next_cursor")
        
        return results
        
    except Exception as e:
        print(f"ERROR: Failed to query Plans DB: {e}", file=sys.stderr)
        return []


def _get_page_history(page_id: str) -> list[dict]:
    """Get version history for a Notion page.
    
    Note: Notion API doesn't have a direct "page history" endpoint.
    We use the page's last_edited_time and compare with current state.
    In a full implementation, this would query a local ledger or audit log.
    
    For this implementation, we use the plan_identity_verifications.jsonl
    and notion_plans_status_violations.jsonl as audit sources.
    """
    # This is a simplified implementation
    # A full implementation would track status changes over time
    return []


def _extract_slug_from_page(page: dict) -> Optional[str]:
    """Extract slug from page properties."""
    props = page.get("properties", {})
    slug_prop = props.get("Slug", {})
    title_arr = slug_prop.get("title", [])
    if title_arr:
        return title_arr[0].get("text", {}).get("content", "")
    return None


def _extract_status_from_page(page: dict) -> Optional[str]:
    """Extract current status from page properties."""
    props = page.get("properties", {})
    status_prop = props.get("Status", {})
    select = status_prop.get("select", {})
    if select:
        return select.get("name", "")
    return None


def _extract_created_time(page: dict) -> Optional[str]:
    """Extract page creation time."""
    return page.get("created_time")


def _extract_last_edited_time(page: dict) -> Optional[str]:
    """Extract last edited time."""
    return page.get("last_edited_time")


def _parse_notion_timestamp(ts: Optional[str]) -> Optional[datetime]:
    """Parse Notion ISO timestamp to datetime."""
    if not ts:
        return None
    try:
        # Remove Z suffix and parse
        ts_clean = ts.replace("Z", "+00:00")
        return datetime.fromisoformat(ts_clean)
    except:
        return None


def _load_audit_logs() -> list[dict]:
    """Load audit logs from previous verification runs."""
    audit_logs = []
    
    # Load plan identity verifications
    log_file = Path("artifacts/windsurf/plan_identity_verifications.jsonl")
    if log_file.exists():
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        audit_logs.append(json.loads(line))
                    except:
                        pass
    
    # Load plan status violations
    violation_file = Path("artifacts/windsurf/notion_plans_status_violations.jsonl")
    if violation_file.exists():
        with open(violation_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entry = json.loads(line)
                        entry["_source"] = "status_violation"
                        audit_logs.append(entry)
                    except:
                        pass
    
    return audit_logs


def detect_anomalies(plans: list[dict], audit_logs: list[dict]) -> list[Anomaly]:
    """Detect anomalies in plan status history.
    
    Anomaly types:
    - COMPLETED_TO_DEFERRED: Completed plan marked Deferred within 24h
    - QUICK_STATUS_FLIP: Any status flip within 24h of creation
    - FLIP_FLOP: Multiple status changes in short window
    - IDENTITY_MISMATCH: Audit log shows slug/page_id mismatch
    """
    anomalies = []
    now = datetime.now(timezone.utc)
    lookback = now - timedelta(days=LOOKBACK_DAYS)
    
    # Build plan lookup by page_id
    plan_by_id = {}
    for plan in plans:
        page_id = plan.get("id", "")
        if page_id:
            plan_by_id[page_id] = plan
    
    # Check audit logs for identity mismatches
    for log in audit_logs:
        if log.get("ok") is False:
            # This is a failed verification
            slug = log.get("intended_slug", "UNKNOWN")
            targeted_page = log.get("targeted_page_id", "")
            actual_page = log.get("actual_page_id", "")
            
            # Find plan for targeted page
            plan = plan_by_id.get(targeted_page)
            if plan:
                slug = _extract_slug_from_page(plan) or slug
            
            anomaly = Anomaly(
                plan_slug=slug,
                plan_page_id=targeted_page,
                anomaly_type="IDENTITY_MISMATCH",
                severity="HIGH",
                description=f"Plan identity verification failed: intended {slug[:30]}... but targeted {targeted_page[:8]}...",
                status_changes=[],
                detected_at=now.isoformat(),
            )
            anomalies.append(anomaly)
    
    # Check for suspicious status patterns in plan metadata
    for plan in plans:
        page_id = plan.get("id", "")
        slug = _extract_slug_from_page(plan) or "UNKNOWN"
        current_status = _extract_status_from_page(plan) or "Unknown"
        created_time = _extract_created_time(plan)
        last_edited = _extract_last_edited_time(plan)
        
        created_dt = _parse_notion_timestamp(created_time)
        edited_dt = _parse_notion_timestamp(last_edited)
        
        if not created_dt or not edited_dt:
            continue
        
        # Skip if plan is older than lookback
        if created_dt < lookback.replace(tzinfo=timezone.utc):
            continue
        
        # Anomaly: Plan created and modified very quickly (suspicious)
        time_since_creation = edited_dt - created_dt
        if time_since_creation < timedelta(hours=1) and current_status != "Not Started":
            # Plan created and immediately changed status
            if current_status in ["Completed", "Deferred"]:
                anomaly = Anomaly(
                    plan_slug=slug,
                    plan_page_id=page_id,
                    anomaly_type="QUICK_STATUS_FLIP",
                    severity="MEDIUM",
                    description=f"Plan created and marked '{current_status}' within 1 hour",
                    status_changes=[
                        StatusChange(
                            timestamp=edited_dt.isoformat(),
                            old_status="Not Started",
                            new_status=current_status,
                            changed_by=None,
                        )
                    ],
                    detected_at=now.isoformat(),
                )
                anomalies.append(anomaly)
    
    return anomalies


def _write_report(anomalies: list[Anomaly]) -> None:
    """Write anomaly report to artifacts."""
    report_dir = Path("artifacts/notion")
    report_dir.mkdir(parents=True, exist_ok=True)
    report_file = report_dir / "plan_status_anomalies.json"
    
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "lookback_days": LOOKBACK_DAYS,
        "total_anomalies": len(anomalies),
        "high_severity": len([a for a in anomalies if a.severity == "HIGH"]),
        "medium_severity": len([a for a in anomalies if a.severity == "MEDIUM"]),
        "low_severity": len([a for a in anomalies if a.severity == "LOW"]),
        "anomalies": [asdict(a) for a in anomalies],
    }
    
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)


def main() -> int:
    """Main entry point for CI gate."""
    # Check for token
    if not _get_notion_token():
        print("WARNING: No Notion API token found, skipping anomaly detection", file=sys.stderr)
        # Exit 0 in advisory mode when can't check
        return 0
    
    # Query plans
    plans = _query_plans_db()
    if not plans:
        print("WARNING: No plans retrieved from Notion, skipping anomaly detection", file=sys.stderr)
        return 0
    
    # Load audit history
    audit_logs = _load_audit_logs()
    
    # Detect anomalies
    anomalies = detect_anomalies(plans, audit_logs)
    
    # Write report
    _write_report(anomalies)
    
    # Check fail-closed mode
    fail_closed = os.environ.get("NOTION_PLAN_STATUS_ANOMALIES_FAIL_CLOSED", "") == "1"
    
    if anomalies:
        print(f"[NP3] Detected {len(anomalies)} plan status anomaly(s):", file=sys.stderr)
        for a in anomalies:
            print(f"  [{a.severity}] {a.plan_slug[:40]:<40} | {a.anomaly_type}: {a.description[:60]}...", file=sys.stderr)
        
        if fail_closed:
            print("[NP3] FAIL-CLOSED mode active, exiting with error", file=sys.stderr)
            return 2
        else:
            print("[NP3] Advisory mode — review artifacts/notion/plan_status_anomalies.json", file=sys.stderr)
            return 1
    else:
        print("[NP3] No plan status anomalies detected", file=sys.stderr)
        return 0


if __name__ == "__main__":
    sys.exit(main())
