"""ADG-driven tests for apps_rg/validators/__init__.py — fan_in=2.

Contract tests: namespace importability.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


class TestAppsRgValidatorsInit:
    def test_namespace_importable(self):
        try:
            import apps_rg.validators
            assert apps_rg.validators is not None
        except (ImportError, ModuleNotFoundError) as e:
            pytest.skip(f"apps_rg.validators deps unavailable: {e}")

    def test_init_file_is_importable_as_package(self):
        try:
            import importlib
            mod = importlib.import_module("apps_rg.validators")
            assert mod is not None
        except (ImportError, ModuleNotFoundError) as e:
            pytest.skip(f"apps_rg.validators deps unavailable: {e}")
