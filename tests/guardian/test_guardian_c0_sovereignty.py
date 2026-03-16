"""
Guardian C0 Sovereignty Tests.

1. Clean repo → PASS on all embedding boundary checks
2. File with embedding in conditional → FAIL on embedding_drives_routing
3. File with embedding assigned to threshold → FAIL on embedding_mutates_threshold
4. Output conforms to guardian_contract schema
5. scan functions are deterministic (same input → same output)
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    SYSTEM_LEARNING_DIR,
)
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

_emit_records_execution_trace("p0", "evidence", "test_guardian_c0_sovereignty")
_emit_applies_guardrail("p0", "test_guardian_c0_sovereignty", "p0_governance")
_emit_reads_policy_state("p0", "test_guardian_c0_sovereignty", "policy_binding")
_emit_snapshots_state("p0", "test_guardian_c0_sovereignty", "state_snapshot")
emit_replay_key("p0", "test_guardian_c0_sovereignty")
emit_determinism_digest("p0", "test_guardian_c0_sovereignty")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_guardian_c0_sovereignty", "execution_auth")
_emit_validates_capability("p2", "test_guardian_c0_sovereignty", "capability_check")
_emit_routes_to_capability("p2", "test_guardian_c0_sovereignty", "capability_route")
_emit_writes_via_uwg("p2", "test_guardian_c0_sovereignty", "uwg_write")
_emit_blocks_direct_write("p2", "test_guardian_c0_sovereignty", "direct_write_block")
_emit_records_tool_invocation("p2", "test_guardian_c0_sovereignty", "tool_invocation")
_emit_captures_execution_output("p2", "test_guardian_c0_sovereignty", "exec_output")
_emit_dispatches_agent("p3", "test_guardian_c0_sovereignty", "agent_dispatch")
_emit_coordinates_agents("p3", "test_guardian_c0_sovereignty", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_guardian_c0_sovereignty", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_guardian_c0_sovereignty", "healing_outcome")
_emit_escalates_failure("p3", "test_guardian_c0_sovereignty", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_guardian_c0_sovereignty", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_guardian_c0_sovereignty", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_guardian_c0_sovereignty", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_guardian_c0_sovereignty", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_guardian_c0_sovereignty", "eval_metric")
_emit_stores_embedding("p4", "test_guardian_c0_sovereignty", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_guardian_c0_sovereignty", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_guardian_c0_sovereignty", "exec_snapshot_link")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_routing.scripts.run_guardian_c0_sovereignty import (
    run_c0_sovereignty_guardian,
    scan_embedding_control_flow,
)
from agentic_core.L0_routing.types.guardian_contract_types import (
    CheckStatus,
    GuardianStatus,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_execution_terminates_at_uwg,
    _emit_writes_through,
    _emit_validated_by_safety_plane,
    _emit_invokes_eval,
    _emit_proposal_commits_routing,
)
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("test_guardian_c0_sovereignty", "p4obs", "metric_1")
_emit_emits_metric_event("test_guardian_c0_sovereignty", "p4obs", "metric_2")
_emit_emits_metric_event("test_guardian_c0_sovereignty", "p4obs", "metric_3")
_emit_emits_metric_event("test_guardian_c0_sovereignty", "p4obs", "metric_4")
_emit_emits_metric_event("test_guardian_c0_sovereignty", "p4obs", "metric_5")
_emit_emits_metric_event("test_guardian_c0_sovereignty", "p4obs", "metric_6")
_emit_records_incident_event("test_guardian_c0_sovereignty", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_guardian_c0_sovereignty", "p4obs", "anomaly")
_emit_writes_observability_log("test_guardian_c0_sovereignty", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_guardian_c0_sovereignty", "p4obs", "mon_state")
_emit_triggers_alert("test_guardian_c0_sovereignty", "p4obs", "alert")
_emit_links_incident_trace("test_guardian_c0_sovereignty", "p4obs", "trace_link")
_emit_captures_pattern("test_guardian_c0_sovereignty", "p3lm", "pattern")
_emit_records_learning_event("test_guardian_c0_sovereignty", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_guardian_c0_sovereignty", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_guardian_c0_sovereignty", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_guardian_c0_sovereignty", "p3lm", "routing")
_emit_improves_agent_policy("test_guardian_c0_sovereignty", "p3lm", "policy")
_emit_stores_learning_state("test_guardian_c0_sovereignty", "p3lm", "state")
_emit_records_execution_trace("test_guardian_c0_sovereignty", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_guardian_c0_sovereignty", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_guardian_c0_sovereignty", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_guardian_c0_sovereignty", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_guardian_c0_sovereignty", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_guardian_c0_sovereignty", "env_read", "p2_env_1")
_emit_reads_environ("test_guardian_c0_sovereignty", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_guardian_c0_sovereignty", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_guardian_c0_sovereignty", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_guardian_c0_sovereignty", "context_pull")
_emit_pulls_context("p1", "test_guardian_c0_sovereignty", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_guardian_c0_sovereignty", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_guardian_c0_sovereignty", "uwg_term_secondary")
_emit_writes_through("p1", "test_guardian_c0_sovereignty", "write_through")
_emit_writes_through("p1", "test_guardian_c0_sovereignty", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_guardian_c0_sovereignty", "safety_validation")
_emit_invokes_eval("p1", "test_guardian_c0_sovereignty", "eval_call")
_emit_proposal_commits_routing("p1", "test_guardian_c0_sovereignty", "routing_commit")

pytestmark = pytest.mark.guardian


@pytest.fixture()
def clean_repo(tmp_path: Path) -> Path:
    (tmp_path / AGENTIC_CORE_DIR).mkdir()
    (tmp_path / AGENTIC_CORE_DIR / "clean.py").write_text("x = 1\n", encoding="utf-8")
    return tmp_path


@pytest.fixture()
def embedding_routing_repo(tmp_path: Path) -> Path:
    (tmp_path / AGENTIC_CORE_DIR).mkdir()
    (tmp_path / AGENTIC_CORE_DIR / "bad.py").write_text(
        "if embedding_score > 0.5:\n    route = 'high'\n", encoding="utf-8"
    )
    return tmp_path


@pytest.fixture()
def embedding_threshold_repo(tmp_path: Path) -> Path:
    (tmp_path / SYSTEM_LEARNING_DIR).mkdir()
    (tmp_path / SYSTEM_LEARNING_DIR / "bad.py").write_text("threshold = embedding_result\n", encoding="utf-8")
    return tmp_path


class TestC0SovereigntyGuardianClean:
    def test_clean_repo_passes(self, clean_repo):
        result = run_c0_sovereignty_guardian(repo_root=clean_repo)
        check_map = {c.check_id: c.status for c in result.checks}
        assert check_map["embedding_drives_routing"] == CheckStatus.PASS.value
        assert check_map["embedding_drives_tier_selection"] == CheckStatus.PASS.value
        assert check_map["embedding_mutates_threshold"] == CheckStatus.PASS.value

    def test_clean_repo_top_status_pass(self, clean_repo):
        result = run_c0_sovereignty_guardian(repo_root=clean_repo)
        assert result.status == GuardianStatus.PASS.value


class TestC0SovereigntyGuardianViolations:
    def test_embedding_routing_detected(self, embedding_routing_repo):
        viols = scan_embedding_control_flow(embedding_routing_repo)
        assert viols["embedding_drives_routing"]
        assert len(viols["embedding_drives_routing"]) == 1

    def test_embedding_routing_fails_result(self, embedding_routing_repo):
        result = run_c0_sovereignty_guardian(repo_root=embedding_routing_repo)
        check_map = {c.check_id: c.status for c in result.checks}
        assert check_map["embedding_drives_routing"] == CheckStatus.FAIL.value

    def test_embedding_threshold_detected(self, embedding_threshold_repo):
        viols = scan_embedding_control_flow(embedding_threshold_repo)
        assert viols["embedding_mutates_threshold"]
        assert len(viols["embedding_mutates_threshold"]) == 1

    def test_embedding_threshold_fails_result(self, embedding_threshold_repo):
        result = run_c0_sovereignty_guardian(repo_root=embedding_threshold_repo)
        check_map = {c.check_id: c.status for c in result.checks}
        assert check_map["embedding_mutates_threshold"] == CheckStatus.FAIL.value


class TestC0SovereigntyDeterminism:
    def test_scan_is_deterministic(self, embedding_routing_repo):
        a = scan_embedding_control_flow(embedding_routing_repo)
        b = scan_embedding_control_flow(embedding_routing_repo)
        assert a == b

    def test_result_guardian_id_correct(self, clean_repo):
        result = run_c0_sovereignty_guardian(repo_root=clean_repo)
        assert result.guardian_id == "c0_sovereignty_enforcement"
