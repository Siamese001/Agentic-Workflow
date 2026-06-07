"""Close out two deferred items from residual cleanup orchestrator:

1. Plans DB registration retry — probe schema, retry with correct column names
2. Wave D.2 — band-extraction from Blocking Items text for the 63 rows that had no [Pn] in title
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOKEN = os.environ.get("NOTION_TOKEN")
VERSION = "2025-09-03"

PLANS_DS = "ac53d31b-3068-4039-9ebe-856c12caab32"  # data_source_id for reads
PLANS_DB = "6aba34d9-4d0b-4f4c-b956-b2bdea541ca9"  # database_id for writes
RECEIPTS = ROOT / "artifacts" / "notion" / "_writeback_receipts.jsonl"
PLAN_SLUG = "notion-backlog-residual-cleanup-c3d8f2"
PLAN_FILE = "docs/archive/windsurf/legacy-tree/plans/notion-backlog-residual-cleanup-c3d8f2.md"

ROWS = json.loads((ROOT / "artifacts/notion/open_rows_with_ids.json").read_text(encoding="utf-8"))
RESCORE = json.loads((ROOT / "artifacts/notion/_pending_rescore.json").read_text(encoding="utf-8"))


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


def _title(s, max_len=200):
    return {"title": [{"type": "text", "text": {"content": s[:max_len]}}]}


def receipt(op, page_id, ok, **extra):
    RECEIPTS.parent.mkdir(parents=True, exist_ok=True)
    rec = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "op": op,
        "page_id": page_id,
        "ok": ok,
        **extra,
    }
    with RECEIPTS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


# ---- Part 1: Plans DB schema probe + retry --------------------------------


def probe_plans_schema():
    """Retrieve data source to see actual column names + types."""
    r = http("GET", f"https://api.notion.com/v1/data_sources/{PLANS_DS}")
    props = r.get("properties", {})
    schema = {name: p.get("type") for name, p in props.items()}
    print("Plans DB schema:")
    for name, ptype in sorted(schema.items()):
        marker = "  [TITLE]" if ptype == "title" else ""
        print(f"  {name:<35} {ptype}{marker}")
    return schema


def retry_plan_registration(schema: dict):
    """Build properties dict matching actual schema, retry POST."""
    # Find the title column
    title_col = next((name for name, t in schema.items() if t == "title"), None)
    if not title_col:
        print("[ERROR] No title column found in Plans DB schema", file=sys.stderr)
        return ""

    props = {title_col: _title(PLAN_SLUG)}

    # Opportunistic field matching
    for cand_name, value, value_type in [
        ("Plan File Path", PLAN_FILE, "rich_text"),
        ("Plan File", PLAN_FILE, "rich_text"),
        ("File Path", PLAN_FILE, "rich_text"),
        ("Path", PLAN_FILE, "rich_text"),
        ("Slug", PLAN_SLUG, "rich_text"),
        ("Status", "Not Started", "select"),
        ("Exists On Disk", True, "checkbox"),
    ]:
        if cand_name in schema:
            actual_type = schema[cand_name]
            if actual_type == "rich_text" and value_type == "rich_text":
                props[cand_name] = _rt(value)
            elif actual_type == "select" and value_type == "select":
                props[cand_name] = {"select": {"name": value}}
            elif actual_type == "checkbox" and value_type == "checkbox":
                props[cand_name] = {"checkbox": value}
            # URL-type columns
            elif actual_type == "url" and value_type == "rich_text":
                props[cand_name] = {"url": None}  # skip — no URL to provide

    body = {"parent": {"type": "database_id", "database_id": PLANS_DB}, "properties": props}
    try:
        r = http("POST", "https://api.notion.com/v1/pages", body)
        receipt("POST-plan-register-retry", r["id"], True, slug=PLAN_SLUG, props_used=list(props.keys()))
        print(f"[plan] REGISTERED: {r['id']} (columns used: {list(props.keys())})")
        return r["id"]
    except urllib.error.HTTPError as e:
        detail = e.read().decode()
        receipt("POST-plan-register-retry", None, False, detail=detail[:500], props_tried=list(props.keys()))
        print(f"[plan] retry failed: {detail[:400]}", file=sys.stderr)
        return ""


# ---- Part 2: Wave D.2 — band extraction from Blocking Items --------------

BAND_RE = re.compile(r"\[(P[1-5])\]")


def wave_d2():
    """For each unscorable row whose TITLE lacks [Pn] but whose row data contains it,
    extract from any available text field and PATCH P-Band."""
    # Get fresh snapshot of current rows (bands may have been updated in prior run)
    unscorable = [r for r in RESCORE if r.get("proposed_band") == "UNSCORABLE"]

    # For each, find the matching full row in ROWS (which has blocking text)
    rows_by_id = {r["id"]: r for r in ROWS}

    candidates = []
    for ur in unscorable:
        row = rows_by_id.get(ur["id"])
        if not row:
            continue
        # Skip any that Wave D already caught (title-based)
        if BAND_RE.search(row["title"]):
            continue
        # Check blocking items
        match = BAND_RE.search(row["blocking"])
        if match:
            candidates.append(
                (row["id"], row["wave"], row["phase"], row["title"], match.group(1), "blocking")
            )

    print(f"Wave D.2: {len(candidates)} rows have [Pn] in Blocking Items")

    done = 0
    for page_id, wave, phase, title, band, source in candidates:
        note = (
            f"BAND-EXTRACTED 2026-04-24 (Wave D.2 of {PLAN_SLUG}): band={band} extracted from "
            f"{source} field. Impact score not computed (preserves human-assigned priority). "
            f"Title: {title[:150]}"
        )
        body = {
            "properties": {
                "P-Band": {"select": {"name": band}},
                "Blocking Items": _rt(note),
            }
        }
        try:
            http("PATCH", f"https://api.notion.com/v1/pages/{page_id}", body)
            receipt(
                "PATCH-band-extracted-d2", page_id, True, wave=wave, phase=phase, band=band, source=source
            )
            done += 1
            if done % 10 == 0:
                print(f"  [{done}/{len(candidates)}] ...")
        except urllib.error.HTTPError as e:
            detail = e.read().decode()
            receipt("PATCH-band-extracted-d2", page_id, False, detail=detail[:300])
            print(f"  [FAIL] {page_id}: {detail[:200]}", file=sys.stderr)
    print(f"Wave D.2 complete: {done}/{len(candidates)} band extractions applied")
    return done, len(candidates)


# ---- Main -----------------------------------------------------------------


def main():
    if not TOKEN:
        print("NOTION_TOKEN missing", file=sys.stderr)
        return 1

    print("=" * 70)
    print("Part 1: Plans DB schema probe + retry registration")
    print("=" * 70)
    schema = probe_plans_schema()
    plan_page_id = retry_plan_registration(schema)

    print()
    print("=" * 70)
    print("Part 2: Wave D.2 — band-extraction from Blocking Items")
    print("=" * 70)
    d2_done, d2_total = wave_d2()

    print()
    print("=" * 70)
    print("FOLLOWUP COMPLETE")
    print("=" * 70)
    print(f"Plan registered: {'YES' if plan_page_id else 'NO'}")
    print(f"Wave D.2: {d2_done}/{d2_total} band extractions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
