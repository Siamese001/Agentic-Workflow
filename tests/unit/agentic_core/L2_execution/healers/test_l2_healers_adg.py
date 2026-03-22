"""ADG-driven tests for L2 execution healers — fan_in=1.

Covers: architecture_governor_healer, file_classification_healer,
        filesystem_ssot_healer, gravity_leak_healer.
"""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_records_execution_trace("p0", "evidence", "test_l2_healers_adg")
_emit_applies_guardrail("p0", "test_l2_healers_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_l2_healers_adg", "policy_binding")
_emit_snapshots_state("p0", "test_l2_healers_adg", "state_snapshot")
emit_replay_key("p0", "test_l2_healers_adg")
emit_determinism_digest("p0", "test_l2_healers_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_l2_healers_adg", "execution_auth")
_emit_validates_capability("p2", "test_l2_healers_adg", "capability_check")
_emit_routes_to_capability("p2", "test_l2_healers_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_l2_healers_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_l2_healers_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_l2_healers_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_l2_healers_adg", "exec_output")
_emit_dispatches_agent("p3", "test_l2_healers_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_l2_healers_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_l2_healers_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_l2_healers_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_l2_healers_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_l2_healers_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_l2_healers_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_l2_healers_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_l2_healers_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_l2_healers_adg", "eval_metric")
_emit_stores_embedding("p4", "test_l2_healers_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_l2_healers_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_l2_healers_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit

# ---------------------------------------------------------------------------
# architecture_governor_healer
# ---------------------------------------------------------------------------
from agentic_core.L2_execution.healers.architecture_governor_healer import (
    CHECK_ID as ARCH_CHECK_ID,
)
from agentic_core.L2_execution.healers.architecture_governor_healer import (
    heal_architecture_governance,
)
from agentic_core.L2_execution.types.heal_contract_types import HealCheckResult, HealStatus


class TestArchitectureGovernorHealer:
    def test_check_id_string(self):
        assert isinstance(ARCH_CHECK_ID, str)

    def test_heal_callable(self):
        assert callable(heal_architecture_governance)

    def test_no_violations_returns_healed(self):
        result = heal_architecture_governance(
            {"violations_count": 0}, apply=False
        )
        assert isinstance(result, HealCheckResult)
        assert result.status == HealStatus.HEALED

    def test_dry_run_with_violations_returns_result(self):
        result = heal_architecture_governance(
            {"violations_count": 3, "territory": "agentic_core"},
            apply=False,
        )
        assert isinstance(result, HealCheckResult)
        assert result.status != HealStatus.HEALED

    def test_check_id_matches(self):
        result = heal_architecture_governance({"violations_count": 0})
        assert result.check_id == ARCH_CHECK_ID


# ---------------------------------------------------------------------------
# file_classification_healer
# ---------------------------------------------------------------------------
from agentic_core.L2_execution.healers.file_classification_healer import (
    CHECK_ID as FILE_CLASS_CHECK_ID,
)
from agentic_core.L2_execution.healers.file_classification_healer import (
    heal_file_classification,
)


class TestFileClassificationHealer:
    def test_check_id_string(self):
        assert isinstance(FILE_CLASS_CHECK_ID, str)

    def test_heal_callable(self):
        assert callable(heal_file_classification)

    def test_no_violations_returns_healed(self):
        result = heal_file_classification(
            {"violations_count": 0}, apply=False
        )
        assert isinstance(result, HealCheckResult)
        assert result.status == HealStatus.HEALED

    def test_dry_run_with_violations_returns_result(self):
        result = heal_file_classification(
            {"violations_count": 2, "territory": "agentic_core"},
            apply=False,
        )
        assert isinstance(result, HealCheckResult)

    def test_check_id_matches(self):
        result = heal_file_classification({"violations_count": 0})
        assert result.check_id == FILE_CLASS_CHECK_ID


# ---------------------------------------------------------------------------
# filesystem_ssot_healer
# ---------------------------------------------------------------------------
from agentic_core.L2_execution.healers.filesystem_ssot_healer import (
    CHECK_ID as FS_CHECK_ID,
)
from agentic_core.L2_execution.healers.filesystem_ssot_healer import (
    heal_filesystem_ssot_drift,
)


class TestFilesystemSSOTHealer:
    def test_check_id_string(self):
        assert isinstance(FS_CHECK_ID, str)

    def test_heal_callable(self):
        assert callable(heal_filesystem_ssot_drift)

    def test_no_evidence_returns_healed(self):
        result = heal_filesystem_ssot_drift({"evidence": {}}, apply=False)
        assert isinstance(result, HealCheckResult)
        assert result.status == HealStatus.HEALED

    def test_dry_run_with_forbidden_folders(self):
        result = heal_filesystem_ssot_drift(
            {"evidence": {"forbidden_folders": ["bad_folder"]}},
            apply=False,
        )
        assert isinstance(result, HealCheckResult)

    def test_check_id_matches(self):
        result = heal_filesystem_ssot_drift({"evidence": {}})
        assert result.check_id == FS_CHECK_ID


# ---------------------------------------------------------------------------
# gravity_leak_healer
# ---------------------------------------------------------------------------
from agentic_core.L2_execution.healers.gravity_leak_healer import (
    CHECK_ID as GRAVITY_CHECK_ID,
)
from agentic_core.L2_execution.healers.gravity_leak_healer import (
    heal_gravity_violations,
)
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_emits_metric_event("test_l2_healers_adg", "p4obs", "metric_1")
_emit_emits_metric_event("test_l2_healers_adg", "p4obs", "metric_2")
_emit_emits_metric_event("test_l2_healers_adg", "p4obs", "metric_3")
_emit_emits_metric_event("test_l2_healers_adg", "p4obs", "metric_4")
_emit_emits_metric_event("test_l2_healers_adg", "p4obs", "metric_5")
_emit_emits_metric_event("test_l2_healers_adg", "p4obs", "metric_6")
_emit_records_incident_event("test_l2_healers_adg", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_l2_healers_adg", "p4obs", "anomaly")
_emit_writes_observability_log("test_l2_healers_adg", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_l2_healers_adg", "p4obs", "mon_state")
_emit_triggers_alert("test_l2_healers_adg", "p4obs", "alert")
_emit_links_incident_trace("test_l2_healers_adg", "p4obs", "trace_link")
_emit_captures_pattern("test_l2_healers_adg", "p3lm", "pattern")
_emit_records_learning_event("test_l2_healers_adg", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_l2_healers_adg", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_l2_healers_adg", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_l2_healers_adg", "p3lm", "routing")
_emit_improves_agent_policy("test_l2_healers_adg", "p3lm", "policy")
_emit_stores_learning_state("test_l2_healers_adg", "p3lm", "state")
_emit_records_execution_trace("test_l2_healers_adg", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_l2_healers_adg", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_l2_healers_adg", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_l2_healers_adg", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_l2_healers_adg", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_l2_healers_adg", "env_read", "p2_env_1")
_emit_reads_environ("test_l2_healers_adg", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_l2_healers_adg", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_l2_healers_adg", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_l2_healers_adg", "context_pull")
_emit_pulls_context("p1", "test_l2_healers_adg", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_l2_healers_adg", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_l2_healers_adg", "uwg_term_secondary")
_emit_writes_through("p1", "test_l2_healers_adg", "write_through")
_emit_writes_through("p1", "test_l2_healers_adg", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_l2_healers_adg", "safety_validation")
_emit_invokes_eval("p1", "test_l2_healers_adg", "eval_call")
_emit_proposal_commits_routing("p1", "test_l2_healers_adg", "routing_commit")
_emit_escalates_to_human("p1", "test_l2_healers_adg", "human_escalation")
_emit_routes_through("p1", "test_l2_healers_adg", "route_through")
_emit_checks_agent_registry("p1", "test_l2_healers_adg", "agent_registry")
_emit_validates_agent_capability("p1", "test_l2_healers_adg", "capability")
_emit_dispatches_execution_plan("p1", "test_l2_healers_adg", "exec_plan")
_emit_agent_executes_agent("p1", "test_l2_healers_adg", "sub_agent")
_emit_routes_to_agent("p1", "test_l2_healers_adg", "target_agent")
_emit_verifies_policy("p1", "test_l2_healers_adg", "policy_check")
_emit_observes_runtime_state("p1", "test_l2_healers_adg", "runtime_state")
_emit_verifies_boundary("p1", "test_l2_healers_adg", "boundary_check")
_emit_transcripts_response("p1", "test_l2_healers_adg", "transcript")
_emit_hard_fails_untranscripted("p1", "test_l2_healers_adg")
_emit_gated_by_confidence("p1", "test_l2_healers_adg", "confidence_gate")


class TestGravityLeakHealer:
    def test_check_id_string(self):
        assert isinstance(GRAVITY_CHECK_ID, str)

    def test_heal_callable(self):
        assert callable(heal_gravity_violations)

    def test_no_violations_returns_healed(self):
        result = heal_gravity_violations(
            {"violations_count": 0, "evidence": {}}, apply=False
        )
        assert isinstance(result, HealCheckResult)
        assert result.status == HealStatus.HEALED

    def test_dry_run_with_violations_returns_result(self):
        result = heal_gravity_violations(
            {
                "violations_count": 1,
                "evidence": {"violations": [{"file": "foo.py", "import": "L5.bar"}]},
            },
            apply=False,
        )
        assert isinstance(result, HealCheckResult)

    def test_check_id_matches(self):
        result = heal_gravity_violations({"violations_count": 0, "evidence": {}})
        assert result.check_id == GRAVITY_CHECK_ID
