"""apps_rfp U0 intake — produces ValidatedRequest for proposal assembly.

Mirrors apps_qna.u0_intake pattern: constructs the fully-populated
ValidatedRequest for the agentic_core spine from apps_rfp-specific
envelope fields.

Plan: .windsurf/plans/one-spine-qna-rfp-migration-d2e8f1.md W2.P1
"""
from __future__ import annotations

import time
import uuid
from datetime import datetime, timezone

from agentic_core.L0_routing.intake.validated_request import (
    AuthVerdict,
    IdempotencyStatus,
    ModalityManifest,
    NormalizationVerdict,
    PrincipalType,
    QuotaVerdict,
    SchemaVerdict,
    SourceClass,
    ValidatedRequest,
)


def intake_rfp_request(
    *,
    rfp_document_path: str = "",
    target_company: str = "",
    request_id: str | None = None,
    run_id: str | None = None,
    tenant_id: str = "apps_rfp",
    trace_id: str = "",
    dry_run: bool = False,
) -> ValidatedRequest:
    """Produce a ValidatedRequest for an apps_rfp proposal assembly invocation.

    Args:
        rfp_document_path: Path to the RFP document being responded to.
        target_company: Target company name for the proposal.
        request_id: Optional explicit request id; defaults to a fresh uuid.
        run_id: Optional explicit run id; defaults to a fresh uuid.
        tenant_id: Tenant identifier; defaults to 'apps_rfp'.
        trace_id: Optional trace id for observability.
        dry_run: If True, marks the request as dry-run mode.

    Returns:
        ValidatedRequest stamped for apps_rfp proposal_assembly runtime.

    Raises:
        ValueError: If neither rfp_document_path nor target_company is provided.
    """
    if not rfp_document_path and not target_company:
        raise ValueError(
            "intake_rfp_request: rfp_document_path or target_company is required."
        )

    request_id = request_id or uuid.uuid4().hex
    run_id = run_id or f"rfp-run-{uuid.uuid4().hex[:12]}"
    received_at = datetime.now(timezone.utc).isoformat()

    batch_key = rfp_document_path or target_company

    return ValidatedRequest(
        request_id=request_id,
        session_id=f"rfp_proposal:{batch_key}",
        trace_root=trace_id or request_id,
        ingress_time_unix=time.time(),
        received_at_iso=received_at,
        source_channel="apps_rfp.proposal_assembly_runtime",
        source_class=SourceClass.BATCH,
        tenant_bind=tenant_id,
        workspace_bind=None,
        principal_type=PrincipalType.SERVICE,
        principal_id="apps_rfp.proposal_assembly",
        auth_verdict=AuthVerdict.SERVICE_BOUND,
        caller_scope_baseline="service:internal",
        region_scope_baseline=None,
        baseline_entitlements=("apps_rfp:proposal_assembly",),
        quota_verdict=QuotaVerdict.ALLOWED,
        quota_bucket="apps_rfp.default",
        rate_window_state="ok",
        dedupe_status="ok",
        idempotency_status=IdempotencyStatus.NEW,
        abuse_precheck_status="ok",
        retry_after_seconds=None,
        schema_verdict=SchemaVerdict.VALID,
        envelope_version="1",
        request_shape_class="rfp_proposal_assembly",
        modality_manifest=ModalityManifest(declared=("text",), observed=("text",)),
        field_validation_report=(),
        normalization_verdict=NormalizationVerdict.NORMALIZED,
        normalized_payload={
            "rfp_document_path": rfp_document_path,
            "target_company": target_company,
            "dry_run": dry_run,
        },
        normalized_payload_ref="",
        raw_payload_ref="",
        raw_payload_hash="",
        normalized_payload_hash="",
        normalization_report="",
        suspicious_field_markers=(),
        attachment_manifest=(),
        upstream_traceparent="",
        locale="en",
        timezone="UTC",
        client_version="apps_rfp.w2",
        platform="server",
        batch_id=batch_key,
        job_id=run_id,
        alert_id=None,
        webhook_delivery_id=None,
        ingress_reason_codes=(),
        downstream_authority="none",
        permitted_next_layer="L1",
        intake_status="ok",
        intake_manifest_hash="",
        normalized_request_hash="",
        ingress_replay_seed_ref="",
        transport_receipt_ref="",
        identity_receipt_ref="",
        quota_receipt_ref="",
        schema_validation_receipt_ref="",
        correlation_receipt_ref="",
        origin_label_manifest_ref="",
        intake_warnings=(),
        handoff_created_at_observed=received_at,
    )


__all__ = ["intake_rfp_request"]
