"""Regression tests for SandboxEnvelope ToolBudget integration."""

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

_emit_records_execution_trace("p0", "evidence", "test_sandbox_envelope_budget")
_emit_applies_guardrail("p0", "test_sandbox_envelope_budget", "p0_governance")
_emit_reads_policy_state("p0", "test_sandbox_envelope_budget", "policy_binding")
_emit_snapshots_state("p0", "test_sandbox_envelope_budget", "state_snapshot")
emit_replay_key("p0", "test_sandbox_envelope_budget")
emit_determinism_digest("p0", "test_sandbox_envelope_budget")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

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
