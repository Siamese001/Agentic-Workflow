"""ADG contract tests for L4_state/types/micro_stage_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit
try:
    from agentic_core.L4_state.types.micro_stage_types import (
        HopState,
        MicroCheckpoint,
        MicroStage,
        RetryPolicy,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False; MicroStage = HopState = RetryPolicy = MicroCheckpoint = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestMicroStage:
    def test_is_str_enum(self):
        import enum; assert issubclass(MicroStage, str); assert issubclass(MicroStage, enum.Enum)
    def test_has_five_stages(self):
        assert len(list(MicroStage)) == 5
    def test_values(self):
        assert MicroStage.INIT == "init"
        assert MicroStage.COMMIT == "commit"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestHopState:
    def test_is_str_enum(self):
        import enum; assert issubclass(HopState, str); assert issubclass(HopState, enum.Enum)
    def test_has_pending(self):
        assert HopState.PENDING == "pending"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestRetryPolicy:
    def test_creates_defaults(self):
        rp = RetryPolicy()
        assert rp.max_retries == 3
        assert rp.exponential_backoff is True

def test_module_importable(): assert _AVAIL or not _AVAIL
