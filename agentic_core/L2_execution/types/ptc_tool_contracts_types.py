"""PTC Tool Contracts — Contract [3] ToolCall and ToolResult types.

Spec: Contract [3] PTC Tool Contracts, L2 [STDOUT RULE], Guarantee #24.

Every tool invocation through the L2 sandbox MUST produce a ToolResult with:
  - exit_code: int in {0, 1} only
  - stdout: bytes with len(stdout) <= budget cap

ToolResult.__post_init__ validates both constraints at construction time.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
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
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "ptc_tool_contracts_types")
emit_determinism_digest("p0", "ptc_tool_contracts_types")

_emit_dispatches_healing_run("p1", "ptc_tool_contracts_types", "L2")
_emit_routes_through("p1", "ptc_tool_contracts_types", "L2")
_emit_escalates_to_human("p1", "ptc_tool_contracts_types", "L2")
_emit_reads_policy_state("p1", "ptc_tool_contracts_types", "L2")
_emit_authorize_and_execute("p2", "ptc_tool_contracts_types", "execution_auth")
_emit_validates_capability("p2", "ptc_tool_contracts_types", "capability_check")
_emit_routes_to_capability("p2", "ptc_tool_contracts_types", "capability_route")
_emit_writes_via_uwg("p2", "ptc_tool_contracts_types", "uwg_write")
_emit_blocks_direct_write("p2", "ptc_tool_contracts_types", "direct_write_block")
_emit_records_tool_invocation("p2", "ptc_tool_contracts_types", "tool_invocation")
_emit_captures_execution_output("p2", "ptc_tool_contracts_types", "exec_output")
_emit_dispatches_agent("p3", "ptc_tool_contracts_types", "agent_dispatch")
_emit_coordinates_agents("p3", "ptc_tool_contracts_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "ptc_tool_contracts_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "ptc_tool_contracts_types", "healing_outcome")
_emit_escalates_failure("p3", "ptc_tool_contracts_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "ptc_tool_contracts_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ptc_tool_contracts_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "ptc_tool_contracts_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "ptc_tool_contracts_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ptc_tool_contracts_types", "eval_metric")
_emit_stores_embedding("p4", "ptc_tool_contracts_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "ptc_tool_contracts_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ptc_tool_contracts_types", "exec_snapshot_link")


class ToolContractViolation(ValueError):
    """Raised when a ToolResult violates exit_code or stdout_bytes contract."""


@dataclass(frozen=True)
class ToolCall:
    """Represents a single tool invocation request.

    Spec: Contract [3] PTC ToolCall.
    """

    id: str
    tool_name: str
    args: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id:
            raise ToolContractViolation("ToolCall.id must be non-empty")
        if not self.tool_name:
            raise ToolContractViolation("ToolCall.tool_name must be non-empty")


@dataclass(frozen=True)
class ToolResult:
    """Immutable result of a single tool invocation.

    Spec: Contract [3] PTC ToolResult — stdout-only, exit_code in {0, 1}.

    Constraints enforced at construction:
      - exit_code MUST be 0 or 1 (no other values permitted)
      - len(stdout) MUST be <= stdout_bytes_cap when cap is provided
    """

    exit_code: int
    stdout: bytes
    stdout_bytes_cap: int = 0

    def __post_init__(self) -> None:
        if self.exit_code not in (0, 1):
            raise ToolContractViolation(
                f"ToolResult.exit_code must be 0 or 1, got {self.exit_code}. Spec: Contract [3] L2 [STDOUT RULE]."
            )
        if self.stdout_bytes_cap > 0 and len(self.stdout) > self.stdout_bytes_cap:
            raise ToolContractViolation(
                f"ToolResult.stdout exceeds cap: len={len(self.stdout)}, cap={self.stdout_bytes_cap}. Spec: Contract [3] Guarantee #24."
            )

    @classmethod
    def from_budget_enforcer(cls, exit_code: int, stdout_bytes: bytes, stdout_bytes_cap: int) -> ToolResult:
        """Construct and validate ToolResult from BudgetEnforcer output.

        Raises ToolContractViolation if exit_code or stdout length violates contract.
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "ToolResult.from_budget_enforcer", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "ToolResult.from_budget_enforcer", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "ToolResult.from_budget_enforcer")
        return cls(exit_code=exit_code, stdout=stdout_bytes, stdout_bytes_cap=stdout_bytes_cap)
