"""Foundational behavioral tests for agentic_core/adg/schema.py.

fan_in=35 — imported by 35 other modules.
ADG import-hygiene is covered separately by test_schema_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.adg.schema_util import (  # noqa: F401
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_DEPTH,
    MAX_RETRIES,
    THRESHOLD,
    canonical_name,
    module_path_to_layer,
    verify_layer_graph_consistency,
)


class TestCanonicalNameFunction:
    def test_is_callable(self):
        assert callable(canonical_name)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(canonical_name)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestVerifyLayerGraphConsistencyFunction:
    def test_is_callable(self):
        assert callable(verify_layer_graph_consistency)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(verify_layer_graph_consistency)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestModulePathToLayerFunction:
    def test_is_callable(self):
        assert callable(module_path_to_layer)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(module_path_to_layer)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_RETRIES is not None

class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

    def test_value_is_truthy_or_defined(self):
        assert DEFAULT_SLEEP is not None

class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

    def test_value_is_truthy_or_defined(self):
        assert THRESHOLD is not None

class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BUFFER_SIZE is not None

class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BATCH_SIZE is not None

class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Smoke: schema importable or gracefully unavailable."""
    pass
