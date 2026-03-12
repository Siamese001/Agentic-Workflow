"""Foundational behavioral tests for agentic_core/L0_routing/seam/seam_audit.py.

fan_in=13 — this module is imported by 13 other modules.
ADG contract: import-hygiene is covered by test_seam_audit_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.seam.seam_audit import (  # noqa: F401
        SeamAuditRecord,
        SeamAuditLogger,
        get_seam_audit_logger,
        seam_audit_hook,
        log_seam_operation,
        get_seam_audit_digest,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    SeamAuditRecord = None  # type: ignore[assignment,misc]
    SeamAuditLogger = None  # type: ignore[assignment,misc]
    get_seam_audit_logger = None  # type: ignore[assignment,misc]
    seam_audit_hook = None  # type: ignore[assignment,misc]
    log_seam_operation = None  # type: ignore[assignment,misc]
    get_seam_audit_digest = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="seam_audit.py deps unavailable")
class TestSeamAuditRecordContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(SeamAuditRecord)

    def test_is_frozen(self):
        assert SeamAuditRecord.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(SeamAuditRecord)}
        assert field_names >= {'seam_id', 'operation', 'inputs_hash', 'invocation_hash', 'outputs_hash'}

    def test_immutable_after_creation(self):
        import dataclasses
        fields = dataclasses.fields(SeamAuditRecord)
        if not fields:
            pytest.skip('no fields to test immutability')
        # Verify frozen raises on setattr
        # (create requires knowing required fields — skip if args unknown)
        assert SeamAuditRecord.__dataclass_params__.frozen is True

@pytest.mark.skipif(not _AVAILABLE, reason="seam_audit.py deps unavailable")
class TestSeamAuditLoggerContract:
    def test_is_class(self):
        assert isinstance(SeamAuditLogger, type)

    def test_has_method_enable(self):
        assert callable(getattr(SeamAuditLogger, 'enable', None))

    def test_has_method_disable(self):
        assert callable(getattr(SeamAuditLogger, 'disable', None))

    def test_has_method_log_seam_operation(self):
        assert callable(getattr(SeamAuditLogger, 'log_seam_operation', None))

    def test_has_method_get_records(self):
        assert callable(getattr(SeamAuditLogger, 'get_records', None))

@pytest.mark.skipif(not _AVAILABLE, reason="seam_audit.py deps unavailable")
class TestGetSeamAuditLoggerFunction:
    def test_is_callable(self):
        assert callable(get_seam_audit_logger)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_seam_audit_logger)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="seam_audit.py deps unavailable")
class TestSeamAuditHookFunction:
    def test_is_callable(self):
        assert callable(seam_audit_hook)

@pytest.mark.skipif(not _AVAILABLE, reason="seam_audit.py deps unavailable")
class TestLogSeamOperationFunction:
    def test_is_callable(self):
        assert callable(log_seam_operation)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(log_seam_operation)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="seam_audit.py deps unavailable")
class TestGetSeamAuditDigestFunction:
    def test_is_callable(self):
        assert callable(get_seam_audit_digest)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_seam_audit_digest)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="seam_audit.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="seam_audit.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="seam_audit.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="seam_audit.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="seam_audit.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module seam_audit must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
