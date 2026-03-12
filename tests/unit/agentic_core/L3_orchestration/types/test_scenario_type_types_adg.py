"""ADG contract tests for L3_orchestration/types/scenario_type_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
from agentic_core.L3_orchestration.types.scenario_type_types import ScenarioType, PerformanceLevel, TrainingScenario

class TestScenarioType:
    def test_is_enum(self):
        import enum; assert issubclass(ScenarioType, enum.Enum)
    def test_has_golden_dataset(self):
        assert ScenarioType.GOLDEN_DATASET.value == "golden_dataset"

class TestPerformanceLevel:
    def test_is_enum(self):
        import enum; assert issubclass(PerformanceLevel, enum.Enum)
    def test_has_critical(self):
        assert PerformanceLevel.CRITICAL.value == "critical"

class TestTrainingScenario:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(TrainingScenario)
    def test_creates(self):
        s = TrainingScenario(id="s1", name="test", ScenarioType=ScenarioType.REGRESSION, description="d", test_cases=[])
        assert s.id == "s1"
    def test_to_dict(self):
        s = TrainingScenario(id="s1", name="n", ScenarioType=ScenarioType.STRESS_TEST, description="d", test_cases=[])
        d = s.to_dict()
        assert d["id"] == "s1"
