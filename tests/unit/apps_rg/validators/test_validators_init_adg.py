"""ADG-driven tests for apps_rg/validators/__init__.py — fan_in=2.

Contract tests: namespace importability.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


class TestAppsRgValidatorsInit:
    def test_namespace_importable(self):
                import apps_rg.validators
                assert apps_rg.validators is not None

        assert apps_rg.validators is not None
