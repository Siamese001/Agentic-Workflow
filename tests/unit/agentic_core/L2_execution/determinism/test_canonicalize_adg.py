"""ADG-driven tests for L2_execution/determinism/canonicalize.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.determinism.canonicalize import canonical_bytes


class TestCanonicalBytes:
    def test_callable(self):
        assert callable(canonical_bytes)

    def test_returns_bytes(self):
        result = canonical_bytes({"key": "value"})
        assert isinstance(result, bytes)

    def test_deterministic(self):
        obj = {"b": 2, "a": 1}
        assert canonical_bytes(obj) == canonical_bytes(obj)

    def test_sort_keys(self):
        a = canonical_bytes({"b": 2, "a": 1})
        b = canonical_bytes({"a": 1, "b": 2})
        assert a == b

    def test_plain_string(self):
        result = canonical_bytes("hello")
        assert isinstance(result, bytes)
