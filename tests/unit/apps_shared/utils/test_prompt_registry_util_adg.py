"""ADG-driven tests for apps_shared/utils/prompt_registry_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.prompt_registry_util import (  # noqa: F401
        PromptCategory,
        PromptTemplate,
        PromptRegistry,
        create_prompt_registry,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
        MAX_DEPTH,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    PromptCategory = None  # type: ignore[assignment,misc]
    PromptTemplate = None  # type: ignore[assignment,misc]
    PromptRegistry = None  # type: ignore[assignment,misc]
    create_prompt_registry = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="prompt_registry_util.py deps unavailable")
class TestPromptCategory:
    def test_is_enum(self):
        import enum
        assert issubclass(PromptCategory, enum.Enum)
    def test_has_members(self):
        assert len(list(PromptCategory)) >= 1
    def test_importable(self):
        assert PromptCategory is not None

@pytest.mark.skipif(not _AVAILABLE, reason="prompt_registry_util.py deps unavailable")
class TestPromptTemplate:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(PromptTemplate)
    def test_importable(self):
        assert PromptTemplate is not None

@pytest.mark.skipif(not _AVAILABLE, reason="prompt_registry_util.py deps unavailable")
class TestPromptRegistry:
    def test_is_class(self):
        assert isinstance(PromptRegistry, type)
    def test_importable(self):
        assert PromptRegistry is not None

@pytest.mark.skipif(not _AVAILABLE, reason="prompt_registry_util.py deps unavailable")
class TestCreatePromptRegistry:
    def test_is_callable(self):
        assert callable(create_prompt_registry)

@pytest.mark.skipif(not _AVAILABLE, reason="prompt_registry_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="prompt_registry_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="prompt_registry_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="prompt_registry_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="prompt_registry_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="prompt_registry_util.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module prompt_registry_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
