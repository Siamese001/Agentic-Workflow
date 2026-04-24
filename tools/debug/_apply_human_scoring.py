"""Applier: ingest human-filled worksheet, PATCH Notion rows.

Reads artifacts/notion/human_scoring_worksheet.json.
For each row with BAND filled:
  - BAND in {P1..P5}: PATCH P-Band + optional Layer/Files In Scope/Blocking Items
  - BAND=DESCOPE: PATCH Status=Descoped
  - BAND=SKIP: no-op (keeps UNSCORED)
  - BAND empty: no-op

Idempotent: safe to re-run.
"""
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
WORKSHEET = ROOT / "artifacts" / "notion" / "human_scoring_worksheet.json"
RECEIPTS = ROOT / "artifacts" / "notion" / "_writeback_receipts.jsonl"
PLAN_SLUG = "notion-backlog-human-scoring-e7a941"

VALID_BANDS = {"P1", "P2", "P3", "P4", "P5"}
VALID_SPECIAL = {"DESCOPE", "SKIP"}


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


def _rt(s, max_len=2000):
    return {"rich_text": [{"type": "text", "text": {"content": s[:max_len]}}]}


def receipt(op, page_id, ok, **extra):
    RECEIPTS.parent.mkdir(parents=True, exist_ok=True)
    rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "op": op, "page_id": page_id, "ok": ok, **extra}
    with RECEIPTS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


def apply_row(row: dict) -> str:
    """Apply a single worksheet row. Returns one of: 'patched', 'descoped', 'skipped', 'empty', 'error'."""
    band = (row.get("BAND") or "").strip().upper()
    if not band:
        return "empty"
    if band == "SKIP":
        return "skipped"

    layer = (row.get("LAYER") or "").strip()
    files = (row.get("FILES") or "").strip()
    notes = (row.get("NOTES") or "").strip()
    page_id = row["id"]

    if band == "DESCOPE":
        note_text = (
            f"DESCOPED 2026-04-24 (human-scoring Wave 5 of {PLAN_SLUG}): "
            f"{notes if notes else 'human review determined row is obsolete/landed/duplicate'}."
        )
        body = {
            "properties": {
                "Status": {"select": {"name": "Descoped"}},
                "Blocking Items": _rt(note_text),
            }
        }
        try:
            http("PATCH", f"https://api.notion.com/v1/pages/{page_id}", body)
            receipt("PATCH-human-scored", page_id, True,
                    wave=row["wave"], phase=row["phase"], action="descope", notes=notes[:200])
            return "descoped"
        except urllib.error.HTTPError as e:
            detail = e.read().decode()
            receipt("PATCH-human-scored", page_id, False, detail=detail[:300])
            return "error"

    if band not in VALID_BANDS:
        print(f"  [WARN] unknown BAND value '{band}' for {row['wave']}/{row['phase']}; skipping", file=sys.stderr)
        return "error"

    # Normal band assignment
    props = {"P-Band": {"select": {"name": band}}}
    blocking_parts = [
        f"HUMAN-SCORED 2026-04-24 (Wave 5 of {PLAN_SLUG}): band={band}"
    ]
    if layer:
        props["Layer"] = {"select": {"name": layer}}
        blocking_parts.append(f"layer={layer}")
    if files:
        props["Files In Scope"] = _rt(files)
        blocking_parts.append(f"files={files[:100]}")
    if notes:
        blocking_parts.append(f"notes={notes}")
    props["Blocking Items"] = _rt(". ".join(blocking_parts))

    body = {"properties": props}
    try:
        http("PATCH", f"https://api.notion.com/v1/pages/{page_id}", body)
        receipt("PATCH-human-scored", page_id, True,
                wave=row["wave"], phase=row["phase"], action="patch", band=band,
                layer=layer, has_files=bool(files), notes=notes[:200])
        return "patched"
    except urllib.error.HTTPError as e:
        detail = e.read().decode()
        receipt("PATCH-human-scored", page_id, False, detail=detail[:300])
        return "error"


def main():
    if not TOKEN:
        print("NOTION_TOKEN missing", file=sys.stderr)
        return 1
    if not WORKSHEET.exists():
        print(f"Worksheet missing: {WORKSHEET}", file=sys.stderr)
        print("Generate with: python tools/debug/_build_scoring_worksheet.py", file=sys.stderr)
        return 2

    worksheet = json.loads(WORKSHEET.read_text(encoding="utf-8"))
    print(f"Worksheet rows: {len(worksheet)}")
    filled = sum(1 for r in worksheet if (r.get("BAND") or "").strip())
    print(f"Filled (BAND non-empty): {filled}")
    if filled == 0:
        print("\nNothing to apply — worksheet empty. Fill BAND column first, then re-run.")
        print(f"Worksheet path: {WORKSHEET}")
        return 0

    counts = {"patched": 0, "descoped": 0, "skipped": 0, "empty": 0, "error": 0}
    for row in worksheet:
        outcome = apply_row(row)
        counts[outcome] = counts.get(outcome, 0) + 1
        if outcome in ("patched", "descoped"):
            band = (row.get("BAND") or "").strip().upper()
            print(f"  [{outcome}] {row['wave']}/{row['phase']}: BAND={band}")

    print(f"\n=== Applier complete ===")
    for k, v in counts.items():
        print(f"  {k}: {v}")
    return 0 if counts["error"] == 0 else 3


if __name__ == "__main__":
    sys.exit(main())
