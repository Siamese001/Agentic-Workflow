"""
Phase 7 — ToolIntentExecutor: execute ToolIntent only inside L2.2 commit sandbox.

Reuses the existing L2.2 sandbox flag from Phase 4 (ml_write_intent.py).
Any ToolIntent with requires_commit=True executed outside the sandbox raises
ToolViolation(code="TOOL_WRITE_OUTSIDE_SANDBOX").
"""

from __future__ import annotations

import hashlib
import json
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Callable
from agentic_core.L2_execution.enforcement.guardrail_gate import get_guardrail_gate, Generator

from agentic_core.L2_execution.types.ml_write_intent_types import is_commit_sandbox_active
from agentic_core.L2_execution.types.tool_intent_types import ToolIntent, ToolViolation

_SCHEMA_VERSION: int = 1


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass
class ToolResult:
    """
    Typed result of a ToolIntent execution.

    Fields
    ------
    schema_version : int   — bumped on breaking changes
    tool_name      : str   — matches the originating ToolIntent.tool_name
    args_hash      : str   — matches the originating ToolIntent.args_hash
    success        : bool  — True if execution completed without error
    output_summary : str   — deterministic string summary of the output
    anchor_ids     : list  — chunk_ids of any retrieved content (may be empty)
    result_hash    : str   — sha256(canonical_bytes excluding result_hash)
    """

    schema_version: int
    tool_name: str
    args_hash: str
    success: bool
    output_summary: str
    anchor_ids: list[str]
    result_hash: str = field(default="", init=False)

    def __post_init__(self) -> None:
        if self.schema_version != _SCHEMA_VERSION:
            raise ValueError(
                f"ToolResult: schema_version must be {_SCHEMA_VERSION}, got {self.schema_version!r}"
            )
        if not self.tool_name:
            raise ValueError("ToolResult: tool_name must be non-empty")
        if not self.args_hash:
            raise ValueError("ToolResult: args_hash must be non-empty")
        if not isinstance(self.anchor_ids, list):
            raise TypeError("ToolResult: anchor_ids must be a list")
        self.anchor_ids = sorted(self.anchor_ids)
        object.__setattr__(self, "result_hash", _sha256(self.canonical_bytes()))

    def canonical_bytes(self) -> bytes:
        """Deterministic serialisation excluding result_hash (self-referential)."""
        doc: dict[str, Any] = {
            "anchor_ids": sorted(self.anchor_ids),
            "args_hash": self.args_hash,
            "output_summary": self.output_summary,
            "schema_version": self.schema_version,
            "success": self.success,
            "tool_name": self.tool_name,
        }
        return json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "tool_name": self.tool_name,
            "args_hash": self.args_hash,
            "success": self.success,
            "output_summary": self.output_summary,
            "anchor_ids": list(self.anchor_ids),
            "result_hash": self.result_hash,
        }


class ToolIntentExecutor:
    """
    Executes a ToolIntent inside the L2.2 commit sandbox.

    Usage
    -----
    with ToolIntentExecutor() as executor:
        result = executor.execute(intent, fn=my_tool_fn)

    Guarantees
    ----------
    - If intent.requires_commit and sandbox not active → ToolViolation("TOOL_WRITE_OUTSIDE_SANDBOX")
    - Non-mutating intents (requires_commit=False) may be executed anywhere.
    - fn is called with intent.args; must return a dict with at least "output_summary".
    """

    @contextmanager
    def __enter__(self) -> Generator[ToolIntentExecutor, None, None]:
        yield self

    def __exit__(self, *args: Any) -> None:
        pass

    def execute(self, intent: ToolIntent, fn: Callable[[dict[str, Any]], dict[str, Any]]) -> ToolResult:
        """
        Execute a ToolIntent.

        Parameters
        ----------
        intent : ToolIntent
        fn     : callable(args: dict) -> dict
            Must return a dict with at least "output_summary" (str) and
            optionally "anchor_ids" (list[str]).

        Raises
        ------
        ToolViolation(code="TOOL_WRITE_OUTSIDE_SANDBOX")
            If intent.requires_commit and sandbox is not active.
        """
        if intent.requires_commit and (not is_commit_sandbox_active()):
            raise ToolViolation(
                code="TOOL_WRITE_OUTSIDE_SANDBOX",
                detail=f"tool '{intent.tool_name}' requires commit sandbox (capability={intent.capability.value})",
            )
        raw = fn(intent.args)
        output_summary = str(raw.get("output_summary", ""))
        anchor_ids: list[str] = list(raw.get("anchor_ids", []))
        return ToolResult(
            schema_version=_SCHEMA_VERSION,
            tool_name=intent.tool_name,
            args_hash=intent.args_hash,
            success=raw.get("success", True),
            output_summary=output_summary,
            anchor_ids=anchor_ids,
        )
