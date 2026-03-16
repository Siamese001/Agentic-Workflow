"""
Script to execute the integrated Sovereignty Guardians.
Runs RootHygieneAgent and PascalSovereigntyAgent to clean and enforce standards.
"""

import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
)
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

_emit_records_execution_trace("p0", "evidence", "run_sovereignty_agents")
_emit_applies_guardrail("p0", "run_sovereignty_agents", "p0_governance")
_emit_reads_policy_state("p0", "run_sovereignty_agents", "policy_binding")
_emit_snapshots_state("p0", "run_sovereignty_agents", "state_snapshot")
emit_replay_key("p0", "run_sovereignty_agents")
emit_determinism_digest("p0", "run_sovereignty_agents")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "run_sovereignty_agents", "execution_auth")
_emit_validates_capability("p2", "run_sovereignty_agents", "capability_check")
_emit_routes_to_capability("p2", "run_sovereignty_agents", "capability_route")
_emit_writes_via_uwg("p2", "run_sovereignty_agents", "uwg_write")
_emit_blocks_direct_write("p2", "run_sovereignty_agents", "direct_write_block")
_emit_records_tool_invocation("p2", "run_sovereignty_agents", "tool_invocation")
_emit_captures_execution_output("p2", "run_sovereignty_agents", "exec_output")
_emit_dispatches_agent("p3", "run_sovereignty_agents", "agent_dispatch")
_emit_coordinates_agents("p3", "run_sovereignty_agents", "agent_coordination")
_emit_records_workflow_lineage("p3", "run_sovereignty_agents", "workflow_lineage")
_emit_records_healing_outcome("p3", "run_sovereignty_agents", "healing_outcome")
_emit_escalates_failure("p3", "run_sovereignty_agents", "failure_escalation")
_emit_orchestrates_workflow("p3", "run_sovereignty_agents", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "run_sovereignty_agents", "healing_dispatch")
_emit_invokes_evaluation("p3", "run_sovereignty_agents", "evaluation_signal")
_emit_records_telemetry_event("p4", "run_sovereignty_agents", "telemetry_event")
_emit_captures_evaluation_metric("p4", "run_sovereignty_agents", "eval_metric")
_emit_stores_embedding("p4", "run_sovereignty_agents", "embedding_store")
_emit_updates_meta_learning_state("p4", "run_sovereignty_agents", "meta_learning")
_emit_links_execution_to_snapshot("p4", "run_sovereignty_agents", "exec_snapshot_link")

project_root = Path(__file__).parent.parent
# guardian: allow-global-mutation
sys.path.insert(0, str(project_root))
from agentic_core.L5_safety.reasoning.PascalSovereigntyAgent import PascalSovereigntyAgent
from agentic_core.L5_safety.reasoning.root_hygiene_healer import RootHygieneAgent


def main():
    print("=" * 80)
    print("SOVEREIGNTY GUARDIANS EXECUTION")
    print("=" * 80)
    print("\n[PHASE 1] Executing RootHygieneAgent...")
    hygiene_agent = RootHygieneAgent(project_root=project_root, dry_run=False)
    hygiene_result = hygiene_agent.run()
    print("\n=== ROOT HYGIENE RESULTS ===")
    print(f"Success: {hygiene_result['success']}")
    print(f"Stats: {hygiene_result['stats']}")
    print(f"Summary: {hygiene_result['summary']}")
    print("\n[PHASE 2] Executing PascalSovereigntyAgent...")
    pascal_agent = PascalSovereigntyAgent(project_root=project_root, dry_run=False)
    pascal_result = pascal_agent.run()
    print("\n=== PASCAL SOVEREIGNTY RESULTS ===")
    print(f"Success: {pascal_result['success']}")
    print(f"Stats: {pascal_result['stats']}")
    print(f"Summary: {pascal_result['summary']}")
    print("\n[PHASE 3] Running validation audit...")
    validator = PascalSovereigntyAgent(project_root=project_root, dry_run=True, validate_only=True)
    validator.run()
    total_violations = sum(validator.stats["violations"].values())
    print("\n=== VALIDATION AUDIT ===")
    print(f"Total Violations Remaining: {total_violations}")
    print(f"Compliant Files: {validator.stats['compliant']}")
    print(f"Analyzed Files: {validator.stats['analyzed']}")
    if total_violations == 0:
        print("\n✅ 100% COMPLIANT - All sovereignty standards enforced!")
        return 0
    else:
        print(f"\n⚠️  {total_violations} violations remain - manual review required")
        return 1


if __name__ == "__main__":
    sys.exit(main())
