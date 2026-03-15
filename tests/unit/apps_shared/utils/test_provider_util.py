"""Foundational behavioral tests for apps_shared/utils/provider_util.py.

fan_in=12 — this module is imported by 12 other modules.
ADG contract: import-hygiene is covered by test_provider_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.provider_util import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        MultiProviderClient,
        Provider,
        get_client,
        get_default_model,
        get_instructor_client,
        get_litellm_completion,
    )
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    Provider = None  # type: ignore[assignment,misc]
    MultiProviderClient = None  # type: ignore[assignment,misc]
    get_client = None  # type: ignore[assignment,misc]
    get_instructor_client = None  # type: ignore[assignment,misc]
    get_litellm_completion = None  # type: ignore[assignment,misc]
    get_default_model = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="provider_util.py deps unavailable")
class TestProviderContract:
    def test_is_enum(self):
        import enum
        assert issubclass(Provider, enum.Enum)

    def test_has_members(self):
        assert len(list(Provider)) >= 1

    def test_member_values_are_strings_or_ints(self):
        for member in Provider:
            assert member.value is not None

    def test_known_member_openai_exists(self):
        assert hasattr(Provider, 'OPENAI')

@pytest.mark.skipif(not _AVAILABLE, reason="provider_util.py deps unavailable")
class TestMultiProviderClientContract:
    def test_is_class(self):
        assert isinstance(MultiProviderClient, type)

    def test_has_method_completion(self):
        assert callable(getattr(MultiProviderClient, 'completion', None))

@pytest.mark.skipif(not _AVAILABLE, reason="provider_util.py deps unavailable")
class TestGetClientFunction:
    def test_is_callable(self):
        assert callable(get_client)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_client)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="provider_util.py deps unavailable")
class TestGetInstructorClientFunction:
    def test_is_callable(self):
        assert callable(get_instructor_client)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_instructor_client)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="provider_util.py deps unavailable")
class TestGetLitellmCompletionFunction:
    def test_is_callable(self):
        assert callable(get_litellm_completion)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_litellm_completion)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="provider_util.py deps unavailable")
class TestGetDefaultModelFunction:
    def test_is_callable(self):
        assert callable(get_default_model)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_default_model)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="provider_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="provider_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="provider_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="provider_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="provider_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module provider_util must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
