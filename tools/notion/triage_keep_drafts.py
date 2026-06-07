#!/usr/bin/env python3
"""Triage the surviving Not Started backlog rows into A/B/C/D buckets.

Run AFTER bulk_flip_stale_drafts.py has already removed strong-closure +
missing-plan rows. Operates on whatever Drafts remain.

Buckets:
  A — Time-gated / dependency-gated   → stay Not Started + annotate
  B — BACKLOG / future ideas           → stay Not Started + annotate
  C — Soft-closure (likely done)       → retire (with note)
  D — Genuinely unblocked work         → stay Not Started, surface for ranking

Modes:
  --dry-run             classify only, print counts + samples
  --execute             mutate: annotate A/B, retire C, leave D untouched
  --emit-plan PATH      write markdown plan to PATH
  --post-plan-notion    create Plans-DB row for the markdown plan
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
PLANS_DB_ID = "6aba34d9-4d0b-4f4c-b956-b2bdea541ca9"

REPO_ROOT = Path(__file__).resolve().parents[2]
AUDIT_LOG = REPO_ROOT / "artifacts" / "governance" / "triage_keep_drafts_audit.jsonl"

# --- bucket signal regexes --------------------------------------------------
A_SIGNALS = re.compile(
    r"(?i)(90[- ]day|cannot proceed before|blocked on W\d|gated on|phase d\.5|"
    r"multi[- ]week|requires real production|requires multi-?session|"
    r"depends on \w+\s*\([gw]\d|deferred — need|deferred until|sequencing 202\d|"
    r"strict 90|2026-0[8-9]|2026-1[0-2]|2027-)"
)
B_SIGNALS = re.compile(
    r"(?i)(MCP-BACKLOG|^BACKLOG\b|Notion-only plan|BACKLOG idea|"
    r"\[NEXT[·\.\-]P\d|FUTURE:|operational-grounds duplication|"
    r"future-work|review apps_|enhancement opportunit)"
)
# Tightened C-criterion (post spot-check 2026-05-02):
# Require co-location of closure word + (commit SHA OR explicit date stamp).
# This eliminates false positives where "complete"/"implemented"/"landed" appear
# in plan-language ("not implemented", "complete X", "Backlog follow-up").
SOFT_CLOSURE = re.compile(
    r"(?i)("
    r"(?:RESOLVED|CLOSED|COMPLETED|Closed|Complete|Done)\s*[\.:]?\s*\d{4}-\d{2}-\d{2}"  # "COMPLETED 2026-04-24"
    r"|landed as [0-9a-f]{8,}"                                                            # "landed as 4d9bd6f164"
    r"|landed in commit[s]?\s+[0-9a-f]{8,}"                                               # "landed in commits 1e714a28a3"
    r"|landed in commits?\s*\([^)]*\)"
    r"|pushed to origin/main"
    r"|Done\.\s+(?:W\d|Follow-up|Deferred|All|Implemented)"                               # "Done. Follow-up..." / "Done. W6..."
    r")"
)
# (kept as a marker for the bulk_flip script; unused here directly)
STRONG_CLOSURE = re.compile(
    r"(commit\s+[0-9a-f]{8,}|AUTO-CLOSE|signed[_ ]off|fully complete|fully landed)",
    re.IGNORECASE,
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
    return {"Authorization": f"Bearer {tok}", "Notion-Version": NOTION_VERSION, "Content-Type": "application/json"}


def _http(method: str, url: str, tok: str, body: dict | None = None, timeout: int = 30) -> dict[str, Any]:
    data = json.dumps(body).encode("utf-8") if body else None
    req = urllib.request.Request(url, data=data, method=method, headers=_headers(tok))
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as err:
            if err.code == 429 and attempt < 3:
                time.sleep(int(err.headers.get("Retry-After", "2"))); continue
            raise RuntimeError(f"HTTP {err.code} {method} {url}: {err.read().decode('utf-8','replace')}") from err
        except urllib.error.URLError as err:
            if attempt < 3: time.sleep(1 + attempt); continue
            raise
    raise RuntimeError("retries exhausted")


def _audit(entry: dict) -> None:
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry["ts"] = datetime.now(timezone.utc).isoformat()
    with AUDIT_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def fetch_not_started(tok: str) -> list[dict]:
    rows, cursor = [], None
    while True:
        body = {"filter": {"property": "Status", "select": {"equals": "Not Started"}}, "page_size": 100}
        if cursor: body["start_cursor"] = cursor
        data = _http("POST", f"{NOTION_API}/data_sources/{BACKLOG_DS_ID}/query", tok, body)
        rows.extend(data.get("results", []))
        if not data.get("has_more"): break
        cursor = data.get("next_cursor")
    seen, out = set(), []
    for r in rows:
        if r["id"] in seen: continue
        seen.add(r["id"]); out.append(r)
    return out


def _txt(prop: dict | None) -> str:
    if not prop: return ""
    rt = prop.get("rich_text") or []
    return rt[0]["plain_text"] if rt else ""


def classify(row: dict) -> tuple[str, str]:
    p = row["properties"]
    title = p["Phase Title"]["title"][0]["plain_text"] if p["Phase Title"]["title"] else ""
    bi = _txt(p.get("Blocking Items"))
    sc = _txt(p.get("Success Criteria"))
    ev = _txt(p.get("Evidence"))
    haystack = f"{title}\n{bi}\n{sc}\n{ev}"

    # B before A: BACKLOG-tagged items often also reference dates.
    if B_SIGNALS.search(haystack):
        return "B", "backlog_tag"
    if A_SIGNALS.search(haystack):
        return "A", "time_or_dep_gated"
    # C-bucket: closure language must appear in BI or SC (not just title/evidence stamp).
    bi_sc = f"{bi}\n{sc}"
    if (bi or sc) and SOFT_CLOSURE.search(bi_sc) and not STRONG_CLOSURE.search(haystack):
        return "C", "soft_closure"
    return "D", "unblocked_work"


def annotate(tok: str, page_id: str, bucket: str, note_body: str, dry: bool) -> None:
    today = date.today().isoformat()
    addendum = f"[TRIAGE {today}] bucket={bucket}. {note_body}"[:1900]
    body = {"properties": {
        "Last Updated": {"date": {"start": today}},
        "Evidence": {"rich_text": [{"type": "text", "text": {"content": addendum}}]},
    }}
    if not dry:
        _http("PATCH", f"{NOTION_API}/pages/{page_id}", tok, body)


def retire(tok: str, page_id: str, reason: str, dry: bool) -> None:
    today = date.today().isoformat()
    body = {"properties": {
        "Status": {"select": {"name": "Retired"}},
        "Last Updated": {"date": {"start": today}},
        "Evidence": {"rich_text": [{"type": "text", "text": {"content": f"[TRIAGE {today}] retired: {reason}"[:1900]}}]},
    }}
    if not dry:
        _http("PATCH", f"{NOTION_API}/pages/{page_id}", tok, body)


def emit_plan(buckets: dict[str, list[dict]], path: Path) -> None:
    today = date.today().isoformat()
    lines = []
    lines.append("# Backlog Triage — KEEP-bucket Wave Plan")
    lines.append("")
    lines.append(f"Generated: {today}  ·  Status: Live")
    lines.append("")
    lines.append("## Context")
    lines.append("")
    lines.append("Companion to `bulk_flip_stale_not_started` (2026-05-02): of the 298 Not Started "
                 "rows in the Backlog Items DB, 89 were closed (commit-attested) and 54 "
                 "retired (plan deleted). The remaining ~155 are triaged here.")
    lines.append("")
    lines.append("## Wave Structure")
    lines.append("")
    lines.append("| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |")
    lines.append("|---|---|---|---:|---|---|---|")
    lines.append(f"| W1 | A.1 | Annotate {len(buckets['A'])} time/dep-gated rows: stays Not Started, recorded reason | 4000 | Rows have explicit gating language in Blocking Items | Live | All A-rows have Evidence stamped `[TRIAGE {today}] bucket=A` |")
    lines.append(f"| W2 | B.1 | Annotate {len(buckets['B'])} BACKLOG/future-idea rows: stays Not Started, recorded reason | 2000 | Rows tagged MCP-BACKLOG / NEXT·P* / FUTURE | Live | All B-rows stamped `bucket=B` |")
    lines.append(f"| W3 | C.1 | Retire {len(buckets['C'])} soft-closure rows (work likely done, no commit attestation) | 4000 | Soft-match on 'implemented/complete/landed' without commit SHA; spot-check via audit log | Live | C-rows flipped to Retired with reason |")
    lines.append(f"| W4 | D.1 | Surface {len(buckets['D'])} unblocked rows ranked by Impact Score for next-session pickup | 1000 | No mutation; ranking only | Live | Top-N table emitted in this plan |")
    lines.append("")
    lines.append("## Phase-Level Summary")
    lines.append("")
    lines.append("| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |")
    lines.append("|---|---|---|---|---:|---|")
    lines.append(f"| A.1 | Annotate gated Not Started rows | Notion Backlog Items DB ({len(buckets['A'])} rows) | None — pure annotation | 4000 | Live |")
    lines.append(f"| B.1 | Annotate BACKLOG-tagged Not Started rows | Notion Backlog Items DB ({len(buckets['B'])} rows) | None — pure annotation | 2000 | Live |")
    lines.append(f"| C.1 | Retire soft-closure Not Started rows | Notion Backlog Items DB ({len(buckets['C'])} rows) | False-positive risk if 'complete' refers to phase title | 4000 | Live |")
    lines.append(f"| D.1 | Rank unblocked work queue | Notion Backlog Items DB ({len(buckets['D'])} rows) | None — read-only | 1000 | Live |")
    lines.append("")
    lines.append("## Files In Scope")
    lines.append("")
    lines.append("- `tools/notion/triage_keep_drafts.py` — this triage script")
    lines.append("- `tools/notion/bulk_flip_stale_drafts.py` — predecessor (already executed 2026-05-02)")
    lines.append("- Notion Backlog Items DB (data source `fc7f6bf4-6a73-43cd-a4e8-1ef23267dbe7`)")
    lines.append("")
    lines.append("## Bucket Detail")
    lines.append("")
    for b, label in [("A", "Time/Dependency-Gated"), ("B", "BACKLOG / Future Ideas"), ("C", "Soft Closure (likely done)"), ("D", "Genuinely Unblocked")]:
        lines.append(f"### Bucket {b} — {label} ({len(buckets[b])} rows)")
        lines.append("")
        sample = buckets[b][:10]
        for r in sample:
            p = r["properties"]
            title = p["Phase Title"]["title"][0]["plain_text"][:80] if p["Phase Title"]["title"] else "(no title)"
            band = p["P-Band"]["select"]["name"] if p["P-Band"]["select"] else "--"
            lines.append(f"- `[{band}]` {title}")
        if len(buckets[b]) > 10:
            lines.append(f"- ... and {len(buckets[b]) - 10} more (see audit log)")
        lines.append("")

    # Top-10 D ranked by impact
    lines.append("## D-Bucket Ranked Work Queue (next-session candidates)")
    lines.append("")
    lines.append("| Rank | Band | Impact | Title | Plan File |")
    lines.append("|---:|---|---:|---|---|")
    d = []
    for r in buckets["D"]:
        p = r["properties"]
        impact = p.get("Impact Score", {}).get("number") or 0
        title = p["Phase Title"]["title"][0]["plain_text"][:70] if p["Phase Title"]["title"] else "(no title)"
        band = p["P-Band"]["select"]["name"] if p["P-Band"]["select"] else "--"
        plan = _txt(p.get("Plan File"))[:50]
        d.append((impact, band, title, plan))
    d.sort(reverse=True)
    for i, (impact, band, title, plan) in enumerate(d[:10], 1):
        lines.append(f"| {i} | {band} | {impact:.1f} | {title} | `{plan}` |")
    lines.append("")
    lines.append("## ADG_GRAPH_LAYER_EVIDENCE")
    lines.append("")
    lines.append("Not applicable — this is a backlog-governance plan, not a code refactor. "
                 "No agentic_core mutations. ADG snapshot unchanged. Constitutional §22 "
                 "graph-layer evidence requirement applies to T2/T3 *refactoring* plans only.")
    lines.append("")
    lines.append("## ADG_HOTSPOT_REPORT")
    lines.append("")
    lines.append("Not applicable — see above.")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def post_plan_to_notion(tok: str, plan_path: Path, slug: str) -> str:
    today = date.today().isoformat()
    body = {
        "parent": {"type": "database_id", "database_id": PLANS_DB_ID},
        "properties": {
            "Slug": {"title": [{"type": "text", "text": {"content": slug}}]},
            "Status": {"select": {"name": "In Progress"}},
            "Plan File Path": {"rich_text": [{"type": "text", "text": {"content": str(plan_path.relative_to(REPO_ROOT)).replace("\\", "/")}}]},
            "Exists On Disk": {"checkbox": True},
            "Summary": {"rich_text": [{"type": "text", "text": {"content": f"Backlog KEEP-bucket triage: A/B/C/D classification of 155 surviving Not Started rows after 2026-05-02 bulk-flip. Companion to bulk_flip_stale_drafts.py."}}]},
        },
    }
    res = _http("POST", f"{NOTION_API}/pages", tok, body)
    return res["id"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--emit-plan", type=str, default="")
    ap.add_argument("--post-plan-notion", action="store_true")
    args = ap.parse_args()
    if args.dry_run == args.execute:
        ap.error("specify --dry-run or --execute")

    tok = _token()
    rows = fetch_not_started(tok)
    print(f"not started rows: {len(rows)}", flush=True)

    buckets: dict[str, list[dict]] = {"A": [], "B": [], "C": [], "D": []}
    classifications: dict[str, str] = {}
    for r in rows:
        b, reason = classify(r)
        buckets[b].append(r)
        classifications[r["id"]] = reason
    for k in "ABCD":
        print(f"  {k}: {len(buckets[k])}", flush=True)

    if args.emit_plan:
        plan_path = Path(args.emit_plan)
        if not plan_path.is_absolute():
            plan_path = REPO_ROOT / plan_path
        emit_plan(buckets, plan_path)
        print(f"plan written: {plan_path}", flush=True)

    if args.post_plan_notion and args.emit_plan:
        plan_path = Path(args.emit_plan)
        if not plan_path.is_absolute():
            plan_path = REPO_ROOT / plan_path
        slug = plan_path.stem
        if not args.dry_run:
            page_id = post_plan_to_notion(tok, plan_path, slug)
            print(f"Notion plans row: {page_id}", flush=True)
            _audit({"step": "post_plan", "page_id": page_id, "slug": slug})

    # Mutations
    print("\n--- mutations ---", flush=True)
    n_a, n_b, n_c = 0, 0, 0
    for r in buckets["A"]:
        annotate(tok, r["id"], "A", "time/dependency gated; stays Not Started pending external clock or dependency.", args.dry_run)
        n_a += 1; _audit({"step": "annotate_A", "page_id": r["id"], "dry_run": args.dry_run})
        time.sleep(0.35)
    print(f"A annotated: {n_a}", flush=True)
    for r in buckets["B"]:
        annotate(tok, r["id"], "B", "BACKLOG / future-idea row; intentionally Not Started until promoted.", args.dry_run)
        n_b += 1; _audit({"step": "annotate_B", "page_id": r["id"], "dry_run": args.dry_run})
        time.sleep(0.35)
    print(f"B annotated: {n_b}", flush=True)
    for r in buckets["C"]:
        retire(tok, r["id"], "soft-closure language without commit attestation; assumed done after 2026-05-02 audit. Reopen if work resurfaces.", args.dry_run)
        n_c += 1; _audit({"step": "retire_C", "page_id": r["id"], "dry_run": args.dry_run})
        time.sleep(0.35)
    print(f"C retired: {n_c}", flush=True)
    print(f"D untouched (work queue): {len(buckets['D'])}", flush=True)
    print(f"\naudit: {AUDIT_LOG}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
