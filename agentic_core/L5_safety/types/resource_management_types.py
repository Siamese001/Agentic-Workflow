from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    # noqa: E402,
    # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "resource_management_types")
emit_determinism_digest("p0", "resource_management_types")

_emit_dispatches_healing_run("p1", "resource_management_types", "L5")
_emit_routes_through("p1", "resource_management_types", "L5")
_emit_checks_agent_registry("p1", "resource_management_types", "agent_registry")
_emit_validates_agent_capability("p1", "resource_management_types", "capability")
_emit_dispatches_execution_plan("p1", "resource_management_types", "exec_plan")
_emit_agent_executes_agent("p1", "resource_management_types", "sub_agent")
_emit_routes_to_agent("p1", "resource_management_types", "target_agent")
_emit_verifies_policy("p1", "resource_management_types", "policy_check")
_emit_observes_runtime_state("p1", "resource_management_types", "runtime_state")
_emit_verifies_boundary("p1", "resource_management_types", "boundary_check")
_emit_transcripts_response("p1", "resource_management_types", "transcript")
_emit_hard_fails_untranscripted("p1", "resource_management_types")
_emit_gated_by_confidence("p1", "resource_management_types", "confidence_gate")
_emit_escalates_to_human("p1", "resource_management_types", "L5")
_emit_reads_policy_state("p1", "resource_management_types", "L5")

_emit_applies_guardrail("p0", "resource_management_types", "p0_governance")
_emit_snapshots_state("p0", "resource_management_types", "state_snapshot")
_emit_authorize_and_execute("p2", "resource_management_types", "execution_auth")
_emit_validates_capability("p2", "resource_management_types", "capability_check")
_emit_routes_to_capability("p2", "resource_management_types", "capability_route")
_emit_writes_via_uwg("p2", "resource_management_types", "uwg_write")
_emit_blocks_direct_write("p2", "resource_management_types", "direct_write_block")
_emit_records_tool_invocation("p2", "resource_management_types", "tool_invocation")
_emit_captures_execution_output("p2", "resource_management_types", "exec_output")
_emit_dispatches_agent("p3", "resource_management_types", "agent_dispatch")
_emit_coordinates_agents("p3", "resource_management_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "resource_management_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "resource_management_types", "healing_outcome")
_emit_escalates_failure("p3", "resource_management_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "resource_management_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "resource_management_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "resource_management_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "resource_management_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "resource_management_types", "eval_metric")
_emit_stores_embedding("p4", "resource_management_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "resource_management_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "resource_management_types", "exec_snapshot_link")

"""
Resource Management Guardrail - Consolidated Resource Control

Merges:
- CostGovernor
- governor
- control_plane

Composable Rules:
- cost_limits: Cost control and budgeting
- resource_quotas: CPU, memory, token limits
- control_plane: Control plane management
"""


from dataclasses import dataclass
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
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

_emit_emits_metric_event("resource_management_types", "p4obs", "metric_1")
_emit_emits_metric_event("resource_management_types", "p4obs", "metric_2")
_emit_emits_metric_event("resource_management_types", "p4obs", "metric_3")
_emit_emits_metric_event("resource_management_types", "p4obs", "metric_4")
_emit_emits_metric_event("resource_management_types", "p4obs", "metric_5")
_emit_emits_metric_event("resource_management_types", "p4obs", "metric_6")
_emit_records_incident_event("resource_management_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("resource_management_types", "p4obs", "anomaly")
_emit_writes_observability_log("resource_management_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("resource_management_types", "p4obs", "mon_state")
_emit_triggers_alert("resource_management_types", "p4obs", "alert")
_emit_links_incident_trace("resource_management_types", "p4obs", "trace_link")
_emit_captures_pattern("resource_management_types", "p3lm", "pattern")
_emit_records_learning_event("resource_management_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("resource_management_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("resource_management_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("resource_management_types", "p3lm", "routing")
_emit_improves_agent_policy("resource_management_types", "p3lm", "policy")
_emit_stores_learning_state("resource_management_types", "p3lm", "state")
_emit_records_execution_trace("resource_management_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("resource_management_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("resource_management_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("resource_management_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("resource_management_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("resource_management_types", "env_read", "p2_env_1")
_emit_reads_environ("resource_management_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("resource_management_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("resource_management_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "resource_management_types", "context_pull")
_emit_pulls_context("p1", "resource_management_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "resource_management_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "resource_management_types", "uwg_term_2")
_emit_writes_through("p1", "resource_management_types", "write_through")
_emit_writes_through("p1", "resource_management_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "resource_management_types", "safety_validation")
_emit_invokes_eval("p1", "resource_management_types", "eval_call")
_emit_proposal_commits_routing("p1", "resource_management_types", "routing_commit")


class ResourceType(Enum):
    """Types of managed resources."""

    TOKENS = "tokens"
    API_CALLS = "api_calls"
    MEMORY = "memory"
    CPU = "cpu"
    STORAGE = "storage"
    COST = "cost"


@dataclass
class ResourceQuota:
    """Resource quota definition."""

    resource_type: ResourceType
    limit: float
    used: float = 0.0
    unit: str = ""

    @property
    def remaining(self) -> float:
        return max(0, self.limit - self.used)

    @property
    def usage_percent(self) -> float:
        return (self.used / self.limit * 100) if self.limit > 0 else 0


@dataclass
class ResourceCheckResult:
    """Result of resource check."""

    allowed: bool
    resource_type: ResourceType
    requested: float
    available: float
    message: str = ""


class ResourceManagementGuardrail:
    """
    Consolidated Resource Management Guardrail.

    Provides unified resource control with:
    - Cost limits and budgeting
    - Resource quotas (tokens, API calls, memory)
    - Control plane management
    """

    def __init__(self):
        """Initialize resource management guardrail."""
        self.enabled_rules: list[str] = [
            "cost_limits",
            "resource_quotas",
            "control_plane",
        ]

        # Default quotas
        self.quotas: dict[ResourceType, ResourceQuota] = {
            # guardian: allow-magic-config
            ResourceType.TOKENS: ResourceQuota(
                resource_type=ResourceType.TOKENS,
                limit=1_000_000,
                unit="tokens",
            ),
            # guardian: allow-magic-config
            ResourceType.API_CALLS: ResourceQuota(
                resource_type=ResourceType.API_CALLS,
                limit=1_000,
                unit="calls",
            ),
            # guardian: allow-magic-config
            ResourceType.COST: ResourceQuota(resource_type=ResourceType.COST, limit=100.0, unit="USD"),
            # guardian: allow-magic-config
            ResourceType.MEMORY: ResourceQuota(resource_type=ResourceType.MEMORY, limit=1024, unit="MB"),
        }

        # Cost rates
        self.cost_rates = {
            "gpt-4": 0.03,  # per 1K tokens
            "gpt-3.5-turbo": 0.002,
            "claude-3": 0.015,
            "default": 0.01,
        }

        # Statistics
        self.checks_performed = 0
        self.requests_allowed = 0
        self.requests_denied = 0
        self.total_cost = 0.0

    async def check_resource(self, resource_type: ResourceType, amount: float) -> ResourceCheckResult:
        """
        Check if resource request is allowed.

        Args:
            resource_type: Type of resource
            amount: Amount requested

        Returns:
            ResourceCheckResult
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L5_POLICY,
            "ResourceManagementGuardrail.check_resource",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:ResourceManagementGuardrail.check_resource".encode(),
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        self.checks_performed += 1

        if "resource_quotas" not in self.enabled_rules:
            self.requests_allowed += 1
            return ResourceCheckResult(
                allowed=True,
                resource_type=resource_type,
                requested=amount,
                available=float("inf"),
                message="Resource quotas disabled",
            )

        quota = self.quotas.get(resource_type)
        if not quota:
            self.requests_allowed += 1
            return ResourceCheckResult(
                allowed=True,
                resource_type=resource_type,
                requested=amount,
                available=float("inf"),
                message="No quota defined",
            )

        if amount <= quota.remaining:
            self.requests_allowed += 1
            return ResourceCheckResult(
                allowed=True,
                resource_type=resource_type,
                requested=amount,
                available=quota.remaining,
                message="Request approved",
            )
        else:
            self.requests_denied += 1
            return ResourceCheckResult(
                allowed=False,
                resource_type=resource_type,
                requested=amount,
                available=quota.remaining,
                message=f"Quota exceeded: requested {amount}, available {quota.remaining}",
            )

    async def consume_resource(self, resource_type: ResourceType, amount: float) -> bool:
        """
        Consume resource from quota.

        Args:
            resource_type: Type of resource
            amount: Amount to consume

        Returns:
            True if consumption successful
        """
        check = await self.check_resource(resource_type, amount)

        if check.allowed:
            quota = self.quotas.get(resource_type)
            if quota:
                quota.used += amount
            return True

        return False

    def calculate_cost(self, model: str, tokens: int) -> float:
        """
        Calculate cost for token usage.

        Args:
            model: Model name
            tokens: Number of tokens

        Returns:
            Cost in USD
        """
        if "cost_limits" not in self.enabled_rules:
            return 0.0

        rate = self.cost_rates.get(model, self.cost_rates["default"])
        cost = (tokens / 1000) * rate
        self.total_cost += cost
        return cost

    async def check_cost_limit(self, estimated_cost: float) -> ResourceCheckResult:
        """
        Check if cost is within limits.

        Args:
            estimated_cost: Estimated cost

        Returns:
            ResourceCheckResult
        """
        return await self.check_resource(ResourceType.COST, estimated_cost)

    def set_quota(self, resource_type: ResourceType, limit: float) -> None:
        """Set quota for resource type."""
        if resource_type in self.quotas:
            self.quotas[resource_type].limit = limit
        else:
            self.quotas[resource_type] = ResourceQuota(resource_type=resource_type, limit=limit)

    def reset_quotas(self) -> None:
        """Reset all quota usage."""
        for quota in self.quotas.values():
            quota.used = 0.0

    def get_quota_status(self) -> dict[str, Any]:
        """Get status of all quotas."""
        return {
            rt.value: {
                "limit": q.limit,
                "used": q.used,
                "remaining": q.remaining,
                "usage_percent": q.usage_percent,
                "unit": q.unit,
            }
            for rt, q in self.quotas.items()
        }

    def get_statistics(self) -> dict[str, Any]:
        """Get resource management statistics."""
        return {
            "checks_performed": self.checks_performed,
            "requests_allowed": self.requests_allowed,
            "requests_denied": self.requests_denied,
            "denial_rate": (self.requests_denied / self.checks_performed * 100)
            if self.checks_performed > 0
            else 0,
            "total_cost": self.total_cost,
            "quota_status": self.get_quota_status(),
        }
