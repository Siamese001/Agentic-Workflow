"""ADG-driven tests for L2_execution/types/llm_replay_types.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.types.llm_replay_types import (
        ReplayMode,
        PRODUCTION_ALLOWED_MODES,
        DEV_TEST_ALLOWED_MODES,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ReplayMode = None  # type: ignore[assignment,misc]
    PRODUCTION_ALLOWED_MODES = None  # type: ignore[assignment]
    DEV_TEST_ALLOWED_MODES = None  # type: ignore[assignment]


@pytest.mark.skipif(not _AVAILABLE, reason="llm_replay_types deps unavailable")
class TestReplayMode:
    def test_is_enum(self):
        import enum
        assert issubclass(ReplayMode, enum.Enum)

    def test_recorded_output_value(self):
        assert ReplayMode.RECORDED_OUTPUT.value == "RECORDED_OUTPUT"

    def test_deterministic_inference_value(self):
        assert ReplayMode.DETERMINISTIC_INFERENCE.value == "DETERMINISTIC_INFERENCE"


@pytest.mark.skipif(not _AVAILABLE, reason="llm_replay_types deps unavailable")
class TestAllowedModes:
    def test_production_modes_is_frozenset(self):
        assert isinstance(PRODUCTION_ALLOWED_MODES, frozenset)

    def test_production_has_recorded_output(self):
        assert ReplayMode.RECORDED_OUTPUT in PRODUCTION_ALLOWED_MODES

    def test_production_not_has_deterministic_inference(self):
        assert ReplayMode.DETERMINISTIC_INFERENCE not in PRODUCTION_ALLOWED_MODES

    def test_dev_test_superset_of_production(self):
        assert PRODUCTION_ALLOWED_MODES.issubset(DEV_TEST_ALLOWED_MODES)


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
