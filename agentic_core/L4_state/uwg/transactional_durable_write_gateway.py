"""Transactional UWG implementation backed by the canonical L4 SQLite store."""

from __future__ import annotations

import threading
import time
from dataclasses import replace
from typing import Any, Mapping, Sequence

from agentic_core.L4_state.audit.sqlite_audit_ledger import SQLiteAuditLedger
from agentic_core.L4_state.contracts.records import (
    CommitRequest,
    ReadSurfaceRefreshPlan,
    ReadSurfaceRefreshReceipt,
    RollbackPlan,
    StateDiff,
    UWGBlockedCommitReceipt,
    UWGCommitReceipt,
    UWGValidationReceipt,
    stamp_digest,
)
from agentic_core.L4_state.otel.spans import emit_uwg_span
from agentic_core.L4_state.storage.sqlite_backend import (
    DurableLockContentionError,
    ProjectionTask,
    ReplayConflictError,
    SQLiteL4Backend,
    get_default_backend,
)
from agentic_core.L4_state.uwg.durable_write_gateway import DurableWriteGateway


class TransactionalDurableWriteGateway(DurableWriteGateway):
    """UWG whose accepted commit is one canonical SQLite transaction.

    The transaction includes immutable state versions, audit append, validation
    and commit receipts, durable surface-fencing tokens, and projection-outbox
    records. Derived read surfaces are not reported as refreshed until their
    outbox tasks pass read-after-write verification.
    """

    def __init__(
        self,
        *,
        canonical_backend: SQLiteL4Backend | None = None,
        refresh_coordinator: Any | None = None,
    ) -> None:
        backend = canonical_backend if canonical_backend is not None else get_default_backend()
        self._canonical_backend = backend
        audit = SQLiteAuditLedger(backend) if backend is not None else None
        super().__init__(audit_ledger=audit, refresh_coordinator=refresh_coordinator)
        self._staged_state_payloads: dict[str, dict[str, Any]] = {}
        self._projection_contexts: dict[str, dict[str, Any]] = {}
        self._staging_lock = threading.RLock()

    @property
    def canonical_backend(self) -> SQLiteL4Backend | None:
        return self._canonical_backend

    def stage_state_payload(
        self,
        *,
        commit_request_id: str,
        state_diff_id: str,
        payload: Any,
    ) -> None:
        """Stage inert canonical payload before validation; only UWG can commit it."""

        with self._staging_lock:
            self._staged_state_payloads.setdefault(commit_request_id, {})[
                state_diff_id
            ] = payload

    def stage_projection_context(
        self,
        *,
        commit_request_id: str,
        context: Mapping[str, Any],
    ) -> None:
        with self._staging_lock:
            self._projection_contexts[commit_request_id] = dict(context)

    def _take_staged_payloads(
        self, commit_request_id: str
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        with self._staging_lock:
            payloads = self._staged_state_payloads.pop(commit_request_id, {})
            context = self._projection_contexts.pop(commit_request_id, {})
        return payloads, context

    def _pending_refresh_receipts(
        self,
        *,
        refresh_plan: ReadSurfaceRefreshPlan,
        commit_receipt: UWGCommitReceipt,
        projection_tasks: Sequence[ProjectionTask],
    ) -> list[ReadSurfaceRefreshReceipt]:
        receipts: list[ReadSurfaceRefreshReceipt] = []
        for task in projection_tasks:
            receipt = ReadSurfaceRefreshReceipt(
                refresh_receipt_id=f"pending:{task.projection_id}",
                refresh_plan_ref=refresh_plan.refresh_plan_id,
                source_commit_receipt_ref=commit_receipt.commit_receipt_id,
                state_surface=task.target_surface,
                refresh_type=task.projection_type,
                before_snapshot=refresh_plan.before_snapshot,
                status="PENDING",
                retry_count=task.attempt_count,
                started_at=str(commit_receipt.committed_at),
                reason_codes=("projection_outbox_pending",),
            )
            receipts.append(stamp_digest(receipt))
        return receipts

    def commit(
        self,
        *,
        commit_request: CommitRequest,
        state_diffs: list[StateDiff],
        rollback_plan: RollbackPlan,
        refresh_plan: ReadSurfaceRefreshPlan,
    ) -> tuple[
        UWGCommitReceipt | None,
        UWGBlockedCommitReceipt | None,
        list[ReadSurfaceRefreshReceipt],
    ]:
        backend = self._canonical_backend
        if backend is None:
            return super().commit(
                commit_request=commit_request,
                state_diffs=state_diffs,
                rollback_plan=rollback_plan,
                refresh_plan=refresh_plan,
            )

        started = time.time()
        emit_uwg_span(
            "uwg.commit.request_received",
            policy_hash=commit_request.policy_hash,
            blueprint_hash=commit_request.blueprint_hash,
            replay_key=commit_request.replay_key,
            tenant_id=commit_request.tenant_id,
            source_surface=commit_request.source_surface,
            commit_request_id=commit_request.commit_request_id,
            extra={"state_diff_count": len(state_diffs), "transactional": True},
        )
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
            state_refs=tuple(commit_request.state_diff_refs),
        )

        validation = self._validate(
            commit_request, state_diffs, rollback_plan, refresh_plan
        )
        if validation.validation_status == "FAIL":
            blocked = self._emit_blocked(commit_request, validation)
            self._record_decision_safe(
                commit_request=commit_request,
                state_diffs=state_diffs,
                validation=validation,
                blocked=blocked,
                commit_receipt=None,
                refresh_receipts=[],
                latency_ms=int((time.time() - started) * 1000),
                snapshot_after=None,
                block_stage="validation",
            )
            self._take_staged_payloads(commit_request.commit_request_id)
            return None, blocked, []

        target_surfaces = tuple(commit_request.affected_state_surfaces) or tuple(
            row.target_surface for row in state_diffs
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
            failed_validation = stamp_digest(
                replace(
                    validation,
                    write_lock_status="CONTENTION",
                    failed_rules=tuple(validation.failed_rules)
                    + ("write_lock_contention",),
                    reason_codes=tuple(validation.reason_codes)
                    + ("write_lock_contention",),
                    deterministic_digest="",
                )
            )
            blocked = self._emit_blocked(commit_request, failed_validation)
            self._take_staged_payloads(commit_request.commit_request_id)
            return None, blocked, []

        try:
            snapshot_after = self._allocate_snapshot()
            payloads, projection_context = self._take_staged_payloads(
                commit_request.commit_request_id
            )
            try:
                result = backend.atomic_commit(
                    commit_request=commit_request,
                    state_diffs=state_diffs,
                    rollback_plan=rollback_plan,
                    refresh_plan=refresh_plan,
                    validation_receipt=validation,
                    write_lock_receipt=write_lock_receipt,
                    snapshot_before=snapshot_before,
                    snapshot_after=snapshot_after,
                    state_payload_overrides=payloads,
                    projection_context=projection_context,
                )
            except ReplayConflictError:
                failed_validation = stamp_digest(
                    replace(
                        validation,
                        validation_status="FAIL",
                        failed_rules=tuple(validation.failed_rules)
                        + ("replay_key_conflict",),
                        reason_codes=tuple(validation.reason_codes)
                        + ("replay_key_conflict",),
                        deterministic_digest="",
                    )
                )
                blocked = self._emit_blocked(commit_request, failed_validation)
                return None, blocked, []
            except DurableLockContentionError:
                failed_validation = stamp_digest(
                    replace(
                        validation,
                        validation_status="FAIL",
                        write_lock_status="CONTENTION",
                        failed_rules=tuple(validation.failed_rules)
                        + ("durable_write_lock_contention",),
                        reason_codes=tuple(validation.reason_codes)
                        + ("durable_write_lock_contention",),
                        deterministic_digest="",
                    )
                )
                blocked = self._emit_blocked(commit_request, failed_validation)
                return None, blocked, []

            commit_receipt = result.commit_receipt
            self._commits[commit_receipt.commit_receipt_id] = commit_receipt
            self._last_snapshot_id = commit_receipt.snapshot_after
            if isinstance(self._audit, SQLiteAuditLedger):
                self._audit.sync_committed_record(
                    result.audit_record, result.audit_append_receipt
                )
            pending_receipts = self._pending_refresh_receipts(
                refresh_plan=refresh_plan,
                commit_receipt=commit_receipt,
                projection_tasks=result.projection_tasks,
            )
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
                snapshot_id=commit_receipt.snapshot_after,
                status=(
                    "IDEMPOTENT_REPLAY" if result.idempotent_replay else "COMMITTED"
                ),
                extra={
                    "transactional": True,
                    "logical_hash": result.logical_hash,
                    "state_version_ids": list(result.state_version_ids),
                    "projection_outbox_count": len(result.projection_tasks),
                    "fencing_tokens": result.fencing_tokens,
                },
            )
            self._record_decision_safe(
                commit_request=commit_request,
                state_diffs=state_diffs,
                validation=validation,
                blocked=None,
                commit_receipt=commit_receipt,
                refresh_receipts=pending_receipts,
                latency_ms=int((time.time() - started) * 1000),
                snapshot_after=commit_receipt.snapshot_after,
                block_stage="",
            )
            return commit_receipt, None, pending_receipts
        finally:
            self._lock_mgr.release(
                target_surfaces=target_surfaces, owner=lock_owner
            )

    def complete_projection(
        self,
        projection_id: str,
        *,
        observed_payload_digest: str,
        receipt_payload: Mapping[str, Any] | None = None,
    ) -> None:
        if self._canonical_backend is None:
            raise RuntimeError("canonical backend is required for projection completion")
        record = self._canonical_backend.complete_projection(
            projection_id,
            observed_payload_digest=observed_payload_digest,
            receipt_payload=receipt_payload,
        )
        if isinstance(self._audit, SQLiteAuditLedger):
            self._audit.sync_committed_record(record)

    def fail_projection(self, projection_id: str, *, error: str) -> None:
        if self._canonical_backend is None:
            raise RuntimeError("canonical backend is required for projection failure")
        record = self._canonical_backend.fail_projection(projection_id, error=error)
        if isinstance(self._audit, SQLiteAuditLedger):
            self._audit.sync_committed_record(record)

    def projection_tasks(
        self,
        *,
        commit_receipt_id: str,
        statuses: Sequence[str] = ("PENDING", "FAILED"),
    ) -> list[ProjectionTask]:
        if self._canonical_backend is None:
            return []
        return self._canonical_backend.list_projection_tasks(
            commit_receipt_id=commit_receipt_id, statuses=statuses
        )

    def get_validation_receipt(
        self,
        validation_receipt_id: str,
    ) -> UWGValidationReceipt | None:
        """Return the original durable validation receipt for replayed commits."""

        existing = super().get_validation_receipt(validation_receipt_id)
        if existing is not None:
            return existing
        backend = self._canonical_backend
        if backend is None:
            return None
        payload = backend.get_validation_receipt_payload(validation_receipt_id)
        if payload is None:
            return None
        receipt = UWGValidationReceipt(
            **{
                **payload,
                "checked_rules": tuple(payload.get("checked_rules") or ()),
                "failed_rules": tuple(payload.get("failed_rules") or ()),
                "reason_codes": tuple(payload.get("reason_codes") or ()),
                "audit_refs": tuple(payload.get("audit_refs") or ()),
            }
        )
        self._validations[receipt.uwg_validation_receipt_id] = receipt
        return receipt

    def transition_state_lifecycle(
        self,
        *,
        state_version_id: str,
        source_commit_receipt_id: str,
        target_stage: str,
        reason: str,
    ) -> str:
        if self._canonical_backend is None:
            raise RuntimeError("canonical backend is required for lifecycle transitions")
        event_id = self._canonical_backend.transition_lifecycle(
            state_version_id=state_version_id,
            source_commit_receipt_id=source_commit_receipt_id,
            target_stage=target_stage,
            reason=reason,
            authorized_by_uwg=True,
        )
        if isinstance(self._audit, SQLiteAuditLedger):
            self._audit.reload()
        return event_id

    def reconcile_commit(self, commit_receipt_id: str) -> dict[str, Any]:
        if self._canonical_backend is None:
            return {
                "consistent": False,
                "reason_codes": ["canonical_backend_disabled"],
                "commit_receipt_id": commit_receipt_id,
            }
        return self._canonical_backend.reconcile_commit(commit_receipt_id)

    @staticmethod
    def _record_decision_safe(
        *,
        commit_request: CommitRequest,
        state_diffs: list[StateDiff],
        validation: UWGValidationReceipt,
        blocked: UWGBlockedCommitReceipt | None,
        commit_receipt: UWGCommitReceipt | None,
        refresh_receipts: list[ReadSurfaceRefreshReceipt],
        latency_ms: int,
        snapshot_after: str | None,
        block_stage: str,
    ) -> None:
        try:
            from agentic_core.L4_state.uwg.durable_write_gateway import (
                _record_uwg_decision,
            )

            _record_uwg_decision(
                commit_request=commit_request,
                state_diffs=state_diffs,
                validation_status=validation.validation_status,
                block_stage=block_stage,
                commit_receipt=commit_receipt,
                blocked_receipt=blocked,
                refresh_receipts=refresh_receipts,
                latency_ms=latency_ms,
                snapshot_after=snapshot_after,
            )
        except (ImportError, AttributeError, TypeError, ValueError, RuntimeError):
            return


__all__ = ["TransactionalDurableWriteGateway"]
