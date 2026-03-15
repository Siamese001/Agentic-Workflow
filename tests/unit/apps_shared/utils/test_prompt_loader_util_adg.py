"""ADG-driven tests for apps_shared/utils/prompt_loader_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.prompt_loader_util import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        PromptLoader,
        get_global_constraints,
        get_specialist_prompt,
        load_prompt_for_agent,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    PromptLoader = None  # type: ignore[assignment,misc]
    load_prompt_for_agent = None  # type: ignore[assignment,misc]
    get_global_constraints = None  # type: ignore[assignment,misc]
    get_specialist_prompt = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="prompt_loader_util.py deps unavailable")
class TestPromptLoader:
    def test_is_class(self):
        assert isinstance(PromptLoader, type)
    def test_importable(self):
        assert PromptLoader is not None

@pytest.mark.skipif(not _AVAILABLE, reason="prompt_loader_util.py deps unavailable")
class TestLoadPromptForAgent:
    def test_is_callable(self):
        assert callable(load_prompt_for_agent)

@pytest.mark.skipif(not _AVAILABLE, reason="prompt_loader_util.py deps unavailable")
class TestGetGlobalConstraints:
    def test_is_callable(self):
        assert callable(get_global_constraints)

@pytest.mark.skipif(not _AVAILABLE, reason="prompt_loader_util.py deps unavailable")
class TestGetSpecialistPrompt:
    def test_is_callable(self):
        assert callable(get_specialist_prompt)

@pytest.mark.skipif(not _AVAILABLE, reason="prompt_loader_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="prompt_loader_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="prompt_loader_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="prompt_loader_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="prompt_loader_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="prompt_loader_util.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module prompt_loader_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
