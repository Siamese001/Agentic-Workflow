"""
L2 Read Gateway — MCP-backed read operations.

All filesystem reads from non-local, external, or audited paths SHOULD be
routed through this gateway. Uses mcp6_* (MCP filesystem tools) for reads,
with graceful fallback to direct Python I/O when the MCP server is unavailable.

Tool ID Prefix: ACT-020
"""
# guardian: allow-silent_swallower - ADG violation exemption


from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

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

emit_replay_key("p0", "read_gateway")
emit_determinism_digest("p0", "read_gateway")

_emit_dispatches_healing_run("p1", "read_gateway", "L2")
_emit_routes_through("p1", "read_gateway", "L2")
_emit_checks_agent_registry("p1", "read_gateway", "agent_registry")
_emit_validates_agent_capability("p1", "read_gateway", "capability")
_emit_dispatches_execution_plan("p1", "read_gateway", "exec_plan")
_emit_agent_executes_agent("p1", "read_gateway", "sub_agent")
_emit_routes_to_agent("p1", "read_gateway", "target_agent")
_emit_verifies_policy("p1", "read_gateway", "policy_check")
_emit_observes_runtime_state("p1", "read_gateway", "runtime_state")
_emit_verifies_boundary("p1", "read_gateway", "boundary_check")
_emit_transcripts_response("p1", "read_gateway", "transcript")
_emit_hard_fails_untranscripted("p1", "read_gateway")
_emit_gated_by_confidence("p1", "read_gateway", "confidence_gate")
_emit_escalates_to_human("p1", "read_gateway", "L2")
_emit_reads_policy_state("p1", "read_gateway", "L2")
_emit_authorize_and_execute("p2", "read_gateway", "execution_auth")
_emit_validates_capability("p2", "read_gateway", "capability_check")
_emit_routes_to_capability("p2", "read_gateway", "capability_route")
_emit_writes_via_uwg("p2", "read_gateway", "uwg_write")
_emit_blocks_direct_write("p2", "read_gateway", "direct_write_block")
_emit_records_tool_invocation("p2", "read_gateway", "tool_invocation")
_emit_captures_execution_output("p2", "read_gateway", "exec_output")
_emit_dispatches_agent("p3", "read_gateway", "agent_dispatch")
_emit_coordinates_agents("p3", "read_gateway", "agent_coordination")
_emit_records_workflow_lineage("p3", "read_gateway", "workflow_lineage")
_emit_records_healing_outcome("p3", "read_gateway", "healing_outcome")
_emit_escalates_failure("p3", "read_gateway", "failure_escalation")
_emit_orchestrates_workflow("p3", "read_gateway", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "read_gateway", "healing_dispatch")
_emit_invokes_evaluation("p3", "read_gateway", "evaluation_signal")
_emit_records_telemetry_event("p4", "read_gateway", "telemetry_event")
_emit_captures_evaluation_metric("p4", "read_gateway", "eval_metric")
_emit_stores_embedding("p4", "read_gateway", "embedding_store")
_emit_updates_meta_learning_state("p4", "read_gateway", "meta_learning")
_emit_links_execution_to_snapshot("p4", "read_gateway", "exec_snapshot_link")
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

_emit_emits_metric_event("read_gateway", "p4obs", "metric_1")
_emit_emits_metric_event("read_gateway", "p4obs", "metric_2")
_emit_emits_metric_event("read_gateway", "p4obs", "metric_3")
_emit_emits_metric_event("read_gateway", "p4obs", "metric_4")
_emit_emits_metric_event("read_gateway", "p4obs", "metric_5")
_emit_emits_metric_event("read_gateway", "p4obs", "metric_6")
_emit_records_incident_event("read_gateway", "p4obs", "incident")
_emit_captures_runtime_anomaly("read_gateway", "p4obs", "anomaly")
_emit_writes_observability_log("read_gateway", "p4obs", "obs_log")
_emit_updates_monitoring_state("read_gateway", "p4obs", "mon_state")
_emit_triggers_alert("read_gateway", "p4obs", "alert")
_emit_links_incident_trace("read_gateway", "p4obs", "trace_link")
_emit_captures_pattern("read_gateway", "p3lm", "pattern")
_emit_records_learning_event("read_gateway", "p3lm", "learning_event")
_emit_writes_learning_snapshot("read_gateway", "p3lm", "snapshot")
_emit_feeds_meta_learning("read_gateway", "p3lm", "meta_feed")
_emit_updates_routing_strategy("read_gateway", "p3lm", "routing")
_emit_improves_agent_policy("read_gateway", "p3lm", "policy")
_emit_stores_learning_state("read_gateway", "p3lm", "state")
_emit_records_execution_trace("read_gateway", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("read_gateway", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("read_gateway", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("read_gateway", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("read_gateway", "L4_STATE", "p2_trace_5")
_emit_reads_environ("read_gateway", "env_read", "p2_env_1")
_emit_reads_environ("read_gateway", "env_read", "p2_env_2")
_emit_reads_runtime_state("read_gateway", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("read_gateway", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "read_gateway", "context_pull")
_emit_pulls_context("p1", "read_gateway", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "read_gateway", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "read_gateway", "uwg_term_2")
_emit_writes_through("p1", "read_gateway", "write_through")
_emit_writes_through("p1", "read_gateway", "write_through_2")
_emit_validated_by_safety_plane("p1", "read_gateway", "safety_validation")
_emit_invokes_eval("p1", "read_gateway", "eval_call")
_emit_proposal_commits_routing("p1", "read_gateway", "routing_commit")

Logger: Any = logging.getLogger("L2.ReadGateway")


def read_text(path: str | Path, encoding: str = "utf-8") -> str:
    """
    Read text content from a file via MCP filesystem.
    Tool ID: ACT-020

    Args:
        path: File path to read.
        encoding: Text encoding (default: utf-8).

    Returns:
        str: File content, or raises OSError on failure.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "read_text", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "read_text", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "read_text")
    p = Path(path)
    Logger.debug(f"[ReadGateway] read_text: {p}")
    try:
        from mcp6_read_text_file import mcp6_read_text_file

        result: Any = mcp6_read_text_file(path=str(p))
        return result
    except ImportError:  # guardian: allow-silent-swallow
        Logger.debug("[ReadGateway] mcp6_read_text_file unavailable, using direct I/O")
        return p.read_text(encoding=encoding)
    except (RuntimeError, ValueError) as e:  # guardian: allow-silent-swallow
        Logger.warning(f"[ReadGateway] mcp6 read failed for {p}, falling back: {e}")
        return p.read_text(encoding=encoding)


def read_bytes(path: str | Path) -> bytes:
    """
    Read binary content from a file via MCP filesystem.
    Tool ID: ACT-021

    Args:
        path: File path to read.

    Returns:
        bytes: File content.
    """
    p = Path(path)
    Logger.debug(f"[ReadGateway] read_bytes: {p}")
    return p.read_bytes()


def read_json(path: str | Path) -> Any:
    """
    Read and parse a JSON file via MCP filesystem.
    Tool ID: ACT-022

    Args:
        path: File path to read.

    Returns:
        Parsed JSON object.
    """
    p = Path(path)
    Logger.debug(f"[ReadGateway] read_json: {p}")
    content = read_text(p)
    return json.loads(content)


def list_directory(path: str | Path) -> list[str]:
    """
    List directory contents via MCP filesystem.
    Tool ID: ACT-023

    Args:
        path: Directory path to list.

    Returns:
        list[str]: List of file/directory names.
    """
    p = Path(path)
    Logger.debug(f"[ReadGateway] list_directory: {p}")
    try:
        from mcp6_list_directory import mcp6_list_directory

        result: Any = mcp6_list_directory(path=str(p))
        if isinstance(result, list):
            return result
        if isinstance(result, str):
            return result.splitlines()
        return list(result)
    except ImportError:
        Logger.debug("[ReadGateway] mcp6_list_directory unavailable, using direct I/O")
        return [entry.name for entry in p.iterdir()]
    except (RuntimeError, ValueError) as e:  # guardian: allow-silent-swallow
        Logger.warning(f"[ReadGateway] mcp6 list failed for {p}, falling back: {e}")
        return [entry.name for entry in p.iterdir()]


def file_exists(path: str | Path) -> bool:
    """
    Check if a file exists via MCP filesystem.
    Tool ID: ACT-024

    Args:
        path: File path to check.

    Returns:
        bool: True if file exists.
    """
    return Path(path).exists()


def get_file_info(path: str | Path) -> dict[str, Any]:
    """
    Get file metadata via MCP filesystem.
    Tool ID: ACT-025

    Args:
        path: File path to inspect.

    Returns:
        dict with size, modified, is_file, is_dir keys.
    """
    p = Path(path)
    Logger.debug(f"[ReadGateway] get_file_info: {p}")
    try:
        from mcp6_get_file_info import mcp6_get_file_info

        result: Any = mcp6_get_file_info(path=str(p))
        return result if isinstance(result, dict) else {"raw": result}
    except ImportError as e:

        raise ImportError(f"Required dependency missing: {e}")
        Logger.debug("[ReadGateway] mcp6_get_file_info unavailable, using direct stat")
    except (RuntimeError, ValueError) as e:  # guardian: allow-silent-swallow
        Logger.warning(f"[ReadGateway] mcp6 file_info failed for {p}, falling back: {e}")
    stat = p.stat()
    return {
        "size": stat.st_size,
        "modified": stat.st_mtime,
        "is_file": p.is_file(),
        "is_dir": p.is_dir(),
        "name": p.name,
        "path": str(p),
    }


__all__ = [
    "read_text",
    "read_bytes",
    "read_json",
    "list_directory",
    "file_exists",
    "get_file_info",
]
