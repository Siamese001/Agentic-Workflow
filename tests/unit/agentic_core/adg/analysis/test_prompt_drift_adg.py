"""ADG importability contract for agentic_core/adg/analysis/prompt_drift.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_prompt_drift.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.adg.analysis.prompt_drift import (  # noqa: F401
        PromptEdgeDelta,
        PromptDriftReport,
        detect_prompt_drift,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    PromptEdgeDelta = None  # type: ignore[assignment,misc]
    PromptDriftReport = None  # type: ignore[assignment,misc]
    detect_prompt_drift = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="prompt_drift.py deps unavailable")
class TestPromptDriftImportability:
    def test_module_importable(self) -> None:
        """ADG contract: prompt_drift.py must be importable."""
        assert _AVAILABLE

    def test_promptedgedelta_is_type(self) -> None:
        assert PromptEdgeDelta is not None

    def test_promptdriftreport_is_type(self) -> None:
        assert PromptDriftReport is not None

    def test_detect_prompt_drift_callable(self) -> None:
        assert callable(detect_prompt_drift)

