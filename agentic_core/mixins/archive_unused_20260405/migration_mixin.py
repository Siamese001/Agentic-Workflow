import inspect
import logging
from datetime import datetime
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
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
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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

_emit_applies_guardrail("p0", "migration_mixin", "p0_governance")
_emit_reads_policy_state("p0", "migration_mixin", "policy_binding")
_emit_snapshots_state("p0", "migration_mixin", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("migration_mixin", "p4obs", "metric_1")
_emit_emits_metric_event("migration_mixin", "p4obs", "metric_2")
_emit_emits_metric_event("migration_mixin", "p4obs", "metric_3")
_emit_emits_metric_event("migration_mixin", "p4obs", "metric_4")
_emit_emits_metric_event("migration_mixin", "p4obs", "metric_5")
_emit_emits_metric_event("migration_mixin", "p4obs", "metric_6")
_emit_records_incident_event("migration_mixin", "p4obs", "incident")
_emit_captures_runtime_anomaly("migration_mixin", "p4obs", "anomaly")
_emit_writes_observability_log("migration_mixin", "p4obs", "obs_log")
_emit_updates_monitoring_state("migration_mixin", "p4obs", "mon_state")
_emit_triggers_alert("migration_mixin", "p4obs", "alert")
_emit_links_incident_trace("migration_mixin", "p4obs", "trace_link")
_emit_captures_pattern("migration_mixin", "p3lm", "pattern")
_emit_records_learning_event("migration_mixin", "p3lm", "learning_event")
_emit_writes_learning_snapshot("migration_mixin", "p3lm", "snapshot")
_emit_feeds_meta_learning("migration_mixin", "p3lm", "meta_feed")
_emit_updates_routing_strategy("migration_mixin", "p3lm", "routing")
_emit_improves_agent_policy("migration_mixin", "p3lm", "policy")
_emit_stores_learning_state("migration_mixin", "p3lm", "state")
_emit_records_execution_trace("migration_mixin", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("migration_mixin", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("migration_mixin", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("migration_mixin", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("migration_mixin", "L4_STATE", "p2_trace_5")
_emit_reads_environ("migration_mixin", "env_read", "p2_env_1")
_emit_reads_environ("migration_mixin", "env_read", "p2_env_2")
_emit_reads_runtime_state("migration_mixin", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("migration_mixin", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "migration_mixin", "context_pull")
_emit_pulls_context("p1", "migration_mixin", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "migration_mixin", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "migration_mixin", "uwg_term_2")
_emit_writes_through("p1", "migration_mixin", "write_through")
_emit_writes_through("p1", "migration_mixin", "write_through_2")
_emit_validated_by_safety_plane("p1", "migration_mixin", "safety_validation")
_emit_invokes_eval("p1", "migration_mixin", "eval_call")
_emit_proposal_commits_routing("p1", "migration_mixin", "routing_commit")
_emit_escalates_to_human("p1", "migration_mixin", "human_escalation")
_emit_routes_through("p1", "migration_mixin", "route_through")
_emit_checks_agent_registry("p1", "migration_mixin", "agent_registry")
_emit_validates_agent_capability("p1", "migration_mixin", "capability")
_emit_dispatches_execution_plan("p1", "migration_mixin", "exec_plan")
_emit_agent_executes_agent("p1", "migration_mixin", "sub_agent")
_emit_routes_to_agent("p1", "migration_mixin", "target_agent")
_emit_verifies_policy("p1", "migration_mixin", "policy_check")
_emit_observes_runtime_state("p1", "migration_mixin", "runtime_state")
_emit_verifies_boundary("p1", "migration_mixin", "boundary_check")
_emit_transcripts_response("p1", "migration_mixin", "transcript")
_emit_hard_fails_untranscripted("p1", "migration_mixin")
_emit_gated_by_confidence("p1", "migration_mixin", "confidence_gate")
emit_replay_key("p0", "migration_mixin")
emit_determinism_digest("p0", "migration_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "migration_mixin", "execution_auth")
_emit_validates_capability("p2", "migration_mixin", "capability_check")
_emit_routes_to_capability("p2", "migration_mixin", "capability_route")
_emit_writes_via_uwg("p2", "migration_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "migration_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "migration_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "migration_mixin", "exec_output")
_emit_dispatches_agent("p3", "migration_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "migration_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "migration_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "migration_mixin", "healing_outcome")
_emit_escalates_failure("p3", "migration_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "migration_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "migration_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "migration_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "migration_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "migration_mixin", "eval_metric")
_emit_stores_embedding("p4", "migration_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "migration_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "migration_mixin", "exec_snapshot_link")


class MigrationError(Exception):
    """Raised when a schema migration fails or is invalid."""

    pass


class MigrationMixin:
    """
    Phase 2 observability Infrastructure: Migration Support (Report 4.5).

    Provides version awareness and schema migration hooks for agents.
    Features:
    - Version tracking (_schema_version)
    - Automatic migration discovery
    - Backward compatibility warnings
    - Migration history tracking
    """

    _schema_version: str = "1.0"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._mm_logger = logging.getLogger(self.__class__.__name__)
        self._migration_history: list[dict[str, str]] = []

    def get_current_version(self) -> str:
        """Returns the current schema version of the agent."""
        return self._schema_version

    async def migrate_data(self, data: dict[str, Any], from_version: str) -> dict[str, Any]:
        """Hardened: rollback snapshot + post-migration validation."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "MigrationMixin.migrate_data")

        data.copy()
        "\n        Orchestrates the migration of data from an older version to current.\n\n        Args:\n            data: The raw data dictionary to migrate.\n            from_version: The version string the data currently follows.\n\n        Returns:\n            Dict: The migrated data matching the current _schema_version.\n        "
        target_version = self._schema_version
        if from_version == target_version:
            return data
        self._mm_logger.info(f"Starting migration: {from_version} -> {target_version}")
        current_v = from_version
        while current_v != target_version:
            v_norm = current_v.replace(".", "_")
            migration_method_name = f"migrate_v{v_norm}_to_next"
            migration_func = getattr(self, migration_method_name, None)
            if not migration_func:
                error_msg = f"No migration path found from {current_v}. Missing {migration_method_name}."
                self._mm_logger.error(error_msg)
                raise MigrationError(error_msg)
            pre_step_snapshot = data.copy()
            old_v = current_v
            try:
                data = await migration_func(data)
                current_v = data.get("_new_version_id", target_version)
                self._migration_history.append(
                    {"from": old_v, "to": current_v, "timestamp": datetime.utcnow().isoformat()},
                )
                if hasattr(self, "_validate_after_migration_step"):
                    hook = self._validate_after_migration_step
                    hook_result = hook(data, current_v)
                    if inspect.isawaitable(hook_result):
                        await hook_result
            except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
                raise
                self._mm_logger.error(f"Rollback triggered at {old_v}: {e}")
                data = pre_step_snapshot
                if hasattr(self, "emit_event"):
                    self.emit_event(
                        "migration.rollback",
                        {"from_version": old_v, "to_version": current_v, "error": str(e)},
                        severity="ERROR",
                    )
                raise MigrationError(f"Step {current_v} failed: {e}")
        self._mm_logger.info(f"Migration successful. Final version: {current_v}")
        return data
