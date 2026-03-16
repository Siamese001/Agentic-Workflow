"""Scan execute_ssot.py for silent_swallower antipatterns using the gate's scanner."""

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

_emit_records_execution_trace("p0", "evidence", "_scan_silent_swallower")
_emit_applies_guardrail("p0", "_scan_silent_swallower", "p0_governance")
_emit_reads_policy_state("p0", "_scan_silent_swallower", "policy_binding")
_emit_snapshots_state("p0", "_scan_silent_swallower", "state_snapshot")
emit_replay_key("p0", "_scan_silent_swallower")
emit_determinism_digest("p0", "_scan_silent_swallower")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "_scan_silent_swallower", "execution_auth")
_emit_validates_capability("p2", "_scan_silent_swallower", "capability_check")
_emit_routes_to_capability("p2", "_scan_silent_swallower", "capability_route")
_emit_writes_via_uwg("p2", "_scan_silent_swallower", "uwg_write")
_emit_blocks_direct_write("p2", "_scan_silent_swallower", "direct_write_block")
_emit_records_tool_invocation("p2", "_scan_silent_swallower", "tool_invocation")
_emit_captures_execution_output("p2", "_scan_silent_swallower", "exec_output")
_emit_dispatches_agent("p3", "_scan_silent_swallower", "agent_dispatch")
_emit_coordinates_agents("p3", "_scan_silent_swallower", "agent_coordination")
_emit_records_workflow_lineage("p3", "_scan_silent_swallower", "workflow_lineage")
_emit_records_healing_outcome("p3", "_scan_silent_swallower", "healing_outcome")
_emit_escalates_failure("p3", "_scan_silent_swallower", "failure_escalation")
_emit_orchestrates_workflow("p3", "_scan_silent_swallower", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "_scan_silent_swallower", "healing_dispatch")
_emit_invokes_evaluation("p3", "_scan_silent_swallower", "evaluation_signal")
_emit_records_telemetry_event("p4", "_scan_silent_swallower", "telemetry_event")
_emit_captures_evaluation_metric("p4", "_scan_silent_swallower", "eval_metric")
_emit_stores_embedding("p4", "_scan_silent_swallower", "embedding_store")
_emit_updates_meta_learning_state("p4", "_scan_silent_swallower", "meta_learning")
_emit_links_execution_to_snapshot("p4", "_scan_silent_swallower", "exec_snapshot_link")

# guardian: allow-global-mutation
sys.path.insert(0, ".")
from pathlib import Path

from agentic_core.L5_safety.validators.anti_pattern_scanner_validator import AntiPatternScanner

project_root = Path(".")
scanner = AntiPatternScanner(project_root)
results = scanner.scan_file(Path("agentic_core/L0_routing/scripts/execute_ssot.py"))
print(f"result type: {type(results)}")
if isinstance(results, list):
    ss = [
        r
        for r in results
        if getattr(r, "category", None) == "silent_swallower" or "silent" in str(getattr(r, "category", ""))
    ]
    print(f"silent_swallower count={len(ss)}")
    for item in ss:
        print(f"  line={getattr(item, 'line_no', '?')}  {str(item)[:120]}")
    # Show all categories
    from collections import Counter

    cats = Counter(getattr(r, "category", str(r)) for r in results)
    print("All categories:", dict(cats))
elif isinstance(results, dict):
    for cat, items in results.items():
        if cat == "silent_swallower":
            print(f"silent_swallower count={len(items)}")
            for item in items:
                print(f"  line={item.line_no}  snippet={item.snippet[:100]}")
        elif items:
            print(f"{cat} count={len(items)}")
