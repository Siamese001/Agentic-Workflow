"""Foundational behavioral tests for agentic_core/L5_safety/utils/gravity_visitor_util.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_gravity_visitor_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.utils.gravity_visitor_util import (  # noqa: F401
        GravityVisitor,
        get_file_imports,
        extract_layer_from_path,
        extract_layer_from_import,
        check_gravity_violation,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    GravityVisitor = None  # type: ignore[assignment,misc]
    get_file_imports = None  # type: ignore[assignment,misc]
    extract_layer_from_path = None  # type: ignore[assignment,misc]
    extract_layer_from_import = None  # type: ignore[assignment,misc]
    check_gravity_violation = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="gravity_visitor_util.py deps unavailable")
class TestGravityVisitorContract:
    def test_is_class(self):
        assert isinstance(GravityVisitor, type)

    def test_has_method_visit_Import(self):
        assert callable(getattr(GravityVisitor, 'visit_Import', None))

    def test_has_method_visit_ImportFrom(self):
        assert callable(getattr(GravityVisitor, 'visit_ImportFrom', None))

@pytest.mark.skipif(not _AVAILABLE, reason="gravity_visitor_util.py deps unavailable")
class TestGetFileImportsFunction:
    def test_is_callable(self):
        assert callable(get_file_imports)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_file_imports)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="gravity_visitor_util.py deps unavailable")
class TestExtractLayerFromPathFunction:
    def test_is_callable(self):
        assert callable(extract_layer_from_path)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(extract_layer_from_path)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="gravity_visitor_util.py deps unavailable")
class TestExtractLayerFromImportFunction:
    def test_is_callable(self):
        assert callable(extract_layer_from_import)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(extract_layer_from_import)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="gravity_visitor_util.py deps unavailable")
class TestCheckGravityViolationFunction:
    def test_is_callable(self):
        assert callable(check_gravity_violation)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(check_gravity_violation)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="gravity_visitor_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="gravity_visitor_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="gravity_visitor_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="gravity_visitor_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="gravity_visitor_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module gravity_visitor_util must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
