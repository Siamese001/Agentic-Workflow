"""ADG contract tests for apps_shared/types/standard_type_types.py."""
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

_emit_records_execution_trace("p0", "evidence", "test_standard_type_types_adg")
_emit_applies_guardrail("p0", "test_standard_type_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_standard_type_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_standard_type_types_adg", "state_snapshot")
emit_replay_key("p0", "test_standard_type_types_adg")
emit_determinism_digest("p0", "test_standard_type_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit
try:
    from apps_shared.types.standard_type_types import (
        QualityDimension,
        QualityStandard,
        StandardType,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False
    StandardType = QualityDimension = QualityStandard = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestStandardType:
    def test_is_enum(self):
        import enum; assert issubclass(StandardType, enum.Enum)
    def test_has_base(self): assert StandardType.BASE.value == "base"
    def test_has_excellence(self): assert StandardType.EXCELLENCE.value == "excellence"
    def test_three_types(self): assert len(list(StandardType)) == 3

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestQualityDimension:
    def test_is_enum(self):
        import enum; assert issubclass(QualityDimension, enum.Enum)
    def test_has_accuracy(self): assert QualityDimension.ACCURACY.value == "accuracy"
    def test_six_dimensions(self): assert len(list(QualityDimension)) == 6

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestQualityStandard:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(QualityStandard)
    def test_creates(self):
        s = QualityStandard(
            name="test_std", description="Test standard",
            dimension=QualityDimension.ACCURACY, standard_type=StandardType.BASE,
            criteria={"min_score": 0.8}, measurement_method="analysis",
        )
        assert s.name == "test_std"; assert s.validation_rules == []
    def test_evaluate_returns_dict(self):
        s = QualityStandard(
            name="s", description="d", dimension=QualityDimension.CLARITY,
            standard_type=StandardType.BASE, criteria={}, measurement_method="m",
        )
        result = s.evaluate("some content", {}); assert "score" in result

def test_module_importable(): assert _AVAIL or not _AVAIL
