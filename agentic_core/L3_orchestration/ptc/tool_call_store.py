"""
Programmatic Tool Calling (PTC) - Tool Call Store

Append-only storage for tool call records using in-memory store.
Ensures deterministic storage and retrieval of tool call artifacts.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from .tool_contract import (
    ToolCall,
    ToolCallResult,
    ToolSpec,
    tool_call_result_to_json,
    tool_call_to_json,
    tool_spec_to_json,
)


class ToolCallStore:
    """Append-only storage for tool call records."""

    def __init__(self):
        """Initialize with in-memory store."""
        self._store: list[dict[str, Any]] = []

    def record_call(
        self,
        call: ToolCall,
        result: ToolCallResult,
        spec: ToolSpec,
        policy: dict[str, Any] | None = None,
    ) -> None:
        """Record a tool call and its result.

        Args:
            call: Tool call that was made
            result: Result of the tool call
            spec: Tool specification
            policy: Policy used for the call
        """
        # Create payload
        payload = {
            "call": json.loads(tool_call_to_json(call)),
            "result": json.loads(tool_call_result_to_json(result)),
            "tool_spec": json.loads(tool_spec_to_json(spec)),
            "policy": policy or {},
            "timestamp": datetime.utcnow().isoformat() + "Z",  # UTC timestamp
        }

        # Store in memory
        self._store.append(payload)

    def list_calls(self, tool_id: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        """List stored tool calls.

        Args:
            tool_id: Optional tool ID filter
            limit: Maximum number of calls to return

        Returns:
            List of tool call records
        """
        # Filter by tool_id if specified
        if tool_id:
            filtered = [r for r in self._store if r["call"]["tool_id"] == tool_id]
        else:
            filtered = self._store.copy()

        # Sort deterministically by timestamp and call_id
        filtered.sort(key=lambda r: (r["timestamp"], r["call"]["call_id"]))

        # Apply limit
        return filtered[:limit]

    def get_call(self, tool_id: str, call_id: str) -> dict[str, Any] | None:
        """Get a specific tool call record.

        Args:
            tool_id: Tool identifier
            call_id: Call identifier

        Returns:
            Tool call record or None if not found
        """
        # Find matching call
        for record in self._store:
            if record["call"]["tool_id"] == tool_id and record["call"]["call_id"] == call_id:
                return record

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
) -> None:
    """Record a tool call in the global store.

    Args:
        call: Tool call that was made
        result: Result of the tool call
        spec: Tool specification
        policy: Policy used for the call
    """
    store = get_tool_call_store()
    store.record_call(call, result, spec, policy)


def list_tool_calls(tool_id: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
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
