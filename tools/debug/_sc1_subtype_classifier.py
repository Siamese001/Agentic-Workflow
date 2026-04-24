"""W7.1-P0: SC-1 structural-conformance subtype classifier.

Because the ADG snapshot does not materialize `v_structural_conformance` as a
SQL view (it's computed at gate-time in Python), we reconstruct the SC-1
violation set by unioning the P-views that flag structural boundary /
mis-layering / cycle / bypass defects, then classify each row into one of
four subtypes per ADR-051:

    Subtype 1 — direct mutation bypass          (Write/State Surface)
    Subtype 2 — boundary bypass                 (Execution Surface)
    Subtype 3 — ingress shortcut                (Execution Surface)
    Subtype 4 — exit-control skip               (Security Surface)

Outputs a markdown report with per-violation subtype + layer + archetype
hints + fan-in + surface. This is read-only; no edits.
"""
from __future__ import annotations

import sqlite3
from collections import Counter, defaultdict
from datetime import datetime, timezone

UTC = timezone.utc
from pathlib import Path

SNAP = sorted(Path("artifacts/adg").glob("adg_indexed_*.sqlite"))[-1]
OUT_REPORT = Path(
    f"docs/reports/sc1_subtype_triage_{datetime.now(UTC):%Y%m%d}.md"
)
OUT_REPORT.parent.mkdir(parents=True, exist_ok=True)

# P-view -> (subtype, surface, rationale)
SOURCES: dict[str, tuple[int, str, str]] = {
    "v_p0_write_bypass_uwg":   (1, "Write",      "direct write bypassing UWG"),
    "v_p0_l6_mutation":         (1, "State",      "L6 direct mutation"),
    "v_p0_apps_direct_infra":   (2, "Execution",  "apps reaching infrastructure"),
    "v_p0_l1_direct_infra":     (2, "Execution",  "L1 reaching infrastructure"),
    "v_p1_mis_layered_infra":   (2, "Execution",  "mis-layered infra dependency"),
    "v_p0_l0_raw_execution":    (3, "Execution",  "L0 raw execution ingress"),
    "v_p0_provider_bypass":     (4, "Security",   "provider bypass skipping exit-control"),
}


def main() -> int:
    con = sqlite3.connect(str(SNAP))
    cur = con.cursor()

    # Discover column schema for each source view (varies per view)
    view_cols: dict[str, list[str]] = {}
    for view in SOURCES:
        try:
            cur.execute(f"SELECT * FROM {view} LIMIT 1")
            view_cols[view] = [d[0] for d in cur.description]
        except sqlite3.Error:
            view_cols[view] = []

    # Build ranked violation list: (subtype, surface, rationale, view, row_dict)
    rows: list[dict] = []
    per_view_count: Counter[str] = Counter()
    for view, (subtype, surface, rationale) in SOURCES.items():
        cols = view_cols.get(view) or []
        if not cols:
            continue
        try:
            cur.execute(f"SELECT * FROM {view}")
        except sqlite3.Error:
            continue
        for r in cur.fetchall():
            rec = dict(zip(cols, r, strict=False))
            rec["_subtype"] = subtype
            rec["_surface"] = surface
            rec["_rationale"] = rationale
            rec["_source_view"] = view
            rows.append(rec)
            per_view_count[view] += 1

    # Attach fan-in from nodes/edges tables where possible.
    # Best-effort module path identification.
    def find_module_key(rec: dict) -> str | None:
        for k in ("writer_file", "file", "src_module", "src", "module", "file_path", "path", "importer", "from_module"):
            if k in rec and rec[k]:
                return str(rec[k])
        return None

    # Cache fan-in counts per module
    fan_in_cache: dict[str, int] = {}
    def fan_in(module_key: str) -> int:
        if module_key in fan_in_cache:
            return fan_in_cache[module_key]
        try:
            # imports edges where target node's file_path == module_key or module
            cur.execute(
                "SELECT COUNT(*) FROM edges e JOIN nodes n ON e.tgt_id = n.id "
                "WHERE (n.file_path = ? OR n.adg_name = ?) AND e.relation_type = 'imports'",
                (module_key, module_key),
            )
            row = cur.fetchone()
            count = int(row[0]) if row else 0
        except sqlite3.Error:
            count = 0
        fan_in_cache[module_key] = count
        return count

    # Dedupe + enrich
    seen: set[tuple] = set()
    deduped: list[dict] = []
    for rec in rows:
        key = (rec.get("_source_view"), tuple(sorted(rec.items())))
        if key in seen:
            continue
        seen.add(key)
        mod = find_module_key(rec)
        rec["_module"] = mod or "(unknown)"
        rec["_fan_in"] = fan_in(mod) if mod else 0
        deduped.append(rec)

    # Group counts
    by_subtype: Counter[int] = Counter(rec["_subtype"] for rec in deduped)
    by_surface: Counter[str] = Counter(rec["_surface"] for rec in deduped)

    # --- emit markdown report ---
    lines: list[str] = []
    lines.append(f"# SC-1 Subtype Triage Report — {datetime.now(UTC):%Y-%m-%d}")
    lines.append("")
    lines.append(f"- Snapshot: `{SNAP.name}`")
    lines.append(f"- Total structural violations classified: **{len(deduped)}**")
    lines.append(
        "- Data source: unioned P-views (v_p0_write_bypass_uwg, "
        "v_p0_l6_mutation, v_p0_apps_direct_infra, v_p0_l1_direct_infra, "
        "v_p1_mis_layered_infra, v_p0_l0_raw_execution, v_p0_provider_bypass)."
    )
    lines.append(
        "- Note: `v_structural_conformance` is not materialized in this "
        "snapshot (gate computes SC-1 in Python at run time). This classifier "
        "reconstructs the intended set from the P-view surfaces."
    )
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("State Surface + Write Surface + Execution Surface + Security Surface.")
    lines.append("")
    lines.append("## Per-source-view counts")
    lines.append("")
    lines.append("| P-view | Count | Subtype | Surface |")
    lines.append("|---|---:|:---:|:---:|")
    for view, (subtype, surface, _) in SOURCES.items():
        lines.append(f"| `{view}` | {per_view_count[view]} | {subtype} | {surface} |")
    lines.append("")
    lines.append("## Subtype totals")
    lines.append("")
    lines.append("| Subtype | Description | Count |")
    lines.append("|:---:|---|---:|")
    subtype_desc = {
        1: "Direct mutation bypass",
        2: "Boundary bypass",
        3: "Ingress shortcut",
        4: "Exit-control skip",
    }
    for st in (1, 2, 3, 4):
        lines.append(f"| {st} | {subtype_desc[st]} | {by_subtype.get(st, 0)} |")
    lines.append("")
    lines.append("## Surface totals")
    lines.append("")
    lines.append("| Surface | Count |")
    lines.append("|---|---:|")
    for surface in ("Write", "State", "Execution", "Security"):
        lines.append(f"| {surface} | {by_surface.get(surface, 0)} |")
    lines.append("")

    # Top modules by violation count
    mod_counter: Counter[str] = Counter(rec["_module"] for rec in deduped)
    lines.append("## Top 20 modules by structural-violation count")
    lines.append("")
    lines.append("| Module | Violations | Fan-in (imports) |")
    lines.append("|---|---:|---:|")
    for mod, cnt in mod_counter.most_common(20):
        fi = fan_in(mod) if mod != "(unknown)" else 0
        lines.append(f"| `{mod}` | {cnt} | {fi} |")
    lines.append("")

    # Per-violation listing (capped at 200 for readability)
    lines.append("## Per-violation detail (first 200 rows)")
    lines.append("")
    lines.append("| # | Subtype | Surface | Module | Fan-in | Source view | Rationale |")
    lines.append("|---:|:---:|:---:|---|---:|---|---|")
    for idx, rec in enumerate(deduped[:200], 1):
        mod = rec["_module"]
        fi = rec["_fan_in"]
        lines.append(
            f"| {idx} | {rec['_subtype']} | {rec['_surface']} | `{mod}` | {fi} | "
            f"`{rec['_source_view']}` | {rec['_rationale']} |"
        )
    if len(deduped) > 200:
        lines.append("")
        lines.append(f"_... {len(deduped) - 200} additional rows omitted for readability._")
    lines.append("")

    # Archetype hints (cross-reference mv_hotspot_centrality)
    lines.append("## Archetype hints (top-10 modules intersecting `mv_hotspot_centrality`)")
    lines.append("")
    try:
        cur.execute(
            "SELECT name FROM sqlite_master WHERE name='mv_hotspot_centrality' AND type='table'"
        )
        if cur.fetchone():
            cur.execute("SELECT * FROM mv_hotspot_centrality LIMIT 1")
            hc_cols = [d[0] for d in cur.description]
            lines.append(f"Columns: `{hc_cols}`")
            top_mods = [m for m, _ in mod_counter.most_common(10)]
            for mod in top_mods:
                try:
                    col = "file_path" if "file_path" in hc_cols else (
                        "module" if "module" in hc_cols else (
                        "adg_name" if "adg_name" in hc_cols else None
                    ))
                    if col:
                        cur.execute(
                            f"SELECT * FROM mv_hotspot_centrality WHERE {col}=? LIMIT 1",
                            (mod,),
                        )
                        row = cur.fetchone()
                        if row:
                            lines.append(f"- `{mod}`: {dict(zip(hc_cols, row, strict=False))}")
                except sqlite3.Error:
                    continue
        else:
            lines.append("_mv_hotspot_centrality not available in this snapshot._")
    except sqlite3.Error as exc:
        lines.append(f"_hotspot centrality lookup failed: {exc}_")
    lines.append("")

    lines.append("## Next-phase input (W7.1-P1 remediation plan)")
    lines.append("")
    lines.append(
        "Subtype 1 rows (Write/State Surface) are scheduled first per ADR-051 "
        "because they intersect the L5 safety plane with the highest layer "
        "multiplier (×2.0). Subtypes 2+3 follow in W7.1-P2; subtype 4 and "
        "legitimate exemptions in W7.1-P3; validation + close in W7.1-P4."
    )
    lines.append("")
    lines.append(f"_Generated by `tools/debug/_sc1_subtype_classifier.py` on {datetime.now(UTC).isoformat()}._")

    OUT_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_REPORT} ({len(deduped)} violations classified)")
    print(f"subtype tallies: {dict(by_subtype)}")
    print(f"surface tallies: {dict(by_surface)}")
    con.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
