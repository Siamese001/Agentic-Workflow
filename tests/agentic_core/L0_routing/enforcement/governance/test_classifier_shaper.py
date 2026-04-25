"""Tests for classifier_shaper.py module."""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.enforcement.governance.classifier_shaper import (
    RouteCategory,
    RiskTier,
    ShapedBundle,
    ClassifierShaper,
)


class TestRouteCategory:
    """Tests for RouteCategory enum."""

    def test_route_category_values(self):
        """Test RouteCategory has expected values."""
        assert RouteCategory.CACHE_HIT is not None
        assert RouteCategory.RAG_GROUNDED is not None
        assert RouteCategory.TOOL_CALL is not None
        assert RouteCategory.MODEL_GENERATION is not None
        assert RouteCategory.HITL_REQUIRED is not None
        assert RouteCategory.FALLBACK_SAFE is not None

    def test_route_category_count(self):
        """Test RouteCategory has 6 values."""
        assert len(RouteCategory) == 6


class TestRiskTier:
    """Tests for RiskTier enum."""

    def test_risk_tier_values(self):
        """Test RiskTier has expected values."""
        assert RiskTier.LOW is not None
        assert RiskTier.MEDIUM is not None
        assert RiskTier.HIGH is not None
        assert RiskTier.CRITICAL is not None

    def test_risk_tier_count(self):
        """Test RiskTier has 4 values."""
        assert len(RiskTier) == 4


class TestShapedBundle:
    """Tests for ShapedBundle dataclass."""

    def test_shaped_bundle_creation(self):
        """Test ShapedBundle creation with all fields."""
        bundle = ShapedBundle(
            category=RouteCategory.CACHE_HIT,
            risk_tier=RiskTier.LOW,
            route_target="L0_cache",
            requires_governance=False,
            shaped_payload={"key": "value"},
            metadata={"meta": "data"},
        )
        assert bundle.category == RouteCategory.CACHE_HIT
        assert bundle.risk_tier == RiskTier.LOW
        assert bundle.route_target == "L0_cache"
        assert bundle.requires_governance is False
        assert bundle.shaped_payload == {"key": "value"}
        assert bundle.metadata == {"meta": "data"}

    def test_shaped_bundle_defaults(self):
        """Test ShapedBundle with default values."""
        bundle = ShapedBundle(
            category=RouteCategory.CACHE_HIT,
            risk_tier=RiskTier.LOW,
            route_target="L0_cache",
            requires_governance=False,
        )
        assert bundle.shaped_payload == {}
        assert bundle.metadata == {}


class TestClassifierShaper:
    """Tests for ClassifierShaper class."""

    def test_classifier_shaper_init(self):
        """Test ClassifierShaper initialization."""
        shaper = ClassifierShaper()
        assert shaper._category_rules == []
        assert shaper._risk_thresholds == {
            RiskTier.LOW: 0.3,
            RiskTier.MEDIUM: 0.5,
            RiskTier.HIGH: 0.7,
            RiskTier.CRITICAL: 0.9,
        }

    def test_classify_and_shape_cache_hit(self):
        """Test classify_and_shape with cache hit request."""
        shaper = ClassifierShaper()
        request = {"operation": "cache_lookup", "cache_hit": True}
        
        bundle = shaper.classify_and_shape(request, risk_score=0.1)
        
        assert bundle.category == RouteCategory.CACHE_HIT
        assert bundle.risk_tier == RiskTier.LOW
        assert bundle.route_target == "L0_cache"
        assert bundle.requires_governance is False

    def test_classify_and_shape_rag_grounded(self):
        """Test classify_and_shape with RAG grounded request."""
        shaper = ClassifierShaper()
        request = {"operation": "rag_retrieve"}
        
        bundle = shaper.classify_and_shape(request, risk_score=0.4)
        
        assert bundle.category == RouteCategory.RAG_GROUNDED
        assert bundle.route_target == "C0_retrieval"

    def test_classify_and_shape_tool_call(self):
        """Test classify_and_shape with tool call request."""
        shaper = ClassifierShaper()
        request = {"operation": "tool_execute"}
        
        bundle = shaper.classify_and_shape(request, risk_score=0.3)
        
        assert bundle.category == RouteCategory.TOOL_CALL
        assert bundle.route_target == "L2_execution"

    def test_classify_and_shape_model_generation(self):
        """Test classify_and_shape with model generation request."""
        shaper = ClassifierShaper()
        request = {"operation": "llm_generate"}
        
        bundle = shaper.classify_and_shape(request, risk_score=0.5)
        
        assert bundle.category == RouteCategory.MODEL_GENERATION
        assert bundle.route_target == "L2_model_invoke"

    def test_classify_and_shape_hitl_required(self):
        """Test classify_and_shape with HITL required request."""
        shaper = ClassifierShaper()
        request = {"operation": "hitl_decision", "confidence": 0.3}
        
        bundle = shaper.classify_and_shape(request, risk_score=0.4)
        
        assert bundle.category == RouteCategory.HITL_REQUIRED
        assert bundle.route_target == "L5_HITL"
        assert bundle.requires_governance is True

    def test_classify_and_shape_fallback_safe(self):
        """Test classify_and_shape with fallback safe request."""
        shaper = ClassifierShaper()
        request = {"operation": "unknown_operation"}
        
        bundle = shaper.classify_and_shape(request, risk_score=0.2)
        
        assert bundle.category == RouteCategory.FALLBACK_SAFE
        assert bundle.route_target == "L0_fallback"

    def test_classify_and_shape_high_risk(self):
        """Test classify_and_shape with high risk score."""
        shaper = ClassifierShaper()
        request = {"operation": "tool_execute"}
        
        bundle = shaper.classify_and_shape(request, risk_score=0.8)
        
        assert bundle.risk_tier == RiskTier.HIGH
        assert bundle.requires_governance is True

    def test_classify_and_shape_critical_risk(self):
        """Test classify_and_shape with critical risk score."""
        shaper = ClassifierShaper()
        request = {"operation": "tool_execute"}
        
        bundle = shaper.classify_and_shape(request, risk_score=0.95)
        
        assert bundle.risk_tier == RiskTier.CRITICAL
        assert bundle.requires_governance is True

    def test_classify_and_shape_shaped_payload(self):
        """Test classify_and_shape shapes payload correctly."""
        shaper = ClassifierShaper()
        request = {"operation": "cache_lookup", "cache_hit": True, "key": "value"}
        
        bundle = shaper.classify_and_shape(request, risk_score=0.1)
        
        assert "governance_category" in bundle.shaped_payload
        assert "shaped_at" in bundle.shaped_payload
        assert bundle.shaped_payload["key"] == "value"
        assert bundle.shaped_payload["governance_category"] == "CACHE_HIT"

    def test_classify_and_shape_metadata(self):
        """Test classify_and_shape includes metadata."""
        shaper = ClassifierShaper()
        request = {"operation": "cache_lookup", "cache_hit": True}
        
        bundle = shaper.classify_and_shape(request, risk_score=0.42)
        
        assert bundle.metadata["original_operation"] == "cache_lookup"
        assert bundle.metadata["risk_score"] == 0.42

    def test_classify_cache_hit_indicator(self):
        """Test _classify detects cache hit."""
        shaper = ClassifierShaper()
        
        # With cache_hit flag
        request1 = {"cache_hit": True}
        assert shaper._classify(request1) == RouteCategory.CACHE_HIT
        
        # With cache in operation
        request2 = {"operation": "cache_refresh"}
        assert shaper._classify(request2) == RouteCategory.CACHE_HIT

    def test_classify_rag_indicators(self):
        """Test _classify detects RAG indicators."""
        shaper = ClassifierShaper()
        
        assert shaper._classify({"operation": "rag_query"}) == RouteCategory.RAG_GROUNDED
        assert shaper._classify({"operation": "retrieve_docs"}) == RouteCategory.RAG_GROUNDED
        assert shaper._classify({"operation": "evidence_search"}) == RouteCategory.RAG_GROUNDED
        assert shaper._classify({"operation": "search_index"}) == RouteCategory.RAG_GROUNDED

    def test_classify_tool_indicators(self):
        """Test _classify detects tool indicators."""
        shaper = ClassifierShaper()
        
        assert shaper._classify({"operation": "tool_run"}) == RouteCategory.TOOL_CALL
        assert shaper._classify({"operation": "execute_command"}) == RouteCategory.TOOL_CALL
        assert shaper._classify({"operation": "invoke_function"}) == RouteCategory.TOOL_CALL

    def test_classify_model_indicators(self):
        """Test _classify detects model indicators."""
        shaper = ClassifierShaper()
        
        assert shaper._classify({"operation": "model_inference"}) == RouteCategory.MODEL_GENERATION
        assert shaper._classify({"operation": "llm_call"}) == RouteCategory.MODEL_GENERATION
        assert shaper._classify({"operation": "generate_text"}) == RouteCategory.MODEL_GENERATION
        assert shaper._classify({"operation": "completion"}) == RouteCategory.MODEL_GENERATION

    def test_classify_hitl_indicators(self):
        """Test _classify detects HITL indicators."""
        shaper = ClassifierShaper()
        
        # Low confidence
        assert shaper._classify({"operation": "decision", "confidence": 0.3}) == RouteCategory.HITL_REQUIRED
        
        # HITL in operation name
        assert shaper._classify({"operation": "hitl_approval"}) == RouteCategory.HITL_REQUIRED

    def test_classify_fallback_default(self):
        """Test _classify falls back to FALLBACK_SAFE."""
        shaper = ClassifierShaper()
        
        assert shaper._classify({"operation": "random_operation"}) == RouteCategory.FALLBACK_SAFE

    def test_assess_risk_tier_hitl_boost(self):
        """Test _assess_risk_tier boosts HITL_REQUIRED category."""
        shaper = ClassifierShaper()
        
        # HITL_REQUIRED should boost risk score to at least 0.7
        tier = shaper._assess_risk_tier(0.2, RouteCategory.HITL_REQUIRED)
        assert tier == RiskTier.HIGH

    def test_assess_risk_tier_tool_call_boost(self):
        """Test _assess_risk_tier boosts TOOL_CALL category."""
        shaper = ClassifierShaper()
        
        # TOOL_CALL should boost risk score to at least 0.5
        tier = shaper._assess_risk_tier(0.2, RouteCategory.TOOL_CALL)
        assert tier == RiskTier.MEDIUM

    def test_assess_risk_tier_thresholds(self):
        """Test _assess_risk_tier respects thresholds."""
        shaper = ClassifierShaper()
        
        assert shaper._assess_risk_tier(0.2, RouteCategory.CACHE_HIT) == RiskTier.LOW
        assert shaper._assess_risk_tier(0.4, RouteCategory.CACHE_HIT) == RiskTier.LOW
        assert shaper._assess_risk_tier(0.5, RouteCategory.CACHE_HIT) == RiskTier.MEDIUM
        assert shaper._assess_risk_tier(0.7, RouteCategory.CACHE_HIT) == RiskTier.HIGH
        assert shaper._assess_risk_tier(0.9, RouteCategory.CACHE_HIT) == RiskTier.CRITICAL

    def test_select_route_all_categories(self):
        """Test _select_route returns correct route for each category."""
        shaper = ClassifierShaper()
        
        assert shaper._select_route(RouteCategory.CACHE_HIT, RiskTier.LOW) == "L0_cache"
        assert shaper._select_route(RouteCategory.RAG_GROUNDED, RiskTier.MEDIUM) == "C0_retrieval"
        assert shaper._select_route(RouteCategory.TOOL_CALL, RiskTier.HIGH) == "L2_execution"
        assert shaper._select_route(RouteCategory.MODEL_GENERATION, RiskTier.CRITICAL) == "L2_model_invoke"
        assert shaper._select_route(RouteCategory.HITL_REQUIRED, RiskTier.HIGH) == "L5_HITL"
        assert shaper._select_route(RouteCategory.FALLBACK_SAFE, RiskTier.LOW) == "L0_fallback"

    def test_select_route_unknown_category(self):
        """Test _select_route returns default for unknown category."""
        shaper = ClassifierShaper()
        
        # Create a mock category that's not in the mapping
        class MockCategory:
            name = "MOCK"
        
        route = shaper._select_route(MockCategory(), RiskTier.LOW)
        assert route == "L0_default"

    def test_shape_payload(self):
        """Test _shape_payload adds governance metadata."""
        shaper = ClassifierShaper()
        request = {"operation": "test", "key": "value"}
        
        shaped = shaper._shape_payload(request, RouteCategory.CACHE_HIT)
        
        assert shaped["operation"] == "test"
        assert shaped["key"] == "value"
        assert shaped["governance_category"] == "CACHE_HIT"
        assert shaped["shaped_at"] == "g5_classifier"

    def test_set_risk_threshold(self):
        """Test set_risk_threshold updates threshold."""
        shaper = ClassifierShaper()
        
        shaper.set_risk_threshold(RiskTier.LOW, 0.4)
        assert shaper._risk_thresholds[RiskTier.LOW] == 0.4

    def test_set_risk_threshold_clamps_to_zero(self):
        """Test set_risk_threshold clamps negative values to 0.0."""
        shaper = ClassifierShaper()
        
        shaper.set_risk_threshold(RiskTier.LOW, -0.5)
        assert shaper._risk_thresholds[RiskTier.LOW] == 0.0

    def test_set_risk_threshold_clamps_to_one(self):
        """Test set_risk_threshold clamps values above 1.0 to 1.0."""
        shaper = ClassifierShaper()
        
        shaper.set_risk_threshold(RiskTier.HIGH, 1.5)
        assert shaper._risk_thresholds[RiskTier.HIGH] == 1.0
