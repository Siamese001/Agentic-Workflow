"""
Unit Tests for CodeHealerAgent Facade - Phase 4

Tests the facade conversion of CodeHealerAgent including:
- Legacy signature compatibility
- CodeHealingStrategy functionality
- Healing action preservation
- Return type consistency
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from agentic_core.L3_orchestration.reasoning.UnifiedAgent import HealingResult
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_code_healer_facade")
_emit_applies_guardrail("p0", "test_code_healer_facade", "p0_governance")
_emit_reads_policy_state("p0", "test_code_healer_facade", "policy_binding")
_emit_snapshots_state("p0", "test_code_healer_facade", "state_snapshot")
emit_replay_key("p0", "test_code_healer_facade")
emit_determinism_digest("p0", "test_code_healer_facade")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

class TestCodeHealingStrategy:
    """Tests for CodeHealingStrategy."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return {
            "enable_canon": True,
            "enable_import": True,
            "enable_structural": True,
            "dry_run": True,
        }

    @pytest.fixture
    def strategy(self, config):
        """Create CodeHealingStrategy instance."""
        from agentic_core.L5_safety.reasoning.CodeHealerAgent import (
            CodeHealingStrategy,
        )

        return CodeHealingStrategy(config)

    def test_initialization(self, strategy, config):
        """Test strategy initialization."""
        assert strategy.enable_canon is True
        assert strategy.enable_import is True
        assert strategy.enable_structural is True

    @pytest.mark.asyncio
    async def test_execute_returns_healing_result(self, strategy):
        """Test execute returns HealingResult."""
        mock_agent = Mock()
        mock_agent.log_info = Mock()

        result = await strategy.execute(mock_agent, dry_run=True)

        assert isinstance(result, HealingResult)
        assert result.violations_found >= 0
        assert result.violations_fixed >= 0


class TestCodeHealerAgentFacade:
    """Tests for CodeHealerAgent facade."""

    @pytest.fixture
    def agent(self):
        """Create CodeHealerAgent instance."""
        with patch("agentic_core.base_agents.SovereignBaseAgent.SovereignBaseAgent.__init__"):
            from agentic_core.L5_safety.reasoning.CodeHealerAgent import (
                CodeHealerAgent,
            )

            agent = CodeHealerAgent()
            return agent

    def test_initialization(self, agent):
        """Test agent initialization."""
        assert agent.project_root is not None
        assert agent._agent_config is not None
        assert agent._actions == []

    def test_unified_strategy_initialized(self, agent):
        """Test unified strategy is initialized."""
        assert agent._unified_strategy is not None
        from agentic_core.L5_safety.reasoning.CodeHealerAgent import (
            CodeHealingStrategy,
        )

        assert isinstance(agent._unified_strategy, CodeHealingStrategy)

    def test_heal_repository_signature(self, agent):
        """Test heal_repository has correct signature."""
        import inspect

        sig = inspect.signature(agent.heal_repository)
        params = list(sig.parameters.keys())

        assert "dry_run" in params
        assert "execute" in params

    def test_heal_repository_returns_dict(self, agent):
        """Test heal_repository returns proper dict structure."""
        result = agent.heal_repository(dry_run=True)

        assert isinstance(result, dict)
        assert "violations_found" in result
        assert "violations_fixed" in result
        assert "errors" in result

    def test_heal_method_exists(self, agent):
        """Test heal method exists."""
        assert hasattr(agent, "heal")
        assert callable(agent.heal)

    def test_heal_all_method_exists(self, agent):
        """Test heal_all method exists."""
        assert hasattr(agent, "heal_all")
        assert callable(agent.heal_all)

    def test_heal_imports_method_exists(self, agent):
        """Test heal_imports method exists."""
        assert hasattr(agent, "heal_imports")
        assert callable(agent.heal_imports)

    def test_heal_canon_method_exists(self, agent):
        """Test heal_canon method exists."""
        assert hasattr(agent, "heal_canon")
        assert callable(agent.heal_canon)

    def test_heal_structural_method_exists(self, agent):
        """Test heal_structural method exists."""
        assert hasattr(agent, "heal_structural")
        assert callable(agent.heal_structural)


class TestHealingTypes:
    """Tests for healing type enums and dataclasses."""

    def test_healing_type_enum(self):
        """Test HealingType enum exists."""
        from agentic_core.L5_safety.reasoning.CodeHealerAgent import HealingType

        assert hasattr(HealingType, "CANON")
        assert hasattr(HealingType, "IMPORT")
        assert hasattr(HealingType, "STRUCTURAL")

    def test_healing_action_dataclass(self):
        """Test HealingAction dataclass exists."""
        from agentic_core.L5_safety.reasoning.CodeHealerAgent import HealingAction

        action = HealingAction(
            healing_type="CANON",
            file_path=Path("/test/file.py"),
            line_number=1,
            description="Test action",
            old_code="old",
            new_code="new",
        )

        assert action.healing_type == "CANON"
        assert action.applied is False

    def test_healer_config_dataclass(self):
        """Test HealerConfig dataclass exists."""
        from agentic_core.L5_safety.reasoning.CodeHealerAgent import HealerConfig

        config = HealerConfig()

        assert config.enable_canon is True
        assert config.enable_import is True
        assert config.enable_structural is True
        assert config.dry_run is True


class TestLegacyCompatibility:
    """Tests ensuring 100% legacy compatibility."""

    def test_import_compatibility(self):
        """Test original import still works."""
        from agentic_core.L5_safety.reasoning.CodeHealerAgent import CodeHealerAgent

        assert CodeHealerAgent is not None

    def test_inherits_from_sovereign_base(self):
        """Test class still inherits from SovereignBaseAgent."""
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
        from agentic_core.L5_safety.reasoning.CodeHealerAgent import CodeHealerAgent

        assert issubclass(CodeHealerAgent, SovereignBaseAgent)

    def test_factory_functions_exist(self):
        """Test factory functions exist."""
        from agentic_core.L5_safety.reasoning.CodeHealerAgent import (
            create_legacy_canon_healer,
            create_legacy_import_healer,
        )

        assert callable(create_legacy_canon_healer)
        assert callable(create_legacy_import_healer)

    def test_stdlib_modules_constant(self):
        """Test STDLIB_MODULES constant exists."""
        from agentic_core.L5_safety.reasoning.CodeHealerAgent import CodeHealerAgent

        assert hasattr(CodeHealerAgent, "STDLIB_MODULES")
        assert isinstance(CodeHealerAgent.STDLIB_MODULES, set)
        assert "os" in CodeHealerAgent.STDLIB_MODULES

    def test_atomic_write_method(self):
        """Test atomic_write method exists."""
        from agentic_core.L5_safety.reasoning.CodeHealerAgent import CodeHealerAgent

        with patch("agentic_core.base_agents.SovereignBaseAgent.SovereignBaseAgent.__init__"):
            agent = CodeHealerAgent()
            assert hasattr(agent, "atomic_write")
            assert callable(agent.atomic_write)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
