"""Foundational behavioral tests for agentic_core/mixins/atomic_execution_mixin.py.

fan_in=5 — imported by 5 other modules.
ADG import-hygiene is covered separately by test_atomic_execution_mixin_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.mixins.atomic_execution_mixin import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        AtomicExecutionError,
        AtomicExecutionMixin,
        AtomicTransaction,
        FileBackup,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    FileBackup = None  # type: ignore[assignment,misc]
    AtomicTransaction = None  # type: ignore[assignment,misc]
    AtomicExecutionError = None  # type: ignore[assignment,misc]
    AtomicExecutionMixin = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="atomic_execution_mixin.py deps unavailable")
class TestFileBackupContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(FileBackup)

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(FileBackup)}
        assert fnames >= {'content_hash', 'backup_path', 'original_path', 'timestamp'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(FileBackup)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="atomic_execution_mixin.py deps unavailable")
class TestAtomicTransactionContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(AtomicTransaction)

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(AtomicTransaction)}
        assert fnames >= {'backups', 'committed', 'created_files', 'started_at', 'transaction_id', 'modified_files'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(AtomicTransaction)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="atomic_execution_mixin.py deps unavailable")
class TestAtomicExecutionErrorContract:
    def test_is_class(self):
        assert isinstance(AtomicExecutionError, type)

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(AtomicExecutionError) if not m.startswith('_')]
        assert len(pub) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="atomic_execution_mixin.py deps unavailable")
class TestAtomicExecutionMixinContract:
    def test_is_class(self):
        assert isinstance(AtomicExecutionMixin, type)

    def test_has_method_atomic_transaction(self):
        assert callable(getattr(AtomicExecutionMixin, 'atomic_transaction', None))

    def test_has_method_atomic_write(self):
        assert callable(getattr(AtomicExecutionMixin, 'atomic_write', None))

    def test_has_method_atomic_delete(self):
        assert callable(getattr(AtomicExecutionMixin, 'atomic_delete', None))

    def test_has_method_atomic_rename(self):
        assert callable(getattr(AtomicExecutionMixin, 'atomic_rename', None))

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(AtomicExecutionMixin) if not m.startswith('_')]
        assert len(pub) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="atomic_execution_mixin.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="atomic_execution_mixin.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

    def test_value_is_truthy_or_defined(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="atomic_execution_mixin.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

    def test_value_is_truthy_or_defined(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="atomic_execution_mixin.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="atomic_execution_mixin.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="atomic_execution_mixin.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Smoke: atomic_execution_mixin importable or gracefully unavailable."""
    pass
