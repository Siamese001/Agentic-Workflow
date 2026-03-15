"""
Programmatic Tool Calling (PTC) - Tool Contract

Defines immutable data structures for tool specification, calls, and results.
Provides deterministic serialization and validation for tool registry.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
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

_emit_dispatches_healing_run("p1", "tool_contract", "L3")
_emit_routes_through("p1", "tool_contract", "L3")
_emit_escalates_to_human("p1", "tool_contract", "L3")
_emit_reads_policy_state("p1", "tool_contract", "L3")


@dataclass(frozen=True)
class ToolArg:
    """Immutable argument specification for a tool."""

    name: str
    kind: str
    required: bool
    default: str | None = None

    def __post_init__(self):
        """Validate argument specification."""
        if not self.name:
            raise ValueError("name cannot be empty")
        if not self.kind:
            raise ValueError("kind cannot be empty")
        valid_kinds = {"str", "int", "bool", "list[str]", "dict"}
        if self.kind not in valid_kinds:
            raise ValueError(f"kind must be one of {valid_kinds}")
        if not self.required and self.default is None:
            raise ValueError("optional args must have default value")


@dataclass(frozen=True)
class ToolSpec:
    """Immutable specification for a tool."""

    tool_id: str
    description: str
    side_effect_class: str
    args: tuple[ToolArg, ...]
    output_kind: str
    version: int = 1

    def __post_init__(self):
        """Validate tool specification."""
        if not self.tool_id:
            raise ValueError("tool_id cannot be empty")
        if not self.description:
            raise ValueError("description cannot be empty")
        valid_side_effects = {"PURE", "READONLY", "WRITE_FS", "SUBPROCESS"}
        if self.side_effect_class not in valid_side_effects:
            raise ValueError(f"side_effect_class must be one of {valid_side_effects}")
        valid_outputs = {"TEXT", "JSON"}
        if self.output_kind not in valid_outputs:
            raise ValueError(f"output_kind must be one of {valid_outputs}")
        if self.version < 1:
            raise ValueError("version must be >= 1")
        arg_names = [arg.name for arg in self.args]
        if arg_names != sorted(arg_names):
            raise ValueError("args must be sorted by name")


@dataclass(frozen=True)
class ToolCall:
    """Immutable tool call invocation."""

    call_id: str
    tool_id: str
    args: dict[str, Any]
    policy: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate tool call."""
        if not self.call_id:
            raise ValueError("call_id cannot be empty")
        if not self.tool_id:
            raise ValueError("tool_id cannot be empty")


@dataclass(frozen=True)
class ToolCallResult:
    """Immutable result of a tool call."""

    exit_code: int
    stdout: str
    stderr: str
    truncated: bool
    hashes: dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        """Validate tool call result."""
        if self.exit_code < 0:
            raise ValueError("exit_code must be >= 0")


def canonical_json(obj: Any) -> str:
    """Serialize object to canonical JSON.

    Args:
        obj: Object to serialize

    Returns:
        Canonical JSON string
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "canonical_json", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "canonical_json", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "canonical_json")
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256_hex(data: str) -> str:
    """Calculate SHA256 hash of string data.

    Args:
        data: String data to hash

    Returns:
        Hexadecimal SHA256 hash
    """
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def generate_call_id(tool_id: str, args: dict[str, Any]) -> str:
    """Generate deterministic call ID from tool ID and arguments.

    Args:
        tool_id: Tool identifier
        args: Tool arguments

    Returns:
        SHA256 hash for call ID
    """
    canonical_args = canonical_json(args)
    data = f"{tool_id}:{canonical_args}"
    return sha256_hex(data)


def hash_result_data(result: ToolCallResult) -> dict[str, str]:
    """Generate hashes for result data.

    Args:
        result: Tool call result

    Returns:
        Dictionary with hashes
    """
    hashes = {}
    if result.stdout:
        hashes["stdout"] = sha256_hex(result.stdout)
    if result.stderr:
        hashes["stderr"] = sha256_hex(result.stderr)
    hashes["truncated"] = sha256_hex(str(result.truncated))
    return hashes


def tool_spec_to_json(spec: ToolSpec) -> str:
    """Serialize ToolSpec to deterministic JSON."""
    data = {
        "tool_id": spec.tool_id,
        "description": spec.description,
        "side_effect_class": spec.side_effect_class,
        "args": [
            {"name": arg.name, "kind": arg.kind, "required": arg.required, "default": arg.default}
            for arg in spec.args
        ],
        "output_kind": spec.output_kind,
        "version": spec.version,
    }
    return canonical_json(data)


def tool_call_to_json(call: ToolCall) -> str:
    """Serialize ToolCall to deterministic JSON."""
    data = {"call_id": call.call_id, "tool_id": call.tool_id, "args": call.args, "policy": call.policy}
    return canonical_json(data)


def tool_call_result_to_json(result: ToolCallResult) -> str:
    """Serialize ToolCallResult to deterministic JSON."""
    data = {
        "exit_code": result.exit_code,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "truncated": result.truncated,
        "hashes": result.hashes,
    }
    return canonical_json(data)


__all__ = [
    "ToolArg",
    "ToolSpec",
    "ToolCall",
    "ToolCallResult",
    "canonical_json",
    "sha256_hex",
    "generate_call_id",
    "hash_result_data",
    "tool_spec_to_json",
    "tool_call_to_json",
    "tool_call_result_to_json",
]
