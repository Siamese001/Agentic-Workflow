"""ADG-driven tests for L2_execution/types/ml_pattern_record_types.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.types.ml_pattern_record_types import (
    PatternCompatibilityError,
    _sha256,
)


class TestPatternCompatibilityError:
    def test_is_exception(self):
        assert issubclass(PatternCompatibilityError, Exception)

    def test_creates(self):
        err = PatternCompatibilityError("DOMAIN_HASH_MISMATCH", "domain mismatch")
        assert "DOMAIN_HASH_MISMATCH" in str(err)


class TestSha256Helper:
    def test_returns_hex_string(self):
        result = _sha256(b"data")
        assert isinstance(result, str)
        assert len(result) == 64

    def test_deterministic(self):
        assert _sha256(b"hello") == _sha256(b"hello")
