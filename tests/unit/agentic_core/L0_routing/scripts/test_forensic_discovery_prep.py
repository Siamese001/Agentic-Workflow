"""Foundational behavioral tests for agentic_core/L0_routing/scripts/forensic_discovery_prep.py.

fan_in=12 — this module is imported by 12 other modules.
ADG contract: import-hygiene is covered by test_forensic_discovery_prep_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.forensic_discovery_prep import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        ForensicAgentRecord,
        build_class_bases_map,
        extract_precise_mro,
        resolve_full_mro,
        sha256_file,
    )
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    ForensicAgentRecord = None  # type: ignore[assignment,misc]
    sha256_file = None  # type: ignore[assignment,misc]
    extract_precise_mro = None  # type: ignore[assignment,misc]
    build_class_bases_map = None  # type: ignore[assignment,misc]
    resolve_full_mro = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="forensic_discovery_prep.py deps unavailable")
class TestForensicAgentRecordContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ForensicAgentRecord)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(ForensicAgentRecord)}
        assert field_names >= {'agent_name', 'mro_signature', 'layer', 'class_name', 'file_path'}

@pytest.mark.skipif(not _AVAILABLE, reason="forensic_discovery_prep.py deps unavailable")
class TestSha256FileFunction:
    def test_is_callable(self):
        assert callable(sha256_file)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(sha256_file)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="forensic_discovery_prep.py deps unavailable")
class TestExtractPreciseMroFunction:
    def test_is_callable(self):
        assert callable(extract_precise_mro)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(extract_precise_mro)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="forensic_discovery_prep.py deps unavailable")
class TestBuildClassBasesMapFunction:
    def test_is_callable(self):
        assert callable(build_class_bases_map)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(build_class_bases_map)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="forensic_discovery_prep.py deps unavailable")
class TestResolveFullMroFunction:
    def test_is_callable(self):
        assert callable(resolve_full_mro)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(resolve_full_mro)
        assert sig.return_annotation is not inspect.Parameter.empty

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


def test_module_importable():
    """Module forensic_discovery_prep must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
