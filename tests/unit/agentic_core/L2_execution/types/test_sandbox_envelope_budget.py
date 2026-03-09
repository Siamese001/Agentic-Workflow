"""Regression tests for SandboxEnvelope ToolBudget integration."""

import pytest

pytestmark = pytest.mark.unit_min_deps

"""Regression: SandboxEnvelope must carry ToolBudget in signable surface."""
from agentic_core.L2_execution.enforcement.key_source import (
    TestKeySource,
    inject_key_source,
)
from agentic_core.L2_execution.types.sandbox_envelope_types import (
    SandboxEnvelope,
    ToolBudget,
)

inject_key_source(TestKeySource())


def _make_env(**kwargs) -> SandboxEnvelope:
    defaults = {"envelope_id": "e1", "tool_name": "test_tool"}
    return SandboxEnvelope(**{**defaults, **kwargs})


def test_default_budget_present():
    env = _make_env()
    assert env.budget.compute_ms > 0
    assert env.budget.memory_mb > 0
    assert env.budget.stdout_bytes > 0


def test_custom_budget_in_signable_dict():
    budget = ToolBudget(compute_ms=5000, memory_mb=64, stdout_bytes=1024)
    env = _make_env(budget=budget)
    sd = env._signable_dict()
    assert sd["budget"] == {"compute_ms": 5000, "memory_mb": 64, "stdout_bytes": 1024}


def test_budget_bound_in_signature():
    env1 = _make_env(budget=ToolBudget(compute_ms=1000, memory_mb=32, stdout_bytes=512))
    env2 = _make_env(budget=ToolBudget(compute_ms=9000, memory_mb=32, stdout_bytes=512))
    assert env1.signature != env2.signature


def test_zero_budget_rejected():
    with pytest.raises(ValueError):
        ToolBudget(compute_ms=0, memory_mb=64, stdout_bytes=1024)


def test_verify_passes_with_budget():
    secret = TestKeySource.TEST_SECRET
    env = _make_env(budget=ToolBudget(compute_ms=5000, memory_mb=64, stdout_bytes=1024))
    env.verify(secret)  # must not raise
    assert True  # no-exception contract
