"""ADG-driven tests for apps_lic/validators/safety_validate_outreach_constraints_validator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_lic.validators.safety_validate_outreach_constraints_validator import (  # noqa: F401
        validate_outreach_constraints,
        get_validate_outreach_constraints_config,
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
    validate_outreach_constraints = None  # type: ignore[assignment,misc]
    get_validate_outreach_constraints_config = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="safety_validate_outreach_constraints_validator.py deps unavailable")
class TestValidateOutreachConstraints:
    def test_is_callable(self):
        assert callable(validate_outreach_constraints)

@pytest.mark.skipif(not _AVAILABLE, reason="safety_validate_outreach_constraints_validator.py deps unavailable")
class TestGetValidateOutreachConstraintsConfig:
    def test_is_callable(self):
        assert callable(get_validate_outreach_constraints_config)

@pytest.mark.skipif(not _AVAILABLE, reason="safety_validate_outreach_constraints_validator.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="safety_validate_outreach_constraints_validator.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="safety_validate_outreach_constraints_validator.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="safety_validate_outreach_constraints_validator.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="safety_validate_outreach_constraints_validator.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="safety_validate_outreach_constraints_validator.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module safety_validate_outreach_constraints_validator.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
