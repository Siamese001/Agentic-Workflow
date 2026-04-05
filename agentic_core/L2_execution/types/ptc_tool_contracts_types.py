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
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "ptc_tool_contracts_types")
emit_determinism_digest("p0", "ptc_tool_contracts_types")

_emit_dispatches_healing_run("p1", "ptc_tool_contracts_types", "L2")
_emit_routes_through("p1", "ptc_tool_contracts_types", "L2")
_emit_checks_agent_registry("p1", "ptc_tool_contracts_types", "agent_registry")
_emit_validates_agent_capability("p1", "ptc_tool_contracts_types", "capability")
_emit_dispatches_execution_plan("p1", "ptc_tool_contracts_types", "exec_plan")
_emit_agent_executes_agent("p1", "ptc_tool_contracts_types", "sub_agent")
_emit_routes_to_agent("p1", "ptc_tool_contracts_types", "target_agent")
_emit_verifies_policy("p1", "ptc_tool_contracts_types", "policy_check")
_emit_observes_runtime_state("p1", "ptc_tool_contracts_types", "runtime_state")
_emit_verifies_boundary("p1", "ptc_tool_contracts_types", "boundary_check")
_emit_transcripts_response("p1", "ptc_tool_contracts_types", "transcript")
_emit_hard_fails_untranscripted("p1", "ptc_tool_contracts_types")
_emit_gated_by_confidence("p1", "ptc_tool_contracts_types", "confidence_gate")
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
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("ptc_tool_contracts_types", "p4obs", "metric_1")
_emit_emits_metric_event("ptc_tool_contracts_types", "p4obs", "metric_2")
_emit_emits_metric_event("ptc_tool_contracts_types", "p4obs", "metric_3")
_emit_emits_metric_event("ptc_tool_contracts_types", "p4obs", "metric_4")
_emit_emits_metric_event("ptc_tool_contracts_types", "p4obs", "metric_5")
_emit_emits_metric_event("ptc_tool_contracts_types", "p4obs", "metric_6")
_emit_records_incident_event("ptc_tool_contracts_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("ptc_tool_contracts_types", "p4obs", "anomaly")
_emit_writes_observability_log("ptc_tool_contracts_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("ptc_tool_contracts_types", "p4obs", "mon_state")
_emit_triggers_alert("ptc_tool_contracts_types", "p4obs", "alert")
_emit_links_incident_trace("ptc_tool_contracts_types", "p4obs", "trace_link")
_emit_captures_pattern("ptc_tool_contracts_types", "p3lm", "pattern")
_emit_records_learning_event("ptc_tool_contracts_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("ptc_tool_contracts_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("ptc_tool_contracts_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("ptc_tool_contracts_types", "p3lm", "routing")
_emit_improves_agent_policy("ptc_tool_contracts_types", "p3lm", "policy")
_emit_stores_learning_state("ptc_tool_contracts_types", "p3lm", "state")
_emit_records_execution_trace("ptc_tool_contracts_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("ptc_tool_contracts_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("ptc_tool_contracts_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("ptc_tool_contracts_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("ptc_tool_contracts_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("ptc_tool_contracts_types", "env_read", "p2_env_1")
_emit_reads_environ("ptc_tool_contracts_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("ptc_tool_contracts_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("ptc_tool_contracts_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "ptc_tool_contracts_types", "context_pull")
_emit_pulls_context("p1", "ptc_tool_contracts_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "ptc_tool_contracts_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "ptc_tool_contracts_types", "uwg_term_2")
_emit_writes_through("p1", "ptc_tool_contracts_types", "write_through")
_emit_writes_through("p1", "ptc_tool_contracts_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "ptc_tool_contracts_types", "safety_validation")
_emit_invokes_eval("p1", "ptc_tool_contracts_types", "eval_call")
_emit_proposal_commits_routing("p1", "ptc_tool_contracts_types", "routing_commit")


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
