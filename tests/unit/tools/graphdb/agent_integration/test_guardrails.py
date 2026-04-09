"""Tests for Architectural Guardrails - Phase 1 GraphDB integration."""

import pytest
from unittest.mock import Mock, patch

from tools.graphdb.agent_integration.guardrails import (
    ArchitecturalGuardrails,
    GuardrailResult,
    GuardrailAction,
    HighRiskActionFilter,
)
from tools.graphdb.agent_integration.decision_engine import ArchitecturalContext, DecisionResult, RiskLevel


class TestArchitecturalGuardrails:
    """Test suite for ArchitecturalGuardrails."""

    @pytest.fixture
    def mock_decision_engine(self):
        """Create mock decision engine."""
        engine = Mock()
        engine.analyze_action.return_value = DecisionResult(
            approved=True,
            risk_level=RiskLevel.LOW,
            insights=["Test insight"],
            warnings=[],
            alternatives=[],
            architectural_justification="Test justification",
        )
        return engine

    @pytest.fixture
    def guardrails(self, mock_decision_engine):
        """Create guardrails with mock decision engine."""
        return ArchitecturalGuardrails(mock_decision_engine)

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

    def test_initialization(self, mock_decision_engine):
        """Test guardrails initialization."""
        guardrails = ArchitecturalGuardrails(mock_decision_engine)

        assert guardrails.decision_engine == mock_decision_engine
        assert guardrails.blocked_actions == []
        assert guardrails.warned_actions == []

    def test_validate_action_low_risk(self, guardrails, sample_context, mock_decision_engine):
        """Test validation of low risk actions."""
        mock_decision_engine.analyze_action.return_value = DecisionResult(
            approved=True,
            risk_level=RiskLevel.LOW,
            insights=["Low risk action"],
            warnings=[],
            alternatives=[],
            architectural_justification="Action is safe",
        )

        result = guardrails.validate_action(sample_context)

        assert result.action == GuardrailAction.ALLOW
        assert "approved" in result.message.lower()
        assert result.required_modifications == []
        assert result.escalation_required is False

    def test_validate_action_medium_risk(self, guardrails, sample_context, mock_decision_engine):
        """Test validation of medium risk actions."""
        mock_decision_engine.analyze_action.return_value = DecisionResult(
            approved=True,
            risk_level=RiskLevel.MEDIUM,
            insights=["Medium risk action"],
            warnings=["Consider impact"],
            alternatives=[],
            architectural_justification="Action requires caution",
        )

        result = guardrails.validate_action(sample_context)

        assert result.action == GuardrailAction.WARN
        assert "caution" in result.message.lower()
        assert result.required_modifications == []
        assert result.escalation_required is False

    def test_validate_action_high_risk_with_alternatives(
        self, guardrails, sample_context, mock_decision_engine
    ):
        """Test validation of high risk actions with alternatives."""
        mock_decision_engine.analyze_action.return_value = DecisionResult(
            approved=False,
            risk_level=RiskLevel.HIGH,
            insights=["High risk action"],
            warnings=["Significant impact"],
            alternatives=[{"type": "use_gateway", "description": "Use gateway pattern"}],
            architectural_justification="Action requires safer alternative",
        )

        result = guardrails.validate_action(sample_context)

        assert result.action == GuardrailAction.REQUIRE_ALTERNATIVE
        assert "alternative" in result.message.lower()
        assert len(result.required_modifications) > 0
        assert result.escalation_required is False

    def test_validate_action_high_risk_no_alternatives(
        self, guardrails, sample_context, mock_decision_engine
    ):
        """Test validation of high risk actions without alternatives."""
        mock_decision_engine.analyze_action.return_value = DecisionResult(
            approved=False,
            risk_level=RiskLevel.HIGH,
            insights=["High risk action"],
            warnings=["Significant impact"],
            alternatives=[],
            architectural_justification="Action requires caution",
        )

        result = guardrails.validate_action(sample_context)

        assert result.action == GuardrailAction.WARN
        assert "proceed with caution" in result.message.lower()
        assert result.escalation_required is False

    def test_validate_action_critical_risk(self, guardrails, sample_context, mock_decision_engine):
        """Test validation of critical risk actions."""
        mock_decision_engine.analyze_action.return_value = DecisionResult(
            approved=False,
            risk_level=RiskLevel.CRITICAL,
            insights=["Critical risk action"],
            warnings=["Severe impact", "Sovereignty violation"],
            alternatives=[{"type": "use_gateway", "description": "Use gateway pattern"}],
            architectural_justification="Action blocked due to critical risk",
        )

        result = guardrails.validate_action(sample_context)

        assert result.action == GuardrailAction.BLOCK
        assert "blocked" in result.message.lower()
        assert len(result.required_modifications) > 0
        assert result.escalation_required is True

        # Check that action was logged in blocked_actions
        assert len(guardrails.blocked_actions) == 1
        assert guardrails.blocked_actions[0]["reason"] == "Critical architectural risk"

    def test_get_guardrail_statistics(self, guardrails, mock_decision_engine):
        """Test guardrail statistics collection."""
        # Simulate some blocked and warned actions
        mock_decision_engine.analyze_action.return_value = DecisionResult(
            approved=False,
            risk_level=RiskLevel.CRITICAL,
            insights=["Critical"],
            warnings=["Severe"],
            alternatives=[],
            architectural_justification="Blocked",
        )

        context = ArchitecturalContext(
            agent_type="test",
            action_type="test",
            target_modules=["test"],
            proposed_changes={},
            session_id="test",
        )

        # Block an action
        guardrails.validate_action(context)

        # Warn an action
        mock_decision_engine.analyze_action.return_value = DecisionResult(
            approved=False,
            risk_level=RiskLevel.HIGH,
            insights=["High risk"],
            warnings=["Impact"],
            alternatives=[],
            architectural_justification="Warning",
        )

        guardrails.validate_action(context)

        stats = guardrails.get_guardrail_statistics()

        assert stats["total_blocked"] == 1
        assert stats["total_warned"] == 1
        assert stats["block_rate"] == 0.5  # 1 blocked out of 2 total
        assert len(stats["recent_blocks"]) == 1
        assert len(stats["recent_warnings"]) == 1

    def test_get_critical_modifications(self, guardrails):
        """Test critical modification suggestions."""
        decision_result = DecisionResult(
            approved=False,
            risk_level=RiskLevel.CRITICAL,
            insights=["Critical"],
            warnings=["UWG bypass risk: module → direct_write", "High blast radius"],
            alternatives=[
                {"type": "use_gateway", "description": "Use gateway pattern"},
                {"type": "phased", "description": "Implement in phases"},
            ],
            architectural_justification="Blocked",
        )

        modifications = guardrails._get_critical_modifications(decision_result)

        assert len(modifications) >= 2
        assert any("gateway" in mod for mod in modifications)
        assert any("blast radius" in mod for mod in modifications)
        assert any("Consider:" in mod for mod in modifications)


class TestGuardrailResult:
    """Test suite for GuardrailResult."""

    def test_guardrail_result_creation(self):
        """Test guardrail result creation."""
        result = GuardrailResult(
            action=GuardrailAction.ALLOW,
            message="Test message",
            decision_result=Mock(),
            required_modifications=["mod1", "mod2"],
            escalation_required=False,
        )

        assert result.action == GuardrailAction.ALLOW
        assert result.message == "Test message"
        assert result.required_modifications == ["mod1", "mod2"]
        assert result.escalation_required is False


class TestHighRiskActionFilter:
    """Test suite for HighRiskActionFilter."""

    def test_is_high_risk_patterns(self):
        """Test high risk pattern detection."""
        # Test high risk action types
        assert HighRiskActionFilter.is_high_risk("write_file", ["module1"])
        assert HighRiskActionFilter.is_high_risk("create_module", ["module1"])
        assert HighRiskActionFilter.is_high_risk("import_module", ["module1"])
        assert HighRiskActionFilter.is_high_risk("direct_write", ["module1"])
        assert HighRiskActionFilter.is_high_risk("cross_layer_call", ["module1"])

        # Test high risk target modules
        assert HighRiskActionFilter.is_high_risk("read_file", ["spine_module"])
        assert HighRiskActionFilter.is_high_risk("read_file", ["critical_component"])
        assert HighRiskActionFilter.is_high_risk("read_file", ["core_system"])

        # Test low risk action
        assert not HighRiskActionFilter.is_high_risk("read_config", ["safe_module"])
        assert not HighRiskActionFilter.is_high_risk("analyze_code", ["utility"])

    def test_get_required_validations(self):
        """Test required validations for action types."""
        # File write actions
        validations = HighRiskActionFilter.get_required_validations("write_file")
        assert "illegal_paths" in validations
        assert "uwg_conformance" in validations

        # Module import actions
        validations = HighRiskActionFilter.get_required_validations("import_module")
        assert "layer_violations" in validations
        assert "blast_radius" in validations

        # Gateway bypass actions
        validations = HighRiskActionFilter.get_required_validations("direct_write")
        assert "uwg_conformance" in validations
        assert "sovereignty_check" in validations

        # Layer violation actions
        validations = HighRiskActionFilter.get_required_validations("cross_layer_call")
        assert "gravity_imports" in validations
        assert "layer_reach" in validations

        # Low risk action
        validations = HighRiskActionFilter.get_required_validations("read_file")
        assert len(validations) == 0

    def test_high_risk_patterns_completeness(self):
        """Test that all high risk patterns are covered."""
        patterns = HighRiskActionFilter.HIGH_RISK_PATTERNS

        # Check that all expected categories exist
        expected_categories = [
            "file_write",
            "module_import",
            "gateway_bypass",
            "layer_violation",
            "critical_path",
        ]

        for category in expected_categories:
            assert category in patterns
            assert len(patterns[category]) > 0

        # Check that patterns are lowercase for consistent matching
        for category, pattern_list in patterns.items():
            for pattern in pattern_list:
                assert pattern == pattern.lower()
                assert isinstance(pattern, str)


class TestGuardrailAction:
    """Test suite for GuardrailAction enum."""

    def test_guardrail_action_values(self):
        """Test guardrail action enum values."""
        assert GuardrailAction.ALLOW.value == "allow"
        assert GuardrailAction.WARN.value == "warn"
        assert GuardrailAction.BLOCK.value == "block"
        assert GuardrailAction.REQUIRE_ALTERNATIVE.value == "require_alternative"
