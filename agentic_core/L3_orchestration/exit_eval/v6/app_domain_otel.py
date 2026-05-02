"""OTEL attribute helpers for app-domain contract refs (W6).

Two surfaces:

1. :func:`build_app_domain_span_attributes` — given an ``ExitReviewPacket``
   (or an equivalent ref bundle), returns a flat dict of OTEL attributes
   with the canonical ``app.*`` key namespace. Used by any span emission
   site that wants to carry app-contract provenance.

2. :func:`build_app_domain_proof_packet_section` — returns a dict of
   proof-bundle fields per plan §P6.2 required schema. Slotted into the
   proof bundle emitted by ``apps_shared/proof/proof_runner.py``.

Plan: ``.windsurf/plans/apps-domain-contract-fortknox-c4d8e2.md`` §W6.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping, Optional


# Canonical span-attribute key namespace.
APP_DOMAIN_SPAN_KEYS = (
    "app.id",
    "app.task_class",
    "app.domain_contract_ref",
    "app.domain_contract_digest",
    "app.input_contract_ref",
    "app.output_schema_ref",
    "app.rubric_ref",
    "app.threshold_profile_ref",
    "app.grader_roster_ref",
    "app.retrieval_profile_ref",
    "app.prompt_profile_ref",
    "app.capability_profile_ref",
    "app.route_profile_ref",
    "app.orchestration_profile_ref",
    "app.l4_record_refs",
    "exit.x3_disposition",
    "exit.app_specific_eval_passed",
    "uwg.registration_receipt_ref",
    "l4.record_refs",
)


def build_app_domain_span_attributes(
    *,
    app_id: str = "",
    task_class: str = "",
    domain_contract_ref: str = "",
    domain_contract_digest: str = "",
    input_contract_ref: str = "",
    output_schema_ref: str = "",
    rubric_ref: str = "",
    threshold_profile_ref: str = "",
    grader_roster_ref: str = "",
    retrieval_profile_ref: str = "",
    prompt_profile_ref: str = "",
    capability_profile_ref: str = "",
    route_profile_ref: str = "",
    orchestration_profile_ref: str = "",
    l4_record_refs: "tuple[str, ...] | list[str]" = (),
    x3_disposition: str = "",
    app_specific_eval_passed: Optional[bool] = None,
    uwg_registration_receipt_ref: str = "",
) -> Dict[str, Any]:
    """Build a flat OTEL attributes dict for a span.

    Empty strings / empty collections are omitted so spans stay compact
    when the route wasn't app-bound. Booleans are emitted as ``True`` /
    ``False`` — the OTEL exporter serializes per its own contract.
    """
    out: Dict[str, Any] = {}
    if app_id:
        out["app.id"] = app_id
    if task_class:
        out["app.task_class"] = task_class
    if domain_contract_ref:
        out["app.domain_contract_ref"] = domain_contract_ref
    if domain_contract_digest:
        out["app.domain_contract_digest"] = domain_contract_digest
    if input_contract_ref:
        out["app.input_contract_ref"] = input_contract_ref
    if output_schema_ref:
        out["app.output_schema_ref"] = output_schema_ref
    if rubric_ref:
        out["app.rubric_ref"] = rubric_ref
    if threshold_profile_ref:
        out["app.threshold_profile_ref"] = threshold_profile_ref
    if grader_roster_ref:
        out["app.grader_roster_ref"] = grader_roster_ref
    if retrieval_profile_ref:
        out["app.retrieval_profile_ref"] = retrieval_profile_ref
    if prompt_profile_ref:
        out["app.prompt_profile_ref"] = prompt_profile_ref
    if capability_profile_ref:
        out["app.capability_profile_ref"] = capability_profile_ref
    if route_profile_ref:
        out["app.route_profile_ref"] = route_profile_ref
    if orchestration_profile_ref:
        out["app.orchestration_profile_ref"] = orchestration_profile_ref
    if l4_record_refs:
        # OTEL attrs are typically str/int/bool; join refs into a comma-sep
        # string for dashboards, and also keep the list for structured
        # exporters that accept sequences.
        out["app.l4_record_refs"] = list(l4_record_refs)
        out["l4.record_refs"] = ",".join(l4_record_refs)
    if x3_disposition:
        out["exit.x3_disposition"] = x3_disposition
    if app_specific_eval_passed is not None:
        out["exit.app_specific_eval_passed"] = bool(app_specific_eval_passed)
    if uwg_registration_receipt_ref:
        out["uwg.registration_receipt_ref"] = uwg_registration_receipt_ref
    return out


def build_app_domain_span_attributes_from_packet(packet: Any) -> Dict[str, Any]:
    """Convenience: read the app.* fields off an :class:`ExitReviewPacket`."""
    kwargs = {
        "app_id": getattr(packet, "app_id", ""),
        "task_class": getattr(packet, "task_class", ""),
        "domain_contract_ref": getattr(packet, "domain_contract_ref", ""),
        "domain_contract_digest": getattr(packet, "resolved_domain_contract_digest", ""),
        "input_contract_ref": getattr(packet, "input_contract_ref", ""),
        "output_schema_ref": getattr(packet, "output_schema_ref", ""),
        "rubric_ref": getattr(packet, "rubric_ref", ""),
        "threshold_profile_ref": getattr(packet, "threshold_profile_ref", ""),
        "grader_roster_ref": getattr(packet, "grader_roster_ref", ""),
        "retrieval_profile_ref": getattr(packet, "retrieval_profile_ref", ""),
        "prompt_profile_ref": getattr(packet, "prompt_profile_ref", ""),
        "capability_profile_ref": getattr(packet, "capability_profile_ref", ""),
        "route_profile_ref": getattr(packet, "route_profile_ref", ""),
        "l4_record_refs": tuple(getattr(packet, "app_contract_l4_record_refs", ()) or ()),
    }
    eval_block = getattr(packet, "app_specific_eval", None) or {}
    if isinstance(eval_block, dict) and "passed" in eval_block:
        kwargs["app_specific_eval_passed"] = bool(eval_block.get("passed"))
    return build_app_domain_span_attributes(**kwargs)


def build_app_domain_proof_packet_section(
    *,
    app_id: str = "",
    task_class: str = "",
    app_domain_contract_ref: str = "",
    l4_domain_contract_record_ref: str = "",
    uwg_registration_receipt_ref: str = "",
    resolved_l4_record_refs: "tuple[str, ...] | list[str]" = (),
    route_contract_ref: str = "",
    final_evidence_contract_ref: str = "",
    compiled_prompt_artifact_ref: str = "",
    sealed_l2_artifact_ref: str = "",
    exit_review_packet_ref: str = "",
    x1_app_specific_gate_results: Optional[Mapping[str, str]] = None,
    x2_aggregation_result: str = "",
    x3_disposition: str = "",
    runtime_exhaust_bundle_ref: str = "",
    otel_trace_ref: str = "",
    replay_receipt_ref: str = "",
    no_bypass_receipt_ref: str = "",
) -> Dict[str, Any]:
    """Build the ``app_domain_contract`` section of the proof bundle.

    Field set follows plan §P6 required proof bundle fields verbatim.
    Unset fields are omitted. Slots into the apps_shared/proof/proof_runner
    bundle output.
    """
    out: Dict[str, Any] = {}
    if app_id:
        out["app_id"] = app_id
    if task_class:
        out["task_class"] = task_class
    if app_domain_contract_ref:
        out["app_domain_contract_ref"] = app_domain_contract_ref
    if l4_domain_contract_record_ref:
        out["l4_domain_contract_record_ref"] = l4_domain_contract_record_ref
    if uwg_registration_receipt_ref:
        out["uwg_registration_receipt_ref"] = uwg_registration_receipt_ref
    if resolved_l4_record_refs:
        out["resolved_l4_record_refs"] = list(resolved_l4_record_refs)
    if route_contract_ref:
        out["route_contract_ref"] = route_contract_ref
    if final_evidence_contract_ref:
        out["final_evidence_contract_ref"] = final_evidence_contract_ref
    if compiled_prompt_artifact_ref:
        out["compiled_prompt_artifact_ref"] = compiled_prompt_artifact_ref
    if sealed_l2_artifact_ref:
        out["sealed_l2_artifact_ref"] = sealed_l2_artifact_ref
    if exit_review_packet_ref:
        out["exit_review_packet_ref"] = exit_review_packet_ref
    if x1_app_specific_gate_results:
        out["x1_app_specific_gate_results"] = dict(x1_app_specific_gate_results)
    if x2_aggregation_result:
        out["x2_aggregation_result"] = x2_aggregation_result
    if x3_disposition:
        out["x3_disposition"] = x3_disposition
    if runtime_exhaust_bundle_ref:
        out["runtime_exhaust_bundle_ref"] = runtime_exhaust_bundle_ref
    if otel_trace_ref:
        out["otel_trace_ref"] = otel_trace_ref
    if replay_receipt_ref:
        out["replay_receipt_ref"] = replay_receipt_ref
    if no_bypass_receipt_ref:
        out["no_bypass_receipt_ref"] = no_bypass_receipt_ref
    return out


__all__ = [
    "APP_DOMAIN_SPAN_KEYS",
    "build_app_domain_span_attributes",
    "build_app_domain_span_attributes_from_packet",
    "build_app_domain_proof_packet_section",
]
