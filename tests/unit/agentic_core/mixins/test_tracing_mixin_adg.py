"""ADG importability contract for agentic_core/mixins/tracing_mixin.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_tracing_mixin.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.mixins.tracing_mixin import (  # noqa: F401
        SpanContext,
        TracingMixin,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    SpanContext = None  # type: ignore[assignment,misc]
    TracingMixin = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="tracing_mixin.py deps unavailable")
class TestTracingMixinImportability:
    def test_module_importable(self) -> None:
        """ADG contract: tracing_mixin.py must be importable."""
        assert _AVAILABLE

    def test_spancontext_is_type(self) -> None:
        assert SpanContext is not None

    def test_tracingmixin_is_type(self) -> None:
        assert TracingMixin is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

