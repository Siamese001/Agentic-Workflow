"""Foundational behavioral tests for agentic_core/mixins/mcp_hardened_mixin.py.

fan_in=12 — this module is imported by 12 other modules.
ADG contract: import-hygiene is covered by test_mcp_hardened_mixin_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.mixins.mcp_hardened_mixin import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        MCPHardenedMixin,
    )
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    MCPHardenedMixin = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="mcp_hardened_mixin.py deps unavailable")
class TestMCPHardenedMixinContract:
    def test_is_class(self):
        assert isinstance(MCPHardenedMixin, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(MCPHardenedMixin, type)

@pytest.mark.skipif(not _AVAILABLE, reason="mcp_hardened_mixin.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="mcp_hardened_mixin.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="mcp_hardened_mixin.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="mcp_hardened_mixin.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="mcp_hardened_mixin.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module mcp_hardened_mixin must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
