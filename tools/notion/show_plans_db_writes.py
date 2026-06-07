#!/usr/bin/env python3
"""show_plans_db_writes.py — view/summarize Plans-DB write telemetry.

Reads ``artifacts/governance/plans_db_writes.jsonl`` (the unified telemetry
log written by every Plans-DB writer) and prints a readable summary or
filtered tail.

Usage:
    python tools/notion/show_plans_db_writes.py                   # last 50 rows
    python tools/notion/show_plans_db_writes.py --tail 100        # last N rows
    python tools/notion/show_plans_db_writes.py --slug foo-aaaaaa # filter by slug
    python tools/notion/show_plans_db_writes.py --writer triage   # filter by writer substring
    python tools/notion/show_plans_db_writes.py --since 2026-05-10  # filter by date
    python tools/notion/show_plans_db_writes.py --summary         # event/writer counts

Plan: notion-plans-status-rca-followups-b8e3f2 (W3.P2).
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LOG_PATH = REPO_ROOT / "artifacts" / "governance" / "plans_db_writes.jsonl"


def _read_rows() -> list[dict]:
    if not LOG_PATH.exists():
        return []
    rows: list[dict] = []
    with LOG_PATH.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def _filter(rows: list[dict], args: argparse.Namespace) -> list[dict]:
    out = rows
    if args.slug:
        out = [r for r in out if r.get("slug") == args.slug]
    if args.writer:
        out = [r for r in out if args.writer in str(r.get("writer", ""))]
    if args.event:
        out = [r for r in out if r.get("event") == args.event]
    if args.since:
        try:
            since_dt = datetime.fromisoformat(args.since.replace("Z", "+00:00"))
        except ValueError:
            print(f"WARN: --since {args.since!r} is not ISO date; ignoring", file=sys.stderr)
            since_dt = None
        if since_dt:
            if since_dt.tzinfo is None:
                since_dt = since_dt.replace(tzinfo=timezone.utc)
            kept: list[dict] = []
            for r in out:
                ts = r.get("timestamp", "")
                try:
                    rdt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                except ValueError:
                    continue
                if rdt >= since_dt:
                    kept.append(r)
            out = kept
    return out


def _print_rows(rows: list[dict]) -> None:
    if not rows:
        print("(no rows)")
        return
    for r in rows:
        ts = r.get("timestamp", "?")
        ev = r.get("event", "?")
        slug = r.get("slug", "")
        writer = r.get("writer", "?")
        ok = r.get("ok")
        ok_tag = "✓" if ok else ("✗" if ok is False else "·")
        before = r.get("status_before")
        after = r.get("status_after")
        flow = ""
        if before is not None or after is not None:
            flow = f"  {before or '-'} → {after or '-'}"
        detail = r.get("detail", "")
        page_id = r.get("page_id", "")
        page_short = page_id[:8] if page_id else ""
        print(f"  {ts}  {ok_tag}  {ev:<24} {slug:<40}  [{writer}]{flow}")
        if detail:
            print(f"      {detail}")
        if page_short:
            print(f"      page_id={page_short}…")


def _summary(rows: list[dict]) -> None:
    if not rows:
        print("(no rows in log)")
        return
    print(f"Total rows: {len(rows)}\n")
    print("By event:")
    for ev, n in Counter(r.get("event", "?") for r in rows).most_common():
        print(f"  {n:>5}  {ev}")
    print("\nBy writer:")
    for w, n in Counter(r.get("writer", "?") for r in rows).most_common():
        print(f"  {n:>5}  {w}")
    print("\nBy ok:")
    ok_counts = Counter(r.get("ok") for r in rows)
    for ok, n in ok_counts.items():
        tag = "ok" if ok else ("FAIL" if ok is False else "?")
        print(f"  {n:>5}  {tag}")
    fail_rows = [r for r in rows if r.get("ok") is False]
    if fail_rows:
        print(f"\nLast 5 failures:")
        for r in fail_rows[-5:]:
            print(
                f"  {r.get('timestamp')}  {r.get('event')}  slug={r.get('slug')}  "
                f"writer={r.get('writer')}  detail={r.get('detail')}"
            )


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--tail", type=int, default=50, help="Show last N rows (default 50)")
    p.add_argument("--slug", help="Filter by exact slug")
    p.add_argument("--writer", help="Filter by writer substring (e.g. 'triage')")
    p.add_argument("--event", help="Filter by exact event name")
    p.add_argument("--since", help="ISO date/datetime cutoff (e.g. 2026-05-10)")
    p.add_argument("--summary", action="store_true", help="Print event/writer counts")
    p.add_argument("--json", action="store_true", help="Emit raw JSON rows")
    args = p.parse_args()

    if not LOG_PATH.exists():
        print(f"No telemetry log at {LOG_PATH}")
        print("Run any Plans-DB writer (e.g. triage_plans_duplicates.py) to populate.")
        return 0

    rows = _filter(_read_rows(), args)

    if args.summary:
        _summary(rows)
        return 0

    rows = rows[-args.tail:]
    if args.json:
        for r in rows:
            print(json.dumps(r, ensure_ascii=False))
        return 0

    _print_rows(rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
