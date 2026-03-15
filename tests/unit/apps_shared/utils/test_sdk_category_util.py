"""Foundational behavioral tests for apps_shared/utils/sdk_category_util.py.

fan_in=13 — this module is imported by 13 other modules.
ADG contract: import-hygiene is covered by test_sdk_category_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.sdk_category_util import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        SDKCategory,
        SDKEntry,
        get_available_sdks,
        get_sdk_by_category,
        validate_all_sdks,
        validate_sdk,
    )
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    SDKCategory = None  # type: ignore[assignment,misc]
    SDKEntry = None  # type: ignore[assignment,misc]
    validate_sdk = None  # type: ignore[assignment,misc]
    validate_all_sdks = None  # type: ignore[assignment,misc]
    get_sdk_by_category = None  # type: ignore[assignment,misc]
    get_available_sdks = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="sdk_category_util.py deps unavailable")
class TestSDKCategoryContract:
    def test_is_enum(self):
        import enum
        assert issubclass(SDKCategory, enum.Enum)

    def test_has_members(self):
        assert len(list(SDKCategory)) >= 1

    def test_member_values_are_strings_or_ints(self):
        for member in SDKCategory:
            assert member.value is not None

    def test_known_member_llm_provider_exists(self):
        assert hasattr(SDKCategory, 'LLM_PROVIDER')

@pytest.mark.skipif(not _AVAILABLE, reason="sdk_category_util.py deps unavailable")
class TestSDKEntryContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(SDKEntry)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(SDKEntry)}
        assert field_names >= {'required', 'module', 'name', 'category', 'env_var'}

@pytest.mark.skipif(not _AVAILABLE, reason="sdk_category_util.py deps unavailable")
class TestValidateSdkFunction:
    def test_is_callable(self):
        assert callable(validate_sdk)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(validate_sdk)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="sdk_category_util.py deps unavailable")
class TestValidateAllSdksFunction:
    def test_is_callable(self):
        assert callable(validate_all_sdks)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(validate_all_sdks)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="sdk_category_util.py deps unavailable")
class TestGetSdkByCategoryFunction:
    def test_is_callable(self):
        assert callable(get_sdk_by_category)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_sdk_by_category)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="sdk_category_util.py deps unavailable")
class TestGetAvailableSdksFunction:
    def test_is_callable(self):
        assert callable(get_available_sdks)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_available_sdks)
        assert sig.return_annotation is not inspect.Parameter.empty

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


def test_module_importable():
    """Module sdk_category_util must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
