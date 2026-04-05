# Core pytest configuration
import pytest


# Standard fixtures for path semantics
@pytest.fixture
def test_data_path():
    """Fixture for test data path."""
    from pathlib import Path
    return Path(__file__).parent / "test_data"

@pytest.fixture
def temp_project_dir(tmp_path):
    """Fixture for temporary project directory."""
    return tmp_path / "project"

# Test collection configuration
def pytest_configure(config):
    """Configure pytest with custom settings."""
    config.addinivalue_line("markers", "data: marks tests as data-dependent")

# Core pytest configuration
import pytest


# Standard fixtures for path semantics
@pytest.fixture
def test_data_path():
    """Fixture for test data path."""
    from pathlib import Path
    return Path(__file__).parent / "test_data"

@pytest.fixture
def temp_project_dir(tmp_path):
    """Fixture for temporary project directory."""
    return tmp_path / "project"

# Test collection configuration
def pytest_configure(config):
    """Configure pytest with custom settings."""
    config.addinivalue_line("markers", "data: marks tests as data-dependent")

"""Pytest configuration for sovereign hardening test suite."""

import os

import pytest

# REMOVED: _emit_records_execution_trace("p0", "evidence", "conftest_sovereign_hardening")
# REMOVED: _emit_applies_guardrail("p0", "conftest_sovereign_hardening", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "conftest_sovereign_hardening", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "conftest_sovereign_hardening", "state_snapshot")
# REMOVED: emit_replay_key("p0", "conftest_sovereign_hardening")
# REMOVED: emit_determinism_digest("p0", "conftest_sovereign_hardening")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "conftest", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "conftest", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "conftest", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "conftest", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "conftest", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "conftest", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "conftest", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "conftest", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "conftest", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "conftest", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "conftest", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "conftest", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "conftest", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "conftest", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "conftest", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "conftest", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "conftest", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "conftest", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "conftest", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "conftest", "exec_snapshot_link")
from agentic_core.L2_execution.enforcement.key_source import (
    TestKeySource,
    inject_key_source,
)
from agentic_core.L2_execution.UniversalWriteGateway import reset_write_gateway

# REMOVED: _emit_emits_metric_event("conftest", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("conftest", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("conftest", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("conftest", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("conftest", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("conftest", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("conftest", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("conftest", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("conftest", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("conftest", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("conftest", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("conftest", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("conftest", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("conftest", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("conftest", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("conftest", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("conftest", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("conftest", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("conftest", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("conftest", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("conftest", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("conftest", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("conftest", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("conftest", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("conftest", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("conftest", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("conftest", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("conftest", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "conftest", "context_pull")
# REMOVED: _emit_pulls_context("p1", "conftest", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "conftest", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "conftest", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "conftest", "write_through")
# REMOVED: _emit_writes_through("p1", "conftest", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "conftest", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "conftest", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "conftest", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "conftest", "human_escalation")
# REMOVED: _emit_routes_through("p1", "conftest", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "conftest", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "conftest", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "conftest", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "conftest", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "conftest", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "conftest", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "conftest", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "conftest", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "conftest", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "conftest")
# REMOVED: _emit_gated_by_confidence("p1", "conftest", "confidence_gate")


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
