"""Tests for reasoning_policy_engine — L0 calibration feedback.

G2 Fix: Provides test coverage for calibrate_from_outcomes method
which was previously untested.
"""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.reasoning.reasoning_policy_engine import (
    ReasoningPolicyEngine,
    RequestStructureFeatures,
    compute_complexity_score,
    select_tier,
)
from agentic_core.L0_routing.types.reasoning_intensity_types import ReasoningTier


class TestCalibrateFromOutcomes:
    """Test calibrate_from_outcomes method for L6→L0 feedback loop."""

    def test_empty_aggregates(self):
        """Edge case: empty aggregates returns empty report."""
        engine = ReasoningPolicyEngine({"version": "1.0.0"})
        report = engine.calibrate_from_outcomes([])

        assert report["outcome_count"] == 0
        assert report["tier_adjustments"] == {}
        assert report["policy_hash"] == engine.policy_hash
        assert "timestamp" in report

    def test_high_error_rate_suggests_increase_depth(self):
        """Happy path: high error rate suggests increase_depth action."""
        engine = ReasoningPolicyEngine({"version": "1.0.0"})

        aggregates = [
            {
                "complexity_tier": "complex",
                "path_id": "tot",
                "avg_latency_ms": 1000.0,
                "error_rate": 0.15,  # 15% error rate > 10% threshold
                "p95_latency_ms": 1500.0,
            },
        ]

        report = engine.calibrate_from_outcomes(aggregates)

        adjustment = report["tier_adjustments"]["complex:tot"]
        assert adjustment["suggested_action"] == "increase_depth"
        assert "15.00%" in adjustment["reason"]
        assert adjustment["error_rate"] == 0.15

    def test_low_latency_low_error_suggests_maintain_or_reduce(self):
        """Happy path: low latency and low error suggests maintain_or_reduce."""
        engine = ReasoningPolicyEngine({"version": "1.0.0"})

        aggregates = [
            {
                "complexity_tier": "simple",
                "path_id": "cot",
                "avg_latency_ms": 250.0,  # < 500ms
                "error_rate": 0.02,  # < 5%
                "p95_latency_ms": 400.0,
            },
        ]

        report = engine.calibrate_from_outcomes(aggregates)

        adjustment = report["tier_adjustments"]["simple:cot"]
        assert adjustment["suggested_action"] == "maintain_or_reduce"
        assert "250ms" in adjustment["reason"]
        assert adjustment["error_rate"] == 0.02

    def test_mid_range_suggests_maintain(self):
        """Edge case: mid-range performance suggests maintain."""
        engine = ReasoningPolicyEngine({"version": "1.0.0"})

        aggregates = [
            {
                "complexity_tier": "moderate",
                "path_id": "reflexion",
                "avg_latency_ms": 750.0,  # Between 500-1000ms
                "error_rate": 0.07,  # Between 5-10%
                "p95_latency_ms": 1000.0,
            },
        ]

        report = engine.calibrate_from_outcomes(aggregates)

        adjustment = report["tier_adjustments"]["moderate:reflexion"]
        assert adjustment["suggested_action"] == "maintain"
        assert "within acceptable bounds" in adjustment["reason"]

    def test_multiple_tier_adjustments(self):
        """Happy path: multiple tiers produce multiple adjustments."""
        engine = ReasoningPolicyEngine({"version": "1.0.0"})

        aggregates = [
            {
                "complexity_tier": "simple",
                "path_id": "cot",
                "avg_latency_ms": 250.0,
                "error_rate": 0.02,
                "p95_latency_ms": 400.0,
            },
            {
                "complexity_tier": "complex",
                "path_id": "tot",
                "avg_latency_ms": 2000.0,
                "error_rate": 0.20,
                "p95_latency_ms": 3000.0,
            },
        ]

        report = engine.calibrate_from_outcomes(aggregates)

        assert len(report["tier_adjustments"]) == 2
        assert "simple:cot" in report["tier_adjustments"]
        assert "complex:tot" in report["tier_adjustments"]
        assert report["tier_adjustments"]["simple:cot"]["suggested_action"] == "maintain_or_reduce"
        assert report["tier_adjustments"]["complex:tot"]["suggested_action"] == "increase_depth"

    def test_exact_threshold_boundary(self):
        """Edge case: exactly at threshold boundaries."""
        engine = ReasoningPolicyEngine({"version": "1.0.0"})

        aggregates = [
            {
                "complexity_tier": "moderate",
                "path_id": "cot",
                "avg_latency_ms": 500.0,  # Exactly at threshold
                "error_rate": 0.05,  # Exactly at threshold
                "p95_latency_ms": 750.0,
            },
        ]

        report = engine.calibrate_from_outcomes(aggregates)

        # Exactly at threshold should be maintain (not maintain_or_reduce)
        adjustment = report["tier_adjustments"]["moderate:cot"]
        # 500ms is NOT < 500, and 0.05 is NOT < 0.05 (strict comparison)
        assert adjustment["suggested_action"] == "maintain"

    def test_adg_stats_included(self):
        """Happy path: ADG stats included in report when provided."""
        engine = ReasoningPolicyEngine({"version": "1.0.0"})

        adg_stats = {"node_count": 1000, "edge_count": 5000}
        report = engine.calibrate_from_outcomes([], current_adg_stats=adg_stats)

        assert report["adg_integration"] == adg_stats

    def test_missing_optional_fields_use_defaults(self):
        """Edge case: missing optional fields use defaults."""
        engine = ReasoningPolicyEngine({"version": "1.0.0"})

        # Aggregate with minimal fields
        aggregates = [
            {
                "path_id": "unknown_path",
            },
        ]

        report = engine.calibrate_from_outcomes(aggregates)

        adjustment = report["tier_adjustments"]["moderate:unknown_path"]
        assert adjustment["latency_ms"] == 0  # Default for missing
        assert adjustment["error_rate"] == 0  # Default for missing
        # With 0 error rate, should suggest maintain_or_reduce (0 < 0.05)
        assert adjustment["suggested_action"] == "maintain_or_reduce"


class TestRequestStructureFeatures:
    """Test RequestStructureFeatures validation."""

    def test_valid_features(self):
        """Happy path: valid features create successfully."""
        features = RequestStructureFeatures(
            input_length=1000,
            tool_count_requested=5,
            risk_tier_candidate=3,
            stage_count=5,
            l4_budget_remaining_tokens=5000,
            l4_rate_limit_headroom=0.8,
            aggregated_prior_success_rate=0.9,
        )
        assert features.input_length == 1000

    def test_negative_input_length_raises(self):
        """Failure path: negative input_length raises ValueError."""
        with pytest.raises(ValueError, match="input_length must be >= 0"):
            RequestStructureFeatures(
                input_length=-1,
                tool_count_requested=5,
                risk_tier_candidate=3,
                stage_count=5,
                l4_budget_remaining_tokens=5000,
                l4_rate_limit_headroom=0.8,
                aggregated_prior_success_rate=0.9,
            )

    def test_risk_tier_out_of_range_raises(self):
        """Failure path: risk_tier > 5 raises ValueError."""
        with pytest.raises(ValueError, match="risk_tier_candidate must be 0-5"):
            RequestStructureFeatures(
                input_length=1000,
                tool_count_requested=5,
                risk_tier_candidate=6,
                stage_count=5,
                l4_budget_remaining_tokens=5000,
                l4_rate_limit_headroom=0.8,
                aggregated_prior_success_rate=0.9,
            )

    def test_stage_count_less_than_1_raises(self):
        """Failure path: stage_count < 1 raises ValueError."""
        with pytest.raises(ValueError, match="stage_count must be >= 1"):
            RequestStructureFeatures(
                input_length=1000,
                tool_count_requested=5,
                risk_tier_candidate=3,
                stage_count=0,
                l4_budget_remaining_tokens=5000,
                l4_rate_limit_headroom=0.8,
                aggregated_prior_success_rate=0.9,
            )

    def test_rate_limit_headroom_out_of_range_raises(self):
        """Failure path: rate_limit_headroom > 1.0 raises ValueError."""
        with pytest.raises(ValueError, match="l4_rate_limit_headroom must be in"):
            RequestStructureFeatures(
                input_length=1000,
                tool_count_requested=5,
                risk_tier_candidate=3,
                stage_count=5,
                l4_budget_remaining_tokens=5000,
                l4_rate_limit_headroom=1.5,
                aggregated_prior_success_rate=0.9,
            )


class TestComputeComplexityScore:
    """Test complexity score computation."""

    def test_minimal_features(self):
        """Happy path: minimal features produce valid score."""
        features = RequestStructureFeatures(
            input_length=0,
            tool_count_requested=0,
            risk_tier_candidate=0,
            stage_count=1,
            l4_budget_remaining_tokens=0,
            l4_rate_limit_headroom=1.0,
            aggregated_prior_success_rate=1.0,
        )
        score = compute_complexity_score(features)
        assert 0.0 <= score <= 1.0
        assert score == 0.0  # All minimum values

    def test_maximal_features(self):
        """Happy path: maximal features produce valid score."""
        features = RequestStructureFeatures(
            input_length=10000,  # > 8192 saturation
            tool_count_requested=15,  # > 10 saturation
            risk_tier_candidate=5,
            stage_count=10,
            l4_budget_remaining_tokens=0,
            l4_rate_limit_headroom=0.0,
            aggregated_prior_success_rate=0.0,
        )
        score = compute_complexity_score(features)
        assert 0.0 <= score <= 1.0
        assert score > 0.8  # High complexity

    def test_score_bounds(self):
        """Edge case: score is always bounded [0, 1]."""
        features = RequestStructureFeatures(
            input_length=100000,  # Extreme
            tool_count_requested=100,  # Extreme
            risk_tier_candidate=5,
            stage_count=100,
            l4_budget_remaining_tokens=0,
            l4_rate_limit_headroom=0.0,
            aggregated_prior_success_rate=0.0,
        )
        score = compute_complexity_score(features)
        assert score == 1.0  # Capped at 1.0


class TestSelectTier:
    """Test tier selection based on complexity score."""

    def test_select_critical_tier(self):
        """Happy path: score >= 0.75 selects CRITICAL."""
        assert select_tier(0.75) == ReasoningTier.CRITICAL
        assert select_tier(0.9) == ReasoningTier.CRITICAL

    def test_select_high_tier(self):
        """Happy path: score >= 0.50 selects HIGH."""
        assert select_tier(0.50) == ReasoningTier.HIGH
        assert select_tier(0.74) == ReasoningTier.HIGH

    def test_select_medium_tier(self):
        """Happy path: score >= 0.25 selects MEDIUM."""
        assert select_tier(0.25) == ReasoningTier.MEDIUM
        assert select_tier(0.49) == ReasoningTier.MEDIUM

    def test_select_low_tier(self):
        """Happy path: score < 0.25 selects LOW."""
        assert select_tier(0.24) == ReasoningTier.LOW
        assert select_tier(0.0) == ReasoningTier.LOW

    def test_select_tier_boundary_exact(self):
        """Edge case: exact boundary values."""
        assert select_tier(0.75) == ReasoningTier.CRITICAL  # Boundary
        assert select_tier(0.50) == ReasoningTier.HIGH  # Boundary
        assert select_tier(0.25) == ReasoningTier.MEDIUM  # Boundary
        assert select_tier(0.249999) == ReasoningTier.LOW  # Just under boundary
