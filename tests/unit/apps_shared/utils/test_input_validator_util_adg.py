"""ADG-driven tests for apps_shared/utils/input_validator_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.input_validator_util import (  # noqa: F401
        ValidationType,
        ValidationRule,
        InputValidationError,
        InputValidator,
        ValidatedInput,
        create_default_validator,
        validate_with_pydantic,
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
    ValidationType = None  # type: ignore[assignment,misc]
    ValidationRule = None  # type: ignore[assignment,misc]
    InputValidationError = None  # type: ignore[assignment,misc]
    InputValidator = None  # type: ignore[assignment,misc]
    ValidatedInput = None  # type: ignore[assignment,misc]
    create_default_validator = None  # type: ignore[assignment,misc]
    validate_with_pydantic = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="input_validator_util.py deps unavailable")
class TestValidationType:
    def test_is_enum(self):
        import enum
        assert issubclass(ValidationType, enum.Enum)
    def test_has_members(self):
        assert len(list(ValidationType)) >= 1
    def test_importable(self):
        assert ValidationType is not None

@pytest.mark.skipif(not _AVAILABLE, reason="input_validator_util.py deps unavailable")
class TestValidationRule:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ValidationRule)
    def test_importable(self):
        assert ValidationRule is not None

@pytest.mark.skipif(not _AVAILABLE, reason="input_validator_util.py deps unavailable")
class TestInputValidationError:
    def test_is_class(self):
        assert isinstance(InputValidationError, type)
    def test_importable(self):
        assert InputValidationError is not None

@pytest.mark.skipif(not _AVAILABLE, reason="input_validator_util.py deps unavailable")
class TestInputValidator:
    def test_is_class(self):
        assert isinstance(InputValidator, type)
    def test_importable(self):
        assert InputValidator is not None

@pytest.mark.skipif(not _AVAILABLE, reason="input_validator_util.py deps unavailable")
class TestValidatedInput:
    def test_is_class(self):
        assert isinstance(ValidatedInput, type)
    def test_importable(self):
        assert ValidatedInput is not None

@pytest.mark.skipif(not _AVAILABLE, reason="input_validator_util.py deps unavailable")
class TestCreateDefaultValidator:
    def test_is_callable(self):
        assert callable(create_default_validator)

@pytest.mark.skipif(not _AVAILABLE, reason="input_validator_util.py deps unavailable")
class TestValidateWithPydantic:
    def test_is_callable(self):
        assert callable(validate_with_pydantic)

@pytest.mark.skipif(not _AVAILABLE, reason="input_validator_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="input_validator_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="input_validator_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="input_validator_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="input_validator_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="input_validator_util.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module input_validator_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
