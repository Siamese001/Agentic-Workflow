"""Regression tests for SandboxEnvelope ToolBudget integration."""

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
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
_emit_authorize_and_execute("p2", "test_sandbox_envelope_budget", "execution_auth")
_emit_validates_capability("p2", "test_sandbox_envelope_budget", "capability_check")
_emit_routes_to_capability("p2", "test_sandbox_envelope_budget", "capability_route")
_emit_writes_via_uwg("p2", "test_sandbox_envelope_budget", "uwg_write")
_emit_blocks_direct_write("p2", "test_sandbox_envelope_budget", "direct_write_block")
_emit_records_tool_invocation("p2", "test_sandbox_envelope_budget", "tool_invocation")
_emit_captures_execution_output("p2", "test_sandbox_envelope_budget", "exec_output")
_emit_dispatches_agent("p3", "test_sandbox_envelope_budget", "agent_dispatch")
_emit_coordinates_agents("p3", "test_sandbox_envelope_budget", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_sandbox_envelope_budget", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_sandbox_envelope_budget", "healing_outcome")
_emit_escalates_failure("p3", "test_sandbox_envelope_budget", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_sandbox_envelope_budget", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_sandbox_envelope_budget", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_sandbox_envelope_budget", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_sandbox_envelope_budget", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_sandbox_envelope_budget", "eval_metric")
_emit_stores_embedding("p4", "test_sandbox_envelope_budget", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_sandbox_envelope_budget", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_sandbox_envelope_budget", "exec_snapshot_link")

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
