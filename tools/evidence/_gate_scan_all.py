"""Scan all blocking files for gate violations."""

import sys

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "_gate_scan_all")
_emit_applies_guardrail("p0", "_gate_scan_all", "p0_governance")
_emit_reads_policy_state("p0", "_gate_scan_all", "policy_binding")
_emit_snapshots_state("p0", "_gate_scan_all", "state_snapshot")
emit_replay_key("p0", "_gate_scan_all")
emit_determinism_digest("p0", "_gate_scan_all")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "_gate_scan_all", "execution_auth")
_emit_validates_capability("p2", "_gate_scan_all", "capability_check")
_emit_routes_to_capability("p2", "_gate_scan_all", "capability_route")
_emit_writes_via_uwg("p2", "_gate_scan_all", "uwg_write")
_emit_blocks_direct_write("p2", "_gate_scan_all", "direct_write_block")
_emit_records_tool_invocation("p2", "_gate_scan_all", "tool_invocation")
_emit_captures_execution_output("p2", "_gate_scan_all", "exec_output")
_emit_dispatches_agent("p3", "_gate_scan_all", "agent_dispatch")
_emit_coordinates_agents("p3", "_gate_scan_all", "agent_coordination")
_emit_records_workflow_lineage("p3", "_gate_scan_all", "workflow_lineage")
_emit_records_healing_outcome("p3", "_gate_scan_all", "healing_outcome")
_emit_escalates_failure("p3", "_gate_scan_all", "failure_escalation")
_emit_orchestrates_workflow("p3", "_gate_scan_all", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "_gate_scan_all", "healing_dispatch")
_emit_invokes_evaluation("p3", "_gate_scan_all", "evaluation_signal")
_emit_records_telemetry_event("p4", "_gate_scan_all", "telemetry_event")
_emit_captures_evaluation_metric("p4", "_gate_scan_all", "eval_metric")
_emit_stores_embedding("p4", "_gate_scan_all", "embedding_store")
_emit_updates_meta_learning_state("p4", "_gate_scan_all", "meta_learning")
_emit_links_execution_to_snapshot("p4", "_gate_scan_all", "exec_snapshot_link")

# guardian: allow-global-mutation
sys.path.insert(0, ".")
from collections import Counter
from pathlib import Path

from agentic_core.L5_safety.validators.anti_pattern_scanner_validator import AntiPatternScanner

project_root = Path(".")
scanner = AntiPatternScanner(project_root)

FILES = [
    "agentic_core/L5_safety/enforcement/hitl_gate.py",
    "tools/_scan_temp_folders.py",
    "tools/adg/adg_redis_ingest.py",
    "tools/evidence/_adg_confidence_audit.py",
    "tools/evidence/_adg_confidence_audit2.py",
    "tools/evidence/_scan_silent_swallower.py",
]

for f in FILES:
    p = Path(f)
    if not p.exists():
        print(f"MISSING: {f}")
        continue
    results = scanner.scan_file(p)
    if isinstance(results, list):
        cats = Counter(str(getattr(r, "category", r)).split(".")[-1].strip("'>") for r in results)
        if cats:
            print(f"\n{f}:")
            for cat, cnt in cats.items():
                print(f"  {cat}: {cnt}")
            for r in results:
                cat = str(getattr(r, "category", r)).split(".")[-1].strip("'>")
                ln = getattr(r, "line_number", "?")
                print(f"    line={ln}  cat={cat}")
