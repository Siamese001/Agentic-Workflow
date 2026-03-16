from __future__ import annotations

import shutil
from pathlib import Path

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

emit_replay_key("p0", "extract_net")
emit_determinism_digest("p0", "extract_net")

_emit_dispatches_healing_run("p1", "extract_net", "L0")
_emit_routes_through("p1", "extract_net", "L0")
_emit_escalates_to_human("p1", "extract_net", "L0")
_emit_reads_policy_state("p1", "extract_net", "L0")
_emit_authorize_and_execute("p2", "extract_net", "execution_auth")
_emit_validates_capability("p2", "extract_net", "capability_check")
_emit_routes_to_capability("p2", "extract_net", "capability_route")
_emit_writes_via_uwg("p2", "extract_net", "uwg_write")
_emit_blocks_direct_write("p2", "extract_net", "direct_write_block")
_emit_records_tool_invocation("p2", "extract_net", "tool_invocation")
_emit_captures_execution_output("p2", "extract_net", "exec_output")
_emit_dispatches_agent("p3", "extract_net", "agent_dispatch")
_emit_coordinates_agents("p3", "extract_net", "agent_coordination")
_emit_records_workflow_lineage("p3", "extract_net", "workflow_lineage")
_emit_records_healing_outcome("p3", "extract_net", "healing_outcome")
_emit_escalates_failure("p3", "extract_net", "failure_escalation")
_emit_orchestrates_workflow("p3", "extract_net", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "extract_net", "healing_dispatch")
_emit_invokes_evaluation("p3", "extract_net", "evaluation_signal")
_emit_records_telemetry_event("p4", "extract_net", "telemetry_event")
_emit_captures_evaluation_metric("p4", "extract_net", "eval_metric")
_emit_stores_embedding("p4", "extract_net", "embedding_store")
_emit_updates_meta_learning_state("p4", "extract_net", "meta_learning")
_emit_links_execution_to_snapshot("p4", "extract_net", "exec_snapshot_link")

"Brief description of functionality and purpose."
"Brief description of functionality and purpose."
from typing import Any

from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)


def extract_net_incremental() -> None:
    """Extract files that don't exist in sovereign codebase."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "extract_net_incremental", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "extract_net_incremental", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "extract_net_incremental")
    source_dir: Any = Path("archives/legacy_lic")
    staging_dir: Any = Path("archive_code")
    if staging_dir.exists():
        assert_no_persistent_write("L0", "shutil.mutate")
        shutil.rmtree(staging_dir)
    staging_dir.mkdir()
    existing_files: Any = get_existing_files()
    extracted_files: Any = []
    from agentic_core.utils.ssot_discovery_validator import get_python_files

    for py_file in get_python_files(source_dir):
        FILENAME: Any = py_file.name
        name_exists: Any = any(FILENAME in existing for existing in existing_files)
        if not name_exists:
            dest_path: Any = staging_dir / FILENAME
            shutil.copy2(py_file, dest_path)
            extracted_files.append(FILENAME)
    return extracted_files
