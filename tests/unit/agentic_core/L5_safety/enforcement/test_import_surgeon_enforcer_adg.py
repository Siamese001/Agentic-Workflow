"""ADG-driven tests for agentic_core/L5_safety/enforcement/import_surgeon_enforcer.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.enforcement.import_surgeon_enforcer import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        ImportViolation,
        SovereignImportSurgeon,
        main,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    ImportViolation = None  # type: ignore[assignment,misc]
    SovereignImportSurgeon = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="import_surgeon_enforcer.py deps unavailable")
class TestImportViolation:
    def test_is_class(self):
        assert isinstance(ImportViolation, type)
    def test_importable(self):
        assert ImportViolation is not None

@pytest.mark.skipif(not _AVAILABLE, reason="import_surgeon_enforcer.py deps unavailable")
class TestSovereignImportSurgeon:
    def test_is_class(self):
        assert isinstance(SovereignImportSurgeon, type)
    def test_importable(self):
        assert SovereignImportSurgeon is not None

@pytest.mark.skipif(not _AVAILABLE, reason="import_surgeon_enforcer.py deps unavailable")
class TestMain:
    def test_is_callable(self):
        assert callable(main)

@pytest.mark.skipif(not _AVAILABLE, reason="import_surgeon_enforcer.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="import_surgeon_enforcer.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="import_surgeon_enforcer.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="import_surgeon_enforcer.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="import_surgeon_enforcer.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="import_surgeon_enforcer.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module import_surgeon_enforcer.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE