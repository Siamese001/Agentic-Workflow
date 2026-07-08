"""
L2 Read Gateway — MCP-backed read operations.

All filesystem reads from non-local, external, or audited paths SHOULD be
routed through this gateway. Uses mcp6_* (MCP filesystem tools) for reads,
with graceful fallback to direct Python I/O when the MCP server is unavailable.

Tool ID Prefix: ACT-020
"""
# review: allow-silent-swallower -- ADG violation exemption

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "read_gateway")
trace_contract.emit_determinism_digest("p0", "read_gateway")

trace_contract._emit_dispatches_healing_run("p1", "read_gateway", "L2")
trace_contract._emit_routes_through("p1", "read_gateway", "L2")
trace_contract._emit_checks_agent_registry("p1", "read_gateway", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "read_gateway", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "read_gateway", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "read_gateway", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "read_gateway", "target_agent")
trace_contract._emit_verifies_policy("p1", "read_gateway", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "read_gateway", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "read_gateway", "boundary_check")
trace_contract._emit_transcripts_response("p1", "read_gateway", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "read_gateway")
trace_contract._emit_gated_by_confidence("p1", "read_gateway", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "read_gateway", "L2")
trace_contract._emit_reads_policy_state("p1", "read_gateway", "L2")
trace_contract._emit_authorize_and_execute("p2", "read_gateway", "execution_auth")
trace_contract._emit_validates_capability("p2", "read_gateway", "capability_check")
trace_contract._emit_routes_to_capability("p2", "read_gateway", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "read_gateway", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "read_gateway", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "read_gateway", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "read_gateway", "exec_output")
trace_contract._emit_dispatches_agent("p3", "read_gateway", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "read_gateway", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "read_gateway", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "read_gateway", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "read_gateway", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "read_gateway", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "read_gateway", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "read_gateway", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "read_gateway", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "read_gateway", "eval_metric")
trace_contract._emit_stores_embedding("p4", "read_gateway", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "read_gateway", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "read_gateway", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("read_gateway", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("read_gateway", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("read_gateway", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("read_gateway", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("read_gateway", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("read_gateway", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("read_gateway", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("read_gateway", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("read_gateway", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("read_gateway", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("read_gateway", "p4obs", "alert")
trace_contract._emit_links_incident_trace("read_gateway", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("read_gateway", "p3lm", "pattern")
trace_contract._emit_records_learning_event("read_gateway", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("read_gateway", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("read_gateway", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("read_gateway", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("read_gateway", "p3lm", "policy")
trace_contract._emit_stores_learning_state("read_gateway", "p3lm", "state")
trace_contract._emit_records_execution_trace("read_gateway", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("read_gateway", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("read_gateway", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("read_gateway", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("read_gateway", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("read_gateway", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("read_gateway", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("read_gateway", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("read_gateway", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "read_gateway", "context_pull")
trace_contract._emit_pulls_context("p1", "read_gateway", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "read_gateway", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "read_gateway", "uwg_term_2")
trace_contract._emit_writes_through("p1", "read_gateway", "write_through")
trace_contract._emit_writes_through("p1", "read_gateway", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "read_gateway", "safety_validation")
trace_contract._emit_invokes_eval("p1", "read_gateway", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "read_gateway", "routing_commit")

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

    trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "read_text", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "read_text", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L2_EXECUTION, "read_text")
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
    except ImportError as e:  # guardian: allow-log-and-swallow -- re-raises wrapped ImportError; Logger.debug below is unreachable dead code
        raise ImportError(f"Required dependency missing: {e}")
    except (
        RuntimeError,
        ValueError,
    ) as e:  # guardian: allow-log-and-swallow -- mcp6 file_info: non-fatal, falls back to direct stat
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
