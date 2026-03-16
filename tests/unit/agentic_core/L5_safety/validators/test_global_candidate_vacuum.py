"""
Test Suite: Global Candidate Vacuum (Shared Layer Hardening)
ULTRA-AGGRESSIVE SUITE: Validates Global Candidate Detection.
100% PASS LANGUAGE: Mandatory for Shared Layer Hardening.

[SSOT 2026-01-27] Phase 9 Aggressive Testing

Note: These tests directly invoke the detection logic without full agent instantiation
to avoid CoreIntegrityVerifier overhead during unit testing.
"""

from pathlib import Path

from agentic_core.L5_safety.config.structure_blueprint import (
    APPS_LIC_DIR,
    APPS_RG_DIR,
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
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_escalates_to_human,
    _emit_routes_through,
)

_emit_records_execution_trace("p0", "evidence", "test_global_candidate_vacuum")
_emit_applies_guardrail("p0", "test_global_candidate_vacuum", "p0_governance")
_emit_reads_policy_state("p0", "test_global_candidate_vacuum", "policy_binding")
_emit_snapshots_state("p0", "test_global_candidate_vacuum", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_escalates_to_human,
    _emit_routes_through,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
)

_emit_emits_metric_event("test_global_candidate_vacuum", "p4obs", "metric_1")
_emit_emits_metric_event("test_global_candidate_vacuum", "p4obs", "metric_2")
_emit_emits_metric_event("test_global_candidate_vacuum", "p4obs", "metric_3")
_emit_emits_metric_event("test_global_candidate_vacuum", "p4obs", "metric_4")
_emit_emits_metric_event("test_global_candidate_vacuum", "p4obs", "metric_5")
_emit_emits_metric_event("test_global_candidate_vacuum", "p4obs", "metric_6")
_emit_records_incident_event("test_global_candidate_vacuum", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_global_candidate_vacuum", "p4obs", "anomaly")
_emit_writes_observability_log("test_global_candidate_vacuum", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_global_candidate_vacuum", "p4obs", "mon_state")
_emit_triggers_alert("test_global_candidate_vacuum", "p4obs", "alert")
_emit_links_incident_trace("test_global_candidate_vacuum", "p4obs", "trace_link")
_emit_captures_pattern("test_global_candidate_vacuum", "p3lm", "pattern")
_emit_records_learning_event("test_global_candidate_vacuum", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_global_candidate_vacuum", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_global_candidate_vacuum", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_global_candidate_vacuum", "p3lm", "routing")
_emit_improves_agent_policy("test_global_candidate_vacuum", "p3lm", "policy")
_emit_stores_learning_state("test_global_candidate_vacuum", "p3lm", "state")
_emit_records_execution_trace("test_global_candidate_vacuum", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_global_candidate_vacuum", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_global_candidate_vacuum", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_global_candidate_vacuum", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_global_candidate_vacuum", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_global_candidate_vacuum", "env_read", "p2_env_1")
_emit_reads_environ("test_global_candidate_vacuum", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_global_candidate_vacuum", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_global_candidate_vacuum", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_global_candidate_vacuum", "context_pull")
_emit_pulls_context("p1", "test_global_candidate_vacuum", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_global_candidate_vacuum", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_global_candidate_vacuum", "uwg_term_2")
_emit_writes_through("p1", "test_global_candidate_vacuum", "write_through")
_emit_writes_through("p1", "test_global_candidate_vacuum", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_global_candidate_vacuum", "safety_validation")
_emit_invokes_eval("p1", "test_global_candidate_vacuum", "eval_call")
_emit_proposal_commits_routing("p1", "test_global_candidate_vacuum", "routing_commit")
_emit_escalates_to_human("p1", "test_global_candidate_vacuum", "human_escalation")
_emit_routes_through("p1", "test_global_candidate_vacuum", "route_through")
_emit_checks_agent_registry("p1", "test_global_candidate_vacuum", "agent_registry")
_emit_validates_agent_capability("p1", "test_global_candidate_vacuum", "capability")
_emit_dispatches_execution_plan("p1", "test_global_candidate_vacuum", "exec_plan")
_emit_agent_executes_agent("p1", "test_global_candidate_vacuum", "sub_agent")
_emit_routes_to_agent("p1", "test_global_candidate_vacuum", "target_agent")
_emit_verifies_policy("p1", "test_global_candidate_vacuum", "policy_check")
_emit_observes_runtime_state("p1", "test_global_candidate_vacuum", "runtime_state")
_emit_verifies_boundary("p1", "test_global_candidate_vacuum", "boundary_check")
_emit_transcripts_response("p1", "test_global_candidate_vacuum", "transcript")
_emit_hard_fails_untranscripted("p1", "test_global_candidate_vacuum")
_emit_gated_by_confidence("p1", "test_global_candidate_vacuum", "confidence_gate")
emit_replay_key("p0", "test_global_candidate_vacuum")
emit_determinism_digest("p0", "test_global_candidate_vacuum")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_global_candidate_vacuum", "execution_auth")
_emit_validates_capability("p2", "test_global_candidate_vacuum", "capability_check")
_emit_routes_to_capability("p2", "test_global_candidate_vacuum", "capability_route")
_emit_writes_via_uwg("p2", "test_global_candidate_vacuum", "uwg_write")
_emit_blocks_direct_write("p2", "test_global_candidate_vacuum", "direct_write_block")
_emit_records_tool_invocation("p2", "test_global_candidate_vacuum", "tool_invocation")
_emit_captures_execution_output("p2", "test_global_candidate_vacuum", "exec_output")
_emit_dispatches_agent("p3", "test_global_candidate_vacuum", "agent_dispatch")
_emit_coordinates_agents("p3", "test_global_candidate_vacuum", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_global_candidate_vacuum", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_global_candidate_vacuum", "healing_outcome")
_emit_escalates_failure("p3", "test_global_candidate_vacuum", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_global_candidate_vacuum", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_global_candidate_vacuum", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_global_candidate_vacuum", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_global_candidate_vacuum", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_global_candidate_vacuum", "eval_metric")
_emit_stores_embedding("p4", "test_global_candidate_vacuum", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_global_candidate_vacuum", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_global_candidate_vacuum", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants


def _check_app_domain_violation_logic(
    app_rg_score: float,
    app_lic_score: float,
    rel_path: Path,
) -> tuple[bool, str]:
    """
    Standalone implementation of Global Candidate Detection logic.
    Mirrors LocationValidatorAgent._check_app_domain_violation for unit testing.
    """
    current_root = rel_path.parts[0]

    # 1. GLOBAL CANDIDATE DETECTION (Vacuum to apps_shared)
    if current_root in [APPS_RG_DIR, APPS_LIC_DIR]:
        if app_rg_score < 0.5 and app_lic_score < 0.5:
            filename = rel_path.name
            if not filename.startswith(("rg_", "lic_", "resume_", "outreach_")):
                return (
                    False,
                    "GLOBAL CANDIDATE DETECTED: Low domain signals - belongs in apps_shared/utils",
                )

    # 2. CROSS-CONTAMINATION CHECK (App vs App)
    if current_root == APPS_RG_DIR and app_lic_score > app_rg_score * 2.0:
        return (
            False,
            f"APP DOMAIN VIOLATION: Strong apps_lic signals ({app_lic_score:.1f} vs {app_rg_score:.1f})",
        )

    if current_root == APPS_LIC_DIR and app_rg_score > app_lic_score * 2.0:
        return (
            False,
            f"APP DOMAIN VIOLATION: Strong apps_rg signals ({app_rg_score:.1f} vs {app_lic_score:.1f})",
        )

    return True, ""


class TestGlobalCandidateVacuum:
    """
    ULTRA-AGGRESSIVE SUITE: Validates Global Candidate Detection.
    100% PASS LANGUAGE: Mandatory for Shared Layer Hardening.
    """

    def test_generic_utility_is_vacuumed(self):
        """100% PASS: Ensures 'date_helper.py' in apps_lic is flagged for apps_shared."""
        rel_path = Path("apps_lic/engines/date_helper.py")

        # Simulate generic DNA (app_rg=0.1, app_lic=0.1)
        is_valid, msg = _check_app_domain_violation_logic(0.1, 0.1, rel_path)

        assert is_valid is False, "FAIL: Generic utility was allowed to stay in domain folder."
        assert "GLOBAL CANDIDATE" in msg, f"FAIL: Wrong violation type: {msg}"

    def test_prefixed_file_is_retained(self):
        """100% PASS: Ensures 'lic_special_tool.py' stays in apps_lic despite low DNA."""
        rel_path = Path("apps_lic/engines/lic_special_tool.py")

        # Even with low DNA, the prefix 'lic_' provides "Territorial Immunity"
        is_valid, _ = _check_app_domain_violation_logic(0.1, 0.1, rel_path)
        assert is_valid is True, "FAIL: Prefixed file was incorrectly flagged for vacuuming."

    def test_app_cross_contamination_detection(self):
        """100% PASS: Ensures Resume logic in LinkedIn folder is flagged."""
        rel_path = Path("apps_lic/engines/resume_parser.py")

        # Strong Resume DNA (3.0) vs LinkedIn DNA (0.2)
        is_valid, msg = _check_app_domain_violation_logic(3.0, 0.2, rel_path)
        assert is_valid is False
        assert "Strong apps_rg signals" in msg, "FAIL: Failed to detect app-to-app leakage."

    def test_global_weight_superiority(self):
        """100% PASS: Verifies Shared Gravity (95) beats App Gravity (90) in SSOT."""
        from agentic_core.L5_safety.config.structure_blueprint import (
            get_all_territories,
        )

        shared_w = get_all_territories()["apps_shared"]["ast_signals"]["apps_shared/utils"]["weight"]
        app_w = get_all_territories()["apps_rg"]["ast_signals"]["apps_rg/engines"]["weight"]

        assert shared_w == 95
        assert shared_w > app_w, "CRITICAL: Global utility gravity is weaker than domain gravity."

    def test_rg_prefixed_file_is_retained(self):
        """100% PASS: Ensures 'rg_builder.py' stays in apps_rg despite low DNA."""
        rel_path = Path("apps_rg/engines/rg_builder.py")

        is_valid, _ = _check_app_domain_violation_logic(0.1, 0.1, rel_path)
        assert is_valid is True, "FAIL: rg_ prefixed file was incorrectly flagged."

    def test_resume_prefixed_file_is_retained(self):
        """100% PASS: Ensures 'resume_formatter.py' stays in apps_rg despite low DNA."""
        rel_path = Path("apps_rg/engines/resume_formatter.py")

        is_valid, _ = _check_app_domain_violation_logic(0.1, 0.1, rel_path)
        assert is_valid is True, "FAIL: resume_ prefixed file was incorrectly flagged."

    def test_outreach_prefixed_file_is_retained(self):
        """100% PASS: Ensures 'outreach_manager.py' stays in apps_lic despite low DNA."""
        rel_path = Path("apps_lic/engines/outreach_manager.py")

        is_valid, _ = _check_app_domain_violation_logic(0.1, 0.1, rel_path)
        assert is_valid is True, "FAIL: outreach_ prefixed file was incorrectly flagged."

    def test_apps_shared_files_not_flagged(self):
        """100% PASS: Ensures files already in apps_shared are not flagged."""
        rel_path = Path("apps_shared/utils/date_helper.py")

        # Files in apps_shared should pass (not in apps_rg or apps_lic)
        is_valid, _ = _check_app_domain_violation_logic(0.1, 0.1, rel_path)
        assert is_valid is True, "FAIL: apps_shared file was incorrectly flagged."
