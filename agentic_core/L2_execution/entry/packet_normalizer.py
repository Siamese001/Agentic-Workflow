"""Packet Normalizer — entry-time L2 packet validation and normalization.

Maps to: docs/reference/04_L2_Execute/04.1 §PHASE 2 ENTRY PIPELINE
                                      §PHASE 3 FAILURE MODES
                                      §PHASE 4 ACCEPTANCE TESTS

Purpose
-------
Convert a raw signed packet from L0 or a current step from L3 into a
:class:`agentic_core.L2_execution.types.l2_execution_request.L2ExecutionRequest`
that E1 Prep can safely consume.

This is the single chokepoint for the L2 entry boundary. If a packet would
broaden authority, mutate the route, smuggle human text into authority
fields, or omit required governance metadata, it MUST be rejected here —
before E1 freezes any execution context.

Hard rule: this module performs **no execution and no retrieval**. It only
validates and normalizes shape.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any, Mapping

from agentic_core.L2_execution.types.l2_execution_request import (
    EntryRejection,
    EntryRejectionReason,
    ExecutionAuthorityContext,
    HumanInputScope,
    IssuerSurface,
    L2BoundaryAssertion,
    L2ExecutionRequest,
    SourcePacketType,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


_REQUIRED_REQUEST_FIELDS: tuple[str, ...] = (
    "request_id",
    "run_id",
    "trace_root",
    "route_id",
    "route_contract_ref",
    "execution_form",
    "signed_packet_ref",
    "task_spec_ref",
    "capability_token_ref",
    "sandbox_envelope_ref",
    "side_effect_class",
    "policy_hash",
    "blueprint_hash",
    "replay_key",
    "snapshot_manifest_ref",
    "expected_output_contract",
)


def _make_rejection_id() -> str:
    return f"l2-entry-reject-{uuid.uuid4().hex[:12]}"


def _has_human_text_in_authority(authority: ExecutionAuthorityContext) -> bool:
    """Heuristic: authority context fields must not contain free-form prose.

    The entry contract names these as opaque IDs / scope tokens. If the value
    contains a space (i.e. likely a sentence), or a newline, we treat it as
    human text leaking into an authority field — a forbidden transition under
    04.1 §PHASE 3.
    """
    suspect_fields = (
        authority.issuer_receipt_ref,
        authority.route_authority_ref,
        authority.capability_scope,
        authority.sandbox_scope,
        authority.tenant_scope,
        authority.acl_scope,
        authority.provider_lane,
        authority.filesystem_scope,
        authority.network_scope,
        authority.credential_scope,
    )
    for value in suspect_fields:
        if not isinstance(value, str):
            continue
        if "\n" in value:
            return True
        # Long strings with whitespace are prose, not refs/scopes.
        if " " in value and len(value) > 64:
            return True
    return False


def _human_input_scope_is_data_only(scope: HumanInputScope) -> bool:
    return scope is HumanInputScope.DATA_ONLY


# ---------------------------------------------------------------------------
# Normalization result
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class NormalizationResult:
    """Outcome of :func:`normalize_to_request`.

    Exactly one of ``request`` or ``rejection`` is non-None.
    """

    request: L2ExecutionRequest | None
    rejection: EntryRejection | None

    @property
    def ok(self) -> bool:
        return self.request is not None and self.rejection is None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def normalize_to_request(
    *,
    raw_packet: Mapping[str, Any],
    authority_context: ExecutionAuthorityContext,
    boundary_assertion: L2BoundaryAssertion | None = None,
    expected_route_digest: str | None = None,
) -> NormalizationResult:
    """Convert a raw signed packet to a normalized :class:`L2ExecutionRequest`.

    Args:
        raw_packet: A mapping carrying the fields from
            :data:`_REQUIRED_REQUEST_FIELDS` plus optional refs
            (``prompt_envelope_ref``, ``final_evidence_contract_ref``,
            ``l3_step_contract_ref``, PTC-related refs, etc.) and:

              * ``source_packet_type``: a :class:`SourcePacketType` value or
                its string name.
              * ``issuer_signature_hmac``: required non-empty signature.
              * ``grounded``: bool — when True, evidence/prompt refs are
                required.
              * ``is_model_execution``: bool — when True, prompt envelope is
                required.
              * ``is_ptc_execution``: bool — when True, ``ptc_execution_profile_ref``,
                ``script_digest``, and ``sandbox_profile_ref`` are required.
              * ``route_digest`` (optional): when provided AND
                ``expected_route_digest`` is given, they must match.

        authority_context: The :class:`ExecutionAuthorityContext` for this
            invocation. Must have ``issuer_surface`` ∈ {L0, L3}.

        boundary_assertion: Caller-provided assertion. If omitted, a
            default fully-asserted instance is constructed.

        expected_route_digest: Optional route digest to enforce.

    Returns:
        :class:`NormalizationResult` with either a sealed
        :class:`L2ExecutionRequest` ready for E1, or an
        :class:`EntryRejection` (no work performed).
    """
    boundary = boundary_assertion or L2BoundaryAssertion()

    # --- Boundary first (cheapest) ----------------------------------------
    if not boundary.all_clean():
        return NormalizationResult(
            request=None,
            rejection=EntryRejection(
                rejection_id=_make_rejection_id(),
                reason=EntryRejectionReason.BOUNDARY_VIOLATION,
                detail="L2BoundaryAssertion has unasserted bits",
                boundary_violations=boundary.violations(),
            ),
        )

    # --- Issuer must be governed (L0 or L3) -------------------------------
    if authority_context.issuer_surface not in (IssuerSurface.L0, IssuerSurface.L3):
        return NormalizationResult(
            request=None,
            rejection=EntryRejection(
                rejection_id=_make_rejection_id(),
                reason=EntryRejectionReason.NON_GOVERNED_ISSUER,
                detail=f"issuer_surface={authority_context.issuer_surface!r} is not L0/L3",
            ),
        )

    # --- Authority context invariants (data-only / no-write) --------------
    if not _human_input_scope_is_data_only(authority_context.human_input_scope):
        return NormalizationResult(
            request=None,
            rejection=EntryRejection(
                rejection_id=_make_rejection_id(),
                reason=EntryRejectionReason.HUMAN_TEXT_IN_AUTHORITY,
                detail="human_input_scope must be DATA_ONLY at L2 entry",
            ),
        )

    if _has_human_text_in_authority(authority_context):
        return NormalizationResult(
            request=None,
            rejection=EntryRejection(
                rejection_id=_make_rejection_id(),
                reason=EntryRejectionReason.HUMAN_TEXT_IN_AUTHORITY,
                detail="prose-like content detected in an authority context field",
            ),
        )

    if authority_context.durable_write_authority.value != "NONE":
        return NormalizationResult(
            request=None,
            rejection=EntryRejection(
                rejection_id=_make_rejection_id(),
                reason=EntryRejectionReason.GRANTS_DURABLE_WRITE,
                detail="L2 cannot accept a packet that grants durable_write_authority",
            ),
        )

    # --- Required fields --------------------------------------------------
    for fname in _REQUIRED_REQUEST_FIELDS:
        if fname not in raw_packet or raw_packet[fname] in (None, ""):
            return NormalizationResult(
                request=None,
                rejection=EntryRejection(
                    rejection_id=_make_rejection_id(),
                    reason=EntryRejectionReason.MISSING_REQUIRED_REF,
                    detail=f"required field missing or empty: {fname}",
                    failed_field=fname,
                ),
            )

    # route_contract_ref also explicitly checked (FAIL_CLOSED #1)
    if not raw_packet.get("route_contract_ref"):
        return NormalizationResult(
            request=None,
            rejection=EntryRejection(
                rejection_id=_make_rejection_id(),
                reason=EntryRejectionReason.NO_ROUTE_CONTRACT_REF,
                detail="route_contract_ref is required",
            ),
        )

    # --- Source packet type -----------------------------------------------
    spt_raw = raw_packet.get("source_packet_type")
    if isinstance(spt_raw, SourcePacketType):
        source_packet_type = spt_raw
    else:
        try:
            source_packet_type = SourcePacketType(str(spt_raw))
        except ValueError:
            return NormalizationResult(
                request=None,
                rejection=EntryRejection(
                    rejection_id=_make_rejection_id(),
                    reason=EntryRejectionReason.MISSING_REQUIRED_REF,
                    detail=f"unknown source_packet_type={spt_raw!r}",
                    failed_field="source_packet_type",
                ),
            )

    # --- Signature --------------------------------------------------------
    issuer_sig = str(raw_packet.get("issuer_signature_hmac", "") or "")
    if not issuer_sig:
        return NormalizationResult(
            request=None,
            rejection=EntryRejection(
                rejection_id=_make_rejection_id(),
                reason=EntryRejectionReason.UNSIGNED_PACKET,
                detail="issuer_signature_hmac is empty",
                source_packet_type=source_packet_type,
            ),
        )

    # --- Route digest match (when caller asserts an expected digest) ------
    declared_digest = raw_packet.get("route_digest")
    if expected_route_digest is not None and declared_digest is not None:
        if str(declared_digest) != str(expected_route_digest):
            return NormalizationResult(
                request=None,
                rejection=EntryRejection(
                    rejection_id=_make_rejection_id(),
                    reason=EntryRejectionReason.ROUTE_DIGEST_MISMATCH,
                    detail=(
                        f"route_digest mismatch: packet={declared_digest!r} "
                        f"expected={expected_route_digest!r}"
                    ),
                    source_packet_type=source_packet_type,
                ),
            )

    # --- Forbidden requests in payload (asks L2 to retrieve/route/expand)
    forbidden_intents = (
        "retrieve_more_evidence",
        "select_route",
        "reroute",
        "expand_workflow",
        "approve_output",
        "ask_user_clarification",
    )
    declared_intent = str(raw_packet.get("declared_intent", "") or "")
    if declared_intent in forbidden_intents:
        return NormalizationResult(
            request=None,
            rejection=EntryRejection(
                rejection_id=_make_rejection_id(),
                reason=EntryRejectionReason.ASKS_L2_TO_RETRIEVE_OR_ROUTE,
                detail=f"declared_intent={declared_intent!r} is forbidden at L2",
                source_packet_type=source_packet_type,
            ),
        )

    # --- Mode-specific required refs --------------------------------------
    grounded = bool(raw_packet.get("grounded", False))
    is_model_execution = bool(raw_packet.get("is_model_execution", False))
    is_ptc_execution = bool(raw_packet.get("is_ptc_execution", False))

    final_evidence_contract_ref = raw_packet.get("final_evidence_contract_ref")
    prompt_envelope_ref = raw_packet.get("prompt_envelope_ref")

    if grounded and (not final_evidence_contract_ref or not prompt_envelope_ref):
        return NormalizationResult(
            request=None,
            rejection=EntryRejection(
                rejection_id=_make_rejection_id(),
                reason=EntryRejectionReason.GROUNDED_MISSING_EVIDENCE_CONTRACT,
                detail="grounded=True requires final_evidence_contract_ref and prompt_envelope_ref",
                source_packet_type=source_packet_type,
            ),
        )

    if is_model_execution and not prompt_envelope_ref:
        return NormalizationResult(
            request=None,
            rejection=EntryRejection(
                rejection_id=_make_rejection_id(),
                reason=EntryRejectionReason.MODEL_EXECUTION_MISSING_PROMPT_ENVELOPE,
                detail="is_model_execution=True requires prompt_envelope_ref",
                source_packet_type=source_packet_type,
            ),
        )

    if is_ptc_execution:
        ptc_profile_ref = raw_packet.get("ptc_execution_profile_ref")
        script_digest = raw_packet.get("script_digest")
        sandbox_profile_ref = raw_packet.get("sandbox_profile_ref")
        if not ptc_profile_ref or not script_digest or not sandbox_profile_ref:
            return NormalizationResult(
                request=None,
                rejection=EntryRejection(
                    rejection_id=_make_rejection_id(),
                    reason=EntryRejectionReason.PTC_MISSING_DIGEST_OR_PROFILE,
                    detail=(
                        "is_ptc_execution=True requires ptc_execution_profile_ref, "
                        "script_digest, and sandbox_profile_ref"
                    ),
                    source_packet_type=source_packet_type,
                ),
            )

    # --- All checks passed: build the normalized request ------------------
    telemetry_keys_raw = raw_packet.get("telemetry_keys", ())
    if isinstance(telemetry_keys_raw, (list, tuple)):
        telemetry_keys: tuple[str, ...] = tuple(str(k) for k in telemetry_keys_raw)
    else:
        telemetry_keys = ()

    request = L2ExecutionRequest(
        request_id=str(raw_packet["request_id"]),
        run_id=str(raw_packet["run_id"]),
        trace_root=str(raw_packet["trace_root"]),
        route_id=str(raw_packet["route_id"]),
        route_contract_ref=str(raw_packet["route_contract_ref"]),
        execution_form=str(raw_packet["execution_form"]),
        source_packet_type=source_packet_type,
        signed_packet_ref=str(raw_packet["signed_packet_ref"]),
        task_spec_ref=str(raw_packet["task_spec_ref"]),
        capability_token_ref=str(raw_packet["capability_token_ref"]),
        sandbox_envelope_ref=str(raw_packet["sandbox_envelope_ref"]),
        side_effect_class=str(raw_packet["side_effect_class"]),
        policy_hash=str(raw_packet["policy_hash"]),
        blueprint_hash=str(raw_packet["blueprint_hash"]),
        replay_key=str(raw_packet["replay_key"]),
        snapshot_manifest_ref=str(raw_packet["snapshot_manifest_ref"]),
        expected_output_contract=str(raw_packet["expected_output_contract"]),
        max_attempts=int(raw_packet.get("max_attempts", 1)),
        max_repair_count=int(raw_packet.get("max_repair_count", 1)),
        timeout_ms=int(raw_packet.get("timeout_ms", 30_000)),
        cost_budget=float(raw_packet.get("cost_budget", 0.0)),
        authority_context=authority_context,
        boundary_assertion=boundary,
        prompt_envelope_ref=str(prompt_envelope_ref) if prompt_envelope_ref else None,
        final_evidence_contract_ref=(
            str(final_evidence_contract_ref) if final_evidence_contract_ref else None
        ),
        l3_step_contract_ref=(
            str(raw_packet["l3_step_contract_ref"])
            if raw_packet.get("l3_step_contract_ref")
            else None
        ),
        ptc_execution_profile_ref=(
            str(raw_packet["ptc_execution_profile_ref"])
            if raw_packet.get("ptc_execution_profile_ref")
            else None
        ),
        script_digest=(
            str(raw_packet["script_digest"]) if raw_packet.get("script_digest") else None
        ),
        sandbox_profile_ref=(
            str(raw_packet["sandbox_profile_ref"])
            if raw_packet.get("sandbox_profile_ref")
            else None
        ),
        telemetry_keys=telemetry_keys,
        grounded=grounded,
        is_model_execution=is_model_execution,
        is_ptc_execution=is_ptc_execution,
        issuer_signature_hmac=issuer_sig,
    )
    return NormalizationResult(request=request, rejection=None)


__all__ = [
    "NormalizationResult",
    "normalize_to_request",
]
