"""Re-export symbols from the standalone determinism.py module.

The standalone agentic_core/L2_execution/determinism.py is shadowed by this
package directory. This __init__ loads it via importlib and re-exports its
public API so that existing `from agentic_core.L2_execution.determinism import ...`
calls continue to work.
"""

from __future__ import annotations

import importlib.util
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
from agentic_core.L5_safety.enforcement.import_guard import get_import_guard
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

emit_replay_key("p0", "__init__")
emit_determinism_digest("p0", "__init__")

_emit_dispatches_healing_run("p1", "__init__", "L2")
_emit_routes_through("p1", "__init__", "L2")
_emit_escalates_to_human("p1", "__init__", "L2")
_emit_reads_policy_state("p1", "__init__", "L2")

_emit_snapshots_state("p0", "__init__", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "__init__", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "__init__")
_emit_authorize_and_execute("p2", "__init__", "execution_auth")
_emit_validates_capability("p2", "__init__", "capability_check")
_emit_routes_to_capability("p2", "__init__", "capability_route")
_emit_writes_via_uwg("p2", "__init__", "uwg_write")
_emit_blocks_direct_write("p2", "__init__", "direct_write_block")
_emit_records_tool_invocation("p2", "__init__", "tool_invocation")
_emit_captures_execution_output("p2", "__init__", "exec_output")
_emit_dispatches_agent("p3", "__init__", "agent_dispatch")
_emit_coordinates_agents("p3", "__init__", "agent_coordination")
_emit_records_workflow_lineage("p3", "__init__", "workflow_lineage")
_emit_records_healing_outcome("p3", "__init__", "healing_outcome")
_emit_escalates_failure("p3", "__init__", "failure_escalation")
_emit_orchestrates_workflow("p3", "__init__", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "__init__", "healing_dispatch")
_emit_invokes_evaluation("p3", "__init__", "evaluation_signal")
_emit_records_telemetry_event("p4", "__init__", "telemetry_event")
_emit_captures_evaluation_metric("p4", "__init__", "eval_metric")
_emit_stores_embedding("p4", "__init__", "embedding_store")
_emit_updates_meta_learning_state("p4", "__init__", "meta_learning")
_emit_links_execution_to_snapshot("p4", "__init__", "exec_snapshot_link")

_STANDALONE = Path(__file__).resolve().parent.parent / "determinism.py"
if _STANDALONE.exists():
    get_import_guard().check(
        operation="spec_from_file_location", module_name="agentic_core.L2_execution._determinism_standalone"
    )
    _spec = importlib.util.spec_from_file_location(
        "agentic_core.L2_execution._determinism_standalone", _STANDALONE
    )
    _mod = importlib.util.module_from_spec(_spec)
    get_import_guard().check(operation="exec_module", module_name=_mod.__name__)
    _spec.loader.exec_module(_mod)
    build_agent_2x2_inventory = _mod.build_agent_2x2_inventory
    compute_p5_determinism_digest = _mod.compute_p5_determinism_digest
    compute_w6_determinism_digest = _mod.compute_w6_determinism_digest
    compute_lockdown_determinism_digest = _mod.compute_lockdown_determinism_digest
    generate_determinism_digest = _mod.generate_determinism_digest
    generate_lockdown_determinism_digest = _mod.generate_lockdown_determinism_digest
    write_agent_2x2_inventory = _mod.write_agent_2x2_inventory
    get_embedding_config_surface = _mod.get_embedding_config_surface
    get_meta_learning_config_surface = _mod.get_meta_learning_config_surface
    INVENTORY_ARTIFACT_PATH = _mod.INVENTORY_ARTIFACT_PATH
    REPO_ROOT = _mod.REPO_ROOT
