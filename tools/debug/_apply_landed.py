"""Apply LANDED verdicts: mark 5 audited rows as Done with evidence."""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOKEN = os.environ.get("NOTION_TOKEN")
VERSION = "2025-09-03"
RECEIPTS = ROOT / "artifacts" / "notion" / "_writeback_receipts.jsonl"
AUDIT_PATH = ROOT / "artifacts" / "notion" / "_pending_audit.json"


def http(method, url, body=None):
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Notion-Version": VERSION,
        "Content-Type": "application/json",
    }
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def _rt(s):
    return {"rich_text": [{"type": "text", "text": {"content": s}}]}


def main():
    if not TOKEN:
        print("NOTION_TOKEN missing", file=sys.stderr)
        return 1

    audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    landed = [r for r in audit if r.get("verdict") == "LANDED"]
    print(f"Applying {len(landed)} LANDED verdicts...")

    done = 0
    for r in landed:
        # Build evidence string
        evidence_parts = [f"category={r['category']}"]
        for k, v in r.items():
            if k in ("id", "url", "wave", "phase", "title", "category", "verdict"):
                continue
            evidence_parts.append(f"{k}={v}")
        evidence = "; ".join(evidence_parts)
        note = f"VERIFIED LANDED 2026-04-24 (audit dry-run pass 2): {evidence}"
        body = {
            "properties": {
                "Status": {"select": {"name": "Done"}},
                "Blocking Items": _rt(note[:2000]),
            }
        }
        try:
            http("PATCH", f"https://api.notion.com/v1/pages/{r['id']}", body)
            with RECEIPTS.open("a", encoding="utf-8") as f:
                f.write(
                    json.dumps(
                        {
                            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                            "op": "PATCH-landed-to-done",
                            "page_id": r["id"],
                            "ok": True,
                            "wave": r["wave"],
                            "phase": r["phase"],
                            "title": r["title"][:120],
                            "category": r["category"],
                        }
                    )
                    + "\n"
                )
            done += 1
            print(f"[{done}/{len(landed)}] DONE {r['wave']}/{r['phase']}: {r['title'][:80]}")
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            detail = getattr(e, "read", lambda: b"")().decode() if hasattr(e, "read") else str(e)
            with RECEIPTS.open("a", encoding="utf-8") as f:
                f.write(
                    json.dumps(
                        {
                            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                            "op": "PATCH-landed-to-done",
                            "page_id": r["id"],
                            "ok": False,
                            "detail": detail[:300],
                        }
                    )
                    + "\n"
                )
            print(f"[FAIL] {r['id']}: {e}", file=sys.stderr)

    print(f"\nDone: {done}/{len(landed)}")
    return 0 if done == len(landed) else 2


if __name__ == "__main__":
    sys.exit(main())
