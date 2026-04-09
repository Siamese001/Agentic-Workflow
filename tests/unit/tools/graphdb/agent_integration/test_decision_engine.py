"""Tests for Agent Decision Engine - Phase 1 GraphDB integration."""

import pytest
import networkx as nx
from unittest.mock import Mock, patch

from tools.graphdb.agent_integration.decision_engine import (
    AgentDecisionEngine,
    ArchitecturalContext,
    DecisionResult,
    RiskLevel,
)
from tools.graphdb.agent_integration.cache import QueryCache


class TestAgentDecisionEngine:
    """Test suite for AgentDecisionEngine."""

    @pytest.fixture
    def mock_graph(self):
        """Create a mock NetworkX graph for testing."""
        graph = nx.DiGraph()

        # Add some test nodes
        graph.add_node("node1", name="test_module", graph_type="Module", properties={"layer": "L2"})
        graph.add_node("node2", name="uwg_gateway", graph_type="Gateway", properties={"layer": "L5"})
        graph.add_node("node3", name="spine_component", graph_type="Component", properties={"layer": "L1"})

        # Add some test edges
        graph.add_edge("node1", "node2", graph_type="WRITES_TO")
        graph.add_edge("node3", "node1", graph_type="CALLS")

        return graph

    @pytest.fixture
    def decision_engine(self, mock_graph):
        """Create decision engine with mock graph."""
        cache = QueryCache(max_size=100, default_ttl=60.0)
        return AgentDecisionEngine(mock_graph, cache)

    @pytest.fixture
    def sample_context(self):
        """Create sample architectural context."""
        return ArchitecturalContext(
            agent_type="code_agent",
            action_type="write_file",
            target_modules=["test_module"],
            proposed_changes={"type": "direct_write"},
            session_id="test_session_123",
        )

    def test_initialization(self, mock_graph):
        """Test decision engine initialization."""
        engine = AgentDecisionEngine(mock_graph)

        assert engine.graph == mock_graph
        assert engine.cache is not None
        assert engine.structural_queries is not None
        assert engine.blast_queries is not None

    def test_analyze_action_basic(self, decision_engine, sample_context):
        """Test basic action analysis."""
        with (
            patch.object(
                decision_engine.structural_queries, "uwg_durable_write_conformance", return_value=[]
            ),
            patch.object(
                decision_engine,
                "_analyze_blast_radius",
                return_value={"total_impact": 0, "risk_level": "low"},
            ),
            patch.object(
                decision_engine.structural_queries,
                "agentic_spine_completeness",
                return_value={"spine_complete": True},
            ),
        ):
            result = decision_engine.analyze_action(sample_context)

            assert isinstance(result, DecisionResult)
            assert result.approved is True
            assert result.risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
            assert isinstance(result.insights, list)
            assert isinstance(result.warnings, list)
            assert isinstance(result.alternatives, list)
            assert isinstance(result.architectural_justification, str)

    def test_analyze_action_with_violations(self, decision_engine, sample_context):
        """Test action analysis with violations."""
        violations = [{"from_node": "test_module", "to_node": "direct_write", "type": "uwg_bypass"}]

        with (
            patch.object(
                decision_engine.structural_queries, "uwg_durable_write_conformance", return_value=violations
            ),
            patch.object(
                decision_engine,
                "_analyze_blast_radius",
                return_value={"total_impact": 5, "risk_level": "medium"},
            ),
            patch.object(
                decision_engine.structural_queries,
                "agentic_spine_completeness",
                return_value={"spine_complete": True},
            ),
        ):
            result = decision_engine.analyze_action(sample_context)

            assert result.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
            assert len(result.warnings) > 0
            assert "UWG bypass" in result.warnings[0]

    def test_check_illegal_paths_with_cache(self, decision_engine, sample_context):
        """Test illegal path checking with caching."""
        violations = [{"from_node": "test", "to_node": "direct"}]

        with patch.object(
            decision_engine.structural_queries, "uwg_durable_write_conformance", return_value=violations
        ):
            # First call should query and cache
            result1 = decision_engine._check_illegal_paths(sample_context)
            assert result1 == violations

            # Second call should use cache
            result2 = decision_engine._check_illegal_paths(sample_context)
            assert result2 == violations

            # Verify cache was used
            cache_key = f"illegal_paths_{hash(str(sample_context.target_modules))}"
            cached_value = decision_engine.cache.get(cache_key)
            assert cached_value == violations

    def test_analyze_blast_radius_error_handling(self, decision_engine, sample_context):
        """Test blast radius analysis error handling."""
        with patch.object(decision_engine, "_find_node_by_module", side_effect=ValueError("Node not found")):
            result = decision_engine._analyze_blast_radius(sample_context)

            assert "error" in result["per_module"]["test_module"]
            assert result["total_impact"] == 0

    def test_risk_level_calculation(self, decision_engine):
        """Test risk level calculation logic."""
        # Test low risk
        risk = decision_engine._calculate_risk_level([], {"total_impact": 0}, {"spine_complete": True})
        assert risk == RiskLevel.LOW

        # Test medium risk
        risk = decision_engine._calculate_risk_level([], {"total_impact": 5}, {"spine_complete": True})
        assert risk == RiskLevel.MEDIUM

        # Test high risk
        risk = decision_engine._calculate_risk_level(
            [{"violation": "test"}], {"total_impact": 5}, {"spine_complete": True}
        )
        assert risk == RiskLevel.HIGH

        # Test critical risk
        risk = decision_engine._calculate_risk_level(
            [{"violation": "test"}, {"violation": "test2"}], {"total_impact": 10}, {"spine_complete": False}
        )
        assert risk == RiskLevel.CRITICAL

    def test_generate_insights(self, decision_engine):
        """Test insight generation."""
        illegal_paths = [{"from_node": "test", "to_node": "direct"}]
        blast_impact = {"total_impact": 5}
        spine_completeness = {"spine_complete": False, "missing_components": ["L1_reasoning"]}

        insights = decision_engine._generate_insights(illegal_paths, blast_impact, spine_completeness)

        assert len(insights) == 3
        assert any("sovereignty violations" in insight for insight in insights)
        assert any("downstream dependencies" in insight for insight in insights)
        assert any("spine components" in insight for insight in insights)

    def test_suggest_alternatives(self, decision_engine, sample_context):
        """Test alternative suggestion."""
        illegal_paths = [{"from_node": "test", "to_node": "direct"}]
        blast_impact = {"total_impact": 15}  # High impact

        alternatives = decision_engine._suggest_alternatives(sample_context, illegal_paths, blast_impact)

        assert len(alternatives) == 2
        assert any(alt["type"] == "use_gateway_pattern" for alt in alternatives)
        assert any(alt["type"] == "phased_implementation" for alt in alternatives)

    def test_find_node_by_module(self, decision_engine):
        """Test node finding by module name."""
        # Test existing node
        node_id = decision_engine._find_node_by_module("test_module")
        assert node_id == "node1"

        # Test non-existing node
        node_id = decision_engine._find_node_by_module("nonexistent")
        assert node_id is None

    def test_classify_blast_risk(self, decision_engine):
        """Test blast risk classification."""
        assert decision_engine._classify_blast_risk(0) == "low"
        assert decision_engine._classify_blast_risk(5) == "medium"
        assert decision_engine._classify_blast_risk(10) == "medium"
        assert decision_engine._classify_blast_risk(20) == "high"
        assert decision_engine._classify_blast_risk(50) == "high"


class TestArchitecturalContext:
    """Test suite for ArchitecturalContext."""

    def test_context_creation(self):
        """Test architectural context creation."""
        context = ArchitecturalContext(
            agent_type="test_agent",
            action_type="test_action",
            target_modules=["module1", "module2"],
            proposed_changes={"key": "value"},
            session_id="session_123",
        )

        assert context.agent_type == "test_agent"
        assert context.action_type == "test_action"
        assert context.target_modules == ["module1", "module2"]
        assert context.proposed_changes == {"key": "value"}
        assert context.session_id == "session_123"


class TestDecisionResult:
    """Test suite for DecisionResult."""

    def test_decision_result_creation(self):
        """Test decision result creation."""
        result = DecisionResult(
            approved=True,
            risk_level=RiskLevel.LOW,
            insights=["Test insight"],
            warnings=["Test warning"],
            alternatives=[{"type": "test"}],
            architectural_justification="Test justification",
        )

        assert result.approved is True
        assert result.risk_level == RiskLevel.LOW
        assert result.insights == ["Test insight"]
        assert result.warnings == ["Test warning"]
        assert result.alternatives == [{"type": "test"}]
        assert result.architectural_justification == "Test justification"


class TestRiskLevel:
    """Test suite for RiskLevel enum."""

    def test_risk_level_values(self):
        """Test risk level enum values."""
        assert RiskLevel.LOW.value == "low"
        assert RiskLevel.MEDIUM.value == "medium"
        assert RiskLevel.HIGH.value == "high"
        assert RiskLevel.CRITICAL.value == "critical"
