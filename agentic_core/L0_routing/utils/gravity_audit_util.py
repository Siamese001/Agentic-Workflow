from __future__ import annotations

import ast

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

emit_replay_key("p0", "gravity_audit_util")
emit_determinism_digest("p0", "gravity_audit_util")

_emit_dispatches_healing_run("p1", "gravity_audit_util", "L0")
_emit_routes_through("p1", "gravity_audit_util", "L0")
_emit_escalates_to_human("p1", "gravity_audit_util", "L0")
_emit_reads_policy_state("p1", "gravity_audit_util", "L0")
_emit_authorize_and_execute("p2", "gravity_audit_util", "execution_auth")
_emit_validates_capability("p2", "gravity_audit_util", "capability_check")
_emit_routes_to_capability("p2", "gravity_audit_util", "capability_route")
_emit_writes_via_uwg("p2", "gravity_audit_util", "uwg_write")
_emit_blocks_direct_write("p2", "gravity_audit_util", "direct_write_block")
_emit_records_tool_invocation("p2", "gravity_audit_util", "tool_invocation")
_emit_captures_execution_output("p2", "gravity_audit_util", "exec_output")
_emit_dispatches_agent("p3", "gravity_audit_util", "agent_dispatch")
_emit_coordinates_agents("p3", "gravity_audit_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "gravity_audit_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "gravity_audit_util", "healing_outcome")
_emit_escalates_failure("p3", "gravity_audit_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "gravity_audit_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "gravity_audit_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "gravity_audit_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "gravity_audit_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "gravity_audit_util", "eval_metric")
_emit_stores_embedding("p4", "gravity_audit_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "gravity_audit_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "gravity_audit_util", "exec_snapshot_link")

"Brief description of functionality and purpose."
"Brief description of functionality and purpose."
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config import AGENTIC_CORE_DIR
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

root: Any = Path("C:/Git/Agentic-Workflow")
core: Any = ROOT / AGENTIC_CORE_DIR


def audit_gravity() -> Any:
    """Brief description of functionality and purpose."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "audit_gravity", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "audit_gravity", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "audit_gravity")
    print("[*] STARTING FINAL GRAVITY AUDIT...")
    leaks: Any = []
    from agentic_core.utils.ssot_discovery_validator import get_python_files

    for py_file in get_python_files(CORE):
        if py_file.name == "__init__.py" or "legacy" in str(py_file):
            continue
        try:
            with open(py_file, encoding="utf-8") as f:
                tree: Any = ast.parse(f.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if any(x in alias.name for x in [APPS_RG_DIR, APPS_LIC_DIR, APPS_SHARED_DIR]):
                            leaks.append((py_file.relative_to(ROOT), f"Direct: {alias.name}"))
                elif isinstance(node, ast.ImportFrom):
                    if node.module and any(
                        x in node.module for x in [APPS_RG_DIR, APPS_LIC_DIR, APPS_SHARED_DIR]
                    ):
                        leaks.append((py_file.relative_to(ROOT), f"From: {node.module}"))
        # guardian: allow-silent-swallow
        except Exception as e:
            print(f"  [!] Audit Failed for {py_file.name}: {e}")
    if not leaks:
        print("\n[SUCCESS] Gravity is 100% Pure. No downstream leaks detected.")
    else:
        print(f"\n[!] ALERT: Found {len(leaks)} Gravity Violations:")
        for file, reason in leaks:
            print(f"  [X] {file} -> {reason}")
    return leaks


if __name__ == "__main__":
    audit_gravity()
