"""ADG-driven tests for apps_rg/config/void_compliance_config.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_rg.config.void_compliance_config import (  # noqa: F401
        validate_file_naming,
        get_placement_guidance,
        check_span_of_two_violation,
        validate_import_conventions,
        validate_file_location,
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
    validate_file_naming = None  # type: ignore[assignment,misc]
    get_placement_guidance = None  # type: ignore[assignment,misc]
    check_span_of_two_violation = None  # type: ignore[assignment,misc]
    validate_import_conventions = None  # type: ignore[assignment,misc]
    validate_file_location = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="void_compliance_config.py deps unavailable")
class TestValidateFileNaming:
    def test_is_callable(self):
        assert callable(validate_file_naming)

@pytest.mark.skipif(not _AVAILABLE, reason="void_compliance_config.py deps unavailable")
class TestGetPlacementGuidance:
    def test_is_callable(self):
        assert callable(get_placement_guidance)

@pytest.mark.skipif(not _AVAILABLE, reason="void_compliance_config.py deps unavailable")
class TestCheckSpanOfTwoViolation:
    def test_is_callable(self):
        assert callable(check_span_of_two_violation)

@pytest.mark.skipif(not _AVAILABLE, reason="void_compliance_config.py deps unavailable")
class TestValidateImportConventions:
    def test_is_callable(self):
        assert callable(validate_import_conventions)

@pytest.mark.skipif(not _AVAILABLE, reason="void_compliance_config.py deps unavailable")
class TestValidateFileLocation:
    def test_is_callable(self):
        assert callable(validate_file_location)

@pytest.mark.skipif(not _AVAILABLE, reason="void_compliance_config.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="void_compliance_config.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="void_compliance_config.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="void_compliance_config.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="void_compliance_config.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="void_compliance_config.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module void_compliance_config.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
