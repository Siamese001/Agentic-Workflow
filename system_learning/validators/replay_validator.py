"""G-16-20: Deterministic replay validator for System Learning engines.

Validates that optimization engines produce identical outputs when run twice
with the same inputs (determinism enforcement).

Invariants:
  - No randomness/time/env access
  - Engine function and canonicalizer are injected
  - No store access
  - Fail-closed on any determinism violation
"""

from __future__ import annotations

import hashlib
from typing import Any, Callable

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    emit_determinism_digest,
    record_execution_trace,
)

emit_determinism_digest("replay_validator", "replay_validator_digest")
record_execution_trace("replay_validator", "replay_validator_trace")



class DeterminismViolation(RuntimeError):
    """Raised when an engine produces different outputs across identical runs."""


def replay_validate(
    snapshot: Any, engine_fn: Callable[[Any], Any], *, canonicalize_fn: Callable[[Any], bytes]
) -> str:
    """Validate that an engine produces identical outputs across two runs.

    Runs the engine function twice with the same snapshot input, canonicalizes
    each output, and compares SHA-256 hashes. Raises if hashes differ.

    Parameters
    ----------
    snapshot : Any
        The snapshot input to pass to the engine function.
    engine_fn : Callable[[Any], Any]
        The engine function to validate (must be deterministic).
    canonicalize_fn : Callable[[Any], bytes]
        Function to convert engine output to canonical bytes for hashing.

    Returns
    -------
    str
        SHA-256 hex digest of the canonical output (if deterministic).

    Raises
    ------
    DeterminismViolation
        If the two runs produce different hashes.

    Examples
    --------
    >>> def my_engine(snapshot):
    ...     return {"value": snapshot["input"] * 2}
    >>> def canonicalize(output):
    ...     return str(output).encode("utf-8")
    >>> snapshot = {"input": 5}
    >>> hash_result = replay_validate(snapshot, my_engine, canonicalize_fn=canonicalize)
    """
    output1 = engine_fn(snapshot)
    canonical1 = canonicalize_fn(output1)
    hash1 = hashlib.sha256(canonical1).hexdigest()
    output2 = engine_fn(snapshot)
    canonical2 = canonicalize_fn(output2)
    hash2 = hashlib.sha256(canonical2).hexdigest()
    if hash1 != hash2:
        raise DeterminismViolation(
            f"DETERMINISM_VIOLATION: Engine produced different outputs across runs.\nRun 1 hash: {hash1}\nRun 2 hash: {hash2}"
        )
    return hash1
