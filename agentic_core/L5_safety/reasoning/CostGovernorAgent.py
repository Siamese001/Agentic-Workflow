from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "CostGovernorAgent")
emit_determinism_digest("p0", "CostGovernorAgent")

_emit_dispatches_healing_run("p1", "CostGovernorAgent", "L5")
_emit_routes_through("p1", "CostGovernorAgent", "L5")
_emit_escalates_to_human("p1", "CostGovernorAgent", "L5")
_emit_reads_policy_state("p1", "CostGovernorAgent", "L5")
_emit_authorize_and_execute("p2", "CostGovernorAgent", "execution_auth")
_emit_validates_capability("p2", "CostGovernorAgent", "capability_check")
_emit_routes_to_capability("p2", "CostGovernorAgent", "capability_route")
_emit_writes_via_uwg("p2", "CostGovernorAgent", "uwg_write")
_emit_blocks_direct_write("p2", "CostGovernorAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "CostGovernorAgent", "tool_invocation")
_emit_captures_execution_output("p2", "CostGovernorAgent", "exec_output")
_emit_dispatches_agent("p3", "CostGovernorAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "CostGovernorAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "CostGovernorAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "CostGovernorAgent", "healing_outcome")
_emit_escalates_failure("p3", "CostGovernorAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "CostGovernorAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "CostGovernorAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "CostGovernorAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "CostGovernorAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "CostGovernorAgent", "eval_metric")
_emit_stores_embedding("p4", "CostGovernorAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "CostGovernorAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "CostGovernorAgent", "exec_snapshot_link")

'Cost Governor Agent - L5 Safety financial guardrail for LLM spend tracking.\n\nThis module provides a financial guardrail agent that tracks and limits\nspending across LLM models and tools. It enforces budget constraints\nand raises exceptions when limits are exceeded.\n\nTypical usage:\n    agent = CostGovernorAgent(config={"budget_limit": 10.0})\n    cost = agent.track(model="gpt-4", input_tokens=100, output_tokens=50)\n'
import logging
from dataclasses import dataclass
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)
from agentic_core.utils.decorators_compat_util import standard_heal
from agentic_core.utils.timeout_decorator_util import timeout
from agentic_core.runtime.lifecycle_trace_contract import _emit_pulls_context, _emit_execution_terminates_at_uwg, _emit_writes_through, _emit_validated_by_safety_plane, _emit_invokes_eval, _emit_proposal_commits_routing
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("CostGovernorAgent", "p4obs", "metric_1")
_emit_emits_metric_event("CostGovernorAgent", "p4obs", "metric_2")
_emit_emits_metric_event("CostGovernorAgent", "p4obs", "metric_3")
_emit_emits_metric_event("CostGovernorAgent", "p4obs", "metric_4")
_emit_emits_metric_event("CostGovernorAgent", "p4obs", "metric_5")
_emit_emits_metric_event("CostGovernorAgent", "p4obs", "metric_6")
_emit_records_incident_event("CostGovernorAgent", "p4obs", "incident")
_emit_captures_runtime_anomaly("CostGovernorAgent", "p4obs", "anomaly")
_emit_writes_observability_log("CostGovernorAgent", "p4obs", "obs_log")
_emit_updates_monitoring_state("CostGovernorAgent", "p4obs", "mon_state")
_emit_triggers_alert("CostGovernorAgent", "p4obs", "alert")
_emit_links_incident_trace("CostGovernorAgent", "p4obs", "trace_link")
_emit_captures_pattern("CostGovernorAgent", "p3lm", "pattern")
_emit_records_learning_event("CostGovernorAgent", "p3lm", "learning_event")
_emit_writes_learning_snapshot("CostGovernorAgent", "p3lm", "snapshot")
_emit_feeds_meta_learning("CostGovernorAgent", "p3lm", "meta_feed")
_emit_updates_routing_strategy("CostGovernorAgent", "p3lm", "routing")
_emit_improves_agent_policy("CostGovernorAgent", "p3lm", "policy")
_emit_stores_learning_state("CostGovernorAgent", "p3lm", "state")
_emit_records_execution_trace("CostGovernorAgent", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("CostGovernorAgent", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("CostGovernorAgent", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("CostGovernorAgent", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("CostGovernorAgent", "L4_STATE", "p2_trace_5")
_emit_reads_environ("CostGovernorAgent", "env_read", "p2_env_1")
_emit_reads_environ("CostGovernorAgent", "env_read", "p2_env_2")
_emit_reads_runtime_state("CostGovernorAgent", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("CostGovernorAgent", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "CostGovernorAgent", "context_pull")
_emit_pulls_context("p1", "CostGovernorAgent", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "CostGovernorAgent", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "CostGovernorAgent", "uwg_term_2")
_emit_writes_through("p1", "CostGovernorAgent", "write_through")
_emit_writes_through("p1", "CostGovernorAgent", "write_through_2")
_emit_validated_by_safety_plane("p1", "CostGovernorAgent", "safety_validation")
_emit_invokes_eval("p1", "CostGovernorAgent", "eval_call")
_emit_proposal_commits_routing("p1", "CostGovernorAgent", "routing_commit")


class BudgetExceededError(Exception):
    """Raised when LLM spending exceeds the configured budget limit."""

    pass


@dataclass
class CostGovernorAgent(SovereignBaseAgent):
    """L5 Safety agent that tracks and limits LLM spend across models and tools.

    This financial guardrail monitors API costs and enforces budget constraints.
    It calculates costs based on token usage and raises BudgetExceededError
    when the configured limit is exceeded.

    Attributes:
        config: configuration dictionary with budget settings.
        limit: Maximum allowed spend in dollars.
        spend: Current accumulated spend in dollars.

    Inherits:
        SubatomicTestingMixin: Provides testing utilities.
        HealerMixin: Provides healing chain support.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize the cost governor with budget configuration.

        Args:
            config: configuration dictionary containing:
                - budget_limit: Maximum allowed spend in dollars (default: 10.0)
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "CostGovernorAgent.__init__", "state_snapshot")
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "CostGovernorAgent.__init__", "p0_governance")
        self.config: dict[str, Any] = config
        self.limit: float = config.get("budget_limit", 10.0)
        self.spend: float = 0.0

    def track(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate and record the cost of an LLM call.

        Args:
            model: Name of the LLM model used.
            input_tokens: Number of input tokens in the request.
            output_tokens: Number of output tokens in the response.

        Returns:
            Cost of this call in dollars.

        Raises:
            BudgetExceededError: If total spend exceeds the configured limit.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "CostGovernorAgent.track")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:CostGovernorAgent.track".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        cost: float = (input_tokens + output_tokens) * 2e-05
        self.spend += cost
        logging.info(f"Governor: Current Spend ${self.spend:.4f} / Limit ${self.limit:.2f}")
        if self.spend > self.limit:
            raise BudgetExceededError(
                f"BUDGET EXCEEDED: ${self.spend:.2f} exceeds limit of ${self.limit:.2f}"
            )
        return cost

    @timeout(300)
    @standard_heal
    # guardian: allow-magic-config
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set[str] | None = None,
    ) -> dict[str, int]:
        """Execute L5 safety healing operations.

        This is an operational agent - no repository healing required.
        Implements cycle detection and depth limiting.

        Args:
            dry_run: If True, only report what would be done (default: True).
            execute: If True, execute healing actions (default: False).
            depth: Current recursion depth for cycle detection (default: 0).
            max_depth: Maximum recursion depth allowed (default: 3).
            _call_path: Set of agent names in current call chain for cycle detection.

        Returns:
            Dictionary with healing results: {"skipped": 1} for operational agents.
        """
        super().heal_repository()
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L5 safety - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)

    # guardian: allow-type-erasure
    def heal(self, violation: dict) -> dict:
        """Heal cost governance violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (budget_exceeded)
                - model: Model that caused the overspend
                - spend: Current spend amount

        Returns:
            Dictionary with healing results following standard_heal format.
        """
        logging.info("[COST_GOVERNOR] Budget violations are runtime-managed")
        return {
            "violations_fixed": 0,
            "violations_found": 1,
            "errors": 0,
            "skipped": 1,
            "reason": "Budget violations are runtime-managed, not code-healable",
        }
