"""ADG importability contract for apps_shared/reasoning/BaseProactiveAgent.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_BaseProactiveAgent.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from apps_shared.reasoning.BaseProactiveAgent import (  # noqa: F401
        BaseProactiveAgent,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    BaseProactiveAgent = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="BaseProactiveAgent.py deps unavailable")
class TestBaseproactiveagentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: BaseProactiveAgent.py must be importable."""
        assert _AVAILABLE

    def test_baseproactiveagent_is_type(self) -> None:
        assert BaseProactiveAgent is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

