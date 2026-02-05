"""
Unit Tests for StructuralValidatorAgent Facade - Phase 2

Tests the facade conversion of StructuralValidatorAgent including:
- Legacy signature compatibility
- StructuralValidatorStrategy functionality
- Validation preservation
- Return type consistency
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from agentic_core.base_agents.UnifiedAgent import (
    StructuralValidatorStrategy,
    ValidationResult,
)


class TestStructuralValidatorStrategy:
    """Tests for StructuralValidatorStrategy."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return {
            "enable_gravity": True,
            "enable_hierarchy": True,
            "enable_naming": True,
            "enable_documentation": True,
            "agent_suffix": "Agent",
        }

    @pytest.fixture
    def strategy(self, config):
        """Create StructuralValidatorStrategy instance."""
        return StructuralValidatorStrategy(config)

    def test_initialization(self, strategy, config):
        """Test strategy initialization."""
        assert strategy.enable_gravity is True
        assert strategy.enable_hierarchy is True
        assert strategy.enable_naming is True
        assert strategy.enable_documentation is True
        assert strategy.agent_suffix == "Agent"

    def test_initialization_with_disabled_features(self):
        """Test strategy initialization with disabled features."""
        config = {
            "enable_gravity": False,
            "enable_hierarchy": True,
            "enable_naming": False,
            "enable_documentation": True,
            "agent_suffix": "Handler",
        }
        strategy = StructuralValidatorStrategy(config)

        assert strategy.enable_gravity is False
        assert strategy.enable_hierarchy is True
        assert strategy.enable_naming is False
        assert strategy.enable_documentation is True
        assert strategy.agent_suffix == "Handler"

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


class TestStructuralValidatorAgentFacade:
    """Tests for StructuralValidatorAgent facade."""

    @pytest.fixture
    def agent(self):
        """Create StructuralValidatorAgent instance."""
        with patch("agentic_core.base_agents.SovereignBaseAgent.SovereignBaseAgent.__init__"):
            from agentic_core.L5_safety.policy_engine.structural_validator_agent_types import (
                StructuralValidatorAgent,
                StructureConfig,
            )

            agent = object.__new__(StructuralValidatorAgent)
            agent._config = StructureConfig()
            agent.project_root = Path.cwd()
            agent._lock = None
            agent._violations = []
            from agentic_core.base_agents.UnifiedAgent import (
                StructuralValidatorStrategy,
            )

            agent._unified_strategy = StructuralValidatorStrategy(
                {
                    "enable_gravity": True,
                    "enable_hierarchy": True,
                    "enable_naming": True,
                    "enable_documentation": True,
                    "agent_suffix": "Agent",
                }
            )
            return agent

    def test_initialization(self, agent):
        """Test agent initialization."""
        assert agent._config is not None
        assert agent._violations == []
        assert agent.project_root is not None

    def test_unified_strategy_initialized(self, agent):
        """Test unified strategy is initialized."""
        assert agent._unified_strategy is not None
        assert isinstance(agent._unified_strategy, StructuralValidatorStrategy)

    def test_config_property(self, agent):
        """Test config property exists."""
        assert hasattr(agent, "config")
        assert agent.config is not None

    def test_validate_structure_method_exists(self, agent):
        """Test validate_structure method exists."""
        assert hasattr(agent, "validate_structure")
        assert callable(agent.validate_structure)

    def test_validate_file_method_exists(self, agent):
        """Test validate_file method exists."""
        assert hasattr(agent, "validate_file")
        assert callable(agent.validate_file)

    def test_force_rename_class_method_exists(self, agent):
        """Test force_rename_class method exists."""
        assert hasattr(agent, "force_rename_class")
        assert callable(agent.force_rename_class)

    def test_heal_method_exists(self, agent):
        """Test heal method exists."""
        assert hasattr(agent, "heal")
        assert callable(agent.heal)

    def test_layer_order_constant(self, agent):
        """Test LAYER_ORDER constant exists."""
        assert hasattr(agent, "LAYER_ORDER")
        assert isinstance(agent.LAYER_ORDER, dict)
        assert "L0" in agent.LAYER_ORDER
        assert "L5" in agent.LAYER_ORDER

    def test_gravity_rules_constant(self, agent):
        """Test GRAVITY_RULES constant exists."""
        assert hasattr(agent, "GRAVITY_RULES")
        assert isinstance(agent.GRAVITY_RULES, dict)
        assert "L0" in agent.GRAVITY_RULES
        assert "L5" in agent.GRAVITY_RULES


class TestStructureTypes:
    """Tests for structure type classes and dataclasses."""

    def test_structure_violation_type_class(self):
        """Test StructureViolationType class exists."""
        from agentic_core.L5_safety.policy_engine.structural_validator_agent_types import (
            StructureViolationType,
        )

        assert hasattr(StructureViolationType, "GRAVITY")
        assert hasattr(StructureViolationType, "HIERARCHY")
        assert hasattr(StructureViolationType, "NAMING")
        assert hasattr(StructureViolationType, "DOCUMENTATION")
        assert hasattr(StructureViolationType, "ASCII")

    def test_structure_violation_dataclass(self):
        """Test StructureViolation dataclass exists."""
        from agentic_core.L5_safety.policy_engine.structural_validator_agent_types import (
            StructureViolation,
            StructureViolationType,
        )

        violation = StructureViolation(
            file_path=Path("/test/file.py"),
            line_number=10,
            violation_type=StructureViolationType.GRAVITY,
            message="Test violation",
        )

        assert violation.violation_type == StructureViolationType.GRAVITY
        assert violation.severity == "ERROR"
        assert violation.auto_fixable is False

    def test_structure_config_dataclass(self):
        """Test StructureConfig dataclass exists."""
        from agentic_core.L5_safety.policy_engine.structural_validator_agent_types import (
            StructureConfig,
        )

        config = StructureConfig()

        assert config.enable_gravity is True
        assert config.enable_hierarchy is True
        assert config.enable_naming is True
        assert config.enable_documentation is True
        assert config.agent_suffix == "Agent"


class TestLegacyCompatibility:
    """Tests ensuring 100% legacy compatibility."""

    def test_import_compatibility(self):
        """Test original import still works."""
        from agentic_core.L5_safety.policy_engine.structural_validator_agent_types import (
            StructuralValidatorAgent,
        )

        assert StructuralValidatorAgent is not None

    def test_inherits_from_sovereign_base(self):
        """Test class still inherits from SovereignBaseAgent."""
        from agentic_core.base_agents.sovereign_base_agent import SovereignBaseAgent
        from agentic_core.L5_safety.policy_engine.structural_validator_agent_types import (
            StructuralValidatorAgent,
        )

        assert issubclass(StructuralValidatorAgent, SovereignBaseAgent)

    def test_violations_property(self):
        """Test violations property exists."""
        from agentic_core.L5_safety.policy_engine.structural_validator_agent_types import (
            StructuralValidatorAgent,
            StructureConfig,
        )

        with patch("agentic_core.base_agents.SovereignBaseAgent.SovereignBaseAgent.__init__"):
            agent = object.__new__(StructuralValidatorAgent)
            agent._config = StructureConfig()
            agent._violations = []
            assert hasattr(agent, "violations")
            assert isinstance(agent.violations, list)

    def test_check_duplicates_method(self):
        """Test check_duplicates method exists."""
        from agentic_core.L5_safety.policy_engine.structural_validator_agent_types import (
            StructuralValidatorAgent,
            StructureConfig,
        )

        with patch("agentic_core.base_agents.SovereignBaseAgent.SovereignBaseAgent.__init__"):
            agent = object.__new__(StructuralValidatorAgent)
            agent._config = StructureConfig()
            agent._violations = []
            assert hasattr(agent, "check_duplicates")
            assert callable(agent.check_duplicates)


class TestValidationFunctionality:
    """Tests for actual validation functionality."""

    @pytest.fixture
    def agent(self):
        """Create StructuralValidatorAgent instance."""
        with patch("agentic_core.base_agents.SovereignBaseAgent.SovereignBaseAgent.__init__"):
            from agentic_core.L5_safety.policy_engine.structural_validator_agent_types import (
                StructuralValidatorAgent,
                StructureConfig,
            )

            agent = object.__new__(StructuralValidatorAgent)
            agent._config = StructureConfig()
            agent.project_root = Path.cwd()
            agent._lock = None
            agent._violations = []
            agent.LAYER_ORDER = {"L0": 0, "L1": 1, "L2": 2, "L3": 3, "L4": 4, "L5": 5, "L6": 6}
            return agent

    def test_extract_layer_from_path(self, agent):
        """Test layer extraction from file path."""
        path = Path("/project/agentic_core/L5_safety/validators/TestAgent.py")
        layer = agent._extract_layer(path)
        assert layer == "L5"

    def test_extract_layer_no_layer(self, agent):
        """Test layer extraction returns None for non-layer path."""
        path = Path("/project/apps_rg/engines/TestAgent.py")
        layer = agent._extract_layer(path)
        assert layer is None

    def test_validate_file_nonexistent(self, agent):
        """Test validate_file with nonexistent file."""
        result = agent.validate_file(Path("/nonexistent/file.py"))
        assert result == []

    def test_violations_initially_empty(self, agent):
        """Test violations list is initially empty."""
        assert agent.violations == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
