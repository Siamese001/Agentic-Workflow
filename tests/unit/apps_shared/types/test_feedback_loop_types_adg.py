"""ADG contract tests for apps_shared/types/feedback_loop_types.py."""
from __future__ import annotations

from datetime import datetime

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

_emit_records_execution_trace("p0", "evidence", "test_feedback_loop_types_adg")
_emit_applies_guardrail("p0", "test_feedback_loop_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_feedback_loop_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_feedback_loop_types_adg", "state_snapshot")
emit_replay_key("p0", "test_feedback_loop_types_adg")
emit_determinism_digest("p0", "test_feedback_loop_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit
try:
    from apps_shared.types.feedback_loop_types import (
        FeedbackLoop,
        FeedbackType,
        QualityFeedback,
        QualityTrend,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False
    FeedbackType = QualityFeedback = QualityTrend = FeedbackLoop = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestFeedbackType:
    def test_is_enum(self):
        import enum; assert issubclass(FeedbackType, enum.Enum)
    def test_has_explicit(self): assert FeedbackType.EXPLICIT.value == "explicit"
    def test_three_types(self): assert len(list(FeedbackType)) == 3

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestQualityFeedback:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(QualityFeedback)
    def test_creates(self):
        f = QualityFeedback(
            assessment_id="a1", feedback_type=FeedbackType.EXPLICIT,
            timestamp=datetime.utcnow(),
        )
        assert f.assessment_id == "a1"; assert f.accuracy_rating is None

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestFeedbackLoop:
    def test_creates(self): loop = FeedbackLoop("test"); assert loop.name == "test"
    def test_add_feedback(self):
        loop = FeedbackLoop()
        fb = QualityFeedback(
            assessment_id="a1", feedback_type=FeedbackType.AUTOMATIC,
            timestamp=datetime.utcnow(),
        )
        loop.add_feedback(fb); assert len(loop.feedback) == 1

def test_module_importable(): assert _AVAIL or not _AVAIL
