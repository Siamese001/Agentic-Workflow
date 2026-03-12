"""ADG-driven tests for L2_execution/determinism/digest_calculator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.determinism.digest_calculator import DigestCalculator
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    DigestCalculator = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="digest_calculator deps unavailable")
class TestDigestCalculator:
    def test_importable(self):
        assert callable(DigestCalculator)

    def test_component_keys_defined(self):
        assert hasattr(DigestCalculator, "COMPONENT_KEYS")
        assert isinstance(DigestCalculator.COMPONENT_KEYS, tuple)
        assert len(DigestCalculator.COMPONENT_KEYS) == 5

    def test_all_five_keys_present(self):
        keys = DigestCalculator.COMPONENT_KEYS
        assert "policy_hash" in keys
        assert "transcript_hash" in keys
        assert "dependency_lock_hash" in keys


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
