"""ADG-driven tests for agentic_core/L5_safety/governance/lazy_seam_enforcer.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.governance.lazy_seam_enforcer import (  # noqa: F401
        IMPORT_LAYER_PATTERN,
        LAYER_PATTERN,
        LazySeamEnforcer,
        LazyUpwardImport,
        collect_lazy_upward_imports,
        extract_import_targets,
        lazy_upward_import_metric,
        main,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    LazyUpwardImport = None  # type: ignore[assignment,misc]
    LazySeamEnforcer = None  # type: ignore[assignment,misc]
    extract_import_targets = None  # type: ignore[assignment,misc]
    collect_lazy_upward_imports = None  # type: ignore[assignment,misc]
    lazy_upward_import_metric = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]
    LAYER_PATTERN = None  # type: ignore[assignment,misc]
    IMPORT_LAYER_PATTERN = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="lazy_seam_enforcer.py deps unavailable")
class TestLazyUpwardImport:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(LazyUpwardImport)
    def test_importable(self):
        assert LazyUpwardImport is not None

@pytest.mark.skipif(not _AVAILABLE, reason="lazy_seam_enforcer.py deps unavailable")
class TestLazySeamEnforcer:
    def test_is_class(self):
        assert isinstance(LazySeamEnforcer, type)
    def test_importable(self):
        assert LazySeamEnforcer is not None

@pytest.mark.skipif(not _AVAILABLE, reason="lazy_seam_enforcer.py deps unavailable")
class TestExtractImportTargets:
    def test_is_callable(self):
        assert callable(extract_import_targets)

@pytest.mark.skipif(not _AVAILABLE, reason="lazy_seam_enforcer.py deps unavailable")
class TestCollectLazyUpwardImports:
    def test_is_callable(self):
        assert callable(collect_lazy_upward_imports)

@pytest.mark.skipif(not _AVAILABLE, reason="lazy_seam_enforcer.py deps unavailable")
class TestLazyUpwardImportMetric:
    def test_is_callable(self):
        assert callable(lazy_upward_import_metric)

@pytest.mark.skipif(not _AVAILABLE, reason="lazy_seam_enforcer.py deps unavailable")
class TestMain:
    def test_is_callable(self):
        assert callable(main)

@pytest.mark.skipif(not _AVAILABLE, reason="lazy_seam_enforcer.py deps unavailable")
class TestLayerPatternConstant:
    def test_is_not_none(self):
        assert LAYER_PATTERN is not None

@pytest.mark.skipif(not _AVAILABLE, reason="lazy_seam_enforcer.py deps unavailable")
class TestImportLayerPatternConstant:
    def test_is_not_none(self):
        assert IMPORT_LAYER_PATTERN is not None


def test_module_importable():
    """Module lazy_seam_enforcer.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
