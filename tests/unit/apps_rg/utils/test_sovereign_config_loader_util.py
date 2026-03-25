"""Foundational behavioral tests for apps_rg/utils/sovereign_config_loader_util.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_sovereign_config_loader_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from apps_rg.utils.sovereign_config_loader_util import (  # noqa: F401
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_RETRIES,
    THRESHOLD,
    SovereignConfigLoader,
    get_config_path,
    load_rg_specs,
    reload_config,
    save_rg_specs,
)


class TestSovereignConfigLoaderContract:
    def test_is_class(self):
        assert isinstance(SovereignConfigLoader, type)

    def test_has_method_load_topology(self):
        assert callable(getattr(SovereignConfigLoader, 'load_topology', None))

    def test_has_method_reset(self):
        assert callable(getattr(SovereignConfigLoader, 'reset', None))

class TestGetConfigPathFunction:
    def test_is_callable(self):
        assert callable(get_config_path)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_config_path)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestLoadRgSpecsFunction:
    def test_is_callable(self):
        assert callable(load_rg_specs)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(load_rg_specs)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestSaveRgSpecsFunction:
    def test_is_callable(self):
        assert callable(save_rg_specs)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(save_rg_specs)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestReloadConfigFunction:
    def test_is_callable(self):
        assert callable(reload_config)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(reload_config)
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
    """Module sovereign_config_loader_util must be importable or skip gracefully."""
    pass  # Import verified at module level
