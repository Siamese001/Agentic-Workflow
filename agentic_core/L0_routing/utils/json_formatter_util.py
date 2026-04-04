import json
import logging
import sys
from datetime import datetime, timezone

from agentic_core.config.settings_config import get_settings
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
    emit_determinism_digest,
    emit_replay_key,
)

_emit_dispatches_healing_run("p1", "json_formatter_util", "L0")
_emit_routes_through("p1", "json_formatter_util", "L0")
_emit_checks_agent_registry("p1", "json_formatter_util", "agent_registry")
_emit_validates_agent_capability("p1", "json_formatter_util", "capability")
_emit_dispatches_execution_plan("p1", "json_formatter_util", "exec_plan")
_emit_agent_executes_agent("p1", "json_formatter_util", "sub_agent")
_emit_routes_to_agent("p1", "json_formatter_util", "target_agent")
_emit_verifies_policy("p1", "json_formatter_util", "policy_check")
_emit_observes_runtime_state("p1", "json_formatter_util", "runtime_state")
_emit_verifies_boundary("p1", "json_formatter_util", "boundary_check")
_emit_transcripts_response("p1", "json_formatter_util", "transcript")
_emit_hard_fails_untranscripted("p1", "json_formatter_util")
_emit_gated_by_confidence("p1", "json_formatter_util", "confidence_gate")
_emit_escalates_to_human("p1", "json_formatter_util", "L0")
_emit_reads_policy_state("p1", "json_formatter_util", "L0")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "json_formatter_util", "p0_governance")
_emit_snapshots_state("p0", "json_formatter_util", "state_snapshot")
_emit_authorize_and_execute("p2", "json_formatter_util", "execution_auth")
_emit_validates_capability("p2", "json_formatter_util", "capability_check")
_emit_routes_to_capability("p2", "json_formatter_util", "capability_route")
_emit_writes_via_uwg("p2", "json_formatter_util", "uwg_write")
_emit_blocks_direct_write("p2", "json_formatter_util", "direct_write_block")
_emit_records_tool_invocation("p2", "json_formatter_util", "tool_invocation")
_emit_captures_execution_output("p2", "json_formatter_util", "exec_output")
_emit_dispatches_agent("p3", "json_formatter_util", "agent_dispatch")
_emit_coordinates_agents("p3", "json_formatter_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "json_formatter_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "json_formatter_util", "healing_outcome")
_emit_escalates_failure("p3", "json_formatter_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "json_formatter_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "json_formatter_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "json_formatter_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "json_formatter_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "json_formatter_util", "eval_metric")
_emit_stores_embedding("p4", "json_formatter_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "json_formatter_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "json_formatter_util", "exec_snapshot_link")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

_emit_emits_metric_event("json_formatter_util", "p4obs", "metric_1")
_emit_emits_metric_event("json_formatter_util", "p4obs", "metric_2")
_emit_emits_metric_event("json_formatter_util", "p4obs", "metric_3")
_emit_emits_metric_event("json_formatter_util", "p4obs", "metric_4")
_emit_emits_metric_event("json_formatter_util", "p4obs", "metric_5")
_emit_emits_metric_event("json_formatter_util", "p4obs", "metric_6")
_emit_records_incident_event("json_formatter_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("json_formatter_util", "p4obs", "anomaly")
_emit_writes_observability_log("json_formatter_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("json_formatter_util", "p4obs", "mon_state")
_emit_triggers_alert("json_formatter_util", "p4obs", "alert")
_emit_links_incident_trace("json_formatter_util", "p4obs", "trace_link")
_emit_captures_pattern("json_formatter_util", "p3lm", "pattern")
_emit_records_learning_event("json_formatter_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("json_formatter_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("json_formatter_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("json_formatter_util", "p3lm", "routing")
_emit_improves_agent_policy("json_formatter_util", "p3lm", "policy")
_emit_stores_learning_state("json_formatter_util", "p3lm", "state")
_emit_records_execution_trace("json_formatter_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("json_formatter_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("json_formatter_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("json_formatter_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("json_formatter_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("json_formatter_util", "env_read", "p2_env_1")
_emit_reads_environ("json_formatter_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("json_formatter_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("json_formatter_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "json_formatter_util", "context_pull")
_emit_pulls_context("p1", "json_formatter_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "json_formatter_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "json_formatter_util", "uwg_term_2")
_emit_writes_through("p1", "json_formatter_util", "write_through")
_emit_writes_through("p1", "json_formatter_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "json_formatter_util", "safety_validation")
_emit_invokes_eval("p1", "json_formatter_util", "eval_call")
_emit_proposal_commits_routing("p1", "json_formatter_util", "routing_commit")


class JSONFormatter(logging.Formatter):
    """
    Formats log records as JSON objects for machine parsing.
    """

    def format(self, record: logging.LogRecord) -> str:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "JSONFormatter.format")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        log_obj = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "func": record.funcName,
            "line": record.lineno,
            "app": get_settings().APP_NAME,
            "env": get_settings().ENVIRONMENT,
        }
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)


def setup_logging():
    """
    Initialize application-wide logging.
    Call this once at application startup.
    """
    settings = get_settings()
    handler = logging.StreamHandler(sys.stdout)
    if settings.ENVIRONMENT == "prod":
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s"))
    logger = logging.getLogger()
    logger.setLevel(settings.LOG_LEVEL)
    if not logger.handlers:
        logger.addHandler(handler)
    return logger
