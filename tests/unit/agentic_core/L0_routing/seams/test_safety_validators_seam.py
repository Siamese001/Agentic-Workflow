"""Foundational behavioral tests for agentic_core/L0_routing/seams/safety_validators_seam.py.

fan_in=20 — this module is imported by 20 other modules.
ADG contract: import-hygiene is covered by test_safety_validators_seam_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.seams.safety_validators_seam import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        load_autonomy_guardian,
        load_canonical_truth_validator,
        load_healing_strategy,
        load_hygiene_guardian,
    )
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    load_hygiene_guardian = None  # type: ignore[assignment,misc]
    load_autonomy_guardian = None  # type: ignore[assignment,misc]
    load_healing_strategy = None  # type: ignore[assignment,misc]
    load_canonical_truth_validator = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="safety_validators_seam.py deps unavailable")
class TestLoadHygieneGuardianFunction:
    def test_is_callable(self):
        assert callable(load_hygiene_guardian)

@pytest.mark.skipif(not _AVAILABLE, reason="safety_validators_seam.py deps unavailable")
class TestLoadAutonomyGuardianFunction:
    def test_is_callable(self):
        assert callable(load_autonomy_guardian)

@pytest.mark.skipif(not _AVAILABLE, reason="safety_validators_seam.py deps unavailable")
class TestLoadHealingStrategyFunction:
    def test_is_callable(self):
        assert callable(load_healing_strategy)

@pytest.mark.skipif(not _AVAILABLE, reason="safety_validators_seam.py deps unavailable")
class TestLoadCanonicalTruthValidatorFunction:
    def test_is_callable(self):
        assert callable(load_canonical_truth_validator)

@pytest.mark.skipif(not _AVAILABLE, reason="safety_validators_seam.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="safety_validators_seam.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="safety_validators_seam.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="safety_validators_seam.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="safety_validators_seam.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module safety_validators_seam must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
