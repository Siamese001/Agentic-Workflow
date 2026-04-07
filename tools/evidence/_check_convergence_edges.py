"""Check emits_determinism_digest and records_execution_trace edge counts in the latest ADG."""
import glob
import os
import sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADG_DIR = os.path.join(ROOT, "artifacts", "adg")

# Find latest sqlite
candidates = sorted(glob.glob(os.path.join(ADG_DIR, "adg_indexed_*.sqlite")), key=lambda p: os.path.basename(p), reverse=True)
if not candidates:
    print("ERROR: No ADG SQLite found")
    exit(1)

db_path = candidates[0]
print(f"Using: {os.path.basename(db_path)}")

conn = sqlite3.connect(db_path)
c = conn.cursor()

# Check the 17 remaining blocker modules
BLOCKERS = [
    "agentic_core/L0_routing/enforcement/trace_id_generator.py",
    "agentic_core/L0_routing/enforcement/traceability_contracts.py",
    "agentic_core/L0_routing/telemetry/routing_telemetry.py",
    "agentic_core/L2_execution/determinism/execution_proof_emitter.py",
    "agentic_core/L2_execution/trace_context.py",
    "agentic_core/L2_execution/types/execution_trace_types.py",
    "agentic_core/L3_orchestration/types/execution_trace_types.py",
    "agentic_core/L4_state/enforcement/telemetry_recorder.py",
    "agentic_core/L6_observability/enforcement/agent_monitor.py",
    "agentic_core/L6_observability/enforcement/outcome_logger.py",
    "agentic_core/L6_observability/evaluation/evaluation_record.py",
    "agentic_core/L6_observability/evaluation/evaluation_signal_integrator.py",
    "agentic_core/L6_observability/metrics/performance_metrics_emitter.py",
    "agentic_core/adg/runtime/determinism_control.py",
    "agentic_core/runtime/trace_emitter.py",
    "ops_scripts/ci/_reasoning_traceability_gate.py",
    "system_learning/engines/trace_feature_extractor.py",
]

print(f"\nChecking {len(BLOCKERS)} remaining blocker modules:")
print("-" * 80)

for module in BLOCKERS:
    rows = c.execute(
        "SELECT relation_type, COUNT(*) FROM edges WHERE source_file = ? GROUP BY relation_type",
        (module,),
    ).fetchall()
    rels = {r[0]: r[1] for r in rows}
    has_digest = "emits_determinism_digest" in rels
    has_trace = "records_execution_trace" in rels
    status = []
    if not has_digest:
        status.append("MISSING emits_determinism_digest")
    if not has_trace:
        status.append("MISSING records_execution_trace")
    if status:
        print(f"  BLOCKER {module}: {', '.join(status)}")
    else:
        print(f"  OK      {module}")

# Overall counts
print(f"\n{'='*60}")
print("OVERALL ADG EDGE COUNTS")
print(f"{'='*60}")
for rel in ["emits_determinism_digest", "records_execution_trace"]:
    count = c.execute("SELECT COUNT(*) FROM edges WHERE relation_type = ?", (rel,)).fetchone()[0]
    modules = c.execute("SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type = ?", (rel,)).fetchone()[0]
    print(f"  {rel}: {count} edges across {modules} modules")

conn.close()
