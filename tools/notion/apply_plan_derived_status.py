#!/usr/bin/env python3
"""W4 P4.3 — Apply Plan-derived Status upgrade (option A).

Reads artifacts/notion/backlog_plan_derived_delta.json.
For each row where:
  - Status.classification == "conflict"
  - Status.backlog_is_scorer_default == True  (Backlog Status == "Draft")
  - Status.plan_value in {"Live", "Completed", "Waiting", "Retired", "Archived"}

Patches the Backlog row's Status with the Plan-derived value, plus an
Evidence note and Last Updated timestamp.

Idempotent: re-running after rows are updated will produce 0 eligible rows
(their Status is no longer the scorer-default "Draft").

Flags:
  --dry-run   Compute but do not PATCH.
  --limit N   Process at most N rows (debug).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / ".windsurf" / "scripts"))

from _notion_constants import NOTION_API_VERSION, NOTION_BASE  # noqa: E402

try:
    from tqdm import tqdm
except ImportError:  # pragma: no cover
    tqdm = lambda it, **kw: it  # type: ignore[assignment,misc]

DELTA_JSON = REPO_ROOT / "artifacts" / "notion" / "backlog_plan_derived_delta.json"
PAGE_URL_FMT = f"{NOTION_BASE}/pages/{{}}"
TIMEOUT = 30.0
THROTTLE_S = 0.35

_VALID_PLAN_STATUSES = {"Live", "Completed", "Waiting", "Retired", "Archived"}
_SCORER_DEFAULT_STATUS = "Draft"
_EVIDENCE_NOTE = "W4 P4.3 upgrade — Status promoted from Plan-derived value (was scorer-default Draft)"


def _token() -> str:
    tok = os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY")
    if not tok:
        print("ERROR: set NOTION_TOKEN or NOTION_API_KEY", file=sys.stderr)
        sys.exit(1)
    return tok


def _headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_API_VERSION,
    }


def _patch_page(page_id: str, properties: dict, token: str) -> tuple[bool, str]:
    req = urllib.request.Request(
        PAGE_URL_FMT.format(page_id),
        data=json.dumps({"properties": properties}).encode("utf-8"),
        method="PATCH",
        headers=_headers(token),
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            resp.read()
        return True, "ok"
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")[:300]
        return False, f"http_{exc.code}:{body}"
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return False, f"net:{exc!r}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    if not DELTA_JSON.exists():
        print(f"ERROR: {DELTA_JSON} not found — run audit_backlog_plan_derived.py first", file=sys.stderr)
        return 1

    with DELTA_JSON.open(encoding="utf-8") as fh:
        delta = json.load(fh)

    rows = delta.get("rows") or []

    # Filter to eligible rows
    eligible: list[dict] = []
    for row in rows:
        status_info = (row.get("fields") or {}).get("Status") or {}
        if (
            status_info.get("classification") == "conflict"
            and status_info.get("backlog_is_scorer_default") is True
            and status_info.get("plan_value") in _VALID_PLAN_STATUSES
        ):
            eligible.append(row)

    print(f"Delta rows: {len(rows)}", file=sys.stderr)
    print(f"Eligible (scorer-default → plan upgrade): {len(eligible)}", file=sys.stderr)

    if args.limit is not None:
        eligible = eligible[: args.limit]
        print(f"Limited to: {len(eligible)}", file=sys.stderr)

    token = _token()
    today_iso = date.today().isoformat()
    ok = fail = skip = 0

    bar = tqdm(eligible, desc="Upgrading Status", unit="row", colour="green")
    for row in bar:
        page_id = row.get("page_id")
        if not page_id:
            skip += 1
            continue

        plan_status = row["fields"]["Status"]["plan_value"]
        props: dict = {
            "Status": {"select": {"name": plan_status}},
            "Evidence": {
                "rich_text": [{"type": "text", "text": {"content": _EVIDENCE_NOTE}}]
            },
            "Last Updated": {"date": {"start": today_iso}},
        }

        if args.dry_run:
            ok += 1
            if hasattr(bar, "write"):
                bar.write(f"DRY {page_id}: Status → {plan_status}")
            continue

        success, err = _patch_page(page_id, props, token)
        if success:
            ok += 1
        else:
            fail += 1
            msg = f"FAIL {page_id}: {err}"
            if hasattr(bar, "write"):
                bar.write(msg)
            else:
                print(msg, file=sys.stderr)
        time.sleep(THROTTLE_S)

    print(
        f"\nDone. dry_run={args.dry_run}  ok={ok}  fail={fail}  skip={skip}",
        file=sys.stderr,
    )
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
