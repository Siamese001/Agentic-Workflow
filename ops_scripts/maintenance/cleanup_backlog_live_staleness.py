"""cleanup_backlog_live_staleness.py — Backlog Items DB Live-status sweep.

Classifies every row with Status=Live by title regex and staleness:

  Completed  if title contains CLOSURE / COMPLETE / VALIDATED RESOLVED /
             VALIDATED GATE ADDED / explicit "DONE" suffix.
  Retired    if last_edited_time < today-14d AND not Completed
             (borrowed from Plans DB invariant — staleness rule).
  Live       everything else.

Run dry-run first; --apply posts the Notion patches.

Uses NOTION_TOKEN env var. Paginates Notion data source query. One API call
per row for the patch — rate-limited to 3 req/s.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

DATA_SOURCE_ID = "fc7f6bf4-6a73-43cd-a4e8-1ef23267dbe7"
STALE_DAYS = 14           # Live older than this → Retired
ACTIVE_DAYS = 3           # In Progress older than this (but < STALE_DAYS) → Not Started (re-queue)
RATE_LIMIT_SEC = 0.35

# Title-pattern rules — order matters; first match wins.
# Title-pattern rules— brackets may contain dates, so use \b word boundaries.
COMPLETED_PATTERNS = [
    re.compile(r"\[CLOSURE\b", re.I),
    re.compile(r"\[COMPLETE\b", re.I),
    re.compile(r"\[VALIDATED\s+(RESOLVED|GATE\s+ADDED)\b", re.I),
    re.compile(r"\[BACKLOG-DONE\b", re.I),
    re.compile(r"\[DONE\b", re.I),
    re.compile(r"[—\-]\s*COMPLETE\b", re.I),
    re.compile(r"[—\-]\s*DONE\b", re.I),
    re.compile(r"\bDONE\s*$"),
]


def _notion_headers() -> dict[str, str]:
    tok = os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY")
    if not tok:
        raise RuntimeError("NOTION_TOKEN not set")
    return {
        "Authorization": f"Bearer {tok}",
        "Content-Type": "application/json",
        "Notion-Version": "2025-09-03",
    }


def _post(url: str, payload: dict) -> dict:
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"),
        headers=_notion_headers(), method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _patch(url: str, payload: dict) -> dict:
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"),
        headers=_notion_headers(), method="PATCH",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _iter_live_rows():
    url = f"https://api.notion.com/v1/data_sources/{DATA_SOURCE_ID}/query"
    cursor = None
    while True:
        payload = {
            "filter": {"property": "Status", "select": {"equals": "In Progress"}},
            "page_size": 100,
        }
        if cursor:
            payload["start_cursor"] = cursor
        resp = _post(url, payload)
        yield from resp.get("results", [])
        if not resp.get("has_more"):
            return
        cursor = resp.get("next_cursor")


def _classify(title: str, staleness_iso: str,
              stale_cutoff: datetime, active_cutoff: datetime) -> str:
    for pat in COMPLETED_PATTERNS:
        if pat.search(title):
            return "Completed"
    try:
        le = datetime.fromisoformat(staleness_iso.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return "In Progress"
    if le < stale_cutoff:
        return "Retired"
    if le < active_cutoff:
        return "Not Started"   # re-queue: not actively in flight
    return "In Progress"


def _patch_row(page_id: str, new_status: str, rationale: str, apply: bool) -> None:
    if not apply:
        return
    url = f"https://api.notion.com/v1/pages/{page_id}"
    props = {"Status": {"select": {"name": new_status}}}
    # Append rationale as a small evidence note (does NOT overwrite existing Evidence).
    # Safer: only set status; leave Evidence alone for bulk sweep.
    last_exc: Exception | None = None
    for attempt in range(3):
        try:
            _patch(url, {"properties": props})
            time.sleep(RATE_LIMIT_SEC)
            return
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError) as exc:
            last_exc = exc
            time.sleep(2 ** attempt)
    raise last_exc if last_exc else RuntimeError("patch failed")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="Actually patch rows (default: dry-run)")
    ap.add_argument("--limit", type=int, default=0, help="Cap rows processed (0=all)")
    args = ap.parse_args(argv)

    now = datetime.now(timezone.utc)
    stale_cutoff = now - timedelta(days=STALE_DAYS)
    active_cutoff = now - timedelta(days=ACTIVE_DAYS)
    counts = {"Completed": 0, "Retired": 0, "Draft": 0, "Live": 0}
    log_rows: list[dict] = []

    for i, row in enumerate(_iter_live_rows()):
        if args.limit and i >= args.limit:
            break
        pid = row["id"]
        title_arr = row["properties"].get("Phase Title", {}).get("title") or []
        title = title_arr[0]["plain_text"] if title_arr else "(no title)"
        # Prefer the Last Updated custom property (authored staleness)
        # over last_edited_time (touched by any API write, including bulk syncs).
        last_upd_prop = row["properties"].get("Last Updated", {}).get("date") or {}
        last_upd_start = (last_upd_prop or {}).get("start") if last_upd_prop else None
        le = last_upd_start or row.get("last_edited_time", "")
        # Normalize date-only ISO to datetime at UTC midnight.
        if le and len(le) == 10:
            le = le + "T00:00:00+00:00"
        verdict = _classify(title, le, stale_cutoff, active_cutoff)
        counts[verdict] += 1
        log_rows.append({"page_id": pid, "title": title[:120], "last_edited": le, "verdict": verdict})
        if verdict != "Live":
            try:
                _patch_row(pid, verdict, f"auto-classified as {verdict} by title/staleness", args.apply)
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError) as exc:
                print(f"[warn] patch failed {pid}: {exc}", file=sys.stderr)

    # Write audit log.
    out = Path("artifacts/maintenance/backlog_live_sweep.jsonl")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        for r in log_rows:
            fh.write(json.dumps(r) + "\n")

    mode = "APPLIED" if args.apply else "DRY-RUN"
    print(f"[{mode}] processed={sum(counts.values())} "
          f"Completed={counts['Completed']} Retired={counts['Retired']} "
          f"Draft(re-queued)={counts['Draft']} Live(kept)={counts['Live']}")
    print(f"[{mode}] audit log: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
