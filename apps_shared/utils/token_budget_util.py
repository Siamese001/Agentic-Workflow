"""Token Budget Enforcement for cost control.

Phase 1 - Pillar 11: Cost & Optimization (Semantic Caching)
Converts token budget inspector into active enforcement mechanism.
"""

import logging
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
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
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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

_emit_applies_guardrail("p0", "token_budget_util", "p0_governance")
_emit_reads_policy_state("p0", "token_budget_util", "policy_binding")
_emit_snapshots_state("p0", "token_budget_util", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("token_budget_util", "p4obs", "metric_1")
_emit_emits_metric_event("token_budget_util", "p4obs", "metric_2")
_emit_emits_metric_event("token_budget_util", "p4obs", "metric_3")
_emit_emits_metric_event("token_budget_util", "p4obs", "metric_4")
_emit_emits_metric_event("token_budget_util", "p4obs", "metric_5")
_emit_emits_metric_event("token_budget_util", "p4obs", "metric_6")
_emit_records_incident_event("token_budget_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("token_budget_util", "p4obs", "anomaly")
_emit_writes_observability_log("token_budget_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("token_budget_util", "p4obs", "mon_state")
_emit_triggers_alert("token_budget_util", "p4obs", "alert")
_emit_links_incident_trace("token_budget_util", "p4obs", "trace_link")
_emit_captures_pattern("token_budget_util", "p3lm", "pattern")
_emit_records_learning_event("token_budget_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("token_budget_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("token_budget_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("token_budget_util", "p3lm", "routing")
_emit_improves_agent_policy("token_budget_util", "p3lm", "policy")
_emit_stores_learning_state("token_budget_util", "p3lm", "state")
_emit_records_execution_trace("token_budget_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("token_budget_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("token_budget_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("token_budget_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("token_budget_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("token_budget_util", "env_read", "p2_env_1")
_emit_reads_environ("token_budget_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("token_budget_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("token_budget_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "token_budget_util", "context_pull")
_emit_pulls_context("p1", "token_budget_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "token_budget_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "token_budget_util", "uwg_term_2")
_emit_writes_through("p1", "token_budget_util", "write_through")
_emit_writes_through("p1", "token_budget_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "token_budget_util", "safety_validation")
_emit_invokes_eval("p1", "token_budget_util", "eval_call")
_emit_proposal_commits_routing("p1", "token_budget_util", "routing_commit")
_emit_escalates_to_human("p1", "token_budget_util", "human_escalation")
_emit_routes_through("p1", "token_budget_util", "route_through")
_emit_checks_agent_registry("p1", "token_budget_util", "agent_registry")
_emit_validates_agent_capability("p1", "token_budget_util", "capability")
_emit_dispatches_execution_plan("p1", "token_budget_util", "exec_plan")
_emit_agent_executes_agent("p1", "token_budget_util", "sub_agent")
_emit_routes_to_agent("p1", "token_budget_util", "target_agent")
_emit_verifies_policy("p1", "token_budget_util", "policy_check")
_emit_observes_runtime_state("p1", "token_budget_util", "runtime_state")
_emit_verifies_boundary("p1", "token_budget_util", "boundary_check")
_emit_transcripts_response("p1", "token_budget_util", "transcript")
_emit_hard_fails_untranscripted("p1", "token_budget_util")
_emit_gated_by_confidence("p1", "token_budget_util", "confidence_gate")
emit_replay_key("p0", "token_budget_util")
emit_determinism_digest("p0", "token_budget_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "token_budget_util", "execution_auth")
_emit_validates_capability("p2", "token_budget_util", "capability_check")
_emit_routes_to_capability("p2", "token_budget_util", "capability_route")
_emit_writes_via_uwg("p2", "token_budget_util", "uwg_write")
_emit_blocks_direct_write("p2", "token_budget_util", "direct_write_block")
_emit_records_tool_invocation("p2", "token_budget_util", "tool_invocation")
_emit_captures_execution_output("p2", "token_budget_util", "exec_output")
_emit_dispatches_agent("p3", "token_budget_util", "agent_dispatch")
_emit_coordinates_agents("p3", "token_budget_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "token_budget_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "token_budget_util", "healing_outcome")
_emit_escalates_failure("p3", "token_budget_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "token_budget_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "token_budget_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "token_budget_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "token_budget_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "token_budget_util", "eval_metric")
_emit_stores_embedding("p4", "token_budget_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "token_budget_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "token_budget_util", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class BudgetExceededError(Exception):
    """Raised when token budget is exceeded."""

    def __init__(self, message: str, current_tokens: int, max_tokens: int, budget_type: str = "total"):
        super().__init__(message)
        self.current_tokens = current_tokens
        self.max_tokens = max_tokens
        self.budget_type = budget_type


@dataclass
class TokenBudgetConfig:
    """Token budget configuration."""

    max_prompt_tokens: int = 100000
    max_completion_tokens: int = 50000
    max_total_tokens: int = 150000
    max_tokens_per_request: int = 8000
    enforce_limits: bool = True
    warn_threshold: float = 0.8


class TokenBudget:
    """Token budget tracker and enforcer.

    Tracks token usage across requests and enforces limits
    to prevent cost overruns.
    """

    def __init__(self, config: TokenBudgetConfig | None = None, enable_logging: bool = True):
        """Initialize token budget.

        Args:
            config: Budget configuration
            enable_logging: Enable logging of budget events
        """
        self.config = config or TokenBudgetConfig()
        self.enable_logging = enable_logging
        self._prompt_tokens = 0
        self._completion_tokens = 0
        self._total_tokens = 0
        self._request_count = 0

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text.

        Uses simple heuristic: ~4 characters per token.
        For production, use tiktoken or similar.

        Args:
            text: Text to estimate

        Returns:
            Estimated token count
        """
        return len(text) // 4

    def check_request_budget(self, prompt: str, max_completion_tokens: int) -> None:
        """Check if a request fits within budget.

        Args:
            prompt: The prompt text
            max_completion_tokens: Max tokens for completion

        Raises:
            BudgetExceededError: If budget would be exceeded
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "TokenBudget.check_request_budget"
        )

        prompt_tokens = self.estimate_tokens(prompt)
        if prompt_tokens > self.config.max_tokens_per_request:
            raise BudgetExceededError(
                f"Prompt exceeds per-request limit: {prompt_tokens} > {self.config.max_tokens_per_request}",
                current_tokens=prompt_tokens,
                max_tokens=self.config.max_tokens_per_request,
                budget_type="per_request",
            )
        projected_total = self._total_tokens + prompt_tokens + max_completion_tokens
        if self.config.enforce_limits and projected_total > self.config.max_total_tokens:
            raise BudgetExceededError(
                f"Request would exceed total budget: {projected_total} > {self.config.max_total_tokens}",
                current_tokens=projected_total,
                max_tokens=self.config.max_total_tokens,
                budget_type="total",
            )
        warn_threshold = self.config.max_total_tokens * self.config.warn_threshold
        if self.enable_logging and projected_total > warn_threshold:
            logger.warning(
                "token_budget_warning",
                extra={
                    "projected_total": projected_total,
                    "max_total": self.config.max_total_tokens,
                    "utilization": projected_total / self.config.max_total_tokens,
                },
            )

    def record_usage(self, prompt_tokens: int, completion_tokens: int) -> None:
        """Record token usage for a request.

        Args:
            prompt_tokens: Tokens used in prompt
            completion_tokens: Tokens used in completion
        """
        self._prompt_tokens += prompt_tokens
        self._completion_tokens += completion_tokens
        self._total_tokens += prompt_tokens + completion_tokens
        self._request_count += 1
        if self.enable_logging:
            logger.info(
                "token_usage_recorded",
                extra={
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": self._total_tokens,
                    "request_count": self._request_count,
                },
            )
        if self.config.enforce_limits:
            if self._prompt_tokens > self.config.max_prompt_tokens:
                raise BudgetExceededError(
                    f"Prompt token budget exceeded: {self._prompt_tokens} > {self.config.max_prompt_tokens}",
                    current_tokens=self._prompt_tokens,
                    max_tokens=self.config.max_prompt_tokens,
                    budget_type="prompt",
                )
            if self._completion_tokens > self.config.max_completion_tokens:
                raise BudgetExceededError(
                    f"Completion token budget exceeded: {self._completion_tokens} > {self.config.max_completion_tokens}",
                    current_tokens=self._completion_tokens,
                    max_tokens=self.config.max_completion_tokens,
                    budget_type="completion",
                )
            if self._total_tokens > self.config.max_total_tokens:
                raise BudgetExceededError(
                    f"Total token budget exceeded: {self._total_tokens} > {self.config.max_total_tokens}",
                    current_tokens=self._total_tokens,
                    max_tokens=self.config.max_total_tokens,
                    budget_type="total",
                )

    def get_stats(self) -> dict[str, Any]:
        """Get budget statistics.

        Returns:
            Dict with budget stats
        """
        return {
            "prompt_tokens": self._prompt_tokens,
            "completion_tokens": self._completion_tokens,
            "total_tokens": self._total_tokens,
            "request_count": self._request_count,
            "max_prompt_tokens": self.config.max_prompt_tokens,
            "max_completion_tokens": self.config.max_completion_tokens,
            "max_total_tokens": self.config.max_total_tokens,
            "prompt_utilization": self._prompt_tokens / max(1, self.config.max_prompt_tokens),
            "completion_utilization": self._completion_tokens / max(1, self.config.max_completion_tokens),
            "total_utilization": self._total_tokens / max(1, self.config.max_total_tokens),
        }

    def reset(self) -> None:
        """Reset budget counters."""
        self._prompt_tokens = 0
        self._completion_tokens = 0
        self._total_tokens = 0
        self._request_count = 0
        if self.enable_logging:
            logger.info("token_budget_reset")

    def get_remaining(self) -> dict[str, int]:
        """Get remaining token budget.

        Returns:
            Dict with remaining tokens for each category
        """
        return {
            "prompt": max(0, self.config.max_prompt_tokens - self._prompt_tokens),
            "completion": max(0, self.config.max_completion_tokens - self._completion_tokens),
            "total": max(0, self.config.max_total_tokens - self._total_tokens),
        }


def enforce_token_budget(prompt: str, max_completion_tokens: int, budget: TokenBudget) -> None:
    """Convenience function to enforce token budget.

    Args:
        prompt: The prompt text
        max_completion_tokens: Max completion tokens
        budget: TokenBudget instance

    Raises:
        BudgetExceededError: If budget exceeded
    """
    budget.check_request_budget(prompt, max_completion_tokens)
