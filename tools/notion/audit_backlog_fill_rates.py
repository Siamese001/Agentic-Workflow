#!/usr/bin/env python3
"""One-shot audit: compute fill rates for every property in Backlog Items DB.

Prints a table sorted by fill rate (ascending — most-empty first).
Requires NOTION_TOKEN or NOTION_API_KEY.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1].parent / ".windsurf" / "scripts"))
from _notion_constants import (  # noqa: E402
    NOTION_API_VERSION,
    NOTION_BASE,
    WAVE_PHASE_DATA_SOURCE_ID,
)

URL = f"{NOTION_BASE}/data_sources/{WAVE_PHASE_DATA_SOURCE_ID}/query"
TOKEN = os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY")
if not TOKEN:
    print("ERROR: set NOTION_TOKEN or NOTION_API_KEY", file=sys.stderr)
    sys.exit(1)


def _post(body: dict) -> dict:
    req = urllib.request.Request(
        URL,
        data=json.dumps(body).encode("utf-8"),
        method="POST",
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
            "Notion-Version": NOTION_API_VERSION,
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _is_populated(prop: dict) -> bool:
    t = prop.get("type")
    v = prop.get(t)
    if v is None:
        return False
    if t in {"title", "rich_text"}:
        return bool(v) and any((r.get("plain_text") or "").strip() for r in v)
    if t == "number":
        return v is not None
    if t == "select":
        return v is not None and bool(v.get("name"))
    if t == "multi_select":
        return bool(v)
    if t == "date":
        return v is not None and bool(v.get("start"))
    if t == "relation":
        return bool(v)
    if t == "people":
        return bool(v)
    if t == "checkbox":
        return True  # always has a value
    return bool(v)


def main() -> None:
    rows: list[dict] = []
    cursor: str | None = None
    while True:
        body: dict = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        data = _post(body)
        rows.extend(data.get("results") or [])
        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")

    total = len(rows)
    prop_counts: dict[str, int] = {}
    prop_types: dict[str, str] = {}
    for row in rows:
        for name, prop in (row.get("properties") or {}).items():
            prop_types.setdefault(name, prop.get("type", "?"))
            if _is_populated(prop):
                prop_counts[name] = prop_counts.get(name, 0) + 1
            else:
                prop_counts.setdefault(name, 0)

    print(f"Total rows: {total}\n")
    print(f"{'Property':<24} {'Type':<12} {'Filled':>7} {'Empty':>7} {'Fill %':>7}")
    print("-" * 62)
    for name in sorted(prop_counts, key=lambda k: (prop_counts[k], k)):
        filled = prop_counts[name]
        empty = total - filled
        pct = (100.0 * filled / total) if total else 0.0
        print(f"{name:<24} {prop_types[name]:<12} {filled:>7} {empty:>7} {pct:>6.1f}%")


if __name__ == "__main__":
    main()
