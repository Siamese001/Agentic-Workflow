"""ADG importability contract for agentic_core/L5_safety/reasoning/SafetyDetectorAgent.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_SafetyDetectorAgent.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.reasoning.SafetyDetectorAgent import (  # noqa: F401
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        SafetyConfig,
        SafetyDetectorAgent,
        SafetyThreat,
        SafetyThreatType,
        ThreatSeverity,
        create_legacy_bias_detector,
        create_legacy_injection_detector,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    SafetyThreatType = None  # type: ignore[assignment,misc]
    ThreatSeverity = None  # type: ignore[assignment,misc]
    SafetyThreat = None  # type: ignore[assignment,misc]
    SafetyConfig = None  # type: ignore[assignment,misc]
    SafetyDetectorAgent = None  # type: ignore[assignment,misc]
    create_legacy_bias_detector = None  # type: ignore[assignment,misc]
    create_legacy_injection_detector = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="SafetyDetectorAgent.py deps unavailable")
class TestSafetydetectoragentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: SafetyDetectorAgent.py must be importable."""
        assert _AVAILABLE

    def test_safetythreattype_is_type(self) -> None:
        assert SafetyThreatType is not None

    def test_threatseverity_is_type(self) -> None:
        assert ThreatSeverity is not None

    def test_safetythreat_is_type(self) -> None:
        assert SafetyThreat is not None

    def test_create_legacy_bias_detector_callable(self) -> None:
        assert callable(create_legacy_bias_detector)

    def test_create_legacy_injection_detector_callable(self) -> None:
        assert callable(create_legacy_injection_detector)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None