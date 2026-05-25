"""EvalGatedL4StateWriter — decorator enforcing eval-freshness at write time.

Wraps any :class:`~system_learning.engines.l4_state_writer.L4StateWriter`
implementation with a pre-write check against
:class:`~system_learning.engines.eval_freshness_gate.EvalFreshnessGate`. If the
gate blocks the write (stale or missing gating eval for the change class), an
:class:`EvalFreshnessViolation` is raised before the underlying writer is
called; the inner writer sees no mutation.

Consumer pattern:

.. code-block:: python

    inner = FileBackedL4StateWriter(...)
    gate = EvalFreshnessGate.from_repo(repo_root)

    def change_class_fn(bucket_name: str) -> str:
        return {
            "l4a_detection_signal": "baseline",
            "l4b_healing_snapshot": "baseline",
            "l4c_shadow_drift": "baseline",
            "l4c_policy_recommendation": "policy",
            "l4c_retrieval_profile_proposal": "retrieval_profile",
        }[bucket_name]

    writer = EvalGatedL4StateWriter(
        inner=inner,
        gate=gate,
        change_class_for_bucket=change_class_fn,
    )

The decorator is intentionally separate from the existing writer implementations
so downstream callers can opt in without forcing a breaking change on the
Protocol. Plan SSOT: ``.windsurf/plans/system-learning-waves-7b3c91.md`` C1.

Eval records are provided per-call via an optional ``eval_record_timestamp``
keyword that passes through to the gate; callers that never supplied one can
still use the decorator — the gate will block only when the change class has a
non-null TTL.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol

from .eval_freshness_gate import (
    EvalFreshnessGate,
    EvalFreshnessViolation,
    FreshnessDecision,
)


class _WriterProtocol(Protocol):
    """Structural type for the subset of L4StateWriter we delegate to."""

    def write_l4a_detection_signal(
        self, *, payload_bytes: bytes, component_name: str, created_utc: int
    ) -> str: ...

    def write_l4b_healing_snapshot(
        self, *, payload_bytes: bytes, component_name: str, created_utc: int
    ) -> str: ...

    def write_l4c_shadow_drift(
        self, *, payload_bytes: bytes, component_name: str, created_utc: int
    ) -> str: ...

    def write_l4c_policy_recommendation(
        self, *, payload_bytes: bytes, component_name: str, created_utc: int
    ) -> str: ...

    def write_l4c_retrieval_profile_proposal(
        self, *, payload_bytes: bytes, component_name: str, created_utc: int
    ) -> str: ...


# Default bucket → change_class mapping. Callers may override.
_DEFAULT_BUCKET_CLASS: dict[str, str] = {
    "l4a_detection_signal": "baseline",
    "l4b_healing_snapshot": "baseline",
    "l4c_shadow_drift": "baseline",
    "l4c_policy_recommendation": "policy",
    "l4c_retrieval_profile_proposal": "retrieval_profile",
}


@dataclass(frozen=True)
class GateCheckRecord:
    """Audit record returned by :meth:`EvalGatedL4StateWriter.last_check`."""

    bucket: str
    change_class: str
    decision: FreshnessDecision


class EvalGatedL4StateWriter:
    """Decorator that enforces :class:`EvalFreshnessGate` before every L4 write.

    The decorator is stateful only for a single-entry "last check" cache so
    callers can introspect the most recent decision without plumbing it back
    through every write path.
    """

    def __init__(
        self,
        *,
        inner: _WriterProtocol,
        gate: EvalFreshnessGate,
        change_class_for_bucket: Callable[[str], str] | None = None,
        eval_record_timestamp_for_bucket: Callable[[str], float | None] | None = None,
    ) -> None:
        self._inner = inner
        self._gate = gate
        self._mapping = change_class_for_bucket or (lambda bucket: _DEFAULT_BUCKET_CLASS.get(bucket, bucket))
        self._eval_ts = eval_record_timestamp_for_bucket or (lambda _bucket: None)
        self._last_check: GateCheckRecord | None = None

    @property
    def inner(self) -> _WriterProtocol:
        return self._inner

    def last_check(self) -> GateCheckRecord | None:
        return self._last_check

    # ------------------------------------------------------------------
    # Internal check helper
    # ------------------------------------------------------------------

    def _enforce(
        self,
        *,
        bucket: str,
        created_utc: int,
        eval_record_timestamp: float | None = None,
    ) -> None:
        change_class = self._mapping(bucket)
        ts = float(eval_record_timestamp) if eval_record_timestamp is not None else self._eval_ts(bucket)
        decision = self._gate.check(
            change_class=change_class,
            eval_record_timestamp=ts,
            now=float(created_utc) if created_utc else None,
        )
        self._last_check = GateCheckRecord(bucket=bucket, change_class=change_class, decision=decision)
        if decision.blocked:
            raise EvalFreshnessViolation(
                f"L4 write to bucket={bucket!r} blocked by eval-freshness gate: {decision.reason}"
            )

    # ------------------------------------------------------------------
    # Delegated write methods
    # ------------------------------------------------------------------

    def write_l4a_detection_signal(
        self,
        *,
        payload_bytes: bytes,
        component_name: str,
        created_utc: int,
        eval_record_timestamp: float | None = None,
    ) -> str:
        self._enforce(
            bucket="l4a_detection_signal",
            created_utc=created_utc,
            eval_record_timestamp=eval_record_timestamp,
        )
        return self._inner.write_l4a_detection_signal(
            payload_bytes=payload_bytes,
            component_name=component_name,
            created_utc=created_utc,
        )

    def write_l4b_healing_snapshot(
        self,
        *,
        payload_bytes: bytes,
        component_name: str,
        created_utc: int,
        eval_record_timestamp: float | None = None,
    ) -> str:
        self._enforce(
            bucket="l4b_healing_snapshot",
            created_utc=created_utc,
            eval_record_timestamp=eval_record_timestamp,
        )
        return self._inner.write_l4b_healing_snapshot(
            payload_bytes=payload_bytes,
            component_name=component_name,
            created_utc=created_utc,
        )

    def write_l4c_shadow_drift(
        self,
        *,
        payload_bytes: bytes,
        component_name: str,
        created_utc: int,
        eval_record_timestamp: float | None = None,
    ) -> str:
        self._enforce(
            bucket="l4c_shadow_drift",
            created_utc=created_utc,
            eval_record_timestamp=eval_record_timestamp,
        )
        return self._inner.write_l4c_shadow_drift(
            payload_bytes=payload_bytes,
            component_name=component_name,
            created_utc=created_utc,
        )

    def write_l4c_policy_recommendation(
        self,
        *,
        payload_bytes: bytes,
        component_name: str,
        created_utc: int,
        eval_record_timestamp: float | None = None,
    ) -> str:
        self._enforce(
            bucket="l4c_policy_recommendation",
            created_utc=created_utc,
            eval_record_timestamp=eval_record_timestamp,
        )
        return self._inner.write_l4c_policy_recommendation(
            payload_bytes=payload_bytes,
            component_name=component_name,
            created_utc=created_utc,
        )

    def write_l4c_retrieval_profile_proposal(
        self,
        *,
        payload_bytes: bytes,
        component_name: str,
        created_utc: int,
        eval_record_timestamp: float | None = None,
    ) -> str:
        self._enforce(
            bucket="l4c_retrieval_profile_proposal",
            created_utc=created_utc,
            eval_record_timestamp=eval_record_timestamp,
        )
        return self._inner.write_l4c_retrieval_profile_proposal(
            payload_bytes=payload_bytes,
            component_name=component_name,
            created_utc=created_utc,
        )


__all__ = ["EvalGatedL4StateWriter", "GateCheckRecord"]
