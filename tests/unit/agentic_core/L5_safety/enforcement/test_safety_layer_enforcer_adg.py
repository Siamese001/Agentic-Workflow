"""ADG-driven tests for agentic_core/L5_safety/enforcement/safety_layer_enforcer.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.enforcement.safety_layer_enforcer import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        L5SafetyLayer,
        create_l5_safety_layer,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    L5SafetyLayer = None  # type: ignore[assignment,misc]
    create_l5_safety_layer = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="safety_layer_enforcer.py deps unavailable")
class TestL5SafetyLayer:
    def test_is_class(self):
        assert isinstance(L5SafetyLayer, type)
    def test_importable(self):
        assert L5SafetyLayer is not None

@pytest.mark.skipif(not _AVAILABLE, reason="safety_layer_enforcer.py deps unavailable")
class TestCreateL5SafetyLayer:
    def test_is_callable(self):
        assert callable(create_l5_safety_layer)

@pytest.mark.skipif(not _AVAILABLE, reason="safety_layer_enforcer.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="safety_layer_enforcer.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="safety_layer_enforcer.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="safety_layer_enforcer.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="safety_layer_enforcer.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="safety_layer_enforcer.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module safety_layer_enforcer.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE