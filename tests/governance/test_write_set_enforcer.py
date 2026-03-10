"""Wave 6.1: L2.2 Write-Set Enforcement tests.

Validates:
- Declared write executes successfully
- Undeclared write attempt is blocked
- Aborted enforcer rejects all subsequent writes
- verify() returns correct state
- actual_writes tracks correctly
"""

import pytest

from agentic_core.L2_execution.enforcement.write_set_enforcer import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    WriteSetEnforcer,
    WriteSetViolation,
)

pytestmark = pytest.mark.governance


class TestDeclaredWriteAllowed:
    """Declared writes must succeed."""

    def test_declared_write_succeeds(self):
        enforcer = WriteSetEnforcer(declared_write_set=frozenset({"key_a", "key_b"}))
        enforcer.record_write("key_a")
        assert "key_a" in enforcer.actual_writes

    def test_multiple_declared_writes(self):
        enforcer = WriteSetEnforcer(declared_write_set=frozenset({"a", "b", "c"}))
        enforcer.record_write("a")
        enforcer.record_write("b")
        enforcer.record_write("c")
        assert enforcer.is_complete

    def test_verify_passes_on_declared(self):
        enforcer = WriteSetEnforcer(declared_write_set=frozenset({"x"}))
        enforcer.record_write("x")
        assert enforcer.verify() is True


class TestUndeclaredWriteBlocked:
    """Undeclared writes must raise."""

    def test_undeclared_write_raises(self):
        enforcer = WriteSetEnforcer(declared_write_set=frozenset({"key_a"}))
        with pytest.raises(WriteSetViolation, match="Undeclared write"):
            enforcer.record_write("key_z")

    def test_undeclared_aborts_enforcer(self):
        enforcer = WriteSetEnforcer(declared_write_set=frozenset({"key_a"}))
        with pytest.raises(WriteSetViolation):
            enforcer.record_write("bad_key")
        assert enforcer.is_aborted

    def test_aborted_rejects_subsequent(self):
        enforcer = WriteSetEnforcer(declared_write_set=frozenset({"a", "b"}))
        with pytest.raises(WriteSetViolation):
            enforcer.record_write("bad")
        with pytest.raises(WriteSetViolation, match="aborted"):
            enforcer.record_write("a")

    def test_verify_fails_after_violation(self):
        enforcer = WriteSetEnforcer(declared_write_set=frozenset({"a"}))
        with pytest.raises(WriteSetViolation):
            enforcer.record_write("bad")
        assert enforcer.verify() is False


class TestWriteSetTracking:
    """actual_writes must track correctly."""

    def test_empty_initially(self):
        enforcer = WriteSetEnforcer(declared_write_set=frozenset({"a"}))
        assert enforcer.actual_writes == frozenset()

    def test_partial_not_complete(self):
        enforcer = WriteSetEnforcer(declared_write_set=frozenset({"a", "b"}))
        enforcer.record_write("a")
        assert not enforcer.is_complete

    def test_duplicate_write_idempotent(self):
        enforcer = WriteSetEnforcer(declared_write_set=frozenset({"a"}))
        enforcer.record_write("a")
        enforcer.record_write("a")
        assert enforcer.actual_writes == frozenset({"a"})
