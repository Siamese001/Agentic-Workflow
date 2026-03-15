"""Measure P0 Deterministic Core edge counts from latest ADG SQLite."""
import glob
import os
import sqlite3

ADG_DIR = os.path.join(os.path.dirname(__file__), "..", "artifacts", "adg")

# Find latest sqlite
pattern = os.path.join(ADG_DIR, "adg_indexed_*.sqlite")
files = sorted(glob.glob(pattern))
if not files:
    print("No ADG sqlite found!")
    raise SystemExit(1)

db_path = files[-1]
print(f"Using: {os.path.basename(db_path)}")

db = sqlite3.connect(db_path)
cur = db.cursor()

# Get all edge types and counts
cur.execute("SELECT relation_type, COUNT(*) FROM edges GROUP BY relation_type ORDER BY COUNT(*) DESC")
edge_counts = dict(cur.fetchall())

# P0 edge types
P0_EDGES = [
    "records_execution_trace",
    "signs_execution_trace",
    "applies_guardrail",
    "validated_by_safety_plane",
    "verifies_boundary",
    "agent_executes_agent",
    "writes_through",
    "snapshots_state",
    "observes_runtime_state",
    "verifies_policy",
    "gated_by_confidence",
    "hard_fails_untranscripted",
    "transcripts_response",
    "emits_replay_key",
    "emits_determinism_digest",
]

print("\n=== P0 DETERMINISTIC CORE - Edge Counts ===")
total_p0 = 0
for e in P0_EDGES:
    count = edge_counts.get(e, 0)
    total_p0 += count
    print(f"  {e:<35} {count:>6}")

print(f"  {'─' * 35} {'─' * 6}")
print(f"  {'TOTAL P0 EDGES':<35} {total_p0:>6}")

total_all = sum(edge_counts.values())
print(f"  {'TOTAL ALL EDGES':<35} {total_all:>6}")
print(f"  P0 share of total: {total_p0 / total_all * 100:.1f}%")

# Modules with P0 edges
placeholders = ",".join("?" * len(P0_EDGES))
cur.execute(
    f"SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type IN ({placeholders})",
    P0_EDGES,
)
p0_modules = cur.fetchone()[0]

cur.execute("SELECT COUNT(DISTINCT source_file) FROM edges")
total_modules = cur.fetchone()[0]
print(f"  Modules with P0 edges: {p0_modules}/{total_modules} ({p0_modules / total_modules * 100:.1f}%)")

# Per-layer P0 coverage
print("\n=== P0 Coverage by Layer ===")
for layer in ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]:
    cur.execute(
        f"""SELECT COUNT(DISTINCT source_file) FROM edges
            WHERE relation_type IN ({placeholders}) AND source_file LIKE ?""",
        P0_EDGES + [f"%{layer}_%"],
    )
    layer_p0 = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(DISTINCT source_file) FROM edges WHERE source_file LIKE ?",
        (f"%{layer}_%",),
    )
    layer_total = cur.fetchone()[0]

    pct = (layer_p0 / layer_total * 100) if layer_total else 0
    print(f"  {layer}: {layer_p0}/{layer_total} modules ({pct:.1f}%)")

db.close()
