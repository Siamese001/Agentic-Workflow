"""
Unit Tests for ComplexityAnalyzerAgent Facade - Phase 5

Tests the facade conversion of ComplexityAnalyzerAgent including:
- Legacy signature compatibility
- ComplexityAnalyzerStrategy functionality
- Complexity analysis preservation
- Return type consistency
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

import pytest

from agentic_core.L3_orchestration.reasoning.UnifiedAgent import ValidationResult


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

class TestComplexityAnalyzerStrategy:
    """Tests for ComplexityAnalyzerStrategy."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return {
            "max_cyclomatic_complexity": 10,
            "max_function_length": 50,
            "max_arguments": 6,
        }

    @pytest.fixture
    def strategy(self, config):
        """Create ComplexityAnalyzerStrategy instance."""
        from agentic_core.L5_safety.reasoning.ComplexityAnalyzerAgent import (
            ComplexityAnalyzerStrategy,
        )

        return ComplexityAnalyzerStrategy(config)

    def test_initialization(self, strategy, config):
        """Test strategy initialization."""
        assert strategy.max_cyclomatic_complexity == 10
        assert strategy.max_function_length == 50
        assert strategy.max_arguments == 6

    @pytest.mark.asyncio
    async def test_execute_returns_validation_result(self, strategy):
        """Test execute returns ValidationResult."""
        mock_agent = Mock()
        mock_agent.log_info = Mock()

        result = await strategy.execute(mock_agent)

        assert isinstance(result, ValidationResult)
        assert result.passed is True


class TestComplexityAnalyzerAgentFacade:
    """Tests for ComplexityAnalyzerAgent facade."""

    @pytest.fixture
    def agent(self):
        """Create ComplexityAnalyzerAgent instance."""
        from agentic_core.L5_safety.reasoning.ComplexityAnalyzerAgent import (
            ComplexityAnalyzerAgent,
        )

        return ComplexityAnalyzerAgent()

    def test_initialization(self, agent):
        """Test agent initialization."""
        assert agent.project_root is not None
        assert agent._complexity_config is not None
        assert agent._violations == []

    def test_unified_strategy_initialized(self, agent):
        """Test unified strategy is initialized."""
        assert agent._unified_strategy is not None
        from agentic_core.L5_safety.reasoning.ComplexityAnalyzerAgent import (
            ComplexityAnalyzerStrategy,
        )

        assert isinstance(agent._unified_strategy, ComplexityAnalyzerStrategy)

    def test_analyze_repository_method_exists(self, agent):
        """Test analyze_repository method exists."""
        assert hasattr(agent, "analyze_repository")
        assert callable(agent.analyze_repository)

    def test_analyze_file_method_exists(self, agent):
        """Test analyze_file method exists."""
        assert hasattr(agent, "analyze_file")
        assert callable(agent.analyze_file)

    def test_heal_repository_method_exists(self, agent):
        """Test heal_repository method exists."""
        assert hasattr(agent, "heal_repository")
        assert callable(agent.heal_repository)

    def test_heal_method_exists(self, agent):
        """Test heal method exists."""
        assert hasattr(agent, "heal")
        assert callable(agent.heal)

    def test_heal_returns_proper_structure(self, agent):
        """Test heal returns proper dict structure."""
        violation = {"type": "CYCLOMATIC", "path": "/test.py"}
        result = agent.heal(violation)

        assert isinstance(result, dict)
        assert "violations_fixed" in result
        assert "violations_found" in result
        assert "skipped" in result


class TestComplexityTypes:
    """Tests for complexity type dataclasses."""

    def test_complexity_violation_dataclass(self):
        """Test ComplexityViolation dataclass exists."""
        from agentic_core.L5_safety.reasoning.ComplexityAnalyzerAgent import (
            ComplexityViolation,
        )

        violation = ComplexityViolation(
            file_path=Path("/test/file.py"),
            function_name="complex_function",
            line_number=10,
            complexity=15,
            max_allowed=10,
            type="CYCLOMATIC",
            severity="CRITICAL",
        )

        assert violation.function_name == "complex_function"
        assert violation.complexity == 15

    def test_complexity_config_dataclass(self):
        """Test ComplexityConfig dataclass exists."""
        from agentic_core.L5_safety.reasoning.ComplexityAnalyzerAgent import (
            ComplexityConfig,
        )

        config = ComplexityConfig()

        assert config.max_cyclomatic_complexity == 10
        assert config.max_function_length == 50
        assert config.max_arguments == 6
        assert config.ignore_tests is True


class TestLegacyCompatibility:
    """Tests ensuring 100% legacy compatibility."""

    def test_import_compatibility(self):
        """Test original import still works."""
        from agentic_core.L5_safety.reasoning.ComplexityAnalyzerAgent import (
            ComplexityAnalyzerAgent,
        )

        assert ComplexityAnalyzerAgent is not None

    def test_inherits_from_sovereign_base(self):
        """Test class still inherits from SovereignBaseAgent."""
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
        from agentic_core.L5_safety.reasoning.ComplexityAnalyzerAgent import (
            ComplexityAnalyzerAgent,
        )

        assert issubclass(ComplexityAnalyzerAgent, SovereignBaseAgent)

    def test_calculate_complexity_method(self):
        """Test _calculate_complexity method exists."""
        from agentic_core.L5_safety.reasoning.ComplexityAnalyzerAgent import (
            ComplexityAnalyzerAgent,
        )

        agent = ComplexityAnalyzerAgent()
        assert hasattr(agent, "_calculate_complexity")
        assert callable(agent._calculate_complexity)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
