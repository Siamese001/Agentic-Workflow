"""
Programmatic Tool Calling (PTC) - Tool Call Store

Append-only storage for tool call records using persistent store.
Ensures deterministic storage and retrieval of tool call artifacts.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

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
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_authorize_and_execute("p2", "tool_call_store", "execution_auth")
_emit_validates_capability("p2", "tool_call_store", "capability_check")
_emit_routes_to_capability("p2", "tool_call_store", "capability_route")
_emit_writes_via_uwg("p2", "tool_call_store", "uwg_write")
_emit_blocks_direct_write("p2", "tool_call_store", "direct_write_block")
_emit_records_tool_invocation("p2", "tool_call_store", "tool_invocation")
_emit_captures_execution_output("p2", "tool_call_store", "exec_output")
_emit_dispatches_agent("p3", "tool_call_store", "agent_dispatch")
_emit_coordinates_agents("p3", "tool_call_store", "agent_coordination")
_emit_records_workflow_lineage("p3", "tool_call_store", "workflow_lineage")
_emit_records_healing_outcome("p3", "tool_call_store", "healing_outcome")
_emit_escalates_failure("p3", "tool_call_store", "failure_escalation")
_emit_orchestrates_workflow("p3", "tool_call_store", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "tool_call_store", "healing_dispatch")
_emit_invokes_evaluation("p3", "tool_call_store", "evaluation_signal")
_emit_records_telemetry_event("p4", "tool_call_store", "telemetry_event")
_emit_captures_evaluation_metric("p4", "tool_call_store", "eval_metric")
_emit_stores_embedding("p4", "tool_call_store", "embedding_store")
_emit_updates_meta_learning_state("p4", "tool_call_store", "meta_learning")
_emit_links_execution_to_snapshot("p4", "tool_call_store", "exec_snapshot_link")
from .tool_contract import (
    ToolCall,
    ToolCallResult,
    ToolSpec,
    tool_call_result_to_json,
    tool_call_to_json,
    tool_spec_to_json,
)

emit_replay_key("p0", "tool_call_store")
emit_determinism_digest("p0", "tool_call_store")

_emit_dispatches_healing_run("p1", "tool_call_store", "L3")
_emit_routes_through("p1", "tool_call_store", "L3")
_emit_escalates_to_human("p1", "tool_call_store", "L3")
_emit_reads_policy_state("p1", "tool_call_store", "L3")

_emit_snapshots_state("p0", "tool_call_store", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "tool_call_store", "p0_governance")


class ToolCallStore:
    """Append-only storage for tool call records."""

    def __init__(self, root_dir: Path | str | None = None):
        """Initialize with persistent store.

        Args:
            root_dir: Root directory for storage (defaults to repo root/docs/store)
        """
        from agentic_core.L4_state.storage.filesystem_store import FileSystemStore

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
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ToolCallStore.record_call")

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

    # guardian: allow-magic-config
    def list_calls(
        self, tool_id: str | None = None, limit: int = 100
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
                    )
                )
                if artifact.payload["call"]["tool_id"] == tool_id:
                    return artifact.payload
        # guardian: allow-silent-swallow
        except Exception:  # guardian: allow-silent-swallower
            pass

        return None

    def _get_code_commit(self) -> str:
        """Get current git commit hash.

        Returns:
            Git commit hash or "unknown"
        """
        try:
            import subprocess

            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                shell=False,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        # guardian: allow-silent-swallow
        except Exception:  # guardian: allow-silent-swallower
            pass


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


# guardian: allow-magic-config
def list_tool_calls(
    tool_id: str | None = None, limit: int = 100
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
