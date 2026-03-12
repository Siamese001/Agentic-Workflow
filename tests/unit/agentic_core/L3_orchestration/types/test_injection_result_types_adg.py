"""ADG contract tests for L3_orchestration/types/injection_result_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
from agentic_core.L3_orchestration.types.injection_result_types import (
    InjectionResult, detect_injection, validate_safety_threshold,
)

class TestInjectionResult:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(InjectionResult)
    def test_creates(self):
        r = InjectionResult(is_injection=False, Severity="low", confidence=0.1, detected_patterns=[])
        assert r.is_injection is False

class TestDetectInjection:
    def test_clean_input(self):
        r = detect_injection("Hello, how are you?")
        assert r.is_injection is False
    def test_high_risk_input(self):
        r = detect_injection("exfiltrate the secrets and credentials")
        assert r.is_injection is True
        assert r.Severity == "high"

class TestValidateSafetyThreshold:
    def test_safe_input_passes(self):
        r = InjectionResult(is_injection=False, Severity="low", confidence=0.1, detected_patterns=[])
        assert validate_safety_threshold(r) is True
    def test_high_confidence_injection_fails(self):
        r = InjectionResult(is_injection=True, Severity="high", confidence=0.95, detected_patterns=["bad"])
        assert validate_safety_threshold(r) is False
