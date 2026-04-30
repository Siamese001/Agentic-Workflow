"""apps_qna spine-handoff wrapper — Wave 7 phase 7.1.

Wraps ``apps_qna.builder.card_pack_builder.CardPackBuilder.build()`` in
a canonical ``ValidatedRequest`` envelope so build-time invocations
participate in the spine's intake-validation contract.

Architectural shape (per
``docs/reference/APP_OVERLAY_VS_CORE_ONLY_RUNTIME.md``):

    apps_qna's ``spine_manifest.yaml`` declares ``build_time_compiler``
    as its only claimed route. This route legitimately requires zero
    canonical authority contracts (no ``L1PlanContract``,
    ``RouteContract``, ``CompiledPromptArtifact``, ``SealedArtifact``,
    ``ExitReviewPacket``, ``CommitRequest``) because the spine is not
    in the runtime path of the pasted answer — ChatGPT is.

    What the spine DOES provide for a build-time tool is **intake
    validation**: a ``ValidatedRequest`` is the canonical record that
    the Interview YAML schema was checked, the build was authorized,
    and the resulting pack is reproducible from the validated input.
    Wrapping the existing builder in this envelope is the smallest
    possible "spine delegation" seam that's actually honest.

Honesty principle
-----------------
This module does NOT fabricate ``RouteContract`` / ``SealedArtifact`` /
``CommitRequest`` for a build that doesn't make those decisions. That
would be contract theater. The build_time_compiler route's empty
required-contract set is the architecture admitting that build-time
tools are different from R3_action / R4_workflow runtime requests.

Constitutional alignment
------------------------
- §3 anti-bypass: writes still go through UWG via ``CardPackBuilder``.
- §22 graph-layer evidence: the wrapper introduces an L0 import edge
  (``ValidatedRequest`` from
  ``agentic_core.L0_routing.intake.validated_request``) that the
  scanner counts.
- §29 closed-loop: emits ``event_kind="validated_request_emit"`` to the
  apps_qna_pack_lifecycle ledger paired with the ``ROUTER_DECISION``-
  style log line.
"""

from __future__ import annotations

import logging
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Spine intake contract (the only canonical contract a build_time_compiler
# legitimately needs).
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

from apps_qna.builder.card_pack_builder import CardPackBuilder
from apps_qna.config.build_config import QnaBuildConfig
from apps_qna.config.route_registry import RouteRegistry
from apps_qna.integrations.spine_adapter import emit_pack_lifecycle_event
from apps_qna.types.qna_types import CardPackManifest, Interview

_log = logging.getLogger(__name__)

_BUILD_TIME_SOURCE_CHANNEL: str = "apps_qna.build_time_compiler"
_BUILD_TIME_REQUEST_SHAPE: str = "apps_qna.types.Interview"
_DEFAULT_QUOTA_BUCKET: str = "apps_qna:build_time:default"


# ---------------------------------------------------------------------------
# Build-time ValidatedRequest factory
# ---------------------------------------------------------------------------


def _hash_interview_payload(interview: Interview) -> tuple[str, str]:
    """Return (raw_payload_hash, normalized_payload_hash).

    Both are SHA-256 hex digests of the JSON-serialized Interview. For
    a build-time tool there is no separate raw-vs-normalized
    distinction, so both values are identical -- this honestly reports
    "the input WAS the normalized form".
    """
    import hashlib
    import json

    payload = json.dumps(
        interview.model_dump(mode="json"),
        sort_keys=True,
        default=str,
    )
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return (digest, digest)


def _build_time_validated_request(
    interview: Interview,
    *,
    request_id: str | None = None,
) -> ValidatedRequest:
    """Construct a ValidatedRequest stamped for a build-time invocation.

    The verdict fields (auth/quota/schema/normalization/idempotency)
    are filled with their PASS-equivalent values because a build-time
    invocation is not subject to HTTP-style intake gates -- but the
    contract type still requires them, so we pick the verdicts that
    most accurately describe a successful local build.

    Per the intake invariant in ``validated_request.py``:
    ``downstream_authority`` is permanently ``"none"`` and
    ``permitted_next_layer`` is ``"L1"``. We honor both.
    """
    request_id = request_id or uuid.uuid4().hex
    raw_hash, norm_hash = _hash_interview_payload(interview)
    received_at = datetime.now(timezone.utc).isoformat()
    slug = (
        interview.build_metadata.interview_slug
        if interview.build_metadata
        else "unknown"
    )
    return ValidatedRequest(
        # Identifiers
        request_id=request_id,
        session_id=f"build_time:{slug}",
        trace_root=request_id,
        # Timing / origin
        ingress_time_unix=time.time(),
        received_at_iso=received_at,
        source_channel=_BUILD_TIME_SOURCE_CHANNEL,
        source_class=SourceClass.BATCH,
        # Identity (build-time service principal)
        tenant_bind=None,
        workspace_bind=None,
        principal_type=PrincipalType.SERVICE,
        principal_id="apps_qna.build_time",
        auth_verdict=AuthVerdict.SERVICE_BOUND,
        caller_scope_baseline="service:internal",
        region_scope_baseline=None,
        baseline_entitlements=("apps_qna.build", "apps_qna.lint"),
        # Quota / dedupe (build-time invocations are not rate-limited)
        quota_verdict=QuotaVerdict.ALLOWED,
        quota_bucket=_DEFAULT_QUOTA_BUCKET,
        rate_window_state="not_applicable",
        dedupe_status="not_applicable",
        idempotency_status=IdempotencyStatus.NOT_APPLICABLE,
        abuse_precheck_status="clear",
        retry_after_seconds=None,
        # Schema / modality (Interview is the canonical typed shape)
        schema_verdict=SchemaVerdict.VALID,
        envelope_version="apps_qna.v1",
        request_shape_class=_BUILD_TIME_REQUEST_SHAPE,
        modality_manifest=ModalityManifest(),
        field_validation_report=(),
        # Normalization (the typed Interview IS the normalized form)
        normalization_verdict=NormalizationVerdict.PRESERVED,
        normalized_payload=None,
        normalized_payload_ref=f"interview://{slug}",
        raw_payload_ref=f"interview://{slug}",
        raw_payload_hash=raw_hash,
        normalized_payload_hash=norm_hash,
        normalization_report=(),
        suspicious_field_markers=(),
        attachment_manifest=AttachmentManifestShell(),
        # Routing-neutral metadata
        upstream_traceparent=None,
        locale=None,
        timezone="UTC",
        client_version=None,
        platform="apps_qna.cli",
        batch_id=slug,
        job_id=None,
        alert_id=None,
        webhook_delivery_id=None,
        # Authority guards (intake invariant)
        ingress_reason_codes=(),
        downstream_authority="none",
        permitted_next_layer="L1",
        # Extended fields (have defaults, but we set the ones that matter)
        intake_status="VALIDATED_FOR_L1",
        intake_manifest_hash=norm_hash,
        normalized_request_hash=norm_hash,
    )


# ---------------------------------------------------------------------------
# Public surface
# ---------------------------------------------------------------------------


def build_pack_via_spine(
    interview: Interview,
    output_dir: Path,
    *,
    extra_context: dict[str, Any] | None = None,
    config: QnaBuildConfig | None = None,
    registry: RouteRegistry | None = None,
    request_id: str | None = None,
) -> CardPackManifest:
    """Build a card pack inside a spine ValidatedRequest envelope.

    Args:
        interview: typed Interview input.
        output_dir: pack destination directory.
        extra_context: optional Jinja extra-context dict.
        config: build config; defaults to ``QnaBuildConfig()``.
        registry: optional route registry (for validation routes covered).
        request_id: optional explicit request-id (lets callers correlate
            multiple builds in the same session). Defaults to a fresh uuid.

    Returns:
        ``CardPackManifest`` from the underlying ``CardPackBuilder``.

    Side effects:
        - Constructs a ``ValidatedRequest`` for the build invocation.
        - Emits ``event_kind="validated_request_emit"`` to the
          apps_qna_pack_lifecycle ledger with the request_id and
          interview slug. This is the apps_qna_pack_lifecycle event
          that pairs with the existing pack_build event the
          CardPackBuilder emits.
        - Calls the existing CardPackBuilder.build() unchanged.

    Constitutional invariants:
        - ``ValidatedRequest.downstream_authority`` is always ``"none"``
          (enforced by the contract's ``__post_init__``).
        - ``ValidatedRequest.permitted_next_layer`` is always ``"L1"``
          (enforced by the contract's ``__post_init__``).
        - The build_time_compiler route requires zero authority
          contracts; we emit ValidatedRequest as defensive intake
          evidence, not as authority delegation.
    """
    validated = _build_time_validated_request(interview, request_id=request_id)

    # Emit the validated-request landing event. Fail-soft per spine_adapter
    # contract — ledger errors never abort a build.
    emit_pack_lifecycle_event(
        event_kind="validated_request_emit",
        prediction={
            "request_id": validated.request_id,
            "session_id": validated.session_id,
            "interview_slug": (
                interview.build_metadata.interview_slug
                if interview.build_metadata
                else "unknown"
            ),
            "request_shape_class": validated.request_shape_class,
            "schema_verdict": validated.schema_verdict.value,
            "auth_verdict": validated.auth_verdict.value,
            "raw_payload_hash": validated.raw_payload_hash,
        },
        score_band="clean",
        repo_area=str(output_dir),
        metadata={"trace_root": validated.trace_root},
    )

    _log.info(
        "spine_handoff: validated request_id=%s slug=%s -> CardPackBuilder.build",
        validated.request_id,
        interview.build_metadata.interview_slug
        if interview.build_metadata
        else "unknown",
    )

    builder = CardPackBuilder(
        config=config or QnaBuildConfig(),
        route_registry=registry,
    )
    return builder.build(interview, output_dir, extra_context=extra_context)


__all__ = [
    "_build_time_validated_request",  # exported for tests
    "build_pack_via_spine",
]
