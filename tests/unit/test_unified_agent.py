"""
Unit Tests for UnifiedAgent Core - Phase 1.1

Tests the core UnifiedAgent implementation including:
- AgentCategory enum
- Result types (ValidationResult, OrchestrationResult, HealingResult)
- Strategy pattern implementations
- UnifiedAgent class functionality
"""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from agentic_core.L3_orchestration.reasoning.UnifiedAgent import (
    STRATEGY_MAP,
    AgentCategory,
    GenericStrategy,
    HealingResult,
    HealingStrategy,
    OrchestrationResult,
    OrchestrationStrategy,
    UnifiedAgent,
    ValidationResult,
    ValidatorStrategy,
)


class TestAgentCategory:
    """Tests for AgentCategory enum."""

    def test_category_values(self):
        """Test all category values are defined correctly."""
        assert AgentCategory.VALIDATOR.value == "validator"
        assert AgentCategory.ORCHESTRATOR.value == "orchestrator"
        assert AgentCategory.HEALER.value == "healer"
        assert AgentCategory.GENERIC.value == "generic"
        assert AgentCategory.EXECUTOR.value == "executor"
        assert AgentCategory.MONITOR.value == "monitor"
        assert AgentCategory.ANALYZER.value == "analyzer"
        assert AgentCategory.GOVERNOR.value == "governor"

    def test_category_count(self):
        """Test expected number of categories."""
        assert len(AgentCategory) == 8


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_creation_minimal(self):
        """Test minimal ValidationResult creation."""
        result = ValidationResult(passed=True, issues=[], suggestions=[])
        assert result.passed is True
        assert result.issues == []
        assert result.suggestions == []
        assert result.score is None
        assert result.metadata is None

    def test_creation_full(self):
        """Test full ValidationResult creation."""
        result = ValidationResult(
            passed=False,
            issues=["issue1", "issue2"],
            suggestions=["suggestion1"],
            score=0.75,
            metadata={"key": "value"},
        )
        assert result.passed is False
        assert len(result.issues) == 2
        assert len(result.suggestions) == 1
        assert result.score == 0.75
        assert result.metadata == {"key": "value"}

    def test_to_dict(self):
        """Test ValidationResult to_dict conversion."""
        result = ValidationResult(
            passed=True,
            issues=["issue1"],
            suggestions=["suggestion1"],
            score=0.9,
            metadata={"test": True},
        )
        d = result.to_dict()
        assert d["passed"] is True
        assert d["issues"] == ["issue1"]
        assert d["suggestions"] == ["suggestion1"]
        assert d["score"] == 0.9
        assert d["metadata"] == {"test": True}


class TestOrchestrationResult:
    """Tests for OrchestrationResult dataclass."""

    def test_creation_minimal(self):
        """Test minimal OrchestrationResult creation."""
        result = OrchestrationResult(
            completed=True,
            stage="final",
            signals=[],
            artifacts=[],
            next_actions=[],
        )
        assert result.completed is True
        assert result.stage == "final"
        assert result.signals == []
        assert result.artifacts == []
        assert result.next_actions == []
        assert result.errors == []

    def test_creation_full(self):
        """Test full OrchestrationResult creation."""
        result = OrchestrationResult(
            completed=False,
            stage="validation",
            signals=["signal1", "signal2"],
            artifacts=[{"type": "report"}],
            next_actions=["retry"],
            errors=["error1"],
        )
        assert result.completed is False
        assert result.stage == "validation"
        assert len(result.signals) == 2
        assert len(result.artifacts) == 1
        assert len(result.next_actions) == 1
        assert len(result.errors) == 1

    def test_to_dict(self):
        """Test OrchestrationResult to_dict conversion."""
        result = OrchestrationResult(
            completed=True,
            stage="done",
            signals=["complete"],
            artifacts=[],
            next_actions=[],
            errors=[],
        )
        d = result.to_dict()
        assert d["completed"] is True
        assert d["stage"] == "done"
        assert d["signals"] == ["complete"]


class TestHealingResult:
    """Tests for HealingResult dataclass."""

    def test_creation_minimal(self):
        """Test minimal HealingResult creation."""
        result = HealingResult(
            violations_found=0,
            violations_fixed=0,
            errors=[],
            skipped=[],
        )
        assert result.violations_found == 0
        assert result.violations_fixed == 0
        assert result.errors == []
        assert result.skipped == []
        assert result.artifacts == []

    def test_creation_full(self):
        """Test full HealingResult creation."""
        result = HealingResult(
            violations_found=5,
            violations_fixed=3,
            errors=["error1"],
            skipped=["skip1", "skip2"],
            artifacts=[{"fixed": "file.py"}],
        )
        assert result.violations_found == 5
        assert result.violations_fixed == 3
        assert len(result.errors) == 1
        assert len(result.skipped) == 2
        assert len(result.artifacts) == 1

    def test_to_dict(self):
        """Test HealingResult to_dict conversion."""
        result = HealingResult(
            violations_found=10,
            violations_fixed=8,
            errors=[],
            skipped=["type1"],
        )
        d = result.to_dict()
        assert d["violations_found"] == 10
        assert d["violations_fixed"] == 8
        assert d["skipped"] == ["type1"]


class TestValidatorStrategy:
    """Tests for ValidatorStrategy."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return {
            "validation_rules": {
                "pattern_test": {
                    "type": "pattern_match",
                    "pattern": r"forbidden_pattern",
                },
                "keyword_test": {
                    "type": "keyword_check",
                    "keywords": ["python", "java", "react"],
                    "min_threshold": 2,
                },
            },
            "forbidden_content": ["bad_word"],
            "required_content": ["good_word"],
        }

    @pytest.fixture
    def strategy(self, config):
        """Create ValidatorStrategy instance."""
        return ValidatorStrategy(config)

    def test_initialization(self, strategy, config):
        """Test strategy initialization."""
        assert strategy.validation_rules == config["validation_rules"]
        assert strategy.forbidden_content == config["forbidden_content"]
        assert strategy.required_content == config["required_content"]

    @pytest.mark.asyncio
    async def test_execute_no_data(self, strategy):
        """Test execute with no data returns failure."""
        mock_agent = Mock()
        mock_agent._category = AgentCategory.VALIDATOR
        mock_agent.log_info = Mock()
        mock_agent.ctx = None

        result = await strategy.execute(mock_agent)

        assert isinstance(result, ValidationResult)
        assert result.passed is False
        assert "No target data available" in result.issues[0]

    @pytest.mark.asyncio
    async def test_execute_with_clean_data(self, strategy):
        """Test execute with clean data passes validation."""
        mock_agent = Mock()
        mock_agent._category = AgentCategory.VALIDATOR
        mock_agent.log_info = Mock()

        # Clean data with required content and keywords
        result = await strategy.execute(
            mock_agent,
            data={"content": "python java good_word experience"},
        )

        assert isinstance(result, ValidationResult)
        assert result.passed is True
        assert len(result.issues) == 0

    @pytest.mark.asyncio
    async def test_execute_with_forbidden_content(self, strategy):
        """Test execute detects forbidden content."""
        mock_agent = Mock()
        mock_agent._category = AgentCategory.VALIDATOR
        mock_agent.log_info = Mock()

        result = await strategy.execute(
            mock_agent,
            data={"content": "python java bad_word good_word"},
        )

        assert isinstance(result, ValidationResult)
        assert result.passed is False
        assert any("bad_word" in issue for issue in result.issues)

    @pytest.mark.asyncio
    async def test_execute_with_pattern_violation(self, strategy):
        """Test execute detects pattern violations."""
        mock_agent = Mock()
        mock_agent._category = AgentCategory.VALIDATOR
        mock_agent.log_info = Mock()

        result = await strategy.execute(
            mock_agent,
            data={"content": "python java forbidden_pattern good_word"},
        )

        assert isinstance(result, ValidationResult)
        assert result.passed is False
        assert any("pattern_test" in issue.lower() for issue in result.issues)

    def test_to_string_conversion(self, strategy):
        """Test _to_string handles various types."""
        assert strategy._to_string("hello") == "hello"
        assert strategy._to_string(["a", "b", "c"]) == "a b c"
        assert "key" in strategy._to_string({"key": "value"})
        assert strategy._to_string(123) == "123"

    def test_calculate_keyword_score(self, strategy):
        """Test keyword score calculation."""
        data = {"skills": "python javascript react"}
        reference = "Looking for python and react developer"

        score = strategy._calculate_keyword_score(data, reference)

        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0


class TestOrchestrationStrategy:
    """Tests for OrchestrationStrategy."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return {
            "workflow_steps": [
                {"name": "validate", "type": "validation"},
                {"name": "process", "type": "agent_call", "agent": "processor"},
                {"name": "complete", "type": "completion"},
            ],
            "signal_handlers": {
                "validation_completed": "continue",
                "validation_failed": "retry",
            },
        }

    @pytest.fixture
    def strategy(self, config):
        """Create OrchestrationStrategy instance."""
        return OrchestrationStrategy(config)

    def test_initialization(self, strategy, config):
        """Test strategy initialization."""
        assert len(strategy.workflow_steps) == 3
        assert strategy.signal_handlers == config["signal_handlers"]

    @pytest.mark.asyncio
    async def test_execute_complete_workflow(self, strategy):
        """Test execute completes all workflow steps."""
        mock_agent = Mock()
        mock_agent._category = AgentCategory.ORCHESTRATOR
        mock_agent.log_info = Mock()
        mock_agent.log_error = Mock()

        result = await strategy.execute(mock_agent)

        assert isinstance(result, OrchestrationResult)
        assert result.completed is True
        assert result.stage == "complete"
        assert "validation_completed" in result.signals
        assert "orchestration_completed" in result.signals

    @pytest.mark.asyncio
    async def test_execute_empty_workflow(self):
        """Test execute with empty workflow."""
        strategy = OrchestrationStrategy({"workflow_steps": []})
        mock_agent = Mock()
        mock_agent._category = AgentCategory.ORCHESTRATOR
        mock_agent.log_info = Mock()

        result = await strategy.execute(mock_agent)

        assert isinstance(result, OrchestrationResult)
        assert result.stage == "not_started"
        assert "start_workflow" in result.next_actions

    def test_determine_next_actions(self, strategy):
        """Test next action determination."""
        # Test with validation failure
        actions = strategy._determine_next_actions(["step1"], ["validation_failed"])
        assert "retry_validation" in actions

        # Test with incomplete workflow
        actions = strategy._determine_next_actions(["step1"], [])
        assert "continue_workflow" in actions

        # Test with no completed steps
        actions = strategy._determine_next_actions([], [])
        assert "start_workflow" in actions


class TestHealingStrategy:
    """Tests for HealingStrategy."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return {
            "healing_rules": {
                "test_rule": {
                    "type": "pattern_match",
                    "pattern": r"violation",
                    "severity": "high",
                },
            },
            "auto_fix": False,
            "dry_run_default": True,
        }

    @pytest.fixture
    def strategy(self, config):
        """Create HealingStrategy instance."""
        return HealingStrategy(config)

    def test_initialization(self, strategy, config):
        """Test strategy initialization."""
        assert strategy.healing_rules == config["healing_rules"]
        assert strategy.auto_fix is False
        assert strategy.dry_run_default is True

    @pytest.mark.asyncio
    async def test_execute_dry_run(self, strategy):
        """Test execute in dry run mode."""
        mock_agent = Mock()
        mock_agent._category = AgentCategory.HEALER
        mock_agent.log_info = Mock()

        result = await strategy.execute(mock_agent, dry_run=True)

        assert isinstance(result, HealingResult)
        assert result.violations_found >= 0
        assert result.violations_fixed == 0  # Dry run doesn't fix

    @pytest.mark.asyncio
    async def test_execute_with_auto_fix_disabled(self, strategy):
        """Test execute with auto_fix disabled."""
        mock_agent = Mock()
        mock_agent._category = AgentCategory.HEALER
        mock_agent.log_info = Mock()

        result = await strategy.execute(mock_agent, dry_run=False)

        assert isinstance(result, HealingResult)
        # With auto_fix disabled, nothing should be fixed
        assert result.violations_fixed == 0

    def test_scan_violations(self, strategy):
        """Test violation scanning."""
        mock_agent = Mock()
        violations = strategy._scan_violations(mock_agent)

        assert isinstance(violations, list)
        # Should find violations based on healing_rules
        assert len(violations) == 1
        assert violations[0]["type"] == "test_rule"

    def test_heal_method(self, strategy):
        """Test heal method returns proper structure."""
        mock_agent = Mock()
        violation = {"type": "test", "id": "123"}

        result = strategy.heal(mock_agent, violation)

        assert "status" in result
        assert "details" in result
        assert "artifacts" in result
        assert "errors" in result


class TestGenericStrategy:
    """Tests for GenericStrategy."""

    @pytest.fixture
    def strategy(self):
        """Create GenericStrategy instance."""
        return GenericStrategy({})

    @pytest.mark.asyncio
    async def test_execute(self, strategy):
        """Test generic execute."""
        mock_agent = Mock()
        mock_agent._category = AgentCategory.GENERIC
        mock_agent.log_info = Mock()

        result = await strategy.execute(mock_agent)

        assert isinstance(result, dict)
        assert result["status"] == "completed"
        assert result["category"] == "generic"


class TestStrategyMap:
    """Tests for STRATEGY_MAP configuration."""

    def test_all_categories_mapped(self):
        """Test all categories have strategy mappings."""
        for category in AgentCategory:
            assert category in STRATEGY_MAP

    def test_correct_strategy_types(self):
        """Test correct strategy types are mapped."""
        assert STRATEGY_MAP[AgentCategory.VALIDATOR] == ValidatorStrategy
        assert STRATEGY_MAP[AgentCategory.ORCHESTRATOR] == OrchestrationStrategy
        assert STRATEGY_MAP[AgentCategory.HEALER] == HealingStrategy
        assert STRATEGY_MAP[AgentCategory.GENERIC] == GenericStrategy


class TestUnifiedAgent:
    """Tests for UnifiedAgent class."""

    @pytest.fixture
    def mock_config_loader(self):
        """Mock the config loader."""
        with patch("agentic_core.base_agents.UnifiedAgent.UnifiedAgent._load_unified_config") as mock:
            mock.return_value = {
                "validation_rules": {},
                "forbidden_content": [],
                "required_content": [],
            }
            yield mock

    @pytest.fixture
    def mock_sovereign_init(self):
        """Mock SovereignBaseAgent initialization."""
        with patch.object(UnifiedAgent, "__post_init__", lambda self: None):
            yield

    def test_category_getter(self):
        """Test get_category method."""
        with patch.object(UnifiedAgent, "__post_init__", lambda self: None):
            agent = UnifiedAgent()
            agent._category = AgentCategory.VALIDATOR
            assert agent.get_category() == AgentCategory.VALIDATOR

    def test_config_getter(self):
        """Test get_config method."""
        with patch.object(UnifiedAgent, "__post_init__", lambda self: None):
            agent = UnifiedAgent()
            agent._unified_config = {"test": "value"}
            assert agent.get_config() == {"test": "value"}

    def test_strategy_getter(self):
        """Test get_strategy method."""
        with patch.object(UnifiedAgent, "__post_init__", lambda self: None):
            agent = UnifiedAgent()
            agent._category = AgentCategory.VALIDATOR
            agent._unified_config = {}
            agent._strategy = None

            strategy = agent.get_strategy()

            assert isinstance(strategy, ValidatorStrategy)

    def test_heal_method(self):
        """Test heal method delegates to strategy."""
        with patch.object(UnifiedAgent, "__post_init__", lambda self: None):
            agent = UnifiedAgent()
            agent._category = AgentCategory.HEALER
            agent._unified_config = {}
            agent._strategy = None

            violation = {"type": "test", "id": "123"}
            result = agent.heal(violation)

            assert "status" in result
            assert "details" in result

    def test_heal_repository_method(self):
        """Test heal_repository method delegates to strategy."""
        with patch.object(UnifiedAgent, "__post_init__", lambda self: None):
            agent = UnifiedAgent()
            agent._category = AgentCategory.HEALER
            agent._unified_config = {"healing_rules": {}, "auto_fix": False}
            agent._strategy = None

            result = agent.heal_repository(dry_run=True)

            assert "violations_found" in result
            assert "violations_fixed" in result


class TestUnifiedAgentIntegration:
    """Integration tests for UnifiedAgent with strategies."""

    @pytest.mark.asyncio
    async def test_validator_integration(self):
        """Test UnifiedAgent with ValidatorStrategy integration."""
        with patch.object(UnifiedAgent, "__post_init__", lambda self: None):
            agent = UnifiedAgent()
            agent._category = AgentCategory.VALIDATOR
            agent._unified_config = {
                "validation_rules": {},
                "forbidden_content": ["bad"],
                "required_content": [],
            }
            agent._strategy = ValidatorStrategy(agent._unified_config)
            agent.log_info = Mock()

            result = await agent.execute(data={"content": "good content"})

            assert isinstance(result, ValidationResult)
            assert result.passed is True

    @pytest.mark.asyncio
    async def test_orchestrator_integration(self):
        """Test UnifiedAgent with OrchestrationStrategy integration."""
        with patch.object(UnifiedAgent, "__post_init__", lambda self: None):
            agent = UnifiedAgent()
            agent._category = AgentCategory.ORCHESTRATOR
            agent._unified_config = {
                "workflow_steps": [
                    {"name": "step1", "type": "validation"},
                ],
                "signal_handlers": {},
            }
            agent._strategy = OrchestrationStrategy(agent._unified_config)
            agent.log_info = Mock()
            agent.log_error = Mock()

            result = await agent.execute()

            assert isinstance(result, OrchestrationResult)
            assert result.completed is True

    @pytest.mark.asyncio
    async def test_healer_integration(self):
        """Test UnifiedAgent with HealingStrategy integration."""
        with patch.object(UnifiedAgent, "__post_init__", lambda self: None):
            agent = UnifiedAgent()
            agent._category = AgentCategory.HEALER
            agent._unified_config = {
                "healing_rules": {},
                "auto_fix": False,
                "dry_run_default": True,
            }
            agent._strategy = HealingStrategy(agent._unified_config)
            agent.log_info = Mock()

            result = await agent.execute(dry_run=True)

            assert isinstance(result, HealingResult)
            assert result.violations_fixed == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
