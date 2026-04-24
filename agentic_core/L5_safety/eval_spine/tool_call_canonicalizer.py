"""Canonical tool-call shape and args-hash computation.

Per ADR-037 §2.3, a predicted/reference tool-call record is:

    {"tool": "<canonical_tool_name>", "args_hash": "<sha256_hex>"}

Two records are equivalent iff both fields match.

Canonicalization rules:
  1. Strip volatile fields: ``timestamp``, ``request_id``, ``trace_id``,
     ``span_id``, ``parent_span_id``, ``session_id``.
  2. Sort object keys recursively (JSON Canonicalization Scheme-style).
  3. Serialize with ``separators=(',', ':')``, ``ensure_ascii=False``,
     ``allow_nan=False``, ``sort_keys=True``.
  4. sha256 the UTF-8 bytes, hex-encode.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Final, Mapping

_VOLATILE_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "timestamp",
        "time",
        "t_utc",
        "request_id",
        "trace_id",
        "span_id",
        "parent_span_id",
        "session_id",
    }
)


def _strip_volatile(obj: Any) -> Any:
    """Recursively strip volatile fields from a JSON-like object."""
    if isinstance(obj, Mapping):
        return {
            key: _strip_volatile(value)
            for key, value in obj.items()
            if key not in _VOLATILE_FIELDS
        }
    if isinstance(obj, list):
        return [_strip_volatile(item) for item in obj]
    if isinstance(obj, tuple):
        return [_strip_volatile(item) for item in obj]
    return obj


def canonical_args_json(args: Any) -> str:
    """Return the canonical JSON string for ``args`` per §2.3 rules."""
    stripped = _strip_volatile(args)
    return json.dumps(
        stripped,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def args_hash(args: Any) -> str:
    """Return sha256 hex digest of the canonical args JSON."""
    payload = canonical_args_json(args).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def canonicalize_tool_call(tool: str, args: Any) -> dict[str, str]:
    """Build the canonical record for a tool invocation.

    Parameters
    ----------
    tool:
        Canonical tool name from the MCP / sovereign-gateway registry.
        No aliases — callers must resolve aliases before calling.
    args:
        Raw args dict (or any JSON-serializable value) passed to the tool.

    Returns
    -------
    dict[str, str]
        ``{"tool": tool, "args_hash": "<sha256_hex>"}``

    Raises
    ------
    TypeError
        If ``tool`` is not a non-empty string.
    ValueError
        If ``args`` is not JSON-serializable under the canonical rules.
    """
    if not isinstance(tool, str) or not tool:
        raise TypeError(f"tool must be a non-empty string, got {tool!r}")
    try:
        hash_hex = args_hash(args)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"args not canonicalizable: {exc}") from exc
    return {"tool": tool, "args_hash": hash_hex}


__all__ = [
    "canonical_args_json",
    "args_hash",
    "canonicalize_tool_call",
]
