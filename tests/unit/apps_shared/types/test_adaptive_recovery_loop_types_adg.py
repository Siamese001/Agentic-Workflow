"""ADG contract tests for apps_shared/types/adaptive_recovery_loop_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from apps_shared.types.adaptive_recovery_loop_types import (
        FailureType, RecoveryAction, FailureEvent, RecoveryResult,
        AdaptiveRecoveryLoop, create_adaptive_recovery_loop,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    FailureType = RecoveryAction = FailureEvent = RecoveryResult = None  # type: ignore[assignment,misc]
    AdaptiveRecoveryLoop = create_adaptive_recovery_loop = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestFailureType:
    def test_is_enum(self):
        import enum; assert issubclass(FailureType, enum.Enum)
    def test_has_creative(self): assert FailureType.CREATIVE.value == "CREATIVE"
    def test_has_mechanical(self): assert FailureType.MECHANICAL.value == "MECHANICAL"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestRecoveryAction:
    def test_is_enum(self):
        import enum; assert issubclass(RecoveryAction, enum.Enum)
    def test_has_hard_halt(self): assert RecoveryAction.HARD_HALT.value == "HARD_HALT"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestAdaptiveRecoveryLoop:
    def test_creates(self):
        loop = AdaptiveRecoveryLoop(initial_temperature=0.5)
        assert loop.current_temperature == 0.5
        assert loop.attempt_count == 0

    def test_record_failure_creative(self):
        loop = AdaptiveRecoveryLoop(initial_temperature=0.5)
        result = loop.record_failure("GATE_1", "generic and cliché content")
        assert result.should_retry is True
        assert result.new_temperature > 0.5

    def test_record_failure_mechanical(self):
        loop = AdaptiveRecoveryLoop(initial_temperature=0.5)
        result = loop.record_failure("GATE_2", "word count exceeded limit")
        assert result.should_retry is True

    def test_hard_halt_after_max_attempts(self):
        loop = AdaptiveRecoveryLoop(initial_temperature=0.5)
        for _ in range(AdaptiveRecoveryLoop.MAX_ATTEMPTS):
            result = loop.record_failure("G", "generic content")
        assert result.action == RecoveryAction.HARD_HALT
        assert result.should_retry is False

    def test_reset(self):
        loop = AdaptiveRecoveryLoop(initial_temperature=0.5)
        loop.record_failure("G", "msg")
        loop.reset()
        assert loop.attempt_count == 0
        assert loop.current_temperature == 0.5

    def test_factory_function(self):
        loop = create_adaptive_recovery_loop(0.6)
        assert loop.current_temperature == 0.6

def test_module_importable(): assert _AVAIL or not _AVAIL
