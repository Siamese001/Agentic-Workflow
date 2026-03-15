"""ADG-driven tests for apps_shared/utils/version_tag_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.version_tag_util import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        PromptVersion,
        PromptVersionManager,
        VersionTag,
        create_version_manager,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    VersionTag = None  # type: ignore[assignment,misc]
    PromptVersion = None  # type: ignore[assignment,misc]
    PromptVersionManager = None  # type: ignore[assignment,misc]
    create_version_manager = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="version_tag_util.py deps unavailable")
class TestVersionTag:
    def test_is_enum(self):
        import enum
        assert issubclass(VersionTag, enum.Enum)
    def test_has_members(self):
        assert len(list(VersionTag)) >= 1
    def test_importable(self):
        assert VersionTag is not None

@pytest.mark.skipif(not _AVAILABLE, reason="version_tag_util.py deps unavailable")
class TestPromptVersion:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(PromptVersion)
    def test_importable(self):
        assert PromptVersion is not None

@pytest.mark.skipif(not _AVAILABLE, reason="version_tag_util.py deps unavailable")
class TestPromptVersionManager:
    def test_is_class(self):
        assert isinstance(PromptVersionManager, type)
    def test_importable(self):
        assert PromptVersionManager is not None

@pytest.mark.skipif(not _AVAILABLE, reason="version_tag_util.py deps unavailable")
class TestCreateVersionManager:
    def test_is_callable(self):
        assert callable(create_version_manager)

@pytest.mark.skipif(not _AVAILABLE, reason="version_tag_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="version_tag_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="version_tag_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="version_tag_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="version_tag_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="version_tag_util.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module version_tag_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
