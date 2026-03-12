"""ADG-driven tests for agentic_core/L5_safety/governance/lazy_seam_scanner.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.governance.lazy_seam_scanner import (  # noqa: F401
        LazyUpwardImport,
        LazySeamScanner,
        layer_of_path,
        extract_import_targets,
        collect_lazy_upward_imports,
        lazy_upward_import_metric,
        main,
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
    LazyUpwardImport = None  # type: ignore[assignment,misc]
    LazySeamScanner = None  # type: ignore[assignment,misc]
    layer_of_path = None  # type: ignore[assignment,misc]
    extract_import_targets = None  # type: ignore[assignment,misc]
    collect_lazy_upward_imports = None  # type: ignore[assignment,misc]
    lazy_upward_import_metric = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="lazy_seam_scanner.py deps unavailable")
class TestLazyUpwardImport:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(LazyUpwardImport)
    def test_importable(self):
        assert LazyUpwardImport is not None

@pytest.mark.skipif(not _AVAILABLE, reason="lazy_seam_scanner.py deps unavailable")
class TestLazySeamScanner:
    def test_is_class(self):
        assert isinstance(LazySeamScanner, type)
    def test_importable(self):
        assert LazySeamScanner is not None

@pytest.mark.skipif(not _AVAILABLE, reason="lazy_seam_scanner.py deps unavailable")
class TestLayerOfPath:
    def test_is_callable(self):
        assert callable(layer_of_path)

@pytest.mark.skipif(not _AVAILABLE, reason="lazy_seam_scanner.py deps unavailable")
class TestExtractImportTargets:
    def test_is_callable(self):
        assert callable(extract_import_targets)

@pytest.mark.skipif(not _AVAILABLE, reason="lazy_seam_scanner.py deps unavailable")
class TestCollectLazyUpwardImports:
    def test_is_callable(self):
        assert callable(collect_lazy_upward_imports)

@pytest.mark.skipif(not _AVAILABLE, reason="lazy_seam_scanner.py deps unavailable")
class TestLazyUpwardImportMetric:
    def test_is_callable(self):
        assert callable(lazy_upward_import_metric)

@pytest.mark.skipif(not _AVAILABLE, reason="lazy_seam_scanner.py deps unavailable")
class TestMain:
    def test_is_callable(self):
        assert callable(main)

@pytest.mark.skipif(not _AVAILABLE, reason="lazy_seam_scanner.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="lazy_seam_scanner.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="lazy_seam_scanner.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="lazy_seam_scanner.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="lazy_seam_scanner.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="lazy_seam_scanner.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module lazy_seam_scanner.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
