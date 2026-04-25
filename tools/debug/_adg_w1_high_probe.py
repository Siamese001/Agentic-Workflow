"""W1 Phase 1.1 — pull the 3 HIGH severity antipattern rows + top-4 Tier-B files."""

from __future__ import annotations
import sqlite3
from pathlib import Path

DB = Path("artifacts/adg/adg_indexed_04232026_2248.sqlite")


def main() -> int:
    c = sqlite3.connect(str(DB)).cursor()

    print("=" * 80)
    print("HIGH-SEVERITY ANTIPATTERN ROWS (all columns)")
    print("=" * 80)
    cols = [d[0] for d in c.execute("SELECT * FROM violations LIMIT 0").description]
    print(f"cols: {cols}\n")
    rows = c.execute("SELECT * FROM violations WHERE severity='HIGH' AND category='antipattern'").fetchall()
    for r in rows:
        d = dict(zip(cols, r))
        print(f"--- id={d['id']} ---")
        for k, v in d.items():
            print(f"  {k}: {v}")
        print()

    # Also: Tier-B file exemption detail
    print("=" * 80)
    print("TIER-B FILE EXEMPTIONS (top-4 files by plan)")
    print("=" * 80)
    targets = [
        "tools/eval/retrieval_benchmark.py",
        "ops_scripts/dev_tools/L0_routing_scripts/_ssot_meta_learning.py",
        "agentic_core/L5_safety/reasoning/LocationHealerAgent.py",
        "agentic_core/L2_execution/utils/write_gateway.py",
    ]
    for tgt in targets:
        print(f"\n--- {tgt} ---")
        rows = c.execute(
            "SELECT line_no, disposition, disposition_source, severity, "
            "violation_class, substr(evidence, 1, 120) "
            "FROM violations WHERE file_path = ? "
            "ORDER BY line_no",
            (tgt,),
        ).fetchall()
        if not rows:
            print("  (no rows — check path)")
        else:
            print(f"  count: {len(rows)}")
            for ln, disp, disp_src, sev, vc, ev in rows:
                print(
                    f"    line {ln:>4}  sev={sev:<6}  disp={disp or '-':<12}  "
                    f"src={disp_src or '-':<15} class={vc or '-':<10} ev={ev!r}"
                )

    # Exemption kind breakdown for Tier-B
    print("\n" + "=" * 80)
    print("TIER-B EXEMPTION KIND (from mv_exemptions_near_critical_paths)")
    print("=" * 80)
    for tgt in targets:
        rows = c.execute(
            "SELECT exemption_kind, line_no, criticality_score "
            "FROM mv_exemptions_near_critical_paths "
            "WHERE file = ? ORDER BY line_no",
            (tgt,),
        ).fetchall()
        print(f"\n{tgt}: {len(rows)} exemption rows")
        for kind, ln, sc in rows[:20]:
            print(f"  line {ln:>4}  {kind:<28} score={sc}")

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
