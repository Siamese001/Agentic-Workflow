"""
Unit Tests for StructureHealerAgent Facade - Phase 1

Tests the facade conversion of StructureHealerAgent including:
- Legacy signature compatibility
- StructureHealingStrategy functionality
- Healing action preservation
- Return type consistency
"""

from __future__ import annotations

import pytest
from pathlib import Path
from unittest.mock import Mock

from agentic_core.base_agents.UnifiedAgent import (
    HealingResult,
    StructureHealingStrategy,
)


class TestStructureHealingStrategy:
    """Tests for StructureHealingStrategy."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return {
            "enable_gravity": True,
            "enable_hierarchy": True,
            "enable_naming": True,
            "enable_territory": True,
            "dry_run": True,
        }

    @pytest.fixture
    def strategy(self, config):
        """Create StructureHealingStrategy instance."""
        return StructureHealingStrategy(config)

    def test_initialization(self, strategy, config):
        """Test strategy initialization."""
        assert strategy.enable_gravity is True
        assert strategy.enable_hierarchy is True
        assert strategy.enable_naming is True
        assert strategy.enable_territory is True
        assert strategy.dry_run is True

    def test_initialization_with_disabled_features(self):
        """Test strategy initialization with disabled features."""
        config = {
            "enable_gravity": False,
            "enable_hierarchy": False,
            "enable_naming": True,
            "enable_territory": False,
            "dry_run": False,
        }
        strategy = StructureHealingStrategy(config)

        assert strategy.enable_gravity is False
        assert strategy.enable_hierarchy is False
        assert strategy.enable_naming is True
        assert strategy.enable_territory is False
        assert strategy.dry_run is False

    @pytest.mark.asyncio
    async def test_execute_returns_healing_result(self, strategy):
        """Test execute returns HealingResult."""
        mock_agent = Mock()
        mock_agent.log_info = Mock()

        result = await strategy.execute(mock_agent, dry_run=True)

        assert isinstance(result, HealingResult)
        assert result.violations_found >= 0
        assert result.violations_fixed >= 0

    @pytest.mark.asyncio
    async def test_execute_with_file_path(self, strategy):
        """Test execute with file_path parameter."""
        mock_agent = Mock()
        mock_agent.log_info = Mock()
        mock_agent.heal_all = Mock(return_value=[])

        result = await strategy.execute(mock_agent, file_path="/test/file.py", dry_run=True)

        assert isinstance(result, HealingResult)

    def test_heal_repository_returns_dict(self, strategy):
        """Test heal_repository returns proper dict structure."""
        mock_agent = Mock()
        mock_agent.heal_all = Mock(return_value=[])

        result = strategy.heal_repository(mock_agent, dry_run=True, execute=False)

        assert isinstance(result, dict)
        assert "violations_found" in result
        assert "violations_fixed" in result
        assert "errors" in result


class TestStructureHealerAgentFacade:
    """Tests for StructureHealerAgent facade."""

    @pytest.fixture
    def agent(self):
        """Create StructureHealerAgent instance."""
        from agentic_core.L5_safety.policy_engine.structure_healer_agent_types import (
            StructureHealerAgent,
        )

        return StructureHealerAgent()

    def test_initialization(self, agent):
        """Test agent initialization."""
        assert agent.project_root is not None
        assert agent._agent_config is not None
        assert agent._actions == []

    def test_unified_strategy_initialized(self, agent):
        """Test unified strategy is initialized."""
        assert agent._unified_strategy is not None
        assert isinstance(agent._unified_strategy, StructureHealingStrategy)

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
        assert "violations" in result or "violations_found" in result

    def test_heal_method_exists(self, agent):
        """Test heal method exists."""
        assert hasattr(agent, "heal")
        assert callable(agent.heal)

    def test_heal_all_method_exists(self, agent):
        """Test heal_all method exists."""
        assert hasattr(agent, "heal_all")
        assert callable(agent.heal_all)

    def test_heal_naming_method_exists(self, agent):
        """Test heal_naming method exists."""
        assert hasattr(agent, "heal_naming")
        assert callable(agent.heal_naming)

    def test_heal_gravity_method_exists(self, agent):
        """Test heal_gravity method exists."""
        assert hasattr(agent, "heal_gravity")
        assert callable(agent.heal_gravity)

    def test_heal_territory_method_exists(self, agent):
        """Test heal_territory method exists."""
        assert hasattr(agent, "heal_territory")
        assert callable(agent.heal_territory)

    def test_get_actions_method_exists(self, agent):
        """Test get_actions method exists."""
        assert hasattr(agent, "get_actions")
        assert callable(agent.get_actions)

    def test_layer_order_constant(self, agent):
        """Test LAYER_ORDER constant exists."""
        assert hasattr(agent, "LAYER_ORDER")
        assert isinstance(agent.LAYER_ORDER, dict)
        assert "L0" in agent.LAYER_ORDER
        assert "L5" in agent.LAYER_ORDER


class TestStructureHealingTypes:
    """Tests for structure healing type enums and dataclasses."""

    def test_structure_healing_type_enum(self):
        """Test StructureHealingType enum exists."""
        from agentic_core.L5_safety.policy_engine.structure_healer_agent_types import (
            StructureHealingType,
        )

        assert hasattr(StructureHealingType, "GRAVITY")
        assert hasattr(StructureHealingType, "HIERARCHY")
        assert hasattr(StructureHealingType, "NAMING")
        assert hasattr(StructureHealingType, "TERRITORY")
        assert hasattr(StructureHealingType, "BLUEPRINT")

    def test_structure_healing_action_dataclass(self):
        """Test StructureHealingAction dataclass exists."""
        from agentic_core.L5_safety.policy_engine.structure_healer_agent_types import (
            StructureHealingAction,
            StructureHealingType,
        )

        action = StructureHealingAction(
            healing_type=StructureHealingType.NAMING,
            file_path=Path("/test/file.py"),
            description="Test action",
            old_value="old",
            new_value="new",
        )

        assert action.healing_type == StructureHealingType.NAMING
        assert action.applied is False

    def test_structure_healer_config_dataclass(self):
        """Test StructureHealerConfig dataclass exists."""
        from agentic_core.L5_safety.policy_engine.structure_healer_agent_types import (
            StructureHealerConfig,
        )

        config = StructureHealerConfig()

        assert config.enable_gravity is True
        assert config.enable_hierarchy is True
        assert config.enable_naming is True
        assert config.enable_territory is True
        assert config.dry_run is True


class TestLegacyCompatibility:
    """Tests ensuring 100% legacy compatibility."""

    def test_import_compatibility(self):
        """Test original import still works."""
        from agentic_core.L5_safety.policy_engine.structure_healer_agent_types import (
            StructureHealerAgent,
        )

        assert StructureHealerAgent is not None

    def test_inherits_from_sovereign_base(self):
        """Test class still inherits from SovereignBaseAgent."""
        from agentic_core.L5_safety.policy_engine.structure_healer_agent_types import (
            StructureHealerAgent,
        )
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

        assert issubclass(StructureHealerAgent, SovereignBaseAgent)

    def test_factory_functions_exist(self):
        """Test factory functions exist."""
        from agentic_core.L5_safety.policy_engine.structure_healer_agent_types import (
            create_legacy_gravity_healer,
            create_legacy_naming_healer,
        )

        assert callable(create_legacy_gravity_healer)
        assert callable(create_legacy_naming_healer)

    def test_factory_gravity_healer(self):
        """Test create_legacy_gravity_healer creates correct config."""
        from agentic_core.L5_safety.policy_engine.structure_healer_agent_types import (
            create_legacy_gravity_healer,
        )

        healer = create_legacy_gravity_healer()
        assert healer._agent_config.enable_gravity is True
        assert healer._agent_config.enable_naming is False

    def test_factory_naming_healer(self):
        """Test create_legacy_naming_healer creates correct config."""
        from agentic_core.L5_safety.policy_engine.structure_healer_agent_types import (
            create_legacy_naming_healer,
        )

        healer = create_legacy_naming_healer()
        assert healer._agent_config.enable_naming is True
        assert healer._agent_config.enable_gravity is False

    def test_backup_file_method(self):
        """Test _backup_file method exists."""
        from agentic_core.L5_safety.policy_engine.structure_healer_agent_types import (
            StructureHealerAgent,
        )

        agent = StructureHealerAgent()
        assert hasattr(agent, "_backup_file")
        assert callable(agent._backup_file)

    def test_extract_layer_method(self):
        """Test _extract_layer method exists."""
        from agentic_core.L5_safety.policy_engine.structure_healer_agent_types import (
            StructureHealerAgent,
        )

        agent = StructureHealerAgent()
        assert hasattr(agent, "_extract_layer")
        assert callable(agent._extract_layer)

    def test_is_valid_gravity_method(self):
        """Test _is_valid_gravity method exists."""
        from agentic_core.L5_safety.policy_engine.structure_healer_agent_types import (
            StructureHealerAgent,
        )

        agent = StructureHealerAgent()
        assert hasattr(agent, "_is_valid_gravity")
        assert callable(agent._is_valid_gravity)


class TestHealingFunctionality:
    """Tests for actual healing functionality."""

    @pytest.fixture
    def agent(self):
        """Create StructureHealerAgent instance."""
        from agentic_core.L5_safety.policy_engine.structure_healer_agent_types import (
            StructureHealerAgent,
        )

        return StructureHealerAgent()

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

    def test_is_valid_gravity_same_layer(self, agent):
        """Test gravity validation for same layer."""
        assert agent._is_valid_gravity("L5", "L5") is True

    def test_is_valid_gravity_higher_to_lower(self, agent):
        """Test gravity validation for higher importing lower."""
        assert agent._is_valid_gravity("L5", "L3") is True

    def test_is_valid_gravity_lower_to_higher(self, agent):
        """Test gravity validation for lower importing higher."""
        assert agent._is_valid_gravity("L3", "L5") is False

    def test_heal_all_nonexistent_file(self, agent):
        """Test heal_all with nonexistent file."""
        result = agent.heal_all(Path("/nonexistent/file.py"))
        assert result == []

    def test_get_actions_empty(self, agent):
        """Test get_actions returns empty list initially."""
        actions = agent.get_actions()
        assert actions == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
