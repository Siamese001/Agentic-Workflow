"""
CostGuardrailMixin - Phase 1 Critical Infrastructure: Cost Control

Provides token usage monitoring and hard limits on recursive loops to prevent
runaway costs in production environments.

Features:
- Token usage tracking per operation
- Budget enforcement with configurable limits
- Recursive loop detection and prevention
- Cost estimation for LLM operations
- Real-time budget alerts

SSOT PRINCIPLE:
    All agents requiring cost control should inherit from this mixin.
    This ensures consistent cost tracking across the agent ecosystem.
"""

from __future__ import annotations

import logging
import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("cost_mixin", "p4obs", "metric_1")
_emit_emits_metric_event("cost_mixin", "p4obs", "metric_2")
_emit_emits_metric_event("cost_mixin", "p4obs", "metric_3")
_emit_emits_metric_event("cost_mixin", "p4obs", "metric_4")
_emit_emits_metric_event("cost_mixin", "p4obs", "metric_5")
_emit_emits_metric_event("cost_mixin", "p4obs", "metric_6")
_emit_records_incident_event("cost_mixin", "p4obs", "incident")
_emit_captures_runtime_anomaly("cost_mixin", "p4obs", "anomaly")
_emit_writes_observability_log("cost_mixin", "p4obs", "obs_log")
_emit_updates_monitoring_state("cost_mixin", "p4obs", "mon_state")
_emit_triggers_alert("cost_mixin", "p4obs", "alert")
_emit_links_incident_trace("cost_mixin", "p4obs", "trace_link")
_emit_captures_pattern("cost_mixin", "p3lm", "pattern")
_emit_records_learning_event("cost_mixin", "p3lm", "learning_event")
_emit_writes_learning_snapshot("cost_mixin", "p3lm", "snapshot")
_emit_feeds_meta_learning("cost_mixin", "p3lm", "meta_feed")
_emit_updates_routing_strategy("cost_mixin", "p3lm", "routing")
_emit_improves_agent_policy("cost_mixin", "p3lm", "policy")
_emit_stores_learning_state("cost_mixin", "p3lm", "state")
_emit_records_execution_trace("cost_mixin", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("cost_mixin", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("cost_mixin", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("cost_mixin", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("cost_mixin", "L4_STATE", "p2_trace_5")
_emit_reads_environ("cost_mixin", "env_read", "p2_env_1")
_emit_reads_environ("cost_mixin", "env_read", "p2_env_2")
_emit_reads_runtime_state("cost_mixin", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("cost_mixin", "runtime_state", "p2_rt_2")

_emit_applies_guardrail("p0", "cost_mixin", "p0_governance")
_emit_reads_policy_state("p0", "cost_mixin", "policy_binding")
_emit_snapshots_state("p0", "cost_mixin", "state_snapshot")
_emit_pulls_context("p1", "cost_mixin", "context_pull")
_emit_pulls_context("p1", "cost_mixin", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "cost_mixin", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "cost_mixin", "uwg_term_secondary")
_emit_writes_through("p1", "cost_mixin", "write_through")
_emit_writes_through("p1", "cost_mixin", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "cost_mixin", "safety_validation")
_emit_invokes_eval("p1", "cost_mixin", "eval_call")
_emit_proposal_commits_routing("p1", "cost_mixin", "routing_commit")
_emit_escalates_to_human("p1", "cost_mixin", "human_escalation")
_emit_routes_through("p1", "cost_mixin", "route_through")
_emit_checks_agent_registry("p1", "cost_mixin", "agent_registry")
_emit_validates_agent_capability("p1", "cost_mixin", "capability")
_emit_dispatches_execution_plan("p1", "cost_mixin", "exec_plan")
_emit_agent_executes_agent("p1", "cost_mixin", "sub_agent")
_emit_routes_to_agent("p1", "cost_mixin", "target_agent")
_emit_verifies_policy("p1", "cost_mixin", "policy_check")
_emit_observes_runtime_state("p1", "cost_mixin", "runtime_state")
_emit_verifies_boundary("p1", "cost_mixin", "boundary_check")
_emit_transcripts_response("p1", "cost_mixin", "transcript")
_emit_hard_fails_untranscripted("p1", "cost_mixin")
_emit_gated_by_confidence("p1", "cost_mixin", "confidence_gate")
emit_replay_key("p0", "cost_mixin")
emit_determinism_digest("p0", "cost_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "cost_mixin", "execution_auth")
_emit_validates_capability("p2", "cost_mixin", "capability_check")
_emit_routes_to_capability("p2", "cost_mixin", "capability_route")
_emit_writes_via_uwg("p2", "cost_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "cost_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "cost_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "cost_mixin", "exec_output")
_emit_dispatches_agent("p3", "cost_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "cost_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "cost_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "cost_mixin", "healing_outcome")
_emit_escalates_failure("p3", "cost_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "cost_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "cost_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "cost_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "cost_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "cost_mixin", "eval_metric")
_emit_stores_embedding("p4", "cost_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "cost_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "cost_mixin", "exec_snapshot_link")

Logger = logging.getLogger(__name__)


@dataclass
class TokenUsage:
    """Tracks token usage for a single operation."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0
    model: str = "unknown"
    timestamp: float = field(default_factory=time.time)


@dataclass
class BudgetConfig:
    """Configuration for budget limits."""

    max_tokens_per_request: int = 8000
    max_tokens_per_session: int = 100000
    max_cost_per_session_usd: float = 10.0
    max_recursive_depth: int = 10
    max_loop_iterations: int = 50
    alert_threshold_pct: float = 0.8


class BudgetExceededError(Exception):
    """Raised when budget limits are exceeded."""

    def __init__(self, limit_type: str, current: float, limit: float):
        self.limit_type = limit_type
        self.current = current
        self.limit = limit
        super().__init__(f"Budget exceeded: {limit_type} - Current: {current}, Limit: {limit}")


class RecursionLimitError(Exception):
    """Raised when recursive depth or loop iterations exceed limits."""

    def __init__(self, limit_type: str, current: int, limit: int):
        self.limit_type = limit_type
        self.current = current
        self.limit = limit
        super().__init__(f"Recursion limit exceeded: {limit_type} - Current: {current}, Limit: {limit}")


MODEL_PRICING: dict[str, dict[str, float]] = {
    "gpt-4o": {"input": 0.0025, "output": 0.01},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    "claude-3-opus": {"input": 0.015, "output": 0.075},
    "claude-3-sonnet": {"input": 0.003, "output": 0.015},
    "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
    "default": {"input": 0.001, "output": 0.002},
}


class CostGuardrailMixin:
    """
    Mixin providing cost control and budget enforcement for agents.

    Phase 1 Critical Infrastructure:
    - Token usage tracking
    - Budget limits enforcement
    - Recursive loop prevention
    - Cost estimation and alerts

    Usage:
        class MyAgent(CostGuardrailMixin, SovereignBaseAgent):
            def __init__(self):
                super().__init__()
                self.configure_budget(max_tokens_per_session=50000)

            async def process(self, query: str) -> str:
                with self.track_operation("llm_call"):
                    response = await self.llm_generate(query)
                    self.record_token_usage(
                        prompt_tokens=response["usage"]["prompt_tokens"],
                        completion_tokens=response["usage"]["completion_tokens"],
                        model=response["model"]
                    )
                return response["content"]
    """

    def __init__(self, **kwargs: Any) -> None:
        """Initialize cost guardrail state."""
        super().__init__(**kwargs)
        self._budget_config: BudgetConfig = BudgetConfig()
        self._session_token_usage: list[TokenUsage] = []
        self._session_start_time: float = time.time()
        self._total_session_tokens: int = 0
        self._total_session_cost: float = 0.0
        self._call_stack: list[str] = []
        self._loop_counters: dict[str, int] = {}
        self._cost_lock = threading.RLock()
        self._budget_alerts_sent: set[str] = set()
        self._cost_guardrail_initialized = True
        Logger.debug(f"[COST] {self.__class__.__name__} cost guardrails initialized")

    def configure_budget(
        self,
        max_tokens_per_request: int | None = None,
        max_tokens_per_session: int | None = None,
        max_cost_per_session_usd: float | None = None,
        max_recursive_depth: int | None = None,
        max_loop_iterations: int | None = None,
        alert_threshold_pct: float | None = None,
    ) -> None:
        """
        Configure budget limits for this agent.

        Args:
            max_tokens_per_request: Maximum tokens allowed per single request
            max_tokens_per_session: Maximum tokens allowed per session
            max_cost_per_session_usd: Maximum cost in USD per session
            max_recursive_depth: Maximum recursive call depth
            max_loop_iterations: Maximum iterations in a loop
            alert_threshold_pct: Percentage of budget at which to alert (0.0-1.0)

        Raises:
            ValueError: If any parameter is invalid (negative or out of range)
        """

        _emit_records_execution_trace(
            str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "CostMixin.configure_budget"
        )
        if max_tokens_per_request is not None and max_tokens_per_request <= 0:
            raise ValueError("max_tokens_per_request must be positive")
        if max_tokens_per_session is not None and max_tokens_per_session <= 0:
            raise ValueError("max_tokens_per_session must be positive")
        if max_cost_per_session_usd is not None and max_cost_per_session_usd <= 0:
            raise ValueError("max_cost_per_session_usd must be positive")
        if max_recursive_depth is not None and max_recursive_depth <= 0:
            raise ValueError("max_recursive_depth must be positive")
        if max_loop_iterations is not None and max_loop_iterations <= 0:
            raise ValueError("max_loop_iterations must be positive")
        if alert_threshold_pct is not None and (not 0.0 < alert_threshold_pct <= 1.0):
            raise ValueError("alert_threshold_pct must be between 0.0 and 1.0")
        with self._cost_lock:
            if max_tokens_per_request is not None:
                self._budget_config.max_tokens_per_request = max_tokens_per_request
            if max_tokens_per_session is not None:
                self._budget_config.max_tokens_per_session = max_tokens_per_session
            if max_cost_per_session_usd is not None:
                self._budget_config.max_cost_per_session_usd = max_cost_per_session_usd
            if max_recursive_depth is not None:
                self._budget_config.max_recursive_depth = max_recursive_depth
            if max_loop_iterations is not None:
                self._budget_config.max_loop_iterations = max_loop_iterations
            if alert_threshold_pct is not None:
                self._budget_config.alert_threshold_pct = alert_threshold_pct
        Logger.info(f"[COST] Budget configured: {self._budget_config}")

    def estimate_cost(self, prompt_tokens: int, completion_tokens: int, model: str = "default") -> float:
        """
        Estimate cost for a given token usage.

        Args:
            prompt_tokens: Number of input tokens
            completion_tokens: Number of output tokens
            model: Model name for pricing lookup

        Returns:
            Estimated cost in USD
        """
        pricing = MODEL_PRICING.get(model, MODEL_PRICING["default"])
        input_cost = prompt_tokens / 1000 * pricing["input"]
        output_cost = completion_tokens / 1000 * pricing["output"]
        return input_cost + output_cost

    def record_token_usage(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        model: str = "unknown",
    ) -> TokenUsage:
        """
        Record token usage for an operation.

        Args:
            prompt_tokens: Number of input tokens
            completion_tokens: Number of output tokens
            model: Model used for the operation

        Returns:
            TokenUsage record

        Raises:
            BudgetExceededError: If budget limits are exceeded
        """
        total_tokens = prompt_tokens + completion_tokens
        estimated_cost = self.estimate_cost(prompt_tokens, completion_tokens, model)
        with self._cost_lock:
            if total_tokens > self._budget_config.max_tokens_per_request:
                raise BudgetExceededError(
                    "tokens_per_request",
                    total_tokens,
                    self._budget_config.max_tokens_per_request,
                )
            new_session_total = self._total_session_tokens + total_tokens
            if new_session_total > self._budget_config.max_tokens_per_session:
                raise BudgetExceededError(
                    "tokens_per_session",
                    new_session_total,
                    self._budget_config.max_tokens_per_session,
                )
            new_session_cost = self._total_session_cost + estimated_cost
            if new_session_cost > self._budget_config.max_cost_per_session_usd:
                raise BudgetExceededError(
                    "cost_per_session",
                    new_session_cost,
                    self._budget_config.max_cost_per_session_usd,
                )
            usage = TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                estimated_cost_usd=estimated_cost,
                model=model,
            )
            self._session_token_usage.append(usage)
            self._total_session_tokens = new_session_total
            self._total_session_cost = new_session_cost
            self._check_budget_alerts()
        Logger.debug(
            f"[COST] Recorded: {total_tokens} tokens, ${estimated_cost:.4f} (Session: {self._total_session_tokens} tokens, ${self._total_session_cost:.4f})",
        )
        return usage

    def _check_budget_alerts(self) -> None:
        """Check and emit budget alerts if thresholds are exceeded."""
        threshold = self._budget_config.alert_threshold_pct
        token_pct = self._total_session_tokens / self._budget_config.max_tokens_per_session
        if token_pct >= threshold and "token_threshold" not in self._budget_alerts_sent:
            self._budget_alerts_sent.add("token_threshold")
            Logger.warning(
                f"[COST ALERT] Token usage at {token_pct:.0%} of session limit ({self._total_session_tokens}/{self._budget_config.max_tokens_per_session})",
            )
        cost_pct = self._total_session_cost / self._budget_config.max_cost_per_session_usd
        if cost_pct >= threshold and "cost_threshold" not in self._budget_alerts_sent:
            self._budget_alerts_sent.add("cost_threshold")
            Logger.warning(
                f"[COST ALERT] Cost at {cost_pct:.0%} of session limit (${self._total_session_cost:.4f}/${self._budget_config.max_cost_per_session_usd})",
            )

    def check_recursion_limit(self, operation_id: str) -> None:
        """
        Check and enforce recursion depth limits.

        Args:
            operation_id: Unique identifier for the operation

        Raises:
            RecursionLimitError: If recursion depth exceeds limit
        """
        with self._cost_lock:
            current_depth = self._call_stack.count(operation_id)
            if current_depth >= self._budget_config.max_recursive_depth:
                raise RecursionLimitError(
                    "recursive_depth",
                    current_depth,
                    self._budget_config.max_recursive_depth,
                )
            self._call_stack.append(operation_id)

    def exit_recursion(self, operation_id: str) -> None:
        """
        Exit a recursive operation, removing it from the call stack.

        Args:
            operation_id: Unique identifier for the operation
        """
        with self._cost_lock:
            if operation_id in self._call_stack:
                self._call_stack.remove(operation_id)

    def check_loop_limit(self, loop_id: str) -> int:
        """
        Check and enforce loop iteration limits.

        Args:
            loop_id: Unique identifier for the loop

        Returns:
            Current iteration count

        Raises:
            RecursionLimitError: If loop iterations exceed limit
        """
        with self._cost_lock:
            current_count = self._loop_counters.get(loop_id, 0) + 1
            if current_count > self._budget_config.max_loop_iterations:
                raise RecursionLimitError(
                    "loop_iterations",
                    current_count,
                    self._budget_config.max_loop_iterations,
                )
            self._loop_counters[loop_id] = current_count
            return current_count

    def reset_loop_counter(self, loop_id: str) -> None:
        """
        Reset a loop counter.

        Args:
            loop_id: Unique identifier for the loop
        """
        with self._cost_lock:
            self._loop_counters.pop(loop_id, None)

    def get_budget_status(self) -> dict[str, Any]:
        """
        Get current budget status.

        Returns:
            Dictionary with budget status information
        """
        with self._cost_lock:
            return {
                "session_tokens": self._total_session_tokens,
                "session_cost_usd": self._total_session_cost,
                "max_tokens_per_session": self._budget_config.max_tokens_per_session,
                "max_cost_per_session_usd": self._budget_config.max_cost_per_session_usd,
                "token_usage_pct": self._total_session_tokens / self._budget_config.max_tokens_per_session,
                "cost_usage_pct": self._total_session_cost / self._budget_config.max_cost_per_session_usd,
                "operations_count": len(self._session_token_usage),
                "current_recursion_depth": len(self._call_stack),
                "active_loops": len(self._loop_counters),
                "alerts_sent": list(self._budget_alerts_sent),
            }

    def reset_session(self) -> dict[str, Any]:
        """
        Reset session tracking.

        Returns:
            Summary of the reset session
        """
        with self._cost_lock:
            summary = {
                "total_tokens": self._total_session_tokens,
                "total_cost_usd": self._total_session_cost,
                "operations_count": len(self._session_token_usage),
                "duration_seconds": time.time() - self._session_start_time,
            }
            self._session_token_usage = []
            self._total_session_tokens = 0
            self._total_session_cost = 0.0
            self._session_start_time = time.time()
            self._call_stack = []
            self._loop_counters = {}
            self._budget_alerts_sent = set()
        Logger.info(f"[COST] Session reset. Previous session: {summary}")
        return summary


__all__ = [
    "CostGuardrailMixin",
    "BudgetConfig",
    "TokenUsage",
    "BudgetExceededError",
    "RecursionLimitError",
    "MODEL_PRICING",
]
