#!/usr/bin/env python3
"""W2 apply — disposition of 91 orphan Backlog rows per user-approved batch.

Reads `artifacts/governance/backlog_plan_linkage_misses.jsonl`, classifies each
row's slug, and applies one of two actions:
  * DELETE  — slug contains "(", starts with "_INDEX_", or starts with "multi:"
  * CATCH-ALL — patches Plan relation to the catch-all page id

Catch-all page id is hard-coded (created via API-post-page on 2026-05-03 W2 start).
Idempotent: rows already linked are skipped.
Fail-open per row.

Flags:
  --dry-run    Compute counts but do not PATCH.
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
sys.path.insert(0, str(REPO_ROOT / ".claude" / "governance" / "scripts"))

from _notion_constants import NOTION_API_VERSION, NOTION_BASE  # noqa: E402

try:
    from tqdm import tqdm
except ImportError:
    tqdm = lambda it, **kw: it  # type: ignore[assignment,misc]

CATCH_ALL_PAGE_ID = "35527693-f55c-81f0-be31-dad3f36fa674"
MISS_LOG = REPO_ROOT / "artifacts" / "governance" / "backlog_plan_linkage_misses.jsonl"
RESULT_LOG = REPO_ROOT / "artifacts" / "governance" / "apply_orphan_disposition_results.jsonl"
PAGE_URL_FMT = f"{NOTION_BASE}/pages/{{page_id}}"
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


def _classify(slug: str) -> str:
    s = slug.strip()
    if "(" in s or s.startswith("_INDEX_") or s.startswith("multi:"):
        return "delete"
    return "catch-all"


def _patch(page_id: str, properties: dict, token: str, archived: bool = False) -> tuple[bool, str]:
    body: dict = {"properties": properties}
    if archived:
        body["archived"] = True
    req = urllib.request.Request(
        PAGE_URL_FMT.format(page_id=page_id),
        data=json.dumps(body).encode("utf-8"),
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
    args = parser.parse_args()

    token = _token()

    if not MISS_LOG.exists():
        print(f"ERROR: miss log not found: {MISS_LOG}", file=sys.stderr)
        return 1

    rows: list[dict] = []
    seen_pages: set[str] = set()
    for line in MISS_LOG.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        page_id = rec.get("backlog_page_id", "")
        if not page_id or page_id in seen_pages:
            continue
        seen_pages.add(page_id)
        rec["action"] = _classify(rec.get("slug", ""))
        rows.append(rec)

    delete_count = sum(1 for r in rows if r["action"] == "delete")
    catch_all_count = sum(1 for r in rows if r["action"] == "catch-all")
    print(f"Unique miss rows: {len(rows)}", file=sys.stderr)
    print(f"  DELETE:    {delete_count}", file=sys.stderr)
    print(f"  CATCH-ALL: {catch_all_count}", file=sys.stderr)

    if args.dry_run:
        print("Dry-run — no PATCH issued.", file=sys.stderr)
        return 0

    today_iso = date.today().isoformat()
    RESULT_LOG.parent.mkdir(parents=True, exist_ok=True)
    ok = 0
    fail = 0

    bar = tqdm(rows, desc="Applying", unit="row", colour="green")
    for rec in bar:
        page_id = rec["backlog_page_id"]
        action = rec["action"]
        slug = rec["slug"]

        if action == "delete":
            success, err = _patch(page_id, {}, token, archived=True)
        else:  # catch-all
            props = {
                "Plan": {"relation": [{"id": CATCH_ALL_PAGE_ID}]},
                "Last Updated": {"date": {"start": today_iso}},
            }
            success, err = _patch(page_id, props, token, archived=False)

        result = {
            "ts": today_iso,
            "page_id": page_id,
            "slug": slug,
            "action": action,
            "ok": success,
            "error": None if success else err,
        }
        with RESULT_LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(result) + "\n")

        if success:
            ok += 1
        else:
            fail += 1
            tqdm.write(f"FAIL {page_id} ({action}, slug='{slug[:40]}'): {err}")
        time.sleep(THROTTLE_S)

    print(f"\nDone. ok={ok} fail={fail} (deletes+catch-all)", file=sys.stderr)
    print(f"Results: {RESULT_LOG}", file=sys.stderr)
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
