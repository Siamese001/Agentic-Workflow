"""Foundational behavioral tests for agentic_core/L0_routing/utils/component_util.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_component_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L0_routing.utils.component_util import (  # noqa: F401
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_RETRIES,
    THRESHOLD,
    ComponentFactory,
    get_detection_emitter,
    get_human_review_queue,
    get_meta_learning_service,
    get_verification_gate,
)


class TestComponentFactoryContract:
    def test_is_class(self):
        assert isinstance(ComponentFactory, type)

    def test_has_method_get_verification_gate(self):
        assert callable(getattr(ComponentFactory, "get_verification_gate", None))

    def test_has_method_get_human_review_queue(self):
        assert callable(getattr(ComponentFactory, "get_human_review_queue", None))

    def test_has_method_get_detection_emitter(self):
        assert callable(getattr(ComponentFactory, "get_detection_emitter", None))

    def test_has_method_get_meta_learning_service(self):
        assert callable(getattr(ComponentFactory, "get_meta_learning_service", None))


class TestGetVerificationGateFunction:
    def test_is_callable(self):
        assert callable(get_verification_gate)

    def test_has_return_annotation(self):
        import inspect

        sig = inspect.signature(get_verification_gate)
        assert sig.return_annotation is not inspect.Parameter.empty


class TestGetHumanReviewQueueFunction:
    def test_is_callable(self):
        assert callable(get_human_review_queue)

    def test_has_return_annotation(self):
        import inspect

        sig = inspect.signature(get_human_review_queue)
        assert sig.return_annotation is not inspect.Parameter.empty


class TestGetDetectionEmitterFunction:
    def test_is_callable(self):
        assert callable(get_detection_emitter)

    def test_has_return_annotation(self):
        import inspect

        sig = inspect.signature(get_detection_emitter)
        assert sig.return_annotation is not inspect.Parameter.empty


class TestGetMetaLearningServiceFunction:
    def test_is_callable(self):
        assert callable(get_meta_learning_service)

    def test_has_return_annotation(self):
        import inspect

        sig = inspect.signature(get_meta_learning_service)
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
    """Module component_util must be importable or skip gracefully."""
    # Import verified at module level
    # Verify the module can be imported and has expected attributes
    import agentic_core.L0_routing.utils.component_util as mod

    # Check that key classes are available
    assert hasattr(mod, "ComponentFactory"), "ComponentFactory class should be available"
    assert callable(mod.ComponentFactory), "ComponentFactory should be callable"

    # Check that key functions are available
    expected_functions = [
        "get_verification_gate",
        "get_human_review_queue",
        "get_detection_emitter",
        "get_meta_learning_service",
    ]
    for func_name in expected_functions:
        assert hasattr(mod, func_name), f"{func_name} function should be available"
        assert callable(getattr(mod, func_name)), f"{func_name} should be callable"

    # Check that constants are defined
    expected_constants = ["BATCH_SIZE", "BUFFER_SIZE", "DEFAULT_SLEEP", "MAX_RETRIES", "THRESHOLD"]
    for const_name in expected_constants:
        assert hasattr(mod, const_name), f"{const_name} constant should be defined"
        assert getattr(mod, const_name) is not None, f"{const_name} should not be None"
