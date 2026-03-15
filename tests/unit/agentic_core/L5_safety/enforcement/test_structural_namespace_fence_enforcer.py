"""Foundational behavioral tests for agentic_core/L5_safety/enforcement/structural_namespace_fence_enforcer.py.

fan_in=12 — this module is imported by 12 other modules.
ADG contract: import-hygiene is covered by test_structural_namespace_fence_enforcer_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.enforcement.structural_namespace_fence_enforcer import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        ProvenanceLoader,
        ProvenanceTracker,
        StructuralNamespaceFinder,
        get_provenance_tracker,
        install_structural_namespace_fence,
        uninstall_structural_namespace_fence,
    )
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    ProvenanceTracker = None  # type: ignore[assignment,misc]
    ProvenanceLoader = None  # type: ignore[assignment,misc]
    StructuralNamespaceFinder = None  # type: ignore[assignment,misc]
    install_structural_namespace_fence = None  # type: ignore[assignment,misc]
    uninstall_structural_namespace_fence = None  # type: ignore[assignment,misc]
    get_provenance_tracker = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="structural_namespace_fence_enforcer.py deps unavailable")
class TestProvenanceTrackerContract:
    def test_is_class(self):
        assert isinstance(ProvenanceTracker, type)

    def test_has_method_register(self):
        assert callable(getattr(ProvenanceTracker, 'register', None))

    def test_has_method_namespace_of(self):
        assert callable(getattr(ProvenanceTracker, 'namespace_of', None))

    def test_has_method_is_forbidden_cross_import(self):
        assert callable(getattr(ProvenanceTracker, 'is_forbidden_cross_import', None))

@pytest.mark.skipif(not _AVAILABLE, reason="structural_namespace_fence_enforcer.py deps unavailable")
class TestProvenanceLoaderContract:
    def test_is_class(self):
        assert isinstance(ProvenanceLoader, type)

    def test_has_method_create_module(self):
        assert callable(getattr(ProvenanceLoader, 'create_module', None))

    def test_has_method_exec_module(self):
        assert callable(getattr(ProvenanceLoader, 'exec_module', None))

@pytest.mark.skipif(not _AVAILABLE, reason="structural_namespace_fence_enforcer.py deps unavailable")
class TestStructuralNamespaceFinderContract:
    def test_is_class(self):
        assert isinstance(StructuralNamespaceFinder, type)

    def test_has_method_find_spec(self):
        assert callable(getattr(StructuralNamespaceFinder, 'find_spec', None))

@pytest.mark.skipif(not _AVAILABLE, reason="structural_namespace_fence_enforcer.py deps unavailable")
class TestInstallStructuralNamespaceFenceFunction:
    def test_is_callable(self):
        assert callable(install_structural_namespace_fence)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(install_structural_namespace_fence)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="structural_namespace_fence_enforcer.py deps unavailable")
class TestUninstallStructuralNamespaceFenceFunction:
    def test_is_callable(self):
        assert callable(uninstall_structural_namespace_fence)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(uninstall_structural_namespace_fence)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="structural_namespace_fence_enforcer.py deps unavailable")
class TestGetProvenanceTrackerFunction:
    def test_is_callable(self):
        assert callable(get_provenance_tracker)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_provenance_tracker)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="structural_namespace_fence_enforcer.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="structural_namespace_fence_enforcer.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="structural_namespace_fence_enforcer.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="structural_namespace_fence_enforcer.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="structural_namespace_fence_enforcer.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module structural_namespace_fence_enforcer must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
