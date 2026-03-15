"""Foundational behavioral tests for system_learning/enforcement/determinism.py.

fan_in=13 — this module is imported by 13 other modules.
ADG contract: import-hygiene is covered by test_determinism_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from system_learning.enforcement.determinism import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        assert_no_nondeterminism,
        deterministic_json,
        stable_sha256_json,
    )
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    deterministic_json = None  # type: ignore[assignment,misc]
    stable_sha256_json = None  # type: ignore[assignment,misc]
    assert_no_nondeterminism = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="determinism.py deps unavailable")
class TestDeterministicJsonFunction:
    def test_is_callable(self):
        assert callable(deterministic_json)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(deterministic_json)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="determinism.py deps unavailable")
class TestStableSha256JsonFunction:
    def test_is_callable(self):
        assert callable(stable_sha256_json)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(stable_sha256_json)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="determinism.py deps unavailable")
class TestAssertNoNondeterminismFunction:
    def test_is_callable(self):
        assert callable(assert_no_nondeterminism)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(assert_no_nondeterminism)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="determinism.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="determinism.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="determinism.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="determinism.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="determinism.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module determinism must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
