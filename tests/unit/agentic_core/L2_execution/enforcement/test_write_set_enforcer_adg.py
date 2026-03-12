"""ADG-driven tests for L2_execution/enforcement/write_set_enforcer.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.enforcement.write_set_enforcer import (
    WriteSetEnforcer,
    WriteSetViolation,
)


class TestWriteSetViolation:
    def test_is_runtime_error(self):
        assert issubclass(WriteSetViolation, RuntimeError)


class TestWriteSetEnforcer:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(WriteSetEnforcer)

    def test_creates(self):
        enforcer = WriteSetEnforcer(declared_write_set=frozenset({"key_a", "key_b"}))
        assert enforcer is not None

    def test_record_declared_write_ok(self):
        enforcer = WriteSetEnforcer(declared_write_set=frozenset({"key_a"}))
        enforcer.record_write("key_a")

    def test_record_undeclared_write_raises(self):
        enforcer = WriteSetEnforcer(declared_write_set=frozenset({"key_a"}))
        with pytest.raises(WriteSetViolation):
            enforcer.record_write("key_c")
