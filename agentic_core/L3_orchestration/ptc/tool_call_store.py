"""
Programmatic Tool Calling (PTC) - Tool Call Store

Append-only storage for tool call records using FileSystemStore.
Ensures deterministic storage and retrieval of tool call artifacts.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from ..replay.deterministic_replay import FileSystemStore
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

    def __init__(self, store: FileSystemStore):
        """Initialize with FileSystemStore instance.

        Args:
            store: FileSystemStore for persistent storage
        """
        self.store = store

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
        # Prepare payload
        payload = {
            "call": json.loads(tool_call_to_json(call)),
            "result": json.loads(tool_call_result_to_json(result)),
            "tool_spec": json.loads(tool_spec_to_json(spec)),
            "policy": policy or {},
            "timestamp": datetime.utcnow().isoformat() + "Z",  # UTC timestamp
        }

        # Prepare metadata (allowlist only)
        metadata = {
            "code_commit": self._get_code_commit(),
            "ptc_version": "1.0.0",
            "tool_id": call.tool_id,
            "call_id": call.call_id,
        }

        # Store using FileSystemStore
        self.store.put(
            kind="tool_call",
            logical_id=call.tool_id,
            payload=payload,
            metadata=metadata,
        )

    def list_calls(self, tool_id: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        """List stored tool calls.

        Args:
            tool_id: Optional tool ID filter
            limit: Maximum number of calls to return

        Returns:
            List of tool call records
        """
        # List from FileSystemStore
        refs = self.store.list(kind="tool_call", logical_id=tool_id or "", limit=limit)

        # Retrieve payloads
        records = []
        for ref in refs:
            record = self.store.get(ref["kind"], ref["logical_id"], ref["version"])
            records.append(record.payload)

        # Sort deterministically by timestamp and call_id
        records.sort(key=lambda r: (r["timestamp"], r["call"]["call_id"]))

        return records

    def get_call(self, tool_id: str, call_id: str) -> dict[str, Any] | None:
        """Get a specific tool call record.

        Args:
            tool_id: Tool identifier
            call_id: Call identifier

        Returns:
            Tool call record or None if not found
        """
        # List calls for the tool
        refs = self.store.list(kind="tool_call", logical_id=tool_id, limit=1000)

        # Find matching call
        for ref in refs:
            record = self.store.get(ref["kind"], ref["logical_id"], ref["version"])
            if record.payload["call"]["call_id"] == call_id:
                return record.payload

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
        # Initialize FileSystemStore
        store = FileSystemStore()
        _GLOBAL_STORE = ToolCallStore(store)
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
