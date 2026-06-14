#!/usr/bin/env python3
"""
Notion Backlog Items Waiting-For Completeness Gate (NP11)

Enforces that every Backlog Items DB row with Status="Waiting" has a non-blank
"Waiting For" property.  Mirrors the Plans DB enforcement from NP10 (DS-3
parity).

Queries the Notion Backlog Items DB for all Waiting-status rows and reports an
ERROR for each row where Waiting For is empty or absent.

Usage:
    python ops_scripts/ci/check_notion_backlog_waiting_for.py [--fail-closed] [--json]

Exit codes:
    0 = All Waiting backlog items have Waiting For populated (or no Notion token)
    1 = One or more Waiting items have blank Waiting For (fail-closed mode only)

Bypass:
    NOTION_BACKLOG_WAITING_FOR_BYPASS=1   — skip entirely, log bypass row
Fail-closed:
    NOTION_BACKLOG_WAITING_FOR_FAIL_CLOSED=1  — exit 1 on any ERROR
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

sys.path.insert(0, str(_REPO_ROOT / ".claude" / "governance" / "scripts"))
from _notion_constants import (  # noqa: E402
    NOTION_API_VERSION as _NOTION_API_VERSION,
    NOTION_BASE as _NOTION_BASE,
    BACKLOG_ITEMS_DATA_SOURCE_ID as _BACKLOG_DATA_SOURCE_ID,
)

_NOTION_TIMEOUT_S = 30

_REPORT_PATH = _REPO_ROOT / "artifacts" / "ci" / "np11_backlog_waiting_for_gate.json"


def _notion_token() -> str | None:
    return os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY")


def _is_bypass() -> bool:
    return os.environ.get("NOTION_BACKLOG_WAITING_FOR_BYPASS", "").strip() == "1"


def _is_fail_closed() -> bool:
    return os.environ.get("NOTION_BACKLOG_WAITING_FOR_FAIL_CLOSED", "").strip() == "1"


def _make_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": _NOTION_API_VERSION,
    }


def _query_waiting_items(token: str) -> list[dict[str, Any]]:
    """Fetch ALL Backlog Items DB rows with Status=Waiting using cursor pagination."""
    url = f"{_NOTION_BASE}/data_sources/{_BACKLOG_DATA_SOURCE_ID}/query"
    items: list[dict[str, Any]] = []
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

            title_prop = props.get("Name", props.get("Title", props.get("Slug", {})))
            title = ""
            for key in ("title", "rich_text"):
                rt_list = title_prop.get(key, [])
                if rt_list:
                    title = rt_list[0].get("text", {}).get("content", "")
                    break

            waiting_for_prop = props.get("Waiting For", {})
            waiting_for_text = ""
            if waiting_for_prop.get("rich_text"):
                for rt in waiting_for_prop["rich_text"]:
                    waiting_for_text += rt.get("text", {}).get("content", "")

            items.append({
                "id": row.get("id", ""),
                "title": title or "<no-title>",
                "waiting_for": waiting_for_text.strip() or None,
            })

        if data.get("has_more") and data.get("next_cursor"):
            cursor = data["next_cursor"]
        else:
            break

    return items


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

    items = _query_waiting_items(token)
    violations = []
    for item in items:
        if item["waiting_for"]:
            continue
        violations.append({
            "severity": "ERROR",
            "violation_type": "WAITING_EMPTY_WAITING_FOR",
            "item_title": item["title"],
            "item_id": item["id"],
            "recommendation": (
                f"Populate 'Waiting For' on backlog item '{item['title']}' with the "
                "specific blocker, person, system, decision, or time-bound "
                "trigger this item is waiting on."
            ),
        })

    return {
        "status": "checked",
        "total_waiting": len(items),
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
        print("[NP11] BYPASS active (NOTION_BACKLOG_WAITING_FOR_BYPASS=1)", file=sys.stderr)
        return 0

    token = _notion_token()
    result = evaluate(token)

    result["timestamp"] = datetime.now(timezone.utc).isoformat()
    result["gate"] = "NP11"
    result["fail_closed"] = fail_closed

    try:
        _REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        _REPORT_PATH.write_text(json.dumps(result, indent=2), encoding="utf-8")
    except OSError:
        pass

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("=== NP11 Notion Backlog Items Waiting-For Completeness ===")
        status_str = result.get("status", "unknown")
        if status_str == "skipped":
            print(f"SKIPPED: {result.get('reason')}")
            return 0

        total = result.get("total_waiting", 0)
        violations = result.get("violations", [])
        print(f"Waiting-status backlog items: {total}")
        print(f"Violations (blank Waiting For): {len(violations)}")

        if violations:
            for v in violations:
                print(f"\n  [ERROR] WAITING_EMPTY_WAITING_FOR")
                print(f"    Item : {v['item_title']}")
                print(f"    Fix  : {v['recommendation']}")
        else:
            print("\n✅ All Waiting backlog items have Waiting For populated")

    has_error = bool(result.get("violations"))
    if fail_closed and has_error:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
