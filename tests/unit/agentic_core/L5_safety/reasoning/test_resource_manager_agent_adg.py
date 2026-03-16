"""ADG-driven tests for agentic_core/L5_safety/reasoning/ResourceManagerAgent.py — fan_in=2.

Contract tests: ResourceType, AllocationStatus, ResourceAllocation, ResourceBudget,
ResourceConfig, ResourceManagerAgent init and allocation API.
"""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_resource_manager_agent_adg")
_emit_applies_guardrail("p0", "test_resource_manager_agent_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_resource_manager_agent_adg", "policy_binding")
_emit_snapshots_state("p0", "test_resource_manager_agent_adg", "state_snapshot")
emit_replay_key("p0", "test_resource_manager_agent_adg")
emit_determinism_digest("p0", "test_resource_manager_agent_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.reasoning.ResourceManagerAgent import (
    AllocationStatus,
    ResourceAllocation,
    ResourceBudget,
    ResourceConfig,
    ResourceManagerAgent,
    ResourceType,
)


class TestResourceType:
    def test_all_members_present(self):
        names = {e.name for e in ResourceType}
        assert {"BUDGET", "MEMORY", "CPU", "API_CALLS", "TOKENS"} == names


class TestAllocationStatus:
    def test_all_members_present(self):
        names = {e.name for e in AllocationStatus}
        assert {"ALLOCATED", "DENIED", "FALLBACK", "EXHAUSTED"} == names


class TestResourceAllocation:
    def test_creates_valid(self):
        alloc = ResourceAllocation(
            resource_type=ResourceType.BUDGET,
            amount=100.0,
            agent_id="agent_1",
        )
        assert alloc.resource_type == ResourceType.BUDGET
        assert alloc.amount == 100.0
        assert alloc.status == AllocationStatus.ALLOCATED

    def test_custom_status(self):
        alloc = ResourceAllocation(
            resource_type=ResourceType.TOKENS,
            amount=50.0,
            agent_id="agent_2",
            status=AllocationStatus.DENIED,
        )
        assert alloc.status == AllocationStatus.DENIED


class TestResourceBudget:
    def test_creates_valid(self):
        budget = ResourceBudget(resource_type=ResourceType.BUDGET, total=1000.0)
        assert budget.total == 1000.0
        assert budget.used == 0.0

    def test_available_calculation(self):
        budget = ResourceBudget(resource_type=ResourceType.BUDGET, total=1000.0, used=300.0, reserved=100.0)
        assert budget.available == 600.0

    def test_utilization_calculation(self):
        budget = ResourceBudget(resource_type=ResourceType.BUDGET, total=1000.0, used=800.0)
        assert budget.utilization == 0.8

    def test_is_exhausted_when_full(self):
        budget = ResourceBudget(resource_type=ResourceType.BUDGET, total=100.0, used=100.0)
        assert budget.is_exhausted is True

    def test_not_exhausted_when_available(self):
        budget = ResourceBudget(resource_type=ResourceType.BUDGET, total=100.0, used=50.0)
        assert budget.is_exhausted is False

    def test_available_clamps_to_zero(self):
        budget = ResourceBudget(resource_type=ResourceType.BUDGET, total=100.0, used=150.0)
        assert budget.available == 0.0

    def test_utilization_zero_when_total_zero(self):
        budget = ResourceBudget(resource_type=ResourceType.BUDGET, total=0.0)
        assert budget.utilization == 0.0


class TestResourceConfig:
    def test_defaults(self):
        cfg = ResourceConfig()
        assert cfg.enable_hard_caps is True
        assert cfg.enable_proactive_allocation is True
        assert cfg.enable_fallback is True
        assert cfg.max_concurrent_allocations == 100

    def test_fallback_strategies_nonempty(self):
        cfg = ResourceConfig()
        assert len(cfg.fallback_strategies) > 0


class TestResourceManagerAgentInit:
    def test_creates_without_args(self):
        agent = ResourceManagerAgent()
        assert agent is not None

    def test_config_defaults_applied(self):
        agent = ResourceManagerAgent()
        assert isinstance(agent._agent_config, ResourceConfig)

    def test_budgets_start_empty(self):
        agent = ResourceManagerAgent()
        assert agent._budgets == {}

    def test_set_budget_method_exists(self):
        assert callable(ResourceManagerAgent.set_budget)

    def test_allocate_method_exists(self):
        assert callable(ResourceManagerAgent.allocate)

    def test_is_exhausted_method_exists(self):
        assert callable(ResourceManagerAgent.is_exhausted)


class TestResourceManagerAgentAPI:
    def setup_method(self):
        self.agent = ResourceManagerAgent()

    def test_set_and_query_budget(self):
        self.agent.set_budget(ResourceType.BUDGET, total=1000.0)
        budget = self.agent._budgets.get(ResourceType.BUDGET)
        assert budget is not None
        assert budget.total == 1000.0

    def test_allocate_returns_allocation(self):
        self.agent.set_budget(ResourceType.TOKENS, total=1000.0)
        result = self.agent.allocate("agent_x", ResourceType.TOKENS, 100.0)
        assert isinstance(result, ResourceAllocation)

    def test_allocate_reduces_available(self):
        self.agent.set_budget(ResourceType.TOKENS, total=1000.0)
        self.agent.allocate("agent_x", ResourceType.TOKENS, 400.0)
        assert self.agent._budgets[ResourceType.TOKENS].used == 400.0

    def test_is_exhausted_false_initially(self):
        self.agent.set_budget(ResourceType.BUDGET, total=1000.0)
        assert self.agent.is_exhausted(ResourceType.BUDGET) is False

    def test_heal_repository_returns_dict(self):
        result = self.agent.heal_repository(dry_run=True)
        assert isinstance(result, dict)
        assert "violations" in result
