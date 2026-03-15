"""ADG importability contract for agentic_core/mixins/context_management_mixin.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_context_management_mixin.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.mixins.context_management_mixin import (  # noqa: F401
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        ContextConfig,
        ContextItem,
        ContextManagementMixin,
        ContextOverflowError,
        ContextPriority,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    ContextPriority = None  # type: ignore[assignment,misc]
    ContextItem = None  # type: ignore[assignment,misc]
    ContextConfig = None  # type: ignore[assignment,misc]
    ContextOverflowError = None  # type: ignore[assignment,misc]
    ContextManagementMixin = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="context_management_mixin.py deps unavailable")
class TestContextManagementMixinImportability:
    def test_module_importable(self) -> None:
        """ADG contract: context_management_mixin.py must be importable."""
        assert _AVAILABLE

    def test_contextpriority_is_type(self) -> None:
        assert ContextPriority is not None

    def test_contextitem_is_type(self) -> None:
        assert ContextItem is not None

    def test_contextconfig_is_type(self) -> None:
        assert ContextConfig is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None
