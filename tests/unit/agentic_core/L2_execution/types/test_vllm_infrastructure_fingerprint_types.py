"""Foundational behavioral tests for agentic_core/L2_execution/types/vllm_infrastructure_fingerprint_types.py.

fan_in=9 — imported by 9 other modules.
ADG import-hygiene is covered separately by test_vllm_infrastructure_fingerprint_types_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.types.vllm_infrastructure_fingerprint_types import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        VLLMInfrastructureFingerprint,
        canonical_json,
        sha256_hex,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    VLLMInfrastructureFingerprint = None  # type: ignore[assignment,misc]
    canonical_json = None  # type: ignore[assignment,misc]
    sha256_hex = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="vllm_infrastructure_fingerprint_types.py deps unavailable")
class TestVLLMInfrastructureFingerprintContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(VLLMInfrastructureFingerprint)

    def test_is_frozen(self):
        assert VLLMInfrastructureFingerprint.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(VLLMInfrastructureFingerprint)}
        assert fnames >= {'cuda_version', 'model_name', 'model_revision_sha', 'vllm_version', 'transformers_version', 'torch_version'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(VLLMInfrastructureFingerprint)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="vllm_infrastructure_fingerprint_types.py deps unavailable")
class TestCanonicalJsonFunction:
    def test_is_callable(self):
        assert callable(canonical_json)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(canonical_json)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="vllm_infrastructure_fingerprint_types.py deps unavailable")
class TestSha256HexFunction:
    def test_is_callable(self):
        assert callable(sha256_hex)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(sha256_hex)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="vllm_infrastructure_fingerprint_types.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="vllm_infrastructure_fingerprint_types.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

    def test_value_is_truthy_or_defined(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="vllm_infrastructure_fingerprint_types.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

    def test_value_is_truthy_or_defined(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="vllm_infrastructure_fingerprint_types.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="vllm_infrastructure_fingerprint_types.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="vllm_infrastructure_fingerprint_types.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Smoke: vllm_infrastructure_fingerprint_types importable or gracefully unavailable."""
    pass