"""Exit Wiring — wires L2 output to Exit v6, emits exactly one X3.

W0 thin-slice: minimal exit that produces an ExitReviewPacket with
a single X3 disposition. Full implementation lands in W4.2 with
FEC producer integration and X1/X2/X3 pipeline.

D2.1: Optional UWG/L4 durable write path via emit_uwg_pack_record().
Callers may persist a sealed CardPackManifestExtended to the durable
L4 write surface. The write is strictly optional — failure is fail-open
and returns UWGWriteResult with skipped=True. Only source_surface="Exit"
is accepted by DurableWriteGateway; this module encapsulates that detail.

Plan: docs/archive/windsurf/legacy-tree/plans/apps-qna-spine-integration-e9c5b3.md W0.4
Plan (D2.1): docs/archive/windsurf/legacy-tree/plans/apps-qna-spine-deferred-e9c5b3.md D2
"""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from typing import Any

from apps_qna.types.spine_contracts import (
    CardPackManifestExtended,
    ExitReviewPacket,
    X3Disposition,
)


def emit_exit_review(
    *,
    manifest: CardPackManifestExtended,
    evidence_contract: dict[str, Any],
    build_valid: bool = True,
) -> ExitReviewPacket:
    """Emit exactly one X3 disposition for the completed build.

    Args:
        manifest: The sealed card pack manifest.
        evidence_contract: The evidence contract used.
        build_valid: Whether the build passed validation.

    Returns:
        An ExitReviewPacket with exactly one X3 disposition.
    """
    if not build_valid:
        return ExitReviewPacket(
            x3_disposition=X3Disposition.SAFE_ABSTAIN,
            final_evidence_contract=evidence_contract,
            manifest=manifest,
            reason_codes=("build_validation_failed",),
        )

    if not manifest.cards:
        return ExitReviewPacket(
            x3_disposition=X3Disposition.SAFE_ABSTAIN,
            final_evidence_contract=evidence_contract,
            manifest=manifest,
            reason_codes=("no_cards_rendered",),
        )

    evidence_sufficiency = evidence_contract.get("evidence_sufficiency", "empty")
    if evidence_sufficiency == "empty":
        return ExitReviewPacket(
            x3_disposition=X3Disposition.SAFE_ABSTAIN,
            final_evidence_contract=evidence_contract,
            manifest=manifest,
            reason_codes=("empty_evidence",),
        )

    return ExitReviewPacket(
        x3_disposition=X3Disposition.ALLOW_FINISH,
        final_evidence_contract=evidence_contract,
        manifest=manifest,
        reason_codes=(),
    )


@dataclass(frozen=True)
class UWGWriteResult:
    """Result of an optional UWG durable write for a sealed pack manifest.

    Attributes:
        committed: True when the UWG accepted and applied the commit.
        skipped: True when the write was bypassed (disabled or not requested).
        blocked: True when the UWG blocked the commit (validation failed).
        commit_receipt_id: Receipt ID from UWGCommitReceipt on success.
        blocked_receipt_id: Receipt ID from UWGBlockedCommitReceipt on block.
        reason: Human-readable reason for skip or block.
    """

    committed: bool = False
    skipped: bool = False
    blocked: bool = False
    commit_receipt_id: str = ""
    blocked_receipt_id: str = ""
    reason: str = ""
    error: str = ""


def emit_uwg_pack_record(
    *,
    manifest: CardPackManifestExtended,
    exit_packet: ExitReviewPacket,
    tenant_id: str = "apps_qna",
    policy_hash: str = "",
    blueprint_hash: str = "",
    replay_key: str = "",
    request_id: str = "",
    run_id: str = "",
    trace_root: str = "",
    enabled: bool = True,
) -> UWGWriteResult:
    """Optionally commit a sealed pack manifest to the UWG/L4 durable surface.

    This is a strictly optional write. The function is fail-open: any error
    (import failure, UWG blocked, contention) returns a UWGWriteResult with
    skipped=True or blocked=True rather than raising.

    Only X3Disposition.ALLOW_FINISH packets are committed. SAFE_ABSTAIN and
    other dispositions are skipped — there is nothing durable to write.

    Args:
        manifest: The sealed CardPackManifestExtended to persist.
        exit_packet: The ExitReviewPacket produced by emit_exit_review().
        tenant_id: Tenant identifier for the commit.
        policy_hash: Policy hash from the route contract.
        blueprint_hash: Blueprint hash from the route contract.
        replay_key: Replay key for idempotency.
        request_id: Correlation ID for audit trail.
        run_id: Run identifier.
        trace_root: OTEL trace root.
        enabled: Set False to bypass unconditionally (default True).

    Returns:
        UWGWriteResult describing the outcome.
    """
    if not enabled:
        return UWGWriteResult(skipped=True, reason="disabled_by_caller")

    if exit_packet.x3_disposition != X3Disposition.ALLOW_FINISH:
        return UWGWriteResult(
            skipped=True,
            reason=f"non_allow_finish_disposition:{exit_packet.x3_disposition.value}",
        )

    try:
        from agentic_core.L4_state.contracts.records import (
            CommitRequest,
            ReadSurfaceRefreshPlan,
            RollbackPlan,
            StateDiff,
        )
        from agentic_core.L4_state.uwg.durable_write_gateway import (
            DurableWriteGateway,
        )
    except ImportError as exc:
        return UWGWriteResult(skipped=True, reason="uwg_import_unavailable", error=str(exc))

    try:
        manifest_json = json.dumps(manifest.to_dict(), sort_keys=True)
        manifest_hash = hashlib.sha256(manifest_json.encode()).hexdigest()

        commit_id = str(uuid.uuid4())
        rollback_id = str(uuid.uuid4())
        refresh_id = str(uuid.uuid4())
        diff_id = str(uuid.uuid4())

        effective_policy = policy_hash or f"apps_qna::policy::{manifest_hash[:16]}"
        effective_blueprint = blueprint_hash or f"apps_qna::blueprint::{manifest_hash[:16]}"
        effective_replay = replay_key or f"apps_qna::replay::{commit_id}"
        effective_request = request_id or commit_id
        effective_run = run_id or commit_id
        effective_trace = trace_root or commit_id

        rollback_plan = RollbackPlan(
            rollback_plan_id=rollback_id,
            blast_radius="single_surface",
            target_surfaces=("apps_qna::pack_manifest",),
        )
        refresh_plan = ReadSurfaceRefreshPlan(
            refresh_plan_id=refresh_id,
            source_commit_receipt_ref="",
            before_snapshot="",
            expected_after_snapshot="",
            stale_projection_policy="noop",
            retry_policy="none",
            policy_hash=effective_policy,
            blueprint_hash=effective_blueprint,
        )
        state_diff = StateDiff(
            state_diff_id=diff_id,
            target_surface="apps_qna::pack_manifest",
            operation_type="append_record",
            after_candidate=manifest_hash,
            schema_ref="apps_qna::pack_manifest::v1",
            blast_radius="single_surface",
            rollback_plan_ref=rollback_id,
            proposed_by_surface="Exit",
            created_at=manifest.built_at or "unknown",
        )
        commit_request = CommitRequest(
            commit_request_id=commit_id,
            cleared_exit_review_packet_ref=exit_packet.x3_disposition.value,
            request_id=effective_request,
            run_id=effective_run,
            trace_root=effective_trace,
            tenant_id=tenant_id,
            policy_hash=effective_policy,
            blueprint_hash=effective_blueprint,
            route_contract_ref=manifest.interview_slug or "apps_qna::route",
            replay_key=effective_replay,
            rollback_plan_ref=rollback_id,
            blast_radius="single_surface",
            source_surface="Exit",
            state_diff_refs=(diff_id,),
            gate_verdict_refs=(f"x3:{exit_packet.x3_disposition.value}",),
            affected_state_surfaces=("apps_qna::pack_manifest",),
        )

        gateway = DurableWriteGateway()
        commit_receipt, blocked_receipt, _ = gateway.commit(
            commit_request=commit_request,
            state_diffs=[state_diff],
            rollback_plan=rollback_plan,
            refresh_plan=refresh_plan,
        )

        if commit_receipt is not None:
            return UWGWriteResult(
                committed=True,
                commit_receipt_id=commit_receipt.commit_receipt_id,
            )
        blocked_id = blocked_receipt.blocked_commit_receipt_id if blocked_receipt else ""
        blocked_codes = (
            ",".join(blocked_receipt.blocked_reason_codes) if blocked_receipt else "unknown"
        )
        return UWGWriteResult(
            blocked=True,
            blocked_receipt_id=blocked_id,
            reason=blocked_codes,
        )

    except Exception as exc:  # guardian: allow-broad-except -- UWG write is optional; any failure must be fail-open to not block exit pipeline
        return UWGWriteResult(skipped=True, reason="uwg_error", error=str(exc))


__all__ = ["emit_exit_review", "emit_uwg_pack_record", "UWGWriteResult"]
