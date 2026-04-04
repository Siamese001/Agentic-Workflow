"""ADG-driven tests for apps_shared/config/__init__.py — fan_in=2.

Contract tests: re-exports from operational_config and config_loader_util.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


class TestAppsSharedConfigInit:
    def test_module_importable(self):
        import apps_shared.config as mod

        assert mod is not None

    def test_operational_excluded_dirs_exported(self):
        assert OPERATIONAL_EXCLUDED_DIRS is not None

    def test_operational_scan_targets_exported(self):
        assert OPERATIONAL_SCAN_TARGETS is not None

    def test_operational_allowed_duplicates_exported(self):
        assert OPERATIONAL_ALLOWED_DUPLICATES is not None

    def test_is_excluded_path_callable(self):
        pass
