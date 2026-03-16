"""P0 Runtime Baseline — query the ADG SQLite for P0 edge counts and coverage."""

import json
import sqlite3
import time
from pathlib import Path

ADG_DIR = Path(__file__).resolve().parent.parent / "artifacts" / "adg"
REPORTS_DIR = Path(__file__).resolve().parent.parent / "docs" / "reports"

# Find latest ADG SQLite
sqlite_files = sorted(ADG_DIR.glob("adg_indexed_*.sqlite"))
if not sqlite_files:
    print("ERROR: No ADG SQLite found in", ADG_DIR)
    raise SystemExit(1)

DB_PATH = sqlite_files[-1]
print(f"Using ADG: {DB_PATH.name}")

conn = sqlite3.connect(str(DB_PATH))
cur = conn.cursor()

# ── Discover schema ──────────────────────────────────────────────────────────
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
print(f"Tables: {tables}")

# Find the edges table (might be named differently)
edges_table = None
for t in tables:
    if "edge" in t.lower():
        edges_table = t
        break

if not edges_table:
    print("ERROR: No edges table found. Tables:", tables)
    # Try to find columns in all tables
    for t in tables:
        cur.execute(f"PRAGMA table_info({t})")
        cols = [c[1] for c in cur.fetchall()]
        print(f"  {t}: {cols}")
    conn.close()
    raise SystemExit(1)

print(f"Edges table: {edges_table}")
cur.execute(f"PRAGMA table_info({edges_table})")
cols = [c[1] for c in cur.fetchall()]
print(f"Columns: {cols}")

# Find the relation type column
rel_col = None
for c in cols:
    if "relation" in c.lower() or "edge_kind" in c.lower() or "type" in c.lower():
        rel_col = c
        break

if not rel_col:
    print("ERROR: No relation type column found. Columns:", cols)
    conn.close()
    raise SystemExit(1)

print(f"Relation column: {rel_col}")

# Find source file column
src_col = None
for c in cols:
    if "source" in c.lower() and "file" in c.lower():
        src_col = c
        break
if not src_col:
    for c in cols:
        if "from" in c.lower() or "source" in c.lower() or "caller" in c.lower():
            src_col = c
            break

print(f"Source column: {src_col}")

# ── Sample relation types to understand the data ─────────────────────────────
cur.execute(f"SELECT DISTINCT {rel_col} FROM {edges_table} ORDER BY {rel_col}")
all_relations = [r[0] for r in cur.fetchall()]
print(f"\nTotal distinct relation types: {len(all_relations)}")

# ── P0 Baseline Queries ─────────────────────────────────────────────────────
P0_RELATIONS = [
    "calls",
    "records_execution_trace",
    "applies_guardrail",
    "reads_policy_state",
    "reads_runtime_state",
    "snapshots_state",
    "invokes_eval",
    "emits_replay_key",
    "emits_determinism_digest",
    "signs_execution_trace",
]

# Also check for closely named variants
p0_related = []
for rel in all_relations:
    for p0 in P0_RELATIONS:
        if p0 in rel or rel in p0:
            if rel not in P0_RELATIONS:
                p0_related.append(rel)
                break

if p0_related:
    print(f"\nRelated relation types found: {p0_related}")

results = {}
print(f"\n{'='*60}")
print("P0 BASELINE QUERY RESULTS")
print(f"{'='*60}")

for rel in P0_RELATIONS:
    cur.execute(f"SELECT COUNT(*) FROM {edges_table} WHERE {rel_col} = ?", (rel,))
    count = cur.fetchone()[0]
    results[rel] = count
    print(f"  {rel:40s} = {count:>8,}")

# ── Per-relation, count distinct source modules ──────────────────────────────
print(f"\n{'='*60}")
print("DISTINCT SOURCE MODULES PER RELATION")
print(f"{'='*60}")

module_counts = {}
if src_col:
    for rel in P0_RELATIONS:
        cur.execute(
            f"SELECT COUNT(DISTINCT {src_col}) FROM {edges_table} WHERE {rel_col} = ?",
            (rel,),
        )
        mc = cur.fetchone()[0]
        module_counts[rel] = mc
        print(f"  {rel:40s} = {mc:>8,} modules")

# ── Total modules in call graph ──────────────────────────────────────────────
if src_col:
    cur.execute(
        f"SELECT COUNT(DISTINCT {src_col}) FROM {edges_table} WHERE {rel_col} = 'calls'"
    )
    total_calling_modules = cur.fetchone()[0]

    cur.execute(f"SELECT COUNT(DISTINCT {src_col}) FROM {edges_table}")
    total_modules = cur.fetchone()[0]
    print(f"\n  Total modules with 'calls' edges: {total_calling_modules:,}")
    print(f"  Total modules with any edges:     {total_modules:,}")

# ── Coverage percentages ─────────────────────────────────────────────────────
print(f"\n{'='*60}")
print("P0 COVERAGE (modules with relation / modules with calls)")
print(f"{'='*60}")

coverage = {}
if src_col and total_calling_modules > 0:
    for rel in P0_RELATIONS:
        if rel == "calls":
            continue
        mc = module_counts.get(rel, 0)
        pct = (mc / total_calling_modules) * 100
        coverage[rel] = pct
        bar = "#" * int(pct / 2) + "." * (50 - int(pct / 2))
        print(f"  {rel:40s} {pct:6.1f}%  [{bar}]")

# ── Observes_runtime_state (alternative for reads_runtime_state) ─────────────
alt_runtime = "observes_runtime_state"
cur.execute(f"SELECT COUNT(*) FROM {edges_table} WHERE {rel_col} = ?", (alt_runtime,))
alt_count = cur.fetchone()[0]
if alt_count > 0:
    results[alt_runtime] = alt_count
    print(f"\n  NOTE: '{alt_runtime}' has {alt_count:,} edges (alternative to reads_runtime_state)")
    if src_col:
        cur.execute(
            f"SELECT COUNT(DISTINCT {src_col}) FROM {edges_table} WHERE {rel_col} = ?",
            (alt_runtime,),
        )
        alt_mc = cur.fetchone()[0]
        module_counts[alt_runtime] = alt_mc
        alt_pct = (alt_mc / total_calling_modules) * 100 if total_calling_modules > 0 else 0
        coverage[alt_runtime] = alt_pct
        print(f"  {alt_runtime:40s} {alt_pct:6.1f}%  ({alt_mc:,} modules)")

# ── Additional P0-adjacent relations ─────────────────────────────────────────
additional = [
    "validated_by_safety_plane",
    "verifies_boundary",
    "writes_through",
    "gated_by_confidence",
    "transcripts_response",
    "hard_fails_untranscripted",
    "observes_policy_state",
]
print(f"\n{'='*60}")
print("ADDITIONAL P0-ADJACENT RELATIONS")
print(f"{'='*60}")
for rel in additional:
    cur.execute(f"SELECT COUNT(*) FROM {edges_table} WHERE {rel_col} = ?", (rel,))
    count = cur.fetchone()[0]
    if count > 0:
        results[rel] = count
        print(f"  {rel:40s} = {count:>8,}")
        if src_col:
            cur.execute(
                f"SELECT COUNT(DISTINCT {src_col}) FROM {edges_table} WHERE {rel_col} = ?",
                (rel,),
            )
            mc = cur.fetchone()[0]
            module_counts[rel] = mc

# ── Dump all relation types with counts ──────────────────────────────────────
print(f"\n{'='*60}")
print("ALL RELATION TYPES (sorted by count desc)")
print(f"{'='*60}")
cur.execute(
    f"SELECT {rel_col}, COUNT(*) as cnt FROM {edges_table} GROUP BY {rel_col} ORDER BY cnt DESC"
)
for row in cur.fetchall():
    print(f"  {row[0]:50s} {row[1]:>8,}")

conn.close()

# ── Write results to JSON for downstream use ─────────────────────────────────
output = {
    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
    "adg_file": DB_PATH.name,
    "edge_counts": results,
    "module_counts": module_counts,
    "coverage_pct": coverage,
    "total_calling_modules": total_calling_modules if src_col else 0,
    "total_modules": total_modules if src_col else 0,
}

json_path = REPORTS_DIR / "p0_runtime_baseline.json"
json_path.parent.mkdir(parents=True, exist_ok=True)
json_path.write_text(json.dumps(output, indent=2))
print(f"\nJSON saved: {json_path}")
