"""ADG-driven tests for apps_shared/config/__init__.py — fan_in=2.

Contract tests: re-exports from operational_config and config_loader_util.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.config as mod
from apps_shared.config import (
    OPERATIONAL_ALLOWED_DUPLICATES,
    OPERATIONAL_EXCLUDED_DIRS,
    OPERATIONAL_SCAN_TARGETS,
    ConfigLoader,
    ConfigLoadResult,
    get_config_loader,
    is_allowed_duplicate,
    is_excluded_path,
    load_agent_config,
    should_scan_directory,
)


class TestAppsSharedConfigInit:
    def test_module_importable(self):
        assert mod is not None

    def test_operational_excluded_dirs_exported(self):
        assert OPERATIONAL_EXCLUDED_DIRS is not None

    def test_operational_scan_targets_exported(self):
        assert OPERATIONAL_SCAN_TARGETS is not None

    def test_operational_allowed_duplicates_exported(self):
        assert OPERATIONAL_ALLOWED_DUPLICATES is not None

    def test_is_excluded_path_callable(self):
        assert callable(is_excluded_path)

    def test_is_allowed_duplicate_callable(self):
        assert callable(is_allowed_duplicate)

    def test_should_scan_directory_callable(self):
        assert callable(should_scan_directory)

    def test_config_loader_callable(self):
        assert callable(ConfigLoader)

    def test_config_load_result_callable(self):
        assert callable(ConfigLoadResult)

    def test_get_config_loader_callable(self):
        assert callable(get_config_loader)

    def test_load_agent_config_callable(self):
        assert callable(load_agent_config)

    def test_all_list_complete(self):
        from apps_shared.config import __all__
        for name in (
            "OPERATIONAL_EXCLUDED_DIRS", "OPERATIONAL_SCAN_TARGETS",
            "OPERATIONAL_ALLOWED_DUPLICATES", "is_excluded_path",
            "is_allowed_duplicate", "should_scan_directory",
            "ConfigLoader", "ConfigLoadResult", "get_config_loader", "load_agent_config",
        ):
            assert name in __all__
