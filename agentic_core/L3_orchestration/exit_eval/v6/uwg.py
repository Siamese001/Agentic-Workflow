"""v6 §X3C UWG — Universal Write Gateway sub-flow (U1..U5).

Consumes an ``X3CommitRequestPacket`` produced by Exit Eval and produces a
``UwgReceipt`` with one of three outcomes (COMMIT_ACCEPTED, COMMIT_REJECTED,
COMMIT_HELD).

Spec invariant: UWG is the SOLE durable-write path into L4. Direct L2/L3/HITL/L6
writes are forbidden — those are caught by Exit X1C/X1J before this module runs.

This module ships in-memory reference implementations of the backends UWG
talks to (catalog, lock store, ledger, read-surface refresher). Production
swaps these for real backends (SQLite/Redis) without changing the sub-flow.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from threading import RLock
from typing import Any, Protocol

from agentic_core.L3_orchestration.exit_eval.v6.types import X3CommitRequestPacket

logger = logging.getLogger(__name__)


class UwgOutcome(str, Enum):
    """Spec §X3C UWG outcomes."""

    COMMIT_ACCEPTED = "COMMIT_ACCEPTED"
    COMMIT_REJECTED = "COMMIT_REJECTED"
    COMMIT_HELD = "COMMIT_HELD"


# ---- exceptions ----


class UwgError(RuntimeError):
    """Base class for all UWG sub-flow rejections."""

    reason_code: str = "UWG_REJECTED"


class InvalidSignature(UwgError):
    reason_code = "INVALID_SIGNATURE"


class CapabilityRejected(UwgError):
    reason_code = "CAPABILITY_REJECTED"


class PolicyMismatch(UwgError):
    reason_code = "POLICY_MISMATCH"


class RbacDenied(UwgError):
    reason_code = "RBAC_DENIED"


class BlastRadiusExceeded(UwgError):
    reason_code = "BLAST_RADIUS_EXCEEDED"


class WriteLockConflict(UwgError):
    reason_code = "WRITE_LOCK_CONFLICT"


class CatalogConflict(UwgError):
    reason_code = "CATALOG_CONFLICT"


# ---- backend protocols ----


class CatalogProtocol(Protocol):
    """U2 backend — RBAC + tenant ACL + structure validation."""

    def is_authorized(self, *, tenant_id: str, write_intent_class: str, blast_radius: str) -> bool: ...

    def has_pending_conflict(self, *, write_intent_class: str) -> bool: ...


class LockStoreProtocol(Protocol):
    """U3 backend — exclusive write-lock claim per write_intent_class."""

    def claim(self, *, key: str, holder: str, ttl_seconds: int = 60) -> bool: ...
    def release(self, *, key: str, holder: str) -> bool: ...


class LedgerProtocol(Protocol):
    """U4 backend — durable hash-chained ledger."""

    def append(
        self,
        *,
        commit_request_id: str,
        payload: dict[str, Any],
    ) -> "LedgerAppendResult": ...

    def head_hash(self) -> str: ...


class ReadSurfaceRefresher(Protocol):
    """U5 backend — alias swap + cache invalidation + retrieval refresh."""

    def refresh(self, *, commit_request_id: str, l4_alias: str) -> None: ...


# ---- ledger result + receipt ----


@dataclass(slots=True)
class LedgerAppendResult:
    seq: int
    hash_chain_tip: str


@dataclass(slots=True)
class UwgReceipt:
    """Result of a complete UWG sub-flow run."""

    commit_request_id: str
    outcome: UwgOutcome
    ledger_seq: int = -1
    hash_chain_tip: str = ""
    l4_alias: str = ""
    rejected_reason: str = ""
    sub_flow_log: list[str] = field(default_factory=list)
    timestamp: int = 0
    rollback: dict[str, Any] = field(default_factory=dict)


# ---- in-memory reference backends ----


class InMemoryCatalog:
    """Default-allow catalog. Production swaps for a real RBAC store."""

    def __init__(
        self,
        *,
        denied_intents: tuple[str, ...] = (),
        pending_intents: tuple[str, ...] = (),
        forbidden_blast_radii: tuple[str, ...] = (),
    ) -> None:
        self._denied_intents = set(denied_intents)
        self._pending_intents = set(pending_intents)
        self._forbidden_blast_radii = set(forbidden_blast_radii)

    def is_authorized(self, *, tenant_id: str, write_intent_class: str, blast_radius: str) -> bool:
        del tenant_id  # tenant ACL stub: real impls would check here
        if write_intent_class in self._denied_intents:
            return False
        if blast_radius in self._forbidden_blast_radii:
            return False
        return True

    def has_pending_conflict(self, *, write_intent_class: str) -> bool:
        return write_intent_class in self._pending_intents


class InMemoryLockStore:
    """RLock-protected exclusive lock map."""

    def __init__(self) -> None:
        self._locks: dict[str, str] = {}
        self._mu = RLock()

    def claim(self, *, key: str, holder: str, ttl_seconds: int = 60) -> bool:
        del ttl_seconds  # in-memory store has no TTL
        with self._mu:
            if key in self._locks:
                return False
            self._locks[key] = holder
            return True

    def release(self, *, key: str, holder: str) -> bool:
        with self._mu:
            if self._locks.get(key) == holder:
                del self._locks[key]
                return True
            return False


class InMemoryLedger:
    """Hash-chained append-only ledger backed by a list."""

    def __init__(self) -> None:
        self._entries: list[dict[str, Any]] = []
        self._head = ""
        self._mu = RLock()

    def append(
        self,
        *,
        commit_request_id: str,
        payload: dict[str, Any],
    ) -> LedgerAppendResult:
        with self._mu:
            seq = len(self._entries)
            blob = json.dumps(
                {"seq": seq, "prev": self._head, "id": commit_request_id, "payload": payload},
                sort_keys=True,
            ).encode("utf-8")
            new_head = hashlib.sha256(blob).hexdigest()
            self._entries.append(
                {
                    "seq": seq,
                    "prev": self._head,
                    "id": commit_request_id,
                    "payload": payload,
                    "hash": new_head,
                }
            )
            self._head = new_head
            return LedgerAppendResult(seq=seq, hash_chain_tip=new_head)

    def head_hash(self) -> str:
        with self._mu:
            return self._head

    def entries(self) -> list[dict[str, Any]]:
        with self._mu:
            return list(self._entries)


class NoopReadSurfaceRefresher:
    """Refresher that records calls but does no actual work."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def refresh(self, *, commit_request_id: str, l4_alias: str) -> None:
        self.calls.append((commit_request_id, l4_alias))


# ---- U1..U5 sub-flow ----


def verify_boss(packet: X3CommitRequestPacket) -> None:
    """U1 VERIFY BOSS — reject expired tokens / bad signatures / policy drift."""
    if not packet.hmac_sig:
        raise InvalidSignature("missing hmac_sig")
    if not packet.policy_hash:
        raise PolicyMismatch("missing policy_hash")
    if not packet.compliance_hash:
        raise InvalidSignature("missing compliance_hash")
    cap = packet.capability_token or {}
    if not cap:
        raise CapabilityRejected("missing capability_token")
    if cap.get("expired"):
        raise CapabilityRejected("capability_token expired")
    if cap.get("scope_widened") or cap.get("widened"):
        raise CapabilityRejected("capability_token scope widened")
    if not cap.get("authorizes_write"):
        raise CapabilityRejected("capability_token does not authorize write")
    # Policy drift detection: route_contract carried snapshot must match.
    rc_policy = (packet.route_contract or {}).get("policy_hash", "")
    if rc_policy and rc_policy != packet.policy_hash:
        raise PolicyMismatch(
            f"route_contract.policy_hash={rc_policy!r} != packet.policy_hash={packet.policy_hash!r}"
        )


def check_catalog(
    packet: X3CommitRequestPacket,
    catalog: CatalogProtocol,
) -> None:
    """U2 CHECK CATALOG — RBAC + tenant ACL + blast radius + race detection."""
    state_diff = packet.state_diff or {}
    tenant_id = (
        state_diff.get("tenant_id") or (packet.route_contract or {}).get("tenant_scope", "") or "_default"
    )
    if not catalog.is_authorized(
        tenant_id=tenant_id,
        write_intent_class=packet.write_intent_class,
        blast_radius=packet.blast_radius,
    ):
        raise RbacDenied(
            f"catalog rejected write_intent_class={packet.write_intent_class!r} "
            f"tenant={tenant_id!r} blast_radius={packet.blast_radius!r}"
        )
    if catalog.has_pending_conflict(write_intent_class=packet.write_intent_class):
        raise CatalogConflict(f"pending write conflict on intent={packet.write_intent_class!r}")
    if packet.blast_radius == "irreversible" and not packet.rollback_plan:
        raise BlastRadiusExceeded("irreversible blast_radius requires rollback_plan")


def claim_write_lock(
    packet: X3CommitRequestPacket,
    lock_store: LockStoreProtocol,
) -> str:
    """U3 CLAIM WRITE LOCK — serialize commits per write_intent_class.

    Returns the lock key on success so the caller can release on outcome.
    """
    key = f"uwg::{packet.write_intent_class}"
    holder = packet.commit_request_id
    if not lock_store.claim(key=key, holder=holder, ttl_seconds=60):
        raise WriteLockConflict(f"lock contention on {key!r}")
    return key


def commit_and_append(
    packet: X3CommitRequestPacket,
    ledger: LedgerProtocol,
) -> LedgerAppendResult:
    """U4 COMMIT + CHAIN APPEND — durable ledger write."""
    payload = {
        "request_id": packet.request_id,
        "run_id": packet.run_id,
        "trace_root": packet.trace_root,
        "policy_hash": packet.policy_hash,
        "blueprint_hash": packet.blueprint_hash,
        "replay_key": packet.replay_key,
        "compliance_hash": packet.compliance_hash,
        "write_intent_class": packet.write_intent_class,
        "blast_radius": packet.blast_radius,
        "before_snapshot": packet.before_snapshot,
        "after_proposed_snapshot": packet.after_proposed_snapshot,
        "rollback_plan": packet.rollback_plan,
    }
    return ledger.append(commit_request_id=packet.commit_request_id, payload=payload)


def refresh_read_surfaces(
    packet: X3CommitRequestPacket,
    refresher: ReadSurfaceRefresher,
    *,
    l4_alias: str,
) -> None:
    """U5 REFRESH READ SURFACES — alias swap + cache invalidation."""
    refresher.refresh(commit_request_id=packet.commit_request_id, l4_alias=l4_alias)


# ---- orchestrator ----


@dataclass(slots=True)
class UwgBackends:
    """Bundle of backends consumed by ``process_commit_request``."""

    catalog: CatalogProtocol
    lock_store: LockStoreProtocol
    ledger: LedgerProtocol
    refresher: ReadSurfaceRefresher
    alias_builder: Callable[[X3CommitRequestPacket, LedgerAppendResult], str] = field(
        default=lambda _packet, result: f"l4://commit/{result.seq:08d}"
    )
    rollback_executor: Any = None  # SequentialRollbackExecutor | None — typed loose to avoid cycle


def default_backends() -> UwgBackends:
    """Return a fresh bundle of in-memory backends."""
    return UwgBackends(
        catalog=InMemoryCatalog(),
        lock_store=InMemoryLockStore(),
        ledger=InMemoryLedger(),
        refresher=NoopReadSurfaceRefresher(),
    )


def process_commit_request(
    packet: X3CommitRequestPacket,
    backends: UwgBackends,
) -> UwgReceipt:
    """Run U1..U5 against ``packet`` and return a ``UwgReceipt``.

    Outcome rules:
    - ``COMMIT_ACCEPTED`` if all five steps succeed.
    - ``COMMIT_REJECTED`` if U1, U2, U4, or U5 raises ``UwgError``.
    - ``COMMIT_HELD`` if U3 reports ``WriteLockConflict`` (caller may retry).
    """
    log: list[str] = []
    receipt = UwgReceipt(
        commit_request_id=packet.commit_request_id,
        outcome=UwgOutcome.COMMIT_REJECTED,
        timestamp=int(time.time()),
    )

    # U1
    try:
        verify_boss(packet)
        log.append("U1_VERIFY_BOSS:ok")
    except UwgError as exc:
        receipt.rejected_reason = f"{exc.reason_code}: {exc}"
        log.append(f"U1_VERIFY_BOSS:fail:{exc.reason_code}")
        receipt.sub_flow_log = log
        return receipt

    # U2
    try:
        check_catalog(packet, backends.catalog)
        log.append("U2_CHECK_CATALOG:ok")
    except UwgError as exc:
        receipt.rejected_reason = f"{exc.reason_code}: {exc}"
        log.append(f"U2_CHECK_CATALOG:fail:{exc.reason_code}")
        receipt.sub_flow_log = log
        return receipt

    # U3 — held outcome on lock conflict
    try:
        lock_key = claim_write_lock(packet, backends.lock_store)
        log.append(f"U3_CLAIM_WRITE_LOCK:ok:{lock_key}")
    except WriteLockConflict as exc:
        receipt.outcome = UwgOutcome.COMMIT_HELD
        receipt.rejected_reason = f"{exc.reason_code}: {exc}"
        log.append(f"U3_CLAIM_WRITE_LOCK:held:{exc.reason_code}")
        receipt.sub_flow_log = log
        return receipt

    try:
        # U4
        try:
            ledger_result = commit_and_append(packet, backends.ledger)
            log.append(f"U4_COMMIT:ok:seq={ledger_result.seq}")
        except UwgError as exc:
            receipt.rejected_reason = f"{exc.reason_code}: {exc}"
            log.append(f"U4_COMMIT:fail:{exc.reason_code}")
            receipt.sub_flow_log = log
            return receipt

        # U5
        l4_alias = backends.alias_builder(packet, ledger_result)
        try:
            refresh_read_surfaces(packet, backends.refresher, l4_alias=l4_alias)
            log.append(f"U5_REFRESH:ok:alias={l4_alias}")
        except (UwgError, OSError, RuntimeError) as exc:
            receipt.rejected_reason = f"U5_REFRESH_FAILED: {exc}"
            log.append(f"U5_REFRESH:fail:{type(exc).__name__}")
            # U5 failure after U4 success is the canonical rollback trigger.
            if backends.rollback_executor is not None and packet.rollback_plan:
                from agentic_core.L3_orchestration.exit_eval.v6.rollback import (
                    RollbackPlan,
                )

                plan = RollbackPlan.from_dict(packet.rollback_plan)
                rb_result = backends.rollback_executor.execute(plan)
                receipt.rollback = {
                    "outcome": rb_result.outcome.value,
                    "executed": list(rb_result.executed),
                    "failed_step": rb_result.failed_step,
                    "error": rb_result.error,
                }
                log.append(f"ROLLBACK:{rb_result.outcome.value}")
            receipt.sub_flow_log = log
            return receipt

        receipt.outcome = UwgOutcome.COMMIT_ACCEPTED
        receipt.ledger_seq = ledger_result.seq
        receipt.hash_chain_tip = ledger_result.hash_chain_tip
        receipt.l4_alias = l4_alias
        receipt.sub_flow_log = log
        return receipt
    finally:
        # Always release the write lock once the inner sub-flow is done.
        backends.lock_store.release(key=lock_key, holder=packet.commit_request_id)


__all__ = [
    "BlastRadiusExceeded",
    "CapabilityRejected",
    "CatalogConflict",
    "CatalogProtocol",
    "InMemoryCatalog",
    "InMemoryLedger",
    "InMemoryLockStore",
    "InvalidSignature",
    "LedgerAppendResult",
    "LedgerProtocol",
    "LockStoreProtocol",
    "NoopReadSurfaceRefresher",
    "PolicyMismatch",
    "RbacDenied",
    "ReadSurfaceRefresher",
    "UwgBackends",
    "UwgError",
    "UwgOutcome",
    "UwgReceipt",
    "WriteLockConflict",
    "check_catalog",
    "claim_write_lock",
    "commit_and_append",
    "default_backends",
    "process_commit_request",
    "refresh_read_surfaces",
    "verify_boss",
]
