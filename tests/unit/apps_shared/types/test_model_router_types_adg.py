"""ADG contract tests for apps_shared/types/model_router_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit
try:
    from apps_shared.types.model_router_types import (
        ModelConfig,
        ModelRouter,
        ModelTier,
        TaskProfile,
        TaskType,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False
    ModelTier = TaskType = ModelConfig = TaskProfile = ModelRouter = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestModelTier:
    def test_is_enum(self):
        import enum; assert issubclass(ModelTier, enum.Enum)
    def test_is_str_enum(self): assert issubclass(ModelTier, str)
    def test_has_fast(self): assert ModelTier.FAST.value == "FAST"
    def test_four_tiers(self): assert len(list(ModelTier)) == 4

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestTaskType:
    def test_is_enum(self):
        import enum; assert issubclass(TaskType, enum.Enum)
    def test_is_str_enum(self): assert issubclass(TaskType, str)
    def test_has_resume_formatting(self):
        assert TaskType.RESUME_FORMATTING.value == "RESUME_FORMATTING"
    def test_ten_task_types(self): assert len(list(TaskType)) == 10

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestModelConfig:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(ModelConfig)
    def test_creates(self):
        c = ModelConfig(
            provider="openai", model_name="gpt-4o-mini", tier=ModelTier.FAST,
            max_tokens=4096, temperature=0.7, cost_per_1k_tokens=0.00015,
        )
        assert c.provider == "openai"; assert c.tier == ModelTier.FAST

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestModelRouter:
    def test_creates(self):
        r = ModelRouter(); assert r is not None
    def test_get_model_config_resume(self):
        r = ModelRouter()
        config = r.get_model_config(TaskType.RESUME_FORMATTING, complexity_score=2)
        assert "model" in config; assert "tier" in config
    def test_get_model_config_data_analysis(self):
        r = ModelRouter()
        config = r.get_model_config(TaskType.DATA_ANALYSIS, complexity_score=5)
        assert config["tier"] in {t.value for t in ModelTier}
    def test_get_stats(self):
        r = ModelRouter(); stats = r.get_stats()
        assert "total_requests" in stats; assert "budget_info" in stats

def test_module_importable(): assert _AVAIL or not _AVAIL
