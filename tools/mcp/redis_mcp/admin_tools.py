"""Bounded invalidation and delete Redis MCP tools."""

from __future__ import annotations

from typing import Any

from .client import safe_connect
from .constants import (
    DELETE_PIPELINE_BATCH_SIZE,
    FLUSH_SAMPLE_SIZE,
    FLUSH_SCAN_CAP,
    FLUSH_SCAN_COUNT,
)
from .scan_utils import scan_keys


def _build_unavailable_response(error: str) -> dict[str, Any]:
    return {"status": "unavailable", "error": error}


def register_admin_tools(mcp: Any) -> None:
    """Register mutating Redis admin tools onto the provided MCP server."""

    @mcp.tool()
    def redis_del_key(key: str) -> dict[str, Any]:
        """DEL a single specific key.

        Intended for targeted cache invalidation.
        """
        client, err = safe_connect()
        if err:
            return _build_unavailable_response(err)

        deleted = client.delete(key)
        return {
            "status": "ok",
            "key": key,
            "existed": bool(deleted),
            "deleted": bool(deleted),
        }

    @mcp.tool()
    def redis_flush_namespace(pattern: str, dry_run: bool = True) -> dict[str, Any]:
        """DEL all keys matching a pattern.

        Defaults to dry_run=True for safety.
        """
        client, err = safe_connect()
        if err:
            return _build_unavailable_response(err)

        scan_result = scan_keys(
            client,
            match=pattern,
            count=FLUSH_SCAN_COUNT,
            scan_cap=FLUSH_SCAN_CAP,
        )
        matching = scan_result.keys

        if dry_run:
            return {
                "status": "ok",
                "dry_run": True,
                "pattern": pattern,
                "matching_count": len(matching),
                "sample": matching[:FLUSH_SAMPLE_SIZE],
                "message": "Set dry_run=False to actually delete",
                "truncated": scan_result.truncated,
            }

        deleted = 0
        if matching:
            pipe = client.pipeline(transaction=False)
            for start_idx in range(0, len(matching), DELETE_PIPELINE_BATCH_SIZE):
                batch = matching[start_idx : start_idx + DELETE_PIPELINE_BATCH_SIZE]
                pipe.delete(*batch)
            results = pipe.execute()
            deleted = sum(results)

        return {
            "status": "ok",
            "dry_run": False,
            "pattern": pattern,
            "deleted_count": deleted,
            "truncated": scan_result.truncated,
        }
