"""ADG-driven tests for apps_lic/utils/lic_engine_validation_capability_util.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from apps_lic.utils.lic_engine_validation_capability_util import LICEngineValidationCapability


class TestLICEngineValidationCapability:
    def test_importable(self):
        assert callable(LICEngineValidationCapability)

    def test_signal_name_default_empty(self):
        assert LICEngineValidationCapability.SIGNAL_NAME == ""

    def test_validation_label_default_empty(self):
        assert LICEngineValidationCapability.VALIDATION_LABEL == ""

    def test_has_run_validation(self):
        assert hasattr(LICEngineValidationCapability, "run_validation")

    def test_concrete_subclass(self):
        class ConcreteValidator(LICEngineValidationCapability):
            SIGNAL_NAME = "TEST_SIGNAL"
            VALIDATION_LABEL = "Test check"

            def _validate(self) -> list[str]:
                return []

        validator = ConcreteValidator()
        assert validator.SIGNAL_NAME == "TEST_SIGNAL"
