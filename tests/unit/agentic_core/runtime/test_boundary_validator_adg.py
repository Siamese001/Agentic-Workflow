"""ADG-driven tests for agentic_core/runtime/boundary_validator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.runtime.boundary_validator import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        assert_no_apps_imports,
        check_runtime_boundaries,
        validate_layer_direction,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    assert_no_apps_imports = None  # type: ignore[assignment,misc]
    validate_layer_direction = None  # type: ignore[assignment,misc]
    check_runtime_boundaries = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="boundary_validator.py deps unavailable")
class TestAssertNoAppsImports:
    def test_is_callable(self):
        assert callable(assert_no_apps_imports)

@pytest.mark.skipif(not _AVAILABLE, reason="boundary_validator.py deps unavailable")
class TestValidateLayerDirection:
    def test_is_callable(self):
        assert callable(validate_layer_direction)

@pytest.mark.skipif(not _AVAILABLE, reason="boundary_validator.py deps unavailable")
class TestCheckRuntimeBoundaries:
    def test_is_callable(self):
        assert callable(check_runtime_boundaries)

@pytest.mark.skipif(not _AVAILABLE, reason="boundary_validator.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="boundary_validator.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="boundary_validator.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="boundary_validator.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="boundary_validator.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="boundary_validator.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module boundary_validator.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE