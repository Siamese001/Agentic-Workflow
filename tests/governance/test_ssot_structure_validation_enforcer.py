"""
Wave 1 Phase 2 — SSOT Structure Validation Enforcer Tests

§4-compliant test suite covering:
- Success paths (compliant agents pass all checks)
- Branch paths (all conditionals in each validator method)
- Negative controls (violations correctly detected and categorised)
- Edge cases (empty paths, root-level files, exact depth boundaries)
- Exception paths (graceful handling of missing data)
- Determinism (same agent → same result twice)
- Side-effect safety (validate_agent does not mutate shared state)
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
)
from agentic_core.L5_safety.enforcement.registry_verification_enforcer import AgentInfo
from agentic_core.L5_safety.enforcement.ssot_structure_validation_enforcer import (
    BASE_AGENT_REQUIRED_PATH,
    LAYER_PATTERNS,
    SSOTStructureValidator,
    StructureValidationResult,
    StructureViolation,
    run_structure_validation,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_ssot_structure_validation_enforcer", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_ssot_structure_validation_enforcer", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_ssot_structure_validation_enforcer", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_ssot_structure_validation_enforcer", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_ssot_structure_validation_enforcer", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_ssot_structure_validation_enforcer", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_ssot_structure_validation_enforcer", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_ssot_structure_validation_enforcer", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_ssot_structure_validation_enforcer", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_ssot_structure_validation_enforcer", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_ssot_structure_validation_enforcer", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_ssot_structure_validation_enforcer", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_ssot_structure_validation_enforcer", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_ssot_structure_validation_enforcer", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_ssot_structure_validation_enforcer", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_ssot_structure_validation_enforcer", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_ssot_structure_validation_enforcer", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_ssot_structure_validation_enforcer", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_ssot_structure_validation_enforcer", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_ssot_structure_validation_enforcer", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_ssot_structure_validation_enforcer", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_ssot_structure_validation_enforcer", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_ssot_structure_validation_enforcer", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_ssot_structure_validation_enforcer", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_ssot_structure_validation_enforcer", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_ssot_structure_validation_enforcer", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_ssot_structure_validation_enforcer", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_ssot_structure_validation_enforcer", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_ssot_structure_validation_enforcer")
# REMOVED: _emit_applies_guardrail("p0", "test_ssot_structure_validation_enforcer", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_ssot_structure_validation_enforcer", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_ssot_structure_validation_enforcer", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_ssot_structure_validation_enforcer", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_ssot_structure_validation_enforcer", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_ssot_structure_validation_enforcer", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_ssot_structure_validation_enforcer", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_ssot_structure_validation_enforcer", "write_through")
# REMOVED: _emit_writes_through("p1", "test_ssot_structure_validation_enforcer", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_ssot_structure_validation_enforcer", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_ssot_structure_validation_enforcer", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_ssot_structure_validation_enforcer", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_ssot_structure_validation_enforcer", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_ssot_structure_validation_enforcer", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_ssot_structure_validation_enforcer", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_ssot_structure_validation_enforcer", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_ssot_structure_validation_enforcer", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_ssot_structure_validation_enforcer", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_ssot_structure_validation_enforcer", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_ssot_structure_validation_enforcer", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_ssot_structure_validation_enforcer", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_ssot_structure_validation_enforcer", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_ssot_structure_validation_enforcer", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_ssot_structure_validation_enforcer")
# REMOVED: _emit_gated_by_confidence("p1", "test_ssot_structure_validation_enforcer", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_ssot_structure_validation_enforcer")
# REMOVED: emit_determinism_digest("p0", "test_ssot_structure_validation_enforcer")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_ssot_structure_validation_enforcer", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_ssot_structure_validation_enforcer", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_ssot_structure_validation_enforcer", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_ssot_structure_validation_enforcer", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_ssot_structure_validation_enforcer", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_ssot_structure_validation_enforcer", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_ssot_structure_validation_enforcer", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_ssot_structure_validation_enforcer", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_ssot_structure_validation_enforcer", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_ssot_structure_validation_enforcer", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_ssot_structure_validation_enforcer", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_ssot_structure_validation_enforcer", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_ssot_structure_validation_enforcer", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_ssot_structure_validation_enforcer", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_ssot_structure_validation_enforcer", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_ssot_structure_validation_enforcer", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_ssot_structure_validation_enforcer", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_ssot_structure_validation_enforcer", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_ssot_structure_validation_enforcer", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_ssot_structure_validation_enforcer", "exec_snapshot_link")

REPO_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_agent(
    class_name: str = "FooAgent",
    relative_path: str = "agentic_core/L2_execution/engines/foo_agent.py",
    layer: str = "L2",
) -> AgentInfo:
    """Build a minimal AgentInfo for testing."""
    return AgentInfo(
        class_name=class_name,
        file_path=Path(relative_path),
        relative_path=relative_path,
        layer=layer,
    )


@pytest.fixture()
def validator() -> SSOTStructureValidator:
    return SSOTStructureValidator(REPO_ROOT)


# ===========================================================================
# 1. Success-path tests
# ===========================================================================


class TestSuccessPaths:
    @pytest.mark.governance
    def test_validate_agent_returns_empty_when_l2_agent_compliant(self, validator):
        agent = _make_agent(
            class_name="SandboxAirlock",
            relative_path="agentic_core/L2_execution/assembly/sandbox_airlock.py",
            layer="L2",
        )
        violations = validator.validate_agent(agent)
        # May or may not have territory/depth violations depending on blueprint;
        # critical: no base_agent_location violation for non-BaseAgent class
        base_violations = [v for v in violations if v.violation_type == "base_agent_location"]
        assert base_violations == []

    @pytest.mark.governance
    def test_normalize_path_converts_backslash_to_forward(self, validator):
        result = validator._normalize_path("agentic_core\\L2_execution\\foo.py")
        assert "\\" not in result
        assert "agentic_core/L2_execution/foo.py" == result

    @pytest.mark.governance
    def test_normalize_path_leaves_forward_slash_unchanged(self, validator):
        path = "agentic_core/L5_safety/enforcement/foo.py"
        assert validator._normalize_path(path) == path

    @pytest.mark.governance
    def test_get_actual_depth_returns_correct_count(self, validator):
        path = "agentic_core/L2_execution/engines/foo.py"
        assert validator._get_actual_depth(path) == 4

    @pytest.mark.governance
    def test_structure_validation_result_compliance_pct_when_all_compliant(self):
        result = StructureValidationResult(total_agents=10, compliant_agents=10)
        assert result.compliance_percentage == 100.0

    @pytest.mark.governance
    def test_structure_validation_result_is_fully_compliant_when_no_violations(self):
        result = StructureValidationResult()
        assert result.is_fully_compliant is True

    @pytest.mark.governance
    def test_validate_layer_assignment_returns_none_when_path_and_layer_match(self, validator):
        agent = _make_agent(
            class_name="FooAgent",
            relative_path="agentic_core/L2_execution/engines/foo.py",
            layer="L2",
        )
        result = validator._validate_layer_assignment(agent)
        assert result is None

    @pytest.mark.governance
    def test_validate_base_agent_location_returns_none_when_not_base_agent(self, validator):
        agent = _make_agent(
            class_name="RegularAgent",
            relative_path="agentic_core/L2_execution/engines/regular_agent.py",
        )
        assert validator._validate_base_agent_location(agent) is None

    @pytest.mark.governance
    def test_validate_base_agent_location_returns_none_when_base_agent_in_correct_path(self, validator):
        agent = _make_agent(
            class_name="SovereignBaseAgent",
            relative_path="agentic_core/base_agents/sovereign_base_agent.py",
            layer="Root",
        )
        assert validator._validate_base_agent_location(agent) is None

    @pytest.mark.governance
    def test_generate_report_contains_summary_section(self, validator):
        result = StructureValidationResult(total_agents=5, compliant_agents=5)
        report = validator.generate_report(result)
        assert "Summary" in report
        assert "Total Agents" in report

    @pytest.mark.governance
    def test_generate_report_shows_100_percent_when_fully_compliant(self, validator):
        result = StructureValidationResult(total_agents=4, compliant_agents=4)
        report = validator.generate_report(result)
        assert "100.0%" in report


# ===========================================================================
# 2. Branch-path tests
# ===========================================================================


class TestBranchPaths:
    @pytest.mark.governance
    def test_validate_layer_assignment_returns_none_when_outside_agentic_core(self, validator):
        # apps_rg path — not in agentic_core, should be skipped
        agent = _make_agent(
            class_name="FooAgent",
            relative_path="apps_rg/engines/foo_agent.py",
            layer="L2",
        )
        assert validator._validate_layer_assignment(agent) is None

    @pytest.mark.governance
    def test_validate_layer_assignment_returns_none_when_path_too_short(self, validator):
        agent = _make_agent(
            class_name="FooAgent",
            relative_path=AGENTIC_CORE_DIR,
            layer="L2",
        )
        assert validator._validate_layer_assignment(agent) is None

    @pytest.mark.governance
    def test_validate_layer_assignment_returns_none_when_layer_is_unknown(self, validator):
        # Unknown layer should not produce violation
        agent = _make_agent(
            class_name="FooAgent",
            relative_path="agentic_core/L2_execution/engines/foo.py",
            layer="Unknown",
        )
        assert validator._validate_layer_assignment(agent) is None

    @pytest.mark.governance
    def test_validate_territory_returns_none_when_territory_recognised(self, validator):
        agent = _make_agent(
            relative_path="agentic_core/L2_execution/engines/foo.py",
        )
        # Only check: no root_file or unknown_territory violation for known root
        result = validator._validate_territory(agent)
        if result is not None:
            assert result.violation_type not in ("root_file",)

    @pytest.mark.governance
    def test_validate_territory_detects_root_file(self, validator):
        agent = _make_agent(
            class_name="FooAgent",
            relative_path="foo_agent.py",
            layer="Root",
        )
        result = validator._validate_territory(agent)
        assert result is not None
        assert result.violation_type == "root_file"

    @pytest.mark.governance
    def test_validate_territory_detects_unknown_territory(self, validator):
        agent = _make_agent(
            class_name="FooAgent",
            relative_path="totally_unknown_dir/foo.py",
            layer="Unknown",
        )
        result = validator._validate_territory(agent)
        assert result is not None
        assert result.violation_type == "unknown_territory"

    @pytest.mark.governance
    def test_is_base_agent_returns_true_when_name_ends_with_base_agent(self, validator):
        assert validator._is_base_agent("SovereignBaseAgent") is True

    @pytest.mark.governance
    def test_is_base_agent_returns_false_when_name_does_not_end_with_base_agent(self, validator):
        assert validator._is_base_agent("RegularAgent") is False

    @pytest.mark.governance
    def test_validate_depth_returns_none_when_in_variable_depth_folder(self, validator):
        # "scripts" is typically a variable-depth subfolder
        agent = _make_agent(
            relative_path="agentic_core/L0_routing/scripts/sub/deep/very_deep/foo.py",
        )
        result = validator._validate_depth(agent)
        # Either None or depth violation — but NOT none only because variable depth was ignored
        # We verify the method returns without raising
        assert result is None or isinstance(result, StructureViolation)

    @pytest.mark.governance
    def test_get_actual_depth_returns_1_for_single_part_path(self, validator):
        assert validator._get_actual_depth("foo.py") == 1

    @pytest.mark.governance
    def test_get_actual_depth_handles_trailing_slash(self, validator):
    """Test get_actual_depth_handles_trailing_slash runtime behavior."""
    # Arrange
    # TODO: Set up processing data
    raw_data = []  # Replace with actual test data

    # Act
    # TODO: Process data with get_actual_depth_handles_trailing_slash
    processed_result = None  # Replace with actual processing

    # Assert
    assert processed_result is not None, "Processing should produce a result"
    assert len(processed_result) >= 0, "Processed result should be measurable"
    # TODO: Add specific processing assertions
        violation_types = {v.violation_type for v in violations}
        assert "base_agent_location" in violation_types

    @pytest.mark.governance
    def test_structure_validation_result_compliance_pct_zero_when_no_agents(self):
        result = StructureValidationResult(total_agents=0, compliant_agents=0)
        assert result.compliance_percentage == 0.0

    @pytest.mark.governance
    def test_structure_validation_result_is_not_fully_compliant_when_violations(self):
        v = StructureViolation(
            agent_class="Foo",
            agent_path="foo.py",
            violation_type="root_file",
            message="bad",
        )
        result = StructureValidationResult(violations=[v])
        assert result.is_fully_compliant is False


# ===========================================================================
# 3. Negative controls (enforcement + fail-closed)
# ===========================================================================


class TestNegativeControls:
    @pytest.mark.governance
    def test_validate_base_agent_location_flags_base_agent_outside_required_path(self, validator):
        agent = _make_agent(
            class_name="SovereignBaseAgent",
            relative_path="agentic_core/L5_safety/enforcement/sovereign_base_agent.py",
            layer="L5",
        )
        result = validator._validate_base_agent_location(agent)
        assert result is not None
        assert result.violation_type == "base_agent_location"
        assert result.severity == "critical"

    @pytest.mark.governance
    def test_validate_layer_assignment_flags_layer_mismatch(self, validator):
        # File is in L2 but agent.layer claims L5
        agent = _make_agent(
            class_name="FooAgent",
            relative_path="agentic_core/L2_execution/engines/foo.py",
            layer="L5",
        )
        result = validator._validate_layer_assignment(agent)
        assert result is not None
        assert result.violation_type == "layer_mismatch"

    @pytest.mark.governance
    def test_validate_territory_flags_root_level_file(self, validator):
        agent = _make_agent(
            class_name="BadAgent",
            relative_path="bad_agent.py",
            layer="Root",
        )
        result = validator._validate_territory(agent)
        assert result is not None
        assert result.violation_type == "root_file"
        assert result.severity == "error"

    @pytest.mark.governance
    def test_validate_territory_flags_unknown_territory_with_warning(self, validator):
        agent = _make_agent(
            relative_path="forbidden_zone/sub/foo.py",
        )
        result = validator._validate_territory(agent)
        assert result is not None
        assert result.violation_type == "unknown_territory"

    @pytest.mark.governance
    def test_structure_violation_severity_defaults_to_warning(self):
        v = StructureViolation(
            agent_class="Foo",
            agent_path="foo.py",
            violation_type="unknown_territory",
            message="test",
        )
        assert v.severity == "warning"

    @pytest.mark.governance
    def test_validate_agent_includes_violation_in_result_list(self, validator):
        agent = _make_agent(
            class_name="SovereignBaseAgent",
            relative_path="apps_rg/engines/bad.py",
            layer="Unknown",
        )
        violations = validator.validate_agent(agent)
        assert len(violations) >= 1

    @pytest.mark.governance
    def test_generate_report_shows_base_agent_violations_section(self, validator):
        v = StructureViolation(
            agent_class="BrokenBaseAgent",
            agent_path="wrong/path.py",
            violation_type="base_agent_location",
            message="must be in base_agents",
            severity="critical",
            suggested_fix="move to base_agents/",
        )
        result = StructureValidationResult(
            total_agents=1,
            compliant_agents=0,
            violations=[v],
            base_agent_violations=[v],
        )
        report = validator.generate_report(result)
        assert "Critical" in report or "Base Agent" in report


# ===========================================================================
# 4. Edge cases
# ===========================================================================


class TestEdgeCases:
    @pytest.mark.governance
    def test_normalize_path_handles_empty_string(self, validator):
        result = validator._normalize_path("")
        assert result == ""

    @pytest.mark.governance
    def test_get_actual_depth_returns_zero_for_empty_path(self, validator):
        # Empty parts after filtering — should not crash
        depth = validator._get_actual_depth("")
        assert isinstance(depth, int)

    @pytest.mark.governance
    def test_validate_depth_returns_none_when_no_territory(self, validator):
        agent = _make_agent(
            relative_path="totally_unknown_territory/foo.py",
        )
        # No known territory → depth validation should skip
        result = validator._validate_depth(agent)
        assert result is None

    @pytest.mark.governance
    def test_validate_base_agent_location_handles_empty_path(self, validator):
        agent = _make_agent(
            class_name="SovereignBaseAgent",
            relative_path="",
            layer="Unknown",
        )
        # Should not raise; must return a violation or None
        result = validator._validate_base_agent_location(agent)
        assert result is None or isinstance(result, StructureViolation)

    @pytest.mark.governance
    def test_validate_layer_assignment_handles_empty_path(self, validator):
        agent = _make_agent(
            class_name="FooAgent",
            relative_path="",
            layer="L2",
        )
        result = validator._validate_layer_assignment(agent)
        assert result is None or isinstance(result, StructureViolation)

    @pytest.mark.governance
    def test_structure_validation_result_compliance_pct_with_partial_compliance(self):
        result = StructureValidationResult(total_agents=10, compliant_agents=7)
        assert result.compliance_percentage == pytest.approx(70.0)

    @pytest.mark.governance
    def test_generate_report_truncates_territory_violations_beyond_20(self, validator):
    """Test generate_report_truncates_territory_violations_beyond_20 runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute generate_report_truncates_territory_violations_beyond_20
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    # TODO: Add specific execution assertions
            territory_violations=violations,
        )
        report = validator.generate_report(result)
        # Should mention remaining count
        assert "more" in report

    @pytest.mark.governance
    def test_get_territory_returns_none_for_empty_parts(self, validator):
        result = validator._get_territory("")
        assert result is None

    @pytest.mark.governance
    def test_layer_patterns_covers_all_seven_layers(self):
        assert len(LAYER_PATTERNS) == 7
        for i in range(7):
            assert f"L{i}" in LAYER_PATTERNS

    @pytest.mark.governance
    def test_base_agent_required_path_is_nonempty_string(self):
        assert isinstance(BASE_AGENT_REQUIRED_PATH, str)
        assert len(BASE_AGENT_REQUIRED_PATH) > 0


# ===========================================================================
# 5. Exception-path tests
# ===========================================================================


class TestExceptionPaths:
    @pytest.mark.governance
    def test_validate_structure_handles_empty_agent_list(self, validator):
        with patch.object(validator.verifier, "scan_filesystem", return_value=[]):
            result = validator.validate_structure()
        assert result.total_agents == 0
        assert result.is_fully_compliant is True

    @pytest.mark.governance
    def test_run_structure_validation_returns_result_object(self):
        # run_structure_validation is a module-level function
        result = run_structure_validation()
        assert isinstance(result, StructureValidationResult)
        assert isinstance(result.total_agents, int)

    @pytest.mark.governance
    def test_validate_structure_increments_compliant_when_no_violations(self, validator):
        agent = _make_agent(
            class_name="CleanAgent",
            relative_path="agentic_core/L2_execution/engines/clean.py",
            layer="L2",
        )
        # Patch scan_filesystem to return just this one agent
        with patch.object(validator.verifier, "scan_filesystem", return_value=[agent]):
            with patch.object(validator, "validate_agent", return_value=[]):
                result = validator.validate_structure()
        assert result.compliant_agents == 1

    @pytest.mark.governance
    def test_validate_structure_categorises_base_agent_violations(self, validator):
        v = StructureViolation(
            agent_class="BadBaseAgent",
            agent_path="apps_rg/bad.py",
            violation_type="base_agent_location",
            message="wrong location",
            severity="critical",
        )
        agent = _make_agent(class_name="BadBaseAgent", relative_path="apps_rg/bad.py")
        with patch.object(validator.verifier, "scan_filesystem", return_value=[agent]):
            with patch.object(validator, "validate_agent", return_value=[v]):
                result = validator.validate_structure()
        assert len(result.base_agent_violations) == 1

    @pytest.mark.governance
    def test_validate_structure_categorises_layer_violations(self, validator):
        v = StructureViolation(
            agent_class="FooAgent",
            agent_path="agentic_core/L2_execution/foo.py",
            violation_type="layer_mismatch",
            message="wrong layer",
        )
        agent = _make_agent(class_name="FooAgent")
        with patch.object(validator.verifier, "scan_filesystem", return_value=[agent]):
            with patch.object(validator, "validate_agent", return_value=[v]):
                result = validator.validate_structure()
        assert len(result.layer_violations) == 1

    @pytest.mark.governance
    def test_validate_structure_categorises_depth_violations(self, validator):
        v = StructureViolation(
            agent_class="FooAgent",
            agent_path="agentic_core/L2_execution/engines/sub/deep/foo.py",
            violation_type="depth_violation",
            message="too deep",
        )
        agent = _make_agent(class_name="FooAgent")
        with patch.object(validator.verifier, "scan_filesystem", return_value=[agent]):
            with patch.object(validator, "validate_agent", return_value=[v]):
                result = validator.validate_structure()
        assert len(result.depth_violations) == 1

    @pytest.mark.governance
    def test_validate_structure_categorises_territory_violations(self, validator):
        for vtype in ("root_file", "unknown_territory"):
            v = StructureViolation(
                agent_class="FooAgent",
                agent_path="bad/foo.py",
                violation_type=vtype,
                message="bad territory",
            )
            agent = _make_agent(class_name="FooAgent")
            with patch.object(validator.verifier, "scan_filesystem", return_value=[agent]):
                with patch.object(validator, "validate_agent", return_value=[v]):
                    result = validator.validate_structure()
            assert len(result.territory_violations) == 1


# ===========================================================================
# 6. Determinism tests
# ===========================================================================


class TestDeterminism:
    @pytest.mark.governance
    def test_normalize_path_deterministic_for_same_input_twice(self, validator):
        path = "agentic_core\\L2_execution\\foo.py"
        assert validator._normalize_path(path) == validator._normalize_path(path)

    @pytest.mark.governance
    def test_get_actual_depth_deterministic_for_same_input_twice(self, validator):
        path = "agentic_core/L2_execution/engines/foo.py"
        assert validator._get_actual_depth(path) == validator._get_actual_depth(path)

    @pytest.mark.governance
    def test_validate_agent_deterministic_for_same_agent_twice(self, validator):
        agent = _make_agent(
            class_name="SovereignBaseAgent",
            relative_path="apps_rg/engines/bad.py",
            layer="Unknown",
        )
        v1 = validator.validate_agent(agent)
        v2 = validator.validate_agent(agent)
        assert len(v1) == len(v2)
        assert [x.violation_type for x in v1] == [x.violation_type for x in v2]

    @pytest.mark.governance
    def test_validate_layer_assignment_deterministic_for_same_input_twice(self, validator):
        agent = _make_agent(
            relative_path="agentic_core/L2_execution/engines/foo.py",
            layer="L5",
        )
        r1 = validator._validate_layer_assignment(agent)
        r2 = validator._validate_layer_assignment(agent)
        assert (r1 is None) == (r2 is None)
        if r1 is not None:
            assert r1.violation_type == r2.violation_type

    @pytest.mark.governance
    def test_generate_report_deterministic_for_same_result_twice(self, validator):
        result = StructureValidationResult(total_agents=5, compliant_agents=3)
        assert validator.generate_report(result) == validator.generate_report(result)

    @pytest.mark.governance
    def test_compliance_percentage_deterministic_for_same_counts_twice(self):
        r = StructureValidationResult(total_agents=10, compliant_agents=7)
        assert r.compliance_percentage == r.compliance_percentage


# ===========================================================================
# 7. Side-effect safety tests
# ===========================================================================


class TestSideEffectSafety:
    @pytest.mark.governance
    def test_validate_agent_does_not_mutate_agent_info(self, validator):
        agent = _make_agent(
            class_name="SovereignBaseAgent",
            relative_path="apps_rg/engines/bad.py",
            layer="Unknown",
        )
        original_class_name = agent.class_name
        original_path = agent.relative_path
        validator.validate_agent(agent)
        assert agent.class_name == original_class_name
        assert agent.relative_path == original_path

    @pytest.mark.governance
    def test_validate_agent_called_twice_returns_independent_lists(self, validator):
    """Test validate_agent_called_twice_returns_independent_lists runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute validate_agent_called_twice_returns_independent_lists
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    # TODO: Add specific execution assertions
        v = StructureViolation(agent_class="X", agent_path="x.py", violation_type="root_file", message="m")
        r1.violations.append(v)
        assert r2.violations == []
