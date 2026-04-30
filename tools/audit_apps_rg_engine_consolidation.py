"""W5 audit-only — apps_rg engine consolidation candidate report.

Queries the latest ADG SQLite snapshot directly (constitutional §28 fallback
hierarchy: MCP -> direct sqlite3 -> grep). For every engine file under
`apps_rg/engines/`, computes:

  * fan-out (imports)  -> proxy for complexity
  * fan-in (referrers)  -> proxy for blast radius
  * shared imports with siblings (Jaccard similarity of import sets)

Pairs with Jaccard >= 0.50 are surfaced as consolidation candidates.

Output: docs/reports/apps_rg_engine_consolidation_candidates.md
"""
from __future__ import annotations

import sqlite3
from collections import defaultdict
from itertools import combinations
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ADG_DIR = REPO / "artifacts" / "adg"
OUT = REPO / "docs" / "reports" / "apps_rg_engine_consolidation_candidates.md"


def latest_snapshot() -> Path:
    cands = sorted(ADG_DIR.glob("adg_indexed_*.sqlite"))
    if not cands:
        raise SystemExit("no ADG snapshot found")
    return cands[-1]


def main() -> int:
    snap = latest_snapshot()
    con = sqlite3.connect(str(snap))

    # Engine files
    engine_rows = con.execute("""
        SELECT DISTINCT resolved_path
        FROM nodes
        WHERE resolved_path LIKE 'apps_rg/engines/%'
          AND resolved_path NOT LIKE '%__pycache__%'
          AND resolved_path NOT LIKE '%/__init__.py'
        ORDER BY resolved_path
    """).fetchall()
    engine_paths = [r[0] for r in engine_rows]
    print(f"engine_files={len(engine_paths)}")

    # Build import-target sets per engine file, plus fan-in/fan-out
    imports_per: dict[str, set[str]] = defaultdict(set)
    fanout: dict[str, int] = {}
    fanin: dict[str, int] = {}
    for path in engine_paths:
        cur = con.execute("""
            SELECT DISTINCT n2.resolved_path
            FROM edges e
            JOIN nodes n1 ON n1.id = e.src_id
            JOIN nodes n2 ON n2.id = e.dst_id
            WHERE e.relation_type = 'imports'
              AND n1.resolved_path = ?
        """, (path,))
        targets = {r[0] for r in cur.fetchall() if r[0]}
        imports_per[path] = targets
        fanout[path] = len(targets)
        cur = con.execute(
            "SELECT COUNT(DISTINCT n.resolved_path) FROM edges e "
            "JOIN nodes n ON n.id = e.src_id "
            "JOIN nodes m ON m.id = e.dst_id "
            "WHERE e.relation_type = 'imports' AND m.resolved_path = ?",
            (path,),
        )
        fanin[path] = (cur.fetchone() or (0,))[0]

    # Compute pairwise Jaccard similarity on import-target sets
    candidates: list[tuple[float, str, str, int, int, int]] = []
    for a, b in combinations(engine_paths, 2):
        sa, sb = imports_per[a], imports_per[b]
        if not sa or not sb:
            continue
        inter = len(sa & sb)
        union = len(sa | sb)
        if union == 0:
            continue
        jacc = inter / union
        if jacc >= 0.50:
            candidates.append((jacc, a, b, inter, fanout[a], fanout[b]))
    candidates.sort(reverse=True)

    # Build markdown
    lines: list[str] = []
    lines.append("# apps_rg Engine Consolidation Candidates (W5 audit-only)")
    lines.append("")
    lines.append(f"Snapshot: `{snap.name}`")
    lines.append(f"Engine files scanned: **{len(engine_paths)}**")
    lines.append("")
    lines.append("## How candidates were ranked")
    lines.append("")
    lines.append("- For every engine file, the import-target set was extracted from the static ADG (`relation_type='imports'`).")
    lines.append("- For every pair of engines, Jaccard similarity of their import-target sets was computed.")
    lines.append("- Pairs with Jaccard ≥ 0.50 are surfaced as candidates: they share at least half of their downstream dependencies and so likely share most of their cross-cutting concerns.")
    lines.append("- This is a structural similarity proxy. It does NOT imply behavioral equivalence; before any actual consolidation, behavioral parity must be verified by reading both engines.")
    lines.append("")
    lines.append("## Candidate pairs (Jaccard ≥ 0.50)")
    lines.append("")
    if not candidates:
        lines.append("_No pairs cleared the 0.50 Jaccard threshold. The engine surface appears already de-duplicated._")
    else:
        lines.append("| Rank | Jaccard | Engine A | Engine B | Shared deps | A fan-out | B fan-out |")
        lines.append("|---:|---:|---|---|---:|---:|---:|")
        for i, (jacc, a, b, inter, fa, fb) in enumerate(candidates[:20], 1):
            lines.append(f"| {i} | {jacc:.2f} | `{a.split('/')[-1]}` | `{b.split('/')[-1]}` | {inter} | {fa} | {fb} |")

    # Top fan-out hotspots (orchestration + assembly engines tend to dominate)
    lines.append("")
    lines.append("## Top fan-out engine files (complexity proxy)")
    lines.append("")
    lines.append("| Rank | File | Fan-out | Fan-in |")
    lines.append("|---:|---|---:|---:|")
    sorted_fanout = sorted(engine_paths, key=lambda p: -fanout[p])
    for i, p in enumerate(sorted_fanout[:15], 1):
        lines.append(f"| {i} | `{p}` | {fanout[p]} | {fanin[p]} |")

    # Recommendation
    lines.append("")
    lines.append("## Recommendation")
    lines.append("")
    if candidates:
        top_pairs = candidates[:5]
        lines.append("This audit-only report identifies the following consolidation-candidate pairs, ranked by import-set similarity. Each pair is a hypothesis — not a directive. Before merging, perform Author-Gate decision per `anti-pattern-author-gate.md`:")
        lines.append("")
        for i, (jacc, a, b, inter, fa, fb) in enumerate(top_pairs, 1):
            lines.append(f"{i}. **`{a.split('/')[-1]}` ↔ `{b.split('/')[-1]}`** (Jaccard {jacc:.2f}, {inter} shared deps).")
        lines.append("")
        lines.append("Each candidate consolidation is a separate refactor-class decision. Following constitutional §6, none of the above should be executed silently. Open an ADR per pair, capture the parity-verification evidence, and route through the `architecture_choice` Author-Gate.")
    else:
        lines.append("No structural duplication detected at the import-set level. Consolidation effort is better spent elsewhere (e.g., antipattern burndown, test coverage uplift).")
    lines.append("")
    lines.append("## Out of scope for this report")
    lines.append("")
    lines.append("- Behavioral parity verification (requires reading both engine bodies + their tests)")
    lines.append("- Actual file deletions or merges (that's a real refactor — needs Author-Gate)")
    lines.append("- Ranking by runtime invocation frequency (would require otel_mcp runtime-ADG queries)")
    lines.append("- Test-suite impact estimation (would require ADG-test-triage-gate)")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(REPO)}")
    print(f"candidates_above_0.50_jaccard={len(candidates)}")
    if candidates:
        print(f"top_pair_jaccard={candidates[0][0]:.2f}: {candidates[0][1].split('/')[-1]} <-> {candidates[0][2].split('/')[-1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
