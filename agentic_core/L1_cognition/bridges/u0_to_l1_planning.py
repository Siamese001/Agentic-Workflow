"""U0 ValidatedRequest → L1 v6 ParsedRequestInput bridge.

The existing :mod:`agentic_core.L1_cognition.bridges.u0_to_l1_plan` is a
v4-era adapter that turns a :class:`ValidatedRequest` into the legacy
:class:`L1PlanContract` (note: a totally different contract that lives
in the L0 retrieval surface).

This module is the v6 counterpart: it produces a
:class:`agentic_core.L1_cognition.planning.ParsedRequestInput` so the v6
six-stage pipeline at
:func:`agentic_core.L1_cognition.planning.run_l1_planning` can be
invoked from the U0 ingress without the caller having to reach into the
v6 contracts module directly.

Mapping rules (deterministic, read-only):

============================  ==============================================
ParsedRequestInput field      Source on ValidatedRequest
============================  ==============================================
request_id                    vr.request_id
session_id                    vr.session_id
trace_root                    vr.trace_root
caller_scope_baseline         vr.caller_scope_baseline
normalized_user_payload       vr.normalized_payload or ""
visible_conversation_context  ()  — caller may attach later
user_constraints              ()  — caller may attach later
system_constraints            ()  — caller may attach later
known_artifact_refs           ()  — caller may attach later
uploaded_object_refs          attachments resolved via vr.attachment_manifest
                              (fallback: empty if shell carries no surface)
source_handles                (vr.source_channel,)  if non-empty
request_freshness_hints       (vr.intake_warnings)  — re-used as soft hints
output_channel_expectations   ()
policy_hash_observed          intake_manifest_hash, fallback empty string
instruction_hash_observed     correlation_receipt_ref, fallback empty
source_envelope_id            ingress_replay_seed_ref, fallback empty
validated_request             vr  (carry the original by reference)
rejected_request_summary      None (only set on the rejected path)
============================  ==============================================

Defense-in-depth: the bridge re-asserts U0's invariants
(``vr.permitted_next_layer == "L1"`` and ``vr.downstream_authority == "none"``)
before constructing the v6 input. Any violation raises
:class:`ValueError` immediately rather than letting bad state flow into
the planner.
"""

from __future__ import annotations

from typing import Any

from agentic_core.L0_routing.intake.validated_request import ValidatedRequest
from agentic_core.L1_cognition.planning.contracts import (
    L1ContractViolation,
    ParsedRequestInput,
)

__all__ = [
    "validated_request_to_parsed_request_input",
    "rejected_request_to_parsed_request_input",
]


def _safe_get(obj: Any, name: str, default: str = "") -> str:
    val = getattr(obj, name, default)
    return val if isinstance(val, str) else default


def validated_request_to_parsed_request_input(
    vr: ValidatedRequest,
    *,
    visible_conversation_context: tuple = (),
    user_constraints: tuple = (),
    system_constraints: tuple = (),
    known_artifact_refs: tuple = (),
    output_channel_expectations: tuple = (),
) -> ParsedRequestInput:
    """Translate a passing :class:`ValidatedRequest` into a v6 input packet.

    Args:
        vr: a successfully-stamped ValidatedRequest from the U0 intake
            pipeline. ``vr.permitted_next_layer`` MUST be ``"L1"``.
        visible_conversation_context: caller-supplied context list (e.g.
            recent turns) — empty by default; the L1 v6 layer treats it
            as scoped, never global.
        user_constraints / system_constraints / known_artifact_refs /
        output_channel_expectations: optional hint-tuples passed through
        to the v6 input. Default empty.

    Raises:
        ValueError: if the request was not authorized for L1.
        L1ContractViolation: if the resulting ParsedRequestInput fails
            the v6 contract validation.
    """
    if vr.permitted_next_layer != "L1":
        raise ValueError(
            "validated_request_to_parsed_request_input: "
            f"vr.permitted_next_layer must be 'L1', got {vr.permitted_next_layer!r}"
        )
    if vr.downstream_authority != "none":
        raise ValueError(
            "validated_request_to_parsed_request_input: "
            "vr.downstream_authority must be 'none' (U0 never grants authority)."
        )

    # Resolve uploaded refs from the attachment manifest shell when present.
    uploaded: tuple[str, ...] = ()
    manifest = getattr(vr, "attachment_manifest", None)
    if manifest is not None:
        # AttachmentManifestShell may expose a ``refs`` or ``items`` tuple.
        for fname in ("refs", "items", "manifest_refs"):
            val = getattr(manifest, fname, None)
            if val and hasattr(val, "__iter__") and not isinstance(val, (str, bytes)):
                uploaded = tuple(str(x) for x in val)
                break

    source_handles: tuple[str, ...] = ()
    if vr.source_channel:
        source_handles = (vr.source_channel,)

    return ParsedRequestInput(
        request_id=vr.request_id,
        session_id=vr.session_id,
        trace_root=vr.trace_root,
        caller_scope_baseline=vr.caller_scope_baseline,
        normalized_user_payload=vr.normalized_payload or "",
        visible_conversation_context=tuple(visible_conversation_context),
        user_constraints=tuple(user_constraints),
        system_constraints=tuple(system_constraints),
        known_artifact_refs=tuple(known_artifact_refs),
        uploaded_object_refs=uploaded,
        source_handles=source_handles,
        request_freshness_hints=tuple(vr.intake_warnings),
        output_channel_expectations=tuple(output_channel_expectations),
        policy_hash_observed=_safe_get(vr, "intake_manifest_hash"),
        instruction_hash_observed=_safe_get(vr, "correlation_receipt_ref"),
        source_envelope_id=_safe_get(vr, "ingress_replay_seed_ref"),
        validated_request=vr,
        rejected_request_summary=None,
    )


def rejected_request_to_parsed_request_input(
    rejected_summary: Any,
    *,
    request_id: str,
    session_id: str,
    trace_root: str,
    caller_scope_baseline: str,
    policy_hash_observed: str = "",
    instruction_hash_observed: str = "",
    source_envelope_id: str = "",
) -> ParsedRequestInput:
    """Build a v6 input from a rejected-request summary path.

    Some L1 deployments still feed the planner a rejected-request summary
    so the planner can emit a fallback / clarify recommendation rather
    than discarding the slip silently. This helper makes that path
    explicit and validates the v6 contract invariant
    (validated_request OR rejected_request_summary must be present).
    """
    if rejected_summary is None:
        raise L1ContractViolation(
            "rejected_request_to_parsed_request_input: rejected_summary cannot be None"
        )
    return ParsedRequestInput(
        request_id=request_id,
        session_id=session_id,
        trace_root=trace_root,
        caller_scope_baseline=caller_scope_baseline,
        normalized_user_payload="",
        policy_hash_observed=policy_hash_observed,
        instruction_hash_observed=instruction_hash_observed,
        source_envelope_id=source_envelope_id,
        validated_request=None,
        rejected_request_summary=rejected_summary,
    )
