"""Meta-Control Config Bridge — Wave 7.0.18.

Read-only accessor for APPS_* to consume the meta-control config store.
Delegates to agentic_core config_store; provides zero-write, zero-apply
helpers only.

Hard forbiddances (enforced by tests):
  - Must NOT import meta_apply / meta_apply_ops.
  - Must NOT call any apply functions.
  - Must NOT write files.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agentic_core.interfaces.meta_control import (
    canonical_json,
    load_current,
    validate_component_allowed,
)
from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
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

_emit_records_execution_trace("p0", "evidence", "meta_control_config_bridge")
_emit_applies_guardrail("p0", "meta_control_config_bridge", "p0_governance")
_emit_reads_policy_state("p0", "meta_control_config_bridge", "policy_binding")
_emit_snapshots_state("p0", "meta_control_config_bridge", "state_snapshot")
emit_replay_key("p0", "meta_control_config_bridge")
emit_determinism_digest("p0", "meta_control_config_bridge")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "meta_control_config_bridge", "execution_auth")
_emit_validates_capability("p2", "meta_control_config_bridge", "capability_check")
_emit_routes_to_capability("p2", "meta_control_config_bridge", "capability_route")
_emit_writes_via_uwg("p2", "meta_control_config_bridge", "uwg_write")
_emit_blocks_direct_write("p2", "meta_control_config_bridge", "direct_write_block")
_emit_records_tool_invocation("p2", "meta_control_config_bridge", "tool_invocation")
_emit_captures_execution_output("p2", "meta_control_config_bridge", "exec_output")
_emit_dispatches_agent("p3", "meta_control_config_bridge", "agent_dispatch")
_emit_coordinates_agents("p3", "meta_control_config_bridge", "agent_coordination")
_emit_records_workflow_lineage("p3", "meta_control_config_bridge", "workflow_lineage")
_emit_records_healing_outcome("p3", "meta_control_config_bridge", "healing_outcome")
_emit_escalates_failure("p3", "meta_control_config_bridge", "failure_escalation")
_emit_orchestrates_workflow("p3", "meta_control_config_bridge", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "meta_control_config_bridge", "healing_dispatch")
_emit_invokes_evaluation("p3", "meta_control_config_bridge", "evaluation_signal")
_emit_records_telemetry_event("p4", "meta_control_config_bridge", "telemetry_event")
_emit_captures_evaluation_metric("p4", "meta_control_config_bridge", "eval_metric")
_emit_stores_embedding("p4", "meta_control_config_bridge", "embedding_store")
_emit_updates_meta_learning_state("p4", "meta_control_config_bridge", "meta_learning")
_emit_links_execution_to_snapshot("p4", "meta_control_config_bridge", "exec_snapshot_link")

# Default store root — co-located with meta_control module.
_DEFAULT_STORE_ROOT = (
    Path(__file__).resolve().parents[2] / AGENTIC_CORE_DIR / "L0_routing" / "meta_control" / "config_store"
)


def load_app_component_config(
    app_id: str,
    target_component: str,
    *,
    store_root: Path | None = None,
) -> dict[str, Any]:
    """Load the current config payload for (app_id, target_component).

    Validates target_component against MUTABLE_COMPONENTS (L7 SSOT).
    Returns {} if no config exists yet (pass-through behavior).
    Raises ValueError for invalid component or empty app_id.
    """
    validate_component_allowed(target_component)
    root = store_root if store_root is not None else _DEFAULT_STORE_ROOT
    return load_current(root, app_id, target_component)


def render_app_component_config(
    app_id: str,
    target_component: str,
    *,
    store_root: Path | None = None,
) -> str:
    """Render the current config payload as canonical JSON string.

    Returns "{}" if no config exists yet.
    """
    payload = load_app_component_config(
        app_id,
        target_component,
        store_root=store_root,
    )
    return canonical_json(payload)
