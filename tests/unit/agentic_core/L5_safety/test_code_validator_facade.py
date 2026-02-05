"""
Unit Tests for CodeValidatorAgent Facade - Phase 2

Tests the facade conversion of CodeValidatorAgent including:
- Legacy signature compatibility
- CodeValidatorStrategy functionality
- Validation preservation
- Return type consistency
"""

from __future__ import annotations

import pytest
from unittest.mock import Mock, patch

from agentic_core.base_agents.UnifiedAgent import (
    ValidationResult,
    CodeValidatorStrategy,
)


class TestCodeValidatorStrategy:
    """Tests for CodeValidatorStrategy."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return {
            "check_syntax": True,
            "check_canon": True,
            "check_async": True,
            "check_prints": True,
            "print_policy": "warn",
        }

    @pytest.fixture
    def strategy(self, config):
        """Create CodeValidatorStrategy instance."""
        return CodeValidatorStrategy(config)

    def test_initialization(self, strategy, config):
        """Test strategy initialization."""
        assert strategy.check_syntax is True
        assert strategy.check_canon is True
        assert strategy.check_async is True
        assert strategy.check_prints is True
        assert strategy.print_policy == "warn"

    def test_initialization_with_disabled_features(self):
        """Test strategy initialization with disabled features."""
        config = {
            "check_syntax": False,
            "check_canon": True,
            "check_async": False,
            "check_prints": True,
            "print_policy": "error",
        }
        strategy = CodeValidatorStrategy(config)

        assert strategy.check_syntax is False
        assert strategy.check_canon is True
        assert strategy.check_async is False
        assert strategy.check_prints is True
        assert strategy.print_policy == "error"

    @pytest.mark.asyncio
    async def test_execute_returns_validation_result(self, strategy):
        """Test execute returns ValidationResult."""
        mock_agent = Mock()
        mock_agent.log_info = Mock()

        result = await strategy.execute(mock_agent)

        assert isinstance(result, ValidationResult)
        assert result.passed is True  # No file_path provided, no violations

    @pytest.mark.asyncio
    async def test_execute_with_file_path(self, strategy):
        """Test execute with file_path parameter."""
        mock_agent = Mock()
        mock_agent.log_info = Mock()
        mock_agent.validate_file = Mock(return_value=[])

        result = await strategy.execute(mock_agent, file_path="/test/file.py")

        assert isinstance(result, ValidationResult)
        assert result.passed is True


class TestCodeValidatorAgentFacade:
    """Tests for CodeValidatorAgent facade."""

    @pytest.fixture
    def agent(self):
        """Create CodeValidatorAgent instance."""
        with patch("agentic_core.base_agents.SovereignBaseAgent.SovereignBaseAgent.__init__"):
            from agentic_core.L5_safety.policy_engine.code_validator_agent_types import (
                CodeValidatorAgent,
            )

            return CodeValidatorAgent()

    def test_initialization(self, agent):
        """Test agent initialization."""
        assert agent.ruleset is not None
        assert agent._validation_results == []

    def test_unified_strategy_initialized(self, agent):
        """Test unified strategy is initialized."""
        assert agent._unified_strategy is not None
        assert isinstance(agent._unified_strategy, CodeValidatorStrategy)

    def test_validate_syntax_method_exists(self, agent):
        """Test validate_syntax method exists."""
        assert hasattr(agent, "validate_syntax")
        assert callable(agent.validate_syntax)

    def test_validate_canon_method_exists(self, agent):
        """Test validate_canon method exists."""
        assert hasattr(agent, "validate_canon")
        assert callable(agent.validate_canon)

    def test_validate_async_method_exists(self, agent):
        """Test validate_async method exists."""
        assert hasattr(agent, "validate_async")
        assert callable(agent.validate_async)

    def test_validate_prints_method_exists(self, agent):
        """Test validate_prints method exists."""
        assert hasattr(agent, "validate_prints")
        assert callable(agent.validate_prints)

    def test_validate_file_method_exists(self, agent):
        """Test validate_file method exists."""
        assert hasattr(agent, "validate_file")
        assert callable(agent.validate_file)

    def test_validate_directory_method_exists(self, agent):
        """Test validate_directory method exists."""
        assert hasattr(agent, "validate_directory")
        assert callable(agent.validate_directory)

    def test_validate_project_method_exists(self, agent):
        """Test validate_project method exists."""
        assert hasattr(agent, "validate_project")
        assert callable(agent.validate_project)

    def test_heal_repository_method_exists(self, agent):
        """Test heal_repository method exists."""
        assert hasattr(agent, "heal_repository")
        assert callable(agent.heal_repository)

    def test_heal_method_exists(self, agent):
        """Test heal method exists."""
        assert hasattr(agent, "heal")
        assert callable(agent.heal)


class TestValidationTypes:
    """Tests for validation type enums and dataclasses."""

    def test_violation_type_enum(self):
        """Test ViolationType enum exists."""
        from agentic_core.L5_safety.policy_engine.code_validator_agent_types import (
            ViolationType,
        )

        assert hasattr(ViolationType, "SYNTAX")
        assert hasattr(ViolationType, "CANON")
        assert hasattr(ViolationType, "ASYNC")
        assert hasattr(ViolationType, "PRINT")

    def test_violation_dataclass(self):
        """Test Violation dataclass exists."""
        from agentic_core.L5_safety.policy_engine.code_validator_agent_types import (
            Violation,
            ViolationType,
        )

        violation = Violation(
            violation_type=ViolationType.SYNTAX,
            file_path="/test/file.py",
            line_number=10,
            issue="Test issue",
        )

        assert violation.violation_type == ViolationType.SYNTAX
        assert violation.severity == "MEDIUM"
        assert violation.auto_fixable is False

    def test_ruleset_dataclass(self):
        """Test RuleSet dataclass exists."""
        from agentic_core.L5_safety.policy_engine.code_validator_agent_types import RuleSet

        ruleset = RuleSet()

        assert ruleset.check_syntax is True
        assert ruleset.check_canon is True
        assert ruleset.check_async is True
        assert ruleset.check_prints is True
        assert ruleset.print_policy == "warn"

    def test_validation_report_dataclass(self):
        """Test ValidationReport dataclass exists."""
        from agentic_core.L5_safety.policy_engine.code_validator_agent_types import (
            ValidationReport,
        )

        report = ValidationReport(
            validation_summary={"total": 0},
            violations=[],
            total_violations=0,
            auto_fixable_count=0,
            high_severity_count=0,
        )

        assert report.total_violations == 0
        assert isinstance(report.to_dict(), dict)


class TestLegacyCompatibility:
    """Tests ensuring 100% legacy compatibility."""

    def test_import_compatibility(self):
        """Test original import still works."""
        from agentic_core.L5_safety.policy_engine.code_validator_agent_types import (
            CodeValidatorAgent,
        )

        assert CodeValidatorAgent is not None

    def test_inherits_from_sovereign_base(self):
        """Test class still inherits from SovereignBaseAgent."""
        from agentic_core.L5_safety.policy_engine.code_validator_agent_types import (
            CodeValidatorAgent,
        )
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

        assert issubclass(CodeValidatorAgent, SovereignBaseAgent)

    def test_factory_functions_exist(self):
        """Test factory functions exist."""
        from agentic_core.L5_safety.policy_engine.code_validator_agent_types import (
            create_legacy_syntax_validator,
            create_legacy_canon_validator,
            create_legacy_async_validator,
            create_legacy_print_validator,
        )

        assert callable(create_legacy_syntax_validator)
        assert callable(create_legacy_canon_validator)
        assert callable(create_legacy_async_validator)
        assert callable(create_legacy_print_validator)

    def test_factory_syntax_validator(self):
        """Test create_legacy_syntax_validator creates correct config."""
        with patch("agentic_core.base_agents.SovereignBaseAgent.SovereignBaseAgent.__init__"):
            from agentic_core.L5_safety.policy_engine.code_validator_agent_types import (
                create_legacy_syntax_validator,
            )

            validator = create_legacy_syntax_validator()
            assert validator.ruleset.check_syntax is True
            assert validator.ruleset.check_canon is False

    def test_factory_canon_validator(self):
        """Test create_legacy_canon_validator creates correct config."""
        with patch("agentic_core.base_agents.SovereignBaseAgent.SovereignBaseAgent.__init__"):
            from agentic_core.L5_safety.policy_engine.code_validator_agent_types import (
                create_legacy_canon_validator,
            )

            validator = create_legacy_canon_validator()
            assert validator.ruleset.check_canon is True
            assert validator.ruleset.check_syntax is False

    def test_all_exports(self):
        """Test __all__ exports are correct."""
        from agentic_core.L5_safety.policy_engine.code_validator_agent_types import __all__

        expected = [
            "CodeValidatorAgent",
            "ViolationType",
            "Violation",
            "RuleSet",
            "ValidationReport",
            "create_legacy_syntax_validator",
            "create_legacy_canon_validator",
            "create_legacy_async_validator",
            "create_legacy_print_validator",
        ]
        for item in expected:
            assert item in __all__


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
