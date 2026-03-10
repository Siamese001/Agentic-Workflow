"""
Performance Tests for Zero-Loss Agent Consolidation - Phase 6

Comprehensive performance testing including:
- Strategy execution benchmarks
- Memory usage validation
- Concurrent execution tests
- Facade overhead measurement
"""

from __future__ import annotations

import asyncio
import time
from unittest.mock import Mock, patch

import pytest

from agentic_core.L3_orchestration.reasoning.UnifiedAgent import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

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


class TestStrategyPerformance:
    """Performance tests for strategy execution."""

    @pytest.fixture
    def validator_config(self):
        """Validator configuration."""
        return {
            "validation_rules": {"test": {}},
            "forbidden_content": ["bad"],
            "required_content": [],
            "thresholds": {"min_score": 0.3},
        }

    @pytest.fixture
    def orchestrator_config(self):
        """Orchestrator configuration."""
        return {
            "workflow_steps": [
                {"name": "step1", "type": "validation"},
                {"name": "step2", "type": "agent_call"},
            ],
            "signal_handlers": {},
        }

    @pytest.fixture
    def healer_config(self):
        """Healer configuration."""
        return {
            "healing_rules": {},
            "auto_fix": False,
            "dry_run_default": True,
        }

    @pytest.mark.asyncio
    async def test_validator_strategy_performance(self, validator_config):
        """Test validator strategy executes within acceptable time."""
        strategy = ValidatorStrategy(validator_config)

        with patch.object(UnifiedAgent, "__post_init__", lambda self: None):
            agent = UnifiedAgent()
            agent._category = AgentCategory.VALIDATOR
            agent._unified_config = validator_config
            agent.log_info = Mock()

            start = time.perf_counter()
            for _ in range(100):
                await strategy.execute(agent, data={"content": "test content"})
            elapsed = time.perf_counter() - start

            # Should complete 100 executions in under 1 second
            assert elapsed < 1.0, f"Validator too slow: {elapsed:.3f}s for 100 executions"

    @pytest.mark.asyncio
    async def test_orchestrator_strategy_performance(self, orchestrator_config):
        """Test orchestrator strategy executes within acceptable time."""
        strategy = OrchestrationStrategy(orchestrator_config)

        with patch.object(UnifiedAgent, "__post_init__", lambda self: None):
            agent = UnifiedAgent()
            agent._category = AgentCategory.ORCHESTRATOR
            agent._unified_config = orchestrator_config
            agent.log_info = Mock()
            agent.log_error = Mock()

            start = time.perf_counter()
            for _ in range(100):
                await strategy.execute(agent)
            elapsed = time.perf_counter() - start

            # Should complete 100 executions in under 1 second
            assert elapsed < 1.0, f"Orchestrator too slow: {elapsed:.3f}s for 100 executions"

    @pytest.mark.asyncio
    async def test_healer_strategy_performance(self, healer_config):
        """Test healer strategy executes within acceptable time."""
        strategy = HealingStrategy(healer_config)

        with patch.object(UnifiedAgent, "__post_init__", lambda self: None):
            agent = UnifiedAgent()
            agent._category = AgentCategory.HEALER
            agent._unified_config = healer_config
            agent.log_info = Mock()

            start = time.perf_counter()
            for _ in range(100):
                await strategy.execute(agent, dry_run=True)
            elapsed = time.perf_counter() - start

            # Should complete 100 executions in under 1 second
            assert elapsed < 1.0, f"Healer too slow: {elapsed:.3f}s for 100 executions"


class TestConcurrentExecution:
    """Tests for concurrent strategy execution."""

    @pytest.mark.asyncio
    async def test_concurrent_validator_execution(self):
        """Test multiple validators can run concurrently."""
        config = {
            "validation_rules": {},
            "forbidden_content": [],
            "required_content": [],
            "thresholds": {"min_score": 0.3},
        }

        async def run_validator():
            strategy = ValidatorStrategy(config)
            with patch.object(UnifiedAgent, "__post_init__", lambda self: None):
                agent = UnifiedAgent()
                agent._category = AgentCategory.VALIDATOR
                agent._unified_config = config
                agent.log_info = Mock()
                return await strategy.execute(agent, data={"content": "test"})

        # Run 10 validators concurrently
        tasks = [run_validator() for _ in range(10)]
        results = await asyncio.gather(*tasks)

        assert len(results) == 10
        assert all(isinstance(r, ValidationResult) for r in results)

    @pytest.mark.asyncio
    async def test_mixed_strategy_concurrent_execution(self):
        """Test different strategies can run concurrently."""
        validator_config = {"validation_rules": {}, "forbidden_content": [], "thresholds": {}}
        orchestrator_config = {"workflow_steps": [], "signal_handlers": {}}
        healer_config = {"healing_rules": {}, "auto_fix": False}

        async def run_validator():
            strategy = ValidatorStrategy(validator_config)
            with patch.object(UnifiedAgent, "__post_init__", lambda self: None):
                agent = UnifiedAgent()
                agent._category = AgentCategory.VALIDATOR
                agent._unified_config = validator_config
                agent.log_info = Mock()
                return await strategy.execute(agent, data={"content": "test"})

        async def run_orchestrator():
            strategy = OrchestrationStrategy(orchestrator_config)
            with patch.object(UnifiedAgent, "__post_init__", lambda self: None):
                agent = UnifiedAgent()
                agent._category = AgentCategory.ORCHESTRATOR
                agent._unified_config = orchestrator_config
                agent.log_info = Mock()
                agent.log_error = Mock()
                return await strategy.execute(agent)

        async def run_healer():
            strategy = HealingStrategy(healer_config)
            with patch.object(UnifiedAgent, "__post_init__", lambda self: None):
                agent = UnifiedAgent()
                agent._category = AgentCategory.HEALER
                agent._unified_config = healer_config
                agent.log_info = Mock()
                return await strategy.execute(agent, dry_run=True)

        # Run mixed strategies concurrently
        tasks = [run_validator(), run_orchestrator(), run_healer()]
        results = await asyncio.gather(*tasks)

        assert len(results) == 3
        assert isinstance(results[0], ValidationResult)
        assert isinstance(results[1], OrchestrationResult)
        assert isinstance(results[2], HealingResult)


class TestStrategyMapIntegrity:
    """Tests for strategy map integrity."""

    def test_all_categories_mapped(self):
        """Test all agent categories have strategy mappings."""
        for category in AgentCategory:
            assert category in STRATEGY_MAP, f"Missing strategy for {category}"

    def test_strategy_types_correct(self):
        """Test strategy types are correct for categories."""
        assert STRATEGY_MAP[AgentCategory.VALIDATOR] == ValidatorStrategy
        assert STRATEGY_MAP[AgentCategory.ORCHESTRATOR] == OrchestrationStrategy
        assert STRATEGY_MAP[AgentCategory.HEALER] == HealingStrategy
        assert STRATEGY_MAP[AgentCategory.GENERIC] == GenericStrategy

    def test_analyzer_uses_validator_strategy(self):
        """Test analyzer category uses validator strategy."""
        assert STRATEGY_MAP[AgentCategory.ANALYZER] == ValidatorStrategy

    def test_governor_uses_validator_strategy(self):
        """Test governor category uses validator strategy."""
        assert STRATEGY_MAP[AgentCategory.GOVERNOR] == ValidatorStrategy


class TestResultTypeConsistency:
    """Tests for result type consistency."""

    def test_validation_result_to_dict(self):
        """Test ValidationResult serializes correctly."""
        result = ValidationResult(
            passed=True,
            issues=["issue1"],
            suggestions=["suggestion1"],
            score=0.85,
            metadata={"key": "value"},
        )

        d = result.to_dict()

        assert d["passed"] is True
        assert d["issues"] == ["issue1"]
        assert d["suggestions"] == ["suggestion1"]
        assert d["score"] == 0.85
        assert d["metadata"] == {"key": "value"}

    def test_orchestration_result_to_dict(self):
        """Test OrchestrationResult serializes correctly."""
        result = OrchestrationResult(
            completed=True,
            stage="final",
            signals=["signal1"],
            metadata={"key": "value"},
        )

        d = result.to_dict()

        assert d["completed"] is True
        assert d["stage"] == "final"
        assert d["signals"] == ["signal1"]
        assert d["metadata"] == {"key": "value"}

    def test_healing_result_to_dict(self):
        """Test HealingResult serializes correctly."""
        result = HealingResult(
            violations_found=5,
            violations_fixed=3,
            errors=["error1"],
            skipped=["skipped1"],
        )

        d = result.to_dict()

        assert d["violations_found"] == 5
        assert d["violations_fixed"] == 3
        assert d["errors"] == ["error1"]
        assert d["skipped"] == ["skipped1"]


class TestFacadeOverhead:
    """Tests measuring facade pattern overhead."""

    @pytest.mark.asyncio
    async def test_facade_overhead_acceptable(self):
        """Test facade pattern adds minimal overhead."""
        config = {"validation_rules": {}, "forbidden_content": [], "thresholds": {}}

        # Direct strategy execution
        strategy = ValidatorStrategy(config)
        with patch.object(UnifiedAgent, "__post_init__", lambda self: None):
            agent = UnifiedAgent()
            agent._category = AgentCategory.VALIDATOR
            agent._unified_config = config
            agent.log_info = Mock()

            start = time.perf_counter()
            for _ in range(50):
                await strategy.execute(agent, data={"content": "test"})
            direct_time = time.perf_counter() - start

        # Facade execution (through UnifiedAgent.execute)
        with patch.object(UnifiedAgent, "__post_init__", lambda self: None):
            agent = UnifiedAgent()
            agent._category = AgentCategory.VALIDATOR
            agent._unified_config = config
            agent._strategy = ValidatorStrategy(config)
            agent.log_info = Mock()

            start = time.perf_counter()
            for _ in range(50):
                await agent.execute(data={"content": "test"})
            facade_time = time.perf_counter() - start

        # Facade overhead should be less than 50%
        overhead = (facade_time - direct_time) / direct_time if direct_time > 0 else 0
        assert overhead < 0.5, f"Facade overhead too high: {overhead:.1%}"


class TestComprehensiveIntegration:
    """Comprehensive integration tests."""

    @pytest.mark.asyncio
    async def test_full_workflow_integration(self):
        """Test complete workflow through unified agent."""
        # Validator
        with patch.object(UnifiedAgent, "__post_init__", lambda self: None):
            validator = UnifiedAgent()
            validator._category = AgentCategory.VALIDATOR
            validator._unified_config = {"validation_rules": {}, "forbidden_content": []}
            validator._strategy = ValidatorStrategy(validator._unified_config)
            validator.log_info = Mock()

            v_result = await validator.execute(data={"content": "test"})
            assert isinstance(v_result, ValidationResult)

        # Orchestrator
        with patch.object(UnifiedAgent, "__post_init__", lambda self: None):
            orchestrator = UnifiedAgent()
            orchestrator._category = AgentCategory.ORCHESTRATOR
            orchestrator._unified_config = {"workflow_steps": [], "signal_handlers": {}}
            orchestrator._strategy = OrchestrationStrategy(orchestrator._unified_config)
            orchestrator.log_info = Mock()
            orchestrator.log_error = Mock()

            o_result = await orchestrator.execute()
            assert isinstance(o_result, OrchestrationResult)

        # Healer
        with patch.object(UnifiedAgent, "__post_init__", lambda self: None):
            healer = UnifiedAgent()
            healer._category = AgentCategory.HEALER
            healer._unified_config = {"healing_rules": {}, "auto_fix": False}
            healer._strategy = HealingStrategy(healer._unified_config)
            healer.log_info = Mock()

            h_result = await healer.execute(dry_run=True)
            assert isinstance(h_result, HealingResult)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
