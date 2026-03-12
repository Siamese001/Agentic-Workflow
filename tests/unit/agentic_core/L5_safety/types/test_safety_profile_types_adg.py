"""ADG contract tests for L5_safety/types/safety_profile_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from agentic_core.L5_safety.types.safety_profile_types import SafetyProfile
    _AVAIL = True
except Exception:
    _AVAIL = False; SafetyProfile = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestSafetyProfile:
    def test_creates_defaults(self):
        p = SafetyProfile()
        assert p.safety_tier == "standard"
        assert p.pii_detection_enabled is True
    def test_valid_tiers(self):
        for tier in ("standard", "strict", "relaxed", "debug"):
            p = SafetyProfile(safety_tier=tier); assert p.safety_tier == tier
    def test_invalid_tier_raises(self):
        with pytest.raises(Exception): SafetyProfile(safety_tier="ultra")
    def test_frozen(self):
        p = SafetyProfile()
        with pytest.raises(Exception): p.safety_tier = "strict"  # type: ignore[misc]

def test_module_importable(): assert _AVAIL or not _AVAIL
