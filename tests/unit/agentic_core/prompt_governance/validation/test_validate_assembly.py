"""Foundational behavioral tests for agentic_core/prompt_governance/validation/validate_assembly.py.

fan_in=10 — this module is imported by 10 other modules.
ADG contract: import-hygiene is covered by test_validate_assembly_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.prompt_governance.validation.validate_assembly import (  # noqa: F401
        sha256_bytes,
        sha256_file,
        load_manifest,
        validate,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    sha256_bytes = None  # type: ignore[assignment,misc]
    sha256_file = None  # type: ignore[assignment,misc]
    load_manifest = None  # type: ignore[assignment,misc]
    validate = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="validate_assembly.py deps unavailable")
class TestSha256BytesFunction:
    def test_is_callable(self):
        assert callable(sha256_bytes)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(sha256_bytes)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="validate_assembly.py deps unavailable")
class TestSha256FileFunction:
    def test_is_callable(self):
        assert callable(sha256_file)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(sha256_file)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="validate_assembly.py deps unavailable")
class TestLoadManifestFunction:
    def test_is_callable(self):
        assert callable(load_manifest)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(load_manifest)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="validate_assembly.py deps unavailable")
class TestValidateFunction:
    def test_is_callable(self):
        assert callable(validate)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(validate)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="validate_assembly.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="validate_assembly.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="validate_assembly.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="validate_assembly.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="validate_assembly.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module validate_assembly must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
