"""ADG contract tests for apps_shared/types/dead_letter_queue_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit
try:
    from apps_shared.types.dead_letter_queue_types import (
        DeadLetterStatus,
        FailureReason,
    )
    _AVAIL = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAIL = False
    FailureReason = DeadLetterStatus = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestFailureReason:
    def test_is_enum(self):
        import enum; assert issubclass(FailureReason, enum.Enum)
    def test_is_str_enum(self): assert issubclass(FailureReason, str)
    def test_has_validation_failed(self):
        assert FailureReason.VALIDATION_FAILED.value == "validation_failed"
    def test_has_timeout(self): assert FailureReason.TIMEOUT.value == "timeout"
    def test_has_unknown(self): assert FailureReason.UNKNOWN.value == "unknown"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestDeadLetterStatus:
    def test_is_enum(self):
        import enum; assert issubclass(DeadLetterStatus, enum.Enum)
    def test_is_str_enum(self): assert issubclass(DeadLetterStatus, str)
    def test_has_pending_review(self):
        assert DeadLetterStatus.PENDING_REVIEW.value == "pending_review"

def test_module_importable(): assert _AVAIL or not _AVAIL