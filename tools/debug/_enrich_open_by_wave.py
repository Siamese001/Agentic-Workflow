"""Re-query Notion Wave/Phase Convergence with page IDs captured."""
from __future__ import annotations
import json, os, sys, urllib.request

TOKEN = os.environ.get("NOTION_TOKEN")
DS_ID = "fc7f6bf4-6a73-43cd-a4e8-1ef23267dbe7"


def rt(p): 
    t = p.get("rich_text") or p.get("title") or []
    return "".join(x.get("plain_text", "") for x in t)


def sel(p):
    s = p.get("select") or {}
    return s.get("name", "")


def query_all():
    url = f"https://api.notion.com/v1/data_sources/{DS_ID}/query"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Notion-Version": "2025-09-03",
        "Content-Type": "application/json",
    }
    payload = {"filter": {"property": "Status", "select": {"does_not_equal": "Done"}}, "page_size": 100}
    rows = []
    cursor = None
    while True:
        body = dict(payload)
        if cursor:
            body["start_cursor"] = cursor
        req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as r:
            result = json.loads(r.read())
        rows.extend(result["results"])
        if not result.get("has_more"):
            break
        cursor = result.get("next_cursor")
    return rows


def main():
    if not TOKEN:
        print("NOTION_TOKEN missing", file=sys.stderr)
        return 1
    rows = query_all()
    out = []
    for r in rows:
        pr = r["properties"]
        out.append({
            "id": r["id"],
            "url": r["url"],
            "wave": rt(pr["Wave ID"]),
            "phase": rt(pr["Phase ID"]),
            "title": rt(pr["Phase Title"]),
            "band": sel(pr["P-Band"]) or "UNSCORED",
            "status": sel(pr["Status"]) or "",
            "impact": pr["Impact Score"].get("number"),
            "plan_file": rt(pr["Plan File"]),
            "blocking": rt(pr["Blocking Items"])[:200],
        })
    dest = "artifacts/notion/open_rows_with_ids.json"
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote {len(out)} rows to {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
