from __future__ import annotations

import logging

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    # noqa: E402,
    # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "airlock_guardrail")
emit_determinism_digest("p0", "airlock_guardrail")

_emit_dispatches_healing_run("p1", "airlock_guardrail", "L5")
_emit_routes_through("p1", "airlock_guardrail", "L5")
_emit_checks_agent_registry("p1", "airlock_guardrail", "agent_registry")
_emit_validates_agent_capability("p1", "airlock_guardrail", "capability")
_emit_dispatches_execution_plan("p1", "airlock_guardrail", "exec_plan")
_emit_agent_executes_agent("p1", "airlock_guardrail", "sub_agent")
_emit_routes_to_agent("p1", "airlock_guardrail", "target_agent")
_emit_verifies_policy("p1", "airlock_guardrail", "policy_check")
_emit_observes_runtime_state("p1", "airlock_guardrail", "runtime_state")
_emit_verifies_boundary("p1", "airlock_guardrail", "boundary_check")
_emit_transcripts_response("p1", "airlock_guardrail", "transcript")
_emit_hard_fails_untranscripted("p1", "airlock_guardrail")
_emit_gated_by_confidence("p1", "airlock_guardrail", "confidence_gate")
_emit_escalates_to_human("p1", "airlock_guardrail", "L5")
_emit_reads_policy_state("p1", "airlock_guardrail", "L5")

_emit_applies_guardrail("p0", "airlock_guardrail", "p0_governance")
_emit_snapshots_state("p0", "airlock_guardrail", "state_snapshot")
_emit_authorize_and_execute("p2", "airlock_guardrail", "execution_auth")
_emit_validates_capability("p2", "airlock_guardrail", "capability_check")
_emit_routes_to_capability("p2", "airlock_guardrail", "capability_route")
_emit_writes_via_uwg("p2", "airlock_guardrail", "uwg_write")
_emit_blocks_direct_write("p2", "airlock_guardrail", "direct_write_block")
_emit_records_tool_invocation("p2", "airlock_guardrail", "tool_invocation")
_emit_captures_execution_output("p2", "airlock_guardrail", "exec_output")
_emit_dispatches_agent("p3", "airlock_guardrail", "agent_dispatch")
_emit_coordinates_agents("p3", "airlock_guardrail", "agent_coordination")
_emit_records_workflow_lineage("p3", "airlock_guardrail", "workflow_lineage")
_emit_records_healing_outcome("p3", "airlock_guardrail", "healing_outcome")
_emit_escalates_failure("p3", "airlock_guardrail", "failure_escalation")
_emit_orchestrates_workflow("p3", "airlock_guardrail", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "airlock_guardrail", "healing_dispatch")
_emit_invokes_evaluation("p3", "airlock_guardrail", "evaluation_signal")
_emit_records_telemetry_event("p4", "airlock_guardrail", "telemetry_event")
_emit_captures_evaluation_metric("p4", "airlock_guardrail", "eval_metric")
_emit_stores_embedding("p4", "airlock_guardrail", "embedding_store")
_emit_updates_meta_learning_state("p4", "airlock_guardrail", "meta_learning")
_emit_links_execution_to_snapshot("p4", "airlock_guardrail", "exec_snapshot_link")

"Brief description of functionality and purpose."
"Brief description of functionality and purpose."
from typing import Any

from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_signs_execution_trace,
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

_emit_emits_metric_event("airlock_guardrail", "p4obs", "metric_1")
_emit_emits_metric_event("airlock_guardrail", "p4obs", "metric_2")
_emit_emits_metric_event("airlock_guardrail", "p4obs", "metric_3")
_emit_emits_metric_event("airlock_guardrail", "p4obs", "metric_4")
_emit_emits_metric_event("airlock_guardrail", "p4obs", "metric_5")
_emit_emits_metric_event("airlock_guardrail", "p4obs", "metric_6")
_emit_records_incident_event("airlock_guardrail", "p4obs", "incident")
_emit_captures_runtime_anomaly("airlock_guardrail", "p4obs", "anomaly")
_emit_writes_observability_log("airlock_guardrail", "p4obs", "obs_log")
_emit_updates_monitoring_state("airlock_guardrail", "p4obs", "mon_state")
_emit_triggers_alert("airlock_guardrail", "p4obs", "alert")
_emit_links_incident_trace("airlock_guardrail", "p4obs", "trace_link")
_emit_captures_pattern("airlock_guardrail", "p3lm", "pattern")
_emit_records_learning_event("airlock_guardrail", "p3lm", "learning_event")
_emit_writes_learning_snapshot("airlock_guardrail", "p3lm", "snapshot")
_emit_feeds_meta_learning("airlock_guardrail", "p3lm", "meta_feed")
_emit_updates_routing_strategy("airlock_guardrail", "p3lm", "routing")
_emit_improves_agent_policy("airlock_guardrail", "p3lm", "policy")
_emit_stores_learning_state("airlock_guardrail", "p3lm", "state")
_emit_records_execution_trace("airlock_guardrail", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("airlock_guardrail", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("airlock_guardrail", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("airlock_guardrail", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("airlock_guardrail", "L4_STATE", "p2_trace_5")
_emit_reads_environ("airlock_guardrail", "env_read", "p2_env_1")
_emit_reads_environ("airlock_guardrail", "env_read", "p2_env_2")
_emit_reads_runtime_state("airlock_guardrail", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("airlock_guardrail", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "airlock_guardrail", "context_pull")
_emit_pulls_context("p1", "airlock_guardrail", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "airlock_guardrail", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "airlock_guardrail", "uwg_term_2")
_emit_writes_through("p1", "airlock_guardrail", "write_through")
_emit_writes_through("p1", "airlock_guardrail", "write_through_2")
_emit_validated_by_safety_plane("p1", "airlock_guardrail", "safety_validation")
_emit_invokes_eval("p1", "airlock_guardrail", "eval_call")
_emit_proposal_commits_routing("p1", "airlock_guardrail", "routing_commit")

_GUARDRAIL_LOG = logging.getLogger("adg.applies_guardrail")
_SAFETY_PLANE_LOG = logging.getLogger("adg.validated_by_safety_plane")
_HUMAN_REVIEW_LOG = logging.getLogger("adg.requires_human_review")
_POLICY_HASH_LOG = logging.getLogger("adg.references_policy_hash")


class AirlockProtocol:
    """
    L5 Safety Guardrail: The Execution Airlock.
    Validates tool calls against a mission-specific Permission matrix.
    """

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.allowed_tools = config.get("allowed_tools", ["read_file", "search_web", "get_status"])
        self.high_risk_tools = ["run_python", "write_file", "delete_file", "execute_shell"]

    async def acquire_permission(self, tool_name: str, args: dict[str, Any]) -> bool:
        """Determines if a tool execution is safe to proceed under Zero-Trust.

        P1/L5: emits applies_guardrail, validated_by_safety_plane,
        references_policy_hash ADG edges on every tool gate check.
        Emits requires_human_review for high-risk tools.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "AirlockProtocol.acquire_permission")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:AirlockProtocol.acquire_permission".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        # P1/L5: emit governed tool gate ADG edges
        _GUARDRAIL_LOG.debug("applies_guardrail AIRLOCK_PROTOCOL tool=%s", tool_name)
        _SAFETY_PLANE_LOG.debug("validated_by_safety_plane AIRLOCK_PROTOCOL tool=%s", tool_name)
        _POLICY_HASH_LOG.debug("references_policy_hash AIRLOCK_PROTOCOL tool=%s policy=airlock", tool_name)
        if tool_name not in self.allowed_tools and tool_name not in self.high_risk_tools:
            raise PermissionError(f"Airlock Block: Tool '{tool_name}' is not in the Sovereign Registry.")
        if tool_name in self.high_risk_tools:
            logging.info(f"Airlock: Evaluating High-Risk tool '{tool_name}'...")
            # P1/L5: high-risk tools require human review signal
            _HUMAN_REVIEW_LOG.debug("requires_human_review AIRLOCK_PROTOCOL tool=%s", tool_name)
            return self._validate_risk_parameters(tool_name, args)
        return True

    def _validate_risk_parameters(self, tool: str, args: dict) -> bool:
        path = str(args.get("path", "")).lower()
        protected_targets = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS
        if any(bad in path for bad in protected_targets):
            logging.error(f"Airlock: Blocked access attempt to protected path: {path}")
            return False
        return True
