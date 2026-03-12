"""
Wave 6.1: L2.2 Write-Set Enforcement.

Compares actual writes against the declared_write_set from L2.0.
Aborts execution if an undeclared write is attempted.

Lives in L2 (execution enforcement) per gravity rules.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

class WriteSetViolation(RuntimeError):
    """Raised when an undeclared write is attempted."""

@dataclass
class WriteSetEnforcer:
    """Enforces that actual writes match the declared write set.

    Usage::

        enforcer = WriteSetEnforcer(
            declared_write_set={"key_a", "key_b"}
        )
        enforcer.record_write("key_a")   # ok
        enforcer.record_write("key_c")   # raises
    """
    declared_write_set: frozenset[str]
    _actual_writes: set[str] = field(default_factory=set, init=False, repr=False)
    _aborted: bool = field(default=False, init=False, repr=False)

    def record_write(self, key: str) -> None:
        """Record an actual write and enforce declaration.

        Raises WriteSetViolation if key is not in the
        declared write set.
        """
        if self._aborted:
            raise WriteSetViolation('Execution aborted due to prior write-set violation.')
        if key not in self.declared_write_set:
            self._aborted = True
            raise WriteSetViolation(f"Undeclared write to '{key}'. Declared set: {sorted(self.declared_write_set)}")
        self._actual_writes.add(key)

    @property
    def actual_writes(self) -> frozenset[str]:
        """Return the set of actual writes recorded."""
        return frozenset(self._actual_writes)

    @property
    def is_complete(self) -> bool:
        """True if all declared writes have been performed."""
        return self._actual_writes == set(self.declared_write_set)

    @property
    def is_aborted(self) -> bool:
        return self._aborted

    def verify(self) -> bool:
        """Verify no undeclared writes occurred.

        Returns True if actual_writes is a subset of
        declared_write_set and execution was not aborted.
        """
        if self._aborted:
            return False
        return self._actual_writes.issubset(self.declared_write_set)
