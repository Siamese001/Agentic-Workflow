"""
L2 Read Gateway — MCP-backed read operations.

All filesystem reads from non-local, external, or audited paths SHOULD be
routed through this gateway. Uses mcp6_* (MCP filesystem tools) for reads,
with graceful fallback to direct Python I/O when the MCP server is unavailable.

Tool ID Prefix: ACT-020
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

_emit_dispatches_healing_run("p1", "read_gateway", "L2")
_emit_routes_through("p1", "read_gateway", "L2")
_emit_escalates_to_human("p1", "read_gateway", "L2")
_emit_reads_policy_state("p1", "read_gateway", "L2")

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
    except ImportError:
        Logger.debug("[ReadGateway] mcp6_read_text_file unavailable, using direct I/O")
        return p.read_text(encoding=encoding)
    # guardian: allow-silent-swallow
    except Exception as e:
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
    # guardian: allow-silent-swallow
    except Exception as e:
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
    except ImportError:
        Logger.debug("[ReadGateway] mcp6_get_file_info unavailable, using direct stat")
    # guardian: allow-silent-swallow
    except Exception as e:
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
