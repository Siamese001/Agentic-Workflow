"""ADG-driven tests for mixins/self_diagnosis_mixin.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.mixins.self_diagnosis_mixin import SelfDiagnosisMixin


class TestSelfDiagnosisMixin:
    def test_importable(self):
        assert callable(SelfDiagnosisMixin)

    def test_mandatory_components_default_empty(self):
        assert SelfDiagnosisMixin.MANDATORY_COMPONENTS == []

    def test_has_self_diagnose(self):
        assert hasattr(SelfDiagnosisMixin, "self_diagnose")

    def test_creates(self):
        mixin = SelfDiagnosisMixin()
        assert mixin is not None
