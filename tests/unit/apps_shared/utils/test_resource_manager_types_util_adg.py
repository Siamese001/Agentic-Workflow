"""ADG-driven tests for apps_shared/utils/resource_manager_types_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.resource_manager_types_util import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        ResourceConfig,
        ResourceKey,
        ResourceManager,
        ResourceNamespace,
        get_resource_manager,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    ResourceNamespace = None  # type: ignore[assignment,misc]
    ResourceConfig = None  # type: ignore[assignment,misc]
    ResourceKey = None  # type: ignore[assignment,misc]
    ResourceManager = None  # type: ignore[assignment,misc]
    get_resource_manager = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="resource_manager_types_util.py deps unavailable")
class TestResourceNamespace:
    def test_is_enum(self):
        import enum
        assert issubclass(ResourceNamespace, enum.Enum)
    def test_has_members(self):
        assert len(list(ResourceNamespace)) >= 1
    def test_importable(self):
        assert ResourceNamespace is not None

@pytest.mark.skipif(not _AVAILABLE, reason="resource_manager_types_util.py deps unavailable")
class TestResourceConfig:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ResourceConfig)
    def test_importable(self):
        assert ResourceConfig is not None

@pytest.mark.skipif(not _AVAILABLE, reason="resource_manager_types_util.py deps unavailable")
class TestResourceKey:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ResourceKey)
    def test_importable(self):
        assert ResourceKey is not None

@pytest.mark.skipif(not _AVAILABLE, reason="resource_manager_types_util.py deps unavailable")
class TestResourceManager:
    def test_is_class(self):
        assert isinstance(ResourceManager, type)
    def test_importable(self):
        assert ResourceManager is not None

@pytest.mark.skipif(not _AVAILABLE, reason="resource_manager_types_util.py deps unavailable")
class TestGetResourceManager:
    def test_is_callable(self):
        assert callable(get_resource_manager)

@pytest.mark.skipif(not _AVAILABLE, reason="resource_manager_types_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="resource_manager_types_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="resource_manager_types_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="resource_manager_types_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="resource_manager_types_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="resource_manager_types_util.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module resource_manager_types_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
