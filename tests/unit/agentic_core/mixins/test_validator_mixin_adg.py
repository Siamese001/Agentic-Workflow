"""ADG-driven tests for mixins/validator_mixin.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: from agentic_core.mixins.validator_mixin import ValidatorMixin


class TestValidatorMixin:
    def test_importable(self):
                from agentic_core.mixins.validator_mixin import ValidatorMixin
                assert callable(ValidatorMixin)

        assert callable(ValidatorMixin)

    def test_validator_orchestrator_default_none(self):
        assert ValidatorMixin._validator_orchestrator is None

    def test_has_orchestrator_validate(self):
        assert hasattr(ValidatorMixin, "orchestrator_validate")

    def test_has_validator_orchestrator_property(self):
        assert hasattr(ValidatorMixin, "validator_orchestrator")
