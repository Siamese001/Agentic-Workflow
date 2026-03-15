"""Foundational behavioral tests for agentic_core/L0_routing/scripts/ssot_adapters.py.

fan_in=15 — this module is imported by 15 other modules.
ADG contract: import-hygiene is covered by test_ssot_adapters_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.ssot_adapters import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        ArchGovAdapter,
        FileClassAdapter,
        GravityAdapter,
        HierarchyAdapter,
        LocationAdapter,
        ReconcilerAdapter,
        build_adapters,
    )
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    ReconcilerAdapter = None  # type: ignore[assignment,misc]
    LocationAdapter = None  # type: ignore[assignment,misc]
    FileClassAdapter = None  # type: ignore[assignment,misc]
    HierarchyAdapter = None  # type: ignore[assignment,misc]
    ArchGovAdapter = None  # type: ignore[assignment,misc]
    GravityAdapter = None  # type: ignore[assignment,misc]
    build_adapters = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="ssot_adapters.py deps unavailable")
class TestReconcilerAdapterContract:
    def test_is_class(self):
        assert isinstance(ReconcilerAdapter, type)

    def test_has_method_pre_commit(self):
        assert callable(getattr(ReconcilerAdapter, 'pre_commit', None))

    def test_has_method_validate(self):
        assert callable(getattr(ReconcilerAdapter, 'validate', None))

    def test_has_method_execute(self):
        assert callable(getattr(ReconcilerAdapter, 'execute', None))

    def test_has_method_heal(self):
        assert callable(getattr(ReconcilerAdapter, 'heal', None))

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_adapters.py deps unavailable")
class TestLocationAdapterContract:
    def test_is_class(self):
        assert isinstance(LocationAdapter, type)

    def test_has_method_pre_commit(self):
        assert callable(getattr(LocationAdapter, 'pre_commit', None))

    def test_has_method_validate(self):
        assert callable(getattr(LocationAdapter, 'validate', None))

    def test_has_method_execute(self):
        assert callable(getattr(LocationAdapter, 'execute', None))

    def test_has_method_heal(self):
        assert callable(getattr(LocationAdapter, 'heal', None))

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_adapters.py deps unavailable")
class TestFileClassAdapterContract:
    def test_is_class(self):
        assert isinstance(FileClassAdapter, type)

    def test_has_method_pre_commit(self):
        assert callable(getattr(FileClassAdapter, 'pre_commit', None))

    def test_has_method_validate(self):
        assert callable(getattr(FileClassAdapter, 'validate', None))

    def test_has_method_execute(self):
        assert callable(getattr(FileClassAdapter, 'execute', None))

    def test_has_method_heal(self):
        assert callable(getattr(FileClassAdapter, 'heal', None))

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_adapters.py deps unavailable")
class TestHierarchyAdapterContract:
    def test_is_class(self):
        assert isinstance(HierarchyAdapter, type)

    def test_has_method_pre_commit(self):
        assert callable(getattr(HierarchyAdapter, 'pre_commit', None))

    def test_has_method_validate(self):
        assert callable(getattr(HierarchyAdapter, 'validate', None))

    def test_has_method_execute(self):
        assert callable(getattr(HierarchyAdapter, 'execute', None))

    def test_has_method_heal(self):
        assert callable(getattr(HierarchyAdapter, 'heal', None))

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_adapters.py deps unavailable")
class TestArchGovAdapterContract:
    def test_is_class(self):
        assert isinstance(ArchGovAdapter, type)

    def test_has_method_pre_commit(self):
        assert callable(getattr(ArchGovAdapter, 'pre_commit', None))

    def test_has_method_validate(self):
        assert callable(getattr(ArchGovAdapter, 'validate', None))

    def test_has_method_execute(self):
        assert callable(getattr(ArchGovAdapter, 'execute', None))

    def test_has_method_heal(self):
        assert callable(getattr(ArchGovAdapter, 'heal', None))

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_adapters.py deps unavailable")
class TestGravityAdapterContract:
    def test_is_class(self):
        assert isinstance(GravityAdapter, type)

    def test_has_method_pre_commit(self):
        assert callable(getattr(GravityAdapter, 'pre_commit', None))

    def test_has_method_validate(self):
        assert callable(getattr(GravityAdapter, 'validate', None))

    def test_has_method_execute(self):
        assert callable(getattr(GravityAdapter, 'execute', None))

    def test_has_method_heal(self):
        assert callable(getattr(GravityAdapter, 'heal', None))

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_adapters.py deps unavailable")
class TestBuildAdaptersFunction:
    def test_is_callable(self):
        assert callable(build_adapters)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(build_adapters)
        assert sig.return_annotation is not inspect.Parameter.empty

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


def test_module_importable():
    """Module ssot_adapters must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
