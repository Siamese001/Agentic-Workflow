"""
Guardian Change Package Activation Tests.

1. Clean repo → PASS on all activation checks
2. File with direct VersionStore.commit() → FAIL on direct_version_store_commit
3. File with activate() missing approval_gate → FAIL on activation_without_approval_gate
4. Output conforms to guardian_contract schema
5. scan functions are deterministic (same input → same output)
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

#  # MOVED: from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    SYSTEM_LEARNING_DIR,
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_guardian_change_package_activation")
# REMOVED: _emit_applies_guardrail("p0", "test_guardian_change_package_activation", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_guardian_change_package_activation", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_guardian_change_package_activation", "state_snapshot")
# REMOVED: emit_replay_key("p0", "test_guardian_change_package_activation")
# REMOVED: emit_determinism_digest("p0", "test_guardian_change_package_activation")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_guardian_change_package_activation", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_guardian_change_package_activation", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_guardian_change_package_activation", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_guardian_change_package_activation", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_guardian_change_package_activation", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_guardian_change_package_activation", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_guardian_change_package_activation", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_guardian_change_package_activation", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_guardian_change_package_activation", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_guardian_change_package_activation", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_guardian_change_package_activation", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_guardian_change_package_activation", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_guardian_change_package_activation", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_guardian_change_package_activation", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_guardian_change_package_activation", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_guardian_change_package_activation", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_guardian_change_package_activation", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_guardian_change_package_activation", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_guardian_change_package_activation", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_guardian_change_package_activation", "exec_snapshot_link")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

#  # MOVED: from agentic_core.L0_routing.scripts.run_guardian_change_package_activation import (
    run_change_package_activation_guardian,
    scan_activation_patterns,
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

# REMOVED: _emit_emits_metric_event("test_guardian_change_package_activation", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_guardian_change_package_activation", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_guardian_change_package_activation", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_guardian_change_package_activation", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_guardian_change_package_activation", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_guardian_change_package_activation", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_guardian_change_package_activation", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_guardian_change_package_activation", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_guardian_change_package_activation", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_guardian_change_package_activation", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_guardian_change_package_activation", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_guardian_change_package_activation", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_guardian_change_package_activation", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_guardian_change_package_activation", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_guardian_change_package_activation", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_guardian_change_package_activation", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_guardian_change_package_activation", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_guardian_change_package_activation", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_guardian_change_package_activation", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_guardian_change_package_activation", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_guardian_change_package_activation", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_guardian_change_package_activation", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_guardian_change_package_activation", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_guardian_change_package_activation", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_guardian_change_package_activation", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_guardian_change_package_activation", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_guardian_change_package_activation", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_guardian_change_package_activation", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_guardian_change_package_activation", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_guardian_change_package_activation", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_guardian_change_package_activation", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_guardian_change_package_activation", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_guardian_change_package_activation", "write_through")
# REMOVED: _emit_writes_through("p1", "test_guardian_change_package_activation", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_guardian_change_package_activation", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_guardian_change_package_activation", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_guardian_change_package_activation", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_guardian_change_package_activation", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_guardian_change_package_activation", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_guardian_change_package_activation", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_guardian_change_package_activation", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_guardian_change_package_activation", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_guardian_change_package_activation", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_guardian_change_package_activation", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_guardian_change_package_activation", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_guardian_change_package_activation", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_guardian_change_package_activation", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_guardian_change_package_activation", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_guardian_change_package_activation")
# REMOVED: _emit_gated_by_confidence("p1", "test_guardian_change_package_activation", "confidence_gate")

pytestmark = pytest.mark.guardian


@pytest.fixture()
def clean_repo(tmp_path: Path) -> Path:
    (tmp_path / AGENTIC_CORE_DIR).mkdir()
    (tmp_path / AGENTIC_CORE_DIR / "clean.py").write_text("x = 1\n", encoding="utf-8")
    return tmp_path


@pytest.fixture()
def direct_commit_repo(tmp_path: Path) -> Path:
    (tmp_path / SYSTEM_LEARNING_DIR).mkdir()
    (tmp_path / SYSTEM_LEARNING_DIR / "bad.py").write_text("version_store.commit(data)\n", encoding="utf-8")
    return tmp_path


@pytest.fixture()
def missing_gate_repo(tmp_path: Path) -> Path:
    (tmp_path / AGENTIC_CORE_DIR).mkdir()
    (tmp_path / AGENTIC_CORE_DIR / "bad.py").write_text("change_package.activate()\n", encoding="utf-8")
    return tmp_path


class TestChangePackageActivationGuardianClean:
    def test_clean_repo_passes(self, clean_repo):
        from agentic_core.L0_routing.config.path_constants import (
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
        from agentic_core.L0_routing.scripts.run_guardian_change_package_activation import (
        from agentic_core.L0_routing.types.guardian_contract_types import (
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
        result = run_change_package_activation_guardian(repo_root=clean_repo)
        check_map = {c.check_id: c.status for c in result.checks}
        assert check_map["proposal_only_bypass"] == CheckStatus.PASS.value
        assert check_map["direct_version_store_commit"] == CheckStatus.PASS.value
        assert check_map["activation_without_approval_gate"] == CheckStatus.PASS.value

    def test_clean_repo_top_status_pass(self, clean_repo):
        result = run_change_package_activation_guardian(repo_root=clean_repo)
        assert result.status == GuardianStatus.PASS.value


class TestChangePackageActivationGuardianViolations:
    def test_direct_commit_detected(self, direct_commit_repo):
        viols = scan_activation_patterns(direct_commit_repo)
        assert viols["direct_version_store_commit"]
        assert len(viols["direct_version_store_commit"]) == 1

    def test_direct_commit_fails_result(self, direct_commit_repo):
        result = run_change_package_activation_guardian(repo_root=direct_commit_repo)
        check_map = {c.check_id: c.status for c in result.checks}
        assert check_map["direct_version_store_commit"] == CheckStatus.FAIL.value

    def test_missing_gate_detected(self, missing_gate_repo):
        viols = scan_activation_patterns(missing_gate_repo)
        assert viols["activation_without_approval_gate"]
        assert len(viols["activation_without_approval_gate"]) == 1

    def test_missing_gate_fails_result(self, missing_gate_repo):
        result = run_change_package_activation_guardian(repo_root=missing_gate_repo)
        check_map = {c.check_id: c.status for c in result.checks}
        assert check_map["activation_without_approval_gate"] == CheckStatus.FAIL.value


class TestChangePackageActivationDeterminism:
    def test_scan_is_deterministic(self, direct_commit_repo):
        a = scan_activation_patterns(direct_commit_repo)
        b = scan_activation_patterns(direct_commit_repo)
        assert a == b

    def test_result_guardian_id_correct(self, clean_repo):
        result = run_change_package_activation_guardian(repo_root=clean_repo)
        assert result.guardian_id == "change_package_activation_guard"
