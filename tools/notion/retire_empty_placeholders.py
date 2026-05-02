#!/usr/bin/env python3
"""Retire Draft rows that are pure placeholders.

Targets rows where:
  - Blocking Items is empty
  - Success Criteria is empty
  - Evidence is either empty OR contains only an auto-DEFERRED-SCOPE stub
    ("Auto-captured from DEFERRED_SCOPE marker ... Cascade to fill on execution")
  - Title is the only signal

These are deferred-scope markers that were auto-posted but never enriched —
they're trackers without enough information to act on. Retiring with a
clear reason lets a future session re-create them with real scope.

Conservative: skip any row whose title contains 'BACKLOG', '[NEXT', or
'MCP-BACKLOG' (those are intentional future-idea placeholders held for
later promotion).
"""
from __future__ import annotations
import argparse, json, re, sys, time
from datetime import date, datetime, timezone
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
from triage_keep_drafts import (  # type: ignore[import-not-found]
    _token, _http, _txt, fetch_drafts, NOTION_API, REPO_ROOT,
)

AUDIT_LOG = REPO_ROOT / "artifacts" / "windsurf" / "retire_empty_placeholders_audit.jsonl"

DEFERRED_STUB = re.compile(
    r"Auto-captured from DEFERRED_SCOPE marker.*Cascade to fill on execution",
    re.DOTALL,
)
TRIAGE_STAMP = re.compile(r"^\[TRIAGE \d{4}-\d{2}-\d{2}\] bucket=[A-Z]\d?\.")
PROTECTED_TITLE = re.compile(r"(?i)(BACKLOG|\[NEXT|MCP-BACKLOG|future-idea)")


def is_empty_placeholder(row: dict) -> tuple[bool, str]:
    p = row["properties"]
    title = (p["Phase Title"]["title"][0]["plain_text"]
             if p["Phase Title"]["title"] else "")
    bi = _txt(p.get("Blocking Items")).strip()
    sc = _txt(p.get("Success Criteria")).strip()
    ev = _txt(p.get("Evidence")).strip()

    if PROTECTED_TITLE.search(title):
        return False, "protected_title"

    # Empty BI + SC required
    if bi or sc:
        return False, "has_bi_or_sc"

    # Evidence: must be empty OR only triage-stamp OR only deferred-stub
    if not ev:
        return True, "all_empty"
    if TRIAGE_STAMP.match(ev) and len(ev) < 200:
        # Only a triage stamp (no follow-up content)
        return False, "triage_stamped_intentional"
    # Strip out the deferred-scope auto-stub, see if anything remains
    cleaned = DEFERRED_STUB.sub("", ev).strip()
    cleaned = re.sub(r"^Success:\s*\|", "", cleaned).strip()
    cleaned = re.sub(r"^Blocking:\s*", "", cleaned).strip()
    if not cleaned or len(cleaned) < 30:
        return True, "deferred_stub_only"
    # Has real content beyond the stub — keep
    return False, "has_real_evidence"


def _audit(entry: dict) -> None:
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry["ts"] = datetime.now(timezone.utc).isoformat()
    with AUDIT_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def retire(tok: str, page_id: str, reason: str, dry: bool) -> None:
    today = date.today().isoformat()
    note = (
        f"[PLACEHOLDER RETIRE {today}] reason={reason}. "
        f"Row had no Blocking Items, no Success Criteria, no actionable "
        f"Evidence beyond an auto-stub. Re-create with real scope when "
        f"ready to execute."
    )[:1900]
    body = {"properties": {
        "Status": {"select": {"name": "Retired"}},
        "Last Updated": {"date": {"start": today}},
        "Evidence": {"rich_text": [{"type": "text", "text": {"content": note}}]},
    }}
    if not dry:
        _http("PATCH", f"{NOTION_API}/pages/{page_id}", tok, body)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--execute", action="store_true")
    args = ap.parse_args()
    if args.dry_run == args.execute:
        ap.error("--dry-run or --execute")

    tok = _token()
    rows = fetch_drafts(tok)
    print(f"draft rows: {len(rows)}")

    retire_list = []
    keep_reasons = {}
    for r in rows:
        flag, reason = is_empty_placeholder(r)
        if flag:
            retire_list.append((r, reason))
        else:
            keep_reasons[reason] = keep_reasons.get(reason, 0) + 1

    print(f"\nRETIRE: {len(retire_list)}")
    print(f"KEEP reasons:")
    for k, v in sorted(keep_reasons.items(), key=lambda x: -x[1]):
        print(f"  {v:4} {k}")

    print(f"\n--- sample of RETIRE list ---")
    for r, reason in retire_list[:8]:
        t = r["properties"]["Phase Title"]["title"]
        title = t[0]["plain_text"][:90] if t else "(no)"
        print(f"  [{reason}] {title}")

    print(f"\n--- mutations ---")
    n = 0
    for r, reason in retire_list:
        t = r["properties"]["Phase Title"]["title"]
        title = t[0]["plain_text"][:80] if t else "(no)"
        try:
            retire(tok, r["id"], reason, dry=args.dry_run)
            _audit({"step": "placeholder_retire", "page_id": r["id"], "title": title, "reason": reason, "dry_run": args.dry_run})
            n += 1
        except Exception as e:
            print(f"  ERROR {r['id']}: {e}")
        time.sleep(0.35)
    print(f"TOTAL retired: {n}")
    print(f"audit: {AUDIT_LOG}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
