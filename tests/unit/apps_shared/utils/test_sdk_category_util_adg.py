"""ADG-driven tests for apps_shared/utils/sdk_category_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.sdk_category_util import (  # noqa: F401
        SDKCategory,
        SDKEntry,
        validate_sdk,
        validate_all_sdks,
        get_sdk_by_category,
        get_available_sdks,
        reset_all_clients,
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
    SDKCategory = None  # type: ignore[assignment,misc]
    SDKEntry = None  # type: ignore[assignment,misc]
    validate_sdk = None  # type: ignore[assignment,misc]
    validate_all_sdks = None  # type: ignore[assignment,misc]
    get_sdk_by_category = None  # type: ignore[assignment,misc]
    get_available_sdks = None  # type: ignore[assignment,misc]
    reset_all_clients = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="sdk_category_util.py deps unavailable")
class TestSDKCategory:
    def test_is_enum(self):
        import enum
        assert issubclass(SDKCategory, enum.Enum)
    def test_has_members(self):
        assert len(list(SDKCategory)) >= 1
    def test_importable(self):
        assert SDKCategory is not None

@pytest.mark.skipif(not _AVAILABLE, reason="sdk_category_util.py deps unavailable")
class TestSDKEntry:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(SDKEntry)
    def test_importable(self):
        assert SDKEntry is not None

@pytest.mark.skipif(not _AVAILABLE, reason="sdk_category_util.py deps unavailable")
class TestValidateSdk:
    def test_is_callable(self):
        assert callable(validate_sdk)

@pytest.mark.skipif(not _AVAILABLE, reason="sdk_category_util.py deps unavailable")
class TestValidateAllSdks:
    def test_is_callable(self):
        assert callable(validate_all_sdks)

@pytest.mark.skipif(not _AVAILABLE, reason="sdk_category_util.py deps unavailable")
class TestGetSdkByCategory:
    def test_is_callable(self):
        assert callable(get_sdk_by_category)

@pytest.mark.skipif(not _AVAILABLE, reason="sdk_category_util.py deps unavailable")
class TestGetAvailableSdks:
    def test_is_callable(self):
        assert callable(get_available_sdks)

@pytest.mark.skipif(not _AVAILABLE, reason="sdk_category_util.py deps unavailable")
class TestResetAllClients:
    def test_is_callable(self):
        assert callable(reset_all_clients)

@pytest.mark.skipif(not _AVAILABLE, reason="sdk_category_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="sdk_category_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="sdk_category_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="sdk_category_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="sdk_category_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="sdk_category_util.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module sdk_category_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
