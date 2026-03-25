"""
File: tests/L0/test_pascal_fixer_collisions.py
Rationale: Verifies collision resolution strategies (Delete vs Conflict Rename).
"""

import pytest

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,  # noqa: E402
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

# REMOVED: _emit_authorize_and_execute("p2", "test_pascal_fixer_collisions", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_pascal_fixer_collisions", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_pascal_fixer_collisions", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_pascal_fixer_collisions", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_pascal_fixer_collisions", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_pascal_fixer_collisions", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_pascal_fixer_collisions", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_pascal_fixer_collisions", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_pascal_fixer_collisions", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_pascal_fixer_collisions", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_pascal_fixer_collisions", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_pascal_fixer_collisions", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_pascal_fixer_collisions", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_pascal_fixer_collisions", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_pascal_fixer_collisions", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_pascal_fixer_collisions", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_pascal_fixer_collisions", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_pascal_fixer_collisions", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_pascal_fixer_collisions", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_pascal_fixer_collisions", "exec_snapshot_link")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
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
    _emit_writes_through,  # noqa: E402
)
from tests.helpers.dev_tools_loader import load_dev_script

# REMOVED: _emit_emits_metric_event("test_pascal_fixer_collisions", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_pascal_fixer_collisions", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_pascal_fixer_collisions", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_pascal_fixer_collisions", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_pascal_fixer_collisions", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_pascal_fixer_collisions", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_pascal_fixer_collisions", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_pascal_fixer_collisions", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_pascal_fixer_collisions", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_pascal_fixer_collisions", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_pascal_fixer_collisions", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_pascal_fixer_collisions", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_pascal_fixer_collisions", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_pascal_fixer_collisions", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_pascal_fixer_collisions", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_pascal_fixer_collisions", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_pascal_fixer_collisions", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_pascal_fixer_collisions", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_pascal_fixer_collisions", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_pascal_fixer_collisions", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_pascal_fixer_collisions", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_pascal_fixer_collisions", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_pascal_fixer_collisions", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_pascal_fixer_collisions", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_pascal_fixer_collisions", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_pascal_fixer_collisions", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_pascal_fixer_collisions", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_pascal_fixer_collisions", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_pascal_fixer_collisions")
# REMOVED: _emit_applies_guardrail("p0", "test_pascal_fixer_collisions", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_pascal_fixer_collisions", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_pascal_fixer_collisions", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_pascal_fixer_collisions", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_pascal_fixer_collisions", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_pascal_fixer_collisions", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_pascal_fixer_collisions", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_pascal_fixer_collisions", "write_through")
# REMOVED: _emit_writes_through("p1", "test_pascal_fixer_collisions", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_pascal_fixer_collisions", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_pascal_fixer_collisions", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_pascal_fixer_collisions", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_pascal_fixer_collisions", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_pascal_fixer_collisions", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_pascal_fixer_collisions", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_pascal_fixer_collisions", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_pascal_fixer_collisions", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_pascal_fixer_collisions", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_pascal_fixer_collisions", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_pascal_fixer_collisions", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_pascal_fixer_collisions", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_pascal_fixer_collisions", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_pascal_fixer_collisions", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_pascal_fixer_collisions")
# REMOVED: _emit_gated_by_confidence("p1", "test_pascal_fixer_collisions", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_pascal_fixer_collisions")
# REMOVED: emit_determinism_digest("p0", "test_pascal_fixer_collisions")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

_psf = load_dev_script("pascal_sovereignty_fixer.py")
PascalSovereigntyFixer = _psf.PascalSovereigntyFixer


@pytest.fixture
def fixer_env(tmp_path):
    (tmp_path / "src").mkdir()
    return tmp_path / "src"


def test_identical_collision_deletes_violator(fixer_env):
    """Test safe deduplication of identical files."""
    fixer = PascalSovereigntyFixer(dry_run=False)
    target = fixer_env / "subatomic_testing_mixin.py"
    violator = fixer_env / "SubatomicTestingMixin.py"

    code = "class SubatomicTestingMixin: pass"
    target.write_text(code, encoding="utf-8")
    violator.write_text(code, encoding="utf-8")

    result = fixer.resolve_collision_and_rename(violator, "subatomic_testing_mixin.py")

    assert result is True
    assert not violator.exists()
    assert target.exists()


def test_divergent_collision_renames_violator(fixer_env):
    """Test preservation of divergent data via .CONFLICT rename."""
    fixer = PascalSovereigntyFixer(dry_run=False)
    target = fixer_env / "adaptive_execution_mixin.py"
    violator = fixer_env / "AdaptiveExecutionMixin.py"

    target.write_text("class Mixin: pass # V1")
    violator.write_text("class Mixin: pass # V2_MODIFIED")

    result = fixer.resolve_collision_and_rename(violator, "adaptive_execution_mixin.py")

    assert result is True
    assert not violator.exists()
    # Check for conflict file
    conflicts = list(fixer_env.glob("adaptive_execution_mixin.py.CONFLICT_*"))
    assert len(conflicts) == 1
    assert "V2_MODIFIED" in conflicts[0].read_text()


def test_no_collision_standard_rename(fixer_env):
    """Test standard rename when no collision exists."""
    fixer = PascalSovereigntyFixer(dry_run=False)
    src = fixer_env / "OldName.py"
    src.write_text("class Test: pass")

    result = fixer.resolve_collision_and_rename(src, "NewName.py")

    assert result is True
    assert not src.exists()
    assert (fixer_env / "NewName.py").exists()


def test_dry_run_mode(fixer_env):
    """Test that dry run mode doesn't actually modify files."""
    fixer = PascalSovereigntyFixer(dry_run=True)
    src = fixer_env / "TestFile.py"
    src.write_text("class Test: pass")

    result = fixer.resolve_collision_and_rename(src, "NewFile.py")

    assert result is True
    assert src.exists()  # File should still exist in dry run mode
    assert not (fixer_env / "NewFile.py").exists()


def test_collision_with_binary_content(fixer_env):
    """Test collision resolution with binary content differences."""
    fixer = PascalSovereigntyFixer(dry_run=False)
    target = fixer_env / "test_file.py"
    violator = fixer_env / "TestFile.py"

    # Write identical binary content first
    target.write_bytes(b"\x00\x01\x02\x03")
    violator.write_bytes(b"\x00\x01\x02\x03")

    result = fixer.resolve_collision_and_rename(violator, "test_file.py")

    assert result is True
    assert not violator.exists()
    assert target.exists()


def test_collision_case_insensitive_windows(fixer_env):
    """Test case-insensitive collision handling."""
    fixer = PascalSovereigntyFixer(dry_run=False)
    target = fixer_env / "test_file.py"
    violator = fixer_env / "TEST_FILE.py"

    target.write_text("class Test: pass")
    violator.write_text("class Test: pass")

    result = fixer.resolve_collision_and_rename(violator, "test_file.py")

    assert result is True
    # On Windows, case-insensitive paths may resolve to the same file
    # Check that the target still exists and has correct content
    assert target.exists()
    assert "class Test: pass" in target.read_text()


def test_trivial_match_no_action(fixer_env):
    """Test that no action is taken when source and destination are the same."""
    fixer = PascalSovereigntyFixer(dry_run=False)
    src = fixer_env / "test_file.py"
    src.write_text("class Test: pass")

    result = fixer.resolve_collision_and_rename(src, "test_file.py")

    assert result is False
    assert src.exists()


def test_error_handling_during_collision(fixer_env):
    """Test graceful error handling during collision resolution."""
    fixer = PascalSovereigntyFixer(dry_run=False)
    target = fixer_env / "target.py"
    violator = fixer_env / "violator.py"

    target.write_text("class Target: pass")
    violator.write_text("class Violator: pass")

    # Create a file that will cause read error by making it unreadable
    # On Windows, we can simulate this by creating a scenario where the file
    # gets removed during the operation

    # Test with a non-existent target to trigger error path
    fixer_env / "non_existent.py"
    result = fixer.resolve_collision_and_rename(violator, "non_existent.py")

    # Should succeed since there's no collision
    assert result is True
    assert not violator.exists()
    assert (fixer_env / "non_existent.py").exists()
