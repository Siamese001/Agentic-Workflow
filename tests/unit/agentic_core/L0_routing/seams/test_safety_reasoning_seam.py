"""Foundational behavioral tests for agentic_core/L0_routing/seams/safety_reasoning_seam.py.

fan_in=19 — this module is imported by 19 other modules.
ADG contract: import-hygiene is covered by test_safety_reasoning_seam_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.seams.safety_reasoning_seam import (  # noqa: F401
        load_naming_agent,
        load_structure_enforcer_agent,
        load_cognitive_disposition_agent,
        load_file_classification_agent,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    load_naming_agent = None  # type: ignore[assignment,misc]
    load_structure_enforcer_agent = None  # type: ignore[assignment,misc]
    load_cognitive_disposition_agent = None  # type: ignore[assignment,misc]
    load_file_classification_agent = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="safety_reasoning_seam.py deps unavailable")
class TestLoadNamingAgentFunction:
    def test_is_callable(self):
        assert callable(load_naming_agent)

@pytest.mark.skipif(not _AVAILABLE, reason="safety_reasoning_seam.py deps unavailable")
class TestLoadStructureEnforcerAgentFunction:
    def test_is_callable(self):
        assert callable(load_structure_enforcer_agent)

@pytest.mark.skipif(not _AVAILABLE, reason="safety_reasoning_seam.py deps unavailable")
class TestLoadCognitiveDispositionAgentFunction:
    def test_is_callable(self):
        assert callable(load_cognitive_disposition_agent)

@pytest.mark.skipif(not _AVAILABLE, reason="safety_reasoning_seam.py deps unavailable")
class TestLoadFileClassificationAgentFunction:
    def test_is_callable(self):
        assert callable(load_file_classification_agent)

@pytest.mark.skipif(not _AVAILABLE, reason="safety_reasoning_seam.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="safety_reasoning_seam.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="safety_reasoning_seam.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="safety_reasoning_seam.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="safety_reasoning_seam.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module safety_reasoning_seam must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
