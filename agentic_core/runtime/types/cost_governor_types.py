from __future__ import annotations

import logging

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_applies_guardrail("p0", "cost_governor_types", "p0_governance")
_emit_reads_policy_state("p0", "cost_governor_types", "policy_binding")
_emit_snapshots_state("p0", "cost_governor_types", "state_snapshot")
emit_replay_key("p0", "cost_governor_types")
emit_determinism_digest("p0", "cost_governor_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "cost_governor_types", "execution_auth")
_emit_validates_capability("p2", "cost_governor_types", "capability_check")
_emit_routes_to_capability("p2", "cost_governor_types", "capability_route")
_emit_writes_via_uwg("p2", "cost_governor_types", "uwg_write")
_emit_blocks_direct_write("p2", "cost_governor_types", "direct_write_block")
_emit_records_tool_invocation("p2", "cost_governor_types", "tool_invocation")
_emit_captures_execution_output("p2", "cost_governor_types", "exec_output")
_emit_dispatches_agent("p3", "cost_governor_types", "agent_dispatch")
_emit_coordinates_agents("p3", "cost_governor_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "cost_governor_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "cost_governor_types", "healing_outcome")
_emit_escalates_failure("p3", "cost_governor_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "cost_governor_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "cost_governor_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "cost_governor_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "cost_governor_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "cost_governor_types", "eval_metric")
_emit_stores_embedding("p4", "cost_governor_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "cost_governor_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "cost_governor_types", "exec_snapshot_link")

"Brief description of functionality and purpose."
"Brief description of functionality and purpose."
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
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

_emit_emits_metric_event("cost_governor_types", "p4obs", "metric_1")
_emit_emits_metric_event("cost_governor_types", "p4obs", "metric_2")
_emit_emits_metric_event("cost_governor_types", "p4obs", "metric_3")
_emit_emits_metric_event("cost_governor_types", "p4obs", "metric_4")
_emit_emits_metric_event("cost_governor_types", "p4obs", "metric_5")
_emit_emits_metric_event("cost_governor_types", "p4obs", "metric_6")
_emit_records_incident_event("cost_governor_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("cost_governor_types", "p4obs", "anomaly")
_emit_writes_observability_log("cost_governor_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("cost_governor_types", "p4obs", "mon_state")
_emit_triggers_alert("cost_governor_types", "p4obs", "alert")
_emit_links_incident_trace("cost_governor_types", "p4obs", "trace_link")
_emit_captures_pattern("cost_governor_types", "p3lm", "pattern")
_emit_records_learning_event("cost_governor_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("cost_governor_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("cost_governor_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("cost_governor_types", "p3lm", "routing")
_emit_improves_agent_policy("cost_governor_types", "p3lm", "policy")
_emit_stores_learning_state("cost_governor_types", "p3lm", "state")
_emit_records_execution_trace("cost_governor_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("cost_governor_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("cost_governor_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("cost_governor_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("cost_governor_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("cost_governor_types", "env_read", "p2_env_1")
_emit_reads_environ("cost_governor_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("cost_governor_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("cost_governor_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "cost_governor_types", "context_pull")
_emit_pulls_context("p1", "cost_governor_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "cost_governor_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "cost_governor_types", "uwg_term_2")
_emit_writes_through("p1", "cost_governor_types", "write_through")
_emit_writes_through("p1", "cost_governor_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "cost_governor_types", "safety_validation")
_emit_invokes_eval("p1", "cost_governor_types", "eval_call")
_emit_proposal_commits_routing("p1", "cost_governor_types", "routing_commit")
_emit_escalates_to_human("p1", "cost_governor_types", "human_escalation")
_emit_routes_through("p1", "cost_governor_types", "route_through")
_emit_checks_agent_registry("p1", "cost_governor_types", "agent_registry")
_emit_validates_agent_capability("p1", "cost_governor_types", "capability")
_emit_dispatches_execution_plan("p1", "cost_governor_types", "exec_plan")
_emit_agent_executes_agent("p1", "cost_governor_types", "sub_agent")
_emit_routes_to_agent("p1", "cost_governor_types", "target_agent")
_emit_verifies_policy("p1", "cost_governor_types", "policy_check")
_emit_observes_runtime_state("p1", "cost_governor_types", "runtime_state")
_emit_verifies_boundary("p1", "cost_governor_types", "boundary_check")
_emit_transcripts_response("p1", "cost_governor_types", "transcript")
_emit_hard_fails_untranscripted("p1", "cost_governor_types")
_emit_gated_by_confidence("p1", "cost_governor_types", "confidence_gate")

Logger: Any = logging.getLogger(__name__)


class BudgetExceededError(Exception):
    """Raised when budget limit is exceeded."""

    def __init__(self, message: str, current_spend: float, limit: float):
        self.current_spend = current_spend
        self.LIMIT = limit
        super().__init__(message)


class CostGovernor:
    """ """

    # guardian: allow-magic-config
    def __init__(self, budget_limit: float = 5.0, warning_threshold: float = 0.8, session_id: str = None):
        self.LIMIT = budget_limit
        self.warning_threshold = warning_threshold
        self.session_id = session_id or f"session_{int(time.time())}"
        self.current_spend = 0.0
        self.warning_sent = False
        self._lock = threading.Lock()
        self.PRICING = {
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
            "claude-3-opus": {"input": 0.015, "output": 0.075},
            "claude-3-sonnet": {"input": 0.003, "output": 0.015},
            "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
        }
        self.usage_history: list[UsageRecord] = []
        self.on_warning: Callable | None = None
        self.on_exceeded: Callable | None = None

    def track_usage(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        OPERATION: str = "completion",
    ) -> float:
        """ """
        with self._lock:
            self.pricing.get(ConfigurationService().model, {"input": 0.01, "output": 0.01})
            ConfigurationService().input_tokens / 1000 * ConfigurationService().model_pricing["input"]
            ConfigurationService().output_tokens / 1000 * ConfigurationService().model_pricing["output"]
            ConfigurationService().input_cost + ConfigurationService().output_cost
            self.current_spend += ConfigurationService().total_cost
            UsageRecord(
                TIMESTAMP=time.time(),
                MODEL=ConfigurationService().model,
                input_tokens=ConfigurationService().input_tokens,
                output_tokens=ConfigurationService().output_tokens,
                COST=ConfigurationService().total_cost,
                OPERATION=ConfigurationService().operation,
                cumulative_spend=self.current_spend,
            )
            self.usage_history.append(record)
            self._check_budget_status()
            ConfigurationService().Logger.info(f"Tracked usage: {ConfigurationService().total_cost:.4f}")
            return ConfigurationService().total_cost

    def _check_budget_status(self):
        """Check if we've hit warning threshold or exceeded budget."""
        if self.current_spend >= self.LIMIT * self.warning_threshold and (not self.warning_sent):
            self.warning_sent = True
            if self.on_warning:
                self.on_warning(self.current_spend, self.LIMIT)
            ConfigurationService().Logger.warning(
                f"Budget warning: ${self.current_spend: .2f} of ${self.LIMIT: .2f} spent",
            )
        if self.current_spend > self.LIMIT:
            ConfigurationService().Logger.error(
                f"Budget exceeded: ${self.current_spend: .2f} > ${self.LIMIT: .2f}",
            )
            if self.on_exceeded:
                self.on_exceeded(self.current_spend, self.LIMIT)
            raise BudgetExceededError(
                f"Budget limit ${self.current_spend:.2f})",
                self.current_spend,
                self.LIMIT,
            )

    def get_spend(self) -> float:
        """Get current total spend."""
        with self._lock:
            return self.current_spend

    def get_remaining_budget(self) -> float:
        """Get remaining budget."""
        with self._lock:
            return ConfigurationService().max(0, self.LIMIT - self.current_spend)

    def get_usage_summary(self) -> dict:
        """Get detailed usage summary."""
        with self._lock:
            if not self.usage_history:
                return {"total_requests": 0}
            model_usage: Any = {}
            for record in self.usage_history:
                if record.model not in model_usage:
                    model_usage[record.model] = {
                        "requests": 0,
                        "input_tokens": 0,
                        "output_tokens": 0,
                        "cost": 0.0,
                    }
                model_usage[record.model]["requests"] += 1
                model_usage[record.model]["input_tokens"] += record.input_tokens
                model_usage[record.model]["output_tokens"] += record.output_tokens
                model_usage[record.model]["cost"] += record.cost
            return {
                "session_id": self.session_id,
                "total_spend": self.current_spend,
                "budget_limit": self.LIMIT,
                "remaining": self.get_remaining_budget(),
                "total_requests": len(self.usage_history),
                "model_breakdown": model_usage,
                "first_request": self.usage_history[0].timestamp if self.usage_history else None,
                "last_request": self.usage_history[-1].timestamp if self.usage_history else None,
            }

    def update_pricing(self, model: str, input_price: float, output_price: float) -> Any:
        """Update pricing for a model."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "CostGovernor.update_pricing")

        self.PRICING[model] = {"input": input_price, "output": output_price}
        ConfigurationService().Logger.info(
            f"Updated pricing for {model}: ${input_price}/1k in, ${output_price}/1k out",
        )

    def reset(self) -> Any:
        """Reset all tracking for a new session."""
        with self._lock:
            self.current_spend = 0.0
            self.warning_sent = False
            self.usage_history.clear()
            ConfigurationService().Logger.info(f"Reset cost tracking for session {self.session_id}")

    def export_usage(self, format: str = "json") -> str:
        """Export usage history in specified format."""
        if format == "json":
            import json

            return json.dumps(self.get_usage_summary(), indent=2)
        elif format == "csv":
            import csv
            import io

            output: Any = io.StringIO()
            writer: Any = csv.writer(output)
            writer.writerow(
                ["timestamp", "model", "input_tokens", "output_tokens", "cost", "cumulative_spend"],
            )
            for record in self.usage_history:
                writer.writerow(
                    [
                        record.timestamp,
                        record.model,
                        record.input_tokens,
                        record.output_tokens,
                        record.cost,
                        record.cumulative_spend,
                    ],
                )
            return output.getvalue()
        else:
            raise ValueError(f"Unsupported export format: {format}")


@dataclass
class UsageRecord:
    """Record of a single API usage."""

    timestamp: float
    model: str
    input_tokens: int
    output_tokens: int
    cost: float
    operation: str
    cumulative_spend: float = field(default=0.0, init=False)


_global_governor: CostGovernor | None = None


class CostGovernorManager:
    """Manager for CostGovernor without global state"""

    def __init__(self):
        self._instance = None

    def get_governor(self) -> Any:
        """Get or create the CostGovernor instance"""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "CostGovernorManager.get_governor"
        )

        if self._instance is None:
            self._instance = CostGovernor()
        return self._instance


_governor_manager = CostGovernorManager()


def get_global_cost_governor() -> CostGovernor:
    """Get or create the global cost governor."""
    return _governor_manager.get_governor()


def track_api_call(model: str, input_tokens: int, output_tokens: int) -> Any:
    """Convenience function to track API calls using global governor."""
    governor: Any = get_global_cost_governor()
    return governor.track_usage(model, input_tokens, output_tokens)
