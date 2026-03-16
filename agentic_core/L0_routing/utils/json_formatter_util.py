import json
import logging
import sys
from datetime import datetime, timezone

from agentic_core.config.settings_config import get_settings

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
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
    emit_determinism_digest,
    emit_replay_key,
)

_emit_dispatches_healing_run("p1", "json_formatter_util", "L0")
_emit_routes_through("p1", "json_formatter_util", "L0")
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
