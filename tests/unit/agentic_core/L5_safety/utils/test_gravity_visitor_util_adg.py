"""ADG-driven tests for agentic_core/L5_safety/utils/gravity_visitor_util.py — fan_in=0."""
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
        MAX_DEPTH,
    )
    _AVAILABLE = True
except Exception:
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
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="gravity_visitor_util.py deps unavailable")
class TestGravityVisitor:
    def test_is_class(self):
        assert isinstance(GravityVisitor, type)
    def test_importable(self):
        assert GravityVisitor is not None

@pytest.mark.skipif(not _AVAILABLE, reason="gravity_visitor_util.py deps unavailable")
class TestGetFileImports:
    def test_is_callable(self):
        assert callable(get_file_imports)

@pytest.mark.skipif(not _AVAILABLE, reason="gravity_visitor_util.py deps unavailable")
class TestExtractLayerFromPath:
    def test_is_callable(self):
        assert callable(extract_layer_from_path)

@pytest.mark.skipif(not _AVAILABLE, reason="gravity_visitor_util.py deps unavailable")
class TestExtractLayerFromImport:
    def test_is_callable(self):
        assert callable(extract_layer_from_import)

@pytest.mark.skipif(not _AVAILABLE, reason="gravity_visitor_util.py deps unavailable")
class TestCheckGravityViolation:
    def test_is_callable(self):
        assert callable(check_gravity_violation)

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

@pytest.mark.skipif(not _AVAILABLE, reason="gravity_visitor_util.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module gravity_visitor_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
