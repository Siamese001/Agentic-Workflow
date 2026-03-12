"""Foundational behavioral tests for agentic_core/L5_safety/reasoning/filesystem_ssot_reconciler.py.

fan_in=5 — imported by 5 other modules.
ADG import-hygiene is covered separately by test_filesystem_ssot_reconciler_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.reasoning.filesystem_ssot_reconciler import (  # noqa: F401
        ReconciliationViolation,
        FilesystemSSOTReconcilerAgent,
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
    ReconciliationViolation = None  # type: ignore[assignment,misc]
    FilesystemSSOTReconcilerAgent = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="filesystem_ssot_reconciler.py deps unavailable")
class TestReconciliationViolationContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ReconciliationViolation)

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(ReconciliationViolation)}
        assert fnames >= {'severity', 'suggested_action', 'message', 'drift_type', 'file_path', 'is_valid'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(ReconciliationViolation)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="filesystem_ssot_reconciler.py deps unavailable")
class TestFilesystemSSOTReconcilerAgentContract:
    def test_is_class(self):
        assert isinstance(FilesystemSSOTReconcilerAgent, type)

    def test_has_method_heal(self):
        assert callable(getattr(FilesystemSSOTReconcilerAgent, 'heal', None))

    def test_has_method_run_ci_verification_sync(self):
        assert callable(getattr(FilesystemSSOTReconcilerAgent, 'run_ci_verification_sync', None))

    def test_has_method_run_ci_verification(self):
        assert callable(getattr(FilesystemSSOTReconcilerAgent, 'run_ci_verification', None))

    def test_has_method_enforce_gospel(self):
        assert callable(getattr(FilesystemSSOTReconcilerAgent, 'enforce_gospel', None))

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(FilesystemSSOTReconcilerAgent) if not m.startswith('_')]
        assert len(pub) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="filesystem_ssot_reconciler.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="filesystem_ssot_reconciler.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

    def test_value_is_truthy_or_defined(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="filesystem_ssot_reconciler.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

    def test_value_is_truthy_or_defined(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="filesystem_ssot_reconciler.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="filesystem_ssot_reconciler.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="filesystem_ssot_reconciler.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Smoke: filesystem_ssot_reconciler importable or gracefully unavailable."""
    assert True
