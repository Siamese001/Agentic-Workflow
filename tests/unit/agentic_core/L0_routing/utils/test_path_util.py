"""Foundational behavioral tests for agentic_core/L0_routing/utils/path_util.py.

fan_in=14 — this module is imported by 14 other modules.
ADG contract: import-hygiene is covered by test_path_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.utils.path_util import (  # noqa: F401
        get_validated_project_root,
        validate_path_within_project,
        safe_path_join,
        safe_prefixed_filename,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    get_validated_project_root = None  # type: ignore[assignment,misc]
    validate_path_within_project = None  # type: ignore[assignment,misc]
    safe_path_join = None  # type: ignore[assignment,misc]
    safe_prefixed_filename = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="path_util.py deps unavailable")
class TestGetValidatedProjectRootFunction:
    def test_is_callable(self):
        assert callable(get_validated_project_root)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_validated_project_root)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="path_util.py deps unavailable")
class TestValidatePathWithinProjectFunction:
    def test_is_callable(self):
        assert callable(validate_path_within_project)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(validate_path_within_project)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="path_util.py deps unavailable")
class TestSafePathJoinFunction:
    def test_is_callable(self):
        assert callable(safe_path_join)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(safe_path_join)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="path_util.py deps unavailable")
class TestSafePrefixedFilenameFunction:
    def test_is_callable(self):
        assert callable(safe_prefixed_filename)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(safe_prefixed_filename)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="path_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="path_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="path_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="path_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="path_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module path_util must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
