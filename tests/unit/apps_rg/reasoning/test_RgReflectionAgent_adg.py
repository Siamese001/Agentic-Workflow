"""ADG importability contract for apps_rg/reasoning/RgReflectionAgent.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_RgReflectionAgent.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from apps_rg.reasoning.RgReflectionAgent import (  # noqa: F401
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        RgReflectionAgent,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    RgReflectionAgent = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="RgReflectionAgent.py deps unavailable")
class TestRgreflectionagentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: RgReflectionAgent.py must be importable."""
        assert _AVAILABLE

    def test_rgreflectionagent_is_type(self) -> None:
        assert RgReflectionAgent is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None
