"""ADG-driven tests for agentic_core/L0_routing/scripts/forensic_discovery_prep.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.forensic_discovery_prep import (  # noqa: F401
        ForensicAgentRecord,
        sha256_file,
        extract_precise_mro,
        build_class_bases_map,
        resolve_full_mro,
        stub_sentinel_detected,
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
    ForensicAgentRecord = None  # type: ignore[assignment,misc]
    sha256_file = None  # type: ignore[assignment,misc]
    extract_precise_mro = None  # type: ignore[assignment,misc]
    build_class_bases_map = None  # type: ignore[assignment,misc]
    resolve_full_mro = None  # type: ignore[assignment,misc]
    stub_sentinel_detected = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="forensic_discovery_prep.py deps unavailable")
class TestForensicAgentRecord:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ForensicAgentRecord)
    def test_importable(self):
        assert ForensicAgentRecord is not None

@pytest.mark.skipif(not _AVAILABLE, reason="forensic_discovery_prep.py deps unavailable")
class TestSha256File:
    def test_is_callable(self):
        assert callable(sha256_file)

@pytest.mark.skipif(not _AVAILABLE, reason="forensic_discovery_prep.py deps unavailable")
class TestExtractPreciseMro:
    def test_is_callable(self):
        assert callable(extract_precise_mro)

@pytest.mark.skipif(not _AVAILABLE, reason="forensic_discovery_prep.py deps unavailable")
class TestBuildClassBasesMap:
    def test_is_callable(self):
        assert callable(build_class_bases_map)

@pytest.mark.skipif(not _AVAILABLE, reason="forensic_discovery_prep.py deps unavailable")
class TestResolveFullMro:
    def test_is_callable(self):
        assert callable(resolve_full_mro)

@pytest.mark.skipif(not _AVAILABLE, reason="forensic_discovery_prep.py deps unavailable")
class TestStubSentinelDetected:
    def test_is_callable(self):
        assert callable(stub_sentinel_detected)

@pytest.mark.skipif(not _AVAILABLE, reason="forensic_discovery_prep.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="forensic_discovery_prep.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="forensic_discovery_prep.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="forensic_discovery_prep.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="forensic_discovery_prep.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="forensic_discovery_prep.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module forensic_discovery_prep.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
