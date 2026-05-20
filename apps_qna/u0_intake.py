"""U0 Intake — wraps CLI envelope into a canonical ValidatedRequest.

W0 thin-slice: minimal intake that produces a ValidatedRequest from
interview parameters. Full implementation lands in W1.1 with proper
CLI parsing and schema validation.

Plan: .windsurf/plans/apps-qna-spine-integration-e9c5b3.md W0.1
"""

from __future__ import annotations

import time
import uuid
from datetime import datetime, timezone
from typing import Any

from agentic_core.L0_routing.intake.envelope import (
    AttachmentManifestShell,
    ModalityManifest,
)
from agentic_core.L0_routing.intake.validated_request import ValidatedRequest
from agentic_core.L0_routing.intake.verdicts import (
    AuthVerdict,
    IdempotencyStatus,
    NormalizationVerdict,
    PrincipalType,
    QuotaVerdict,
    SchemaVerdict,
    SourceClass,
)


def intake_interview_request(
    *,
    interview_slug: str,
    request_id: str | None = None,
    briefing_path: str | None = None,
) -> ValidatedRequest:
    """Produce a ValidatedRequest for a live interview runtime invocation.

    Args:
        interview_slug: The interview slug identifier.
        request_id: Optional explicit request id; defaults to a fresh uuid.
        briefing_path: Optional path to an uploaded briefing file.

    Returns:
        A ValidatedRequest stamped for live interview runtime.
    """
    request_id = request_id or uuid.uuid4().hex
    received_at = datetime.now(timezone.utc).isoformat()

    return ValidatedRequest(
        request_id=request_id,
        session_id=f"live_interview:{interview_slug}",
        trace_root=request_id,
        ingress_time_unix=time.time(),
        received_at_iso=received_at,
        source_channel="apps_qna.app_ingress_runner",
        source_class=SourceClass.BATCH,
        tenant_bind=None,
        workspace_bind=None,
        principal_type=PrincipalType.SERVICE,
        principal_id="apps_qna.live_interview",
        auth_verdict=AuthVerdict.SERVICE_BOUND,
        caller_scope_baseline="service:internal",
        region_scope_baseline=None,
        baseline_entitlements=("apps_qna.live_interview",),
        quota_verdict=QuotaVerdict.ALLOWED,
        quota_bucket="apps_qna:live_interview:default",
        rate_window_state="not_applicable",
        dedupe_status="not_applicable",
        idempotency_status=IdempotencyStatus.NOT_APPLICABLE,
        abuse_precheck_status="clear",
        retry_after_seconds=None,
        schema_verdict=SchemaVerdict.VALID,
        envelope_version="apps_qna.v1",
        request_shape_class="apps_qna.types.Interview",
        modality_manifest=ModalityManifest(),
        field_validation_report=(),
        normalization_verdict=NormalizationVerdict.PRESERVED,
        normalized_payload=None,
        normalized_payload_ref=f"interview://{interview_slug}",
        raw_payload_ref=f"interview://{interview_slug}",
        raw_payload_hash="",
        normalized_payload_hash="",
        normalization_report=(),
        suspicious_field_markers=(),
        attachment_manifest=AttachmentManifestShell(),
        upstream_traceparent=None,
        locale=None,
        timezone="UTC",
        client_version=None,
        platform="apps_qna.cli",
        batch_id=interview_slug,
        job_id=None,
        alert_id=None,
        webhook_delivery_id=None,
        ingress_reason_codes=(),
        downstream_authority="none",
        permitted_next_layer="L1",
        intake_status="VALIDATED_FOR_L1",
        intake_manifest_hash="",
        normalized_request_hash="",
    )


__all__ = ["intake_interview_request"]
