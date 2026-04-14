"""Runtime-hardened tests for ``reasoning_policy_engine``."""

from __future__ import annotations

from datetime import datetime

import pytest

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def reasoning_engine_symbols():
    engine_module = pytest.importorskip("agentic_core.L0_routing.reasoning.reasoning_policy_engine")
    types_module = pytest.importorskip("agentic_core.L0_routing.types.reasoning_intensity_types")
    return {
        "ReasoningPolicyEngine": engine_module.ReasoningPolicyEngine,
        "RequestStructureFeatures": engine_module.RequestStructureFeatures,
        "compute_complexity_score": engine_module.compute_complexity_score,
        "select_tier": engine_module.select_tier,
        "ReasoningTier": types_module.ReasoningTier,
    }


@pytest.fixture()
def engine(reasoning_engine_symbols):
    return reasoning_engine_symbols["ReasoningPolicyEngine"]({"version": "1.0.0"})


class TestCalibrateFromOutcomes:
    def test_empty_aggregates(self, engine):
        report = engine.calibrate_from_outcomes([])

        assert report["outcome_count"] == 0
        assert report["tier_adjustments"] == {}
        assert report["policy_hash"] == engine.policy_hash
        assert "timestamp" in report
        assert isinstance(datetime.fromisoformat(report["timestamp"]), datetime)

    @pytest.mark.parametrize(
        ("aggregate", "key", "action", "reason_fragment"),
        [
            (
                {
                    "complexity_tier": "complex",
                    "path_id": "tot",
                    "avg_latency_ms": 1000.0,
                    "error_rate": 0.15,
                    "p95_latency_ms": 1500.0,
                },
                "complex:tot",
                "increase_depth",
                "15.00%",
            ),
            (
                {
                    "complexity_tier": "simple",
                    "path_id": "cot",
                    "avg_latency_ms": 250.0,
                    "error_rate": 0.02,
                    "p95_latency_ms": 400.0,
                },
                "simple:cot",
                "maintain_or_reduce",
                "250",
            ),
            (
                {
                    "complexity_tier": "moderate",
                    "path_id": "reflexion",
                    "avg_latency_ms": 750.0,
                    "error_rate": 0.07,
                    "p95_latency_ms": 1000.0,
                },
                "moderate:reflexion",
                "maintain",
                "acceptable bounds",
            ),
        ],
    )
    def test_adjustment_suggestions(self, engine, aggregate, key, action, reason_fragment):
        report = engine.calibrate_from_outcomes([aggregate])
        adjustment = report["tier_adjustments"][key]

        assert adjustment["suggested_action"] == action
        assert reason_fragment in adjustment["reason"]

    def test_multiple_tier_adjustments(self, engine):
        report = engine.calibrate_from_outcomes(
            [
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
        )

        assert set(report["tier_adjustments"]) == {"simple:cot", "complex:tot"}
        assert report["tier_adjustments"]["simple:cot"]["suggested_action"] == "maintain_or_reduce"
        assert report["tier_adjustments"]["complex:tot"]["suggested_action"] == "increase_depth"

    def test_exact_threshold_boundary(self, engine):
        report = engine.calibrate_from_outcomes(
            [
                {
                    "complexity_tier": "moderate",
                    "path_id": "cot",
                    "avg_latency_ms": 500.0,
                    "error_rate": 0.05,
                    "p95_latency_ms": 750.0,
                },
            ]
        )

        assert report["tier_adjustments"]["moderate:cot"]["suggested_action"] == "maintain"

    def test_adg_stats_included(self, engine):
        adg_stats = {"node_count": 1000, "edge_count": 5000}

        report = engine.calibrate_from_outcomes([], current_adg_stats=adg_stats)

        assert report["adg_integration"] == adg_stats

    def test_missing_optional_fields_use_defaults(self, engine):
        report = engine.calibrate_from_outcomes([{"path_id": "unknown_path"}])
        adjustment = report["tier_adjustments"]["moderate:unknown_path"]

        assert adjustment["latency_ms"] == 0
        assert adjustment["error_rate"] == 0
        assert adjustment["suggested_action"] == "maintain_or_reduce"


class TestRequestStructureFeatures:
    def test_valid_features(self, reasoning_engine_symbols):
        features = reasoning_engine_symbols["RequestStructureFeatures"](
            input_length=1000,
            tool_count_requested=5,
            risk_tier_candidate=3,
            stage_count=5,
            l4_budget_remaining_tokens=5000,
            l4_rate_limit_headroom=0.8,
            aggregated_prior_success_rate=0.9,
        )

        assert features.input_length == 1000

    @pytest.mark.parametrize(
        ("kwargs", "match"),
        [
            (
                {
                    "input_length": -1,
                    "tool_count_requested": 5,
                    "risk_tier_candidate": 3,
                    "stage_count": 5,
                    "l4_budget_remaining_tokens": 5000,
                    "l4_rate_limit_headroom": 0.8,
                    "aggregated_prior_success_rate": 0.9,
                },
                "input_length must be >= 0",
            ),
            (
                {
                    "input_length": 1000,
                    "tool_count_requested": 5,
                    "risk_tier_candidate": 6,
                    "stage_count": 5,
                    "l4_budget_remaining_tokens": 5000,
                    "l4_rate_limit_headroom": 0.8,
                    "aggregated_prior_success_rate": 0.9,
                },
                "risk_tier_candidate must be 0-5",
            ),
            (
                {
                    "input_length": 1000,
                    "tool_count_requested": 5,
                    "risk_tier_candidate": 3,
                    "stage_count": 0,
                    "l4_budget_remaining_tokens": 5000,
                    "l4_rate_limit_headroom": 0.8,
                    "aggregated_prior_success_rate": 0.9,
                },
                "stage_count must be >= 1",
            ),
            (
                {
                    "input_length": 1000,
                    "tool_count_requested": 5,
                    "risk_tier_candidate": 3,
                    "stage_count": 5,
                    "l4_budget_remaining_tokens": 5000,
                    "l4_rate_limit_headroom": 1.5,
                    "aggregated_prior_success_rate": 0.9,
                },
                "l4_rate_limit_headroom must be in",
            ),
        ],
    )
    def test_invalid_features_raise(self, reasoning_engine_symbols, kwargs, match):
        with pytest.raises(ValueError, match=match):
            reasoning_engine_symbols["RequestStructureFeatures"](**kwargs)


class TestComputeComplexityScore:
    def test_minimal_features(self, reasoning_engine_symbols):
        features = reasoning_engine_symbols["RequestStructureFeatures"](
            input_length=0,
            tool_count_requested=0,
            risk_tier_candidate=0,
            stage_count=1,
            l4_budget_remaining_tokens=0,
            l4_rate_limit_headroom=1.0,
            aggregated_prior_success_rate=1.0,
        )
        score = reasoning_engine_symbols["compute_complexity_score"](features)

        assert 0.0 <= score <= 1.0
        assert score == 0.0

    def test_maximal_features_produce_high_score(self, reasoning_engine_symbols):
        features = reasoning_engine_symbols["RequestStructureFeatures"](
            input_length=10000,
            tool_count_requested=15,
            risk_tier_candidate=5,
            stage_count=10,
            l4_budget_remaining_tokens=0,
            l4_rate_limit_headroom=0.0,
            aggregated_prior_success_rate=0.0,
        )
        score = reasoning_engine_symbols["compute_complexity_score"](features)

        assert 0.0 <= score <= 1.0
        assert score > 0.8

    def test_score_bounds(self, reasoning_engine_symbols):
        features = reasoning_engine_symbols["RequestStructureFeatures"](
            input_length=100000,
            tool_count_requested=100,
            risk_tier_candidate=5,
            stage_count=100,
            l4_budget_remaining_tokens=0,
            l4_rate_limit_headroom=0.0,
            aggregated_prior_success_rate=0.0,
        )
        score = reasoning_engine_symbols["compute_complexity_score"](features)

        assert score == 1.0


class TestSelectTier:
    @pytest.mark.parametrize(
        ("score", "expected_attr"),
        [
            (0.75, "CRITICAL"),
            (0.9, "CRITICAL"),
            (0.50, "HIGH"),
            (0.74, "HIGH"),
            (0.25, "MEDIUM"),
            (0.49, "MEDIUM"),
            (0.24, "LOW"),
            (0.0, "LOW"),
            (0.249999, "LOW"),
        ],
    )
    def test_select_tier(self, reasoning_engine_symbols, score, expected_attr):
        reasoning_tier = reasoning_engine_symbols["ReasoningTier"]
        result = reasoning_engine_symbols["select_tier"](score)

        assert result == getattr(reasoning_tier, expected_attr)
