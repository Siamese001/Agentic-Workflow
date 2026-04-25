"""Out-of-band plane invariants (spec lines 758–783).

The Calibration / Assurance / Audit-Forensic planes feed *future* policy
versions only. They MUST NOT mutate a `GovernanceResult` for the current
run. This module exposes a single API guard that any out-of-band caller
must invoke before touching a frozen result.
"""

from __future__ import annotations

from typing import Any

from agentic_core.L5_safety.v5.contracts import GovernanceResult


class OutOfBandMutationError(RuntimeError):
    """Raised when an out-of-band component attempts to mutate a sealed result."""


def assert_no_current_run_mutation(
    *,
    sealed_result: GovernanceResult,
    proposed_changes: dict[str, Any] | None = None,
) -> None:
    """Spec OUT-OF-BAND INVARIANTS (lines 778–782).

    The function is a contract-level assertion. It refuses any non-empty
    ``proposed_changes`` mapping. Out-of-band callers feed
    ``policy_version_next`` candidates through the calibration plane —
    NOT through this API.

    Raises:
        OutOfBandMutationError: if ``proposed_changes`` is non-empty.
    """
    # Sealed result is a frozen dataclass already. If the caller attempts
    # to forward changes, they must go through the promotion gate.
    if proposed_changes:
        raise OutOfBandMutationError(
            "out-of-band plane attempted to mutate sealed GovernanceResult "
            f"(request_id={sealed_result.review_request.request_id}, "
            f"keys={sorted(proposed_changes)}). Spec lines 778–782: "
            "learning signals inform future thresholds only after promotion.",
        )

    # The frozen dataclass invariant is itself the second line of defense:
    # any setattr on `sealed_result` raises FrozenInstanceError natively.


__all__ = [
    "OutOfBandMutationError",
    "assert_no_current_run_mutation",
]
