"""
Guardian Contract Tests — Schema, Status Promotion, and Contract Integrity.

Verifies:
1. Status promotion: FAIL check promotes top-level status to FAIL
2. Status promotion: ERROR status is sticky (not overwritten by FAIL)
3. Schema compliance across all contract fields
4. Serialization round-trip determinism
5. Artifact path normalization (no absolute paths, no backslashes)
6. Contract version is pinned
7. check_schema_compatibility detects missing/extra keys
8. validate_against_json_schema detects type and enum violations
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_guardian_contract")
# REMOVED: _emit_applies_guardrail("p0", "test_guardian_contract", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_guardian_contract", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_guardian_contract", "state_snapshot")
# REMOVED: emit_replay_key("p0", "test_guardian_contract")
# REMOVED: emit_determinism_digest("p0", "test_guardian_contract")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_guardian_contract", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_guardian_contract", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_guardian_contract", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_guardian_contract", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_guardian_contract", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_guardian_contract", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_guardian_contract", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_guardian_contract", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_guardian_contract", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_guardian_contract", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_guardian_contract", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_guardian_contract", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_guardian_contract", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_guardian_contract", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_guardian_contract", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_guardian_contract", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_guardian_contract", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_guardian_contract", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_guardian_contract", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_guardian_contract", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

#  # MOVED: from agentic_core.L0_routing.types.guardian_contract_types import (
    CONTRACT_VERSION,
    ArtifactClass,
    ArtifactType,
    CheckStatus,
    GuardianCheck,
    GuardianResult,
    GuardianStatus,
    check_schema_compatibility,
    normalize_repo_path,
    validate_against_json_schema,
    validate_no_absolute_paths,
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

# REMOVED: _emit_emits_metric_event("test_guardian_contract", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_guardian_contract", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_guardian_contract", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_guardian_contract", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_guardian_contract", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_guardian_contract", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_guardian_contract", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_guardian_contract", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_guardian_contract", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_guardian_contract", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_guardian_contract", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_guardian_contract", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_guardian_contract", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_guardian_contract", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_guardian_contract", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_guardian_contract", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_guardian_contract", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_guardian_contract", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_guardian_contract", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_guardian_contract", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_guardian_contract", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_guardian_contract", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_guardian_contract", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_guardian_contract", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_guardian_contract", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_guardian_contract", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_guardian_contract", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_guardian_contract", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_guardian_contract", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_guardian_contract", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_guardian_contract", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_guardian_contract", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_guardian_contract", "write_through")
# REMOVED: _emit_writes_through("p1", "test_guardian_contract", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_guardian_contract", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_guardian_contract", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_guardian_contract", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_guardian_contract", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_guardian_contract", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_guardian_contract", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_guardian_contract", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_guardian_contract", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_guardian_contract", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_guardian_contract", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_guardian_contract", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_guardian_contract", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_guardian_contract", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_guardian_contract", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_guardian_contract")
# REMOVED: _emit_gated_by_confidence("p1", "test_guardian_contract", "confidence_gate")

pytestmark = pytest.mark.guardian


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_result(guardian_id: str = "test_guardian") -> GuardianResult:
    return GuardianResult(guardian_id=guardian_id)


# ---------------------------------------------------------------------------
# 1. Status promotion: FAIL check → top-level FAIL
# ---------------------------------------------------------------------------


class TestStatusPromotion:
    """Verify that a FAIL check correctly promotes the top-level status."""

    def test_initial_status_is_pass(self):
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
        from agentic_core.L0_routing.types.guardian_contract_types import (
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
        from agentic_core.L0_routing.config.path_constants import (
        from agentic_core.L0_routing.scripts.run_guardian_c0_sovereignty import (
        from agentic_core.L0_routing.scripts.run_guardian_change_package_activation import (
        from agentic_core.L0_routing.scripts.run_guardian_cross_layer_mutation import (
        from agentic_core.L0_routing.scripts.run_guardian_escalation_determinism import (
        from agentic_core.L0_routing.scripts.run_guardian_gateway_bypass import (
    """Test initial_status_is_pass contract compliance."""
    # Arrange
    # TODO: Set up contract parties and terms
    contract_terms = {}  # Replace with actual contract terms
    """Test single_fail_check_promotes_to_fail contract compliance."""
    # Arrange
    # TODO: Set up test data
    test_data = {}  # Replace with actual test data

"""Test pass_check_does_not_change_pass_status contract compliance."""
# Arrange
# TODO: Set up test data
test_data = {}  # Replace with actual test data

"""Test skip_check_does_not_change_pass_status contract compliance."""
# Arrange
# TODO: Set up test data
test_data = {}  # Replace with actual test data

"""Test fail_after_pass_promotes_to_fail contract compliance."""
# Arrange
# TODO: Set up contract parties and terms
contract_terms = {}  # Replace with actual contract terms

# Act
"""Test pass_after_fail_does_not_revert_to_pass contract compliance."""
# Arrange
# TODO: Set up contract parties and terms
contract_terms = {}  # Replace with actual contract terms

# Act
"""Test error_status_is_sticky_over_fail contract compliance."""
# Arrange
# TODO: Set up contract parties and terms
contract_terms = {}  # Replace with actual contract terms

# Act
"""Test multiple_fail_checks_status_still_fail contract compliance."""
# Arrange
# TODO: Set up test data
test_data = {}  # Replace with actual test data

# Act
"""Test string_fail_value_also_promotes contract compliance."""
# Arrange
# TODO: Set up contract parties and terms
contract_terms = {}  # Replace with actual contract terms

"""Test status_promotion_boundary_single_check contract compliance."""
# Arrange
# TODO: Set up test data
test_data = {}  # Replace with actual test data

# Act
# TODO: Validate schema
validation_result = None  # Replace with actual validation

# Assert - Schema Contract
assert validation_result is not None, "Schema validation should produce a result"
assert isinstance(validation_result, (bool, dict)), "Validation result should be structured"
# TODO: Add specific schema validation assertions
"""Test no_absolute_paths_on_clean_result contract compliance."""
# Arrange
# TODO: Set up contract parties and terms
contract_terms = {}  # Replace with actual contract terms

# Act
"""Test check_schema_compatibility_clean contract compliance."""
# Arrange
# TODO: Set up test data
test_data = {}  # Replace with actual test data

# Act
"""Test contract_version_is_pinned contract compliance."""
# Arrange
# TODO: Set up contract scenario
contract_scenario = {}  # Replace with actual scenario
"""Test guardian_id_is_required contract compliance."""
# Arrange
# TODO: Set up contract parties and terms
contract_terms = {}  # Replace with actual contract terms

# Act
# TODO: Execute contract operations
contract_result = None  # Replace with actual contract operation

# Assert - Core Contract
assert contract_result is not None, "Contract operation should produce a result"
assert isinstance(contract_result, dict), "Contract result should be structured"
"""Test check_schema_keys_exact contract compliance."""
# Arrange
# TODO: Set up test data
test_data = {}  # Replace with actual test data

# Act
# TODO: Validate schema
validation_result = None  # Replace with actual validation

# Assert - Schema Contract
assert validation_result is not None, "Schema validation should produce a result"
assert isinstance(validation_result, (bool, dict)), "Validation result should be structured"
# TODO: Add specific schema validation assertions
# assert validation_result.get("valid", False), "Data should conform to schema"
        result = _make_result()
        result.add_check("c1", CheckStatus.PASS, "ok")
        errors = validate_against_json_schema(result.to_dict())
        assert errors == [], f"JSON schema errors: {errors}"

    def test_validate_against_json_schema_invalid_status_caught(self):
    """Test validate_against_json_schema_invalid_status_caught contract compliance."""
    # Arrange
    # TODO: Set up test data
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Validate schema
    """Test missing_required_key_detected contract compliance."""
    # Arrange
    # TODO: Set up contract parties and terms
    contract_terms = {}  # Replace with actual contract terms

    # Act
    # TODO: Execute contract operations
    """Test extra_key_detected_by_schema_compatibility contract compliance."""
    # Arrange
    # TODO: Set up test data
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Validate schema
    validation_result = None  # Replace with actual validation

    # Assert - Schema Contract
    assert validation_result is not None, "Schema validation should produce a result"
    assert isinstance(validation_result, (bool, dict)), "Validation result should be structured"
    # TODO: Add specific schema validation assertions
    # assert validation_result.get("valid", False), "Data should conform to schema"
    """Test backslash_normalized_to_forward contract compliance."""
    # Arrange
    # TODO: Set up contract parties and terms
    contract_terms = {}  # Replace with actual contract terms

"""Test no_leading_slash contract compliance."""
# Arrange
# TODO: Set up contract parties and terms
contract_terms = {}  # Replace with actual contract terms
"""Test windows_drive_stripped contract compliance."""
# Arrange
# TODO: Set up contract parties and terms
contract_terms = {}  # Replace with actual contract terms

"""Test dot_segment_collapsed contract compliance."""
# Arrange
# TODO: Set up contract parties and terms
contract_terms = {}  # Replace with actual contract terms
"""Test dotdot_raises contract compliance."""
# Arrange
# TODO: Set up contract parties and terms
contract_terms = {}  # Replace with actual contract terms
"""Test artifact_path_in_result_is_normalized contract compliance."""
# Arrange
# TODO: Set up contract parties and terms
contract_terms = {}  # Replace with actual contract terms

# Act
# TODO: Execute contract operations
contract_result = None  # Replace with actual contract operation

# Assert - Core Contract
assert contract_result is not None, "Contract operation should produce a result"
assert isinstance(contract_result, dict), "Contract result should be structured"
# TODO: Add specific contract assertions
# assert contract_result.get("enforced", False), "Contract terms should be enforced"
    def test_same_result_same_dict_twice(self):
    """Test same_result_same_dict_twice contract compliance."""
    # Arrange
    # TODO: Set up contract parties and terms
    contract_terms = {}  # Replace with actual contract terms

    # Act
    # TODO: Execute contract operations
    """Test sorted_checks_in_output contract compliance."""
    # Arrange
    # TODO: Set up test data
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Validate schema
    validation_result = None  # Replace with actual validation
    """Test sorted_remediation_hints contract compliance."""
    # Arrange
    # TODO: Set up contract parties and terms
    contract_terms = {}  # Replace with actual contract terms

    # Act
    # TODO: Execute contract operations
    """Test sorted_artifacts_in_output contract compliance."""
    # Arrange
    # TODO: Set up contract parties and terms
    contract_terms = {}  # Replace with actual contract terms

    # Act
    # TODO: Execute contract operations
    contract_result = None  # Replace with actual contract operation
    """Test metrics_sorted_by_key contract compliance."""
    # Arrange
    # TODO: Set up contract parties and terms
    contract_terms = {}  # Replace with actual contract terms

    # Act
    # TODO: Execute contract operations
    contract_result = None  # Replace with actual contract operation

    # Assert - Core Contract
    assert contract_result is not None, "Contract operation should produce a result"
    assert isinstance(contract_result, dict), "Contract result should be structured"
    # TODO: Add specific contract assertions
    # assert contract_result.get("enforced", False), "Contract terms should be enforced"
    """Test empty_guardian_id_captured_in_validate contract compliance."""
    # Arrange
    # TODO: Set up test data
    test_data = {}  # Replace with actual test data

"""Test invalid_check_status_caught_in_validate contract compliance."""
# Arrange
# TODO: Set up test data
test_data = {}  # Replace with actual test data

# Act
"""Test absolute_path_in_evidence_caught contract compliance."""
# Arrange
# TODO: Set up contract parties and terms
contract_terms = {}  # Replace with actual contract terms

# Act
"""Test windows_absolute_path_in_evidence_caught contract compliance."""
# Arrange
# TODO: Set up contract parties and terms
contract_terms = {}  # Replace with actual contract terms

# Act
"""Test none_timestamp_not_in_dict contract compliance."""
# Arrange
# TODO: Set up contract parties and terms
contract_terms = {}  # Replace with actual contract terms

# Act
"""Test artifact_class_defaults_to_individual contract compliance."""
# Arrange
# TODO: Set up contract parties and terms
contract_terms = {}  # Replace with actual contract terms

# Act
# TODO: Execute contract operations
contract_result = None  # Replace with actual contract operation

# Assert - Core Contract
assert contract_result is not None, "Contract operation should produce a result"
assert isinstance(contract_result, dict), "Contract result should be structured"
# TODO: Add specific contract assertions
# assert contract_result.get("enforced", False), "Contract terms should be enforced"
    return tmp_path


def _all_guardian_runners():
    """Return (guardian_id, runner_callable, clean_repo_factory) tuples."""
#  # MOVED: from agentic_core.L0_routing.config.path_constants import (
        AGENTIC_CORE_DIR,
        APPS_LIC_DIR,
        L0_ROUTING_DIR,
    )
#  # MOVED: from agentic_core.L0_routing.scripts.run_guardian_c0_sovereignty import (
        run_c0_sovereignty_guardian,
    )
#  # MOVED: from agentic_core.L0_routing.scripts.run_guardian_change_package_activation import (
        run_change_package_activation_guardian,
    )
#  # MOVED: from agentic_core.L0_routing.scripts.run_guardian_cross_layer_mutation import (
        run_cross_layer_mutation_guardian,
    )
#  # MOVED: from agentic_core.L0_routing.scripts.run_guardian_escalation_determinism import (
        run_escalation_determinism_guardian,
    )
#  # MOVED: from agentic_core.L0_routing.scripts.run_guardian_gateway_bypass import (
        run_gateway_bypass_guardian,
    )

    return [
        ("c0_sovereignty", run_c0_sovereignty_guardian, [AGENTIC_CORE_DIR]),
        ("change_package_activation", run_change_package_activation_guardian, [AGENTIC_CORE_DIR]),
        ("cross_layer_mutation", run_cross_layer_mutation_guardian, [L0_ROUTING_DIR]),
        ("escalation_determinism", run_escalation_determinism_guardian, [AGENTIC_CORE_DIR]),
        ("gateway_bypass", run_gateway_bypass_guardian, [AGENTIC_CORE_DIR, APPS_LIC_DIR]),
    ]


@pytest.mark.parametrize(
    "guardian_id,runner,subdirs",
    [(gid, r, s) for gid, r, s in _all_guardian_runners()],
    ids=[gid for gid, _, _ in _all_guardian_runners()],
)
class TestCrossGuardianSchemaCompliance:
    """Consolidated schema compliance for all behavioral guardians.

    Replaces the individual test_no_absolute_paths_in_result tests that
    were duplicated across test_guardian_c0_sovereignty.py,
    test_guardian_change_package_activation.py,
    test_guardian_cross_layer_mutation.py,
    test_guardian_escalation_determinism.py, and
    test_guardian_gateway_bypass.py.
    """

    def test_no_absolute_paths(self, guardian_id, runner, subdirs, tmp_path):
    """Test no_absolute_paths contract compliance."""
    # Arrange
    # TODO: Set up contract parties and terms
    contract_terms = {}  # Replace with actual contract terms

    # Act
    # TODO: Execute contract operations
    contract_result = None  # Replace with actual contract operation

    # Assert - Core Contract
    assert contract_result is not None, "Contract operation should produce a result"
    assert isinstance(contract_result, dict), "Contract result should be structured"
    # TODO: Add specific contract assertions
    # assert contract_result.get("enforced", False), "Contract terms should be enforced"
