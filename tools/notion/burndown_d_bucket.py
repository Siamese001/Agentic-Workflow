#!/usr/bin/env python3
"""D-bucket burndown — mechanical pass only.

Second-level triage of the D-bucket after `triage_keep_drafts.py`. Catches:

  A' — Expanded time/dep-gated (adds full 2026-*/2027-* date-reminder titles,
        "monitor ... for fix", "audit ... eligibility", "graduate to strict")
  MP — Plan file no longer on disk → retire (plan-DB invariant per AGENTS.md)
  C' — Soft-closure missed in first pass (e.g., "DONE\\n" with date)
  D  — Genuine engineering residual; NOT touched. Wave plan emitted for
       operator review.

Usage:
  python tools/notion/burndown_d_bucket.py --dry-run --emit-plan PATH
  python tools/notion/burndown_d_bucket.py --execute --emit-plan PATH --post-plan-notion
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
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

# Reuse helpers from triage_keep_drafts
_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
from triage_keep_drafts import (  # type: ignore[import-not-found]
    _token, _http, _audit as _base_audit, _txt, fetch_drafts, classify as classify_primary,
    annotate as annotate_primary, retire as retire_primary,
    post_plan_to_notion, NOTION_API, PLANS_DB_ID, REPO_ROOT,
)

AUDIT_LOG = REPO_ROOT / "artifacts" / "windsurf" / "burndown_d_bucket_audit.jsonl"
PLANS_DIR = REPO_ROOT / ".windsurf" / "plans"

# Expanded A-catch: any ISO date in title (calendar-reminder rows), monitor/audit
# operational patterns, "graduate to strict" migration reminders.
A_EXPANDED = re.compile(
    r"(?i)("
    r"^\s*\[P\d\]\s*2026-\d{2}-\d{2}"              # "[P3] 2026-07-27 audit ..."
    r"|^\s*\[P\d\]\s*2027-\d{2}-\d{2}"
    r"|^\s*2026-\d{2}-\d{2}"
    r"|monitor\s+\S+#\d+\s+for\s+fix"              # "monitor anthropics/...#41 for fix"
    r"|auto-retire\s+eligibility"
    r"|graduate to strict"
    r"|drop\s+--advisory"
    r"|remove\s+[A-Za-z0-9_\-]+\s+deprecated shim"
    r")"
)

# Extra C-catch: "DONE" appearing on its own line, "Follow-up deferred scope"
C_EXPANDED = re.compile(
    r"(?i)(^DONE\b|^Done\.\s|Follow-up deferred scope|fully validated|all .* met)",
    re.MULTILINE,
)


def classify_d_pass2(row: dict, on_disk_plans: set[str]) -> tuple[str, str]:
    """Re-classify a D-bucket row with expanded rules."""
    p = row["properties"]
    title = p["Phase Title"]["title"][0]["plain_text"] if p["Phase Title"]["title"] else ""
    bi = _txt(p.get("Blocking Items"))
    sc = _txt(p.get("Success Criteria"))
    ev = _txt(p.get("Evidence"))
    plan = _txt(p.get("Plan File"))
    haystack = f"{title}\n{bi}\n{sc}\n{ev}"

    if A_EXPANDED.search(haystack):
        return "A2", "expanded_time_or_reminder"

    # Plan missing on disk (same rule as bulk_flip step 2, applied to D-rows)
    pf = plan.split("/")[-1].strip() if plan else ""
    if pf and pf.endswith(".md") and pf not in on_disk_plans:
        if pf.startswith("(") or pf.startswith("NEW:"):
            return "D2", "placeholder_plan"  # keep; not a real missing-plan
        return "MP", f"plan_missing:{pf}"

    if C_EXPANDED.search(haystack) and (bi or sc):
        return "C2", "expanded_soft_closure"

    return "D2", "residual_engineering"


def emit_wave_plan(d_rows: list[dict], path: Path) -> None:
    today = date.today().isoformat()
    # Group by plan file
    by_plan: dict[str, list[dict]] = defaultdict(list)
    for r in d_rows:
        plan = _txt(r["properties"].get("Plan File")) or "(no plan)"
        pf = plan.split("/")[-1].strip()
        by_plan[pf].append(r)

    # Sort plans by max impact desc
    def _max_impact(rows):
        return max((r["properties"].get("Impact Score", {}).get("number") or 0 for r in rows), default=0)
    plans_sorted = sorted(by_plan.items(), key=lambda kv: -_max_impact(kv[1]))

    # Size waves: W1 = top-impact single plan, W2 = next 2 plans, W3 = remainder
    def _band(r):
        return (r["properties"]["P-Band"]["select"] or {}).get("name") or "--"

    lines = []
    lines.append("# D-Bucket Burndown Wave Plan")
    lines.append("")
    lines.append(f"Generated: {today}  ·  Status: Live  ·  Companion to `backlog-keep-triage-d2e4f1`")
    lines.append("")
    lines.append("## Context")
    lines.append("")
    lines.append(f"Remaining {len(d_rows)} D-bucket rows after mechanical pass 2. "
                 "These represent real engineering work, not admin. Waves below "
                 "group by plan file and size by combined impact score. "
                 "Execution is cross-session: W1 first, then stop for review.")
    lines.append("")
    lines.append("## Wave Structure")
    lines.append("")
    lines.append("| Wave | Plans | Row Count | Max Impact | Est. Days | Status |")
    lines.append("|---|---|---:|---:|---:|---|")
    waves: list[tuple[str, list[tuple[str, list[dict]]]]] = []
    # W1: top 1 plan
    w1 = plans_sorted[:1]
    # W2: next 3 plans
    w2 = plans_sorted[1:4]
    # W3: next 6 plans
    w3 = plans_sorted[4:10]
    # W4: remainder
    w4 = plans_sorted[10:]
    for wname, wplans in [("W1", w1), ("W2", w2), ("W3", w3), ("W4", w4)]:
        total = sum(len(rows) for _, rows in wplans)
        mi = max((_max_impact(rows) for _, rows in wplans), default=0)
        est_days = max(1, total // 3)
        plan_str = ", ".join(f"`{pf}` ({len(rows)})" for pf, rows in wplans)[:180]
        lines.append(f"| {wname} | {plan_str} | {total} | {mi:.0f} | {est_days} | Draft |")
        waves.append((wname, wplans))
    lines.append("")
    lines.append("## Phase-Level Summary")
    lines.append("")
    lines.append("| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |")
    lines.append("|---|---|---|---|---:|---|")
    for wname, wplans in waves:
        for pf, rows in wplans:
            bands = Counter(_band(r) for r in rows)
            scope = f"Notion rows attached to {pf} — {len(rows)} items"
            pain = f"bands={dict(bands)}; max impact {_max_impact(rows):.0f}"
            est = 3000 * len(rows)
            lines.append(f"| {wname}.{pf[:20]} | Burn down {pf} D-rows | {scope} | {pain} | {est} | Draft |")
    lines.append("")
    lines.append("## Files In Scope")
    lines.append("")
    lines.append("- Notion Backlog Items DB (data source `fc7f6bf4-6a73-43cd-a4e8-1ef23267dbe7`)")
    lines.append("- Each plan file referenced above under `.windsurf/plans/`")
    lines.append("- `tools/notion/burndown_d_bucket.py` — this driver")
    lines.append("")
    lines.append("## ADG_GRAPH_LAYER_EVIDENCE")
    lines.append("")
    lines.append("Not applicable — governance plan. ADG evidence lives in each child plan.")
    lines.append("")
    lines.append("## ADG_HOTSPOT_REPORT")
    lines.append("")
    lines.append("Not applicable — see above.")
    lines.append("")
    lines.append("## W1 Detail — top-impact plan (start here)")
    lines.append("")
    for pf, rows in w1:
        lines.append(f"### `{pf}` — {len(rows)} rows")
        lines.append("")
        lines.append("| Band | Impact | Title |")
        lines.append("|---|---:|---|")
        for r in sorted(rows, key=lambda x: -(x["properties"].get("Impact Score", {}).get("number") or 0)):
            band = _band(r)
            impact = r["properties"].get("Impact Score", {}).get("number") or 0
            t = r["properties"]["Phase Title"]["title"]
            title = t[0]["plain_text"][:100] if t else "(no title)"
            lines.append(f"| {band} | {impact:.0f} | {title} |")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--emit-plan", type=str, required=True)
    ap.add_argument("--post-plan-notion", action="store_true")
    args = ap.parse_args()
    if args.dry_run == args.execute:
        ap.error("specify --dry-run or --execute")

    tok = _token()
    on_disk = {f.name for f in PLANS_DIR.iterdir() if f.suffix == ".md"}
    print(f"plans on disk: {len(on_disk)}", flush=True)

    rows = fetch_drafts(tok)
    d_rows = [r for r in rows if classify_primary(r)[0] == "D"]
    print(f"D-rows fetched: {len(d_rows)}", flush=True)

    buckets: dict[str, list[tuple[dict, str]]] = {"A2": [], "MP": [], "C2": [], "D2": []}
    for r in d_rows:
        b, reason = classify_d_pass2(r, on_disk)
        buckets[b].append((r, reason))

    for k in ("A2", "MP", "C2", "D2"):
        print(f"  {k}: {len(buckets[k])}", flush=True)

    residual = [r for r, _ in buckets["D2"]]
    plan_path = Path(args.emit_plan)
    if not plan_path.is_absolute():
        plan_path = REPO_ROOT / plan_path
    emit_wave_plan(residual, plan_path)
    print(f"plan: {plan_path}", flush=True)

    if args.post_plan_notion and not args.dry_run:
        slug = plan_path.stem
        page_id = post_plan_to_notion(tok, plan_path, slug)
        print(f"notion plan row: {page_id}", flush=True)

    print("\n--- mutations ---", flush=True)
    n_a, n_mp, n_c = 0, 0, 0
    for r, _ in buckets["A2"]:
        annotate_primary(tok, r["id"], "A2", "date-reminder or expanded time/dep-gated; stays Draft.", args.dry_run)
        n_a += 1
        time.sleep(0.35)
    print(f"A2 annotated: {n_a}", flush=True)
    for r, reason in buckets["MP"]:
        pf = reason.split(":", 1)[1] if ":" in reason else "?"
        retire_primary(tok, r["id"], f"plan file '{pf}' not on disk (D-bucket pass 2).", args.dry_run)
        n_mp += 1
        time.sleep(0.35)
    print(f"MP retired: {n_mp}", flush=True)
    for r, _ in buckets["C2"]:
        retire_primary(tok, r["id"], "expanded soft-closure match (D-bucket pass 2).", args.dry_run)
        n_c += 1
        time.sleep(0.35)
    print(f"C2 retired: {n_c}", flush=True)
    print(f"D2 residual (in wave plan): {len(residual)}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
