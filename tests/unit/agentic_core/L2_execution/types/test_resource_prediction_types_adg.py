"""ADG-driven tests for L2_execution/types/resource_prediction_types.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.types.resource_prediction_types import FailureSignature


class TestFailureSignature:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(FailureSignature)

    def test_is_frozen(self):
        sig = FailureSignature(component="redis", failure_type="timeout", fingerprint="a" * 64)
        with pytest.raises((AttributeError, TypeError)):
            sig.component = "db"

    def test_creates(self):
        sig = FailureSignature(component="redis", failure_type="timeout", fingerprint="a" * 64)
        assert sig.component == "redis"
        assert sig.failure_type == "timeout"

    def test_canonical_bytes_returns_bytes(self):
        sig = FailureSignature(component="redis", failure_type="timeout", fingerprint="a" * 64)
        result = sig.canonical_bytes()
        assert isinstance(result, bytes)

    def test_canonical_bytes_deterministic(self):
        sig = FailureSignature(component="c", failure_type="t", fingerprint="f" * 64)
        assert sig.canonical_bytes() == sig.canonical_bytes()
