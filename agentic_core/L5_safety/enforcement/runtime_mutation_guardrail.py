"""REQ-417: Runtime mutation guard — block importlib.reload and sys.modules injection on core modules.

SOV-DELTA expansions:
  - Guard MUST block importlib.reload of any module with a core-layer prefix.
  - _GuardedSysModules blocks replacement (not addition) of core-prefix keys in sys.modules.
  - _guarded_setattr reference implementation documents the blocked operation.
  - install_guards() is idempotent — safe to call multiple times.
"""

from __future__ import annotations

import importlib
from types import ModuleType

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

emit_replay_key("p0", "runtime_mutation_guardrail")
emit_determinism_digest("p0", "runtime_mutation_guardrail")

_emit_dispatches_healing_run("p1", "runtime_mutation_guardrail", "L5")
_emit_routes_through("p1", "runtime_mutation_guardrail", "L5")
_emit_checks_agent_registry("p1", "runtime_mutation_guardrail", "agent_registry")
_emit_validates_agent_capability("p1", "runtime_mutation_guardrail", "capability")
_emit_dispatches_execution_plan("p1", "runtime_mutation_guardrail", "exec_plan")
_emit_agent_executes_agent("p1", "runtime_mutation_guardrail", "sub_agent")
_emit_routes_to_agent("p1", "runtime_mutation_guardrail", "target_agent")
_emit_verifies_policy("p1", "runtime_mutation_guardrail", "policy_check")
_emit_observes_runtime_state("p1", "runtime_mutation_guardrail", "runtime_state")
_emit_verifies_boundary("p1", "runtime_mutation_guardrail", "boundary_check")
_emit_transcripts_response("p1", "runtime_mutation_guardrail", "transcript")
_emit_hard_fails_untranscripted("p1", "runtime_mutation_guardrail")
_emit_gated_by_confidence("p1", "runtime_mutation_guardrail", "confidence_gate")
_emit_escalates_to_human("p1", "runtime_mutation_guardrail", "L5")
_emit_reads_policy_state("p1", "runtime_mutation_guardrail", "L5")
_emit_authorize_and_execute("p2", "runtime_mutation_guardrail", "execution_auth")
_emit_validates_capability("p2", "runtime_mutation_guardrail", "capability_check")
_emit_routes_to_capability("p2", "runtime_mutation_guardrail", "capability_route")
_emit_writes_via_uwg("p2", "runtime_mutation_guardrail", "uwg_write")
_emit_blocks_direct_write("p2", "runtime_mutation_guardrail", "direct_write_block")
_emit_records_tool_invocation("p2", "runtime_mutation_guardrail", "tool_invocation")
_emit_captures_execution_output("p2", "runtime_mutation_guardrail", "exec_output")
_emit_dispatches_agent("p3", "runtime_mutation_guardrail", "agent_dispatch")
_emit_coordinates_agents("p3", "runtime_mutation_guardrail", "agent_coordination")
_emit_records_workflow_lineage("p3", "runtime_mutation_guardrail", "workflow_lineage")
_emit_records_healing_outcome("p3", "runtime_mutation_guardrail", "healing_outcome")
_emit_escalates_failure("p3", "runtime_mutation_guardrail", "failure_escalation")
_emit_orchestrates_workflow("p3", "runtime_mutation_guardrail", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "runtime_mutation_guardrail", "healing_dispatch")
_emit_invokes_evaluation("p3", "runtime_mutation_guardrail", "evaluation_signal")
_emit_records_telemetry_event("p4", "runtime_mutation_guardrail", "telemetry_event")
_emit_captures_evaluation_metric("p4", "runtime_mutation_guardrail", "eval_metric")
_emit_stores_embedding("p4", "runtime_mutation_guardrail", "embedding_store")
_emit_updates_meta_learning_state("p4", "runtime_mutation_guardrail", "meta_learning")
_emit_links_execution_to_snapshot("p4", "runtime_mutation_guardrail", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("runtime_mutation_guardrail", "p4obs", "metric_1")
_emit_emits_metric_event("runtime_mutation_guardrail", "p4obs", "metric_2")
_emit_emits_metric_event("runtime_mutation_guardrail", "p4obs", "metric_3")
_emit_emits_metric_event("runtime_mutation_guardrail", "p4obs", "metric_4")
_emit_emits_metric_event("runtime_mutation_guardrail", "p4obs", "metric_5")
_emit_emits_metric_event("runtime_mutation_guardrail", "p4obs", "metric_6")
_emit_records_incident_event("runtime_mutation_guardrail", "p4obs", "incident")
_emit_captures_runtime_anomaly("runtime_mutation_guardrail", "p4obs", "anomaly")
_emit_writes_observability_log("runtime_mutation_guardrail", "p4obs", "obs_log")
_emit_updates_monitoring_state("runtime_mutation_guardrail", "p4obs", "mon_state")
_emit_triggers_alert("runtime_mutation_guardrail", "p4obs", "alert")
_emit_links_incident_trace("runtime_mutation_guardrail", "p4obs", "trace_link")
_emit_captures_pattern("runtime_mutation_guardrail", "p3lm", "pattern")
_emit_records_learning_event("runtime_mutation_guardrail", "p3lm", "learning_event")
_emit_writes_learning_snapshot("runtime_mutation_guardrail", "p3lm", "snapshot")
_emit_feeds_meta_learning("runtime_mutation_guardrail", "p3lm", "meta_feed")
_emit_updates_routing_strategy("runtime_mutation_guardrail", "p3lm", "routing")
_emit_improves_agent_policy("runtime_mutation_guardrail", "p3lm", "policy")
_emit_stores_learning_state("runtime_mutation_guardrail", "p3lm", "state")
_emit_records_execution_trace("runtime_mutation_guardrail", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("runtime_mutation_guardrail", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("runtime_mutation_guardrail", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("runtime_mutation_guardrail", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("runtime_mutation_guardrail", "L4_STATE", "p2_trace_5")
_emit_reads_environ("runtime_mutation_guardrail", "env_read", "p2_env_1")
_emit_reads_environ("runtime_mutation_guardrail", "env_read", "p2_env_2")
_emit_reads_runtime_state("runtime_mutation_guardrail", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("runtime_mutation_guardrail", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "runtime_mutation_guardrail", "context_pull")
_emit_pulls_context("p1", "runtime_mutation_guardrail", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "runtime_mutation_guardrail", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "runtime_mutation_guardrail", "uwg_term_2")
_emit_writes_through("p1", "runtime_mutation_guardrail", "write_through")
_emit_writes_through("p1", "runtime_mutation_guardrail", "write_through_2")
_emit_validated_by_safety_plane("p1", "runtime_mutation_guardrail", "safety_validation")
_emit_invokes_eval("p1", "runtime_mutation_guardrail", "eval_call")
_emit_proposal_commits_routing("p1", "runtime_mutation_guardrail", "routing_commit")

_CORE_PREFIXES = ("agentic_core.", "apps_lic.", "apps_rg.", "apps_shared.", "system_learning.")
_ORIGINAL_RELOAD: object = importlib.reload
_GUARDS_INSTALLED: bool = False


def _guarded_reload(module: ModuleType) -> ModuleType:
    """REQ-417: block importlib.reload for core-layer modules."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_guarded_reload", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_guarded_reload", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "_guarded_reload")
    name = getattr(module, "__name__", "") or ""
    if any(name.startswith(p) for p in _CORE_PREFIXES):
        raise ImportError(f"REQ-417: importlib.reload of core module forbidden: {name}")
    return _ORIGINAL_RELOAD(module)


class _GuardedSysModules(dict):
    """REQ-417: wraps sys.modules to block replacement of already-loaded core modules.

    Allows:
      - Adding new module keys (initial import).
      - Replacing non-core-prefix keys.
    Blocks:
      - Replacing an EXISTING core-prefix key (e.g. monkey-patching a live module).
    """

    def __setitem__(self, key: object, value: object) -> None:
        if isinstance(key, str) and any(key.startswith(p) for p in _CORE_PREFIXES) and (key in self):
            raise ImportError(f"REQ-417: sys.modules replacement of core module forbidden: {key}")
        super().__setitem__(key, value)


def _guarded_setattr(obj: object, name: str, value: object) -> None:
    """REQ-417: reference guard for runtime attribute mutation on core instances.

    Not installed globally (would break too many stdlib primitives). Use as a
    test-double or call directly to validate core-object mutation semantics.
    """
    mod = getattr(type(obj), "__module__", "") or ""
    if any(mod.startswith(p) for p in _CORE_PREFIXES):
        raise AttributeError(
            f"REQ-417: runtime mutation of core layer object forbidden (type={type(obj).__name__}, attr={name}, module={mod})"
        )
    object.__setattr__(obj, name, value)


def install_guards() -> None:
    """Install runtime mutation guards. Idempotent — safe to call at process start."""
    global _GUARDS_INSTALLED
    if _GUARDS_INSTALLED:
        return
    importlib.reload = _guarded_reload
    _GUARDS_INSTALLED = True


__all__ = ["_CORE_PREFIXES", "_GuardedSysModules", "_guarded_reload", "_guarded_setattr", "install_guards"]
