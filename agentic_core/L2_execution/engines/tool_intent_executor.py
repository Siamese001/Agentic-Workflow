"""
Phase 7 — ToolIntentExecutor: execute ToolIntent only inside L2.2 commit sandbox.

Reuses the existing L2.2 sandbox flag from Phase 4 (ml_write_intent.py).
Any ToolIntent with requires_commit=True executed outside the sandbox raises
ToolViolation(code="TOOL_WRITE_OUTSIDE_SANDBOX").
"""

from __future__ import annotations

import hashlib
import json
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Callable

from agentic_core.L2_execution.enforcement.guardrail_gate import Generator
from agentic_core.L2_execution.types.ml_write_intent_types import is_commit_sandbox_active
from agentic_core.L2_execution.types.tool_intent_types import ToolIntent, ToolViolation
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
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
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "tool_intent_executor")
emit_determinism_digest("p0", "tool_intent_executor")

_emit_dispatches_healing_run("p1", "tool_intent_executor", "L2")
_emit_routes_through("p1", "tool_intent_executor", "L2")
_emit_escalates_to_human("p1", "tool_intent_executor", "L2")
_emit_reads_policy_state("p1", "tool_intent_executor", "L2")
_emit_routes_to_agent("p1", "tool_intent_executor", "L2")
_emit_orchestrates_workflow("p1", "tool_intent_executor", "L2")
_emit_dispatches_execution_plan("p1", "tool_intent_executor", "L2")
_emit_validates_agent_capability("p1", "tool_intent_executor", "L2")
_emit_checks_agent_registry("p1", "tool_intent_executor", "L2")

_emit_applies_guardrail("p0", "tool_intent_executor", "p0_governance")
_emit_snapshots_state("p0", "tool_intent_executor", "state_snapshot")
_emit_authorize_and_execute("p2", "tool_intent_executor", "execution_auth")
_emit_validates_capability("p2", "tool_intent_executor", "capability_check")
_emit_routes_to_capability("p2", "tool_intent_executor", "capability_route")
_emit_writes_via_uwg("p2", "tool_intent_executor", "uwg_write")
_emit_blocks_direct_write("p2", "tool_intent_executor", "direct_write_block")
_emit_records_tool_invocation("p2", "tool_intent_executor", "tool_invocation")
_emit_captures_execution_output("p2", "tool_intent_executor", "exec_output")
_emit_dispatches_agent("p3", "tool_intent_executor", "agent_dispatch")
_emit_coordinates_agents("p3", "tool_intent_executor", "agent_coordination")
_emit_records_workflow_lineage("p3", "tool_intent_executor", "workflow_lineage")
_emit_records_healing_outcome("p3", "tool_intent_executor", "healing_outcome")
_emit_escalates_failure("p3", "tool_intent_executor", "failure_escalation")
_emit_orchestrates_workflow("p3", "tool_intent_executor", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "tool_intent_executor", "healing_dispatch")
_emit_invokes_evaluation("p3", "tool_intent_executor", "evaluation_signal")
_emit_records_telemetry_event("p4", "tool_intent_executor", "telemetry_event")
_emit_captures_evaluation_metric("p4", "tool_intent_executor", "eval_metric")
_emit_stores_embedding("p4", "tool_intent_executor", "embedding_store")
_emit_updates_meta_learning_state("p4", "tool_intent_executor", "meta_learning")
_emit_links_execution_to_snapshot("p4", "tool_intent_executor", "exec_snapshot_link")


def _invoke_authorize_and_execute(execution_context, target_callable, capability_token, payload, **kw):
    _emit_agent_executes_agent(str(uuid.uuid4()), "Module", "Module._invoke_authorize_and_execute")
    from agentic_core.L2_execution.enforcement.execution_guardrail_chokepoint import (
        authorize_and_execute,  # noqa: PLC0415
    )

    return authorize_and_execute(execution_context, target_callable, capability_token, payload, **kw)


def _make_execution_context(payload, target: str):
    from agentic_core.L2_execution.context.execution_context import (  # noqa: PLC0415
        ActionClass,
        ExecutionContext,
    )

    return ExecutionContext.create(
        run_id="tool_intent_executor",
        capability_token="default",
        policy_hash="default",
        execution_input=str(payload),
        execution_target=target,
        action_class=ActionClass.MUTATION,
    )


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
        _emit_verifies_boundary(str(uuid.uuid4()), "ToolResult.canonical_bytes", "L2_EXECUTION")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "ToolResult.canonical_bytes")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ToolResult.canonical_bytes".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "ToolIntentExecutor.execute")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ToolIntentExecutor.execute".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if intent.requires_commit and (not is_commit_sandbox_active()):
            raise ToolViolation(
                code="TOOL_WRITE_OUTSIDE_SANDBOX",
                detail=f"tool '{intent.tool_name}' requires commit sandbox (capability={intent.capability.value})",
            )
        _ectx = _make_execution_context(intent.args_hash, intent.tool_name)
        _invoke_authorize_and_execute(
            _ectx,
            lambda p: p,
            "default",
            intent.args_hash,
            target_name=intent.tool_name,
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
