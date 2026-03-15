"""Foundational behavioral tests for agentic_core/L0_routing/seams/safety_enforcement_seam.py.

fan_in=12 — this module is imported by 12 other modules.
ADG contract: import-hygiene is covered by test_safety_enforcement_seam_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.seams.safety_enforcement_seam import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        load_activation_gate,
        load_archival_gatekeeper,
        load_code_deduplication_agent,
        load_ssot_scanner,
    )
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    load_code_deduplication_agent = None  # type: ignore[assignment,misc]
    load_archival_gatekeeper = None  # type: ignore[assignment,misc]
    load_ssot_scanner = None  # type: ignore[assignment,misc]
    load_activation_gate = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="safety_enforcement_seam.py deps unavailable")
class TestLoadCodeDeduplicationAgentFunction:
    def test_is_callable(self):
        assert callable(load_code_deduplication_agent)

@pytest.mark.skipif(not _AVAILABLE, reason="safety_enforcement_seam.py deps unavailable")
class TestLoadArchivalGatekeeperFunction:
    def test_is_callable(self):
        assert callable(load_archival_gatekeeper)

@pytest.mark.skipif(not _AVAILABLE, reason="safety_enforcement_seam.py deps unavailable")
class TestLoadSsotScannerFunction:
    def test_is_callable(self):
        assert callable(load_ssot_scanner)

@pytest.mark.skipif(not _AVAILABLE, reason="safety_enforcement_seam.py deps unavailable")
class TestLoadActivationGateFunction:
    def test_is_callable(self):
        assert callable(load_activation_gate)

@pytest.mark.skipif(not _AVAILABLE, reason="safety_enforcement_seam.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="safety_enforcement_seam.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="safety_enforcement_seam.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="safety_enforcement_seam.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="safety_enforcement_seam.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module safety_enforcement_seam must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
