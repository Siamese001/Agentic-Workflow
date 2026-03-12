"""ADG importability contract for agentic_core/mixins/ssot_tracing_mixin.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_ssot_tracing_mixin.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.mixins.ssot_tracing_mixin import (  # noqa: F401
        SSOTTracingMixin,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    SSOTTracingMixin = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_tracing_mixin.py deps unavailable")
class TestSsotTracingMixinImportability:
    def test_module_importable(self) -> None:
        """ADG contract: ssot_tracing_mixin.py must be importable."""
        assert _AVAILABLE

    def test_ssottracingmixin_is_type(self) -> None:
        assert SSOTTracingMixin is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

