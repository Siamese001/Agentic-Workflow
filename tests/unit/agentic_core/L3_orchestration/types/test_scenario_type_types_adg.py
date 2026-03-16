"""ADG contract tests for L3_orchestration/types/scenario_type_types.py."""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_scenario_type_types_adg")
_emit_applies_guardrail("p0", "test_scenario_type_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_scenario_type_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_scenario_type_types_adg", "state_snapshot")
emit_replay_key("p0", "test_scenario_type_types_adg")
emit_determinism_digest("p0", "test_scenario_type_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
pytestmark = pytest.mark.unit
from agentic_core.L3_orchestration.types.scenario_type_types import (
    PerformanceLevel,
    ScenarioType,
    TrainingScenario,
)


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
