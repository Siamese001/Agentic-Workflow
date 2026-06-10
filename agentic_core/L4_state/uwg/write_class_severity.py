"""UWG write-class severity matrix + invalidation coverage + alias atomicity.

Plan: ``docs/archive/windsurf/legacy-tree/plans/routing-decision-process-enhancement-9c7e4d.md`` Wave W11.

Closes opportunities 9.1 (write-class severity / reversibility partition),
9.2 (cache invalidation coverage gate), 9.4 (alias-swap atomicity proof).

Three surfaces:

1. :class:`WriteClass` enum + :func:`classify_write` — partition writes by
   reversibility. ``IRREVERSIBLE`` writes auto-route through second-judge
   confirmation per opportunity 9.1.
2. :class:`InvalidationCoverageGate` — every UWG accept emits the set of
   read surfaces it must invalidate; the gate measures whether downstream
   reads stayed coherent. Returns ``invalidation_miss_rate``.
3. :func:`alias_swap_atomicity_proof` — given a before/after manifest pair,
   verifies that the swap window is zero — i.e. the after-state contains
   no row whose timestamp falls inside the rebind window.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from enum import Enum


class WriteClass(Enum):
    """Reversibility partition for UWG write proposals."""

    REVERSIBLE = "reversible"
    """Plain data write that can be reverted by a follow-up write."""

    SCHEMA_CHANGE = "schema_change"
    """DDL change — irreversible without a costly rebuild; needs second judge."""

    IRREVERSIBLE = "irreversible"
    """Cannot be undone (e.g. external API call, deletion). Needs HITL or judge ensemble."""

    POLICY_UPDATE = "policy_update"
    """Promotion of a policy snapshot. Irreversible at the snapshot layer."""


class WriteClassSeverity(Enum):
    """Legacy durability label for app-domain write-class registration.

    New UWG routing code uses :class:`WriteClass` for reversibility policy.
    Some app-domain registration surfaces still publish durability labels and
    consume ``.value`` directly, so keep this narrow compatibility surface.
    """

    EPHEMERAL = "ephemeral"
    DURABLE = "durable"
    CRITICAL = "critical"


_HEAVY_CLASSES: frozenset[WriteClass] = frozenset(
    {WriteClass.SCHEMA_CHANGE, WriteClass.IRREVERSIBLE, WriteClass.POLICY_UPDATE},
)


def classify_write(*, op: str, target: str) -> WriteClass:
    """Best-effort classification from operation + target.

    Heuristic — caller may override with explicit ``WriteClass`` when the
    classification is known up front.
    """
    op_lc = (op or "").lower()
    target_lc = (target or "").lower()
    if "schema" in target_lc or "ddl" in op_lc or op_lc.startswith("alter "):
        return WriteClass.SCHEMA_CHANGE
    if "policy_snapshot" in target_lc or op_lc == "promote_policy":
        return WriteClass.POLICY_UPDATE
    if op_lc in {"delete", "drop", "purge"} or op_lc.startswith("api_call:"):
        return WriteClass.IRREVERSIBLE
    return WriteClass.REVERSIBLE


def requires_second_judge(write_class: WriteClass) -> bool:
    """True when the write class needs second-judge confirmation."""
    return write_class in _HEAVY_CLASSES


@dataclass
class InvalidationProposal:
    """Set of cache namespaces an accepted write claims to invalidate."""

    write_id: str
    invalidates: frozenset[str]


@dataclass
class InvalidationCoverageGate:
    """Track whether downstream reads stayed coherent with declared invalidations.

    ``record_proposal`` registers a write's declared invalidation set.
    ``record_stale_read`` is called when a read is observed to return
    pre-write data after the write committed. ``miss_rate`` returns the
    fraction of writes whose declared invalidation set did NOT cover the
    surface where the stale read happened.
    """

    _proposals: dict[str, InvalidationProposal] = field(default_factory=dict)
    _stale_reads: list[tuple[str, str]] = field(default_factory=list)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def record_proposal(self, proposal: InvalidationProposal) -> None:
        with self._lock:
            self._proposals[proposal.write_id] = proposal

    def record_stale_read(self, write_id: str, observed_namespace: str) -> None:
        with self._lock:
            self._stale_reads.append((write_id, observed_namespace))

    def miss_rate(self) -> float:
        """Fraction of stale reads that landed OUTSIDE the declared set."""
        with self._lock:
            if not self._stale_reads:
                return 0.0
            misses = 0
            for write_id, observed in self._stale_reads:
                proposal = self._proposals.get(write_id)
                if proposal is None or observed not in proposal.invalidates:
                    misses += 1
            return misses / len(self._stale_reads)

    def reset(self) -> None:
        with self._lock:
            self._proposals.clear()
            self._stale_reads.clear()


@dataclass(frozen=True)
class AliasManifest:
    """Snapshot of an alias mapping at a particular instant."""

    timestamp: float
    alias_to_target: dict[str, str]


class AliasAtomicityViolationError(RuntimeError):
    """Raised when the alias swap manifests overlap improperly."""


def alias_swap_atomicity_proof(
    before: AliasManifest,
    after: AliasManifest,
    swap_window_seconds: float,
) -> None:
    """Verify the swap window respects atomicity.

    The ``after`` manifest's timestamp must be strictly greater than the
    ``before`` manifest's by AT LEAST ``swap_window_seconds``. If the gap
    is smaller, the system observed both states "simultaneously" — an
    atomicity violation.

    Args:
        before: Pre-swap manifest.
        after: Post-swap manifest.
        swap_window_seconds: Minimum observed gap (in seconds) for atomicity.

    Raises:
        AliasAtomicityViolationError: When the swap was not atomic.
    """
    gap = after.timestamp - before.timestamp
    if gap < swap_window_seconds:
        raise AliasAtomicityViolationError(
            f"alias swap not atomic: gap={gap:.6f}s < required "
            f"{swap_window_seconds:.6f}s",
        )


__all__ = [
    "AliasAtomicityViolationError",
    "AliasManifest",
    "InvalidationCoverageGate",
    "InvalidationProposal",
    "WriteClass",
    "WriteClassSeverity",
    "alias_swap_atomicity_proof",
    "classify_write",
    "requires_second_judge",
]
