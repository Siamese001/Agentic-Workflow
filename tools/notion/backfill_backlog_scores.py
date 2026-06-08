#!/usr/bin/env python3
"""Backfill Impact Score + P-Band (and Layer/Surface/Fan-In defaults) on
Backlog Items rows that predate the MECE v2 capture hook.

Strategy:
  * Page through all rows.
  * For each row missing Impact Score:
      - Read existing Layer / Fan-In / Surface; default L_MIXED / 0 / None.
      - coverage_gap_pct defaults to 50.0 (midpoint — no better signal for
        legacy rows since Coverage Gap % column was deleted 2026-05-03).
      - Score via tools.priority.deferred_scope_scorer.score_deferred_scope.
      - PATCH the page with Impact Score, P-Band, Last Updated, and any
        defaulted Layer/Surface/Fan-In.

Idempotent: rows that already have Impact Score are skipped.
Fail-open per row; single-row HTTP failure does not stop the sweep.
Requires NOTION_TOKEN or NOTION_API_KEY.

Flags:
  --dry-run    Compute but do not PATCH.
  --limit N    Process at most N eligible rows (debug).
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
sys.path.insert(0, str(REPO_ROOT / ".claude" / "governance/scripts"))

from _notion_constants import (  # noqa: E402
    NOTION_API_VERSION,
    NOTION_BASE,
    WAVE_PHASE_DATA_SOURCE_ID,
)
from tools.priority.deferred_scope_scorer import score_deferred_scope  # noqa: E402

try:
    from tqdm import tqdm
except ImportError:  # pragma: no cover
    tqdm = lambda it, **kw: it  # type: ignore[assignment,misc]

QUERY_URL = f"{NOTION_BASE}/data_sources/{WAVE_PHASE_DATA_SOURCE_ID}/query"
PAGE_URL_FMT = f"{NOTION_BASE}/pages/{{page_id}}"
TIMEOUT = 30.0
DEFAULT_COVERAGE_GAP_PCT = 50.0


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


def _query_all(token: str) -> list[dict]:
    rows: list[dict] = []
    cursor: str | None = None
    while True:
        body: dict = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        req = urllib.request.Request(
            QUERY_URL,
            data=json.dumps(body).encode("utf-8"),
            method="POST",
            headers=_headers(token),
        )
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        rows.extend(data.get("results") or [])
        if not data.get("has_more"):
            return rows
        cursor = data.get("next_cursor")


def _prop(row: dict, name: str) -> dict | None:
    return (row.get("properties") or {}).get(name)


def _select_name(prop: dict | None) -> str | None:
    if not prop or prop.get("type") != "select":
        return None
    v = prop.get("select")
    return (v or {}).get("name") if v else None


def _number_value(prop: dict | None) -> float | None:
    if not prop or prop.get("type") != "number":
        return None
    return prop.get("number")


def _patch_page(page_id: str, properties: dict, token: str) -> tuple[bool, str]:
    req = urllib.request.Request(
        PAGE_URL_FMT.format(page_id=page_id),
        data=json.dumps({"properties": properties}).encode("utf-8"),
        method="PATCH",
        headers=_headers(token),
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            resp.read()
        return True, "ok"
    except urllib.error.HTTPError as exc:
        return False, f"http_{exc.code}:{exc.read().decode('utf-8', 'replace')[:200]}"
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return False, f"net:{exc!r}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    token = _token()
    print("Querying Backlog Items…", file=sys.stderr)
    rows = _query_all(token)
    print(f"Total rows: {len(rows)}", file=sys.stderr)

    eligible: list[dict] = [r for r in rows if _number_value(_prop(r, "Impact Score")) is None]
    print(f"Rows missing Impact Score: {len(eligible)}", file=sys.stderr)

    if args.limit is not None:
        eligible = eligible[: args.limit]
        print(f"Limited to: {len(eligible)}", file=sys.stderr)

    today_iso = date.today().isoformat()
    ok = 0
    fail = 0
    skipped = 0

    bar = tqdm(eligible, desc="Backfilling", unit="row", colour="green")
    for row in bar:
        page_id = row.get("id")
        if not page_id:
            skipped += 1
            continue

        layer = _select_name(_prop(row, "Layer")) or "L_MIXED"
        surface = _select_name(_prop(row, "Surface")) or "None"
        fan_in_val = _number_value(_prop(row, "Fan-In"))
        fan_in = int(fan_in_val) if fan_in_val is not None else 0

        result = score_deferred_scope(
            layer=layer,
            fan_in=fan_in,
            surface=surface,
            coverage_gap_pct=DEFAULT_COVERAGE_GAP_PCT,
        )

        props: dict = {
            "Impact Score": {"number": round(float(result.impact_score), 2)},
            "P-Band": {"select": {"name": result.band}},
            "Last Updated": {"date": {"start": today_iso}},
        }
        # Also stamp defaults into previously-empty classification cells so the
        # row is fully populated going forward.
        if _select_name(_prop(row, "Layer")) is None:
            props["Layer"] = {"select": {"name": layer}}
        if _select_name(_prop(row, "Surface")) is None:
            props["Surface"] = {"select": {"name": surface}}
        if _number_value(_prop(row, "Fan-In")) is None:
            props["Fan-In"] = {"number": fan_in}

        if args.dry_run:
            ok += 1
            continue

        success, err = _patch_page(page_id, props, token)
        if success:
            ok += 1
        else:
            fail += 1
            tqdm.write(f"FAIL {page_id}: {err}")
        # Light throttle — Notion rate limit is ~3 rps
        time.sleep(0.35)

    print(
        f"\nDone. ok={ok} fail={fail} skipped={skipped} "
        f"(dry_run={args.dry_run})",
        file=sys.stderr,
    )
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
