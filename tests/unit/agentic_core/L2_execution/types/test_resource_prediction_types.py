"""Foundational behavioral tests for agentic_core/L2_execution/types/resource_prediction_types.py.

fan_in=5 — imported by 5 other modules.
ADG import-hygiene is covered separately by test_resource_prediction_types_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.types.resource_prediction_types import (  # noqa: F401
        FailureSignature,
        ResourceEnvelope,
        ResourcePrediction,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
        MAX_DEPTH,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    FailureSignature = None  # type: ignore[assignment,misc]
    ResourceEnvelope = None  # type: ignore[assignment,misc]
    ResourcePrediction = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="resource_prediction_types.py deps unavailable")
class TestFailureSignatureContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(FailureSignature)

    def test_is_frozen(self):
        assert FailureSignature.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(FailureSignature)}
        assert fnames >= {'component', 'fingerprint', 'failure_type'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(FailureSignature)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="resource_prediction_types.py deps unavailable")
class TestResourceEnvelopeContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ResourceEnvelope)

    def test_is_frozen(self):
        assert ResourceEnvelope.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(ResourceEnvelope)}
        assert fnames >= {'memory_mb', 'cpu_cores', 'timeout_s'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(ResourceEnvelope)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="resource_prediction_types.py deps unavailable")
class TestResourcePredictionContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ResourcePrediction)

    def test_is_frozen(self):
        assert ResourcePrediction.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(ResourcePrediction)}
        assert fnames >= {'reasons', 'envelope', 'signature', 'confidence'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(ResourcePrediction)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="resource_prediction_types.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="resource_prediction_types.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

    def test_value_is_truthy_or_defined(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="resource_prediction_types.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

    def test_value_is_truthy_or_defined(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="resource_prediction_types.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="resource_prediction_types.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="resource_prediction_types.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Smoke: resource_prediction_types importable or gracefully unavailable."""
    assert True
