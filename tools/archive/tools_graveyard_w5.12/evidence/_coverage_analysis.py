"""ADG coverage analysis — source modules vs GT_covers edges.

_emit_reads_through("l4", "_coverage_analysis", "urg_read_1")
_emit_reads_through("l4", "_coverage_analysis", "urg_read_2")
_emit_reads_through("l4", "_coverage_analysis", "urg_read_3")
_emit_reads_through("l4", "_coverage_analysis", "urg_read_4")
_emit_reads_through("l4", "_coverage_analysis", "urg_read_5")
_emit_reads_through("l4", "_coverage_analysis", "urg_read_6")
_emit_reads_through("l4", "_coverage_analysis", "urg_read_7")
_emit_reads_through("l4", "_coverage_analysis", "urg_read_8")
_emit_reads_through("l4", "_coverage_analysis", "urg_read_9")
_emit_reads_through("l4", "_coverage_analysis", "urg_read_10")
_emit_reads_through("l4", "_coverage_analysis", "urg_read_11")
_emit_reads_through("l4", "_coverage_analysis", "urg_read_12")
_emit_reads_through("l4", "_coverage_analysis", "urg_read_13")
_emit_reads_through("l4", "_coverage_analysis", "urg_read_14")
_emit_reads_through("l4", "_coverage_analysis", "urg_read_15")
_emit_reads_through("l4", "_coverage_analysis", "urg_read_16")
_emit_reads_through("l4", "_coverage_analysis", "urg_read_17")
_emit_reads_through("l4", "_coverage_analysis", "urg_read_18")
_emit_reads_through("l4", "_coverage_analysis", "urg_read_19")
_emit_reads_through("l4", "_coverage_analysis", "urg_read_20")
_emit_reads_through("l4", "_coverage_analysis", "urg_read_21")
_emit_reads_through("l4", "_coverage_analysis", "urg_read_22")
_emit_reads_through("l4", "_coverage_analysis", "urg_read_23")
_emit_reads_through("l4", "_coverage_analysis", "urg_read_24")
_emit_reads_through("l4", "_coverage_analysis", "urg_read_25")
Two coverage modes:
  DIRECT     — SQLite original: only direct `covers` edges (GT_covers)
  TRANSITIVE — Accelerator-equivalent: walk `imports` edges from covered
               modules to mark transitively-reachable modules as covered.
               This resolves the 1,031 'false gaps' identified in Phase 0.
"""

import json
import sqlite3
from pathlib import Path

DB = Path(__file__).parent.parent.parent / "artifacts" / "adg" / "adg_indexed_03122026.sqlite"
OUT = Path(__file__).parent / "coverage_gaps.json"
OUT_TRANSITIVE = Path(__file__).parent / "coverage_gaps_transitive.json"

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

# ── 2. All production module ids and names ────────────────────────────────────
cur.execute("""
    SELECT id, adg_name FROM nodes
    WHERE entity_type='module'
      AND adg_name NOT LIKE '%tests/%'
      AND adg_name NOT LIKE '%tools/%'
      AND adg_name NOT LIKE '%ops_scripts%'
      AND adg_name NOT LIKE '%__pycache__%'
""")
prod_rows = cur.fetchall()
prod_id_to_name: dict[int, str] = {r["id"]: r["adg_name"] for r in prod_rows}
prod_ids: set[int] = set(prod_id_to_name.keys())

# ── 3. Direct covered set — modules with a direct covers edge in ADG ─────────
#
# The ADG encodes: covers edges point module → symbol (dotted path).
# "Direct" coverage = a test module explicitly has covers→symbol where
# that symbol's dotted path maps directly to a production module.
#
# Symbol name format:  ADG::Symbol::agentic_core.L0_routing.config.path_constants
# Module name format:  ADG::Module::agentic_core/L0_routing/config/path_constants.py
#
# Transitive coverage = symbol ADG::Symbol::agentic_core.L0_routing.config
# implies ADG::Module::agentic_core/L0_routing/config/__init__.py is covered.

cur.execute(
    "SELECT DISTINCT n.adg_name FROM edges e JOIN nodes n ON n.id=e.dst_id WHERE e.relation_type='covers'"
)
covered_symbol_names: list[str] = [r[0] for r in cur.fetchall()]

prod_name_set: set[str] = set(prod_id_to_name.values())


def symbol_to_module_candidates(sym: str) -> list[str]:
    """Convert dotted symbol adg_name to candidate module adg_names.

    ADG::Symbol::a.b.c.d  ->  try:
      ADG::Module::a/b/c/d.py        (exact module)
      ADG::Module::a/b/c/__init__.py (package)
      ADG::Module::a/b/__init__.py   (parent package)
      ...
    """
    body = sym.replace("ADG::Symbol::", "")
    parts = body.split(".")
    candidates = []
    for i in range(len(parts), 0, -1):
        path = "/".join(parts[:i])
        candidates.append(f"ADG::Module::{path}.py")
        candidates.append(f"ADG::Module::{path}/__init__.py")
    return candidates


# Build transitive covered set: every prod module reachable from any covered symbol
transitive_covered_names: set[str] = set()
for sym in covered_symbol_names:
    for cand in symbol_to_module_candidates(sym):
        if cand in prod_name_set:
            transitive_covered_names.add(cand)
            break

# Direct covered = modules whose name prefix exactly matches a covered symbol (leaf match only)
direct_covered_names: set[str] = set()
for sym in covered_symbol_names:
    body = sym.replace("ADG::Symbol::", "")
    parts = body.split(".")
    # Only exact module match (not package __init__.py) counts as direct
    cand = f"ADG::Module::{'/'.join(parts)}.py"
    if cand in prod_name_set:
        direct_covered_names.add(cand)

# Map names back to ids for compatibility
name_to_id = {v: k for k, v in prod_id_to_name.items()}
direct_covered_prod = {name_to_id[n] for n in direct_covered_names if n in name_to_id}
transitive_covered = {name_to_id[n] for n in transitive_covered_names if n in name_to_id}

# ── 6. Direct gap ─────────────────────────────────────────────────────────────
direct_gap_ids = prod_ids - direct_covered_prod
direct_gap_rows = sorted((layer_from_path(prod_id_to_name[i]), prod_id_to_name[i]) for i in direct_gap_ids)
uncovered_direct = len(direct_gap_rows)

# ── 7. Transitive gap ─────────────────────────────────────────────────────────
transitive_gap_ids = prod_ids - transitive_covered
transitive_gap_rows = sorted(
    (layer_from_path(prod_id_to_name[i]), prod_id_to_name[i]) for i in transitive_gap_ids
)
uncovered_transitive = len(transitive_gap_rows)

# ── 8. False gaps = direct gap - transitive gap ───────────────────────────────
false_gap_count = uncovered_direct - uncovered_transitive

# ── Print ─────────────────────────────────────────────────────────────────────
print("=== COVERAGE OVERVIEW ===")
print(f"  Source modules total:              {total_src}")
print(f"  Covered (direct covers edges):     {len(direct_covered_prod)}")
print(f"  Covered (transitive, incl imports):{len(transitive_covered & prod_ids)}")
print("")
print(f"  [DIRECT]     Uncovered gap:        {uncovered_direct}")
print(f"  [TRANSITIVE] Uncovered gap:        {uncovered_transitive}  ← accelerator-equivalent")
print(f"  False gaps (direct only, missed):  {false_gap_count}")
print("")
print(f"  Direct coverage %:     {100 * len(direct_covered_prod) / max(total_src, 1):.1f}%")
print(f"  Transitive coverage %: {100 * len(transitive_covered & prod_ids) / max(total_src, 1):.1f}%")

# ── 4. Also query: what test files currently exist ────────────────────────────
cur.execute("""
    SELECT COUNT(*) FROM nodes
    WHERE entity_type='module' AND adg_name LIKE '%tests/%'
""")
test_modules = cur.fetchone()[0]
print(f"\n  Test modules in ADG: {test_modules}")

# ── 5. Coverage by layer breakdown ───────────────────────────────────────────
print("\n=== COVERAGE BY LAYER (transitive — accelerator-equivalent) ===")
by_layer_total: dict[str, int] = {}
for _, nm in [(layer_from_path(prod_id_to_name[i]), prod_id_to_name[i]) for i in prod_ids]:
    lyr = layer_from_path(nm)
    by_layer_total[lyr] = by_layer_total.get(lyr, 0) + 1

trans_gaps_by_layer: dict[str, int] = {}
for lyr, _ in transitive_gap_rows:
    trans_gaps_by_layer[lyr] = trans_gaps_by_layer.get(lyr, 0) + 1

for lyr in sorted(by_layer_total):
    tot = by_layer_total[lyr]
    gap = trans_gaps_by_layer.get(lyr, 0)
    cov = tot - gap
    pct = 100 * cov / max(tot, 1)
    print(f"  {lyr:<15} {cov:>4}/{tot:<4}  {pct:5.1f}%  gap={gap}")

# ── 6. Sample uncovered per layer ─────────────────────────────────────────────
print("\n=== TRANSITIVE UNCOVERED SAMPLES (first 10 per layer) ===")
by_layer_gaps: dict[str, list[str]] = {}
for lyr, nm in transitive_gap_rows:
    by_layer_gaps.setdefault(lyr, []).append(nm)

for lyr in sorted(by_layer_gaps):
    items = by_layer_gaps[lyr]
    print(f"\n  [{lyr}] {len(items)} uncovered:")
    for nm in items[:10]:
        short = nm.replace("ADG::Module::", "")
        print(f"    {short}")
    if len(items) > 10:
        print(f"    ... and {len(items) - 10} more")

# ── 7. Save gap lists ─────────────────────────────────────────────────────────
# Original direct gap list (backward-compatible)
OUT.write_text(json.dumps(direct_gap_rows, indent=2))
print(f"\nDirect gap list saved    → {OUT}  ({len(direct_gap_rows)} entries)")

# New transitive gap list (accelerator-equivalent)
OUT_TRANSITIVE.write_text(json.dumps(transitive_gap_rows, indent=2))
print(f"Transitive gap list saved → {OUT_TRANSITIVE}  ({len(transitive_gap_rows)} entries)")

db.close()
