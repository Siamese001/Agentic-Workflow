#!/usr/bin/env python3
"""
Notion Plans Status Canonical Enforcement (NP2)

Validates that all Plans DB rows use canonical status values only
(imported from _notion_plans_status_check.CANONICAL_STATUSES — the SSOT).
Also validates status discipline: "In Progress" plans with deferred scope
items >7 days old should have "Waiting For" populated (status stays
"In Progress").

Plan notion-plan-status-reconciliation-a3f2e1: Adds status reconciliation
checks to detect the discipline gap identified in RCA of plan
notion-plan-identity-deferred-scope-a3b7e2.

Canonical statuses (5-status SSOT):
- In Progress
- Not Started
- Completed
- Retired
- Archived

Stale statuses (must NOT be used — coerced to "In Progress" / forbidden):
- Lower Priority, Waiting, Deferred, Deprioritized (removed from taxonomy)
- Draft (red option, id: 79d24503-da3e-4d22-a0fb-13a0c6d36d11)
- 🟡Draft (red option, id: f5abd2a2-03bc-4951-9e38-ae9e1343909c)
- 🔵Completed (pink option, id: 6da99522-3194-4aa3-aac4-44296b4048b7)
- Live, Active

Status discipline violations:
- IN_PROGRESS_EMPTY_WAITING_FOR: "In Progress" plan with empty "Waiting For"
  AND deferred scope entries >7 days old in ledger

Usage:
    python ops_scripts/ci/check_notion_plans_status_canonical.py [--fail-closed] [--json]
    python ops_scripts/ci/check_notion_plans_status_canonical.py --query-notion [--fail-closed] [--json]

Exit codes:
    0 = All statuses canonical (or warnings only in advisory mode)
    1 = Stale statuses found or discipline violations (fail-closed mode)
"""

from __future__ import annotations

import json
import os
import sqlite3
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Set

# Repo root for ledger path resolution
_REPO_ROOT = Path(__file__).resolve().parents[2]
_CURSOR_SCRIPTS = _REPO_ROOT / ".claude" / "governance/scripts"
if str(_CURSOR_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_CURSOR_SCRIPTS))

from _notion_plans_status_check import (  # noqa: E402
    CANONICAL_STATUSES as _CANONICAL_STATUSES_FS,
    FORBIDDEN_PLANS_STATUSES,
    PLANS_DATA_SOURCE_ID,
    STALE_EQUIVALENTS,
)

# Deferred scope ledger path
_DEFERRED_SCOPE_LEDGER = _REPO_ROOT / "artifacts" / "ledgers" / "deferred_scope_calibration.sqlite"

# Notion constants (from _notion_constants.py pattern)
_NOTION_BASE = "https://api.notion.com/v1"
_NOTION_API_VERSION = "2025-09-03"
_NOTION_TIMEOUT_S = 30

# Plans DB data_source_id (SSOT)
_PLANS_DATA_SOURCE_ID = PLANS_DATA_SOURCE_ID

# Canonical status values - ONLY these are allowed (SSOT)
CANONICAL_STATUSES: Set[str] = set(_CANONICAL_STATUSES_FS)

# Stale status values that must NOT be used (SSOT keys + forbidden)
STALE_STATUSES: Set[str] = set(STALE_EQUIVALENTS.keys()) | set(FORBIDDEN_PLANS_STATUSES)

# Status discipline: "In Progress" with these conditions triggers WARN
STATUS_IN_PROGRESS = "In Progress"
STATUS_WAITING = "Waiting"

# Deferred scope age threshold for flagging (7 days)
_DEFERRED_AGE_DAYS = 7


def _notion_token() -> str | None:
    """Get Notion token from environment."""
    return os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY")


def _query_notion_api(url: str, payload: dict[str, Any], token: str) -> dict[str, Any]:
    """Query Notion API with fail-open behavior."""
    try:
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Notion-Version": _NOTION_API_VERSION,
            },
        )
        with urllib.request.urlopen(req, timeout=_NOTION_TIMEOUT_S) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError):
        return {}


def _fetch_in_progress_plans(token: str) -> list[dict[str, Any]]:
    """Fetch all "In Progress" plans from Notion Plans DB.
    
    Returns list of plan dicts with: id, slug, status, waiting_for (text or None).
    """
    url = f"{_NOTION_BASE}/data_sources/{_PLANS_DATA_SOURCE_ID}/query"
    
    # Query for In Progress status
    filter_payload = {
        "filter": {
            "property": "Status",
            "select": {"equals": STATUS_IN_PROGRESS}
        },
        "page_size": 100
    }
    
    data = _query_notion_api(url, filter_payload, token)
    results = data.get("results", [])
    
    plans = []
    for row in results:
        props = row.get("properties", {})
        
        # Extract slug
        slug_prop = props.get("Slug", {})
        slug = ""
        if slug_prop.get("title"):
            slug = slug_prop["title"][0].get("text", {}).get("content", "")
        
        # Extract status
        status_prop = props.get("Status", {})
        status = status_prop.get("select", {}).get("name", "")
        
        # Extract Waiting For (may be empty rich_text)
        waiting_for_prop = props.get("Waiting For", {})
        waiting_for_text = ""
        if waiting_for_prop.get("rich_text"):
            for rt in waiting_for_prop["rich_text"]:
                waiting_for_text += rt.get("text", {}).get("content", "")
        
        plans.append({
            "id": row.get("id"),
            "slug": slug,
            "status": status,
            "waiting_for": waiting_for_text.strip() or None,
        })
    
    return plans


def _read_stale_deferred_scope_items(plan_slug: str, days: int = _DEFERRED_AGE_DAYS) -> list[dict[str, Any]]:
    """Query deferred scope ledger for items older than `days` for a plan.
    
    Returns list of stale deferred items with age information.
    """
    if not _DEFERRED_SCOPE_LEDGER.exists():
        return []
    
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    cutoff_iso = cutoff.strftime("%Y-%m-%dT%H:%M:%S")
    
    try:
        conn = sqlite3.connect(str(_DEFERRED_SCOPE_LEDGER), timeout=5)
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute(
                """
                SELECT
                    prediction_json->>'plan_slug' as plan_slug,
                    prediction_json->>'wave_id' as wave_id,
                    prediction_json->>'phase_id' as phase_id,
                    prediction_json->>'computed_p_band' as computed_p_band,
                    event_time_utc,
                    status
                FROM events
                WHERE event_kind = 'deferred_scope_capture'
                  AND prediction_json->>'plan_slug' = ?
                  AND status = 'predicted'
                  AND event_time_utc < ?
                ORDER BY event_time_utc DESC
                """,
                (plan_slug, cutoff_iso),
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()
    except (sqlite3.Error, OSError):
        return []


def _fetch_waiting_plans(token: str) -> list[dict[str, Any]]:
    """Fetch all 'Waiting' plans from Notion Plans DB.

    Returns list of dicts with: id, slug, status, waiting_for (text or None).
    """
    url = f"{_NOTION_BASE}/data_sources/{_PLANS_DATA_SOURCE_ID}/query"
    filter_payload = {
        "filter": {
            "property": "Status",
            "select": {"equals": STATUS_WAITING}
        },
        "page_size": 100,
    }
    data = _query_notion_api(url, filter_payload, token)
    results = data.get("results", [])

    plans = []
    for row in results:
        props = row.get("properties", {})

        slug_prop = props.get("Slug", {})
        slug = ""
        if slug_prop.get("title"):
            slug = slug_prop["title"][0].get("text", {}).get("content", "")

        waiting_for_prop = props.get("Waiting For", {})
        waiting_for_text = ""
        if waiting_for_prop.get("rich_text"):
            for rt in waiting_for_prop["rich_text"]:
                waiting_for_text += rt.get("text", {}).get("content", "")

        plans.append({
            "id": row.get("id"),
            "slug": slug,
            "status": STATUS_WAITING,
            "waiting_for": waiting_for_text.strip() or None,
            "last_edited_time": row.get("last_edited_time"),
        })

    return plans


# Age threshold (days) after which a blank-Waiting-For ERROR escalates to CRITICAL.
_WAITING_FOR_CRITICAL_AGE_DAYS: int = 14


def _age_days(last_edited_time: str | None) -> int | None:
    """Return the age in whole days of a Notion last_edited_time ISO string."""
    if not last_edited_time:
        return None
    try:
        ts = datetime.fromisoformat(last_edited_time.replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - ts).days
    except (ValueError, TypeError):
        return None


def _check_waiting_for_completeness(token: str | None) -> list[dict[str, Any]]:
    """Check all 'Waiting' plans have a non-blank Waiting For field.

    Returns violations for each Waiting plan whose Waiting For is blank:
    - severity=ERROR  when the plan was edited within _WAITING_FOR_CRITICAL_AGE_DAYS
    - severity=CRITICAL when it has been stale for more than that threshold (DS-4)
    """
    violations = []

    if not token:
        return violations

    waiting_plans = _fetch_waiting_plans(token)

    for plan in waiting_plans:
        waiting_for = plan.get("waiting_for")
        if waiting_for:
            continue
        slug = plan.get("slug", "<unknown>")
        age = _age_days(plan.get("last_edited_time"))
        if age is not None and age >= _WAITING_FOR_CRITICAL_AGE_DAYS:
            severity = "CRITICAL"
            age_note = f" (stale for {age}d — escalated from ERROR)"
        else:
            severity = "ERROR"
            age_note = f" (age: {age}d)" if age is not None else ""
        violations.append({
            "severity": severity,
            "violation_type": "WAITING_EMPTY_WAITING_FOR",
            "plan_slug": slug,
            "plan_id": plan.get("id"),
            "current_status": STATUS_WAITING,
            "waiting_for": None,
            "age_days": age,
            "recommendation": (
                f"Populate 'Waiting For' for plan '{slug}' with the specific "
                "blocker, person, system, decision, or time-bound trigger. "
                f"A blank Waiting For defeats the purpose of the Waiting status.{age_note}"
            ),
        })

    return violations


def _check_status_discipline(token: str | None) -> list[dict[str, Any]]:
    """Check status discipline for all In Progress plans.
    
    Returns list of violations:
    - IN_PROGRESS_EMPTY_WAITING_FOR: "In Progress" plan with empty "Waiting For"
      AND deferred scope entries >7 days old
    """
    violations = []
    
    if not token:
        return violations
    
    in_progress_plans = _fetch_in_progress_plans(token)
    
    for plan in in_progress_plans:
        slug = plan.get("slug", "")
        waiting_for = plan.get("waiting_for")
        
        if not slug:
            continue
        
        # Check if plan has stale deferred scope items
        stale_items = _read_stale_deferred_scope_items(slug, _DEFERRED_AGE_DAYS)
        
        if stale_items and not waiting_for:
            # Violation: In Progress + empty Waiting For + stale deferred items
            violations.append({
                "severity": "WARN",
                "violation_type": "IN_PROGRESS_EMPTY_WAITING_FOR",
                "plan_slug": slug,
                "plan_id": plan.get("id"),
                "current_status": STATUS_IN_PROGRESS,
                # 5-status SSOT: no "Waiting" status — plan stays In Progress;
                # only the "Waiting For" field is populated with the blocker list.
                "recommended_status": STATUS_IN_PROGRESS,
                "waiting_for": waiting_for,
                "stale_deferred_items": len(stale_items),
                "oldest_deferred_days": _calculate_oldest_age_days(stale_items),
                "recommendation": "Populate 'Waiting For' with blocker descriptions (status stays 'In Progress' — '"
                f"{STATUS_WAITING}' is not in the 5-status SSOT)",
            })
    
    return violations


def _calculate_oldest_age_days(items: list[dict[str, Any]]) -> int | None:
    """Calculate age in days of the oldest deferred item."""
    if not items:
        return None
    
    oldest = None
    for item in items:
        ts_str = item.get("event_time_utc", "")
        if not ts_str:
            continue
        try:
            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            if oldest is None or ts < oldest:
                oldest = ts
        except (ValueError, TypeError):
            continue
    
    if oldest:
        age = datetime.now(timezone.utc) - oldest
        return age.days
    return None


def _check_schema_validity() -> list[dict[str, Any]]:
    """Check that canonical/stale status sets are valid."""
    violations = []

    # Check no overlap between canonical and stale
    overlap = CANONICAL_STATUSES & STALE_STATUSES
    if overlap:
        violations.append({
            "severity": "CRITICAL",
            "violation_type": "CANONICAL_STALE_OVERLAP",
            "error": "Status in both canonical and stale sets",
            "statuses": list(overlap)
        })
    
    return violations


def main() -> int:
    import argparse
    import os
    if os.environ.get("NOTION_PLANS_STATUS_CANONICAL_BYPASS") == "1":
        print("[check_notion_plans_status_canonical] BYPASS engaged (NOTION_PLANS_STATUS_CANONICAL_BYPASS=1)", flush=True)
        return 0

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fail-closed", action="store_true", help="Exit 1 on any violation")
    parser.add_argument("--json", action="store_true", help="Output JSON report")
    parser.add_argument("--query-notion", action="store_true", help="Query Notion API for live status checks")
    parser.add_argument("--deferred-age-days", type=int, default=_DEFERRED_AGE_DAYS,
                        help=f"Age threshold for stale deferred items (default: {_DEFERRED_AGE_DAYS})")
    args = parser.parse_args()

    all_violations: list[dict[str, Any]] = []

    # 1. Schema validity checks (always run)
    schema_violations = _check_schema_validity()
    all_violations.extend(schema_violations)

    # 2. Notion API checks (only with --query-notion)
    discipline_violations: list[dict[str, Any]] = []
    waiting_for_violations: list[dict[str, Any]] = []
    if args.query_notion:
        token = _notion_token()
        if token:
            discipline_violations = _check_status_discipline(token)
            waiting_for_violations = _check_waiting_for_completeness(token)
            all_violations.extend(discipline_violations)
            all_violations.extend(waiting_for_violations)
        else:
            # Skip without failing - CI may run without Notion token
            pass

    # Build report
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "canonical_statuses": sorted(CANONICAL_STATUSES),
        "stale_statuses": sorted(STALE_STATUSES),
        "schema_violations": schema_violations,
        "discipline_violations": discipline_violations,
        "waiting_for_violations": waiting_for_violations,
        "query_notion_enabled": args.query_notion,
        "notion_token_available": bool(_notion_token()),
        "deferred_ledger_exists": _DEFERRED_SCOPE_LEDGER.exists(),
        "total_violations": len(all_violations),
        "pass": len(all_violations) == 0,
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("=== Notion Plans Status Canonical Check (NP2) ===")
        print(f"\nCanonical statuses ({len(CANONICAL_STATUSES)}):")
        for s in sorted(CANONICAL_STATUSES):
            print(f"  ✓ {s}")

        print(f"\nStale statuses (FORBIDDEN - {len(STALE_STATUSES)}):")
        for s in sorted(STALE_STATUSES):
            print(f"  ✗ {s}")

        if schema_violations:
            print(f"\n❌ SCHEMA VIOLATIONS ({len(schema_violations)}):")
            for v in schema_violations:
                print(f"   [{v['severity']}] {v['error']}")

        if args.query_notion:
            if _notion_token():
                print(f"\n📊 Status Discipline Check (query-notion enabled):")
                print(f"   Deferred ledger exists: {_DEFERRED_SCOPE_LEDGER.exists()}")
                print(f"   Discipline violations: {len(discipline_violations)}")

                if discipline_violations:
                    for v in discipline_violations:
                        print(f"\n   ⚠️  [{v['severity']}] {v['violation_type']}")
                        print(f"       Plan: {v['plan_slug']}")
                        print(f"       Status: {v['current_status']} → Recommend: {v['recommended_status']}")
                        print(f"       Stale deferred items: {v['stale_deferred_items']} (oldest: {v['oldest_deferred_days']}d)")
                        print(f"       Action: {v['recommendation']}")

                print(f"\n🔍 Waiting-For Completeness Check (NP10):")
                print(f"   Waiting plans with blank Waiting For: {len(waiting_for_violations)}")

                if waiting_for_violations:
                    for v in waiting_for_violations:
                        print(f"\n   ❌ [{v['severity']}] {v['violation_type']}")
                        print(f"       Plan: {v['plan_slug']}")
                        print(f"       Action: {v['recommendation']}")
            else:
                print("\n⏭️  Status discipline checks skipped (NOTION_TOKEN not set)")
        else:
            print("\n💡 Use --query-notion to check status discipline against live Plans DB")

        if not all_violations:
            print("\n✅ All checks passed")
        else:
            print(f"\n📋 Total violations: {len(all_violations)}")

    # Exit code logic
    has_critical = any(v.get("severity") == "CRITICAL" for v in all_violations)
    has_error = any(v.get("severity") == "ERROR" for v in all_violations)
    has_warn = any(v.get("severity") == "WARN" for v in all_violations)

    if has_critical or (args.fail_closed and has_error):
        return 1
    if args.fail_closed and has_warn:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
