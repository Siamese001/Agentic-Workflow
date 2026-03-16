from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "align_tests_structure_util")
emit_determinism_digest("p0", "align_tests_structure_util")

_emit_dispatches_healing_run("p1", "align_tests_structure_util", "L0")
_emit_routes_through("p1", "align_tests_structure_util", "L0")
_emit_escalates_to_human("p1", "align_tests_structure_util", "L0")
_emit_reads_policy_state("p1", "align_tests_structure_util", "L0")
_emit_authorize_and_execute("p2", "align_tests_structure_util", "execution_auth")
_emit_validates_capability("p2", "align_tests_structure_util", "capability_check")
_emit_routes_to_capability("p2", "align_tests_structure_util", "capability_route")
_emit_writes_via_uwg("p2", "align_tests_structure_util", "uwg_write")
_emit_blocks_direct_write("p2", "align_tests_structure_util", "direct_write_block")
_emit_records_tool_invocation("p2", "align_tests_structure_util", "tool_invocation")
_emit_captures_execution_output("p2", "align_tests_structure_util", "exec_output")
_emit_dispatches_agent("p3", "align_tests_structure_util", "agent_dispatch")
_emit_coordinates_agents("p3", "align_tests_structure_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "align_tests_structure_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "align_tests_structure_util", "healing_outcome")
_emit_escalates_failure("p3", "align_tests_structure_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "align_tests_structure_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "align_tests_structure_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "align_tests_structure_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "align_tests_structure_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "align_tests_structure_util", "eval_metric")
_emit_stores_embedding("p4", "align_tests_structure_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "align_tests_structure_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "align_tests_structure_util", "exec_snapshot_link")

"\nTEST STRUCTURE ALIGNMENT\nEnsures all test directories have __init__.py for Python package recognition.\n"
import os
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config.path_constants import TESTS_DIR
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)


def align_tests_structure(root_path: Any) -> Any:
    """Brief description of functionality and purpose."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "align_tests_structure", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "align_tests_structure", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "align_tests_structure")
    from agentic_core.L5_safety.config.structure_blueprint import TESTS_L2_SUBFOLDER_MAP

    print("--- ALIGNING TESTS WITH SOVEREIGN LAW ---")
    tests_root: Any = Path(root_path) / TESTS_DIR
    for l1, l2_list in TESTS_L2_SUBFOLDER_MAP.items():
        l1_path: Any = Path(tests_root) / l1
        ensure_dir_structure(l1_path)
        for l2 in l2_list:
            l2_path: Any = Path(l1_path) / l2
            ensure_dir_structure(l2_path)


def ensure_dir_structure(path: Any) -> Any:
    """Brief description of functionality and purpose."""
    # guardian: allow-path-string
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        print(f"✅ CREATED: {path}")
    init_file: Any = Path(path) / "__init__.py"
    # guardian: allow-path-string
    if not os.path.exists(init_file):
        with open(init_file, "w") as f:
            f.write("# Sovereign Test Module\n")
        print(f"✅ ADDED __init__.py: {path}")
    gitkeep: Any = Path(path) / ".gitkeep"
    # guardian: allow-path-string
    if not os.path.exists(gitkeep):
        with open(gitkeep, "w") as f:
            f.write("")


if __name__ == "__main__":
    PROJECT_ROOT: Any = "C:/Git/Agentic-Workflow"
    align_tests_structure(PROJECT_ROOT)
    print("\n✅ TEST ALIGNMENT COMPLETE. Run your Gatekeeper to confirm.")
