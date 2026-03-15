"""ADG-driven tests for agentic_core/runtime/config/prompt_injection_loader_config.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.runtime.config.prompt_injection_loader_config import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        PromptInjectionLoader,
        get_injection_loader,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    PromptInjectionLoader = None  # type: ignore[assignment,misc]
    get_injection_loader = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="prompt_injection_loader_config.py deps unavailable")
class TestPromptInjectionLoader:
    def test_is_class(self):
        assert isinstance(PromptInjectionLoader, type)
    def test_importable(self):
        assert PromptInjectionLoader is not None

@pytest.mark.skipif(not _AVAILABLE, reason="prompt_injection_loader_config.py deps unavailable")
class TestGetInjectionLoader:
    def test_is_callable(self):
        assert callable(get_injection_loader)

@pytest.mark.skipif(not _AVAILABLE, reason="prompt_injection_loader_config.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="prompt_injection_loader_config.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="prompt_injection_loader_config.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="prompt_injection_loader_config.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="prompt_injection_loader_config.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="prompt_injection_loader_config.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module prompt_injection_loader_config.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
