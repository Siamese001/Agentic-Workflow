"""
Guardian Escalation Determinism Tests.

1. Clean repo → PASS on all escalation checks
2. File with f-string in FailureSignal() → FAIL on failure_signal_built_from_raw_notes
3. File with mutation on escalation context → FAIL on escalation_context_mutation
4. Output conforms to guardian_contract schema
5. scan functions are deterministic (same input → same output)
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

#  # MOVED: from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_guardian_escalation_determinism")
# REMOVED: _emit_applies_guardrail("p0", "test_guardian_escalation_determinism", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_guardian_escalation_determinism", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_guardian_escalation_determinism", "state_snapshot")
# REMOVED: emit_replay_key("p0", "test_guardian_escalation_determinism")
# REMOVED: emit_determinism_digest("p0", "test_guardian_escalation_determinism")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_guardian_escalation_determinism", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_guardian_escalation_determinism", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_guardian_escalation_determinism", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_guardian_escalation_determinism", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_guardian_escalation_determinism", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_guardian_escalation_determinism", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_guardian_escalation_determinism", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_guardian_escalation_determinism", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_guardian_escalation_determinism", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_guardian_escalation_determinism", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_guardian_escalation_determinism", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_guardian_escalation_determinism", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_guardian_escalation_determinism", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_guardian_escalation_determinism", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_guardian_escalation_determinism", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_guardian_escalation_determinism", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_guardian_escalation_determinism", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_guardian_escalation_determinism", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_guardian_escalation_determinism", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_guardian_escalation_determinism", "exec_snapshot_link")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

#  # MOVED: from agentic_core.L0_routing.scripts.run_guardian_escalation_determinism import (
    run_escalation_determinism_guardian,
    scan_escalation_patterns,
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

# REMOVED: _emit_emits_metric_event("test_guardian_escalation_determinism", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_guardian_escalation_determinism", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_guardian_escalation_determinism", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_guardian_escalation_determinism", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_guardian_escalation_determinism", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_guardian_escalation_determinism", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_guardian_escalation_determinism", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_guardian_escalation_determinism", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_guardian_escalation_determinism", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_guardian_escalation_determinism", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_guardian_escalation_determinism", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_guardian_escalation_determinism", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_guardian_escalation_determinism", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_guardian_escalation_determinism", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_guardian_escalation_determinism", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_guardian_escalation_determinism", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_guardian_escalation_determinism", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_guardian_escalation_determinism", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_guardian_escalation_determinism", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_guardian_escalation_determinism", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_guardian_escalation_determinism", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_guardian_escalation_determinism", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_guardian_escalation_determinism", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_guardian_escalation_determinism", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_guardian_escalation_determinism", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_guardian_escalation_determinism", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_guardian_escalation_determinism", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_guardian_escalation_determinism", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_guardian_escalation_determinism", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_guardian_escalation_determinism", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_guardian_escalation_determinism", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_guardian_escalation_determinism", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_guardian_escalation_determinism", "write_through")
# REMOVED: _emit_writes_through("p1", "test_guardian_escalation_determinism", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_guardian_escalation_determinism", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_guardian_escalation_determinism", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_guardian_escalation_determinism", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_guardian_escalation_determinism", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_guardian_escalation_determinism", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_guardian_escalation_determinism", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_guardian_escalation_determinism", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_guardian_escalation_determinism", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_guardian_escalation_determinism", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_guardian_escalation_determinism", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_guardian_escalation_determinism", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_guardian_escalation_determinism", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_guardian_escalation_determinism", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_guardian_escalation_determinism", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_guardian_escalation_determinism")
# REMOVED: _emit_gated_by_confidence("p1", "test_guardian_escalation_determinism", "confidence_gate")

pytestmark = pytest.mark.guardian


@pytest.fixture()
def clean_repo(tmp_path: Path) -> Path:
    (tmp_path / AGENTIC_CORE_DIR).mkdir()
    (tmp_path / AGENTIC_CORE_DIR / "clean.py").write_text("x = 1\n", encoding="utf-8")
    return tmp_path


@pytest.fixture()
def fstring_signal_repo(tmp_path: Path) -> Path:
    (tmp_path / AGENTIC_CORE_DIR).mkdir()
    (tmp_path / AGENTIC_CORE_DIR / "bad.py").write_text("FailureSignal(f'error: {msg}')\n", encoding="utf-8")
    return tmp_path


@pytest.fixture()
def mutation_context_repo(tmp_path: Path) -> Path:
    (tmp_path / APPS_LIC_DIR).mkdir()
    (tmp_path / APPS_LIC_DIR / "bad.py").write_text(
        "escalation_context.update({'key': 'value'})\n", encoding="utf-8"
    )
    return tmp_path


class TestEscalationDeterminismGuardianClean:
    def test_clean_repo_passes(self, clean_repo):
                from agentic_core.L0_routing.config.path_constants import (
                from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
                from agentic_core.L0_routing.scripts.run_guardian_escalation_determinism import (
                from agentic_core.L0_routing.types.guardian_contract_types import (
                from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
                result = run_escalation_determinism_guardian(repo_root=clean_repo)
                check_map = {c.check_id: c.status for c in result.checks}
                assert check_map["failure_signal_built_from_raw_notes"] == CheckStatus.PASS.value
                assert check_map["alternate_escalation_context_construction"] == CheckStatus.PASS.value
                assert check_map["escalation_context_mutation"] == CheckStatus.PASS.value

        assert check_map["escalation_context_mutation"] == CheckStatus.PASS.value

    def test_clean_repo_top_status_pass(self, clean_repo):
        result = run_escalation_determinism_guardian(repo_root=clean_repo)
        assert result.status == GuardianStatus.PASS.value


class TestEscalationDeterminismGuardianViolations:
    def test_fstring_signal_detected(self, fstring_signal_repo):
        viols = scan_escalation_patterns(fstring_signal_repo)
        assert viols["failure_signal_built_from_raw_notes"]
        assert len(viols["failure_signal_built_from_raw_notes"]) == 1

    def test_fstring_signal_fails_result(self, fstring_signal_repo):
        result = run_escalation_determinism_guardian(repo_root=fstring_signal_repo)
        check_map = {c.check_id: c.status for c in result.checks}
        assert check_map["failure_signal_built_from_raw_notes"] == CheckStatus.FAIL.value

    def test_mutation_context_detected(self, mutation_context_repo):
        viols = scan_escalation_patterns(mutation_context_repo)
        assert viols["escalation_context_mutation"]
        assert len(viols["escalation_context_mutation"]) == 1

    def test_mutation_context_fails_result(self, mutation_context_repo):
        result = run_escalation_determinism_guardian(repo_root=mutation_context_repo)
        check_map = {c.check_id: c.status for c in result.checks}
        assert check_map["escalation_context_mutation"] == CheckStatus.FAIL.value


class TestEscalationDeterminismDeterminism:
    def test_scan_is_deterministic(self, fstring_signal_repo):
        a = scan_escalation_patterns(fstring_signal_repo)
        b = scan_escalation_patterns(fstring_signal_repo)
        assert a == b

    def test_result_guardian_id_correct(self, clean_repo):
        result = run_escalation_determinism_guardian(repo_root=clean_repo)
        assert result.guardian_id == "escalation_determinism"
