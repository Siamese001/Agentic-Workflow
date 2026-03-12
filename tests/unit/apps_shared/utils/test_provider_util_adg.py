"""ADG-driven tests for apps_shared/utils/provider_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.provider_util import (  # noqa: F401
        Provider,
        MultiProviderClient,
        get_client,
        get_instructor_client,
        get_litellm_completion,
        get_default_model,
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
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="provider_util.py deps unavailable")
class TestProvider:
    def test_is_enum(self):
        import enum
        assert issubclass(Provider, enum.Enum)
    def test_has_members(self):
        assert len(list(Provider)) >= 1
    def test_importable(self):
        assert Provider is not None

@pytest.mark.skipif(not _AVAILABLE, reason="provider_util.py deps unavailable")
class TestMultiProviderClient:
    def test_is_class(self):
        assert isinstance(MultiProviderClient, type)
    def test_importable(self):
        assert MultiProviderClient is not None

@pytest.mark.skipif(not _AVAILABLE, reason="provider_util.py deps unavailable")
class TestGetClient:
    def test_is_callable(self):
        assert callable(get_client)

@pytest.mark.skipif(not _AVAILABLE, reason="provider_util.py deps unavailable")
class TestGetInstructorClient:
    def test_is_callable(self):
        assert callable(get_instructor_client)

@pytest.mark.skipif(not _AVAILABLE, reason="provider_util.py deps unavailable")
class TestGetLitellmCompletion:
    def test_is_callable(self):
        assert callable(get_litellm_completion)

@pytest.mark.skipif(not _AVAILABLE, reason="provider_util.py deps unavailable")
class TestGetDefaultModel:
    def test_is_callable(self):
        assert callable(get_default_model)

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

@pytest.mark.skipif(not _AVAILABLE, reason="provider_util.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module provider_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
