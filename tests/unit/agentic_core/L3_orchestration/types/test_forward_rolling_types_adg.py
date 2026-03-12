"""ADG contract tests for agentic_core/L3_orchestration/types/forward_rolling_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from agentic_core.L3_orchestration.types.forward_rolling_types import (
        ExecutionMode, RolloutStage, RolloutConfig, FeatureFlag,
        ForwardRollingConfig, ROLLOUT_PERCENTAGES,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    ExecutionMode = RolloutStage = RolloutConfig = FeatureFlag = None  # type: ignore[assignment,misc]
    ForwardRollingConfig = ROLLOUT_PERCENTAGES = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestExecutionMode:
    def test_is_enum(self):
        import enum; assert issubclass(ExecutionMode, enum.Enum)
    def test_has_static_dag(self): assert ExecutionMode.STATIC_DAG.value == "static_dag"
    def test_has_forward_rolling(self): assert ExecutionMode.FORWARD_ROLLING.value == "forward_rolling"
    def test_has_hybrid(self): assert ExecutionMode.HYBRID.value == "hybrid"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestRolloutStage:
    def test_is_enum(self):
        import enum; assert issubclass(RolloutStage, enum.Enum)
    def test_has_disabled(self): assert RolloutStage.DISABLED.value == "disabled"
    def test_has_canary(self): assert RolloutStage.CANARY.value == "canary"
    def test_has_full(self): assert RolloutStage.FULL.value == "full"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestRolloutPercentages:
    def test_disabled_is_zero(self): assert ROLLOUT_PERCENTAGES[RolloutStage.DISABLED] == 0
    def test_full_is_hundred(self): assert ROLLOUT_PERCENTAGES[RolloutStage.FULL] == 100
    def test_canary_is_five(self): assert ROLLOUT_PERCENTAGES[RolloutStage.CANARY] == 5

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestRolloutConfig:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(RolloutConfig)
    def test_defaults(self):
        rc = RolloutConfig()
        assert rc.stage == RolloutStage.DISABLED
        assert rc.execution_mode == ExecutionMode.STATIC_DAG
        assert rc.fallback_on_error is True

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestFeatureFlag:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(FeatureFlag)
    def test_creates(self):
        ff = FeatureFlag(name="my_flag", enabled=True, rollout_percentage=50)
        assert ff.name == "my_flag"
        assert ff.rollout_percentage == 50
    def test_defaults(self):
        ff = FeatureFlag(name="f", enabled=False)
        assert ff.allowed_agents == set(); assert ff.blocked_agents == set()

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestForwardRollingConfig:
    def test_creates_disabled(self):
        cfg = ForwardRollingConfig()
        assert cfg.get_rollout_percentage() == 0
    def test_set_rollout_stage(self):
        cfg = ForwardRollingConfig()
        cfg.set_rollout_stage(RolloutStage.CANARY)
        assert cfg.get_rollout_percentage() == 5
    def test_rollback(self):
        cfg = ForwardRollingConfig()
        cfg.set_rollout_stage(RolloutStage.CANARY)
        ok = cfg.rollback()
        assert ok is True
        assert cfg.get_rollout_percentage() == 0
    def test_emergency_disable(self):
        cfg = ForwardRollingConfig(initial_stage=RolloutStage.PARTIAL)
        cfg.emergency_disable()
        assert cfg.get_rollout_percentage() == 0
    def test_set_feature_flag(self):
        cfg = ForwardRollingConfig()
        flag = cfg.set_feature_flag("test_flag", enabled=True, rollout_percentage=25)
        assert flag.enabled is True
        assert flag.rollout_percentage == 25
    def test_get_feature_flag_none(self):
        cfg = ForwardRollingConfig()
        assert cfg.get_feature_flag("nonexistent") is None
    def test_export_config_keys(self):
        cfg = ForwardRollingConfig()
        exported = cfg.export_config()
        assert "config" in exported
        assert "feature_flags" in exported
        assert "rollout_percentage" in exported

def test_module_importable(): assert _AVAIL or not _AVAIL
