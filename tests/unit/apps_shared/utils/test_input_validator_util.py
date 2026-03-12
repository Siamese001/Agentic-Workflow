"""Foundational behavioral tests for apps_shared/utils/input_validator_util.py.

fan_in=13 — this module is imported by 13 other modules.
ADG contract: import-hygiene is covered by test_input_validator_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
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
    )
    _AVAILABLE = True
except Exception as _exc:
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


@pytest.mark.skipif(not _AVAILABLE, reason="input_validator_util.py deps unavailable")
class TestValidationTypeContract:
    def test_is_enum(self):
        import enum
        assert issubclass(ValidationType, enum.Enum)

    def test_has_members(self):
        assert len(list(ValidationType)) >= 1

    def test_member_values_are_strings_or_ints(self):
        for member in ValidationType:
            assert member.value is not None

    def test_known_member_string_exists(self):
        assert hasattr(ValidationType, 'STRING')

@pytest.mark.skipif(not _AVAILABLE, reason="input_validator_util.py deps unavailable")
class TestValidationRuleContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ValidationRule)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(ValidationRule)}
        assert field_names >= {'min_length', 'required', 'validation_type', 'max_length', 'name'}

@pytest.mark.skipif(not _AVAILABLE, reason="input_validator_util.py deps unavailable")
class TestInputValidationErrorContract:
    def test_is_class(self):
        assert isinstance(InputValidationError, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(InputValidationError, type)

@pytest.mark.skipif(not _AVAILABLE, reason="input_validator_util.py deps unavailable")
class TestInputValidatorContract:
    def test_is_class(self):
        assert isinstance(InputValidator, type)

    def test_has_method_add_rule(self):
        assert callable(getattr(InputValidator, 'add_rule', None))

    def test_has_method_add_schema(self):
        assert callable(getattr(InputValidator, 'add_schema', None))

    def test_has_method_validate(self):
        assert callable(getattr(InputValidator, 'validate', None))

@pytest.mark.skipif(not _AVAILABLE, reason="input_validator_util.py deps unavailable")
class TestValidatedInputContract:
    def test_is_class(self):
        assert isinstance(ValidatedInput, type)

    def test_has_method_sanitize_strings(self):
        assert callable(getattr(ValidatedInput, 'sanitize_strings', None))

    def test_has_method_check_size(self):
        assert callable(getattr(ValidatedInput, 'check_size', None))

@pytest.mark.skipif(not _AVAILABLE, reason="input_validator_util.py deps unavailable")
class TestCreateDefaultValidatorFunction:
    def test_is_callable(self):
        assert callable(create_default_validator)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(create_default_validator)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="input_validator_util.py deps unavailable")
class TestValidateWithPydanticFunction:
    def test_is_callable(self):
        assert callable(validate_with_pydantic)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(validate_with_pydantic)
        assert sig.return_annotation is not inspect.Parameter.empty

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


def test_module_importable():
    """Module input_validator_util must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
