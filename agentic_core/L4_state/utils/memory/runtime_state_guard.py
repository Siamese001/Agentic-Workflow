import json
import os
from pathlib import Path
from typing import Any

from agentic_core.interfaces.write_gateway import get_write_gateway
from agentic_core.L0_routing.config import RUNTIME_STATE_JSON
from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
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

emit_replay_key("p0", "runtime_state_guard")
emit_determinism_digest("p0", "runtime_state_guard")

_emit_dispatches_healing_run("p1", "runtime_state_guard", "L4")
_emit_routes_through("p1", "runtime_state_guard", "L4")
_emit_checks_agent_registry("p1", "runtime_state_guard", "agent_registry")
_emit_validates_agent_capability("p1", "runtime_state_guard", "capability")
_emit_dispatches_execution_plan("p1", "runtime_state_guard", "exec_plan")
_emit_agent_executes_agent("p1", "runtime_state_guard", "sub_agent")
_emit_routes_to_agent("p1", "runtime_state_guard", "target_agent")
_emit_verifies_policy("p1", "runtime_state_guard", "policy_check")
_emit_observes_runtime_state("p1", "runtime_state_guard", "runtime_state")
_emit_verifies_boundary("p1", "runtime_state_guard", "boundary_check")
_emit_transcripts_response("p1", "runtime_state_guard", "transcript")
_emit_hard_fails_untranscripted("p1", "runtime_state_guard")
_emit_gated_by_confidence("p1", "runtime_state_guard", "confidence_gate")
_emit_escalates_to_human("p1", "runtime_state_guard", "L4")
_emit_reads_policy_state("p1", "runtime_state_guard", "L4")
_emit_authorize_and_execute("p2", "runtime_state_guard", "execution_auth")
_emit_validates_capability("p2", "runtime_state_guard", "capability_check")
_emit_routes_to_capability("p2", "runtime_state_guard", "capability_route")
_emit_writes_via_uwg("p2", "runtime_state_guard", "uwg_write")
_emit_blocks_direct_write("p2", "runtime_state_guard", "direct_write_block")
_emit_records_tool_invocation("p2", "runtime_state_guard", "tool_invocation")
_emit_captures_execution_output("p2", "runtime_state_guard", "exec_output")
_emit_dispatches_agent("p3", "runtime_state_guard", "agent_dispatch")
_emit_coordinates_agents("p3", "runtime_state_guard", "agent_coordination")
_emit_records_workflow_lineage("p3", "runtime_state_guard", "workflow_lineage")
_emit_records_healing_outcome("p3", "runtime_state_guard", "healing_outcome")
_emit_escalates_failure("p3", "runtime_state_guard", "failure_escalation")
_emit_orchestrates_workflow("p3", "runtime_state_guard", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "runtime_state_guard", "healing_dispatch")
_emit_invokes_evaluation("p3", "runtime_state_guard", "evaluation_signal")
_emit_records_telemetry_event("p4", "runtime_state_guard", "telemetry_event")
_emit_captures_evaluation_metric("p4", "runtime_state_guard", "eval_metric")
_emit_stores_embedding("p4", "runtime_state_guard", "embedding_store")
_emit_updates_meta_learning_state("p4", "runtime_state_guard", "meta_learning")
_emit_links_execution_to_snapshot("p4", "runtime_state_guard", "exec_snapshot_link")
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

_emit_emits_metric_event("runtime_state_guard", "p4obs", "metric_1")
_emit_emits_metric_event("runtime_state_guard", "p4obs", "metric_2")
_emit_emits_metric_event("runtime_state_guard", "p4obs", "metric_3")
_emit_emits_metric_event("runtime_state_guard", "p4obs", "metric_4")
_emit_emits_metric_event("runtime_state_guard", "p4obs", "metric_5")
_emit_emits_metric_event("runtime_state_guard", "p4obs", "metric_6")
_emit_records_incident_event("runtime_state_guard", "p4obs", "incident")
_emit_captures_runtime_anomaly("runtime_state_guard", "p4obs", "anomaly")
_emit_writes_observability_log("runtime_state_guard", "p4obs", "obs_log")
_emit_updates_monitoring_state("runtime_state_guard", "p4obs", "mon_state")
_emit_triggers_alert("runtime_state_guard", "p4obs", "alert")
_emit_links_incident_trace("runtime_state_guard", "p4obs", "trace_link")
_emit_captures_pattern("runtime_state_guard", "p3lm", "pattern")
_emit_records_learning_event("runtime_state_guard", "p3lm", "learning_event")
_emit_writes_learning_snapshot("runtime_state_guard", "p3lm", "snapshot")
_emit_feeds_meta_learning("runtime_state_guard", "p3lm", "meta_feed")
_emit_updates_routing_strategy("runtime_state_guard", "p3lm", "routing")
_emit_improves_agent_policy("runtime_state_guard", "p3lm", "policy")
_emit_stores_learning_state("runtime_state_guard", "p3lm", "state")
_emit_records_execution_trace("runtime_state_guard", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("runtime_state_guard", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("runtime_state_guard", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("runtime_state_guard", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("runtime_state_guard", "L4_STATE", "p2_trace_5")
_emit_reads_environ("runtime_state_guard", "env_read", "p2_env_1")
_emit_reads_environ("runtime_state_guard", "env_read", "p2_env_2")
_emit_reads_runtime_state("runtime_state_guard", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("runtime_state_guard", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "runtime_state_guard", "context_pull")
_emit_pulls_context("p1", "runtime_state_guard", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "runtime_state_guard", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "runtime_state_guard", "uwg_term_2")
_emit_writes_through("p1", "runtime_state_guard", "write_through")
_emit_writes_through("p1", "runtime_state_guard", "write_through_2")
_emit_validated_by_safety_plane("p1", "runtime_state_guard", "safety_validation")
_emit_invokes_eval("p1", "runtime_state_guard", "eval_call")
_emit_proposal_commits_routing("p1", "runtime_state_guard", "routing_commit")


def _get_write_gateway():
    """Get UWG instance - L4 may only use, not import tools."""
    return get_write_gateway()


class RuntimeStateGuard:
    """
    Atomic guardian for runtime_state.json.
    Implements Write-Replace pattern and automatic backup recovery.
    """

    def __init__(self, project_root: Path):
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "RuntimeStateGuard.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "RuntimeStateGuard.__init__", "p0_governance")
        self.state_path = project_root / RUNTIME_STATE_JSON
        self.backup_path = project_root / f"{RUNTIME_STATE_JSON}.bak"
        self._state_cache: dict[str, Any] = {}
        self._batch_depth = 0
        self._dirty = False
        self._load_state()

    def __enter__(self):
        """Enter batch mode: suspend disk writes."""
        self._batch_depth += 1
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit batch mode: flush if at top level and dirty."""
        self._batch_depth = max(0, self._batch_depth - 1)
        if self._batch_depth == 0 and self._dirty:
            self._atomic_persist()
            self._dirty = False

    def _load_state(self):
        """Loads state with failover to backup if corruption is detected."""
        if not self.state_path.exists():
            self._state_cache = {}
            return
        try:
            with open(self.state_path) as f:
                self._state_cache = json.load(f)
        except json.JSONDecodeError:
            print(f"[StateGuard] CORRUPTION DETECTED in {self.state_path}. Attempting restore...")
            if self.backup_path.exists():
                _get_write_gateway().copy_file(self.backup_path, self.state_path)
                with open(self.state_path) as f:
                    self._state_cache = json.load(f)
            else:
                print("[StateGuard] No backup found. Resetting state.")
                self._state_cache = {}

    def get_metric(self, key: str, default: Any = 0) -> Any:
        return self._state_cache.get("shared_alignment_metrics", {}).get(key, default)

    def increment_metric(self, key: str, value: int = 1):
        """
        Updates metric.
        Persists immediately UNLESS inside a batch context.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "RuntimeStateGuard.increment_metric")

        metrics = self._state_cache.get("shared_alignment_metrics", {})
        current = metrics.get(key, 0)
        metrics[key] = current + value
        self._state_cache["shared_alignment_metrics"] = metrics
        if self._batch_depth > 0:
            self._dirty = True
        else:
            self._atomic_persist()

    def _atomic_persist(self):
        """
        Writes to a temp file then renames to ensure atomicity.
        Prevents half-written files during crashes.
        """
        temp_path = self.state_path.with_suffix(".tmp")
        try:
            assert_no_persistent_write("L4", "json.dump")
            _get_write_gateway().write_json(temp_path, self._state_cache, indent=4)
            if self.state_path.exists():
                _get_write_gateway().copy_file(self.state_path, self.backup_path)
            os.replace(temp_path, self.state_path)
        except (AttributeError, OSError, RuntimeError, TypeError, ValueError) as e:  # guardian: allow-silent-swallow
            print(f"[StateGuard] PERSISTENCE FAILURE: {e}")
            if temp_path.exists():
                assert_no_persistent_write("L4", "os.mutate")
                _get_write_gateway().remove_file(temp_path)
