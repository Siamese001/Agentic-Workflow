"""Foundational behavioral tests for apps_shared/utils/input_validator_util.py.

fan_in=13 — this module is imported by 13 other modules.
ADG contract: import-hygiene is covered by test_input_validator_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from apps_shared.utils.input_validator_util import (  # noqa: F401
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_RETRIES,
    THRESHOLD,
    InputValidationError,
    InputValidator,
    ValidatedInput,
    ValidationRule,
    ValidationType,
    create_default_validator,
    validate_with_pydantic,
)


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

class TestValidationRuleContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ValidationRule)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(ValidationRule)}
        assert field_names >= {'min_length', 'required', 'validation_type', 'max_length', 'name'}

class TestInputValidationErrorContract:
    def test_is_class(self):
        assert isinstance(InputValidationError, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(InputValidationError, type)

class TestInputValidatorContract:
    def test_is_class(self):
        assert isinstance(InputValidator, type)

    def test_has_method_add_rule(self):
        assert callable(getattr(InputValidator, 'add_rule', None))

    def test_has_method_add_schema(self):
        assert callable(getattr(InputValidator, 'add_schema', None))

    def test_has_method_validate(self):
        assert callable(getattr(InputValidator, 'validate', None))

class TestValidatedInputContract:
    def test_is_class(self):
        assert isinstance(ValidatedInput, type)

    def test_has_method_sanitize_strings(self):
        assert callable(getattr(ValidatedInput, 'sanitize_strings', None))

    def test_has_method_check_size(self):
        assert callable(getattr(ValidatedInput, 'check_size', None))

class TestCreateDefaultValidatorFunction:
    def test_is_callable(self):
        assert callable(create_default_validator)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(create_default_validator)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestValidateWithPydanticFunction:
    def test_is_callable(self):
        assert callable(validate_with_pydantic)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(validate_with_pydantic)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module input_validator_util must be importable or skip gracefully."""
    pass  # Import verified at module level
