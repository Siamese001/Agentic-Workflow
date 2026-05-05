#!/usr/bin/env python3
"""Bulk-flip stale Not Started rows in the Backlog Items DB.

Three-step audit + remediation per 2026-05-02 backlog cleanup decision:

1. **CLOSE_NOW** — rows whose Blocking Items / Success Criteria / Evidence
   already contain explicit closure evidence (commit SHA, "DONE",
   "AUTO-CLOSE", "IMPLEMENTED", "fully complete", etc.) are flipped to
   Status=Completed with Last Updated=today.
2. **MISSING_PLAN** — rows whose Plan File references a plan that no
   longer exists under .windsurf/plans/ are flipped to Status=Retired
   with reason "plan file deleted YYYY-MM-DD" prepended to Evidence.
3. **KEEP** — remaining rows printed as a ranked work-queue (Impact Score
   desc) for operator review; no mutation.

Auth: NOTION_TOKEN from env or .env (snapshot_renderer pattern).
Audit: artifacts/windsurf/bulk_flip_stale_drafts_audit.jsonl

Usage:
    python tools/notion/bulk_flip_stale_drafts.py --dry-run
    python tools/notion/bulk_flip_stale_drafts.py --execute
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
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2025-09-03"
BACKLOG_DS_ID = "fc7f6bf4-6a73-43cd-a4e8-1ef23267dbe7"

REPO_ROOT = Path(__file__).resolve().parents[2]
PLANS_DIR = REPO_ROOT / ".windsurf" / "plans"
AUDIT_LOG = REPO_ROOT / "artifacts" / "windsurf" / "bulk_flip_stale_drafts_audit.jsonl"

# Strong closure markers — high confidence the work landed.
STRONG_CLOSURE = re.compile(
    r"(commit\s+[0-9a-f]{8,}"
    r"|AUTO-CLOSE"
    r"|signed[_ ]off"
    r"|already done"
    r"|fully complete"
    r"|fully landed"
    r"|DONE\s*\d{4}-\d{2}-\d{2}"
    r"|closed by commit"
    r"|closed by ADG)",
    re.IGNORECASE,
)

# Soft closure markers — needs strong-evidence corroboration to flip.
SOFT_CLOSURE = re.compile(
    r"(?i)\b(implemented\b|complete[d]?\b|landed\b|merged\b)"
)


def _token() -> str:
    for k in ("NOTION_TOKEN", "NOTION_API_KEY"):
        v = os.environ.get(k)
        if v:
            return v
    env = REPO_ROOT / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if line.startswith(("NOTION_TOKEN=", "NOTION_API_KEY=")):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("NOTION_TOKEN not set")


def _headers(tok: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {tok}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def _http(method: str, url: str, tok: str, body: dict | None = None, timeout: int = 30) -> dict[str, Any]:
    data = json.dumps(body).encode("utf-8") if body else None
    req = urllib.request.Request(url, data=data, method=method, headers=_headers(tok))
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as err:
            if err.code == 429 and attempt < 3:
                time.sleep(int(err.headers.get("Retry-After", "2")))
                continue
            body_txt = err.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {err.code} {method} {url}: {body_txt}") from err
        except urllib.error.URLError as err:
            if attempt < 3:
                time.sleep(1 + attempt)
                continue
            raise RuntimeError(f"URL error: {err}") from err
    raise RuntimeError(f"Exhausted retries: {method} {url}")


def _audit(entry: dict) -> None:
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry["ts"] = datetime.now(timezone.utc).isoformat()
    with AUDIT_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def fetch_all_not_started(tok: str) -> list[dict]:
    rows, cursor = [], None
    body_base = {
        "filter": {"property": "Status", "select": {"equals": "Not Started"}},
        "page_size": 100,
    }
    while True:
        body = dict(body_base)
        if cursor:
            body["start_cursor"] = cursor
        data = _http("POST", f"{NOTION_API}/data_sources/{BACKLOG_DS_ID}/query", tok, body)
        rows.extend(data.get("results", []))
        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")
    # dedupe
    seen, out = set(), []
    for r in rows:
        if r["id"] in seen:
            continue
        seen.add(r["id"])
        out.append(r)
    return out


def _first_text(prop_obj: dict | None) -> str:
    if not prop_obj:
        return ""
    rt = prop_obj.get("rich_text") or []
    return rt[0]["plain_text"] if rt else ""


def classify(row: dict, on_disk_plans: set[str]) -> tuple[str, str]:
    """Return (bucket, reason). Bucket ∈ {CLOSE_NOW, MISSING_PLAN, KEEP}."""
    p = row["properties"]
    bi = _first_text(p.get("Blocking Items"))
    sc = _first_text(p.get("Success Criteria"))
    ev = _first_text(p.get("Evidence"))
    plan = _first_text(p.get("Plan File"))
    haystack = f"{bi}\n{sc}\n{ev}"

    # Step 1: strong closure evidence wins regardless.
    m = STRONG_CLOSURE.search(haystack)
    if m:
        return "CLOSE_NOW", f"strong_closure:{m.group(0)[:60]}"

    # Step 2: soft closure + non-empty SC OR Evidence (avoid false positives
    # from phase titles that just say "complete X").
    if SOFT_CLOSURE.search(haystack) and (sc or ev):
        # Tighten: require at least one strong-ish hint
        if re.search(r"(?i)(NONE\b|N/A\b|all .* pass|0 (?:rows|errors|violations))", haystack):
            return "CLOSE_NOW", "soft_closure_with_evidence"

    # Step 3: missing plan file?
    pf = plan.split("/")[-1].strip() if plan else ""
    if pf and pf.endswith(".md") and pf not in on_disk_plans:
        # Skip rows whose plan field is a placeholder like "(no plan file ...)"
        if pf.startswith("("):
            return "KEEP", "no_plan_field"
        return "MISSING_PLAN", f"plan_missing:{pf}"

    return "KEEP", "real_backlog"


def patch_complete(tok: str, page_id: str, evidence_addendum: str, dry: bool) -> dict:
    today = date.today().isoformat()
    body = {
        "properties": {
            "Status": {"select": {"name": "Completed"}},
            "Last Updated": {"date": {"start": today}},
            "Evidence": {"rich_text": [{"type": "text", "text": {"content": evidence_addendum[:1900]}}]},
        }
    }
    if dry:
        return {"dry_run": True, "page_id": page_id, "body": body}
    return _http("PATCH", f"{NOTION_API}/pages/{page_id}", tok, body)


def patch_retire(tok: str, page_id: str, plan_filename: str, dry: bool) -> dict:
    today = date.today().isoformat()
    reason = f"Retired {today}: plan file '{plan_filename}' deleted from .windsurf/plans/. Work descoped."
    body = {
        "properties": {
            "Status": {"select": {"name": "Retired"}},
            "Last Updated": {"date": {"start": today}},
            "Evidence": {"rich_text": [{"type": "text", "text": {"content": reason}}]},
        }
    }
    if dry:
        return {"dry_run": True, "page_id": page_id, "body": body}
    return _http("PATCH", f"{NOTION_API}/pages/{page_id}", tok, body)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--limit", type=int, default=0, help="cap mutations (0=all)")
    args = ap.parse_args()
    if args.dry_run == args.execute:
        ap.error("specify exactly one of --dry-run / --execute")

    tok = _token()
    on_disk = {f.name for f in PLANS_DIR.iterdir() if f.suffix == ".md"}
    print(f"plans on disk: {len(on_disk)}", flush=True)

    rows = fetch_all_not_started(tok)
    print(f"not started rows fetched: {len(rows)}", flush=True)

    buckets: dict[str, list[tuple[dict, str]]] = {"CLOSE_NOW": [], "MISSING_PLAN": [], "KEEP": []}
    for r in rows:
        bucket, reason = classify(r, on_disk)
        buckets[bucket].append((r, reason))

    print(f"  CLOSE_NOW    : {len(buckets['CLOSE_NOW'])}", flush=True)
    print(f"  MISSING_PLAN : {len(buckets['MISSING_PLAN'])}", flush=True)
    print(f"  KEEP         : {len(buckets['KEEP'])}", flush=True)
    print(flush=True)

    # Step 1: CLOSE_NOW
    print(f"=== Step 1: flip {len(buckets['CLOSE_NOW'])} CLOSE_NOW → Completed ===", flush=True)
    n = 0
    for r, reason in buckets["CLOSE_NOW"]:
        if args.limit and n >= args.limit:
            break
        title = r["properties"]["Phase Title"]["title"]
        title_str = title[0]["plain_text"][:70] if title else "(no title)"
        bi = _first_text(r["properties"].get("Blocking Items"))
        # Build evidence note: prefer existing Evidence; otherwise carry first
        # 200 chars of Blocking Items so we don't lose the closure marker.
        existing_ev = _first_text(r["properties"].get("Evidence"))
        if existing_ev:
            note = f"[BULK-FLIP {date.today().isoformat()}] {reason}. {existing_ev}"
        else:
            note = f"[BULK-FLIP {date.today().isoformat()}] {reason}. From Blocking Items: {bi[:300]}"
        try:
            res = patch_complete(tok, r["id"], note, dry=args.dry_run)
            _audit({"step": "complete", "page_id": r["id"], "title": title_str, "reason": reason, "dry_run": args.dry_run})
            n += 1
            if n % 10 == 0:
                print(f"  ... {n} flipped", flush=True)
        except Exception as e:
            print(f"  ERROR on {r['id']} ({title_str}): {e}", flush=True)
            _audit({"step": "complete_error", "page_id": r["id"], "title": title_str, "error": str(e)})
        time.sleep(0.35)  # Notion rate limit ~3/sec
    print(f"  TOTAL flipped: {n}", flush=True)

    # Step 2: MISSING_PLAN
    print(f"\n=== Step 2: flip {len(buckets['MISSING_PLAN'])} MISSING_PLAN → Retired ===", flush=True)
    n = 0
    for r, reason in buckets["MISSING_PLAN"]:
        if args.limit and n >= args.limit:
            break
        title = r["properties"]["Phase Title"]["title"]
        title_str = title[0]["plain_text"][:70] if title else "(no title)"
        plan_fn = reason.split(":", 1)[1] if ":" in reason else "?"
        try:
            res = patch_retire(tok, r["id"], plan_fn, dry=args.dry_run)
            _audit({"step": "retire", "page_id": r["id"], "title": title_str, "plan": plan_fn, "dry_run": args.dry_run})
            n += 1
            if n % 10 == 0:
                print(f"  ... {n} retired", flush=True)
        except Exception as e:
            print(f"  ERROR on {r['id']} ({title_str}): {e}", flush=True)
            _audit({"step": "retire_error", "page_id": r["id"], "title": title_str, "error": str(e)})
        time.sleep(0.35)
    print(f"  TOTAL retired: {n}", flush=True)

    # Step 3: KEEP work queue (top 5 by Impact Score)
    print(f"\n=== Step 3: top 5 KEEP rows by Impact Score (work queue) ===", flush=True)
    keep = []
    for r, _ in buckets["KEEP"]:
        p = r["properties"]
        impact = p.get("Impact Score", {}).get("number")
        if impact is None:
            continue
        title = p["Phase Title"]["title"][0]["plain_text"] if p["Phase Title"]["title"] else "(no title)"
        band = p["P-Band"]["select"]["name"] if p["P-Band"]["select"] else "--"
        plan = _first_text(p.get("Plan File"))
        keep.append((impact, band, title, plan, r["id"]))
    keep.sort(reverse=True)
    for impact, band, title, plan, rid in keep[:5]:
        print(f"  [{band}] impact={impact}  {title[:80]}", flush=True)
        print(f"        plan={plan}  id={rid}", flush=True)

    print(f"\nAudit: {AUDIT_LOG}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
