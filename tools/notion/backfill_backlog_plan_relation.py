#!/usr/bin/env python3
"""Backfill the Backlog Items `Plan` relation column for rows that carry a
`Plan File` slug but no resolved relation.

Strategy:
  * Page through all Backlog rows.
  * Filter: `Plan.relation = []` AND `Plan File` non-empty.
  * For each: derive slug from `Plan File` (strip `.md`), resolve to a
    Plans-DB page id via `_resolve_plan_page_id` (capture-hook sibling).
  * On hit: PATCH with `Plan = {relation: [{id}]}` + `Last Updated = today`.
  * On miss: log to `artifacts/cursor/backlog_plan_linkage_misses.jsonl`
    for W2 true-orphan triage.

Idempotent: rows whose relation is already set are skipped.
Fail-open per row; single HTTP failure does not stop the sweep.
Requires NOTION_TOKEN or NOTION_API_KEY.

Flags:
  --dry-run    Compute but do not PATCH or log misses.
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
sys.path.insert(0, str(REPO_ROOT / ".cursor" / "scripts" / "_legacy_windsurf"))

from _notion_constants import (  # noqa: E402
    NOTION_API_VERSION,
    NOTION_BASE,
    WAVE_PHASE_DATA_SOURCE_ID,
)
from post_cursor_agent_deferred_scope_capture import _resolve_plan_page_id  # noqa: E402

try:
    from tqdm import tqdm
except ImportError:  # pragma: no cover
    tqdm = lambda it, **kw: it  # type: ignore[assignment,misc]

QUERY_URL = f"{NOTION_BASE}/data_sources/{WAVE_PHASE_DATA_SOURCE_ID}/query"
PAGE_URL_FMT = f"{NOTION_BASE}/pages/{{page_id}}"
MISS_LOG = REPO_ROOT / "artifacts" / "windsurf" / "backlog_plan_linkage_misses.jsonl"
TIMEOUT = 30.0
THROTTLE_S = 0.35


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


def _rich_text_str(prop: dict | None) -> str:
    if not prop or prop.get("type") != "rich_text":
        return ""
    return "".join((r.get("plain_text") or "") for r in (prop.get("rich_text") or []))


def _relation_ids(prop: dict | None) -> list[str]:
    if not prop or prop.get("type") != "relation":
        return []
    return [r.get("id") for r in (prop.get("relation") or []) if r.get("id")]


def _patch(page_id: str, properties: dict, token: str) -> tuple[bool, str]:
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


def _slug_from_plan_file(plan_file: str) -> str:
    s = plan_file.strip()
    if s.endswith(".md"):
        s = s[:-3]
    # Strip any leading directory prefix (defensive; usually already bare slug)
    if "/" in s:
        s = s.rsplit("/", 1)[-1]
    if "\\" in s:
        s = s.rsplit("\\", 1)[-1]
    return s


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    token = _token()
    print("Querying Backlog Items…", file=sys.stderr)
    rows = _query_all(token)
    print(f"Total rows: {len(rows)}", file=sys.stderr)

    eligible: list[tuple[dict, str, str]] = []
    for row in rows:
        rel = _relation_ids(_prop(row, "Plan"))
        if rel:
            continue
        plan_file = _rich_text_str(_prop(row, "Plan File"))
        if not plan_file.strip():
            continue
        slug = _slug_from_plan_file(plan_file)
        eligible.append((row, plan_file, slug))

    print(f"Rows eligible (slug present, no relation): {len(eligible)}", file=sys.stderr)

    if args.limit is not None:
        eligible = eligible[: args.limit]
        print(f"Limited to: {len(eligible)}", file=sys.stderr)

    today_iso = date.today().isoformat()
    ok = 0
    miss = 0
    fail = 0

    if not args.dry_run:
        MISS_LOG.parent.mkdir(parents=True, exist_ok=True)

    bar = tqdm(eligible, desc="Linking", unit="row", colour="cyan")
    for row, plan_file, slug in bar:
        page_id = row.get("id")
        resolved = _resolve_plan_page_id(slug, token)

        if not resolved:
            miss += 1
            if not args.dry_run:
                with MISS_LOG.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps({
                        "ts": today_iso,
                        "backlog_page_id": page_id,
                        "plan_file": plan_file,
                        "slug": slug,
                    }) + "\n")
            tqdm.write(f"MISS {page_id}: slug='{slug}' not found in Plans DB")
            time.sleep(THROTTLE_S)
            continue

        if args.dry_run:
            ok += 1
            continue

        props = {
            "Plan": {"relation": [{"id": resolved}]},
            "Last Updated": {"date": {"start": today_iso}},
        }
        success, err = _patch(page_id, props, token)
        if success:
            ok += 1
        else:
            fail += 1
            tqdm.write(f"FAIL {page_id}: {err}")
        time.sleep(THROTTLE_S)

    print(
        f"\nDone. linked={ok} miss={miss} fail={fail} "
        f"(dry_run={args.dry_run})",
        file=sys.stderr,
    )
    if miss and not args.dry_run:
        print(f"Miss log: {MISS_LOG}", file=sys.stderr)
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
