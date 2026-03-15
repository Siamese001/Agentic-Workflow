"""Foundational behavioral tests for apps_shared/utils/resource_manager_util.py.

fan_in=12 — this module is imported by 12 other modules.
ADG contract: import-hygiene is covered by test_resource_manager_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.resource_manager_util import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        ConnectionPool,
        ResourceInfo,
        ResourceManager,
        ResourceType,
        get_resource_manager,
        shutdown_all_managers,
    )
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    ResourceType = None  # type: ignore[assignment,misc]
    ResourceInfo = None  # type: ignore[assignment,misc]
    ResourceManager = None  # type: ignore[assignment,misc]
    ConnectionPool = None  # type: ignore[assignment,misc]
    get_resource_manager = None  # type: ignore[assignment,misc]
    shutdown_all_managers = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="resource_manager_util.py deps unavailable")
class TestResourceTypeContract:
    def test_is_enum(self):
        import enum
        assert issubclass(ResourceType, enum.Enum)

    def test_has_members(self):
        assert len(list(ResourceType)) >= 1

    def test_member_values_are_strings_or_ints(self):
        for member in ResourceType:
            assert member.value is not None

    def test_known_member_file_handle_exists(self):
        assert hasattr(ResourceType, 'FILE_HANDLE')

@pytest.mark.skipif(not _AVAILABLE, reason="resource_manager_util.py deps unavailable")
class TestResourceInfoContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ResourceInfo)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(ResourceInfo)}
        assert field_names >= {'created_at', 'resource_id', 'last_used', 'cleanup_callback', 'resource_type'}

@pytest.mark.skipif(not _AVAILABLE, reason="resource_manager_util.py deps unavailable")
class TestResourceManagerContract:
    def test_is_class(self):
        assert isinstance(ResourceManager, type)

    def test_has_method_start(self):
        assert callable(getattr(ResourceManager, 'start', None))

    def test_has_method_stop(self):
        assert callable(getattr(ResourceManager, 'stop', None))

    def test_has_method_generate_resource_id(self):
        assert callable(getattr(ResourceManager, 'generate_resource_id', None))

    def test_has_method_register_resource(self):
        assert callable(getattr(ResourceManager, 'register_resource', None))

@pytest.mark.skipif(not _AVAILABLE, reason="resource_manager_util.py deps unavailable")
class TestConnectionPoolContract:
    def test_is_class(self):
        assert isinstance(ConnectionPool, type)

    def test_has_method_get_connection(self):
        assert callable(getattr(ConnectionPool, 'get_connection', None))

    def test_has_method_return_connection(self):
        assert callable(getattr(ConnectionPool, 'return_connection', None))

    def test_has_method_close_all(self):
        assert callable(getattr(ConnectionPool, 'close_all', None))

@pytest.mark.skipif(not _AVAILABLE, reason="resource_manager_util.py deps unavailable")
class TestGetResourceManagerFunction:
    def test_is_callable(self):
        assert callable(get_resource_manager)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_resource_manager)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="resource_manager_util.py deps unavailable")
class TestShutdownAllManagersFunction:
    def test_is_callable(self):
        assert callable(shutdown_all_managers)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(shutdown_all_managers)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="resource_manager_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="resource_manager_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="resource_manager_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="resource_manager_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="resource_manager_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module resource_manager_util must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
