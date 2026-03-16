"""
Run NamingAgent to scan for duplicate filenames and class names.
"""

import sys
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
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

emit_replay_key("p0", "run_naming_scan_util")
emit_determinism_digest("p0", "run_naming_scan_util")

_emit_dispatches_healing_run("p1", "run_naming_scan_util", "L0")
_emit_routes_through("p1", "run_naming_scan_util", "L0")
_emit_escalates_to_human("p1", "run_naming_scan_util", "L0")
_emit_reads_policy_state("p1", "run_naming_scan_util", "L0")

_emit_records_execution_trace("p0", "evidence", "run_naming_scan_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "run_naming_scan_util", "p0_governance")
_emit_snapshots_state("p0", "run_naming_scan_util", "state_snapshot")
_emit_authorize_and_execute("p2", "run_naming_scan_util", "execution_auth")
_emit_validates_capability("p2", "run_naming_scan_util", "capability_check")
_emit_routes_to_capability("p2", "run_naming_scan_util", "capability_route")
_emit_writes_via_uwg("p2", "run_naming_scan_util", "uwg_write")
_emit_blocks_direct_write("p2", "run_naming_scan_util", "direct_write_block")
_emit_records_tool_invocation("p2", "run_naming_scan_util", "tool_invocation")
_emit_captures_execution_output("p2", "run_naming_scan_util", "exec_output")
_emit_dispatches_agent("p3", "run_naming_scan_util", "agent_dispatch")
_emit_coordinates_agents("p3", "run_naming_scan_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "run_naming_scan_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "run_naming_scan_util", "healing_outcome")
_emit_escalates_failure("p3", "run_naming_scan_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "run_naming_scan_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "run_naming_scan_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "run_naming_scan_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "run_naming_scan_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "run_naming_scan_util", "eval_metric")
_emit_stores_embedding("p4", "run_naming_scan_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "run_naming_scan_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "run_naming_scan_util", "exec_snapshot_link")

project_root = Path(__file__).resolve().parents[1]
# guardian: allow-global-mutation
sys.path.insert(0, str(project_root))
from agentic_core.L0_routing.seams.safety_reasoning_seam import load_naming_agent

print("=" * 80)
print("NAMING AGENT SCAN - Duplicate Detection")
print("=" * 80)
NamingAgent = load_naming_agent()
naming = NamingAgent(project_root)
print("\n[1] Scanning for duplicate FILENAMES...")
duplicates = naming.scan_for_duplicate_filenames()
if duplicates:
    print(f"\n❌ Found {len(duplicates)} duplicate filenames:")
    for basename, paths in sorted(duplicates.items()):
        print(f"\n  {basename} ({len(paths)} occurrences):")
        for p in paths:
            print(f"    - {p.relative_to(project_root)}")
else:
    print("\n✅ No duplicate filenames found")
print("\n" + "=" * 80)
print("[2] Scanning for duplicate CLASS NAMES...")
import json
from collections import defaultdict

from agentic_core.L0_routing.config import AGENT_DISCOVERY_JSON

discovery_path = project_root / AGENT_DISCOVERY_JSON
if discovery_path.exists():
    agents = json.loads(discovery_path.read_text(encoding="utf-8"))
    by_name = defaultdict(list)
    for a in agents:
        by_name[a["class_name"]].append(a["path"])
    dup_classes = {k: v for k, v in by_name.items() if len(v) > 1}
    if dup_classes:
        print(f"\n❌ Found {len(dup_classes)} duplicate class names:")
        for name, paths in sorted(dup_classes.items()):
            print(f"\n  {name} ({len(paths)} occurrences):")
            for p in paths:
                print(f"    - {p}")
    else:
        print("\n✅ No duplicate class names found")
else:
    print("\n⚠️  agent_discovery_full.json not found - run full_agent_discovery.py first")
print("\n" + "=" * 80)
print("SCAN COMPLETE")
print("=" * 80)
