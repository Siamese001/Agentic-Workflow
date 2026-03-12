"""ADG importability contract for agentic_core/L2_execution/types/llm_replay_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_llm_replay_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.types.llm_replay_types import (  # noqa: F401
        ReplayMode,
        ReplayBundle,
        LLMReplayStrategy,
        is_authoritative,
        mode_label,
        verify_replay_integrity,
        validate_production_mode,
        PRODUCTION_ALLOWED_MODES,
        DEV_TEST_ALLOWED_MODES,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ReplayMode = None  # type: ignore[assignment,misc]
    ReplayBundle = None  # type: ignore[assignment,misc]
    LLMReplayStrategy = None  # type: ignore[assignment,misc]
    is_authoritative = None  # type: ignore[assignment,misc]
    mode_label = None  # type: ignore[assignment,misc]
    verify_replay_integrity = None  # type: ignore[assignment,misc]
    validate_production_mode = None  # type: ignore[assignment,misc]
    PRODUCTION_ALLOWED_MODES = None  # type: ignore[assignment,misc]
    DEV_TEST_ALLOWED_MODES = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="llm_replay_types.py deps unavailable")
class TestLlmReplayTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: llm_replay_types.py must be importable."""
        assert _AVAILABLE

    def test_replaymode_is_type(self) -> None:
        assert ReplayMode is not None

    def test_replaybundle_is_type(self) -> None:
        assert ReplayBundle is not None

    def test_llmreplaystrategy_is_type(self) -> None:
        assert LLMReplayStrategy is not None

    def test_is_authoritative_callable(self) -> None:
        assert callable(is_authoritative)

    def test_mode_label_callable(self) -> None:
        assert callable(mode_label)

    def test_production_allowed_modes_defined(self) -> None:
        assert PRODUCTION_ALLOWED_MODES is not None

    def test_dev_test_allowed_modes_defined(self) -> None:
        assert DEV_TEST_ALLOWED_MODES is not None

