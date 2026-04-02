"""ADG-driven tests for thin app-layer __init__.py packages — fan_in batch.
"""
from __future__ import annotations

import importlib
from pathlib import Path

import pytest


class TestAppsLicUtils:
    """apps_lic/utils/__init__.py — fan_in=4."""

    def test_package_is_in_apps_lic(self):
        assert Path("apps_lic/utils/__init__.py").exists()

    def test_utils_modules_discoverable(self):
        assert Path("apps_lic/utils").exists()

    def test_no_import_error_on_reimport(self):
        assert importlib.import_module("apps_lic.utils") is not None


class TestAppsRgTypes:
    """apps_rg/types/__init__.py — fan_in=4."""

    def test_package_is_in_apps_rg(self):
        assert Path("apps_rg/types/__init__.py").exists()

    def test_types_modules_discoverable(self):
        assert Path("apps_rg/types").exists()

    def test_no_import_error_on_reimport(self):
        assert importlib.import_module("apps_rg.types") is not None


class TestL4StateReasoningPackage:
    """agentic_core/L4_state/reasoning/__init__.py — fan_in=3."""

    def test_package_in_l4(self):
        assert Path("agentic_core/L4_state/reasoning/__init__.py").exists()

    def test_reasoning_modules_discoverable(self):
        assert Path("agentic_core/L4_state/reasoning").exists()


class TestL4StateUtilsPackage:
    """agentic_core/L4_state/utils/__init__.py — fan_in=3."""

    def test_package_in_l4(self):
        assert Path("agentic_core/L4_state/utils/__init__.py").exists()


    def test_utils_modules_discoverable(self):
        assert Path("agentic_core/L4_state/utils").exists()
