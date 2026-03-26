"""
Guardian Cross-Layer Mutation Tests.

1. Clean repo → PASS on all layer mutation checks
2. L6 file importing from L4 → FAIL on L6_mutates_L4
3. L4 file importing from L2 → FAIL on L4_invokes_L2
4. File with embedding assigned to control_plane → FAIL on C0_mutates_control_plane
5. Output conforms to guardian_contract schema
6. scan functions are deterministic (same input → same output)
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

#  # MOVED: from agentic_core.L0_routing.config.path_constants import (
    L0_ROUTING_DIR,
    L1_COGNITION_DIR,
    L4_STATE_DIR,
    L6_OBSERVABILITY_DIR,
)
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_guardian_cross_layer_mutation")
# REMOVED: _emit_applies_guardrail("p0", "test_guardian_cross_layer_mutation", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_guardian_cross_layer_mutation", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_guardian_cross_layer_mutation", "state_snapshot")
# REMOVED: emit_replay_key("p0", "test_guardian_cross_layer_mutation")
# REMOVED: emit_determinism_digest("p0", "test_guardian_cross_layer_mutation")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_guardian_cross_layer_mutation", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_guardian_cross_layer_mutation", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_guardian_cross_layer_mutation", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_guardian_cross_layer_mutation", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_guardian_cross_layer_mutation", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_guardian_cross_layer_mutation", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_guardian_cross_layer_mutation", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_guardian_cross_layer_mutation", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_guardian_cross_layer_mutation", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_guardian_cross_layer_mutation", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_guardian_cross_layer_mutation", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_guardian_cross_layer_mutation", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_guardian_cross_layer_mutation", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_guardian_cross_layer_mutation", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_guardian_cross_layer_mutation", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_guardian_cross_layer_mutation", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_guardian_cross_layer_mutation", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_guardian_cross_layer_mutation", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_guardian_cross_layer_mutation", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_guardian_cross_layer_mutation", "exec_snapshot_link")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

#  # MOVED: from agentic_core.L0_routing.scripts.run_guardian_cross_layer_mutation import (
    run_cross_layer_mutation_guardian,
    scan_cross_layer_mutations,
)
#  # MOVED: from agentic_core.L0_routing.types.guardian_contract_types import (
    CheckStatus,
    GuardianStatus,
)
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_emits_metric_event("test_guardian_cross_layer_mutation", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_guardian_cross_layer_mutation", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_guardian_cross_layer_mutation", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_guardian_cross_layer_mutation", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_guardian_cross_layer_mutation", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_guardian_cross_layer_mutation", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_guardian_cross_layer_mutation", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_guardian_cross_layer_mutation", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_guardian_cross_layer_mutation", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_guardian_cross_layer_mutation", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_guardian_cross_layer_mutation", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_guardian_cross_layer_mutation", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_guardian_cross_layer_mutation", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_guardian_cross_layer_mutation", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_guardian_cross_layer_mutation", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_guardian_cross_layer_mutation", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_guardian_cross_layer_mutation", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_guardian_cross_layer_mutation", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_guardian_cross_layer_mutation", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_guardian_cross_layer_mutation", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_guardian_cross_layer_mutation", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_guardian_cross_layer_mutation", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_guardian_cross_layer_mutation", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_guardian_cross_layer_mutation", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_guardian_cross_layer_mutation", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_guardian_cross_layer_mutation", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_guardian_cross_layer_mutation", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_guardian_cross_layer_mutation", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_guardian_cross_layer_mutation", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_guardian_cross_layer_mutation", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_guardian_cross_layer_mutation", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_guardian_cross_layer_mutation", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_guardian_cross_layer_mutation", "write_through")
# REMOVED: _emit_writes_through("p1", "test_guardian_cross_layer_mutation", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_guardian_cross_layer_mutation", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_guardian_cross_layer_mutation", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_guardian_cross_layer_mutation", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_guardian_cross_layer_mutation", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_guardian_cross_layer_mutation", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_guardian_cross_layer_mutation", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_guardian_cross_layer_mutation", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_guardian_cross_layer_mutation", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_guardian_cross_layer_mutation", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_guardian_cross_layer_mutation", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_guardian_cross_layer_mutation", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_guardian_cross_layer_mutation", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_guardian_cross_layer_mutation", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_guardian_cross_layer_mutation", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_guardian_cross_layer_mutation")
# REMOVED: _emit_gated_by_confidence("p1", "test_guardian_cross_layer_mutation", "confidence_gate")

pytestmark = pytest.mark.guardian


@pytest.fixture()
def clean_repo(tmp_path: Path) -> Path:
    (tmp_path / L0_ROUTING_DIR).mkdir(parents=True)
    (tmp_path / L0_ROUTING_DIR / "clean.py").write_text("x = 1\n", encoding="utf-8")
    return tmp_path


@pytest.fixture()
def l6_l4_repo(tmp_path: Path) -> Path:
    (tmp_path / L6_OBSERVABILITY_DIR).mkdir(parents=True)
    (tmp_path / L6_OBSERVABILITY_DIR / "bad.py").write_text(
        "from agentic_core.L4_state import Something\n", encoding="utf-8"
    )
    return tmp_path


@pytest.fixture()
def l4_l2_repo(tmp_path: Path) -> Path:
    (tmp_path / L4_STATE_DIR).mkdir(parents=True)
    (tmp_path / L4_STATE_DIR / "bad.py").write_text(
        "from agentic_core.L2_execution import Something\n", encoding="utf-8"
    )
    return tmp_path


@pytest.fixture()
def c0_control_plane_repo(tmp_path: Path) -> Path:
    (tmp_path / L1_COGNITION_DIR).mkdir(parents=True)
    (tmp_path / L1_COGNITION_DIR / "bad.py").write_text("control_plane = embedding_score\n", encoding="utf-8")
    return tmp_path


class TestCrossLayerMutationGuardianClean:
    def test_clean_repo_passes(self, clean_repo):
        from agentic_core.L0_routing.config.path_constants import (
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
        from agentic_core.L0_routing.scripts.run_guardian_cross_layer_mutation import (
        from agentic_core.L0_routing.types.guardian_contract_types import (
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
        result = run_cross_layer_mutation_guardian(repo_root=clean_repo)
        check_map = {c.check_id: c.status for c in result.checks}
        assert check_map["upward_layer_mutation"] == CheckStatus.PASS.value
        assert check_map["L6_mutates_L4"] == CheckStatus.PASS.value
        assert check_map["L4_invokes_L2"] == CheckStatus.PASS.value
        assert check_map["C0_mutates_control_plane"] == CheckStatus.PASS.value

    def test_clean_repo_top_status_pass(self, clean_repo):
        result = run_cross_layer_mutation_guardian(repo_root=clean_repo)
        assert result.status == GuardianStatus.PASS.value


class TestCrossLayerMutationGuardianViolations:
    def test_l6_l4_detected(self, l6_l4_repo):
        viols = scan_cross_layer_mutations(l6_l4_repo)
        assert viols["L6_mutates_L4"]
        assert len(viols["L6_mutates_L4"]) == 1

    def test_l6_l4_fails_result(self, l6_l4_repo):
        result = run_cross_layer_mutation_guardian(repo_root=l6_l4_repo)
        check_map = {c.check_id: c.status for c in result.checks}
        assert check_map["L6_mutates_L4"] == CheckStatus.FAIL.value

    def test_l4_l2_detected(self, l4_l2_repo):
        viols = scan_cross_layer_mutations(l4_l2_repo)
        assert viols["L4_invokes_L2"]
        assert len(viols["L4_invokes_L2"]) == 1

    def test_l4_l2_fails_result(self, l4_l2_repo):
        result = run_cross_layer_mutation_guardian(repo_root=l4_l2_repo)
        check_map = {c.check_id: c.status for c in result.checks}
        assert check_map["L4_invokes_L2"] == CheckStatus.FAIL.value

    def test_c0_control_plane_detected(self, c0_control_plane_repo):
        viols = scan_cross_layer_mutations(c0_control_plane_repo)
        assert viols["C0_mutates_control_plane"]
        assert len(viols["C0_mutates_control_plane"]) == 1

    def test_c0_control_plane_fails_result(self, c0_control_plane_repo):
        result = run_cross_layer_mutation_guardian(repo_root=c0_control_plane_repo)
        check_map = {c.check_id: c.status for c in result.checks}
        assert check_map["C0_mutates_control_plane"] == CheckStatus.FAIL.value


class TestCrossLayerMutationDeterminism:
    def test_scan_is_deterministic(self, l6_l4_repo):
        a = scan_cross_layer_mutations(l6_l4_repo)
        b = scan_cross_layer_mutations(l6_l4_repo)
        assert a == b

    def test_result_guardian_id_correct(self, clean_repo):
        result = run_cross_layer_mutation_guardian(repo_root=clean_repo)
        assert result.guardian_id == "cross_layer_mutation_guard"
