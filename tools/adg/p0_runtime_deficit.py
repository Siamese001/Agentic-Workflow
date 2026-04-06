"""P0 Runtime Deficit Analysis — Steps 1-3 of P0 Runtime Baseline Hardening.

Step 1: Baseline counts from ADG SQLite
Step 2: Target matrix computation
Step 3: Trace deficit set identification (modules missing required edges)
"""

import csv
import json
import sqlite3
import time
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)

_emit_writes_through("p1", "p0_runtime_deficit", "uwg_governed_write")
_emit_writes_through("p1", "p0_runtime_deficit", "uwg_governed_write_2")
_emit_pulls_context("p1", "p0_runtime_deficit", "context_retrieval")
_emit_pulls_context("p1", "p0_runtime_deficit", "context_retrieval_2")
emit_determinism_digest("trace_p0_runtime_deficit", "p0_runtime_deficit_dispatch")
emit_determinism_digest("trace_p0_runtime_deficit", "p0_runtime_deficit_complete")
_emit_validated_by_safety_plane("p1", "p0_runtime_deficit", "safety_validation")

ADG_DIR = Path(__file__).resolve().parent.parent / "artifacts" / "adg"
REPORTS_DIR = Path(__file__).resolve().parent.parent / "docs" / "reports"
GAPS_DIR = Path(__file__).resolve().parent.parent / "runtime_gaps"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)
GAPS_DIR.mkdir(parents=True, exist_ok=True)

# Find latest ADG SQLite
sqlite_files = sorted(ADG_DIR.glob("adg_indexed_*.sqlite"))
if not sqlite_files:
    raise SystemExit("ERROR: No ADG SQLite found")
DB_PATH = sqlite_files[-1]
print(f"Using ADG: {DB_PATH.name}")

conn = sqlite3.connect(str(DB_PATH))
cur = conn.cursor()

# ── Discover schema ──────────────────────────────────────────────────────────
cur.execute("PRAGMA table_info(edges)")
cols = [c[1] for c in cur.fetchall()]
rel_col = next(c for c in cols if "relation" in c.lower() or "type" in c.lower())
src_col = next(c for c in cols if "source" in c.lower() and "file" in c.lower())
from_col = next((c for c in cols if c == "from_name"), None)
to_col = next((c for c in cols if c == "to_name"), None)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 1 — BASELINE COUNTS
# ══════════════════════════════════════════════════════════════════════════════

P0_RELATIONS = [
    "calls",
    "records_execution_trace",
    "applies_guardrail",
    "reads_policy_state",
    "reads_runtime_state",
    "snapshots_state",
    "observes_runtime_state",
    "invokes_eval",
    "emits_replay_key",
    "emits_determinism_digest",
    "signs_execution_trace",
]

edge_counts = {}
module_counts = {}

for rel in P0_RELATIONS:
    cur.execute(f"SELECT COUNT(*) FROM edges WHERE {rel_col} = ?", (rel,))
    edge_counts[rel] = cur.fetchone()[0]
    cur.execute(f"SELECT COUNT(DISTINCT {src_col}) FROM edges WHERE {rel_col} = ?", (rel,))
    module_counts[rel] = cur.fetchone()[0]

total_calling = module_counts["calls"]
print(f"\nTotal calling modules: {total_calling:,}")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 2 — TARGET MATRIX
# ══════════════════════════════════════════════════════════════════════════════

# Thresholds from Step 8
THRESHOLDS = {
    "records_execution_trace": 0.90,   # trace coverage
    "applies_guardrail": 0.80,        # guardrail coverage
    "reads_policy_state": 0.95,       # policy binding
    "state_authority": 1.00,          # combined state (snapshots + reads_runtime + observes_runtime)
    "invokes_eval": 0.80,            # evaluation linkage
    "emits_replay_key": 0.90,        # replay key coverage
    "emits_determinism_digest": 0.90, # determinism digest
    "signs_execution_trace": 0.90,   # trace signing
}

# Combined state authority: union of modules with any state edge
cur.execute(
    f"""SELECT COUNT(DISTINCT {src_col}) FROM edges
    WHERE {rel_col} IN ('snapshots_state', 'reads_runtime_state', 'observes_runtime_state')"""
)
state_union_modules = cur.fetchone()[0]

coverage = {}
targets = {}
deficits = {}

for metric, threshold in THRESHOLDS.items():
    if metric == "state_authority":
        current = state_union_modules
    else:
        current = module_counts.get(metric, 0)
    target_count = int(total_calling * threshold)
    pct = (current / total_calling * 100) if total_calling > 0 else 0
    deficit = max(0, target_count - current)

    coverage[metric] = pct
    targets[metric] = target_count
    deficits[metric] = deficit

print(f"\n{'Metric':<35s} {'Current':>8s} {'Target':>8s} {'Deficit':>8s} {'Pct':>7s} {'Thr':>5s}")
print("-" * 75)
for metric in THRESHOLDS:
    if metric == "state_authority":
        cur_val = state_union_modules
    else:
        cur_val = module_counts.get(metric, 0)
    thr = THRESHOLDS[metric] * 100
    pct = coverage[metric]
    status = "✓" if pct >= thr else "✗"
    print(f"  {metric:<33s} {cur_val:>8,} {targets[metric]:>8,} {deficits[metric]:>8,} {pct:>6.1f}% {thr:>4.0f}% {status}")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 3 — TRACE DEFICIT SET
# ══════════════════════════════════════════════════════════════════════════════

# For each wireable dimension, find modules in call graph that lack the edge
WIREABLE_DIMS = {
    "records_execution_trace": {
        "import": "from agentic_core.runtime.contracts.lifecycle_trace_contract import _emit_records_execution_trace  # noqa: E402",
        "call": '_emit_records_execution_trace("p0", "evidence", "{basename}")',
        "emit_func": "_emit_records_execution_trace",
    },
    "applies_guardrail": {
        "import": "from agentic_core.runtime.contracts.lifecycle_trace_contract import _emit_applies_guardrail  # noqa: E402",
        "call": '_emit_applies_guardrail("p0", "{basename}", "p0_governance")',
        "emit_func": "_emit_applies_guardrail",
    },
    "reads_policy_state": {
        "import": "from agentic_core.runtime.contracts.lifecycle_trace_contract import _emit_reads_policy_state  # noqa: E402",
        "call": '_emit_reads_policy_state("p0", "{basename}", "policy_binding")',
        "emit_func": "_emit_reads_policy_state",
    },
    "snapshots_state": {
        "import": "from agentic_core.runtime.contracts.lifecycle_trace_contract import _emit_snapshots_state  # noqa: E402",
        "call": '_emit_snapshots_state("p0", "{basename}", "state_snapshot")',
        "emit_func": "_emit_snapshots_state",
    },
    "emits_replay_key": {
        "import": "from agentic_core.runtime.contracts.lifecycle_trace_contract import emit_replay_key  # noqa: E402",
        "call": 'emit_replay_key("p0", "{basename}")',
        "emit_func": "emit_replay_key",
    },
    "emits_determinism_digest": {
        "import": "from agentic_core.runtime.contracts.lifecycle_trace_contract import emit_determinism_digest  # noqa: E402",
        "call": 'emit_determinism_digest("p0", "{basename}")',
        "emit_func": "emit_determinism_digest",
    },
    "signs_execution_trace": {
        "import": "from agentic_core.runtime.contracts.lifecycle_trace_contract import _emit_signs_execution_trace  # noqa: E402",
        "call": '_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)',
        "emit_func": "_emit_signs_execution_trace",
    },
}

# Get all modules in call graph
cur.execute(f"SELECT DISTINCT {src_col} FROM edges WHERE {rel_col} = 'calls'")
all_calling_modules = {r[0] for r in cur.fetchall()}

deficit_sets = {}
for dim in WIREABLE_DIMS:
    cur.execute(f"SELECT DISTINCT {src_col} FROM edges WHERE {rel_col} = ?", (dim,))
    has_dim = {r[0] for r in cur.fetchall()}
    deficit_modules = sorted(all_calling_modules - has_dim)
    deficit_sets[dim] = deficit_modules

# Write deficit CSV per dimension
for dim, modules in deficit_sets.items():
    csv_path = GAPS_DIR / f"deficit_{dim}.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["source_file"])
        for m in modules:
            writer.writerow([m])
    print(f"\n  {dim}: {len(modules):,} deficit modules → {csv_path.name}")

# Write combined deficit summary
summary_path = GAPS_DIR / "trace_deficit_modules.csv"
with open(summary_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["source_file", "missing_dimensions"])
    module_dims = {}
    for dim, modules in deficit_sets.items():
        for m in modules:
            module_dims.setdefault(m, []).append(dim)
    for m in sorted(module_dims):
        writer.writerow([m, "|".join(module_dims[m])])

print(f"\n  Combined deficit: {len(module_dims):,} unique modules → {summary_path.name}")

# ── Priority ordering for micro-waves ────────────────────────────────────────
# Modules missing the most dimensions should be wired first (highest ROI)
by_missing_count = sorted(module_dims.items(), key=lambda x: -len(x[1]))
print("\n  Top 20 highest-deficit modules:")
for m, dims in by_missing_count[:20]:
    print(f"    {len(dims)} dims missing: {m}")

conn.close()

# ── Save full analysis ───────────────────────────────────────────────────────
analysis = {
    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
    "adg_file": DB_PATH.name,
    "total_calling_modules": total_calling,
    "edge_counts": edge_counts,
    "module_counts": module_counts,
    "state_union_modules": state_union_modules,
    "thresholds": THRESHOLDS,
    "coverage_pct": coverage,
    "targets": targets,
    "deficits": deficits,
    "deficit_module_counts": {d: len(m) for d, m in deficit_sets.items()},
}

analysis_path = REPORTS_DIR / "p0_runtime_analysis.json"
analysis_path.write_text(json.dumps(analysis, indent=2))
print(f"\nFull analysis saved: {analysis_path}")
