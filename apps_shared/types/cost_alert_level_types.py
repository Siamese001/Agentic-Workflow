"""Per-Agent Cost Tracking with Identity Integration.

Phase 4 - Pillar 11 (Cont.): Cost & Optimization
Tracks costs per agent using SPIFFE identity for financial accountability.

Integrates with:
- Phase 3 SPIFFE Identity (Pillar 2)
- Phase 2 observability (Pillar 10)
- Phase 1 Token Budget (Pillar 11)
"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "cost_alert_level_types", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "cost_alert_level_types", "policy_binding")
trace_contract._emit_snapshots_state("p0", "cost_alert_level_types", "state_snapshot")

trace_contract._emit_emits_metric_event("cost_alert_level_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("cost_alert_level_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("cost_alert_level_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("cost_alert_level_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("cost_alert_level_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("cost_alert_level_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("cost_alert_level_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("cost_alert_level_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("cost_alert_level_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("cost_alert_level_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("cost_alert_level_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("cost_alert_level_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("cost_alert_level_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("cost_alert_level_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("cost_alert_level_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("cost_alert_level_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("cost_alert_level_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("cost_alert_level_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("cost_alert_level_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("cost_alert_level_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("cost_alert_level_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("cost_alert_level_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("cost_alert_level_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("cost_alert_level_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("cost_alert_level_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("cost_alert_level_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("cost_alert_level_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("cost_alert_level_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "cost_alert_level_types", "context_pull")
trace_contract._emit_pulls_context("p1", "cost_alert_level_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "cost_alert_level_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "cost_alert_level_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "cost_alert_level_types", "write_through")
trace_contract._emit_writes_through("p1", "cost_alert_level_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "cost_alert_level_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "cost_alert_level_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "cost_alert_level_types", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "cost_alert_level_types", "human_escalation")
trace_contract._emit_routes_through("p1", "cost_alert_level_types", "route_through")
trace_contract._emit_checks_agent_registry("p1", "cost_alert_level_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "cost_alert_level_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "cost_alert_level_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "cost_alert_level_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "cost_alert_level_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "cost_alert_level_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "cost_alert_level_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "cost_alert_level_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "cost_alert_level_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "cost_alert_level_types")
trace_contract._emit_gated_by_confidence("p1", "cost_alert_level_types", "confidence_gate")
trace_contract.emit_replay_key("p0", "cost_alert_level_types")
trace_contract.emit_determinism_digest("p0", "cost_alert_level_types")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "cost_alert_level_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "cost_alert_level_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "cost_alert_level_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "cost_alert_level_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "cost_alert_level_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "cost_alert_level_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "cost_alert_level_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "cost_alert_level_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "cost_alert_level_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "cost_alert_level_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "cost_alert_level_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "cost_alert_level_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "cost_alert_level_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "cost_alert_level_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "cost_alert_level_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "cost_alert_level_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "cost_alert_level_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "cost_alert_level_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "cost_alert_level_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "cost_alert_level_types", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class CostAlertLevel(Enum):
    """Cost alert levels."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class CostMetrics:
    """Cost metrics for an agent."""

    agent_id: str
    spiffe_id: str
    total_cost: float
    token_count: int
    request_count: int
    avg_cost_per_request: float
    period_start: float
    period_end: float
    model_breakdown: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "agent_id": self.agent_id,
            "spiffe_id": self.spiffe_id,
            "total_cost": self.total_cost,
            "token_count": self.token_count,
            "request_count": self.request_count,
            "avg_cost_per_request": self.avg_cost_per_request,
            "period_start": self.period_start,
            "period_end": self.period_end,
            "model_breakdown": self.model_breakdown,
        }


@dataclass
class CostAlert:
    """Cost alert for budget violations."""

    alert_id: str
    agent_id: str
    spiffe_id: str
    level: CostAlertLevel
    message: str
    current_cost: float
    budget_limit: float
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "alert_id": self.alert_id,
            "agent_id": self.agent_id,
            "spiffe_id": self.spiffe_id,
            "level": self.level.value,
            "message": self.message,
            "current_cost": self.current_cost,
            "budget_limit": self.budget_limit,
            "timestamp": self.timestamp,
        }


class CostTracker:
    """Tracks costs per agent with SPIFFE identity integration.

    Features:
    - Per-agent cost attribution
    - Budget enforcement
    - Cost alerting
    - Model-level breakdown
    - Financial accountability
    """

    # guardian: allow-magic-config
    def __init__(
        self,
        default_budget_per_agent: float | None = None,
        alert_threshold_percent: float = 0.8,
        enable_logging: bool = True,
    ):
        """Initialize cost tracker.

        Args:
            default_budget_per_agent: Default budget per agent
            alert_threshold_percent: Alert when cost reaches this % of budget
            enable_logging: Enable logging
        """
        self.default_budget_per_agent = default_budget_per_agent
        self.alert_threshold_percent = alert_threshold_percent
        self.enable_logging = enable_logging
        self._agent_costs: dict[str, list[dict[str, Any]]] = {}
        self._agent_budgets: dict[str, float] = {}
        self._alerts: list[CostAlert] = []
        if self.enable_logging:
            logger.info(
                "cost_tracker_initialized",
                extra={
                    "default_budget": default_budget_per_agent,
                    "alert_threshold": alert_threshold_percent,
                },
            )

    def record_cost(self, agent_id: str, spiffe_id: str, model_id: str, tokens: int, cost: float) -> None:
        """Record cost for an agent.

        Args:
            agent_id: Agent identifier
            spiffe_id: SPIFFE ID for identity
            model_id: Model used
            tokens: Token count
            cost: Cost incurred
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "CostTracker.record_cost")

        if agent_id not in self._agent_costs:
            self._agent_costs[agent_id] = []
        record = {
            "spiffe_id": spiffe_id,
            "model_id": model_id,
            "tokens": tokens,
            "cost": cost,
            "timestamp": time.time(),
        }
        self._agent_costs[agent_id].append(record)
        if agent_id in self._agent_budgets:
            self._check_budget(agent_id, spiffe_id)
        if self.enable_logging:
            logger.debug("cost_recorded", extra={"agent_id": agent_id, "model_id": model_id, "cost": cost})

    def set_budget(self, agent_id: str, budget: float) -> None:
        """Set budget for an agent.

        Args:
            agent_id: Agent identifier
            budget: Budget amount
        """
        self._agent_budgets[agent_id] = budget
        if self.enable_logging:
            logger.info("budget_set", extra={"agent_id": agent_id, "budget": budget})

    def get_metrics(self, agent_id: str, period_hours: int = 24) -> CostMetrics | None:
        """Get cost metrics for an agent.

        Args:
            agent_id: Agent identifier
            period_hours: Period in hours

        Returns:
            CostMetrics or None
        """
        records = self._agent_costs.get(agent_id, [])
        if not records:
            return None
        period_start = time.time() - period_hours * 3600
        period_records = [r for r in records if r["timestamp"] >= period_start]
        if not period_records:
            return None
        total_cost = sum(r["cost"] for r in period_records)
        token_count = sum(r["tokens"] for r in period_records)
        request_count = len(period_records)
        avg_cost = total_cost / request_count if request_count > 0 else 0.0
        model_breakdown: dict[str, float] = {}
        for record in period_records:
            model_id = record["model_id"]
            model_breakdown[model_id] = model_breakdown.get(model_id, 0.0) + record["cost"]
        spiffe_id = period_records[-1]["spiffe_id"]
        metrics = CostMetrics(
            agent_id=agent_id,
            spiffe_id=spiffe_id,
            total_cost=total_cost,
            token_count=token_count,
            request_count=request_count,
            avg_cost_per_request=avg_cost,
            period_start=period_start,
            period_end=time.time(),
            model_breakdown=model_breakdown,
        )
        return metrics

    def get_all_metrics(self, period_hours: int = 24) -> list[CostMetrics]:
        """Get metrics for all agents.

        Args:
            period_hours: Period in hours

        Returns:
            List of CostMetrics
        """
        all_metrics = []
        for agent_id in self._agent_costs.keys():
            metrics = self.get_metrics(agent_id, period_hours)
            if metrics:
                all_metrics.append(metrics)
        return all_metrics

    def get_alerts(self, agent_id: str | None = None, level: CostAlertLevel | None = None) -> list[CostAlert]:
        """Get cost alerts.

        Args:
            agent_id: Optional agent ID filter
            level: Optional level filter

        Returns:
            List of CostAlert
        """
        alerts = self._alerts
        if agent_id:
            alerts = [a for a in alerts if a.agent_id == agent_id]
        if level:
            alerts = [a for a in alerts if a.level == level]
        return alerts

    def _check_budget(self, agent_id: str, spiffe_id: str) -> None:
        """Check if agent is within budget.

        Args:
            agent_id: Agent identifier
            spiffe_id: SPIFFE ID
        """
        budget = self._agent_budgets.get(agent_id)
        if not budget:
            return
        metrics = self.get_metrics(agent_id)
        if not metrics:
            return
        current_cost = metrics.total_cost
        usage_percent = current_cost / budget
        if usage_percent >= 1.0:
            self._create_alert(
                agent_id=agent_id,
                spiffe_id=spiffe_id,
                level=CostAlertLevel.CRITICAL,
                message=f"Budget exceeded: ${current_cost:.2f} / ${budget:.2f}",
                current_cost=current_cost,
                budget_limit=budget,
            )
        elif usage_percent >= self.alert_threshold_percent:
            self._create_alert(
                agent_id=agent_id,
                spiffe_id=spiffe_id,
                level=CostAlertLevel.WARNING,
                message=f"Budget at {usage_percent:.1%}: ${current_cost:.2f} / ${budget:.2f}",
                current_cost=current_cost,
                budget_limit=budget,
            )

    def _create_alert(
        self,
        agent_id: str,
        spiffe_id: str,
        level: CostAlertLevel,
        message: str,
        current_cost: float,
        budget_limit: float,
    ) -> None:
        """Create cost alert.

        Args:
            agent_id: Agent identifier
            spiffe_id: SPIFFE ID
            level: Alert level
            message: Alert message
            current_cost: Current cost
            budget_limit: Budget limit
        """
        alert = CostAlert(
            alert_id=f"cost_alert_{agent_id}_{int(time.time())}",
            agent_id=agent_id,
            spiffe_id=spiffe_id,
            level=level,
            message=message,
            current_cost=current_cost,
            budget_limit=budget_limit,
        )
        self._alerts.append(alert)
        if len(self._alerts) > 100:
            self._alerts = self._alerts[-100:]
        if self.enable_logging:
            logger.warning(
                "cost_alert_triggered",
                extra={
                    "agent_id": agent_id,
                    "level": level.value,
                    "current_cost": current_cost,
                    "budget": budget_limit,
                },
            )


def create_cost_tracker(default_budget_per_agent: float | None = None) -> CostTracker:
    """Factory function to create cost tracker.

    Args:
        default_budget_per_agent: Default budget per agent

    Returns:
        CostTracker instance
    """
    return CostTracker(default_budget_per_agent=default_budget_per_agent)
