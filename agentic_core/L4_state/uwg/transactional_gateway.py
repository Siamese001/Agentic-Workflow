"""Transactional UWG implementation backed by canonical SQLite L4 state.

Unlike the compatibility gateway, this class does not equate receipt creation
with state mutation.  It delegates one atomic state/audit/receipt/outbox write
to :class:`SQLiteL4Backend` and exposes derived projection execution as a
recoverable outbox operation.
"""

from __future__ import annotations

import dataclasses
import time
import uuid
from dataclasses import replace
from typing import Any, Mapping, Optional, Sequence

from agentic_core.L4_state.audit.audit_ledger import AuditLedger
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
from agentic_core.L4_state.projections.runner import (
    ProjectionHandler,
    ProjectionRunResult,
    ProjectionRunner,
)
from agentic_core.L4_state.storage.sqlite_backend import (
    L4StorageError,
    ReplayConflictError,
    SQLiteL4Backend,
    SurfaceLockContentionError,
)
from agentic_core.L4_state.uwg.durable_write_gateway import DurableWriteGateway


class TransactionalDurableWriteGateway(DurableWriteGateway):
    """UWG whose successful result proves canonical durable state exists."""

    def __init__(
        self,
        *,
        backend: SQLiteL4Backend | None = None,
        audit_ledger: AuditLedger | None = None,
        **kwargs: Any,
    ) -> None:
        self._backend = backend or SQLiteL4Backend()
        ledger = audit_ledger or SQLiteAuditLedger(self._backend.path)
        super().__init__(audit_ledger=ledger, **kwargs)

    @property
    def backend(self) -> SQLiteL4Backend:
        return self._backend

    @staticmethod
    def _payload(value: Any) -> dict[str, Any]:
        if dataclasses.is_dataclass(value):
            return dataclasses.asdict(value)
        if isinstance(value, Mapping):
            return dict(value)
        raise TypeError(f"expected record mapping, got {type(value).__name__}")

    def _persist_blocked(
        self,
        *,
        commit_request: CommitRequest,
        validation: UWGValidationReceipt,
        blocked: UWGBlockedCommitReceipt,
    ) -> None:
        try:
            self._backend.persist_blocked_receipt(
                commit_request_id=commit_request.commit_request_id,
                validation_receipt=validation,
                blocked_receipt=blocked,
            )
        except Exception:
            # The returned block remains fail-closed.  Storage unavailability is
            # already represented by the audit sentinel produced by _emit_blocked.
            pass

    def _blocked_from_validation(
        self,
        *,
        commit_request: CommitRequest,
        validation: UWGValidationReceipt,
    ) -> tuple[None, UWGBlockedCommitReceipt, list[ReadSurfaceRefreshReceipt]]:
        blocked = self._emit_blocked(commit_request, validation)
        self._persist_blocked(
            commit_request=commit_request,
            validation=validation,
            blocked=blocked,
        )
        return None, blocked, []

    def commit(
        self,
        *,
        commit_request: CommitRequest,
        state_diffs: list[StateDiff],
        rollback_plan: RollbackPlan,
        refresh_plan: ReadSurfaceRefreshPlan,
        state_payloads: Mapping[str, Any] | None = None,
        projection_specs: Sequence[Mapping[str, Any]] | None = None,
        projection_context: Mapping[str, Any] | None = None,
    ) -> tuple[
        Optional[UWGCommitReceipt],
        Optional[UWGBlockedCommitReceipt],
        list[ReadSurfaceRefreshReceipt],
    ]:
        """Validate and atomically persist canonical L4 mutation evidence."""

        started = time.time()
        emit_uwg_span(
            "uwg.commit.request_received",
            policy_hash=commit_request.policy_hash,
            blueprint_hash=commit_request.blueprint_hash,
            replay_key=commit_request.replay_key,
            tenant_id=commit_request.tenant_id,
            source_surface=commit_request.source_surface,
            commit_request_id=commit_request.commit_request_id,
            extra={"state_diff_count": len(state_diffs), "transactional_backend": "sqlite"},
        )
        validation = self._validate(
            commit_request,
            state_diffs,
            rollback_plan,
            refresh_plan,
        )
        self._validations[validation.uwg_validation_receipt_id] = validation
        if validation.validation_status != "PASS":
            return self._blocked_from_validation(
                commit_request=commit_request,
                validation=validation,
            )

        try:
            result = self._backend.commit_bundle(
                commit_request=commit_request,
                state_diffs=state_diffs,
                validation_receipt=validation,
                rollback_plan=rollback_plan,
                refresh_plan=refresh_plan,
                state_payloads=state_payloads,
                projection_specs=projection_specs,
                projection_context=projection_context,
            )
        except (ReplayConflictError, SurfaceLockContentionError, L4StorageError) as exc:
            reason = (
                "replay_key_conflict"
                if isinstance(exc, ReplayConflictError)
                else "write_lock_contention"
                if isinstance(exc, SurfaceLockContentionError)
                else "l4_transaction_failed"
            )
            failed_validation = stamp_digest(
                replace(
                    validation,
                    validation_status="FAIL",
                    write_lock_status=(
                        "CONTENTION" if isinstance(exc, SurfaceLockContentionError) else "FAILED"
                    ),
                    failed_rules=tuple(validation.failed_rules) + (reason,),
                    reason_codes=tuple(validation.reason_codes) + (reason, str(exc)),
                    deterministic_digest="",
                )
            )
            self._validations[failed_validation.uwg_validation_receipt_id] = failed_validation
            return self._blocked_from_validation(
                commit_request=commit_request,
                validation=failed_validation,
            )

        receipt_payload = dict(result.commit_receipt_payload)
        receipt_payload.pop("schema_version", None)
        receipt_payload.pop("deterministic_digest", None)
        commit_receipt = stamp_digest(UWGCommitReceipt(**receipt_payload))
        self._commits[commit_receipt.commit_receipt_id] = commit_receipt
        self._last_snapshot_id = commit_receipt.snapshot_after

        queued_receipts: list[ReadSurfaceRefreshReceipt] = []
        for item in result.outbox_items:
            queued = ReadSurfaceRefreshReceipt(
                refresh_receipt_id=f"refreshqueued:{item.projection_id}",
                refresh_plan_ref=refresh_plan.refresh_plan_id,
                source_commit_receipt_ref=commit_receipt.commit_receipt_id,
                state_surface=item.state_surface,
                refresh_type=item.projection_type,
                before_snapshot=commit_receipt.snapshot_before,
                status="SKIPPED",
                retry_count=item.attempt_count,
                started_at=commit_receipt.committed_at,
                after_snapshot=commit_receipt.snapshot_after,
                completed_at=None,
                stale_projection_warning="projection_queued_not_yet_verified",
                reason_codes=("projection_queued",),
                audit_refs=(commit_receipt.audit_append_receipt_ref,),
            )
            queued_receipts.append(stamp_digest(queued))

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
            status="REPLAYED" if result.replayed else "COMMITTED_CANONICAL",
            extra={
                "state_version_count": len(result.state_version_ids),
                "projection_outbox_count": len(result.outbox_items),
                "latency_ms": int((time.time() - started) * 1000),
            },
        )
        return commit_receipt, None, queued_receipts

    def run_projection_outbox(
        self,
        *,
        handlers: Mapping[str, ProjectionHandler],
        commit_receipt_id: str | None = None,
        retry_failed: bool = True,
        raise_on_failure: bool = False,
    ) -> list[ProjectionRunResult]:
        """Execute recoverable derived projections through the UWG boundary."""

        runner = ProjectionRunner(self._backend, handlers=handlers)
        return runner.run_pending(
            commit_receipt_id=commit_receipt_id,
            retry_failed=retry_failed,
            raise_on_failure=raise_on_failure,
        )

    def transition_state_lifecycle(
        self,
        *,
        state_version_id: str,
        source_commit_receipt_id: str,
        target_stage: str,
        reason: str,
    ) -> dict[str, Any]:
        """Apply an additive lifecycle transition under UWG authority."""

        if source_commit_receipt_id not in self._commits:
            payload = self._backend.get_commit_receipt_payload(source_commit_receipt_id)
            if payload is None:
                raise ValueError("source commit receipt is not present in canonical L4")
        return self._backend.transition_lifecycle(
            state_version_id=state_version_id,
            commit_receipt_id=source_commit_receipt_id,
            target_stage=target_stage,
            reason=reason,
            actor_surface="UWG",
        )

    def reconcile_commit(self, commit_receipt_id: str) -> tuple[bool, tuple[str, ...]]:
        return self._backend.reconcile_commit(commit_receipt_id)

    def get_commit_receipt(self, commit_receipt_id: str) -> Optional[UWGCommitReceipt]:
        existing = super().get_commit_receipt(commit_receipt_id)
        if existing is not None:
            return existing
        payload = self._backend.get_commit_receipt_payload(commit_receipt_id)
        if payload is None:
            return None
        payload = dict(payload)
        payload.pop("schema_version", None)
        payload.pop("deterministic_digest", None)
        receipt = stamp_digest(UWGCommitReceipt(**payload))
        self._commits[receipt.commit_receipt_id] = receipt
        return receipt

    def get_validation_receipt(
        self,
        validation_receipt_id: str,
    ) -> Optional[UWGValidationReceipt]:
        existing = super().get_validation_receipt(validation_receipt_id)
        if existing is not None:
            return existing
        payload = self._backend.get_validation_receipt_payload(validation_receipt_id)
        if payload is None:
            return None
        payload = dict(payload)
        payload.pop("schema_version", None)
        payload.pop("deterministic_digest", None)
        receipt = stamp_digest(UWGValidationReceipt(**payload))
        self._validations[receipt.uwg_validation_receipt_id] = receipt
        return receipt


__all__ = ["TransactionalDurableWriteGateway"]
