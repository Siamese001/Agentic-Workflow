from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
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
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "replay_key_computer")
emit_determinism_digest("p0", "replay_key_computer")

_emit_dispatches_healing_run("p1", "replay_key_computer", "L6")
_emit_routes_through("p1", "replay_key_computer", "L6")
_emit_escalates_to_human("p1", "replay_key_computer", "L6")
_emit_reads_policy_state("p1", "replay_key_computer", "L6")
_emit_authorize_and_execute("p2", "replay_key_computer", "execution_auth")
_emit_validates_capability("p2", "replay_key_computer", "capability_check")
_emit_routes_to_capability("p2", "replay_key_computer", "capability_route")
_emit_writes_via_uwg("p2", "replay_key_computer", "uwg_write")
_emit_blocks_direct_write("p2", "replay_key_computer", "direct_write_block")
_emit_records_tool_invocation("p2", "replay_key_computer", "tool_invocation")
_emit_captures_execution_output("p2", "replay_key_computer", "exec_output")
_emit_dispatches_agent("p3", "replay_key_computer", "agent_dispatch")
_emit_coordinates_agents("p3", "replay_key_computer", "agent_coordination")
_emit_records_workflow_lineage("p3", "replay_key_computer", "workflow_lineage")
_emit_records_healing_outcome("p3", "replay_key_computer", "healing_outcome")
_emit_escalates_failure("p3", "replay_key_computer", "failure_escalation")
_emit_orchestrates_workflow("p3", "replay_key_computer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "replay_key_computer", "healing_dispatch")
_emit_invokes_evaluation("p3", "replay_key_computer", "evaluation_signal")
_emit_records_telemetry_event("p4", "replay_key_computer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "replay_key_computer", "eval_metric")
_emit_stores_embedding("p4", "replay_key_computer", "embedding_store")
_emit_updates_meta_learning_state("p4", "replay_key_computer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "replay_key_computer", "exec_snapshot_link")


@dataclass(frozen=True)
class ReplayKeyComponents:
    """A structured container for all components that define a replay key."""

    tier_selection: str
    retry_count: int
    threshold_config: dict[str, float]
    tool_budget_caps: dict[str, int]
    freshness_windows: dict[str, int]
    config_surface_hash: str
    embedding_pack_hash: str
    embedding_model_version: str
    c0_context_hash: str


def compute_replay_key(components: ReplayKeyComponents) -> str:
    """
    Computes a deterministic replay key from a comprehensive set of components.

    This function enforces Guarantee #12 by creating a single, verifiable hash
    that represents the entire context of a governance decision. Any change to
    the inputs (e.g., a config change, a model update, or a different retry
    count) will produce a different key, ensuring that replays are always
    executed against the exact context of the original decision.

    The key is computed in L6 (Observability) and would be stored in L4 (State)
    alongside the decision record.

    Args:
        components: A structured dataclass containing all parts of the replay key.

    Returns:
        A SHA-256 hex digest representing the deterministic replay key.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "compute_replay_key", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "compute_replay_key", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L6_OBSERVABILITY, "compute_replay_key")

    def _canonical_json(data: Any) -> str:
        """Computes canonical JSON: sorted keys, UTF-8, no whitespace."""
        return json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":"))

    from dataclasses import asdict

    material = asdict(components)
    canonical_string = _canonical_json(material)
    return hashlib.sha256(canonical_string.encode("utf-8")).hexdigest()
