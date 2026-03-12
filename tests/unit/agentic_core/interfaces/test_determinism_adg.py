"""ADG-driven tests for interfaces/determinism.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.interfaces.determinism import DETERMINISM_EXCLUDED_FIELDS


class TestDeterminismExcludedFields:
    def test_is_frozenset(self):
        assert isinstance(DETERMINISM_EXCLUDED_FIELDS, frozenset)

    def test_contains_timestamp(self):
        assert "timestamp" in DETERMINISM_EXCLUDED_FIELDS

    def test_contains_duration_ms(self):
        assert "duration_ms" in DETERMINISM_EXCLUDED_FIELDS

    def test_contains_trace_id(self):
        assert "trace_id" in DETERMINISM_EXCLUDED_FIELDS


class TestCanonicalBytes:
    def test_importable(self):
        from agentic_core.interfaces.determinism import canonical_bytes
        assert callable(canonical_bytes)

    def test_returns_bytes(self):
        from agentic_core.interfaces.determinism import canonical_bytes
        result = canonical_bytes({"key": "value"})
        assert isinstance(result, bytes)


class TestCanonicalHash:
    def test_importable(self):
        from agentic_core.interfaces.determinism import canonical_hash
        assert callable(canonical_hash)

    def test_returns_string(self):
        from agentic_core.interfaces.determinism import canonical_hash
        result = canonical_hash({"key": "value"})
        assert isinstance(result, str)
        assert len(result) == 64  # sha256 hex
