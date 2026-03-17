"""Wave 101-110: Full governance numerator audit.

For every governance edge type, show how many are from _emit_* instrumentation
vs real runtime usage. This determines which metrics need normalization.
"""
import glob
import os
import sqlite3

ADG_DIR = r"C:\Git\Agentic-Workflow\artifacts\adg"
files = sorted(glob.glob(os.path.join(ADG_DIR, "adg_indexed_*.sqlite")))
db_path = files[-1]
print(f"Using: {db_path}\n")

conn = sqlite3.connect(db_path)

# All governance numerator types + denominator types
EDGE_TYPES = [
    # Denominators
    "writes_to", "reads_from", "records_execution_trace", "calls",
    # Governance numerators
    "writes_through", "reads_through", "routes_through",
    "pulls_context", "emits_determinism_digest", "emits_metric_event",
    "signs_execution_trace", "applies_guardrail", "snapshots_state",
    "emits_replay_key", "execution_terminates_at_uwg", "validated_by_safety_plane",
    # P1-P4 numerators (high-count ones)
    "orchestrates_workflow", "dispatches_healing_run",
    "agent_executes_agent", "dispatches_execution_plan",
    "validates_agent_capability", "checks_agent_registry",
    "authorize_and_execute", "validates_capability", "routes_to_capability",
    "writes_via_uwg", "blocks_direct_write", "records_tool_invocation",
    "captures_execution_output", "hard_fails_untranscripted",
    "verifies_boundary", "verifies_policy", "transcripts_response",
    "observes_runtime_state", "stores_embedding", "triggers_alert",
]

print(f"{'Edge Type':<40} {'Total':>8} {'_emit_*':>8} {'Real':>8} {'Synth%':>8}")
print("-" * 72)

results = []
for rt in EDGE_TYPES:
    total = conn.execute(
        "SELECT COUNT(*) FROM edges WHERE relation_type=?", (rt,)
    ).fetchone()[0]
    if total == 0:
        continue

    # Count edges where symbol starts with _emit_ or emit_
    synthetic = conn.execute(
        "SELECT COUNT(*) FROM edges WHERE relation_type=? AND (symbol LIKE '_emit_%' OR symbol LIKE 'emit_%')",
        (rt,)
    ).fetchone()[0]
    real = total - synthetic
    pct = f"{synthetic/total*100:.1f}%" if total > 0 else "0%"

    marker = ""
    if synthetic > 0 and synthetic / total > 0.9:
        marker = " *** MOSTLY SYNTHETIC"
    elif synthetic > 0 and synthetic / total > 0.5:
        marker = " ** MIXED"
    elif synthetic > 0:
        marker = " * SOME"

    print(f"  {rt:<38} {total:>8,} {synthetic:>8,} {real:>8,} {pct:>8}{marker}")
    results.append((rt, total, synthetic, real))

# Summary
print("\n=== SUMMARY ===")
total_all = sum(t for _, t, _, _ in results)
total_synth = sum(s for _, _, s, _ in results)
print(f"  Total edges checked: {total_all:,}")
print(f"  Total synthetic: {total_synth:,}")
print(f"  Total real: {total_all - total_synth:,}")

# Show which metrics are invalidated
print("\n=== RATIO VALIDITY AFTER FULL CLEANUP ===")
ratios = [
    ("writes_through / writes_to", "writes_through", "writes_to"),
    ("reads_through / reads_from", "reads_through", "reads_from"),
    ("pulls_context / records_execution_trace", "pulls_context", "records_execution_trace"),
    ("emits_determinism_digest / records_execution_trace", "emits_determinism_digest", "records_execution_trace"),
    ("records_execution_trace / calls", "records_execution_trace", "calls"),
    ("emits_metric_event / records_execution_trace", "emits_metric_event", "records_execution_trace"),
    ("validated_by_safety_plane / applies_guardrail", "validated_by_safety_plane", "applies_guardrail"),
]

# Build lookup
lookup = {rt: (total, synth, real) for rt, total, synth, real in results}

for label, num_rt, den_rt in ratios:
    if num_rt in lookup and den_rt in lookup:
        _, _, num_real = lookup[num_rt]
        _, _, den_real = lookup[den_rt]
        current_ratio = lookup[num_rt][0] / lookup[den_rt][0] * 100 if lookup[den_rt][0] > 0 else float('inf')
        clean_ratio = num_real / den_real * 100 if den_real > 0 else float('inf')
        print(f"\n  {label}")
        print(f"    Current: {lookup[num_rt][0]:,} / {lookup[den_rt][0]:,} = {current_ratio:.1f}%")
        print(f"    Clean:   {num_real:,} / {den_real:,} = {clean_ratio:.1f}%")

conn.close()
