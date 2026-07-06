"""DurableWriteGateway — the only mutation authority for L4 (00.6).

Implements the UWG admission pipeline mandated by
``docs/reference/00_L4_State_and_UWG/00.6_UWG_Durable_Write_Gateway_detailed.md``:

1. Receive CommitRequest (Exit-only)
2. Verify authority and source
3. Validate StateDiff
4. Validate replay/audit
5. Acquire write lock
6. Apply atomic commit
7. Trigger refresh + audit append

Anti-bypass posture (00.8 §PHASE 3): every direct-write attempt from a
non-UWG surface is recorded as a blocked attempt with a receipt and an
``l4.direct_write_attempt.blocked`` span.
"""

from __future__ import annotations

import threading
import uuid
from dataclasses import replace
from typing import Dict, Iterable, List, Optional, Tuple

from agentic_core.L4_state.audit.audit_ledger import (
    AuditAppendReceipt,
    AuditLedger,
    AuditLedgerUnavailableError,
    get_default_ledger,
)
from agentic_core.L4_state.contracts.records import (
    CommitRequest,
    ReadSurfaceRefreshPlan,
    RollbackPlan,
    StateDiff,
    UWGBlockedCommitReceipt,
    UWGCommitReceipt,
    UWGRollbackReceipt,
    UWGValidationReceipt,
    WriteLockReceipt,
    stamp_digest,
    record_canonical_payload,
)
from agentic_core.L4_state.contracts.digests import compute_deterministic_digest
from agentic_core.L4_state.otel.spans import emit_uwg_span
from agentic_core.L4_state.refresh.refresh_coordinator import RefreshCoordinator


# Allowed StateDiff operation types per 00.6 §PHASE 3.
ALLOWED_OPERATIONS: Tuple[str, ...] = (
    "append_record",
    "version_insert",
    "alias_swap",
    "cache_invalidate",
    "index_refresh",
    "graph_projection_refresh",
    "registry_update",
    "policy_version_publish",
    "memory_promotion",
    "rollback",
    "tombstone",
    # Fort Knox app-domain contract registration (plan apps-domain-contract-fortknox-c4d8e2).
    # The registration adapter at agentic_core/L4_state/uwg/app_domain_registration.py
    # submits one StateDiff per app-domain record kind. Source surface remains "Exit"
    # per the UWG Exit-only authority rule.
    "app_domain_contract_register",
)

PLACEHOLDER_HASHES: frozenset[str] = frozenset({"", "unknown", "UNKNOWN", "MIGRATION_UNKNOWN"})


def compute_state_diffs_digest(state_diffs: Iterable[StateDiff]) -> str:
    payload = {
        "state_diffs": [
            record_canonical_payload(sd)
            for sd in sorted(state_diffs, key=lambda row: row.state_diff_id)
        ]
    }
    return compute_deterministic_digest(payload)


# Surfaces NOT allowed to issue CommitRequest directly. Only Exit may.
NON_AUTHORIZED_SOURCES: frozenset[str] = frozenset(
    {
        "L0",
        "L1",
        "L2",
        "L3",
        "L5",
        "L6",
        "C0",
        "PromptAssembly",
        "HITL",
        "Tool",
        "Model",
        "Connector",
        "PTC_Sandbox",
        "BackgroundEvaluator",
        "AdHocScript",
    }
)


class UWGAuthorityError(RuntimeError):
    """Raised when a non-UWG surface attempts to bypass the gateway."""


class UWGContentionError(RuntimeError):
    """Raised when write-lock contention is detected without retry policy."""


class _WriteLockManager:
    """Per-target write lock manager with contention detection."""

    def __init__(self) -> None:
        self._locks: Dict[str, threading.RLock] = {}
        self._holders: Dict[str, str] = {}
        self._lock = threading.Lock()

    def acquire(
        self, *, target_surfaces: Iterable[str], owner: str, timeout: float = 0.0
    ) -> Tuple[bool, List[str]]:
        """Try to acquire all target surface locks. Return (acquired, contentions)."""
        contentions: List[str] = []
        with self._lock:
            for surface in target_surfaces:
                rl = self._locks.setdefault(surface, threading.RLock())
                if not rl.acquire(blocking=False):
                    contentions.append(surface)
            if contentions:
                # Roll back partial acquisitions
                for surface in target_surfaces:
                    if surface not in contentions:
                        try:
                            self._locks[surface].release()
                        except RuntimeError:  # guardian: allow-silent-swallow -- lock release on rollback: lock may already be released; RuntimeError is normal here  # noqa: PERF203
                            pass
                return (False, contentions)
            for surface in target_surfaces:
                self._holders[surface] = owner
            return (True, [])

    def release(self, *, target_surfaces: Iterable[str], owner: str) -> None:
        with self._lock:
            for surface in target_surfaces:
                if self._holders.get(surface) == owner:
                    try:
                        self._locks[surface].release()
                        self._holders.pop(surface, None)
                    except (RuntimeError, KeyError):  # guardian: allow-silent-swallow -- lock release: lock already released or key gone; both are benign during concurrent release
                        pass


class DurableWriteGateway:
    """Admission gateway for durable L4 mutations.

    Construct one per process (or use :func:`get_default_gateway`).
    Submit :class:`CommitRequest` instances and receive either a
    :class:`UWGCommitReceipt` or a :class:`UWGBlockedCommitReceipt` plus
    refresh receipts.
    """

    def __init__(
        self,
        *,
        audit_ledger: Optional[AuditLedger] = None,
        refresh_coordinator: Optional[RefreshCoordinator] = None,
    ) -> None:
        self._audit = audit_ledger or get_default_ledger()
        self._refresh = refresh_coordinator or RefreshCoordinator(audit_ledger=self._audit)
        self._lock_mgr = _WriteLockManager()
        self._snapshot_counter: int = 0
        self._snapshot_lock = threading.Lock()
        self._validations: Dict[str, UWGValidationReceipt] = {}
        self._commits: Dict[str, UWGCommitReceipt] = {}
        self._blocked: Dict[str, UWGBlockedCommitReceipt] = {}
        self._rollbacks: Dict[str, UWGRollbackReceipt] = {}
        self._last_snapshot_id: str = "snapshot:bootstrap"
        self._direct_write_blocks: List[UWGBlockedCommitReceipt] = []

    # ------------------------------------------------------------------
    @property
    def refresh_coordinator(self) -> RefreshCoordinator:
        return self._refresh

    @property
    def audit_ledger(self) -> AuditLedger:
        return self._audit

    @property
    def last_snapshot_id(self) -> str:
        return self._last_snapshot_id

    def get_commit_receipt(self, commit_receipt_id: str) -> Optional[UWGCommitReceipt]:
        return self._commits.get(commit_receipt_id)

    def get_validation_receipt(self, validation_receipt_id: str) -> Optional[UWGValidationReceipt]:
        return self._validations.get(validation_receipt_id)

    def get_blocked_receipt(self, blocked_id: str) -> Optional[UWGBlockedCommitReceipt]:
        return self._blocked.get(blocked_id)

    def list_direct_write_blocks(self) -> List[UWGBlockedCommitReceipt]:
        return list(self._direct_write_blocks)

    # ------------------------------------------------------------------
    def reject_direct_write(
        self,
        *,
        attempting_surface: str,
        target_surface: str,
        reason: str,
        request_id: Optional[str] = None,
        run_id: Optional[str] = None,
    ) -> UWGBlockedCommitReceipt:
        """Record a direct-write bypass attempt and return the block receipt.

        Per 00.8 §PHASE 3: every direct-write path from L2/L6/HITL/Exit (as
        a writer)/L5/C0/PromptAssembly/PTC/Tool/Model/Connector/Background/
        AdHocScript must produce a blocked receipt and an audit record.
        """
        snapshot_before = self._allocate_snapshot()

        record, append_receipt = self._audit.append(
            event_type="direct_write_attempt_blocked",
            state_surface=target_surface,
            operation_type="blocked_direct_write",
            tenant_id="-",
            policy_hash="-",
            blueprint_hash="-",
            snapshot_before=snapshot_before,
            actor_surface=attempting_surface,
            mutation_source=attempting_surface,
            reason_codes=(reason,),
            request_id=request_id,
            run_id=run_id,
        )
        receipt = UWGBlockedCommitReceipt(
            blocked_commit_receipt_id=str(uuid.uuid4()),
            commit_request_ref=f"NO_COMMIT_REQUEST::direct_attempt_by::{attempting_surface}",
            snapshot_before=snapshot_before,
            audit_append_receipt_ref=append_receipt.audit_append_receipt_id,
            blocked_reason_codes=(reason, "non_uwg_surface_blocked"),
            failed_rule_ids=("UWG_AUTHORITY_REQUIRED",),
            state_surfaces_requested=(target_surface,),
        )
        receipt = stamp_digest(receipt)
        self._blocked[receipt.blocked_commit_receipt_id] = receipt
        self._direct_write_blocks.append(receipt)

        emit_uwg_span(
            "l4.direct_write_attempt.blocked",
            operation_type="blocked_direct_write",
            source_surface=attempting_surface,
            mutation_source=attempting_surface,
            state_surface=target_surface,
            blocked_commit_receipt_id=receipt.blocked_commit_receipt_id,
            status="BLOCKED",
            reason_codes=(reason,),
            extra={"audit_record_id": record.audit_record_id},
        )
        return receipt

    # ------------------------------------------------------------------
    def commit(
        self,
        *,
        commit_request: CommitRequest,
        state_diffs: List[StateDiff],
        rollback_plan: RollbackPlan,
        refresh_plan: ReadSurfaceRefreshPlan,
    ) -> Tuple[Optional[UWGCommitReceipt], Optional[UWGBlockedCommitReceipt], List]:
        """Run the full UWG pipeline.

        Returns ``(commit_receipt, blocked_receipt, refresh_receipts)``.
        Exactly one of ``commit_receipt`` / ``blocked_receipt`` is non-None.

        W5.7 (closed-loop-router-fleet-rollout-d8f2a3 NEXT_STEP): every
        commit/blocked verdict is durably recorded to router_l4_uwg ledger
        with stage attribution (validation / lock_contention / happy-path).
        Fail-soft.
        """
        import time as _time  # noqa: PLC0415

        _t_start = _time.time()
        emit_uwg_span(
            "uwg.commit.request_received",
            policy_hash=commit_request.policy_hash,
            blueprint_hash=commit_request.blueprint_hash,
            replay_key=commit_request.replay_key,
            tenant_id=commit_request.tenant_id,
            source_surface=commit_request.source_surface,
            commit_request_id=commit_request.commit_request_id,
            extra={"state_diff_count": len(state_diffs)},
        )
        # 00.5 §PHASE 3 mandates ``commit_request_received`` as a durable
        # audit event, distinct from the in-flight span. We append it
        # before validation runs so the receive-time fact is durable even
        # if validation later fails closed.
        if self._audit.is_available():
            self._audit.append(
                event_type="commit_request_received",
                state_surface=",".join(commit_request.affected_state_surfaces) or "-",
                operation_type="commit_request",
                tenant_id=commit_request.tenant_id,
                policy_hash=commit_request.policy_hash or "-",
                blueprint_hash=commit_request.blueprint_hash or "-",
                snapshot_before=self._last_snapshot_id,
                actor_surface=commit_request.source_surface,
                mutation_source=commit_request.source_surface,
                request_id=commit_request.request_id,
                run_id=commit_request.run_id,
                trace_root=commit_request.trace_root,
                receipt_refs=(commit_request.commit_request_id,),
                state_refs=tuple(sd_ref for sd_ref in commit_request.state_diff_refs),
            )

        # Stage 1+2: authority and source
        validation = self._validate(commit_request, state_diffs, rollback_plan, refresh_plan)
        if validation.validation_status == "FAIL":
            blocked = self._emit_blocked(commit_request, validation)
            _record_uwg_decision(
                commit_request=commit_request,
                state_diffs=state_diffs,
                validation_status=validation.validation_status,
                block_stage="validation",
                commit_receipt=None,
                blocked_receipt=blocked,
                refresh_receipts=[],
                latency_ms=int((_time.time() - _t_start) * 1000.0),
                snapshot_after=None,
            )
            return (None, blocked, [])

        # Stage 5: write lock
        target_surfaces = tuple(commit_request.affected_state_surfaces) or tuple(
            sd.target_surface for sd in state_diffs
        )
        lock_owner = f"UWG::{commit_request.commit_request_id}"
        snapshot_before = self._allocate_snapshot()
        write_lock_receipt = self._acquire_lock(
            commit_request=commit_request,
            target_surfaces=target_surfaces,
            owner=lock_owner,
            snapshot_before=snapshot_before,
        )
        if write_lock_receipt.lock_status != "ACQUIRED":
            blocked = self._emit_blocked(
                commit_request,
                replace(
                    validation,
                    write_lock_status="CONTENTION",
                    failed_rules=tuple(validation.failed_rules) + ("write_lock_contention",),
                    reason_codes=tuple(validation.reason_codes) + ("write_lock_contention",),
                ),
            )
            _record_uwg_decision(
                commit_request=commit_request,
                state_diffs=state_diffs,
                validation_status=validation.validation_status,
                block_stage="lock_contention",
                commit_receipt=None,
                blocked_receipt=blocked,
                refresh_receipts=[],
                latency_ms=int((_time.time() - _t_start) * 1000.0),
                snapshot_after=None,
            )
            return (None, blocked, [])

        try:
            # Stage 6: atomic commit
            snapshot_after = self._allocate_snapshot()
            audit_append_record, audit_append_receipt = self._audit.append(
                event_type="atomic_commit_applied",
                state_surface=",".join(target_surfaces) if target_surfaces else "-",
                operation_type="commit",
                tenant_id=commit_request.tenant_id,
                policy_hash=commit_request.policy_hash,
                blueprint_hash=commit_request.blueprint_hash,
                snapshot_before=snapshot_before,
                snapshot_after=snapshot_after,
                actor_surface="UWG",
                mutation_source="UWG",
                request_id=commit_request.request_id,
                run_id=commit_request.run_id,
                trace_root=commit_request.trace_root,
                receipt_refs=(write_lock_receipt.write_lock_receipt_id,),
                state_refs=tuple(sd.state_diff_id for sd in state_diffs),
            )

            commit_receipt = UWGCommitReceipt(
                commit_receipt_id=str(uuid.uuid4()),
                commit_request_ref=commit_request.commit_request_id,
                write_lock_receipt_ref=write_lock_receipt.write_lock_receipt_id,
                uwg_validation_receipt_ref=validation.uwg_validation_receipt_id,
                snapshot_before=snapshot_before,
                snapshot_after=snapshot_after,
                read_surface_refresh_plan_ref=refresh_plan.refresh_plan_id,
                audit_append_receipt_ref=audit_append_receipt.audit_append_receipt_id,
                committed_at=str(audit_append_receipt.ledger_sequence),
                state_diff_refs=tuple(sd.state_diff_id for sd in state_diffs),
                affected_state_surfaces=target_surfaces,
                audit_refs=tuple(commit_request.audit_refs),
                l5_certification_ref=commit_request.l5_certification_ref,
                source_surface=commit_request.source_surface,
                policy_hash=commit_request.policy_hash,
                blueprint_hash=commit_request.blueprint_hash,
                replay_key=commit_request.replay_key,
                gate_verdict_refs=tuple(commit_request.gate_verdict_refs),
                cleared_exit_review_packet_ref=commit_request.cleared_exit_review_packet_ref,
                registry_digest_set=tuple(commit_request.registry_digest_set),
                clearance_proof_id=commit_request.clearance_proof_id,
                staged_diff_hash=commit_request.staged_diff_hash,
                content_hash=compute_deterministic_digest(
                    {
                        "commit_request_id": commit_request.commit_request_id,
                        "state_diff_refs": [sd.state_diff_id for sd in state_diffs],
                        "snapshot_before": snapshot_before,
                        "snapshot_after": snapshot_after,
                        "audit_append_receipt_ref": audit_append_receipt.audit_append_receipt_id,
                        "audit_chain_hash": audit_append_receipt.chain_hash,
                    }
                ),
                prev_chain_hash=audit_append_receipt.prev_chain_hash,
                chain_hash=audit_append_receipt.chain_hash,
                validator_receipt_id=(
                    commit_request.validator_receipt_id
                    or validation.uwg_validation_receipt_id
                ),
            )
            commit_receipt = stamp_digest(commit_receipt)
            self._commits[commit_receipt.commit_receipt_id] = commit_receipt
            self._last_snapshot_id = snapshot_after

            emit_uwg_span(
                "uwg.commit.apply",
                policy_hash=commit_request.policy_hash,
                blueprint_hash=commit_request.blueprint_hash,
                replay_key=commit_request.replay_key,
                tenant_id=commit_request.tenant_id,
                source_surface="UWG",
                mutation_source="UWG",
                commit_request_id=commit_request.commit_request_id,
                commit_receipt_id=commit_receipt.commit_receipt_id,
                snapshot_id=snapshot_after,
                extra={"audit_record_id": audit_append_record.audit_record_id},
            )
            emit_uwg_span(
                "uwg.commit.receipt_emit",
                policy_hash=commit_request.policy_hash,
                replay_key=commit_request.replay_key,
                tenant_id=commit_request.tenant_id,
                source_surface="UWG",
                commit_request_id=commit_request.commit_request_id,
                commit_receipt_id=commit_receipt.commit_receipt_id,
                snapshot_id=snapshot_after,
            )

            # Stage 7: refresh — rebind plan to point at the freshly-emitted commit receipt
            bound_plan = replace(
                refresh_plan,
                source_commit_receipt_ref=commit_receipt.commit_receipt_id,
                deterministic_digest="",
            )
            bound_plan = stamp_digest(bound_plan)
            refresh_receipts = self._refresh.execute(plan=bound_plan, commit_receipt=commit_receipt)
            _record_uwg_decision(
                commit_request=commit_request,
                state_diffs=state_diffs,
                validation_status=validation.validation_status,
                block_stage="",
                commit_receipt=commit_receipt,
                blocked_receipt=None,
                refresh_receipts=refresh_receipts,
                latency_ms=int((_time.time() - _t_start) * 1000.0),
                snapshot_after=snapshot_after,
            )
            return (commit_receipt, None, refresh_receipts)
        finally:
            self._lock_mgr.release(target_surfaces=target_surfaces, owner=lock_owner)

    # ------------------------------------------------------------------
    def rollback(
        self,
        *,
        rollback_plan: RollbackPlan,
        source_commit_receipt: UWGCommitReceipt,
        reason_codes: Tuple[str, ...] = (),
    ) -> UWGRollbackReceipt:
        """Apply a rollback per 00.6 §PHASE 7."""
        if not source_commit_receipt.snapshot_before:
            raise ValueError("rollback requires source commit's snapshot_before")
        snapshot_before_rollback = source_commit_receipt.snapshot_after
        snapshot_after_rollback = self._allocate_snapshot()

        _record, append_receipt = self._audit.append(
            event_type="rollback_applied",
            state_surface=",".join(rollback_plan.target_surfaces),
            operation_type="rollback",
            tenant_id="-",
            policy_hash="-",
            blueprint_hash="-",
            snapshot_before=snapshot_before_rollback,
            snapshot_after=snapshot_after_rollback,
            actor_surface="UWG",
            mutation_source="UWG",
            receipt_refs=(source_commit_receipt.commit_receipt_id,),
            reason_codes=reason_codes,
        )
        receipt = UWGRollbackReceipt(
            rollback_receipt_id=str(uuid.uuid4()),
            rollback_plan_ref=rollback_plan.rollback_plan_id,
            source_commit_receipt_ref=source_commit_receipt.commit_receipt_id,
            snapshot_before_rollback=snapshot_before_rollback,
            snapshot_after_rollback=snapshot_after_rollback,
            audit_append_receipt_ref=append_receipt.audit_append_receipt_id,
            affected_state_surfaces=rollback_plan.target_surfaces,
            reason_codes=reason_codes,
        )
        receipt = stamp_digest(receipt)
        self._rollbacks[receipt.rollback_receipt_id] = receipt
        self._last_snapshot_id = snapshot_after_rollback

        emit_uwg_span(
            "uwg.rollback.apply",
            replay_key=source_commit_receipt.commit_receipt_id,
            policy_hash="-",
            source_surface="UWG",
            commit_receipt_id=source_commit_receipt.commit_receipt_id,
            snapshot_id=snapshot_after_rollback,
            reason_codes=reason_codes,
        )
        return receipt

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _validate(
        self,
        commit_request: CommitRequest,
        state_diffs: List[StateDiff],
        rollback_plan: RollbackPlan,
        refresh_plan: ReadSurfaceRefreshPlan,
    ) -> UWGValidationReceipt:
        checked: List[str] = []
        failed: List[str] = []
        reason_codes: List[str] = []

        # 00.6 §PHASE 2 step 1
        checked.append("source_is_exit")
        if commit_request.source_surface != "Exit":
            failed.append("source_is_exit")
            reason_codes.append("non_exit_source")
        if commit_request.source_surface in NON_AUTHORIZED_SOURCES:
            failed.append("non_authorized_source")
            reason_codes.append(f"non_authorized:{commit_request.source_surface}")

        # 00.6 §PHASE 2 step 1: required fields
        # progress: fixed-size 7-element validation tuple, no UI bar needed
        for fld in (
            "policy_hash",
            "blueprint_hash",
            "replay_key",
            "tenant_id",
            "request_id",
            "run_id",
            "trace_root",
        ):
            checked.append(f"required_field::{fld}")
            if not getattr(commit_request, fld):
                failed.append(f"required_field::{fld}")
                reason_codes.append(f"missing::{fld}")

        checked.append("policy_hash_not_placeholder")
        if str(commit_request.policy_hash or "").strip() in PLACEHOLDER_HASHES:
            failed.append("policy_hash_not_placeholder")
            reason_codes.append("missing_or_placeholder_policy_hash")

        checked.append("blueprint_hash_not_placeholder")
        if str(commit_request.blueprint_hash or "").strip() in PLACEHOLDER_HASHES:
            failed.append("blueprint_hash_not_placeholder")
            reason_codes.append("missing_or_placeholder_blueprint_hash")

        # 00.6 §PHASE 2 step 2: gate / cert refs
        checked.append("gate_verdict_refs")
        if not commit_request.gate_verdict_refs:
            failed.append("gate_verdict_refs")
            reason_codes.append("missing_gate_verdict_refs")

        checked.append("l5_certification_ref")
        from agentic_core.L5_safety.contracts.verify import verify_certification_ref

        if not verify_certification_ref(commit_request.l5_certification_ref):
            failed.append("l5_certification_ref")
            reason_codes.append("l5_certification_invalid")

        checked.append("clearance_proof_id")
        if not str(commit_request.clearance_proof_id or "").strip():
            failed.append("clearance_proof_id")
            reason_codes.append("missing_clearance_proof_id")

        checked.append("registry_digest_set")
        if commit_request.expected_read_surface_refreshes and not commit_request.registry_digest_set:
            failed.append("registry_digest_set")
            reason_codes.append("missing_registry_digest_set")

        checked.append("commit_request_signature")
        if not (
            str(commit_request.commit_request_signature or "").strip()
            or str(commit_request.signature or "").strip()
        ):
            failed.append("commit_request_signature")
            reason_codes.append("commit_request_signature_invalid")

        supplied_state_diff_ids = tuple(sd.state_diff_id for sd in state_diffs)
        checked.append("state_diff_refs_match")
        if tuple(commit_request.state_diff_refs) != supplied_state_diff_ids:
            failed.append("state_diff_refs_match")
            reason_codes.append("state_diff_refs_mismatch")

        checked.append("staged_diff_hash")
        actual_diff_hash = compute_state_diffs_digest(state_diffs)
        if not commit_request.staged_diff_hash:
            failed.append("staged_diff_hash")
            reason_codes.append("missing_staged_diff_hash")
        elif commit_request.staged_diff_hash != actual_diff_hash:
            failed.append("staged_diff_hash")
            reason_codes.append("state_diff_hash_mismatch")

        # 00.6 §PHASE 2 step 3: state diffs
        # progress: bounded by len(state_diffs) — usually 1-3 per CommitRequest, no UI bar needed
        for sd in state_diffs:
            label = f"state_diff::{sd.state_diff_id}"
            checked.append(label)
            if sd.operation_type not in ALLOWED_OPERATIONS:
                failed.append(label)
                reason_codes.append(f"unknown_operation::{sd.operation_type}")
            if not sd.target_surface:
                failed.append(label)
                reason_codes.append(f"missing_target_surface::{sd.state_diff_id}")
            if not sd.rollback_plan_ref:
                failed.append(label)
                reason_codes.append(f"missing_rollback_plan_ref::{sd.state_diff_id}")
            if not sd.schema_ref:
                failed.append(label)
                reason_codes.append(f"missing_schema_ref::{sd.state_diff_id}")
            if commit_request.affected_state_surfaces and sd.target_surface not in commit_request.affected_state_surfaces:
                failed.append(label)
                reason_codes.append("target_surface_not_allowlisted")

        # 00.6 §PHASE 2 step 4: replay/audit
        checked.append("replay_key_present")
        if not commit_request.replay_key:
            failed.append("replay_key_present")
            reason_codes.append("missing::replay_key")
        checked.append("audit_ledger_available")
        if not self._audit.is_available():
            failed.append("audit_ledger_available")
            reason_codes.append("audit_ledger_unavailable")

        # Rollback plan
        checked.append("rollback_plan_present")
        if rollback_plan.rollback_plan_id != commit_request.rollback_plan_ref:
            failed.append("rollback_plan_present")
            reason_codes.append("rollback_plan_id_mismatch")

        # Refresh plan
        checked.append("refresh_plan_present")
        if not refresh_plan.refresh_plan_id:
            failed.append("refresh_plan_present")
            reason_codes.append("missing::refresh_plan_id")

        # Blast radius bound
        checked.append("blast_radius_bounded")
        allowed_blast = {
            "single_surface",
            "tenant_scoped",
            "route_scoped",
            "policy_scoped",
            "registry_scoped",
        }
        if commit_request.blast_radius not in allowed_blast:
            failed.append("blast_radius_bounded")
            reason_codes.append(f"blast_radius_unbounded::{commit_request.blast_radius}")

        validation = UWGValidationReceipt(
            uwg_validation_receipt_id=str(uuid.uuid4()),
            commit_request_ref=commit_request.commit_request_id,
            validation_status="FAIL" if failed else "PASS",
            policy_status="PASS" if commit_request.policy_hash else "FAIL",
            blueprint_status="PASS" if commit_request.blueprint_hash else "FAIL",
            schema_status="PASS" if all(sd.schema_ref for sd in state_diffs) else "FAIL",
            gate_status="PASS" if commit_request.gate_verdict_refs else "FAIL",
            l5_cert_status=(
                "PASS"
                if "l5_certification_ref" not in failed
                else "FAIL"
            ),
            hitl_status="PASS",  # only checked when explicitly required by route
            replay_status="PASS" if commit_request.replay_key else "FAIL",
            rollback_status="PASS" if commit_request.rollback_plan_ref else "FAIL",
            blast_radius_status="PASS" if commit_request.blast_radius in allowed_blast else "FAIL",
            write_lock_status="PENDING",
            checked_rules=tuple(checked),
            failed_rules=tuple(failed),
            reason_codes=tuple(reason_codes),
        )
        validation = stamp_digest(validation)
        self._validations[validation.uwg_validation_receipt_id] = validation
        emit_uwg_span(
            "uwg.commit.validate",
            policy_hash=commit_request.policy_hash,
            replay_key=commit_request.replay_key,
            tenant_id=commit_request.tenant_id,
            source_surface=commit_request.source_surface,
            commit_request_id=commit_request.commit_request_id,
            status=validation.validation_status,
            reason_codes=tuple(reason_codes),
        )
        return validation

    def _acquire_lock(
        self,
        *,
        commit_request: CommitRequest,
        target_surfaces: Tuple[str, ...],
        owner: str,
        snapshot_before: str,
    ) -> WriteLockReceipt:
        ok, contentions = self._lock_mgr.acquire(target_surfaces=target_surfaces, owner=owner)
        receipt = WriteLockReceipt(
            write_lock_receipt_id=str(uuid.uuid4()),
            commit_request_ref=commit_request.commit_request_id,
            lock_scope=",".join(target_surfaces) if target_surfaces else "-",
            lock_status="ACQUIRED" if ok else "CONTENTION",
            lock_owner=owner,
            policy_hash=commit_request.policy_hash,
            blueprint_hash=commit_request.blueprint_hash,
            snapshot_before=snapshot_before,
            target_surfaces=target_surfaces,
            contention_refs=tuple(contentions),
        )
        receipt = stamp_digest(receipt)
        emit_uwg_span(
            "uwg.write_lock.acquire",
            policy_hash=commit_request.policy_hash,
            replay_key=commit_request.replay_key,
            tenant_id=commit_request.tenant_id,
            source_surface="UWG",
            commit_request_id=commit_request.commit_request_id,
            status=receipt.lock_status,
            extra={"target_surfaces": list(target_surfaces)},
        )
        return receipt

    def _emit_blocked(
        self,
        commit_request: CommitRequest,
        validation: UWGValidationReceipt,
    ) -> UWGBlockedCommitReceipt:
        snapshot_before = self._allocate_snapshot()
        try:
            _record, append_receipt = self._audit.append(
                event_type="commit_blocked",
                state_surface=",".join(commit_request.affected_state_surfaces),
                operation_type="blocked_commit",
                tenant_id=commit_request.tenant_id,
                policy_hash=commit_request.policy_hash or "-",
                blueprint_hash=commit_request.blueprint_hash or "-",
                snapshot_before=snapshot_before,
                actor_surface="UWG",
                mutation_source=commit_request.source_surface,
                request_id=commit_request.request_id,
                run_id=commit_request.run_id,
                trace_root=commit_request.trace_root,
                receipt_refs=(validation.uwg_validation_receipt_id,),
                reason_codes=tuple(validation.reason_codes),
            )
            append_ref = append_receipt.audit_append_receipt_id
        except AuditLedgerUnavailableError:  # guardian: allow-default-fallback -- audit ledger unavailable is a documented degraded mode; receipt records AUDIT_UNAVAILABLE sentinel for post-hoc reconciliation
            append_ref = "AUDIT_UNAVAILABLE"

        receipt = UWGBlockedCommitReceipt(
            blocked_commit_receipt_id=str(uuid.uuid4()),
            commit_request_ref=commit_request.commit_request_id,
            snapshot_before=snapshot_before,
            audit_append_receipt_ref=append_ref,
            uwg_validation_receipt_ref=validation.uwg_validation_receipt_id,
            blocked_reason_codes=tuple(validation.reason_codes),
            failed_rule_ids=tuple(validation.failed_rules),
            state_surfaces_requested=tuple(commit_request.affected_state_surfaces),
        )
        receipt = stamp_digest(receipt)
        self._blocked[receipt.blocked_commit_receipt_id] = receipt
        emit_uwg_span(
            "uwg.commit.blocked",
            policy_hash=commit_request.policy_hash,
            replay_key=commit_request.replay_key,
            tenant_id=commit_request.tenant_id,
            source_surface=commit_request.source_surface,
            mutation_source=commit_request.source_surface,
            commit_request_id=commit_request.commit_request_id,
            blocked_commit_receipt_id=receipt.blocked_commit_receipt_id,
            status="BLOCKED",
            reason_codes=tuple(validation.reason_codes),
        )
        return receipt

    def _allocate_snapshot(self) -> str:
        with self._snapshot_lock:
            self._snapshot_counter += 1
            return f"snapshot:{self._snapshot_counter:08x}"


# Default singleton ----------------------------------------------------------

_DEFAULT_GATEWAY: Optional[DurableWriteGateway] = None
_DEFAULT_LOCK = threading.Lock()


def get_default_gateway() -> DurableWriteGateway:
    """Return the process-wide default gateway (lazy-initialized)."""
    global _DEFAULT_GATEWAY  # noqa: PLW0603
    with _DEFAULT_LOCK:
        if _DEFAULT_GATEWAY is None:
            _DEFAULT_GATEWAY = DurableWriteGateway()
        return _DEFAULT_GATEWAY


def reset_default_gateway() -> None:
    """Reset the default gateway (test hook)."""
    global _DEFAULT_GATEWAY  # noqa: PLW0603
    with _DEFAULT_LOCK:
        _DEFAULT_GATEWAY = DurableWriteGateway()


# =====================================================================
# Constitutional §29 — closed-loop wiring (W5.7)
# =====================================================================
import logging as _logging  # noqa: E402  -- module-bottom helpers

_UWG_LOGGER = _logging.getLogger(__name__)
_UWG_HELPER = None  # type: ignore[var-annotated]


def _get_uwg_helper():
    """Lazy singleton for the L4/uwg RouterClosedLoopHelper."""
    global _UWG_HELPER  # noqa: PLW0603
    if _UWG_HELPER is not None:
        return _UWG_HELPER
    try:
        from tools.ledgers.router_helper import RouterClosedLoopHelper  # noqa: PLC0415

        _UWG_HELPER = RouterClosedLoopHelper(
            layer="L4",
            router="uwg",
            ledger_name="router_l4_uwg",
            repo_area="agentic_core/L4_state/uwg/durable_write_gateway.py",
        )
        return _UWG_HELPER
    except ImportError:  # guardian: allow-log-and-swallow -- helper unavailable must not break UWG commit pipeline
        _UWG_LOGGER.debug("RouterClosedLoopHelper unavailable for L4/uwg", exc_info=True)
        return None


def _record_uwg_decision(
    *,
    commit_request: CommitRequest,
    state_diffs: List[StateDiff],
    validation_status: str,
    block_stage: str,
    commit_receipt: Optional[UWGCommitReceipt],
    blocked_receipt: Optional[UWGBlockedCommitReceipt],
    refresh_receipts: List,
    latency_ms: int,
    snapshot_after: Optional[str],
) -> None:
    """Record commit/blocked verdict + bind outcome in one shot.

    UWG's commit() returns synchronously after the full pipeline executes,
    so the outcome is known at decision-emission time. We use the
    decision-and-outcome-in-one-shot pattern (same shape as L0/agentic and
    L6/promo). Fail-soft: any helper failure is swallowed so the commit
    pipeline is never broken by telemetry.
    """
    helper = _get_uwg_helper()
    if helper is None:
        return
    try:
        success = commit_receipt is not None
        selected = "commit" if success else "blocked"
        target_surfaces = tuple(commit_request.affected_state_surfaces) or tuple(
            sd.target_surface for sd in state_diffs
        )
        # Heuristic prior: validation expected pass at request-receive time
        # since callers should pre-check; lower prior on a pre-failed request.
        predicted_p = 1.0 if validation_status == "PASS" else 0.5
        eu_score = 1.0 if success else 0.0

        handle = helper.record_decision(
            selected=selected,
            cell={
                "source_surface": str(commit_request.source_surface or "unknown"),
                "blast_radius": str(commit_request.blast_radius or "unknown"),
            },
            predicted_p_success=predicted_p,
            eu_score=eu_score,
            decision_id=str(commit_request.commit_request_id),
            prediction_extras={
                "validation_status": str(validation_status),
                "block_stage": str(block_stage),
                "n_state_diffs": int(len(state_diffs)),
                "n_target_surfaces": int(len(target_surfaces)),
                "tenant_id": str(commit_request.tenant_id or ""),
            },
        )
        helper.bind_outcome(
            handle,
            success=success,
            latency_ms=int(latency_ms),
            outcome_extras={
                "commit_receipt_id": (
                    commit_receipt.commit_receipt_id if commit_receipt else None
                ),
                "blocked_receipt_id": (
                    blocked_receipt.blocked_commit_receipt_id if blocked_receipt else None
                ),
                "n_refresh_receipts": int(len(refresh_receipts)),
                "snapshot_after": snapshot_after,
            },
        )
    except (AttributeError, TypeError, ValueError, RuntimeError):  # guardian: allow-log-and-swallow -- ledger emission is best-effort; UWG commit must never break
        _UWG_LOGGER.debug("durable_write_gateway ledger emit failed", exc_info=True)


__all__ = [
    "ALLOWED_OPERATIONS",
    "DurableWriteGateway",
    "NON_AUTHORIZED_SOURCES",
    "UWGAuthorityError",
    "UWGContentionError",
    "get_default_gateway",
    "compute_state_diffs_digest",
    "reset_default_gateway",
]
