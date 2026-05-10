#!/usr/bin/env python3
"""
Notion Plans Waiting-For Completeness Gate (NP10)

Enforces that every Plans DB row with Status="Waiting" has a non-blank
"Waiting For" property.  A blank Waiting For makes the blocked state
unactionable — no one knows what to resolve.

Queries the Notion Plans DB for all Waiting-status rows and reports an
ERROR for each row where Waiting For is empty or absent.

Usage:
    python ops_scripts/ci/check_notion_plans_waiting_for.py [--fail-closed] [--json]

Exit codes:
    0 = All Waiting plans have Waiting For populated (or no Notion token)
    1 = One or more Waiting plans have blank Waiting For (fail-closed mode only)

Bypass:
    NOTION_PLANS_WAITING_FOR_BYPASS=1   — skip entirely, log bypass row
Fail-closed:
    NOTION_PLANS_WAITING_FOR_FAIL_CLOSED=1  — exit 1 on any ERROR
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]

_NOTION_BASE = "https://api.notion.com/v1"
_NOTION_API_VERSION = "2025-09-03"
_NOTION_TIMEOUT_S = 30

_PLANS_DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"

_REPORT_PATH = _REPO_ROOT / "artifacts" / "ci" / "np10_waiting_for_gate.json"


def _notion_token() -> str | None:
    return os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY")


def _is_bypass() -> bool:
    return os.environ.get("NOTION_PLANS_WAITING_FOR_BYPASS", "").strip() == "1"


def _is_fail_closed() -> bool:
    return os.environ.get("NOTION_PLANS_WAITING_FOR_FAIL_CLOSED", "").strip() == "1"


def _make_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": _NOTION_API_VERSION,
    }


def _query_waiting_plans(token: str) -> list[dict[str, Any]]:
    """Fetch ALL Plans DB rows with Status=Waiting using cursor pagination.

    Notion's query API returns at most 100 results per call. This function
    follows has_more + next_cursor until the full result set is retrieved
    (DS-7: pagination support).
    """
    url = f"{_NOTION_BASE}/data_sources/{_PLANS_DATA_SOURCE_ID}/query"
    plans: list[dict[str, Any]] = []
    cursor: str | None = None

    while True:
        payload: dict[str, Any] = {
            "filter": {
                "property": "Status",
                "select": {"equals": "Waiting"},
            },
            "page_size": 100,
        }
        if cursor:
            payload["start_cursor"] = cursor

        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=body,
            method="POST",
            headers=_make_headers(token),
        )
        try:
            with urllib.request.urlopen(req, timeout=_NOTION_TIMEOUT_S) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError):
            break

        for row in data.get("results", []):
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
                "id": row.get("id", ""),
                "slug": slug or "<no-slug>",
                "waiting_for": waiting_for_text.strip() or None,
            })

        if data.get("has_more") and data.get("next_cursor"):
            cursor = data["next_cursor"]
        else:
            break

    return plans


def evaluate(token: str | None) -> dict[str, Any]:
    """Run the check and return a structured result dict."""
    if not token:
        return {
            "status": "skipped",
            "reason": "NOTION_TOKEN not set",
            "violations": [],
            "total_waiting": 0,
            "pass": True,
        }

    plans = _query_waiting_plans(token)
    violations = []
    for plan in plans:
        if plan["waiting_for"]:
            continue
        violations.append({
            "severity": "ERROR",
            "violation_type": "WAITING_EMPTY_WAITING_FOR",
            "plan_slug": plan["slug"],
            "plan_id": plan["id"],
            "recommendation": (
                f"Populate 'Waiting For' on plan '{plan['slug']}' with the "
                "specific blocker, person, system, decision, or time-bound "
                "trigger this plan is waiting on."
            ),
        })

    return {
        "status": "checked",
        "total_waiting": len(plans),
        "violation_count": len(violations),
        "violations": violations,
        "pass": len(violations) == 0,
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fail-closed", action="store_true",
                        help="Exit 1 on any ERROR violation")
    parser.add_argument("--json", action="store_true",
                        help="Output JSON report to stdout")
    args = parser.parse_args()

    fail_closed = args.fail_closed or _is_fail_closed()

    if _is_bypass():
        print("[NP10] BYPASS active (NOTION_PLANS_WAITING_FOR_BYPASS=1)", file=sys.stderr)
        return 0

    token = _notion_token()
    result = evaluate(token)

    result["timestamp"] = datetime.now(timezone.utc).isoformat()
    result["gate"] = "NP10"
    result["fail_closed"] = fail_closed

    # Write report artifact.
    try:
        _REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        _REPORT_PATH.write_text(json.dumps(result, indent=2), encoding="utf-8")
    except OSError:
        pass

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("=== NP10 Notion Plans Waiting-For Completeness ===")
        status_str = result.get("status", "unknown")
        if status_str == "skipped":
            print(f"SKIPPED: {result.get('reason')}")
            return 0

        total = result.get("total_waiting", 0)
        violations = result.get("violations", [])
        print(f"Waiting-status plans: {total}")
        print(f"Violations (blank Waiting For): {len(violations)}")

        if violations:
            for v in violations:
                print(f"\n  [ERROR] WAITING_EMPTY_WAITING_FOR")
                print(f"    Plan : {v['plan_slug']}")
                print(f"    Fix  : {v['recommendation']}")
        else:
            print("\n✅ All Waiting plans have Waiting For populated")

    has_error = bool(result.get("violations"))
    if fail_closed and has_error:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
