"""P0 Gap Analyzer: find modules lacking P0 edges per layer x dimension."""

import ast
import glob
import os
import sqlite3
from collections import defaultdict

ADG_DIR = os.path.join(os.path.dirname(__file__), "..", "artifacts", "adg")
pattern = os.path.join(ADG_DIR, "adg_indexed_*.sqlite")
files = sorted(glob.glob(pattern))
db_path = files[-1]
print(f"Using: {os.path.basename(db_path)}")

db = sqlite3.connect(db_path)
cur = db.cursor()

# P0 edge types grouped by scoring dimension
EVIDENCE_EDGES = ["records_execution_trace", "emits_replay_key", "emits_determinism_digest"]
GOVERNANCE_EDGES = ["applies_guardrail", "verifies_policy", "validated_by_safety_plane", "verifies_boundary"]
TRACE_EDGES = ["signs_execution_trace", "transcripts_response", "hard_fails_untranscripted"]
RUNTIME_EDGES = [
    "snapshots_state",
    "observes_runtime_state",
    "writes_through",
    "agent_executes_agent",
    "gated_by_confidence",
]

ALL_P0 = EVIDENCE_EDGES + GOVERNANCE_EDGES + TRACE_EDGES + RUNTIME_EDGES

LAYERS = ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]

# Get all source files with their edge types
cur.execute("SELECT DISTINCT source_file, relation_type FROM edges")
file_edges = defaultdict(set)
for sf, rt in cur.fetchall():
    file_edges[sf].add(rt)

# Get all known modules per layer
cur.execute("SELECT DISTINCT source_file FROM edges")
all_modules = {r[0] for r in cur.fetchall()}

# Also scan filesystem for .py files in each layer
PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..")
SCAN_DIRS = {
    "L0": "agentic_core/L0_routing",
    "L1": "agentic_core/L1_cognition",
    "L2": "agentic_core/L2_execution",
    "L3": "agentic_core/L3_orchestration",
    "L4": "agentic_core/L4_state",
    "L5": "agentic_core/L5_safety",
    "L6": "agentic_core/L6_observability",
}


def has_wirable_functions(filepath):
    """Check if file has functions with body >= 3 lines."""
    try:
        src = open(filepath, encoding="utf-8", errors="replace").read()
        tree = ast.parse(src)
    # guardian: allow-silent-swallow - acceptable exception handling
    except (SyntaxError, OSError):
        return False
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            body_lines = (node.end_lineno or node.lineno) - node.lineno
            if body_lines >= 3 and not (
                node.name.startswith("__") and node.name not in ("__init__", "__call__")
            ):
                return True
    return False


def has_emit(filepath, emit_func):
    """Check if file already contains the emit function call."""
    try:
        src = open(filepath, encoding="utf-8", errors="replace").read()
        # guardian: allow-silent-swallow - acceptable exception handling
        return emit_func in src
    except OSError:
        return True  # Skip unreadable


print("\n" + "=" * 80)
print("P0 GAP ANALYSIS BY LAYER x DIMENSION")
print("=" * 80)

layer_gaps = {}

for layer in LAYERS:
    scan_dir = os.path.join(PROJECT_ROOT, SCAN_DIRS[layer])
    if not os.path.isdir(scan_dir):
        continue

    # Collect all .py files in this layer
    layer_files = []
    for root, dirs, fns in os.walk(scan_dir):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for fn in sorted(fns):
            if fn.endswith(".py") and fn != "__init__.py":
                fp = os.path.join(root, fn)
                rel = os.path.relpath(fp, PROJECT_ROOT).replace("\\", "/")
                layer_files.append(rel)

    total = len(layer_files)

    # Files with each dimension's edges
    has_evidence = set()
    has_governance = set()
    has_trace = set()
    has_runtime = set()
    has_any_p0 = set()

    for f in layer_files:
        edges = file_edges.get(f, set())
        if edges & set(EVIDENCE_EDGES):
            has_evidence.add(f)
        if edges & set(GOVERNANCE_EDGES):
            has_governance.add(f)
        if edges & set(TRACE_EDGES):
            has_trace.add(f)
        if edges & set(RUNTIME_EDGES):
            has_runtime.add(f)
        if edges & set(ALL_P0):
            has_any_p0.add(f)

    # Files missing each dimension (and wirable)
    missing_evidence = [f for f in layer_files if f not in has_evidence]
    missing_governance = [f for f in layer_files if f not in has_governance]
    missing_trace = [f for f in layer_files if f not in has_trace]
    missing_runtime = [f for f in layer_files if f not in has_runtime]
    missing_any = [f for f in layer_files if f not in has_any_p0]

    # Filter to wirable
    wirable_evidence = [f for f in missing_evidence if has_wirable_functions(os.path.join(PROJECT_ROOT, f))]
    wirable_governance = [
        f for f in missing_governance if has_wirable_functions(os.path.join(PROJECT_ROOT, f))
    ]
    wirable_trace = [f for f in missing_trace if has_wirable_functions(os.path.join(PROJECT_ROOT, f))]
    wirable_runtime = [f for f in missing_runtime if has_wirable_functions(os.path.join(PROJECT_ROOT, f))]

    ev_pct = len(has_evidence) / total * 100 if total else 0
    gov_pct = len(has_governance) / total * 100 if total else 0
    tr_pct = len(has_trace) / total * 100 if total else 0
    rt_pct = len(has_runtime) / total * 100 if total else 0

    print(f"\n--- {layer} ({total} files, {len(has_any_p0)} with P0 edges) ---")
    print(
        f"  Evidence:   {len(has_evidence):>4}/{total} ({ev_pct:5.1f}%)  gap={len(wirable_evidence)} wirable",
    )
    print(
        f"  Governance: {len(has_governance):>4}/{total} ({gov_pct:5.1f}%)  gap={len(wirable_governance)} wirable",
    )
    print(f"  Trace:      {len(has_trace):>4}/{total} ({tr_pct:5.1f}%)  gap={len(wirable_trace)} wirable")
    print(f"  Runtime:    {len(has_runtime):>4}/{total} ({rt_pct:5.1f}%)  gap={len(wirable_runtime)} wirable")

    layer_gaps[layer] = {
        "total": total,
        "evidence_gap": wirable_evidence,
        "governance_gap": wirable_governance,
        "trace_gap": wirable_trace,
        "runtime_gap": wirable_runtime,
    }

# Print priority action plan
print("\n" + "=" * 80)
print("PRIORITY ACTION PLAN (weakest layers first)")
print("=" * 80)

# Sort by total gap
for layer in sorted(
    LAYERS,
    key=lambda l: sum(
        len(layer_gaps.get(l, {}).get(k, []))
        for k in ["evidence_gap", "governance_gap", "trace_gap", "runtime_gap"]
    ),
    reverse=True,
):
    gaps = layer_gaps.get(layer, {})
    total_gap = sum(
        len(gaps.get(k, [])) for k in ["evidence_gap", "governance_gap", "trace_gap", "runtime_gap"]
    )
    print(f"\n{layer}: {total_gap} total wirable gaps")
    for dim, key, emit_fn in [
        ("Evidence", "evidence_gap", "_emit_records_execution_trace"),
        ("Governance", "governance_gap", "_emit_applies_guardrail"),
        ("Trace", "trace_gap", "_emit_signs_execution_trace"),
        ("Runtime", "runtime_gap", "_emit_snapshots_state"),
    ]:
        files = gaps.get(key, [])
        if files:
            # Show files that don't already have the emit
            need_wire = [f for f in files if not has_emit(os.path.join(PROJECT_ROOT, f), emit_fn)]
            print(f"  {dim} ({len(need_wire)} need {emit_fn}):")
            for f in need_wire[:5]:
                print(f"    {f}")
            if len(need_wire) > 5:
                print(f"    ... +{len(need_wire) - 5} more")

db.close()
