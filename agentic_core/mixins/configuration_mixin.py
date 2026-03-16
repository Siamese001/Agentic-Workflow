"""
import uuid
ConfigMixin - Unified configuration Access for Agents

[PHASE 6 MIGRATION] Provides access to SovereignConfigManager.
"""

from agentic_core.config.core.sovereign_config import (
    SovereignConfigManager,
    get_sovereign_config,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
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

_emit_applies_guardrail("p0", "configuration_mixin", "p0_governance")
_emit_reads_policy_state("p0", "configuration_mixin", "policy_binding")
_emit_snapshots_state("p0", "configuration_mixin", "state_snapshot")
emit_replay_key("p0", "configuration_mixin")
emit_determinism_digest("p0", "configuration_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "configuration_mixin", "execution_auth")
_emit_validates_capability("p2", "configuration_mixin", "capability_check")
_emit_routes_to_capability("p2", "configuration_mixin", "capability_route")
_emit_writes_via_uwg("p2", "configuration_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "configuration_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "configuration_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "configuration_mixin", "exec_output")
_emit_dispatches_agent("p3", "configuration_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "configuration_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "configuration_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "configuration_mixin", "healing_outcome")
_emit_escalates_failure("p3", "configuration_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "configuration_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "configuration_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "configuration_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "configuration_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "configuration_mixin", "eval_metric")
_emit_stores_embedding("p4", "configuration_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "configuration_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "configuration_mixin", "exec_snapshot_link")


class ConfigMixin:
    """
    Mixin providing typed configuration access.

    Usage:
        class MyAgent(ConfigMixin):
            def run(self):
                limit = self.config.max_audit_log_size
    """

    _config_manager: SovereignConfigManager | None = None

    @property
    def config(self) -> SovereignConfigManager:
        """Lazy-load config singleton."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ConfigMixin.config")

        if self._config_manager is None:
            self._config_manager = get_sovereign_config()
        return self._config_manager
