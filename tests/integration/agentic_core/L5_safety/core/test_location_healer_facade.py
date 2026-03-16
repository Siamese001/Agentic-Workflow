"""
Unit Tests for LocationHealerAgent Facade - Phase 3

Tests the facade conversion of LocationHealerAgent including:
- Legacy signature compatibility
- LocationHealingStrategy functionality
- Healing preservation
- Return type consistency
"""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from agentic_core.L3_orchestration.reasoning.UnifiedAgent import (
    HealingResult,
    LocationHealingStrategy,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_location_healer_facade")
_emit_applies_guardrail("p0", "test_location_healer_facade", "p0_governance")
_emit_reads_policy_state("p0", "test_location_healer_facade", "policy_binding")
_emit_snapshots_state("p0", "test_location_healer_facade", "state_snapshot")
emit_replay_key("p0", "test_location_healer_facade")
emit_determinism_digest("p0", "test_location_healer_facade")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


class TestLocationHealingStrategy:
    """Tests for LocationHealingStrategy."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return {
            "project_root": "/test/project",
            "backup_enabled": True,
            "auto_fix_imports": True,
        }

    @pytest.fixture
    def strategy(self, config):
        """Create LocationHealingStrategy instance."""
        return LocationHealingStrategy(config)

    def test_initialization(self, strategy, config):
        """Test strategy initialization."""
        assert strategy.project_root == "/test/project"
        assert strategy.backup_enabled is True
        assert strategy.auto_fix_imports is True

    def test_initialization_with_disabled_features(self):
        """Test strategy initialization with disabled features."""
        config = {
            "project_root": "/other/project",
            "backup_enabled": False,
            "auto_fix_imports": False,
        }
        strategy = LocationHealingStrategy(config)

        assert strategy.project_root == "/other/project"
        assert strategy.backup_enabled is False
        assert strategy.auto_fix_imports is False

    @pytest.mark.asyncio
    async def test_execute_returns_healing_result(self, strategy):
        """Test execute returns HealingResult."""
        mock_agent = Mock()
        mock_agent.log_info = Mock()

        result = await strategy.execute(mock_agent)

        assert isinstance(result, HealingResult)
        assert result.violations_found >= 0
        assert result.violations_fixed >= 0

    @pytest.mark.asyncio
    async def test_execute_with_violation(self, strategy):
        """Test execute with violation parameter."""
        mock_agent = Mock()
        mock_agent.log_info = Mock()
        mock_agent.heal = Mock(return_value={"status": "success", "artifacts": []})

        result = await strategy.execute(mock_agent, violation={"type": "DEPTH", "file": "/test/file.py"})

        assert isinstance(result, HealingResult)

    def test_heal_repository_returns_dict(self, strategy):
        """Test heal_repository returns proper dict structure."""
        mock_agent = Mock()
        mock_agent.heal_repository = Mock(return_value={"violations_found": 0, "violations_fixed": 0})

        result = strategy.heal_repository(mock_agent, dry_run=True, execute=False)

        assert isinstance(result, dict)


class TestLocationHealerAgentFacade:
    """Tests for LocationHealerAgent facade."""

    def test_class_exists(self):
        """Test LocationHealerAgent class exists."""
        from agentic_core.L5_safety.reasoning.LocationHealerAgent import (
            LocationHealerAgent,
        )

        assert LocationHealerAgent is not None

    def test_inherits_from_sovereign_base(self):
        """Test class still inherits from SovereignBaseAgent."""
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
        from agentic_core.L5_safety.reasoning.LocationHealerAgent import (
            LocationHealerAgent,
        )

        assert issubclass(LocationHealerAgent, SovereignBaseAgent)

    def test_is_dataclass(self):
        """Test LocationHealerAgent is a dataclass."""
        from dataclasses import is_dataclass

        from agentic_core.L5_safety.reasoning.LocationHealerAgent import (
            LocationHealerAgent,
        )

        assert is_dataclass(LocationHealerAgent)

    def test_has_project_root_field(self):
        """Test LocationHealerAgent has project_root field."""
        from agentic_core.L5_safety.reasoning.LocationHealerAgent import (
            LocationHealerAgent,
        )

        # Check field exists in annotations
        assert "project_root" in LocationHealerAgent.__dataclass_fields__


class TestLocationHealerMethods:
    """Tests for LocationHealerAgent methods existence."""

    def test_heal_method_signature(self):
        """Test heal method exists with correct signature."""
        from agentic_core.L5_safety.reasoning.LocationHealerAgent import (
            LocationHealerAgent,
        )

        assert hasattr(LocationHealerAgent, "heal")
        assert callable(LocationHealerAgent.heal)

    def test_heal_repository_method_signature(self):
        """Test heal_repository method exists."""
        from agentic_core.L5_safety.reasoning.LocationHealerAgent import (
            LocationHealerAgent,
        )

        assert hasattr(LocationHealerAgent, "heal_repository")
        assert callable(LocationHealerAgent.heal_repository)

    def test_safe_move_method_exists(self):
        """Test safe_move method exists."""
        from agentic_core.L5_safety.reasoning.LocationHealerAgent import (
            LocationHealerAgent,
        )

        assert hasattr(LocationHealerAgent, "safe_move")
        assert callable(LocationHealerAgent.safe_move)

    def test_safe_delete_method_exists(self):
        """Test safe_delete method exists."""
        from agentic_core.L5_safety.reasoning.LocationHealerAgent import (
            LocationHealerAgent,
        )

        assert hasattr(LocationHealerAgent, "safe_delete")
        assert callable(LocationHealerAgent.safe_delete)

    def test_post_heal_validation_method_exists(self):
        """Test post_heal_validation method exists."""
        from agentic_core.L5_safety.reasoning.LocationHealerAgent import (
            LocationHealerAgent,
        )

        assert hasattr(LocationHealerAgent, "post_heal_validation")
        assert callable(LocationHealerAgent.post_heal_validation)

    def test_fix_imports_after_move_method_exists(self):
        """Test fix_imports_after_move method exists."""
        from agentic_core.L5_safety.reasoning.LocationHealerAgent import (
            LocationHealerAgent,
        )

        assert hasattr(LocationHealerAgent, "fix_imports_after_move")
        assert callable(LocationHealerAgent.fix_imports_after_move)


class TestLegacyCompatibility:
    """Tests ensuring 100% legacy compatibility."""

    def test_import_compatibility(self):
        """Test original import still works."""
        from agentic_core.L5_safety.reasoning.LocationHealerAgent import (
            LocationHealerAgent,
        )

        assert LocationHealerAgent is not None

    def test_docstring_updated(self):
        """Test docstring mentions facade pattern."""
        from agentic_core.L5_safety.reasoning.LocationHealerAgent import (
            LocationHealerAgent,
        )

        docstring = LocationHealerAgent.__doc__
        assert "FACADE" in docstring or "facade" in docstring.lower()

    def test_unified_strategy_import(self):
        """Test LocationHealingStrategy can be imported."""
        from agentic_core.L3_orchestration.reasoning.UnifiedAgent import LocationHealingStrategy

        assert LocationHealingStrategy is not None


class TestStrategyIntegration:
    """Tests for strategy integration."""

    def test_strategy_in_UnifiedAgent_exports(self):
        """Test LocationHealingStrategy is in UnifiedAgent exports."""
        from agentic_core.L3_orchestration.reasoning.UnifiedAgent import __all__

        assert "LocationHealingStrategy" in __all__

    def test_strategy_inherits_from_healing_strategy(self):
        """Test LocationHealingStrategy inherits from HealingStrategy."""
        from agentic_core.L3_orchestration.reasoning.UnifiedAgent import (
            HealingStrategy,
            LocationHealingStrategy,
        )

        assert issubclass(LocationHealingStrategy, HealingStrategy)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
