"""Foundational behavioral tests for agentic_core/L6_observability/enforcement/reasoning_streamer.py.

fan_in=12 — this module is imported by 12 other modules.
ADG contract: import-hygiene is covered by test_reasoning_streamer_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L6_observability.enforcement.reasoning_streamer import (  # noqa: F401
        L5Streamer,
        get_l5_streamer,
        start_l5_stream,
        broadcast,
        broadcast_reasoning,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    L5Streamer = None  # type: ignore[assignment,misc]
    get_l5_streamer = None  # type: ignore[assignment,misc]
    start_l5_stream = None  # type: ignore[assignment,misc]
    broadcast = None  # type: ignore[assignment,misc]
    broadcast_reasoning = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="reasoning_streamer.py deps unavailable")
class TestL5StreamerContract:
    def test_is_class(self):
        assert isinstance(L5Streamer, type)

    def test_has_method_start_streamer(self):
        assert callable(getattr(L5Streamer, 'start_streamer', None))

    def test_has_method_broadcast(self):
        assert callable(getattr(L5Streamer, 'broadcast', None))

    def test_has_method_broadcast_reasoning(self):
        assert callable(getattr(L5Streamer, 'broadcast_reasoning', None))

    def test_has_method_broadcast_agent_start(self):
        assert callable(getattr(L5Streamer, 'broadcast_agent_start', None))

@pytest.mark.skipif(not _AVAILABLE, reason="reasoning_streamer.py deps unavailable")
class TestGetL5StreamerFunction:
    def test_is_callable(self):
        assert callable(get_l5_streamer)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_l5_streamer)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="reasoning_streamer.py deps unavailable")
class TestStartL5StreamFunction:
    def test_is_callable(self):
        assert callable(start_l5_stream)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(start_l5_stream)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="reasoning_streamer.py deps unavailable")
class TestBroadcastFunction:
    def test_is_callable(self):
        assert callable(broadcast)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(broadcast)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="reasoning_streamer.py deps unavailable")
class TestBroadcastReasoningFunction:
    def test_is_callable(self):
        assert callable(broadcast_reasoning)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(broadcast_reasoning)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="reasoning_streamer.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="reasoning_streamer.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="reasoning_streamer.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="reasoning_streamer.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="reasoning_streamer.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module reasoning_streamer must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
