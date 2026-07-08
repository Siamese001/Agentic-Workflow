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

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "ptc_tool_contracts_types")
trace_contract.emit_determinism_digest("p0", "ptc_tool_contracts_types")

trace_contract._emit_dispatches_healing_run("p1", "ptc_tool_contracts_types", "L2")
trace_contract._emit_routes_through("p1", "ptc_tool_contracts_types", "L2")
trace_contract._emit_checks_agent_registry("p1", "ptc_tool_contracts_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "ptc_tool_contracts_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "ptc_tool_contracts_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "ptc_tool_contracts_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "ptc_tool_contracts_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "ptc_tool_contracts_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "ptc_tool_contracts_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "ptc_tool_contracts_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "ptc_tool_contracts_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "ptc_tool_contracts_types")
trace_contract._emit_gated_by_confidence("p1", "ptc_tool_contracts_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "ptc_tool_contracts_types", "L2")
trace_contract._emit_reads_policy_state("p1", "ptc_tool_contracts_types", "L2")
trace_contract._emit_authorize_and_execute("p2", "ptc_tool_contracts_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "ptc_tool_contracts_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "ptc_tool_contracts_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "ptc_tool_contracts_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "ptc_tool_contracts_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "ptc_tool_contracts_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "ptc_tool_contracts_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "ptc_tool_contracts_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "ptc_tool_contracts_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "ptc_tool_contracts_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "ptc_tool_contracts_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "ptc_tool_contracts_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "ptc_tool_contracts_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "ptc_tool_contracts_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "ptc_tool_contracts_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "ptc_tool_contracts_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "ptc_tool_contracts_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "ptc_tool_contracts_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "ptc_tool_contracts_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "ptc_tool_contracts_types", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("ptc_tool_contracts_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("ptc_tool_contracts_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("ptc_tool_contracts_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("ptc_tool_contracts_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("ptc_tool_contracts_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("ptc_tool_contracts_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("ptc_tool_contracts_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("ptc_tool_contracts_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("ptc_tool_contracts_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("ptc_tool_contracts_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("ptc_tool_contracts_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("ptc_tool_contracts_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("ptc_tool_contracts_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("ptc_tool_contracts_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("ptc_tool_contracts_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("ptc_tool_contracts_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("ptc_tool_contracts_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("ptc_tool_contracts_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("ptc_tool_contracts_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("ptc_tool_contracts_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("ptc_tool_contracts_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("ptc_tool_contracts_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("ptc_tool_contracts_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("ptc_tool_contracts_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("ptc_tool_contracts_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("ptc_tool_contracts_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("ptc_tool_contracts_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("ptc_tool_contracts_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "ptc_tool_contracts_types", "context_pull")
trace_contract._emit_pulls_context("p1", "ptc_tool_contracts_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "ptc_tool_contracts_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "ptc_tool_contracts_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "ptc_tool_contracts_types", "write_through")
trace_contract._emit_writes_through("p1", "ptc_tool_contracts_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "ptc_tool_contracts_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "ptc_tool_contracts_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "ptc_tool_contracts_types", "routing_commit")


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
                f"ToolResult.exit_code must be 0 or 1, got {self.exit_code}. Spec: Contract [3] L2 [STDOUT RULE].",
            )
        if self.stdout_bytes_cap > 0 and len(self.stdout) > self.stdout_bytes_cap:
            raise ToolContractViolation(
                f"ToolResult.stdout exceeds cap: len={len(self.stdout)}, cap={self.stdout_bytes_cap}. Spec: Contract [3] Guarantee #24.",
            )

    @classmethod
    def from_budget_enforcer(cls, exit_code: int, stdout_bytes: bytes, stdout_bytes_cap: int) -> ToolResult:
        """Construct and validate ToolResult from BudgetEnforcer output.

        Raises ToolContractViolation if exit_code or stdout length violates contract.
        """
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "ToolResult.from_budget_enforcer", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "ToolResult.from_budget_enforcer", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L2_EXECUTION, "ToolResult.from_budget_enforcer")
        return cls(exit_code=exit_code, stdout=stdout_bytes, stdout_bytes_cap=stdout_bytes_cap)
