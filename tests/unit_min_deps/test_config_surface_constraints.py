"""Unit tests for system_learning.constraints — config surface constraints.

Covers:
  - Bounds enforcement
  - Max-delta enforcement
  - Forbidden surfaces rejected
  - Model pointer allowlist enforced
  - Deterministic behavior
"""

import pytest

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

_emit_authorize_and_execute("p2", "test_config_surface_constraints", "execution_auth")
_emit_validates_capability("p2", "test_config_surface_constraints", "capability_check")
_emit_routes_to_capability("p2", "test_config_surface_constraints", "capability_route")
_emit_writes_via_uwg("p2", "test_config_surface_constraints", "uwg_write")
_emit_blocks_direct_write("p2", "test_config_surface_constraints", "direct_write_block")
_emit_records_tool_invocation("p2", "test_config_surface_constraints", "tool_invocation")
_emit_captures_execution_output("p2", "test_config_surface_constraints", "exec_output")
_emit_dispatches_agent("p3", "test_config_surface_constraints", "agent_dispatch")
_emit_coordinates_agents("p3", "test_config_surface_constraints", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_config_surface_constraints", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_config_surface_constraints", "healing_outcome")
_emit_escalates_failure("p3", "test_config_surface_constraints", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_config_surface_constraints", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_config_surface_constraints", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_config_surface_constraints", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_config_surface_constraints", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_config_surface_constraints", "eval_metric")
_emit_stores_embedding("p4", "test_config_surface_constraints", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_config_surface_constraints", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_config_surface_constraints", "exec_snapshot_link")
from system_learning.constraints.delta_enforcer import (
    BoundsViolation,
    DeltaViolation,
    ForbiddenSurface,
    PointerViolation,
    TypeViolation,
    UnknownSurface,
    validate_surface_change,
)

_emit_records_execution_trace("p0", "evidence", "test_config_surface_constraints")
_emit_applies_guardrail("p0", "test_config_surface_constraints", "p0_governance")
_emit_reads_policy_state("p0", "test_config_surface_constraints", "policy_binding")
_emit_snapshots_state("p0", "test_config_surface_constraints", "state_snapshot")
emit_replay_key("p0", "test_config_surface_constraints")
emit_determinism_digest("p0", "test_config_surface_constraints")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit_min_deps


# =============================================================================
# Forbidden Surfaces
# =============================================================================


class TestForbiddenSurfaces:
    def test_tool_allowlist_forbidden(self):
        with pytest.raises(ForbiddenSurface, match="FORBIDDEN_SURFACE"):
            validate_surface_change("tool_allowlist", ["read"], ["read", "write"])

    def test_file_scope_whitelist_forbidden(self):
        with pytest.raises(ForbiddenSurface, match="FORBIDDEN_SURFACE"):
            validate_surface_change("file_scope_whitelist", ["/tmp"], ["/tmp", "/"])

    def test_guardian_contracts_forbidden(self):
        with pytest.raises(ForbiddenSurface, match="FORBIDDEN_SURFACE"):
            validate_surface_change("guardian_contracts", "v1", "v2")

    def test_sandbox_escape_forbidden(self):
        with pytest.raises(ForbiddenSurface, match="FORBIDDEN_SURFACE"):
            validate_surface_change("sandbox_escape", False, True)


# =============================================================================
# Unknown Surfaces
# =============================================================================


class TestUnknownSurfaces:
    def test_unknown_surface_rejected(self):
        with pytest.raises(UnknownSurface, match="UNKNOWN_SURFACE"):
            validate_surface_change("unknown_param", 0.5, 0.6)

    def test_arbitrary_surface_rejected(self):
        with pytest.raises(UnknownSurface, match="UNKNOWN_SURFACE"):
            validate_surface_change("arbitrary_config", 100, 200)


# =============================================================================
# L0 Routing Thresholds (Float Constraints)
# =============================================================================


class TestL0RoutingThresholds:
    def test_escalation_threshold_valid_change(self):
        # Within bounds and delta
        validate_surface_change("escalation_threshold", 0.80, 0.82)

    def test_escalation_threshold_below_min_raises(self):
        with pytest.raises(BoundsViolation, match="BOUNDS_VIOLATION"):
            validate_surface_change("escalation_threshold", 0.75, 0.65)

    def test_escalation_threshold_above_max_raises(self):
        with pytest.raises(BoundsViolation, match="BOUNDS_VIOLATION"):
            validate_surface_change("escalation_threshold", 0.90, 0.98)

    def test_escalation_threshold_delta_too_large_raises(self):
        with pytest.raises(DeltaViolation, match="DELTA_VIOLATION"):
            validate_surface_change("escalation_threshold", 0.70, 0.80)

    def test_escalation_threshold_max_delta_allowed(self):
        # Exactly at max delta (0.05)
        validate_surface_change("escalation_threshold", 0.80, 0.85)

    def test_anomaly_routing_threshold_valid_change(self):
        validate_surface_change("anomaly_routing_threshold", 0.70, 0.73)

    def test_anomaly_routing_threshold_bounds_enforced(self):
        with pytest.raises(BoundsViolation):
            validate_surface_change("anomaly_routing_threshold", 0.70, 0.90)


# =============================================================================
# L0 Routing Int Constraints
# =============================================================================


class TestL0RoutingIntConstraints:
    def test_depth_breaker_valid_change(self):
        validate_surface_change("depth_breaker", 10, 11)

    def test_depth_breaker_below_min_raises(self):
        with pytest.raises(BoundsViolation, match="BOUNDS_VIOLATION"):
            validate_surface_change("depth_breaker", 10, 3)

    def test_depth_breaker_above_max_raises(self):
        with pytest.raises(BoundsViolation, match="BOUNDS_VIOLATION"):
            validate_surface_change("depth_breaker", 10, 25)

    def test_depth_breaker_delta_too_large_raises(self):
        with pytest.raises(DeltaViolation, match="DELTA_VIOLATION"):
            validate_surface_change("depth_breaker", 10, 15)

    def test_depth_breaker_max_delta_allowed(self):
        # Exactly at max delta (2)
        validate_surface_change("depth_breaker", 10, 12)


# =============================================================================
# RAG Parameters (Int Constraints)
# =============================================================================


class TestRAGParameters:
    def test_retrieval_top_k_valid_change(self):
        validate_surface_change("retrieval_top_k", 10, 12)

    def test_retrieval_top_k_bounds_enforced(self):
        with pytest.raises(BoundsViolation):
            validate_surface_change("retrieval_top_k", 10, 25)

    def test_retrieval_top_k_delta_enforced(self):
        with pytest.raises(DeltaViolation):
            validate_surface_change("retrieval_top_k", 10, 15)

    def test_rerank_top_n_valid_change(self):
        validate_surface_change("rerank_top_n", 5, 6)

    def test_rerank_top_n_bounds_enforced(self):
        with pytest.raises(BoundsViolation):
            validate_surface_change("rerank_top_n", 5, 15)


# =============================================================================
# L1 Model Pointers (Pointer Constraints)
# =============================================================================


class TestL1ModelPointers:
    def test_cognition_model_valid_pointer(self):
        validate_surface_change("cognition_model", "gpt-4o", "gpt-4o-mini")

    def test_cognition_model_allowlist_enforced(self):
        with pytest.raises(PointerViolation, match="POINTER_VIOLATION"):
            validate_surface_change("cognition_model", "gpt-4o", "gpt-3.5-turbo")

    def test_cognition_model_unknown_model_rejected(self):
        with pytest.raises(PointerViolation):
            validate_surface_change("cognition_model", "gpt-4o", "unknown-model")

    def test_embedding_model_valid_pointer(self):
        validate_surface_change("embedding_model", "text-embedding-3-small", "text-embedding-3-large")

    def test_embedding_model_allowlist_enforced(self):
        with pytest.raises(PointerViolation):
            validate_surface_change("embedding_model", "text-embedding-3-small", "ada-002")


# =============================================================================
# L5 Policy Tunables (Int Constraints)
# =============================================================================


class TestL5PolicyTunables:
    def test_token_budget_valid_change(self):
        validate_surface_change("token_budget", 1_000_000, 1_050_000)

    def test_token_budget_bounds_enforced(self):
        with pytest.raises(BoundsViolation):
            validate_surface_change("token_budget", 1_000_000, 3_000_000)

    def test_token_budget_delta_enforced(self):
        with pytest.raises(DeltaViolation):
            validate_surface_change("token_budget", 1_000_000, 1_200_000)

    def test_max_k_valid_change(self):
        validate_surface_change("max_k", 10, 11)

    def test_max_k_bounds_enforced(self):
        with pytest.raises(BoundsViolation):
            validate_surface_change("max_k", 10, 20)

    def test_max_retries_valid_change(self):
        validate_surface_change("max_retries", 3, 4)

    def test_max_retries_delta_enforced(self):
        with pytest.raises(DeltaViolation):
            validate_surface_change("max_retries", 2, 5)


# =============================================================================
# Type Validation
# =============================================================================


class TestTypeValidation:
    def test_float_constraint_rejects_string(self):
        with pytest.raises(TypeViolation, match="TYPE_VIOLATION"):
            validate_surface_change("escalation_threshold", 0.80, "0.85")

    def test_int_constraint_rejects_float(self):
        with pytest.raises(TypeViolation, match="TYPE_VIOLATION"):
            validate_surface_change("depth_breaker", 10, 11.5)

    def test_pointer_constraint_rejects_int(self):
        with pytest.raises(TypeViolation, match="TYPE_VIOLATION"):
            validate_surface_change("cognition_model", "gpt-4o", 123)


# =============================================================================
# Determinism
# =============================================================================


class TestDeterminism:
    def test_validation_deterministic(self):
        """Same inputs produce same validation result (pass or fail)."""
        # Valid change - should pass both times
        validate_surface_change("escalation_threshold", 0.80, 0.82)
        validate_surface_change("escalation_threshold", 0.80, 0.82)

        # Invalid change - should fail both times with same exception type
        with pytest.raises(BoundsViolation):
            validate_surface_change("escalation_threshold", 0.80, 0.99)
        with pytest.raises(BoundsViolation):
            validate_surface_change("escalation_threshold", 0.80, 0.99)

    def test_validation_order_independent(self):
        """Validation result does not depend on call order."""
        # Call in different orders
        validate_surface_change("depth_breaker", 10, 11)
        validate_surface_change("retrieval_top_k", 10, 12)

        validate_surface_change("retrieval_top_k", 10, 12)
        validate_surface_change("depth_breaker", 10, 11)
