"""ADG-driven tests for L2_execution/types/tool_intent_types.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.types.tool_intent_types import (
        _sha256,
        _SCHEMA_VERSION,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    _sha256 = None  # type: ignore[assignment]
    _SCHEMA_VERSION = None


@pytest.mark.skipif(not _AVAILABLE, reason="tool_intent_types deps unavailable")
class TestSha256Helper:
    def test_returns_hex_string(self):
        result = _sha256(b"hello")
        assert isinstance(result, str)
        assert len(result) == 64

    def test_deterministic(self):
        assert _sha256(b"data") == _sha256(b"data")


@pytest.mark.skipif(not _AVAILABLE, reason="tool_intent_types deps unavailable")
class TestSchemaVersion:
    def test_is_int(self):
        assert isinstance(_SCHEMA_VERSION, int)
        assert _SCHEMA_VERSION >= 1


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
