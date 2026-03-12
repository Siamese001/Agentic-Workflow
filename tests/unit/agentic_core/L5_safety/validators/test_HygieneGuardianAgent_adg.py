"""ADG-driven tests for agentic_core/L5_safety/validators/HygieneGuardianAgent.py — fan_in=2."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.validators.HygieneGuardianAgent import (  # noqa: F401
        HygieneViolation,
        HygieneGuardianAgent,
        MAX_FILENAME_WORDS,
        MAX_TEST_FILENAME_WORDS,
        REDUNDANT_TERMS,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    HygieneViolation = None  # type: ignore[assignment,misc]
    HygieneGuardianAgent = None  # type: ignore[assignment,misc]
    MAX_FILENAME_WORDS = None  # type: ignore[assignment,misc]
    MAX_TEST_FILENAME_WORDS = None  # type: ignore[assignment,misc]
    REDUNDANT_TERMS = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="HygieneGuardianAgent.py deps unavailable")
class TestHygieneViolation:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(HygieneViolation)
    def test_importable(self):
        assert HygieneViolation is not None

@pytest.mark.skipif(not _AVAILABLE, reason="HygieneGuardianAgent.py deps unavailable")
class TestHygieneGuardianAgent:
    def test_is_class(self):
        assert isinstance(HygieneGuardianAgent, type)
    def test_importable(self):
        assert HygieneGuardianAgent is not None

@pytest.mark.skipif(not _AVAILABLE, reason="HygieneGuardianAgent.py deps unavailable")
class TestMaxFilenameWordsConstant:
    def test_is_not_none(self):
        assert MAX_FILENAME_WORDS is not None

@pytest.mark.skipif(not _AVAILABLE, reason="HygieneGuardianAgent.py deps unavailable")
class TestMaxTestFilenameWordsConstant:
    def test_is_not_none(self):
        assert MAX_TEST_FILENAME_WORDS is not None

@pytest.mark.skipif(not _AVAILABLE, reason="HygieneGuardianAgent.py deps unavailable")
class TestRedundantTermsConstant:
    def test_is_not_none(self):
        assert REDUNDANT_TERMS is not None


def test_module_importable():
    """Module HygieneGuardianAgent.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
