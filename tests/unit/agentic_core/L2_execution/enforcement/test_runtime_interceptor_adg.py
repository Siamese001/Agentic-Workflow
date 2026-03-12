"""ADG-driven tests for L2_execution/enforcement/runtime_interceptor.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.enforcement.runtime_interceptor import (
    MutableReferenceError,
    assert_immutable_reference,
)


class TestMutableReferenceError:
    def test_is_runtime_error(self):
        assert issubclass(MutableReferenceError, RuntimeError)


class TestAssertImmutableReference:
    def test_callable(self):
        assert callable(assert_immutable_reference)

    def test_passes_for_frozen_dataclass(self):
        from dataclasses import dataclass

        @dataclass(frozen=True)
        class Frozen:
            x: int

        assert_immutable_reference(Frozen(x=1), context="test")

    def test_passes_for_string(self):
        assert_immutable_reference("hello", context="test")

    def test_passes_for_int(self):
        assert_immutable_reference(42, context="test")
