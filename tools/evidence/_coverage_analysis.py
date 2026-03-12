"""ADG coverage analysis — source modules vs GT_covers edges."""
import sqlite3
import json
from pathlib import Path

DB = Path(__file__).parent.parent.parent / "artifacts" / "adg" / "adg_indexed_03122026.sqlite"
OUT = Path(__file__).parent / "coverage_gaps.json"

db = sqlite3.connect(DB)
db.row_factory = sqlite3.Row
cur = db.cursor()


def layer_from_path(path: str) -> str:
    p = path.replace("ADG::Module::", "")
    for prefix, label in [
        ("agentic_core/L0", "L0"),
        ("agentic_core/L1", "L1"),
        ("agentic_core/L2", "L2"),
        ("agentic_core/L3", "L3"),
        ("agentic_core/L4", "L4"),
        ("agentic_core/L5", "L5"),
        ("agentic_core/L6", "L6"),
        ("apps_rg", "L_APP_RG"),
        ("apps_shared", "L_SHARED"),
        ("system_learning", "L_SL"),
        ("agentic_core/runtime", "L_RUNTIME"),
        ("agentic_core/enforcement", "L_ENF"),
        ("agentic_core/utils", "L_UTILS"),
        ("agentic_core/types", "L_TYPES"),
        ("agentic_core/adg", "L_ADG"),
    ]:
        if p.startswith(prefix):
            return label
    return "OTHER"


# ── 1. Total source modules (excluding tests/tools/ops) ──────────────────────
cur.execute("""
    SELECT COUNT(*) FROM nodes
    WHERE entity_type='module'
      AND adg_name NOT LIKE '%tests/%'
      AND adg_name NOT LIKE '%tools/%'
      AND adg_name NOT LIKE '%ops_scripts%'
      AND adg_name NOT LIKE '%__pycache__%'
""")
total_src = cur.fetchone()[0]

# ── 2. Covered modules (have at least one GT_covers edge inbound) ─────────────
cur.execute("SELECT COUNT(DISTINCT dst_id) FROM edges WHERE relation_type='covers'")
covered = cur.fetchone()[0]

# ── 3. Uncovered modules ──────────────────────────────────────────────────────
cur.execute("""
    SELECT adg_name FROM nodes
    WHERE entity_type='module'
      AND adg_name NOT LIKE '%tests/%'
      AND adg_name NOT LIKE '%tools/%'
      AND adg_name NOT LIKE '%ops_scripts%'
      AND adg_name NOT LIKE '%__pycache__%'
      AND id NOT IN (SELECT dst_id FROM edges WHERE relation_type='covers')
    ORDER BY adg_name
""")
gap_rows = [(layer_from_path(r["adg_name"]), r["adg_name"]) for r in cur]
uncovered = len(gap_rows)

print("=== COVERAGE OVERVIEW ===")
print(f"  Source modules total:   {total_src}")
print(f"  Covered by ADG tests:   {covered}")
print(f"  Uncovered (gap):        {uncovered}")
print(f"  Coverage %:             {100 * covered / max(total_src, 1):.1f}%")

gaps_by_layer: dict[str, int] = {}
for lyr, _ in gap_rows:
    gaps_by_layer[lyr] = gaps_by_layer.get(lyr, 0) + 1

print("\n=== UNCOVERED MODULES BY LAYER ===")
for k, v in sorted(gaps_by_layer.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")

# ── 4. Also query: what test files currently exist ────────────────────────────
cur.execute("""
    SELECT COUNT(*) FROM nodes
    WHERE entity_type='module' AND adg_name LIKE '%tests/%'
""")
test_modules = cur.fetchone()[0]
print(f"\n  Test modules in ADG: {test_modules}")

# ── 5. Coverage by layer breakdown ───────────────────────────────────────────
print("\n=== COVERAGE BY LAYER (covered vs total) ===")
cur.execute("""
    SELECT n.adg_name FROM nodes n
    WHERE n.entity_type='module'
      AND n.adg_name NOT LIKE '%tests/%'
      AND n.adg_name NOT LIKE '%tools/%'
      AND n.adg_name NOT LIKE '%ops_scripts%'
      AND n.adg_name NOT LIKE '%__pycache__%'
""")
all_src = [(layer_from_path(r["adg_name"]), r["adg_name"]) for r in cur]
by_layer_total: dict[str, int] = {}
for lyr, _ in all_src:
    by_layer_total[lyr] = by_layer_total.get(lyr, 0) + 1

for lyr in sorted(by_layer_total):
    tot = by_layer_total[lyr]
    gap = gaps_by_layer.get(lyr, 0)
    cov = tot - gap
    pct = 100 * cov / max(tot, 1)
    print(f"  {lyr:<15} {cov:>4}/{tot:<4}  {pct:5.1f}%  gap={gap}")

# ── 6. Sample uncovered per layer (top 10 per layer for gap impl) ─────────────
print("\n=== UNCOVERED SAMPLES (first 10 per layer) ===")
by_layer_gaps: dict[str, list[str]] = {}
for lyr, nm in gap_rows:
    by_layer_gaps.setdefault(lyr, []).append(nm)

for lyr in sorted(by_layer_gaps):
    items = by_layer_gaps[lyr]
    print(f"\n  [{lyr}] {len(items)} uncovered:")
    for nm in items[:10]:
        short = nm.replace("ADG::Module::", "")
        print(f"    {short}")
    if len(items) > 10:
        print(f"    ... and {len(items) - 10} more")

# ── 7. Save gap list ──────────────────────────────────────────────────────────
OUT.write_text(json.dumps(gap_rows, indent=2))
print(f"\nGap list saved → {OUT}  ({len(gap_rows)} entries)")

db.close()
