"""Generate a human-scoring worksheet for the 63 genuinely UNSCORED rows.

Reads artifacts/notion/_pending_rescore.json + open_rows_with_ids.json
and emits a CSV-style markdown worksheet for a human to fill in.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROWS = json.loads((ROOT / "artifacts/notion/open_rows_with_ids.json").read_text(encoding="utf-8"))
RESCORE = json.loads((ROOT / "artifacts/notion/_pending_rescore.json").read_text(encoding="utf-8"))

BAND_RE = re.compile(r"\[(P[1-5])\]")

# Already-scored rows from last session (Wave A + Wave B + Wave D applications)
APPLIED_IN_PRIOR = {
    "W2-P1/2.1", "F4/F4.2", "W3/P3.1", "W4/W4",  # Wave A
    "GAP/GAP-4", "W5/5.1", "Wave 3/3.2", "W1-P0/1.2",  # Wave B
    "H6/H6.1", "H7/H7.1", "H8/H8.1", "H9/H9.1", "H10/H10.1",  # Wave D
}


def categorize(wave: str, phase: str, title: str) -> str:
    if wave in ("W1", "W2") and re.match(r"\d+\.\d+", phase):
        return "governance"
    if wave in ("W9", "W11", "W12", "W13"):
        return "graph-edge"
    if wave in ("Wave 1", "Wave 2", "Wave 3", "Wave 4"):
        return "structure-cleanup"
    if wave in ("W3-P2", "W1-P0", "GAP", "W4-P3"):
        return "baseline-burndown"
    if wave in ("ENH1", "ENH2", "ENH3", "ENH4", "ENH5", "ENH6"):
        return "enhancement"
    if wave in ("W2-P1",):
        return "governance"
    return "singleton"


def main():
    rows_by_id = {r["id"]: r for r in ROWS}
    unscorable = [r for r in RESCORE if r.get("proposed_band") == "UNSCORABLE"]

    # Filter: skip rows that were applied in prior waves
    worksheet_rows = []
    for ur in unscorable:
        key = f"{ur['wave']}/{ur['phase']}"
        if key in APPLIED_IN_PRIOR:
            continue
        # Also skip if title has [Pn] (already done in Wave D)
        if BAND_RE.search(ur["title"]):
            continue
        row = rows_by_id.get(ur["id"])
        if not row:
            continue
        worksheet_rows.append(row)

    print(f"Worksheet candidates: {len(worksheet_rows)}")

    # Group by category
    by_cat: dict[str, list[dict]] = {}
    for r in worksheet_rows:
        cat = categorize(r["wave"], r["phase"], r["title"])
        by_cat.setdefault(cat, []).append(r)

    for cat, items in sorted(by_cat.items()):
        print(f"  {cat}: {len(items)}")

    # Emit markdown worksheet
    dest = ROOT / "artifacts" / "notion" / "human_scoring_worksheet.md"
    lines = [
        "# Human Scoring Worksheet — 63 UNSCORED Wave/Phase Convergence rows",
        "",
        "**Instructions**: For each row, fill in the `BAND` column with one of `P1`/`P2`/`P3`/`P4`/`P5`/`DESCOPE`/`SKIP`.",
        "",
        "Optional columns to aid scoring (all optional — the applier will PATCH whatever you fill in):",
        "- `LAYER`: L0..L6 / L_OPS / L_TOOLS / L_SHARED / L_APP / L_SL / L_PG / L_INFRA / L_RUNTIME",
        "- `FILES`: comma-separated paths (populates Files In Scope, unblocks future auto-scoring)",
        "- `NOTES`: any freeform text appended to Blocking Items",
        "",
        "## Scoring cheat-sheet (constitutional §24)",
        "",
        "```",
        "impact = coverage_gap_pct × layer_multiplier × (1 + log10(1 + fan_in)) × surface_boost",
        "",
        "layer_multiplier:  L0=2.0, L5=2.0, L3=1.75, L4=1.75, L1=1.0, L2=1.0, L6=0.75, else 1.0",
        "surface_boost:     Security=1.5, Write=1.4, Execution=1.3, State=1.2, Observability=1.1, None=1.0",
        "",
        "Bands: P1 ≥300, P2 ≥150, P3 ≥75, P4 ≥30, P5 <30",
        "```",
        "",
        "## Quick heuristics (if you don't want to compute)",
        "",
        "- Gate/hook wiring on L0 or L5 → **P1**",
        "- Bug fix on L3/L4 with >5 callers → **P2**",
        "- Single-file refactor on L1/L2 → **P3**",
        "- Documentation-only or style → **P4/P5**",
        "- Already landed or obsolete → **DESCOPE**",
        "- Need more info → **SKIP** (leave as UNSCORED)",
        "",
    ]

    for cat in sorted(by_cat):
        items = by_cat[cat]
        items.sort(key=lambda r: (r["wave"], r["phase"]))
        lines.append(f"## {cat.upper()} ({len(items)} rows)")
        lines.append("")
        lines.append("| id | wave | phase | title | BAND | LAYER | FILES | NOTES |")
        lines.append("|---|---|---|---|---|---|---|---|")
        for r in items:
            title = r["title"].replace("|", "\\|")[:80]
            lines.append(f"| `{r['id'][:8]}` | {r['wave']} | {r['phase']} | {title} | | | | |")
        lines.append("")

    dest.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nWrote: {dest}")

    # Also emit a JSON version for the applier script
    data_dest = ROOT / "artifacts" / "notion" / "human_scoring_worksheet.json"
    data = []
    for r in worksheet_rows:
        data.append({
            "id": r["id"],
            "wave": r["wave"],
            "phase": r["phase"],
            "title": r["title"],
            "category": categorize(r["wave"], r["phase"], r["title"]),
            "BAND": "",
            "LAYER": "",
            "FILES": "",
            "NOTES": "",
        })
    data_dest.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Wrote: {data_dest}")


if __name__ == "__main__":
    main()
