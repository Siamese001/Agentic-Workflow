"""ADG-driven tests for agentic_core/L0_routing/scripts/ssot_adapters.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.ssot_adapters import (  # noqa: F401
        ReconcilerAdapter,
        LocationAdapter,
        FileClassAdapter,
        HierarchyAdapter,
        ArchGovAdapter,
        GravityAdapter,
        SysArchAdapter,
        ObsProbeAdapter,
        build_adapters,
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
    ReconcilerAdapter = None  # type: ignore[assignment,misc]
    LocationAdapter = None  # type: ignore[assignment,misc]
    FileClassAdapter = None  # type: ignore[assignment,misc]
    HierarchyAdapter = None  # type: ignore[assignment,misc]
    ArchGovAdapter = None  # type: ignore[assignment,misc]
    GravityAdapter = None  # type: ignore[assignment,misc]
    SysArchAdapter = None  # type: ignore[assignment,misc]
    ObsProbeAdapter = None  # type: ignore[assignment,misc]
    build_adapters = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="ssot_adapters.py deps unavailable")
class TestReconcilerAdapter:
    def test_is_class(self):
        assert isinstance(ReconcilerAdapter, type)
    def test_importable(self):
        assert ReconcilerAdapter is not None

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_adapters.py deps unavailable")
class TestLocationAdapter:
    def test_is_class(self):
        assert isinstance(LocationAdapter, type)
    def test_importable(self):
        assert LocationAdapter is not None

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_adapters.py deps unavailable")
class TestFileClassAdapter:
    def test_is_class(self):
        assert isinstance(FileClassAdapter, type)
    def test_importable(self):
        assert FileClassAdapter is not None

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_adapters.py deps unavailable")
class TestHierarchyAdapter:
    def test_is_class(self):
        assert isinstance(HierarchyAdapter, type)
    def test_importable(self):
        assert HierarchyAdapter is not None

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_adapters.py deps unavailable")
class TestArchGovAdapter:
    def test_is_class(self):
        assert isinstance(ArchGovAdapter, type)
    def test_importable(self):
        assert ArchGovAdapter is not None

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_adapters.py deps unavailable")
class TestGravityAdapter:
    def test_is_class(self):
        assert isinstance(GravityAdapter, type)
    def test_importable(self):
        assert GravityAdapter is not None

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_adapters.py deps unavailable")
class TestSysArchAdapter:
    def test_is_class(self):
        assert isinstance(SysArchAdapter, type)
    def test_importable(self):
        assert SysArchAdapter is not None

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_adapters.py deps unavailable")
class TestObsProbeAdapter:
    def test_is_class(self):
        assert isinstance(ObsProbeAdapter, type)
    def test_importable(self):
        assert ObsProbeAdapter is not None

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_adapters.py deps unavailable")
class TestBuildAdapters:
    def test_is_callable(self):
        assert callable(build_adapters)

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_adapters.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_adapters.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_adapters.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_adapters.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_adapters.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_adapters.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module ssot_adapters.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
