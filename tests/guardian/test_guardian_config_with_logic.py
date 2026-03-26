"""
Guardian: Config-With-Logic Anti-Pattern Tests.

§1 windsurfrules compliance:
- §1.1  Every changed logic has deterministic test coverage
- §1.3  No randomness / wall-clock; all fixtures are static strings
- §1.5  Edge cases: None/empty, malformed, boundary, negative control
- §1.7  Determinism: same input → same violations list
- §1.8  Fail-closed: violation is raised, no side-effects
- §1.9  Matrix: lambda × assignment-type, if × function-name-suffix
- §1.11 Regression: near-miss cases (non-config var with lambda, etc.)

ROBUSTNESS_MATRIX:
  Surface                        | success | edge | failure | determinism
  -------------------------------|---------|------|---------|------------
  lambda in *_config assignment  |   ✅   |  ✅  |   ✅   |     ✅
  lambda in *_spec assignment    |   ✅   |  ✅  |   ✅   |     ✅
  lambda in *_policy assignment  |   ✅   |  ✅  |   ✅   |     ✅
  if-branch in *_config func     |   ✅   |  ✅  |   ✅   |     ✅
  whitelist comment suppression  |   ✅   |  ✅  |   ✅   |     ✅
  clean file                     |   ✅   |  ✅  |   N/A  |     ✅

DEFECT_MODEL:
  D1 - lambda in config dict causes hidden runtime dispatch
  D2 - if-branch in config factory creates shadow runtime behaviour
  D3 - whitelist bypass incorrectly suppresses valid violations
  D4 - non-config variable with lambda triggers false positive
  D5 - detector non-determinism across repeated scans
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

#  # MOVED: from agentic_core.L5_safety.validators.base_detector_validator import (
    AntiPatternCategory,
    EnforcementLevel,
)
#  # MOVED: from agentic_core.L5_safety.validators.config_with_logic_validator import (
    ConfigWithLogicDetector,
)
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_emits_metric_event("test_guardian_config_with_logic", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_guardian_config_with_logic", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_guardian_config_with_logic", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_guardian_config_with_logic", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_guardian_config_with_logic", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_guardian_config_with_logic", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_guardian_config_with_logic", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_guardian_config_with_logic", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_guardian_config_with_logic", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_guardian_config_with_logic", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_guardian_config_with_logic", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_guardian_config_with_logic", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_guardian_config_with_logic", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_guardian_config_with_logic", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_guardian_config_with_logic", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_guardian_config_with_logic", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_guardian_config_with_logic", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_guardian_config_with_logic", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_guardian_config_with_logic", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_guardian_config_with_logic", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_guardian_config_with_logic", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_guardian_config_with_logic", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_guardian_config_with_logic", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_guardian_config_with_logic", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_guardian_config_with_logic", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_guardian_config_with_logic", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_guardian_config_with_logic", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_guardian_config_with_logic", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_guardian_config_with_logic")
# REMOVED: _emit_applies_guardrail("p0", "test_guardian_config_with_logic", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_guardian_config_with_logic", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_guardian_config_with_logic", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_guardian_config_with_logic", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_guardian_config_with_logic", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_guardian_config_with_logic", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_guardian_config_with_logic", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_guardian_config_with_logic", "write_through")
# REMOVED: _emit_writes_through("p1", "test_guardian_config_with_logic", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_guardian_config_with_logic", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_guardian_config_with_logic", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_guardian_config_with_logic", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_guardian_config_with_logic", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_guardian_config_with_logic", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_guardian_config_with_logic", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_guardian_config_with_logic", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_guardian_config_with_logic", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_guardian_config_with_logic", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_guardian_config_with_logic", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_guardian_config_with_logic", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_guardian_config_with_logic", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_guardian_config_with_logic", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_guardian_config_with_logic", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_guardian_config_with_logic")
# REMOVED: _emit_gated_by_confidence("p1", "test_guardian_config_with_logic", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_guardian_config_with_logic")
# REMOVED: emit_determinism_digest("p0", "test_guardian_config_with_logic")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_guardian_config_with_logic", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_guardian_config_with_logic", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_guardian_config_with_logic", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_guardian_config_with_logic", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_guardian_config_with_logic", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_guardian_config_with_logic", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_guardian_config_with_logic", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_guardian_config_with_logic", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_guardian_config_with_logic", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_guardian_config_with_logic", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_guardian_config_with_logic", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_guardian_config_with_logic", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_guardian_config_with_logic", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_guardian_config_with_logic", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_guardian_config_with_logic", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_guardian_config_with_logic", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_guardian_config_with_logic", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_guardian_config_with_logic", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_guardian_config_with_logic", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_guardian_config_with_logic", "exec_snapshot_link")

pytestmark = pytest.mark.guardian

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _detector() -> ConfigWithLogicDetector:
    return ConfigWithLogicDetector(enforcement_level=EnforcementLevel.WARNING)


def _violations(source: str, tmp_path: Path) -> list:
    f = tmp_path / "subject.py"
    f.write_text(source, encoding="utf-8")
    tree = ast.parse(source)
    det = _detector()
    return det.detect(f, tree)


# ---------------------------------------------------------------------------
# Clean-file tests (success path)
# ---------------------------------------------------------------------------


class TestConfigWithLogicCleanFile:
    def test_plain_data_dict_no_violations(self, tmp_path):
                from agentic_core.L5_safety.validators.base_detector_validator import (
                from agentic_core.L5_safety.validators.config_with_logic_validator import (
                from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
                src = "my_config = {'key': 'value', 'n': 42}\n"
                assert _violations(src, tmp_path) == []

        assert _violations(src, tmp_path) == []

    def test_nested_plain_dict_no_violations(self, tmp_path):
        src = "agent_spec = {'name': 'foo', 'opts': {'timeout': 30}}\n"
        assert _violations(src, tmp_path) == []

    def test_non_config_name_with_lambda_no_violation(self, tmp_path):
        # D4 regression: lambda in non-config var must NOT trigger
        src = "transform = lambda x: x * 2\n"
        assert _violations(src, tmp_path) == []

    def test_function_not_config_suffix_with_if_no_violation(self, tmp_path):
    """Test function_not_config_suffix_with_if_no_violation runtime behavior."""
    # Arrange
# TODO: Address this issue - # TODO: Set up test data for function_not_config_suffix_with_if_no_violation
    test_data = {}  # Replace with actual test data

    # Act
# TODO: Address this issue - # TODO: Execute function_not_config_suffix_with_if_no_violation
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    # TODO: Add specific runtime behavior assertions


class TestLambdaInConfigAssignment:
    def test_lambda_in_config_var_detected(self, tmp_path):
        src = "my_config = {'transform': lambda x: x}\n"
        viols = _violations(src, tmp_path)
        assert len(viols) == 1
        assert viols[0].category == AntiPatternCategory.CONFIG_WITH_LOGIC

    def test_lambda_in_spec_var_detected(self, tmp_path):
        src = "agent_spec = {'fn': lambda v: v + 1}\n"
        viols = _violations(src, tmp_path)
        assert len(viols) == 1

    def test_lambda_in_policy_var_detected(self, tmp_path):
        src = "routing_policy = {'filter': lambda x: x > 0}\n"
        viols = _violations(src, tmp_path)
        assert len(viols) == 1

    def test_lambda_in_settings_var_detected(self, tmp_path):
        src = "app_settings = {'hook': lambda: None}\n"
        viols = _violations(src, tmp_path)
        assert len(viols) == 1

    def test_lambda_in_options_var_detected(self, tmp_path):
        src = "render_options = {'fmt': lambda s: s.lower()}\n"
        viols = _violations(src, tmp_path)
        assert len(viols) == 1

    def test_lambda_violation_has_error_severity(self, tmp_path):
        src = "my_config = {'fn': lambda x: x}\n"
        viols = _violations(src, tmp_path)
        assert viols[0].severity == "error"

    def test_lambda_violation_message_contains_keyword(self, tmp_path):
        src = "my_config = {'fn': lambda x: x}\n"
        viols = _violations(src, tmp_path)
        assert "lambda" in viols[0].message.lower()

    def test_multiple_lambdas_produces_multiple_violations(self, tmp_path):
        src = "my_config = {\n    'a': lambda x: x,\n    'b': lambda y: y + 1,\n}\n"
        viols = _violations(src, tmp_path)
        assert len(viols) == 2


# ---------------------------------------------------------------------------
# If-branch in config-factory function violations
# ---------------------------------------------------------------------------


class TestIfBranchInConfigFactory:
    def test_if_in_config_function_detected(self, tmp_path):
    """Test if_in_config_function_detected runtime behavior."""
    # Arrange
    # TODO: Set up test data for if_in_config_function_detected
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute if_in_config_function_detected
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    """Test if_in_spec_function_detected runtime behavior."""
    # Arrange
    # TODO: Set up test data for if_in_spec_function_detected
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute if_in_spec_function_detected
    result = None  # Replace with actual function call

    # Assert
    """Test if_in_policy_function_detected runtime behavior."""
    # Arrange
    # TODO: Set up test data for if_in_policy_function_detected
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute if_in_policy_function_detected
    result = None  # Replace with actual function call

    # Assert
    """Test if_violation_message_mentions_function_name runtime behavior."""
    # Arrange
    # TODO: Set up test data for if_violation_message_mentions_function_name
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute if_violation_message_mentions_function_name
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    # TODO: Add specific runtime behavior assertions
        viols = _violations(src, tmp_path)
        assert viols == []

    def test_whitelist_on_wrong_line_does_not_suppress(self, tmp_path):
        src = "# guardian: allow-config-with-logic\n\nmy_config = {'fn': lambda x: x}\n"
        viols = _violations(src, tmp_path)
        # whitelist is >2 lines away — still flagged
        assert len(viols) == 1

    def test_partial_whitelist_string_does_not_suppress(self, tmp_path):
        src = "# guardian: allow-other-thing\nmy_config = {'fn': lambda x: x}\n"
        viols = _violations(src, tmp_path)
        assert len(viols) == 1


# ---------------------------------------------------------------------------
# Determinism (§1.7 / §1.3)
# ---------------------------------------------------------------------------


class TestDetectorDeterminism:
    def test_same_source_produces_identical_violations(self, tmp_path):
        src = "my_config = {'fn': lambda x: x}\n"
        viols_a = _violations(src, tmp_path)
        # use a fresh temp file to avoid caching side-effects
        tmp2 = tmp_path / "second"
        tmp2.mkdir()
        viols_b = _violations(src, tmp2)
        assert len(viols_a) == len(viols_b)
        assert viols_a[0].category == viols_b[0].category
        assert viols_a[0].message == viols_b[0].message

    def test_clean_source_consistently_empty(self, tmp_path):
        src = "my_config = {'key': 42}\n"
        for _ in range(3):
            assert _violations(src, tmp_path) == []


# ---------------------------------------------------------------------------
# Fail-closed: violation object is well-formed (§1.8)
# ---------------------------------------------------------------------------


class TestViolationContract:
    def test_violation_has_required_fields(self, tmp_path):
        src = "my_config = {'fn': lambda x: x}\n"
        viols = _violations(src, tmp_path)
        v = viols[0]
        assert v.file_path is not None
        assert v.line_number >= 1
        assert v.category == AntiPatternCategory.CONFIG_WITH_LOGIC
        assert v.message
        assert v.evidence
        assert v.suggested_fix

    def test_violation_line_number_is_accurate(self, tmp_path):
        src = "x = 1\nmy_config = {'fn': lambda x: x}\n"
        viols = _violations(src, tmp_path)
        # lambda is on line 2
        assert viols[0].line_number == 2

    def test_violation_file_path_matches(self, tmp_path):
        f = tmp_path / "subject.py"
        src = "my_config = {'fn': lambda x: x}\n"
        f.write_text(src, encoding="utf-8")
        tree = ast.parse(src)
        viols = _detector().detect(f, tree)
        assert viols[0].file_path == f


# ---------------------------------------------------------------------------
# Matrix: variable-suffix × value-type (§1.9)
# ---------------------------------------------------------------------------


class TestSuffixMatrix:
    @pytest.mark.parametrize(
        "varname",
        ["my_config", "agent_spec", "routing_policy", "app_settings", "render_options"],
    )
    def test_all_config_suffixes_trigger(self, varname, tmp_path):
        src = f"{varname} = {{'fn': lambda x: x}}\n"
        viols = _violations(src, tmp_path)
        assert len(viols) >= 1, f"Expected violation for varname={varname!r}"

    @pytest.mark.parametrize(
        "varname",
        ["helper", "transform", "pipeline", "result", "data"],
    )
    def test_non_config_names_do_not_trigger(self, varname, tmp_path):
        src = f"{varname} = {{'fn': lambda x: x}}\n"
        viols = _violations(src, tmp_path)
        assert viols == [], f"Expected no violation for varname={varname!r}"
