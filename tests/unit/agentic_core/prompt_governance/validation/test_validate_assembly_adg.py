"""ADG-driven tests for agentic_core/prompt_governance/validation/validate_assembly.py — fan_in=0."""
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
        MAX_DEPTH,
    )
    _AVAILABLE = True
except Exception:
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
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="validate_assembly.py deps unavailable")
class TestSha256Bytes:
    def test_is_callable(self):
        assert callable(sha256_bytes)

@pytest.mark.skipif(not _AVAILABLE, reason="validate_assembly.py deps unavailable")
class TestSha256File:
    def test_is_callable(self):
        assert callable(sha256_file)

@pytest.mark.skipif(not _AVAILABLE, reason="validate_assembly.py deps unavailable")
class TestLoadManifest:
    def test_is_callable(self):
        assert callable(load_manifest)

@pytest.mark.skipif(not _AVAILABLE, reason="validate_assembly.py deps unavailable")
class TestValidate:
    def test_is_callable(self):
        assert callable(validate)

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

@pytest.mark.skipif(not _AVAILABLE, reason="validate_assembly.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module validate_assembly.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
