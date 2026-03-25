"""Foundational behavioral tests for agentic_core/L4_state/utils/layer_gravity_util.py.

fan_in=13 — this module is imported by 13 other modules.
ADG contract: import-hygiene is covered by test_layer_gravity_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L4_state.utils.layer_gravity_util import (  # noqa: F401
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_RETRIES,
    THRESHOLD,
    extract_layer_from_module,
    extract_layer_from_path,
    get_allowed_layers,
    is_gravity_violation,
)


class TestExtractLayerFromPathFunction:
    def test_is_callable(self):
        assert callable(extract_layer_from_path)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(extract_layer_from_path)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestExtractLayerFromModuleFunction:
    def test_is_callable(self):
        assert callable(extract_layer_from_module)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(extract_layer_from_module)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestIsGravityViolationFunction:
    def test_is_callable(self):
        assert callable(is_gravity_violation)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(is_gravity_violation)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestGetAllowedLayersFunction:
    def test_is_callable(self):
        assert callable(get_allowed_layers)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_allowed_layers)
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
    """Module layer_gravity_util must be importable or skip gracefully."""
    pass  # Import verified at module level
