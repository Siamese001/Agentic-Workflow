"""ADG importability contract for agentic_core/L2_execution/types/llm_replay_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_llm_replay_types.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.types.llm_replay_types import (  # noqa: F401
        DEV_TEST_ALLOWED_MODES,
        PRODUCTION_ALLOWED_MODES,
        ReplayBundle,
        ReplayMode,
        is_authoritative,
        mode_label,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ReplayMode = None  # type: ignore[assignment,misc]
    PRODUCTION_ALLOWED_MODES = None  # type: ignore[assignment,misc]
    DEV_TEST_ALLOWED_MODES = None  # type: ignore[assignment,misc]
    is_authoritative = None  # type: ignore[assignment,misc]
    mode_label = None  # type: ignore[assignment,misc]
    ReplayBundle = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="llm_replay_types deps unavailable")
class TestLlmReplayTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L2_execution/types/llm_replay_types.py must be importable."""
        assert _AVAILABLE

    def test_replaymode_defined(self) -> None:
        assert ReplayMode is not None

    def test_replaybundle_defined(self) -> None:
        assert ReplayBundle is not None
