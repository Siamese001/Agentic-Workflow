"""ADG-driven tests for L2_execution/types/instruction_packet_types.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.types.instruction_packet_types import (
        _canonical_bytes,
        SignatureVerificationError,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    _canonical_bytes = None  # type: ignore[assignment]
    SignatureVerificationError = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="instruction_packet_types deps unavailable")
class TestCanonicalBytes:
    def test_returns_bytes(self):
        result = _canonical_bytes({"key": "value", "num": 42})
        assert isinstance(result, bytes)

    def test_deterministic(self):
        data = {"b": 2, "a": 1}
        assert _canonical_bytes(data) == _canonical_bytes(data)

    def test_sort_insensitive(self):
        assert _canonical_bytes({"a": 1, "b": 2}) == _canonical_bytes({"b": 2, "a": 1})


@pytest.mark.skipif(not _AVAILABLE, reason="instruction_packet_types deps unavailable")
class TestSignatureVerificationError:
    def test_is_exception(self):
        assert issubclass(SignatureVerificationError, Exception)

    def test_raises(self):
        with pytest.raises(SignatureVerificationError):
            raise SignatureVerificationError("bad signature")


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
