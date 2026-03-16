"""Pytest configuration for sovereign hardening test suite."""

import os

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,
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
    _emit_reads_policy_state,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
)

_emit_records_execution_trace("p0", "evidence", "conftest_sovereign_hardening")
_emit_applies_guardrail("p0", "conftest_sovereign_hardening", "p0_governance")
_emit_reads_policy_state("p0", "conftest_sovereign_hardening", "policy_binding")
_emit_snapshots_state("p0", "conftest_sovereign_hardening", "state_snapshot")
emit_replay_key("p0", "conftest_sovereign_hardening")
emit_determinism_digest("p0", "conftest_sovereign_hardening")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "conftest", "execution_auth")
_emit_validates_capability("p2", "conftest", "capability_check")
_emit_routes_to_capability("p2", "conftest", "capability_route")
_emit_writes_via_uwg("p2", "conftest", "uwg_write")
_emit_blocks_direct_write("p2", "conftest", "direct_write_block")
_emit_records_tool_invocation("p2", "conftest", "tool_invocation")
_emit_captures_execution_output("p2", "conftest", "exec_output")
_emit_dispatches_agent("p3", "conftest", "agent_dispatch")
_emit_coordinates_agents("p3", "conftest", "agent_coordination")
_emit_records_workflow_lineage("p3", "conftest", "workflow_lineage")
_emit_records_healing_outcome("p3", "conftest", "healing_outcome")
_emit_escalates_failure("p3", "conftest", "failure_escalation")
_emit_orchestrates_workflow("p3", "conftest", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "conftest", "healing_dispatch")
_emit_invokes_evaluation("p3", "conftest", "evaluation_signal")
_emit_records_telemetry_event("p4", "conftest", "telemetry_event")
_emit_captures_evaluation_metric("p4", "conftest", "eval_metric")
_emit_stores_embedding("p4", "conftest", "embedding_store")
_emit_updates_meta_learning_state("p4", "conftest", "meta_learning")
_emit_links_execution_to_snapshot("p4", "conftest", "exec_snapshot_link")

from agentic_core.L2_execution.enforcement.key_source import (
    TestKeySource,
    inject_key_source,
)
from agentic_core.L2_execution.UniversalWriteGateway import reset_write_gateway


@pytest.fixture(scope="function", autouse=True)
def inject_test_key_source():
    """Inject TestKeySource before every test so SandboxEnvelope construction works."""
    inject_key_source(TestKeySource())
    yield
    # Reset to None so tests do not leak into each other
    import agentic_core.L2_execution.enforcement.key_source as _ks

    _ks._injected_key_source = None


@pytest.fixture(scope="function", autouse=True)
def reset_write_gateway_fixture():
    """Reset write gateway before each test."""
    reset_write_gateway()
    yield
    reset_write_gateway()


@pytest.fixture(scope="function")
def tamper_env():
    """Fixture to temporarily enable W_HARDEN_NEGCTRL_TAMPER."""
    original_value = os.environ.get("W_HARDEN_NEGCTRL_TAMPER")
    os.environ["W_HARDEN_NEGCTRL_TAMPER"] = "1"
    yield
    if original_value is None:
        os.environ.pop("W_HARDEN_NEGCTRL_TAMPER", None)
    else:
        os.environ["W_HARDEN_NEGCTRL_TAMPER"] = original_value


@pytest.fixture(scope="function")
def clean_env():
    """Fixture to ensure clean environment (no tampering)."""
    original_value = os.environ.get("W_HARDEN_NEGCTRL_TAMPER")
    os.environ.pop("W_HARDEN_NEGCTRL_TAMPER", None)
    yield
    if original_value is not None:
        os.environ["W_HARDEN_NEGCTRL_TAMPER"] = original_value


def pytest_configure(config):
    """Configure pytest for sovereign hardening tests."""
    # Add custom markers
    config.addinivalue_line("markers", "negative_control: Tests that use W_HARDEN_NEGCTRL_TAMPER")
    config.addinivalue_line("markers", "determinism: Tests for determinism validation")
    config.addinivalue_line("markers", "sovereignty: Tests for sovereignty enforcement")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names.

    Adds sovereign_hardening marker to every item in this suite so the
    global conftest default-marker filter does not deselect them.
    """
    sovereign_marker = pytest.mark.sovereign_hardening
    for item in items:
        # Only process items from this suite
        if "sovereign_hardening" not in str(item.fspath):
            continue
        # Always add sovereign_hardening so global filter passes it through
        item.add_marker(sovereign_marker)
        if "negative_control" in item.name or "tamper" in item.name.lower():
            item.add_marker(pytest.mark.negative_control)
        if "determinism" in item.name.lower():
            item.add_marker(pytest.mark.determinism)
        if "sovereignty" in item.name.lower() or "boundary" in item.name.lower():
            item.add_marker(pytest.mark.sovereignty)
