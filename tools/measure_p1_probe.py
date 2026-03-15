"""Probe P1 edge type candidates against user-reported P1 numbers."""

import sqlite3
from pathlib import Path

ADG_DIR = Path(__file__).resolve().parent.parent / "artifacts" / "adg"
files = sorted(ADG_DIR.glob("adg_indexed_*.sqlite"))
if not files:
    print("No ADG sqlite found!")
    raise SystemExit(1)

db_path = files[-1]
print(f"Using: {db_path.name}")

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

# Candidate P1 edge types by dimension
P1_DIMS = {
    "Evidence": [
        "reads_policy_state",
        "reads_governed_config",
        "reads_config",
        "reads_env",
        "reads_runtime_state",
    ],
    "Governance": [
        "validated_by_llm_gateway",
        "validated_by_registry",
        "escalates_to_human",
        "requires_human_review",
        "references_policy_hash",
        "validates_config_schema",
    ],
    "Trace": [
        "routes_through",
        "routes_path",
        "execution_terminates_at_uwg",
        "stamps_work_contract",
        "proposal_commits_routing",
    ],
    "Runtime": [
        "orchestrates_healing",
        "dispatches_healing_run",
        "enters_sandbox",
        "guards_replay",
        "intercepts_io",
        "reenters_safety",
        "certifies_envelope",
    ],
}

# User-reported P1 targets for validation
USER_P1 = {
    "L0": {"Evidence": 26, "Governance": 19, "Trace": 10, "Runtime": 7, "pct": 62},
    "L1": {"Evidence": 18, "Governance": 11, "Trace": 9, "Runtime": 6, "pct": 44},
    "L2": {"Evidence": 20, "Governance": 15, "Trace": 9, "Runtime": 6, "pct": 50},
    "L3": {"Evidence": 12, "Governance": 8, "Trace": 8, "Runtime": 5, "pct": 33},
    "L4": {"Evidence": 14, "Governance": 9, "Trace": 8, "Runtime": 5, "pct": 36},
    "L5": {"Evidence": 25, "Governance": 19, "Trace": 10, "Runtime": 7, "pct": 61},
    "L6": {"Evidence": 19, "Governance": 12, "Trace": 10, "Runtime": 6, "pct": 47},
}

print()
header = f"{'Layer':<6}"
for dim in P1_DIMS:
    header += f" {dim:>12}"
header += f" {'Total':>8} {'%Comp':>8}"
print(header)
print("-" * 70)

for layer, path_prefix in LAYER_MAP.items():
    cur.execute(
        "SELECT COUNT(DISTINCT source_file) FROM edges WHERE source_file LIKE ?",
        (f"agentic_core/{path_prefix}/%",),
    )
    total = cur.fetchone()[0]

    line = f"{layer:<6}"
    vals = []
    for dim_name, edge_types in P1_DIMS.items():
        ph = ",".join("?" * len(edge_types))
        cur.execute(
            f"SELECT COUNT(DISTINCT source_file) FROM edges "
            f"WHERE relation_type IN ({ph}) AND source_file LIKE ?",
            edge_types + [f"agentic_core/{path_prefix}/%"],
        )
        cnt = cur.fetchone()[0]
        pct = 100 * cnt / total if total else 0
        vals.append(pct)
        user_val = USER_P1.get(layer, {}).get(dim_name, "?")
        line += f" {pct:>5.0f}%({user_val})"

    avg = sum(vals) / len(vals) if vals else 0
    user_pct = USER_P1.get(layer, {}).get("pct", "?")
    line += f" {avg:>7.0f}% ({user_pct}%)"
    print(line)
    print(f"       total_files={total}")

conn.close()
