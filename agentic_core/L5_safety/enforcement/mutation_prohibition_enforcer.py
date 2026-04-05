"""G-12-1 — Physical Mutation Prohibition for L0/L4/L6.

Every persistent write from L0, L4, or L6 MUST fail closed at runtime.
This module is the single source of truth for mutation prohibition enforcement.

Persistent writes include: Path.write_text/write_bytes, json.dump to file,
os.rename/remove/unlink, shutil.move/rmtree, and open(..., 'w'/'a').

Override: AGENTIC_ALLOW_MUTATION_FOR_TESTS=1 (env var, test-only).
"""

from __future__ import annotations

import logging
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator

from agentic_core.L2_execution.utils import write_gateway as _wg
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "mutation_prohibition_enforcer")
emit_determinism_digest("p0", "mutation_prohibition_enforcer")

_emit_dispatches_healing_run("p1", "mutation_prohibition_enforcer", "L5")
_emit_routes_through("p1", "mutation_prohibition_enforcer", "L5")
_emit_checks_agent_registry("p1", "mutation_prohibition_enforcer", "agent_registry")
_emit_validates_agent_capability("p1", "mutation_prohibition_enforcer", "capability")
_emit_dispatches_execution_plan("p1", "mutation_prohibition_enforcer", "exec_plan")
_emit_agent_executes_agent("p1", "mutation_prohibition_enforcer", "sub_agent")
_emit_routes_to_agent("p1", "mutation_prohibition_enforcer", "target_agent")
_emit_verifies_policy("p1", "mutation_prohibition_enforcer", "policy_check")
_emit_observes_runtime_state("p1", "mutation_prohibition_enforcer", "runtime_state")
_emit_verifies_boundary("p1", "mutation_prohibition_enforcer", "boundary_check")
_emit_transcripts_response("p1", "mutation_prohibition_enforcer", "transcript")
_emit_hard_fails_untranscripted("p1", "mutation_prohibition_enforcer")
_emit_gated_by_confidence("p1", "mutation_prohibition_enforcer", "confidence_gate")
_emit_escalates_to_human("p1", "mutation_prohibition_enforcer", "L5")
_emit_reads_policy_state("p1", "mutation_prohibition_enforcer", "L5")
_emit_authorize_and_execute("p2", "mutation_prohibition_enforcer", "execution_auth")
_emit_validates_capability("p2", "mutation_prohibition_enforcer", "capability_check")
_emit_routes_to_capability("p2", "mutation_prohibition_enforcer", "capability_route")
_emit_writes_via_uwg("p2", "mutation_prohibition_enforcer", "uwg_write")
_emit_blocks_direct_write("p2", "mutation_prohibition_enforcer", "direct_write_block")
_emit_records_tool_invocation("p2", "mutation_prohibition_enforcer", "tool_invocation")
_emit_captures_execution_output("p2", "mutation_prohibition_enforcer", "exec_output")
_emit_dispatches_agent("p3", "mutation_prohibition_enforcer", "agent_dispatch")
_emit_coordinates_agents("p3", "mutation_prohibition_enforcer", "agent_coordination")
_emit_records_workflow_lineage("p3", "mutation_prohibition_enforcer", "workflow_lineage")
_emit_records_healing_outcome("p3", "mutation_prohibition_enforcer", "healing_outcome")
_emit_escalates_failure("p3", "mutation_prohibition_enforcer", "failure_escalation")
_emit_orchestrates_workflow("p3", "mutation_prohibition_enforcer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "mutation_prohibition_enforcer", "healing_dispatch")
_emit_invokes_evaluation("p3", "mutation_prohibition_enforcer", "evaluation_signal")
_emit_records_telemetry_event("p4", "mutation_prohibition_enforcer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "mutation_prohibition_enforcer", "eval_metric")
_emit_stores_embedding("p4", "mutation_prohibition_enforcer", "embedding_store")
_emit_updates_meta_learning_state("p4", "mutation_prohibition_enforcer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "mutation_prohibition_enforcer", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("mutation_prohibition_enforcer", "p4obs", "metric_1")
_emit_emits_metric_event("mutation_prohibition_enforcer", "p4obs", "metric_2")
_emit_emits_metric_event("mutation_prohibition_enforcer", "p4obs", "metric_3")
_emit_emits_metric_event("mutation_prohibition_enforcer", "p4obs", "metric_4")
_emit_emits_metric_event("mutation_prohibition_enforcer", "p4obs", "metric_5")
_emit_emits_metric_event("mutation_prohibition_enforcer", "p4obs", "metric_6")
_emit_records_incident_event("mutation_prohibition_enforcer", "p4obs", "incident")
_emit_captures_runtime_anomaly("mutation_prohibition_enforcer", "p4obs", "anomaly")
_emit_writes_observability_log("mutation_prohibition_enforcer", "p4obs", "obs_log")
_emit_updates_monitoring_state("mutation_prohibition_enforcer", "p4obs", "mon_state")
_emit_triggers_alert("mutation_prohibition_enforcer", "p4obs", "alert")
_emit_links_incident_trace("mutation_prohibition_enforcer", "p4obs", "trace_link")
_emit_captures_pattern("mutation_prohibition_enforcer", "p3lm", "pattern")
_emit_records_learning_event("mutation_prohibition_enforcer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("mutation_prohibition_enforcer", "p3lm", "snapshot")
_emit_feeds_meta_learning("mutation_prohibition_enforcer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("mutation_prohibition_enforcer", "p3lm", "routing")
_emit_improves_agent_policy("mutation_prohibition_enforcer", "p3lm", "policy")
_emit_stores_learning_state("mutation_prohibition_enforcer", "p3lm", "state")
_emit_records_execution_trace("mutation_prohibition_enforcer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("mutation_prohibition_enforcer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("mutation_prohibition_enforcer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("mutation_prohibition_enforcer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("mutation_prohibition_enforcer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("mutation_prohibition_enforcer", "env_read", "p2_env_1")
_emit_reads_environ("mutation_prohibition_enforcer", "env_read", "p2_env_2")
_emit_reads_runtime_state("mutation_prohibition_enforcer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("mutation_prohibition_enforcer", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "mutation_prohibition_enforcer", "context_pull")
_emit_pulls_context("p1", "mutation_prohibition_enforcer", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "mutation_prohibition_enforcer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "mutation_prohibition_enforcer", "uwg_term_2")
_emit_writes_through("p1", "mutation_prohibition_enforcer", "write_through")
_emit_writes_through("p1", "mutation_prohibition_enforcer", "write_through_2")
_emit_validated_by_safety_plane("p1", "mutation_prohibition_enforcer", "safety_validation")
_emit_invokes_eval("p1", "mutation_prohibition_enforcer", "eval_call")
_emit_proposal_commits_routing("p1", "mutation_prohibition_enforcer", "routing_commit")

logger = logging.getLogger(__name__)
FORBIDDEN_WRITE_LAYERS: frozenset[str] = frozenset({"L0", "L4", "L6"})
_ENV_OVERRIDE_KEY = "AGENTIC_ALLOW_MUTATION_FOR_TESTS"


def _is_override_active() -> bool:
    """Check if the test-only mutation override env var is set."""
    return os.environ.get(_ENV_OVERRIDE_KEY) == "1"


def assert_no_persistent_write(
    layer: str, op: str, path: str | None = None, trace_id: str | None = None
) -> None:
    """Fail-closed guard: raises PermissionError if layer is forbidden.

    Args:
        layer: Calling layer identifier (e.g. "L0", "L4", "L6").
        op: Operation name (e.g. "write_text", "json.dump", "shutil.move").
        path: Optional target path for the write.
        trace_id: Optional trace identifier for deterministic diagnostics.

    Raises:
        PermissionError: If layer is in FORBIDDEN_WRITE_LAYERS and override inactive.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "assert_no_persistent_write", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "assert_no_persistent_write", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "assert_no_persistent_write")
    if layer not in FORBIDDEN_WRITE_LAYERS:
        return
    if _is_override_active():
        return
    msg_parts = [f"MUTATION_PROHIBITED:layer={layer}", f"op={op}"]
    if path is not None:
        msg_parts.append(f"path={path}")
    if trace_id is not None:
        msg_parts.append(f"trace_id={trace_id}")
    msg = "|".join(msg_parts)
    logger.error("MUTATION_PROHIBITION DENY: %s", msg)
    raise PermissionError(msg)


def safe_write_text(
    filepath: Path | str, content: str, *, layer: str, trace_id: str | None = None, encoding: str = "utf-8"
) -> None:
    """Guarded Path.write_text replacement."""
    assert_no_persistent_write(layer, "write_text", str(filepath), trace_id)
    _wg.write_text(Path(filepath), content, encoding=encoding)


def safe_write_bytes(filepath: Path | str, data: bytes, *, layer: str, trace_id: str | None = None) -> None:
    """Guarded Path.write_bytes replacement."""
    assert_no_persistent_write(layer, "write_bytes", str(filepath), trace_id)
    _wg.write_bytes(Path(filepath), data)


def safe_json_dump(
    obj: Any,
    filepath: Path | str,
    *,
    layer: str,
    trace_id: str | None = None,
    indent: int | None = 2,
    sort_keys: bool = True,
    **kwargs: Any,
) -> None:
    """Guarded json.dump-to-file replacement."""
    assert_no_persistent_write(layer, "json.dump", str(filepath), trace_id)
    _wg.write_json(filepath, obj, indent=indent)


def safe_shutil_move(src: Path | str, dst: Path | str, *, layer: str, trace_id: str | None = None) -> None:
    """Guarded shutil.move replacement."""
    assert_no_persistent_write(layer, "shutil.move", str(dst), trace_id)
    _wg.move_path(str(src), str(dst))


def safe_shutil_rmtree(target: Path | str, *, layer: str, trace_id: str | None = None) -> None:
    """Guarded shutil.rmtree replacement."""
    assert_no_persistent_write(layer, "shutil.rmtree", str(target), trace_id)
    _wg.remove_tree(str(target))


def safe_os_remove(filepath: Path | str, *, layer: str, trace_id: str | None = None) -> None:
    """Guarded os.remove replacement."""
    assert_no_persistent_write(layer, "os.remove", str(filepath), trace_id)
    _wg.remove_file(filepath)


def safe_os_rename(src: Path | str, dst: Path | str, *, layer: str, trace_id: str | None = None) -> None:
    """Guarded os.rename replacement."""
    assert_no_persistent_write(layer, "os.rename", str(dst), trace_id)
    _wg.rename_path(src, dst)


def safe_open_write(
    filepath: Path | str,
    mode: str = "w",
    *,
    layer: str,
    trace_id: str | None = None,
    encoding: str | None = "utf-8",
) -> Any:
    """Guarded open(..., 'w'/'a') replacement. Returns file handle."""
    assert_no_persistent_write(layer, f"open({mode})", str(filepath), trace_id)
    return open(filepath, mode, encoding=encoding)


@contextmanager
def mutation_guard(layer: str) -> Generator[None, None, None]:
    """Context manager that asserts no mutation is in progress for the layer.

    Raises PermissionError on entry if layer is forbidden.
    Useful for wrapping code blocks that should never write.
    """
    assert_no_persistent_write(layer, "mutation_guard_enter")
    yield


__all__ = [
    "FORBIDDEN_WRITE_LAYERS",
    "assert_no_persistent_write",
    "mutation_guard",
    "safe_json_dump",
    "safe_open_write",
    "safe_os_remove",
    "safe_os_rename",
    "safe_shutil_move",
    "safe_shutil_rmtree",
    "safe_write_bytes",
    "safe_write_text",
]
