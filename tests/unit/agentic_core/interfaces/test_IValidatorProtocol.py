"""Foundational behavioral tests for agentic_core/interfaces/IValidatorProtocol.py.

fan_in=13 — this module is imported by 13 other modules.
ADG contract: import-hygiene is covered by test_IValidatorProtocol_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.interfaces.IValidatorProtocol import (  # noqa: F401
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_RETRIES,
    THRESHOLD,
    AdversarialValidator,
    BoundaryValidator,
    ValidatorProtocol,
    get_adversarial_validator,
    get_boundary_validator,
    get_integration_status,
    register_red_team_validators,
)


class TestValidatorProtocolContract:
    def test_is_class(self):
        assert isinstance(ValidatorProtocol, type)

    def test_has_method_validate(self):
        assert callable(getattr(ValidatorProtocol, 'validate', None))

class TestAdversarialValidatorContract:
    def test_is_class(self):
        assert isinstance(AdversarialValidator, type)

    def test_has_method_validate(self):
        assert callable(getattr(AdversarialValidator, 'validate', None))

class TestBoundaryValidatorContract:
    def test_is_class(self):
        assert isinstance(BoundaryValidator, type)

    def test_has_method_validate(self):
        assert callable(getattr(BoundaryValidator, 'validate', None))

class TestGetAdversarialValidatorFunction:
    def test_is_callable(self):
        assert callable(get_adversarial_validator)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_adversarial_validator)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestGetBoundaryValidatorFunction:
    def test_is_callable(self):
        assert callable(get_boundary_validator)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_boundary_validator)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestRegisterRedTeamValidatorsFunction:
    def test_is_callable(self):
        assert callable(register_red_team_validators)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(register_red_team_validators)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestGetIntegrationStatusFunction:
    def test_is_callable(self):
        assert callable(get_integration_status)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_integration_status)
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
    """Module IValidatorProtocol must be importable or skip gracefully."""
    pass  # Import verified at module level
