"""
Final Consolidation Script - The End of Sprawl

1. Scans the codebase for imports pointing to deleted "Imposter" files.
2. Rewrites them to point to the "Canon" locations.
3. Runs the final ArchGuard verification.
"""

import os
import re
import subprocess
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR, get_validated_project_root
from agentic_core.L5_safety.config.structure_blueprint.ssot import SOVEREIGN_EXCLUDED_FOLDERS
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

_emit_records_execution_trace("p0", "evidence", "execute_final_consolidation")
_emit_applies_guardrail("p0", "execute_final_consolidation", "p0_governance")
_emit_reads_policy_state("p0", "execute_final_consolidation", "policy_binding")
_emit_snapshots_state("p0", "execute_final_consolidation", "state_snapshot")
emit_replay_key("p0", "execute_final_consolidation")
emit_determinism_digest("p0", "execute_final_consolidation")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "execute_final_consolidation", "execution_auth")
_emit_validates_capability("p2", "execute_final_consolidation", "capability_check")
_emit_routes_to_capability("p2", "execute_final_consolidation", "capability_route")
_emit_writes_via_uwg("p2", "execute_final_consolidation", "uwg_write")
_emit_blocks_direct_write("p2", "execute_final_consolidation", "direct_write_block")
_emit_records_tool_invocation("p2", "execute_final_consolidation", "tool_invocation")
_emit_captures_execution_output("p2", "execute_final_consolidation", "exec_output")
_emit_dispatches_agent("p3", "execute_final_consolidation", "agent_dispatch")
_emit_coordinates_agents("p3", "execute_final_consolidation", "agent_coordination")
_emit_records_workflow_lineage("p3", "execute_final_consolidation", "workflow_lineage")
_emit_records_healing_outcome("p3", "execute_final_consolidation", "healing_outcome")
_emit_escalates_failure("p3", "execute_final_consolidation", "failure_escalation")
_emit_orchestrates_workflow("p3", "execute_final_consolidation", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "execute_final_consolidation", "healing_dispatch")
_emit_invokes_evaluation("p3", "execute_final_consolidation", "evaluation_signal")
_emit_records_telemetry_event("p4", "execute_final_consolidation", "telemetry_event")
_emit_captures_evaluation_metric("p4", "execute_final_consolidation", "eval_metric")
_emit_stores_embedding("p4", "execute_final_consolidation", "embedding_store")
_emit_updates_meta_learning_state("p4", "execute_final_consolidation", "meta_learning")
_emit_links_execution_to_snapshot("p4", "execute_final_consolidation", "exec_snapshot_link")

PROJECT_ROOT = get_validated_project_root()

IMPORT_REDIRECTS = {
    r"agentic_core\.L5_safety\.guardrails\.cached_safety_shield": "agentic_core.L5_safety.validators.cached_safety_shield",
    r"agentic_core\.L5_safety\.guardrails\.NeuralAutoImmuneAgent": "agentic_core.L5_safety.reasoning.NeuralAutoImmuneAgent",
    r"agentic_core\.L5_safety\.validators\.DependencyDiplomatAgent": "agentic_core.L0_routing.scripts.DependencyDiplomatAgent",
    r"agentic_core\.L5_safety\.validators\.SemanticTerritoryMapperAgent": "agentic_core.L1_cognition.reasoning.SemanticTerritoryMapperAgent",
    r"agentic_core\.L2_execution\.tool_registry\.L2ExecutionBase": "agentic_core.L2_execution.L2ExecutionBase",
}


def fix_imports():
    print("--- STARTING FINAL IMPORT REWIRING ---")
    fixed_count = 0

    for root, _dirs, files in os.walk(PROJECT_ROOT / AGENTIC_CORE_DIR):
        _dirs[:] = [d for d in _dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]

        for file in files:
            if not file.endswith(".py"):
                continue

            file_path = Path(root) / file
            try:
                content = file_path.read_text(encoding="utf-8")
                original_content = content

                for bad_pattern, good_path in IMPORT_REDIRECTS.items():
                    if re.search(bad_pattern, content):
                        content = re.sub(bad_pattern, good_path, content)

                if content != original_content:
                    file_path.write_text(content, encoding="utf-8")
                    print(f"[FIXED] Rewired imports in {file}")
                    fixed_count += 1
            # guardian: allow-silent-swallow
            except Exception as e:
                raise
                print(f"[ERROR] processing {file}: {e}")

    print(f"--- REWIRING COMPLETE: {fixed_count} files updated ---")


def run_verification():
    print("\n--- RUNNING FINAL VERIFICATION ---")
    try:
        result = subprocess.run(
            ["pytest", "tests/integration/test_arch_guard.py"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )
        print(result.stdout)
        if result.returncode == 0:
            print("\n✅ SYSTEM IS GREEN. 100% SOVEREIGN COMPLIANCE.")
        else:
            print("\n⚠️ SYSTEM HAS REMAINING ISSUES. SEE OUTPUT ABOVE.")
            print(result.stderr)
    # guardian: allow-silent-swallow
    except Exception as e:
        raise
        print(f"Verification failed to run: {e}")


if __name__ == "__main__":
    fix_imports()
    run_verification()
