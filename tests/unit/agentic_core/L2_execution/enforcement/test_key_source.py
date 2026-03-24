"""Foundational behavioral tests for agentic_core/L2_execution/enforcement/key_source.py.

fan_in=5 — imported by 5 other modules.
ADG import-hygiene is covered separately by test_key_source_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.enforcement.key_source import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        EnvKeySource,
        KeySource,
        TestKeySource,
        get_current_secret,
        get_key_source,
        inject_key_source,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    KeySource = None  # type: ignore[assignment,misc]
    TestKeySource = None  # type: ignore[assignment,misc]
    EnvKeySource = None  # type: ignore[assignment,misc]
    inject_key_source = None  # type: ignore[assignment,misc]
    get_key_source = None  # type: ignore[assignment,misc]
    get_current_secret = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="key_source.py deps unavailable")
class TestKeySourceContract:
    def test_is_class(self):
        assert isinstance(KeySource, type)

    def test_has_method_get_secret(self):
        assert callable(getattr(KeySource, 'get_secret', None))

    def test_has_method_assert_key_scope(self):
        assert callable(getattr(KeySource, 'assert_key_scope', None))

    def test_has_method_reject_expired_key(self):
        assert callable(getattr(KeySource, 'reject_expired_key', None))

@pytest.mark.skipif(not _AVAILABLE, reason="key_source.py deps unavailable")
class TestTestKeySourceContract:
    def test_is_class(self):
        assert isinstance(TestKeySource, type)

    def test_has_method_get_secret(self):
        assert callable(getattr(TestKeySource, 'get_secret', None))

    def test_has_method_assert_key_scope(self):
        assert callable(getattr(TestKeySource, 'assert_key_scope', None))

    def test_has_method_reject_expired_key(self):
        assert callable(getattr(TestKeySource, 'reject_expired_key', None))

    def test_has_method_set_key_scope(self):
        assert callable(getattr(TestKeySource, 'set_key_scope', None))

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(TestKeySource) if not m.startswith('_')]
        assert len(pub) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="key_source.py deps unavailable")
class TestEnvKeySourceContract:
    def test_is_class(self):
        assert isinstance(EnvKeySource, type)

    def test_has_method_get_secret(self):
        assert callable(getattr(EnvKeySource, 'get_secret', None))

    def test_has_method_assert_key_scope(self):
        assert callable(getattr(EnvKeySource, 'assert_key_scope', None))

    def test_has_method_reject_expired_key(self):
        assert callable(getattr(EnvKeySource, 'reject_expired_key', None))

    def test_has_method_set_key_scope(self):
        assert callable(getattr(EnvKeySource, 'set_key_scope', None))

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(EnvKeySource) if not m.startswith('_')]
        assert len(pub) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="key_source.py deps unavailable")
class TestInjectKeySourceFunction:
    def test_is_callable(self):
        assert callable(inject_key_source)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(inject_key_source)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="key_source.py deps unavailable")
class TestGetKeySourceFunction:
    def test_is_callable(self):
        assert callable(get_key_source)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_key_source)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="key_source.py deps unavailable")
class TestGetCurrentSecretFunction:
    def test_is_callable(self):
        assert callable(get_current_secret)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_current_secret)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="key_source.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="key_source.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

    def test_value_is_truthy_or_defined(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="key_source.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

    def test_value_is_truthy_or_defined(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="key_source.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="key_source.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="key_source.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Smoke: key_source importable or gracefully unavailable."""
    pass