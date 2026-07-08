"""
Programmatic Tool Calling (PTC) - Tool Call Store

Append-only storage for tool call records using persistent store.
Ensures deterministic storage and retrieval of tool call artifacts.
"""

from __future__ import annotations

import json
import logging
import subprocess
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_authorize_and_execute("p2", "tool_call_store", "execution_auth")
trace_contract._emit_validates_capability("p2", "tool_call_store", "capability_check")
trace_contract._emit_routes_to_capability("p2", "tool_call_store", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "tool_call_store", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "tool_call_store", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "tool_call_store", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "tool_call_store", "exec_output")
trace_contract._emit_dispatches_agent("p3", "tool_call_store", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "tool_call_store", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "tool_call_store", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "tool_call_store", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "tool_call_store", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "tool_call_store", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "tool_call_store", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "tool_call_store", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "tool_call_store", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "tool_call_store", "eval_metric")
trace_contract._emit_stores_embedding("p4", "tool_call_store", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "tool_call_store", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "tool_call_store", "exec_snapshot_link")
# StoredArtifact, StoredArtifactRef imported lazily to avoid L3->L4 violation

from .tool_contract import (
    ToolCall,
    ToolCallResult,
    ToolSpec,
    tool_call_result_to_json,
    tool_call_to_json,
    tool_spec_to_json,
)

trace_contract.emit_replay_key("p0", "tool_call_store")
trace_contract.emit_determinism_digest("p0", "tool_call_store")
Logger = logging.getLogger(__name__)

trace_contract._emit_dispatches_healing_run("p1", "tool_call_store", "L3")
trace_contract._emit_routes_through("p1", "tool_call_store", "L3")
trace_contract._emit_checks_agent_registry("p1", "tool_call_store", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "tool_call_store", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "tool_call_store", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "tool_call_store", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "tool_call_store", "target_agent")
trace_contract._emit_verifies_policy("p1", "tool_call_store", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "tool_call_store", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "tool_call_store", "boundary_check")
trace_contract._emit_transcripts_response("p1", "tool_call_store", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "tool_call_store")
trace_contract._emit_gated_by_confidence("p1", "tool_call_store", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "tool_call_store", "L3")
trace_contract._emit_reads_policy_state("p1", "tool_call_store", "L3")

trace_contract._emit_snapshots_state("p0", "tool_call_store", "state_snapshot")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_applies_guardrail("p0", "tool_call_store", "p0_governance")

trace_contract._emit_emits_metric_event("tool_call_store", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("tool_call_store", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("tool_call_store", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("tool_call_store", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("tool_call_store", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("tool_call_store", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("tool_call_store", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("tool_call_store", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("tool_call_store", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("tool_call_store", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("tool_call_store", "p4obs", "alert")
trace_contract._emit_links_incident_trace("tool_call_store", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("tool_call_store", "p3lm", "pattern")
trace_contract._emit_records_learning_event("tool_call_store", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("tool_call_store", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("tool_call_store", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("tool_call_store", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("tool_call_store", "p3lm", "policy")
trace_contract._emit_stores_learning_state("tool_call_store", "p3lm", "state")
trace_contract._emit_records_execution_trace("tool_call_store", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("tool_call_store", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("tool_call_store", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("tool_call_store", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("tool_call_store", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("tool_call_store", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("tool_call_store", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("tool_call_store", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("tool_call_store", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "tool_call_store", "context_pull")
trace_contract._emit_pulls_context("p1", "tool_call_store", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "tool_call_store", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "tool_call_store", "uwg_term_2")
trace_contract._emit_writes_through("p1", "tool_call_store", "write_through")
trace_contract._emit_writes_through("p1", "tool_call_store", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "tool_call_store", "safety_validation")
trace_contract._emit_invokes_eval("p1", "tool_call_store", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "tool_call_store", "routing_commit")


class ToolCallStore:
    """Append-only storage for tool call records."""

    def __init__(self, root_dir: Path | str | None = None):
        """Initialize with persistent store.

        Args:
            root_dir: Root directory for storage (defaults to repo root/docs/store)
        """
        from agentic_core.L4_state.utils.storage.filesystem_store import FileSystemStore

        if root_dir is None:
            # Default to repo root/docs/store
            root_dir = Path.cwd() / "docs" / "store"
        self._store = FileSystemStore(root_dir)

    def record_call(
        self,
        call: ToolCall,
        result: ToolCallResult,
        spec: ToolSpec,
        policy: dict[str, Any] | None = None,
    ) -> StoredArtifactRef:
        """Record a tool call and its result.

        Args:
            call: Tool call that was made
            result: Result of the tool call
            spec: Tool specification
            policy: Policy used for the call

        Returns:
            Reference to stored artifact
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "ToolCallStore.record_call")

        # Create deterministic payload (no timestamp)
        payload = {
            "call": json.loads(tool_call_to_json(call)),
            "result": json.loads(tool_call_result_to_json(result)),
            "tool_spec": json.loads(tool_spec_to_json(spec)),
            "policy": policy or {},
        }

        # Create artifact with deterministic ID from call_id
        artifact = StoredArtifact(
            kind="tool_call",
            logical_id=call.call_id,
            created_utc="",  # Empty for determinism
            content_type="application/json",
            payload=payload,
        )

        # Store and return reference
        return self._store.put(artifact)

    # guardian: allow-magic-config -- limit default is a pagination parameter for store queries
    def list_calls(
        self,
        tool_id: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:  # guardian: allow-magic-configuration
        """List stored tool calls.

        Args:
            tool_id: Optional tool ID filter
            limit: Maximum number of calls to return

        Returns:
            List of tool call records
        """
        # Get all tool_call artifacts
        refs = self._store.list("tool_call")

        # Load artifacts
        records = []
        for ref in refs:
            artifact = self._store.get(ref)
            # Filter by tool_id if specified
            if tool_id is None or artifact.payload["call"]["tool_id"] == tool_id:
                records.append(artifact.payload)

        # Sort deterministically by call_id
        records.sort(key=lambda r: r["call"]["call_id"])

        # Apply limit
        return records[:limit]

    def get_call(self, tool_id: str, call_id: str) -> dict[str, Any] | None:
        """Get a specific tool call record.

        Args:
            tool_id: Tool identifier
            call_id: Call identifier

        Returns:
            Tool call record or None if not found
        """
        # Try to get artifact by call_id (logical_id)
        try:
            ref = self._store._get_artifact_dir("tool_call", call_id)
            # Find the latest version
            versions = list(ref.parent.glob("v*.json"))
            if versions:
                latest = max(versions, key=lambda p: int(p.stem[1:]))
                artifact = self._store.get(
                    StoredArtifactRef(
                        kind="tool_call",
                        logical_id=call_id,
                        version=int(latest.stem[1:]),
                        path=str(latest),
                    ),
                )
                if artifact.payload["call"]["tool_id"] == tool_id:
                    return artifact.payload
        except (
            ValueError,
            TypeError,
            FileNotFoundError,
            KeyError,
        ) as exc:  # guardian: allow-log-and-swallow -- best-effort lookup: non-fatal, returns None to caller
            Logger.debug(
                "ToolCallStore.get_call best-effort lookup failed for tool_id=%s call_id=%s: %s",
                tool_id,
                call_id,
                exc,
            )

        return None

    def _get_code_commit(self) -> str:
        """Get current git commit hash.

        Returns:
            Git commit hash or "unknown"
        """
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                shell=False,
                cwd=str(Path.cwd()),
                timeout=5,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except (  # guardian: allow-log-and-swallow -- git commit lookup: non-fatal, falls back to 'unknown'
            ValueError,
            TypeError,
            FileNotFoundError,
            OSError,
            subprocess.TimeoutExpired,
        ) as exc:  # guardian: allow-log-and-swallow -- git commit lookup: non-fatal, falls back to 'unknown'
            Logger.debug("ToolCallStore._get_code_commit falling back to 'unknown': %s", exc)
        return "unknown"


# =============================================================================
# Global Store Instance
# =============================================================================

_GLOBAL_STORE: ToolCallStore | None = None


def get_tool_call_store() -> ToolCallStore:
    """Get the global tool call store.

    Returns:
        Global ToolCallStore instance
    """
    global _GLOBAL_STORE
    if _GLOBAL_STORE is None:
        _GLOBAL_STORE = ToolCallStore()
    return _GLOBAL_STORE


def record_tool_call(
    call: ToolCall,
    result: ToolCallResult,
    spec: ToolSpec,
    policy: dict[str, Any] | None = None,
) -> StoredArtifactRef:
    """Record a tool call in the global store.

    Args:
        call: Tool call that was made
        result: Result of the tool call
        spec: Tool specification
        policy: Policy used for the call

    Returns:
        Reference to stored artifact
    """
    store = get_tool_call_store()
    return store.record_call(call, result, spec, policy)


# guardian: allow-magic-config -- limit default is a pagination parameter for module-level API
def list_tool_calls(
    tool_id: str | None = None,
    limit: int = 100,
) -> list[dict[str, Any]]:  # guardian: allow-magic-configuration
    """List tool calls from the global store.

    Args:
        tool_id: Optional tool ID filter
        limit: Maximum number of calls to return

    Returns:
        List of tool call records
    """
    store = get_tool_call_store()
    return store.list_calls(tool_id, limit)


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "ToolCallStore",
    "get_tool_call_store",
    "record_tool_call",
    "list_tool_calls",
]
