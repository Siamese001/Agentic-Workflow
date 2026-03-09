"""Unit tests for system_learning.constraints — config surface constraints.

Covers:
  - Bounds enforcement
  - Max-delta enforcement
  - Forbidden surfaces rejected
  - Model pointer allowlist enforced
  - Deterministic behavior
"""

import pytest

from system_learning.constraints.delta_enforcer import (
    BoundsViolation,
    DeltaViolation,
    ForbiddenSurface,
    PointerViolation,
    TypeViolation,
    UnknownSurface,
    validate_surface_change,
)

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
        assert True  # no-exception contract

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
        assert True  # no-exception contract

    def test_anomaly_routing_threshold_valid_change(self):
        validate_surface_change("anomaly_routing_threshold", 0.70, 0.73)
        assert True  # no-exception contract

    def test_anomaly_routing_threshold_bounds_enforced(self):
        with pytest.raises(BoundsViolation):
            validate_surface_change("anomaly_routing_threshold", 0.70, 0.90)


# =============================================================================
# L0 Routing Int Constraints
# =============================================================================


class TestL0RoutingIntConstraints:
    def test_depth_breaker_valid_change(self):
        validate_surface_change("depth_breaker", 10, 11)
        assert True  # no-exception contract

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
        assert True  # no-exception contract


# =============================================================================
# RAG Parameters (Int Constraints)
# =============================================================================


class TestRAGParameters:
    def test_retrieval_top_k_valid_change(self):
        validate_surface_change("retrieval_top_k", 10, 12)
        assert True  # no-exception contract

    def test_retrieval_top_k_bounds_enforced(self):
        with pytest.raises(BoundsViolation):
            validate_surface_change("retrieval_top_k", 10, 25)

    def test_retrieval_top_k_delta_enforced(self):
        with pytest.raises(DeltaViolation):
            validate_surface_change("retrieval_top_k", 10, 15)

    def test_rerank_top_n_valid_change(self):
        validate_surface_change("rerank_top_n", 5, 6)
        assert True  # no-exception contract

    def test_rerank_top_n_bounds_enforced(self):
        with pytest.raises(BoundsViolation):
            validate_surface_change("rerank_top_n", 5, 15)


# =============================================================================
# L1 Model Pointers (Pointer Constraints)
# =============================================================================


class TestL1ModelPointers:
    def test_cognition_model_valid_pointer(self):
        validate_surface_change("cognition_model", "gpt-4o", "gpt-4o-mini")
        assert True  # no-exception contract

    def test_cognition_model_allowlist_enforced(self):
        with pytest.raises(PointerViolation, match="POINTER_VIOLATION"):
            validate_surface_change("cognition_model", "gpt-4o", "gpt-3.5-turbo")

    def test_cognition_model_unknown_model_rejected(self):
        with pytest.raises(PointerViolation):
            validate_surface_change("cognition_model", "gpt-4o", "unknown-model")

    def test_embedding_model_valid_pointer(self):
        validate_surface_change("embedding_model", "text-embedding-3-small", "text-embedding-3-large")
        assert True  # no-exception contract

    def test_embedding_model_allowlist_enforced(self):
        with pytest.raises(PointerViolation):
            validate_surface_change("embedding_model", "text-embedding-3-small", "ada-002")


# =============================================================================
# L5 Policy Tunables (Int Constraints)
# =============================================================================


class TestL5PolicyTunables:
    def test_token_budget_valid_change(self):
        validate_surface_change("token_budget", 1_000_000, 1_050_000)
        assert True  # no-exception contract

    def test_token_budget_bounds_enforced(self):
        with pytest.raises(BoundsViolation):
            validate_surface_change("token_budget", 1_000_000, 3_000_000)

    def test_token_budget_delta_enforced(self):
        with pytest.raises(DeltaViolation):
            validate_surface_change("token_budget", 1_000_000, 1_200_000)

    def test_max_k_valid_change(self):
        validate_surface_change("max_k", 10, 11)
        assert True  # no-exception contract

    def test_max_k_bounds_enforced(self):
        with pytest.raises(BoundsViolation):
            validate_surface_change("max_k", 10, 20)

    def test_max_retries_valid_change(self):
        validate_surface_change("max_retries", 3, 4)
        assert True  # no-exception contract

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
        assert True  # no-exception contract
