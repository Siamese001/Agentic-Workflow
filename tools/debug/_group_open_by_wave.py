"""One-off: group open Wave/Phase Convergence rows by Wave ID.

Reads all rows from Notion (not just a single page) and groups them by wave
so we can present the deferred scope one-wave-at-a-time.
"""
from __future__ import annotations

import collections
import json
import os
import sys
import urllib.request

TOKEN = os.environ.get("NOTION_TOKEN")
DS_ID = "fc7f6bf4-6a73-43cd-a4e8-1ef23267dbe7"


def rt(prop: dict) -> str:
    t = prop.get("rich_text") or prop.get("title") or []
    return "".join(x.get("plain_text", "") for x in t)


def select_name(prop: dict) -> str:
    sel = prop.get("select") or {}
    return sel.get("name", "")


def query_all() -> list[dict]:
    url = f"https://api.notion.com/v1/data_sources/{DS_ID}/query"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Notion-Version": "2025-09-03",
        "Content-Type": "application/json",
    }
    payload = {
        "filter": {"property": "Status", "select": {"does_not_equal": "Done"}},
        "page_size": 100,
    }
    rows: list[dict] = []
    cursor: str | None = None
    while True:
        body = dict(payload)
        if cursor:
            body["start_cursor"] = cursor
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
        rows.extend(result["results"])
        if not result.get("has_more"):
            break
        cursor = result.get("next_cursor")
    return rows


def main() -> int:
    if not TOKEN:
        print("NOTION_TOKEN not set", file=sys.stderr)
        return 1
    rows = query_all()
    waves: dict[str, list[tuple]] = collections.defaultdict(list)
    for r in rows:
        pr = r["properties"]
        wave = rt(pr["Wave ID"]) or "(no-wave)"
        title = rt(pr["Phase Title"])
        band = select_name(pr["P-Band"]) or "UNSCORED"
        status = select_name(pr["Status"]) or "?"
        phase = rt(pr["Phase ID"])
        impact = pr["Impact Score"].get("number")
        waves[wave].append((band, status, phase, title, impact))

    # also keep only NON-descoped for real "remaining work"
    active_waves = {}
    for w, items in waves.items():
        live = [x for x in items if x[1] not in ("Done", "Descoped", "Won't Do")]
        if live:
            active_waves[w] = live

    print(f"TOTAL rows (not Done): {len(rows)}")
    print(f"Total waves: {len(waves)}")
    print(f"Active waves (with non-descoped rows): {len(active_waves)}")
    print()
    print(f"{'Wave':<20} {'All':>5} {'Active':>7}")
    for w in sorted(waves, key=lambda x: (len(active_waves.get(x, [])), len(waves[x])), reverse=True):
        print(f"  {w:<18} {len(waves[w]):>5} {len(active_waves.get(w, [])):>7}")

    out = {
        "total_rows": len(rows),
        "waves": {
            w: [
                {"band": b, "status": s, "phase": p, "title": t, "impact": i}
                for (b, s, p, t, i) in items
            ]
            for w, items in active_waves.items()
        },
    }
    dest = "artifacts/notion/open_by_wave.json"
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"\nWrote: {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
