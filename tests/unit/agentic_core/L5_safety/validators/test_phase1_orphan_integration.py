"""
Phase 1 Tests: Orphan Agent Integration Foundation

Tests for the integration adapters that wire orphan agents into
the existing validation and healing infrastructure.

Test Coverage:
- Red team integration (AdversarialValidator, BoundaryValidator)
- Chaos healing integration (ChaosResilienceStrategy)
- Dependency healing integration (DependencyPruningStrategy)
- Unified registration module
"""

from __future__ import annotations

import pytest
import sys
from pathlib import Path

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parents[5]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class TestRedTeamIntegration:
    """Tests for red_team_integration module."""

    def test_adversarial_validator_creation(self):
        """Test AdversarialValidator can be instantiated."""
        from agentic_core.L5_safety.validators.red_team_integration import (
            AdversarialValidator,
        )

        validator = AdversarialValidator()
        assert validator is not None
        assert validator._initialized is False

    def test_adversarial_validator_validate_returns_dict(self):
        """Test AdversarialValidator.validate returns proper format."""
        from agentic_core.L5_safety.validators.red_team_integration import (
            AdversarialValidator,
        )

        validator = AdversarialValidator()
        result = validator.validate({"test": "data"}, {})

        assert isinstance(result, dict)
        assert "valid" in result
        assert "errors" in result
        assert isinstance(result["errors"], list)

    def test_boundary_validator_creation(self):
        """Test BoundaryValidator can be instantiated."""
        from agentic_core.L5_safety.validators.red_team_integration import (
            BoundaryValidator,
        )

        validator = BoundaryValidator()
        assert validator is not None
        assert validator._initialized is False

    def test_boundary_validator_validate_returns_dict(self):
        """Test BoundaryValidator.validate returns proper format."""
        from agentic_core.L5_safety.validators.red_team_integration import (
            BoundaryValidator,
        )

        validator = BoundaryValidator()
        result = validator.validate({"test": "data"}, {})

        assert isinstance(result, dict)
        assert "valid" in result
        assert "errors" in result
        assert "recommendations" in result

    def test_get_adversarial_validator_singleton(self):
        """Test get_adversarial_validator returns singleton."""
        from agentic_core.L5_safety.validators.red_team_integration import (
            get_adversarial_validator,
        )

        v1 = get_adversarial_validator()
        v2 = get_adversarial_validator()
        assert v1 is v2

    def test_get_boundary_validator_singleton(self):
        """Test get_boundary_validator returns singleton."""
        from agentic_core.L5_safety.validators.red_team_integration import (
            get_boundary_validator,
        )

        v1 = get_boundary_validator()
        v2 = get_boundary_validator()
        assert v1 is v2

    def test_register_red_team_validators_returns_status(self):
        """Test register_red_team_validators returns proper status."""
        from agentic_core.L5_safety.validators.red_team_integration import (
            register_red_team_validators,
        )

        result = register_red_team_validators()

        assert isinstance(result, dict)
        assert "registered" in result
        assert "errors" in result
        assert "success" in result
        assert isinstance(result["registered"], list)

    def test_get_integration_status(self):
        """Test get_integration_status returns proper format."""
        from agentic_core.L5_safety.validators.red_team_integration import (
            get_integration_status,
        )

        status = get_integration_status()

        assert isinstance(status, dict)
        assert "validators_available" in status
        assert "adversarial_probe" in status["validators_available"]
        assert "boundary_testing" in status["validators_available"]


class TestChaosHealingIntegration:
    """Tests for chaos_healing_integration module."""

    def test_chaos_strategy_creation(self):
        """Test ChaosResilienceStrategy can be instantiated."""
        from agentic_core.L5_safety.validators.chaos_healing_integration import (
            ChaosResilienceStrategy,
        )

        strategy = ChaosResilienceStrategy()
        assert strategy is not None
        assert strategy._initialized is False

    def test_chaos_strategy_can_heal_supported_types(self):
        """Test ChaosResilienceStrategy.can_heal for supported types."""
        from agentic_core.L5_safety.validators.chaos_healing_integration import (
            ChaosResilienceStrategy,
        )

        strategy = ChaosResilienceStrategy()

        # Should handle these violation types
        assert strategy.can_heal({"type": "resilience_check"}) is True
        assert strategy.can_heal({"type": "post_healing_validation"}) is True
        assert strategy.can_heal({"type": "chaos_test_required"}) is True

        # Should not handle these
        assert strategy.can_heal({"type": "unknown_type"}) is False
        assert strategy.can_heal({"type": ""}) is False
        assert strategy.can_heal({}) is False

    def test_chaos_strategy_heal_returns_dict(self):
        """Test ChaosResilienceStrategy.heal returns proper format."""
        from agentic_core.L5_safety.validators.chaos_healing_integration import (
            ChaosResilienceStrategy,
        )

        strategy = ChaosResilienceStrategy()
        result = strategy.heal({"type": "resilience_check"}, {})

        assert isinstance(result, dict)
        assert "success" in result
        assert "resilience_score" in result
        assert "scenarios_tested" in result

    def test_get_chaos_strategy_singleton(self):
        """Test get_chaos_strategy returns singleton."""
        from agentic_core.L5_safety.validators.chaos_healing_integration import (
            get_chaos_strategy,
        )

        s1 = get_chaos_strategy()
        s2 = get_chaos_strategy()
        assert s1 is s2

    def test_register_chaos_healing_returns_status(self):
        """Test register_chaos_healing returns proper status."""
        from agentic_core.L5_safety.validators.chaos_healing_integration import (
            register_chaos_healing,
        )

        result = register_chaos_healing()

        assert isinstance(result, dict)
        assert "registered" in result
        assert "errors" in result
        assert "success" in result

    def test_chaos_integration_status(self):
        """Test get_integration_status returns proper format."""
        from agentic_core.L5_safety.validators.chaos_healing_integration import (
            get_integration_status,
        )

        status = get_integration_status()

        assert isinstance(status, dict)
        assert "strategies_available" in status
        assert "supported_violations" in status
        assert "chaos_resilience" in status["strategies_available"]


class TestDependencyHealingIntegration:
    """Tests for dependency_healing_integration module."""

    def test_dependency_strategy_creation(self):
        """Test DependencyPruningStrategy can be instantiated."""
        from agentic_core.L5_safety.validators.dependency_healing_integration import (
            DependencyPruningStrategy,
        )

        strategy = DependencyPruningStrategy()
        assert strategy is not None
        assert strategy._initialized is False

    def test_dependency_strategy_can_heal_supported_types(self):
        """Test DependencyPruningStrategy.can_heal for supported types."""
        from agentic_core.L5_safety.validators.dependency_healing_integration import (
            DependencyPruningStrategy,
        )

        strategy = DependencyPruningStrategy()

        # Should handle these violation types
        assert strategy.can_heal({"type": "unused_dependency"}) is True
        assert strategy.can_heal({"type": "dependency_bloat"}) is True
        assert strategy.can_heal({"type": "requirements_cleanup"}) is True

        # Should not handle these
        assert strategy.can_heal({"type": "unknown_type"}) is False
        assert strategy.can_heal({"type": ""}) is False

    def test_dependency_strategy_heal_returns_dict(self):
        """Test DependencyPruningStrategy.heal returns proper format."""
        from agentic_core.L5_safety.validators.dependency_healing_integration import (
            DependencyPruningStrategy,
        )

        strategy = DependencyPruningStrategy()
        result = strategy.heal({"type": "unused_dependency"}, {"dry_run": True})

        assert isinstance(result, dict)
        assert "success" in result
        assert "unused_found" in result
        assert "removed" in result

    def test_dependency_strategy_respects_dry_run(self):
        """Test DependencyPruningStrategy respects dry_run context."""
        from agentic_core.L5_safety.validators.dependency_healing_integration import (
            DependencyPruningStrategy,
        )

        strategy = DependencyPruningStrategy()

        # With dry_run=True
        result = strategy.heal({"type": "unused_dependency"}, {"dry_run": True})
        assert result.get("dry_run", True) is True

    def test_get_dependency_strategy_singleton(self):
        """Test get_dependency_strategy returns singleton."""
        from agentic_core.L5_safety.validators.dependency_healing_integration import (
            get_dependency_strategy,
        )

        s1 = get_dependency_strategy()
        s2 = get_dependency_strategy()
        assert s1 is s2

    def test_register_dependency_healing_returns_status(self):
        """Test register_dependency_healing returns proper status."""
        from agentic_core.L5_safety.validators.dependency_healing_integration import (
            register_dependency_healing,
        )

        result = register_dependency_healing()

        assert isinstance(result, dict)
        assert "registered" in result
        assert "errors" in result
        assert "success" in result

    def test_dependency_integration_status(self):
        """Test get_integration_status returns proper format."""
        from agentic_core.L5_safety.validators.dependency_healing_integration import (
            get_integration_status,
        )

        status = get_integration_status()

        assert isinstance(status, dict)
        assert "strategies_available" in status
        assert "supported_violations" in status
        assert "dependency_pruning" in status["strategies_available"]


class TestUnifiedRegistration:
    """Tests for register_all_validators module."""

    def setup_method(self):
        """Reset state before each test."""
        try:
            from agentic_core.L5_safety.validators import register_all_validators

            register_all_validators.reset()
        except Exception:
            pass

    def test_initialize_returns_status(self):
        """Test initialize returns proper status dict."""
        from agentic_core.L5_safety.validators import register_all_validators

        result = register_all_validators.initialize()

        assert isinstance(result, dict)
        assert "status" in result
        assert "validators" in result
        assert "strategies" in result
        assert isinstance(result["validators"], list)
        assert isinstance(result["strategies"], list)

    def test_initialize_idempotent(self):
        """Test initialize is idempotent (safe to call multiple times)."""
        from agentic_core.L5_safety.validators import register_all_validators

        register_all_validators.initialize()
        result2 = register_all_validators.initialize()

        # Second call should return already_initialized
        assert result2["status"] == "already_initialized"

    def test_get_integration_status_format(self):
        """Test get_integration_status returns comprehensive status."""
        from agentic_core.L5_safety.validators import register_all_validators

        status = register_all_validators.get_integration_status()

        assert isinstance(status, dict)
        assert "initialized" in status
        assert "validators_registered" in status
        assert "strategies_registered" in status
        assert "module_status" in status
        assert isinstance(status["module_status"], dict)

    def test_reset_clears_state(self):
        """Test reset clears initialization state."""
        from agentic_core.L5_safety.validators import register_all_validators

        register_all_validators.initialize()
        assert register_all_validators._REGISTERED is True

        register_all_validators.reset()
        assert register_all_validators._REGISTERED is False


class TestIntegrationModulesImportable:
    """Tests that all integration modules are importable."""

    def test_red_team_integration_importable(self):
        """Test red_team_integration module is importable."""
        from agentic_core.L5_safety.validators import red_team_integration

        assert red_team_integration is not None

    def test_chaos_healing_integration_importable(self):
        """Test chaos_healing_integration module is importable."""
        from agentic_core.L5_safety.validators import chaos_healing_integration

        assert chaos_healing_integration is not None

    def test_dependency_healing_integration_importable(self):
        """Test dependency_healing_integration module is importable."""
        from agentic_core.L5_safety.validators import dependency_healing_integration

        assert dependency_healing_integration is not None

    def test_register_all_validators_importable(self):
        """Test register_all_validators module is importable."""
        from agentic_core.L5_safety.validators import register_all_validators

        assert register_all_validators is not None


class TestValidatorProtocolCompliance:
    """Tests that validators comply with ValidatorProtocol."""

    def test_adversarial_validator_has_validate_method(self):
        """Test AdversarialValidator has validate method."""
        from agentic_core.L5_safety.validators.red_team_integration import (
            AdversarialValidator,
        )

        validator = AdversarialValidator()
        assert hasattr(validator, "validate")
        assert callable(validator.validate)

    def test_boundary_validator_has_validate_method(self):
        """Test BoundaryValidator has validate method."""
        from agentic_core.L5_safety.validators.red_team_integration import (
            BoundaryValidator,
        )

        validator = BoundaryValidator()
        assert hasattr(validator, "validate")
        assert callable(validator.validate)


class TestHealingStrategyProtocolCompliance:
    """Tests that healing strategies comply with HealingStrategyProtocol."""

    def test_chaos_strategy_has_required_methods(self):
        """Test ChaosResilienceStrategy has can_heal and heal methods."""
        from agentic_core.L5_safety.validators.chaos_healing_integration import (
            ChaosResilienceStrategy,
        )

        strategy = ChaosResilienceStrategy()
        assert hasattr(strategy, "can_heal")
        assert hasattr(strategy, "heal")
        assert callable(strategy.can_heal)
        assert callable(strategy.heal)

    def test_dependency_strategy_has_required_methods(self):
        """Test DependencyPruningStrategy has can_heal and heal methods."""
        from agentic_core.L5_safety.validators.dependency_healing_integration import (
            DependencyPruningStrategy,
        )

        strategy = DependencyPruningStrategy()
        assert hasattr(strategy, "can_heal")
        assert hasattr(strategy, "heal")
        assert callable(strategy.can_heal)
        assert callable(strategy.heal)


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
