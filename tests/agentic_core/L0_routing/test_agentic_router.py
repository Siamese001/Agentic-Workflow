"""Tests for L0_routing.reasoning.agentic_router module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agentic_core.L0_routing.reasoning import agentic_router


class TestAgenticRouter:
    """Test suite for AgenticRouter routing logic."""

    def setup_method(self):
        """Reset router state before each test."""
        self.router = agentic_router.AgenticRouter()

    def test_router_init(self):
        """Test AgenticRouter initialization."""
        router = agentic_router.AgenticRouter()
        assert router is not None
        assert router._targets == {}
        assert router.min_confidence == 0.2

    def test_router_init_with_custom_params(self):
        """Test AgenticRouter initialization with custom parameters."""
        fallback = AsyncMock()
        router = agentic_router.AgenticRouter(
            fallback_handler=fallback, min_confidence=0.5
        )
        assert router.min_confidence == 0.5
        assert router._fallback is fallback

    def test_register_target(self):
        """Test registering a routing target."""
        handler = AsyncMock(return_value="result")
        self.router.register("test_agent", handler, intent_keywords=["test", "agent"])
        
        assert "test_agent" in self.router._targets
        assert self.router._targets["test_agent"].name == "test_agent"
        assert self.router._targets["test_agent"].handler is handler
        assert "test" in self.router._targets["test_agent"].intent_keywords

    def test_register_target_with_description(self):
        """Test registering a target with description."""
        handler = AsyncMock(return_value="result")
        self.router.register(
            "test_agent", handler, intent_keywords=["test"], description="Test agent"
        )
        
        assert self.router._targets["test_agent"].description == "Test agent"

    def test_register_mad(self):
        """Test registering Multi-Agent Debate target."""
        debater1 = AsyncMock(return_value="answer1")
        debater2 = AsyncMock(return_value="answer2")
        synthesizer = AsyncMock(return_value="synthesized")
        
        self.router.register_mad([debater1, debater2], synthesizer)
        
        assert agentic_router._MAD_TARGET in self.router._targets
        assert "debate" in self.router._targets[agentic_router._MAD_TARGET].intent_keywords

    def test_route_with_registered_target(self):
        """Test routing to a registered target."""
        handler = AsyncMock(return_value="result")
        self.router.register("test_agent", handler, intent_keywords=["test"])
        
        # Mock the _classify method to return a known target
        with patch.object(self.router, "_classify", return_value=("test_intent", "test_agent", 0.95)):
            with patch("agentic_core.L0_routing.reasoning.agentic_router._get_routing_gateway"):
                with patch("agentic_core.L0_routing.reasoning.agentic_router._get_proof_emitter"):
                    with patch("agentic_core.L0_routing.reasoning.agentic_router.emit_replay_key"):
                        with patch("agentic_core.L0_routing.reasoning.agentic_router._emit_records_execution_trace"):
                            with patch("agentic_core.L0_routing.reasoning.agentic_router._emit_signs_execution_trace"):
                                with patch("agentic_core.L0_routing.reasoning.agentic_router.emit_determinism_digest"):
                                    with patch(
                                        "agentic_core.runtime.types.execution_trace.get_active_execution_trace"
                                    ) as mock_trace:
                                        mock_trace.return_value = MagicMock(trace_id="test_trace")
                                        decision = self.router.route("test input")
                                        
                                        assert decision.target_name == "test_agent"
                                        assert decision.confidence == 0.95

    def test_route_no_target_below_threshold(self):
        """Test routing with no target above confidence threshold."""
        # Mock _classify to return low confidence
        with patch.object(self.router, "_classify", return_value=("test_intent", None, 0.1)):
            with patch("agentic_core.L0_routing.reasoning.agentic_router._get_routing_gateway"):
                with patch("agentic_core.L0_routing.reasoning.agentic_router._get_proof_emitter"):
                    with patch("agentic_core.L0_routing.reasoning.agentic_router.emit_replay_key"):
                        with patch("agentic_core.L0_routing.reasoning.agentic_router._emit_records_execution_trace"):
                            with patch("agentic_core.L0_routing.reasoning.agentic_router._emit_signs_execution_trace"):
                                with patch("agentic_core.L0_routing.reasoning.agentic_router.emit_determinism_digest"):
                                    with patch(
                                        "agentic_core.runtime.types.execution_trace.get_active_execution_trace"
                                    ) as mock_trace:
                                        mock_trace.return_value = MagicMock(trace_id="test_trace")
                                        decision = self.router.route("test input")
                                        
                                        assert decision.target_name is None
                                        assert decision.confidence == 0.1

    def test_route_with_fallback_handler(self):
        """Test routing with fallback handler when no target matches."""
        fallback = AsyncMock(return_value="fallback_result")
        router = agentic_router.AgenticRouter(fallback_handler=fallback)
        
        with patch.object(router, "_classify", return_value=("test_intent", None, 0.1)):
            with patch("agentic_core.L0_routing.reasoning.agentic_router._get_routing_gateway"):
                with patch("agentic_core.L0_routing.reasoning.agentic_router._get_proof_emitter"):
                    with patch("agentic_core.L0_routing.reasoning.agentic_router.emit_replay_key"):
                        with patch("agentic_core.L0_routing.reasoning.agentic_router._emit_records_execution_trace"):
                            with patch("agentic_core.L0_routing.reasoning.agentic_router._emit_signs_execution_trace"):
                                with patch("agentic_core.L0_routing.reasoning.agentic_router.emit_determinism_digest"):
                                    with patch(
                                        "agentic_core.runtime.types.execution_trace.get_active_execution_trace"
                                    ) as mock_trace:
                                        mock_trace.return_value = MagicMock(trace_id="test_trace")
                                        decision = router.route("test input")
                                        
                                        fallback.assert_called_once()

    def test_route_target_dataclass(self):
        """Test RouteTarget dataclass structure."""
        handler = AsyncMock()
        target = agentic_router.RouteTarget(
            name="test", handler=handler, intent_keywords=["kw1"], description="desc"
        )
        
        assert target.name == "test"
        assert target.handler is handler
        assert target.intent_keywords == ["kw1"]
        assert target.description == "desc"

    def test_routing_decision_dataclass(self):
        """Test RoutingDecision dataclass structure."""
        decision = agentic_router.RoutingDecision(
            intent="test_intent", target_name="test_target", confidence=0.95
        )
        
        assert decision.intent == "test_intent"
        assert decision.target_name == "test_target"
        assert decision.confidence == 0.95
        assert decision.result is None
        assert decision.error is None

    def test_public_api_exports(self):
        """Test that public API functions are exported."""
        assert hasattr(agentic_router, "AgenticRouter")
        assert hasattr(agentic_router, "RouteTarget")
        assert hasattr(agentic_router, "RoutingDecision")
