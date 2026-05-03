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


import sys
from pathlib import Path

import pytest

# REMOVED: _emit_records_execution_trace("p0", "evidence", "conftest_unit_min_deps")
# REMOVED: _emit_applies_guardrail("p0", "conftest_unit_min_deps", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "conftest_unit_min_deps", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "conftest_unit_min_deps", "state_snapshot")

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
# REMOVED: emit_replay_key("p0", "conftest_unit_min_deps")
# REMOVED: emit_determinism_digest("p0", "conftest_unit_min_deps")
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

# Add project root to allow absolute imports
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(autouse=True)
def _inject_test_key_source():
    """Inject a deterministic TestKeySource for all unit_min_deps tests."""
    from agentic_core.L2_execution.enforcement.key_source import (
        TestKeySource,
        inject_key_source,
    )

    inject_key_source(TestKeySource())
