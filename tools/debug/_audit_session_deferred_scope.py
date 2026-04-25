"""Audit: list all DEFERRED_SCOPE captures since a cutoff timestamp."""

from __future__ import annotations

import json
from pathlib import Path

CUTOFF = "2026-04-23T10:30"  # this chat ~06:30 local = 10:30 UTC
LOG = Path("artifacts/windsurf/deferred_scope_capture.jsonl")


def main() -> int:
    rows = []
    for ln in LOG.read_text(encoding="utf-8").splitlines():
        try:
            r = json.loads(ln)
        except json.JSONDecodeError:
            continue
        ts = r.get("timestamp", "")
        if ts >= CUTOFF:
            rows.append(r)

    print(f"Captures since {CUTOFF} UTC: {len(rows)}\n")
    for r in rows:
        m = r.get("marker", {})
        ts = r.get("timestamp", "")[:19]
        band = r.get("band", "?")
        plan = m.get("plan", "?")
        kind = r.get("kind", "?")
        nid = r.get("notion_page_id", "(none)")
        print(f"  {ts}  [{band}] {plan[:45]:<45} kind={kind:<20} notion={nid}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
