"""Measure P0 Deterministic Core completion by layer × dimension."""

import glob
import os
import sqlite3

ADG_DIR = os.path.join(os.path.dirname(__file__), "..", "artifacts", "adg")
pattern = os.path.join(ADG_DIR, "adg_indexed_*.sqlite")
files = sorted(glob.glob(pattern))
if not files:
    print("No ADG sqlite found!")
    raise SystemExit(1)

db_path = files[-1]
print(f"Using: {os.path.basename(db_path)}")

conn = sqlite3.connect(db_path)
cur = conn.cursor()

LAYER_MAP = {
    "L0": "L0_routing",
    "L1": "L1_cognition",
    "L2": "L2_execution",
    "L3": "L3_orchestration",
    "L4": "L4_state",
    "L5": "L5_safety",
    "L6": "L6_observability",
}

DIMS = {
    "Evidence": [
        "records_execution_trace",
        "emits_replay_key",
        "emits_determinism_digest",
    ],
    "Governance": [
        "applies_guardrail",
        "verifies_policy",
        "validated_by_safety_plane",
        "verifies_boundary",
    ],
    "Trace": [
        "signs_execution_trace",
        "transcripts_response",
        "hard_fails_untranscripted",
    ],
    "Runtime": [
        "snapshots_state",
        "observes_runtime_state",
        "writes_through",
        "agent_executes_agent",
        "gated_by_confidence",
    ],
}

ALL_P0 = []
for v in DIMS.values():
    ALL_P0.extend(v)

# Header
print(f"\n{'Layer':<6} {'Evidence':>10} {'Governance':>12} {'Trace':>10} {'Runtime':>10} {'Avg':>8}")
print("-" * 60)

layer_avgs = []
for layer, path_prefix in LAYER_MAP.items():
    # Total modules in this layer
    cur.execute(
        "SELECT COUNT(DISTINCT source_file) FROM edges WHERE source_file LIKE ?",
        (f"agentic_core/{path_prefix}/%",),
    )
    layer_total = cur.fetchone()[0]
    if layer_total == 0:
        continue

    dim_pcts = []
    for dim_name, edge_types in DIMS.items():
        ph = ",".join("?" * len(edge_types))
        cur.execute(
            f"""SELECT COUNT(DISTINCT source_file) FROM edges
                WHERE relation_type IN ({ph}) AND source_file LIKE ?""",
            edge_types + [f"agentic_core/{path_prefix}/%"],
        )
        dim_modules = cur.fetchone()[0]
        pct = 100 * dim_modules / layer_total
        dim_pcts.append(pct)

    avg = sum(dim_pcts) / len(dim_pcts)
    layer_avgs.append(avg)
    print(
        f"{layer:<6} {dim_pcts[0]:>9.0f}% {dim_pcts[1]:>11.0f}% {dim_pcts[2]:>9.0f}% {dim_pcts[3]:>9.0f}% {avg:>7.0f}%"
    )

p0_overall = sum(layer_avgs) / len(layer_avgs) if layer_avgs else 0
print("-" * 60)
print(f"{'P0 AVG':<6} {'':>44} {p0_overall:>7.0f}%")

# Also show total P0 edge counts
print("\n=== P0 Edge Totals ===")
for e in sorted(ALL_P0):
    cur.execute("SELECT COUNT(*) FROM edges WHERE relation_type = ?", (e,))
    c = cur.fetchone()[0]
    print(f"  {e:<35} {c:>6}")

cur.execute("SELECT COUNT(*) FROM edges")
total = cur.fetchone()[0]
ph = ",".join("?" * len(ALL_P0))
cur.execute(f"SELECT COUNT(*) FROM edges WHERE relation_type IN ({ph})", ALL_P0)
p0_total = cur.fetchone()[0]
print(f"  {'TOTAL P0':.<35} {p0_total:>6} / {total} ({100 * p0_total / total:.1f}%)")

conn.close()
