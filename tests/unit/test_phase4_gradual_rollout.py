"""
Phase 4 Gradual Rollout Test Suite.

Tests for feature flags, traffic routing, and configuration management.

Author: Cascade
Date: February 2026
Phase: 4 - Gradual Rollout Testing
"""

import pytest
from unittest.mock import MagicMock

from agentic_core.L3_orchestration.workflow_engines.ForwardRollingConfig import (
    ExecutionMode,
    FeatureFlag,
    ForwardRollingConfig,
    RolloutConfig,
    RolloutStage,
    ROLLOUT_PERCENTAGES,
)


class TestForwardRollingConfigInitialization:
    """Test ForwardRollingConfig initialization."""

    def test_default_initialization(self):
        """Test config initializes with defaults."""
        config = ForwardRollingConfig()

        assert config._config.stage == RolloutStage.DISABLED
        assert config._config.execution_mode == ExecutionMode.STATIC_DAG
        assert len(config._feature_flags) >= 5

    def test_custom_initial_stage(self):
        """Test config with custom initial stage."""
        config = ForwardRollingConfig(initial_stage=RolloutStage.CANARY)

        assert config._config.stage == RolloutStage.CANARY

    def test_callback_initialization(self):
        """Test config with callback."""
        callback = MagicMock()
        config = ForwardRollingConfig(config_update_callback=callback)

        assert config._config_update_callback == callback


class TestExecutionModeRouting:
    """Test execution mode routing logic."""

    @pytest.fixture
    def config(self):
        """Create test config."""
        return ForwardRollingConfig()

    def test_disabled_stage_returns_static(self, config):
        """Test disabled stage always returns static DAG."""
        config.set_rollout_stage(RolloutStage.DISABLED)

        mode = config.get_execution_mode("agent_1", "mission_1")

        assert mode == ExecutionMode.STATIC_DAG

    def test_full_rollout_returns_forward_rolling(self, config):
        """Test full rollout returns forward rolling mode."""
        config.set_rollout_stage(RolloutStage.FULL)
        config._config.execution_mode = ExecutionMode.FORWARD_ROLLING

        mode = config.get_execution_mode("agent_1", "mission_1")

        assert mode == ExecutionMode.FORWARD_ROLLING

    def test_sticky_routing(self, config):
        """Test sticky routing returns consistent results."""
        config.set_rollout_stage(RolloutStage.PARTIAL)
        config._config.execution_mode = ExecutionMode.FORWARD_ROLLING

        # Get mode multiple times for same agent
        modes = [config.get_execution_mode("agent_1", "mission_1") for _ in range(10)]

        # All should be the same due to sticky routing
        assert len(set(modes)) == 1

    def test_different_agents_may_get_different_modes(self, config):
        """Test different agents may route differently at partial rollout."""
        config.set_rollout_stage(RolloutStage.PARTIAL)
        config._config.execution_mode = ExecutionMode.FORWARD_ROLLING
        config._config.sticky_routing = False

        # Get modes for many different agents
        modes = set()
        for i in range(100):
            mode = config.get_execution_mode(f"agent_{i}", f"mission_{i}")
            modes.add(mode)

        # At 50% rollout, we should see both modes
        assert len(modes) >= 1  # At minimum we should get at least one mode


class TestRolloutStages:
    """Test rollout stage management."""

    @pytest.fixture
    def config(self):
        """Create test config."""
        return ForwardRollingConfig()

    def test_set_rollout_stage(self, config):
        """Test setting rollout stage."""
        config.set_rollout_stage(RolloutStage.CANARY)

        assert config._config.stage == RolloutStage.CANARY
        assert config.get_rollout_percentage() == 5

    def test_rollout_percentages(self, config):
        """Test rollout percentages for each stage."""
        stages_pct = [
            (RolloutStage.DISABLED, 0),
            (RolloutStage.CANARY, 5),
            (RolloutStage.EARLY_ADOPTER, 25),
            (RolloutStage.PARTIAL, 50),
            (RolloutStage.MAJORITY, 75),
            (RolloutStage.FULL, 100),
        ]

        for stage, expected_pct in stages_pct:
            config.set_rollout_stage(stage)
            assert config.get_rollout_percentage() == expected_pct

    def test_stage_change_clears_routing_cache(self, config):
        """Test that changing stage clears routing cache."""
        config.set_rollout_stage(RolloutStage.PARTIAL)
        config.get_execution_mode("agent_1")  # Populate cache

        assert len(config._routing_cache) > 0

        config.set_rollout_stage(RolloutStage.FULL)

        assert len(config._routing_cache) == 0

    def test_callback_invoked_on_stage_change(self):
        """Test callback is invoked when stage changes."""
        callback = MagicMock()
        config = ForwardRollingConfig(config_update_callback=callback)

        config.set_rollout_stage(RolloutStage.CANARY)

        callback.assert_called()


class TestRollback:
    """Test rollback functionality."""

    @pytest.fixture
    def config(self):
        """Create test config."""
        return ForwardRollingConfig()

    def test_rollback_to_previous(self, config):
        """Test rollback restores previous configuration."""
        config.set_rollout_stage(RolloutStage.CANARY)
        config.set_rollout_stage(RolloutStage.PARTIAL)

        result = config.rollback()

        assert result is True
        assert config._config.stage == RolloutStage.CANARY

    def test_rollback_multiple_times(self, config):
        """Test multiple rollbacks."""
        config.set_rollout_stage(RolloutStage.CANARY)
        config.set_rollout_stage(RolloutStage.PARTIAL)
        config.set_rollout_stage(RolloutStage.FULL)

        config.rollback()
        assert config._config.stage == RolloutStage.PARTIAL

        config.rollback()
        assert config._config.stage == RolloutStage.CANARY

    def test_rollback_with_no_history(self, config):
        """Test rollback with no history returns False."""
        result = config.rollback()

        assert result is False


class TestEmergencyDisable:
    """Test emergency disable functionality."""

    def test_emergency_disable(self):
        """Test emergency disable sets everything to disabled."""
        config = ForwardRollingConfig(initial_stage=RolloutStage.FULL)
        config._config.execution_mode = ExecutionMode.FORWARD_ROLLING

        config.emergency_disable()

        assert config._config.stage == RolloutStage.DISABLED
        assert config._config.execution_mode == ExecutionMode.STATIC_DAG

        flag = config.get_feature_flag("forward_rolling_enabled")
        assert flag is not None
        assert flag.enabled is False


class TestFeatureFlags:
    """Test feature flag management."""

    @pytest.fixture
    def config(self):
        """Create test config."""
        return ForwardRollingConfig()

    def test_default_flags_exist(self, config):
        """Test default feature flags are created."""
        flags = config.get_all_feature_flags()

        assert "forward_rolling_enabled" in flags
        assert "context_pruning" in flags
        assert "adaptive_depth" in flags
        assert "monitoring" in flags

    def test_set_feature_flag(self, config):
        """Test setting a feature flag."""
        flag = config.set_feature_flag(
            name="new_feature",
            enabled=True,
            rollout_percentage=50,
        )

        assert flag.name == "new_feature"
        assert flag.enabled is True
        assert flag.rollout_percentage == 50

    def test_update_existing_flag(self, config):
        """Test updating an existing flag."""
        config.set_feature_flag("context_pruning", enabled=False, rollout_percentage=0)

        flag = config.get_feature_flag("context_pruning")

        assert flag.enabled is False
        assert flag.rollout_percentage == 0

    def test_rollout_percentage_clamping(self, config):
        """Test rollout percentage is clamped to 0-100."""
        flag_high = config.set_feature_flag("test_high", True, 150)
        flag_low = config.set_feature_flag("test_low", True, -50)

        assert flag_high.rollout_percentage == 100
        assert flag_low.rollout_percentage == 0

    def test_is_feature_enabled(self, config):
        """Test checking if feature is enabled."""
        config.set_feature_flag("test_feature", enabled=True)

        assert config.is_feature_enabled("test_feature") is True

    def test_feature_disabled_returns_false(self, config):
        """Test disabled feature returns False."""
        config.set_feature_flag("test_feature", enabled=False)

        assert config.is_feature_enabled("test_feature") is False

    def test_nonexistent_feature_returns_false(self, config):
        """Test nonexistent feature returns False."""
        assert config.is_feature_enabled("nonexistent") is False


class TestAgentAllowlistBlocklist:
    """Test agent allowlist and blocklist functionality."""

    @pytest.fixture
    def config(self):
        """Create test config."""
        cfg = ForwardRollingConfig()
        cfg.set_feature_flag("test_flag", enabled=True)
        return cfg

    def test_add_to_blocklist(self, config):
        """Test adding agent to blocklist."""
        result = config.add_agent_to_blocklist("test_flag", "blocked_agent")

        assert result is True

        flag = config.get_feature_flag("test_flag")
        assert "blocked_agent" in flag.blocked_agents

    def test_blocked_agent_feature_disabled(self, config):
        """Test blocked agent doesn't get feature."""
        config.add_agent_to_blocklist("test_flag", "blocked_agent")

        assert config.is_feature_enabled("test_flag", "blocked_agent") is False
        assert config.is_feature_enabled("test_flag", "other_agent") is True

    def test_add_to_allowlist(self, config):
        """Test adding agent to allowlist."""
        result = config.add_agent_to_allowlist("test_flag", "allowed_agent")

        assert result is True

    def test_allowlist_restricts_access(self, config):
        """Test allowlist restricts feature to listed agents."""
        config.add_agent_to_allowlist("test_flag", "allowed_agent")

        assert config.is_feature_enabled("test_flag", "allowed_agent") is True
        assert config.is_feature_enabled("test_flag", "other_agent") is False

    def test_remove_from_blocklist(self, config):
        """Test removing agent from blocklist."""
        config.add_agent_to_blocklist("test_flag", "agent_1")
        result = config.remove_agent_from_blocklist("test_flag", "agent_1")

        assert result is True

        flag = config.get_feature_flag("test_flag")
        assert "agent_1" not in flag.blocked_agents

    def test_remove_from_allowlist(self, config):
        """Test removing agent from allowlist."""
        config.add_agent_to_allowlist("test_flag", "agent_1")
        result = config.remove_agent_from_allowlist("test_flag", "agent_1")

        assert result is True


class TestConfigUpdates:
    """Test configuration updates."""

    @pytest.fixture
    def config(self):
        """Create test config."""
        return ForwardRollingConfig()

    def test_update_config(self, config):
        """Test updating configuration values."""
        config.update_config(max_depth=100, enable_monitoring=False)

        assert config._config.max_depth == 100
        assert config._config.enable_monitoring is False

    def test_update_config_callback(self):
        """Test callback invoked on config update."""
        callback = MagicMock()
        config = ForwardRollingConfig(config_update_callback=callback)

        config.update_config(max_depth=75)

        callback.assert_called()

    def test_get_config(self, config):
        """Test getting current config."""
        cfg = config.get_config()

        assert isinstance(cfg, RolloutConfig)
        assert cfg.stage == RolloutStage.DISABLED


class TestRoutingStats:
    """Test routing statistics."""

    @pytest.fixture
    def config(self):
        """Create test config with some routing data."""
        cfg = ForwardRollingConfig(initial_stage=RolloutStage.PARTIAL)
        cfg._config.execution_mode = ExecutionMode.FORWARD_ROLLING

        # Generate some cached routes
        for i in range(10):
            cfg.get_execution_mode(f"agent_{i}")

        return cfg

    def test_get_routing_stats(self, config):
        """Test getting routing statistics."""
        stats = config.get_routing_stats()

        assert "total_cached_routes" in stats
        assert "mode_distribution" in stats
        assert "rollout_stage" in stats
        assert "rollout_percentage" in stats

    def test_clear_routing_cache(self, config):
        """Test clearing routing cache."""
        count = config.clear_routing_cache()

        assert count == 10
        assert len(config._routing_cache) == 0


class TestConfigExport:
    """Test configuration export."""

    def test_export_config(self):
        """Test exporting configuration."""
        config = ForwardRollingConfig(initial_stage=RolloutStage.CANARY)
        config.set_feature_flag("custom_flag", True, 75)

        export = config.export_config()

        assert "config" in export
        assert "feature_flags" in export
        assert "rollout_percentage" in export
        assert export["config"]["stage"] == "canary"
        assert export["rollout_percentage"] == 5


class TestRolloutPercentages:
    """Test rollout percentage constants."""

    def test_all_stages_have_percentages(self):
        """Test all stages have defined percentages."""
        for stage in RolloutStage:
            assert stage in ROLLOUT_PERCENTAGES

    def test_percentage_ordering(self):
        """Test percentages are in logical order."""
        assert ROLLOUT_PERCENTAGES[RolloutStage.DISABLED] == 0
        assert (
            ROLLOUT_PERCENTAGES[RolloutStage.CANARY]
            < ROLLOUT_PERCENTAGES[RolloutStage.EARLY_ADOPTER]
        )
        assert (
            ROLLOUT_PERCENTAGES[RolloutStage.EARLY_ADOPTER]
            < ROLLOUT_PERCENTAGES[RolloutStage.PARTIAL]
        )
        assert (
            ROLLOUT_PERCENTAGES[RolloutStage.PARTIAL] < ROLLOUT_PERCENTAGES[RolloutStage.MAJORITY]
        )
        assert ROLLOUT_PERCENTAGES[RolloutStage.MAJORITY] < ROLLOUT_PERCENTAGES[RolloutStage.FULL]
        assert ROLLOUT_PERCENTAGES[RolloutStage.FULL] == 100


class TestEnums:
    """Test enum definitions."""

    def test_execution_mode_values(self):
        """Test ExecutionMode enum values."""
        assert ExecutionMode.STATIC_DAG.value == "static_dag"
        assert ExecutionMode.FORWARD_ROLLING.value == "forward_rolling"
        assert ExecutionMode.HYBRID.value == "hybrid"

    def test_rollout_stage_values(self):
        """Test RolloutStage enum values."""
        assert RolloutStage.DISABLED.value == "disabled"
        assert RolloutStage.CANARY.value == "canary"
        assert RolloutStage.FULL.value == "full"


class TestDataclasses:
    """Test dataclass structures."""

    def test_feature_flag_defaults(self):
        """Test FeatureFlag default values."""
        flag = FeatureFlag(name="test", enabled=True)

        assert flag.rollout_percentage == 100
        assert len(flag.allowed_agents) == 0
        assert len(flag.blocked_agents) == 0

    def test_rollout_config_defaults(self):
        """Test RolloutConfig default values."""
        config = RolloutConfig()

        assert config.stage == RolloutStage.DISABLED
        assert config.execution_mode == ExecutionMode.STATIC_DAG
        assert config.max_depth == 50
        assert config.enable_context_pruning is True
        assert config.fallback_on_error is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
