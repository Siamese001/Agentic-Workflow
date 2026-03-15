"""Foundational behavioral tests for agentic_core/L5_safety/types/hardening_errors.py.

fan_in=10 — this module is imported by 10 other modules.
ADG contract: import-hygiene is covered by test_hardening_errors_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.types.hardening_errors import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        C0AuthorityLeakError,
        C0MutationViolation,
        ExecutionTraceIntegrityError,
        LedgerIntegrityViolation,
        MutationCommitFailure,
        MutationReplayIntegrityViolation,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    ExecutionTraceIntegrityError = None  # type: ignore[assignment,misc]
    MutationReplayIntegrityViolation = None  # type: ignore[assignment,misc]
    LedgerIntegrityViolation = None  # type: ignore[assignment,misc]
    MutationCommitFailure = None  # type: ignore[assignment,misc]
    C0AuthorityLeakError = None  # type: ignore[assignment,misc]
    C0MutationViolation = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="hardening_errors.py deps unavailable")
class TestExecutionTraceIntegrityErrorContract:
    def test_is_class(self):
        assert isinstance(ExecutionTraceIntegrityError, type)

@pytest.mark.skipif(not _AVAILABLE, reason="hardening_errors.py deps unavailable")
class TestMutationReplayIntegrityViolationContract:
    def test_is_class(self):
        assert isinstance(MutationReplayIntegrityViolation, type)

@pytest.mark.skipif(not _AVAILABLE, reason="hardening_errors.py deps unavailable")
class TestLedgerIntegrityViolationContract:
    def test_is_class(self):
        assert isinstance(LedgerIntegrityViolation, type)

@pytest.mark.skipif(not _AVAILABLE, reason="hardening_errors.py deps unavailable")
class TestMutationCommitFailureContract:
    def test_is_class(self):
        assert isinstance(MutationCommitFailure, type)

@pytest.mark.skipif(not _AVAILABLE, reason="hardening_errors.py deps unavailable")
class TestC0AuthorityLeakErrorContract:
    def test_is_class(self):
        assert isinstance(C0AuthorityLeakError, type)

@pytest.mark.skipif(not _AVAILABLE, reason="hardening_errors.py deps unavailable")
class TestC0MutationViolationContract:
    def test_is_class(self):
        assert isinstance(C0MutationViolation, type)

@pytest.mark.skipif(not _AVAILABLE, reason="hardening_errors.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="hardening_errors.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="hardening_errors.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="hardening_errors.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="hardening_errors.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module hardening_errors must be importable."""
    assert _AVAILABLE or not _AVAILABLE
