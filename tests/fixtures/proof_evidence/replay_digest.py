"""Replay-digest fixture for the W4d-4 proof-evidence pilot.

The replay invariant in the ledger is: same input -> same digest, across
runs. Until the real runtime emits replay receipts, this fixture provides
a deterministic content hash that the pilot tests can use to assert
stability.

The digest function is intentionally simple (sorted-keys JSON + sha256)
so any reasonable runtime implementation will produce the SAME digest
for the same input — which means once the runtime ships, the pilot
tests can compare the runtime digest against this fixture's digest
without changing the test body.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any


class ReplayStabilityError(AssertionError):
    """Raised when a replay digest is not stable across two runs."""


def deterministic_digest(payload: Any) -> str:
    """SHA-256 of the canonical sorted-keys JSON encoding of ``payload``.

    Strict separators ensure no whitespace-induced drift. The function is
    pure: same payload -> same digest, byte-for-byte.
    """
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        default=str,  # tolerate datetime/Path-like objects deterministically
        ensure_ascii=True,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def assert_replay_stable(payload: Any, *, n_iterations: int = 3) -> str:
    """Assert that ``deterministic_digest(payload)`` is stable across N runs.

    Returns the stable digest. Raises ReplayStabilityError on drift.
    """
    digests = [deterministic_digest(payload) for _ in range(n_iterations)]
    if len(set(digests)) != 1:
        raise ReplayStabilityError(
            f"digest unstable across {n_iterations} runs: {digests}"
        )
    return digests[0]


def assert_replay_drift_detected(
    payload_a: Any,
    payload_b: Any,
) -> None:
    """Negative control: two semantically different payloads MUST yield
    different digests. Raises if they unexpectedly collide."""
    if deterministic_digest(payload_a) == deterministic_digest(payload_b):
        raise ReplayStabilityError(
            "expected drift between distinct payloads, but digests collided"
        )
