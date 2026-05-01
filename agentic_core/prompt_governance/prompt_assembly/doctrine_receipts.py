"""Doctrine-Named Receipt Aggregators (PA.0 .. PA.7).

The Prompt Assembly child files mandate that each stage emit a specific
list of doctrine-named receipts. The internal implementation modules
(``pa0_boundary``, ``pa1_bom_resolver``, ...) emit *richer* result
objects that carry strictly more information than the doctrine receipts
require. This module provides thin, frozen, dict-shaped "doctrine
receipt" wrappers that map the rich result objects onto the names the
doctrine requires.

Each receipt is a :class:`dict` (not a dataclass) so they round-trip
cleanly through JSON and through the existing
:mod:`agentic_core.prompt_governance.prompt_assembly.observability_events`
event payloads.

Doctrine references:
    PA.0 — required_input_inventory, upstream_reference_map,
           assembly_gap_report, boundary_status_receipt
    PA.1 — bom_resolution_receipt, component_inventory,
           component_hash_map, bom_gap_report, bom_hash_receipt
    PA.2 — slot_composition_receipt, slot_authority_map,
           slot_lineage_map, slot_conflict_map,
           structured_slots_hash_receipt
    PA.3 — AssemblySecurityPassReceipt, safe_slot_payload_map,
           rejected_slot_payload_report, prompt_like_payload_report,
           safe_extraction_map, security_gap_report
    PA.4 — SlotValidationReceipt, validation_gap_report,
           authority_order_receipt, context_contract_receipt,
           tool_schema_binding_receipt, validation_hash_receipt
    PA.5 — TokenBudgetLedger, deterministic_trimming_receipt,
           stable_prefix_receipt, overflow_gap_report,
           canonical_hash_input_manifest, budget_status_receipt
    PA.6 — ProviderRenderManifest, rendered_prompt_packet,
           provider_field_mapping_receipt, provider_feature_gap_report,
           schema_render_receipt, tool_render_receipt
    PA.7 — CompiledPromptArtifact, compiled_prompt_artifact_receipt,
           manifest_hash_receipt, hmac_signature_receipt,
           l2_handoff_envelope, final_artifact_gap_report
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping, Sequence

from .assembly_statuses import (
    PAStatus,
    status_for_pa0,
    status_for_pa1,
    status_for_pa2,
    status_for_pa3,
    status_for_pa4,
    status_for_pa5,
    status_for_pa6,
    status_for_pa7,
)
from .forbidden_outputs import assert_no_forbidden

if TYPE_CHECKING:  # pragma: no cover
    from .pa0_boundary import BoundaryCheckResult
    from .pa2_slot_composition import AuthorityStack, CompositionResult
    from .pa3_c0_classifier import C0ChunkRecord, C0ClassifierResult
    from .pa3_h0_healer import H0ReentryResult
    from .pa3_u0_airlock import U0AirlockResult
    from .pa4_validation import PA4ValidationReport
    from .pa5_budget import BudgetReport
    from .pa6_provider_rendering import RenderedPayload


def _classifier_record_entry(rec: "C0ChunkRecord") -> dict[str, Any]:
    """Render a single C0 chunk record into a doctrine payload entry."""
    return {
        "chunk_id": f"{rec.source_id}:{rec.span_id}",
        "source_id": rec.source_id,
        "span_id": rec.span_id,
        "disposition": rec.disposition.value,
        "detected_patterns": list(rec.detected_patterns),
        "safe_residue_hash": rec.safe_residue_hash,
    }


def _route_classifier_entry(
    entry: dict[str, Any],
    *,
    disp: str,
    safe_payload_map: dict[str, Any],
    rejected_payload_report: dict[str, Any],
    prompt_like_payload_report: list[dict[str, Any]],
) -> None:
    if disp in {"PASS", "STRIP"}:
        safe_payload_map.setdefault("C0", []).append(entry)
    elif disp == "REJECT":
        rejected_payload_report.setdefault("C0", []).append(entry)
    else:
        prompt_like_payload_report.append(entry)


def _bucket_one_classifier_record(
    rec: "C0ChunkRecord",
    *,
    safe_payload_map: dict[str, Any],
    rejected_payload_report: dict[str, Any],
    prompt_like_payload_report: list[dict[str, Any]],
    safe_extraction_map: dict[str, Any],
) -> None:
    entry = _classifier_record_entry(rec)
    disp = rec.disposition.value
    _route_classifier_entry(
        entry,
        disp=disp,
        safe_payload_map=safe_payload_map,
        rejected_payload_report=rejected_payload_report,
        prompt_like_payload_report=prompt_like_payload_report,
    )
    if disp == "STRIP":
        safe_extraction_map[entry["chunk_id"]] = rec.safe_residue_hash


def _split_classifier_records(
    records: "tuple[C0ChunkRecord, ...] | list[C0ChunkRecord]",
    *,
    safe_payload_map: dict[str, Any],
    rejected_payload_report: dict[str, Any],
    prompt_like_payload_report: list[dict[str, Any]],
    safe_extraction_map: dict[str, Any],
) -> None:
    """Bucket classifier records into doctrine receipt containers."""
    for rec in records:
        _bucket_one_classifier_record(
            rec,
            safe_payload_map=safe_payload_map,
            rejected_payload_report=rejected_payload_report,
            prompt_like_payload_report=prompt_like_payload_report,
            safe_extraction_map=safe_extraction_map,
        )


# ---------------------------------------------------------------------------
# PA.0
# ---------------------------------------------------------------------------


def pa0_doctrine_receipt(
    result: "BoundaryCheckResult",
    *,
    upstream_refs: Mapping[str, str] | None = None,
    request_id: str = "",
    run_id: str = "",
    trace_id: str = "",
    route_id: str = "",
    plan_id: str = "",
    policy_hash: str = "",
    replay_key: str = "",
) -> dict[str, Any]:
    """Build the PA.0 doctrine receipt envelope.

    The envelope packs:
      * ``boundary_status_receipt``
      * ``required_input_inventory``
      * ``upstream_reference_map``
      * ``assembly_gap_report``
    plus the canonical PA_* status.
    """
    status = status_for_pa0(result)
    inventory = {
        "request_id_present": bool(request_id),
        "run_id_present": bool(run_id),
        "trace_id_present": bool(trace_id),
        "route_id_present": bool(route_id),
        "plan_id_present": bool(plan_id),
        "policy_hash_present": bool(policy_hash),
        "replay_key_present": bool(replay_key),
    }
    gap_report: dict[str, Any] = {
        "missing_required_refs": [k.replace("_present", "") for k, v in inventory.items() if not v],
        "fail_reason": result.fail_reason.value if result.fail_reason else None,
        "notes": list(result.notes),
    }
    receipt = {
        "stage": "PA.0",
        "doctrine_status": status.value,
        "boundary_status_receipt": {
            "status": status.value,
            "internal_status": result.status.value,
            "eligible_for_prompt_assembly": result.eligible_for_prompt_assembly,
            "fail_reason": result.fail_reason.value if result.fail_reason else None,
        },
        "required_input_inventory": inventory,
        "upstream_reference_map": dict(upstream_refs or {}),
        "assembly_gap_report": gap_report,
        "request_id": request_id,
        "run_id": run_id,
        "trace_id": trace_id,
        "route_id": route_id,
        "plan_id": plan_id,
        "policy_hash": policy_hash,
        "replay_key": replay_key,
    }
    assert_no_forbidden(receipt, label="PA.0 doctrine receipt")
    return receipt


# ---------------------------------------------------------------------------
# PA.1
# ---------------------------------------------------------------------------


def pa1_doctrine_receipt(
    *,
    component_inventory: Mapping[str, bool],
    component_hash_map: Mapping[str, str],
    missing_components: Sequence[str] = (),
    prompt_bom_id: str = "",
    bom_hash: str = "",
    request_id: str = "",
    policy_hash: str = "",
    replay_key: str = "",
) -> dict[str, Any]:
    """Build the PA.1 doctrine receipt envelope."""
    status = status_for_pa1(missing_required_components=bool(missing_components))
    receipt = {
        "stage": "PA.1",
        "doctrine_status": status.value,
        "prompt_bom_id": prompt_bom_id,
        "bom_resolution_receipt": {
            "status": status.value,
            "components_resolved": sum(1 for v in component_inventory.values() if v),
            "components_total": len(component_inventory),
        },
        "component_inventory": dict(component_inventory),
        "component_hash_map": dict(component_hash_map),
        "bom_gap_report": {
            "missing_components": list(missing_components),
        },
        "bom_hash_receipt": {
            "bom_hash": bom_hash,
        },
        "request_id": request_id,
        "policy_hash": policy_hash,
        "replay_key": replay_key,
    }
    assert_no_forbidden(receipt, label="PA.1 doctrine receipt")
    return receipt


# ---------------------------------------------------------------------------
# PA.2
# ---------------------------------------------------------------------------


def pa2_doctrine_receipt(
    composition: "CompositionResult | None",
    stack: "AuthorityStack",
    *,
    structured_slots_hash: str = "",
    request_id: str = "",
    policy_hash: str = "",
    replay_key: str = "",
) -> dict[str, Any]:
    """Build the PA.2 doctrine receipt envelope."""
    from .pa2_slot_composition import detect_authority_violations

    violations = detect_authority_violations(stack)
    entries = tuple(stack.entries)
    has_required = bool(entries) and stack.has_slot("S0")
    status = status_for_pa2(
        authority_violations=len(violations),
        has_required_slots=has_required,
    )

    slot_authority_map = {e.code: e.authority_rank for e in entries}
    slot_lineage_map = {
        e.code: composition.lineage.get(e.code, "unknown")
        if composition is not None and hasattr(composition, "lineage")
        else "upstream"
        for e in entries
    }
    slot_conflict_map = {f"violation_{i}": v for i, v in enumerate(violations)}

    receipt = {
        "stage": "PA.2",
        "doctrine_status": status.value,
        "slot_composition_receipt": {
            "status": status.value,
            "slot_count": len(entries),
            "ordered_slot_codes": [e.code for e in entries],
        },
        "slot_authority_map": slot_authority_map,
        "slot_lineage_map": slot_lineage_map,
        "slot_conflict_map": slot_conflict_map,
        "structured_slots_hash_receipt": {
            "structured_slots_hash": structured_slots_hash,
        },
        "request_id": request_id,
        "policy_hash": policy_hash,
        "replay_key": replay_key,
    }
    assert_no_forbidden(receipt, label="PA.2 doctrine receipt")
    return receipt


# ---------------------------------------------------------------------------
# PA.3
# ---------------------------------------------------------------------------


def pa3_doctrine_receipt(
    *,
    u0: "U0AirlockResult | None" = None,
    classifier: "C0ClassifierResult | None" = None,
    h0: "H0ReentryResult | None" = None,
    request_id: str = "",
    policy_hash: str = "",
    replay_key: str = "",
) -> dict[str, Any]:
    """Build the PA.3 AssemblySecurityPassReceipt envelope."""
    h0_rejected = bool(h0 and not h0.accepted)
    status = status_for_pa3(u0=u0, classifier=classifier, h0_rejected=h0_rejected)

    safe_payload_map: dict[str, Any] = {}
    rejected_payload_report: dict[str, Any] = {}
    prompt_like_payload_report: list[dict[str, Any]] = []
    safe_extraction_map: dict[str, Any] = {}

    if u0 is not None:
        safe_payload_map["U0"] = {
            "neutralized_text_hash": u0.neutralized_text_hash,
            "disposition": u0.disposition,
        }
        if u0.stripped_segments:
            rejected_payload_report["U0_stripped_segments"] = list(u0.stripped_segments)

    if classifier is not None:
        _split_classifier_records(
            classifier.records,
            safe_payload_map=safe_payload_map,
            rejected_payload_report=rejected_payload_report,
            prompt_like_payload_report=prompt_like_payload_report,
            safe_extraction_map=safe_extraction_map,
        )

    if h0 is not None:
        if h0.accepted:
            safe_payload_map["H0"] = {
                "same_policy_hash": h0.same_policy_hash,
                "same_blueprint_hash": h0.same_blueprint_hash,
                "no_scope_widening": h0.no_scope_widening,
            }
        else:
            rejected_payload_report["H0"] = {
                "rejection_reason": h0.rejection_reason or "",
            }

    security_gap_report = {
        "u0_unsafe": bool(u0 and not u0.safe_to_proceed),
        "c0_rejected_count": classifier.reject_count if classifier else 0,
        "c0_quarantined_count": classifier.quarantine_count if classifier else 0,
        "h0_rejected": h0_rejected,
    }

    receipt = {
        "stage": "PA.3",
        "doctrine_status": status.value,
        "AssemblySecurityPassReceipt": {
            "status": status.value,
            "u0_disposition": u0.disposition if u0 else None,
            "c0_total": classifier.total if classifier else 0,
            "c0_pass_count": classifier.pass_count if classifier else 0,
            "h0_is_safe": (h0.accepted if h0 else None),
        },
        "safe_slot_payload_map": safe_payload_map,
        "rejected_slot_payload_report": rejected_payload_report,
        "prompt_like_payload_report": prompt_like_payload_report,
        "safe_extraction_map": safe_extraction_map,
        "security_gap_report": security_gap_report,
        "request_id": request_id,
        "policy_hash": policy_hash,
        "replay_key": replay_key,
    }
    assert_no_forbidden(receipt, label="PA.3 doctrine receipt")
    return receipt


# ---------------------------------------------------------------------------
# PA.4
# ---------------------------------------------------------------------------


def pa4_doctrine_receipt(
    report: "PA4ValidationReport",
    *,
    validation_hash: str = "",
    request_id: str = "",
    policy_hash: str = "",
    replay_key: str = "",
) -> dict[str, Any]:
    """Build the PA.4 SlotValidationReceipt envelope."""
    status = status_for_pa4(report)
    failed_checks = [c for c in report.checks if not c.passed]

    authority_checks = [c for c in report.checks if c.check_id.startswith("authority_")]
    context_checks = [c for c in report.checks if c.check_id.startswith("ctx_")]
    schema_checks = [c for c in report.checks if c.check_id.startswith("schema_")]
    tool_checks = [
        c for c in report.checks if c.check_id.startswith("tool_") or c.check_id.startswith("tools_")
    ]

    receipt = {
        "stage": "PA.4",
        "doctrine_status": status.value,
        "SlotValidationReceipt": {
            "status": status.value,
            "checks_total": len(report.checks),
            "checks_passed": sum(1 for c in report.checks if c.passed),
            "checks_failed": len(failed_checks),
        },
        "validation_gap_report": {
            "failed_check_ids": [c.check_id for c in failed_checks],
            "failed_check_details": [{"check_id": c.check_id, "detail": c.detail} for c in failed_checks],
        },
        "authority_order_receipt": {
            "checks": [{"check_id": c.check_id, "passed": c.passed} for c in authority_checks],
        },
        "context_contract_receipt": {
            "checks": [{"check_id": c.check_id, "passed": c.passed} for c in context_checks],
        },
        "tool_schema_binding_receipt": {
            "schema_checks": [{"check_id": c.check_id, "passed": c.passed} for c in schema_checks],
            "tool_checks": [{"check_id": c.check_id, "passed": c.passed} for c in tool_checks],
        },
        "validation_hash_receipt": {
            "validation_hash": validation_hash,
        },
        "request_id": request_id,
        "policy_hash": policy_hash,
        "replay_key": replay_key,
    }
    assert_no_forbidden(receipt, label="PA.4 doctrine receipt")
    return receipt


# ---------------------------------------------------------------------------
# PA.5
# ---------------------------------------------------------------------------


def pa5_doctrine_receipt(
    report: "BudgetReport",
    *,
    canonical_hash_input_manifest: Mapping[str, Any] | None = None,
    stable_prefix_hash: str = "",
    request_id: str = "",
    policy_hash: str = "",
    replay_key: str = "",
) -> dict[str, Any]:
    """Build the PA.5 TokenBudgetLedger envelope."""
    status = status_for_pa5(report)
    trimmed = list(report.trim_actions)

    receipt = {
        "stage": "PA.5",
        "doctrine_status": status.value,
        "TokenBudgetLedger": {
            "status": status.value,
            "input_token_estimate": report.input_token_estimate,
            "reserved_output_tokens": report.reserved_output_tokens,
            "reserved_schema_tokens": report.reserved_schema_tokens,
            "reserved_tool_tokens": report.reserved_tool_tokens,
            "model_context_window": report.model_context_window,
            "overflow_status": report.overflow_status.value,
        },
        "deterministic_trimming_receipt": {
            "trim_actions": trimmed,
            "dropped_items_with_reasons": list(report.dropped_items_with_reasons),
            "after_token_estimate": report.input_token_estimate,
        },
        "stable_prefix_receipt": {
            "stable_prefix_hash": stable_prefix_hash,
        },
        "overflow_gap_report": {
            "overflow_status": report.overflow_status.value,
            "can_dispatch": report.can_dispatch,
        },
        "canonical_hash_input_manifest": dict(canonical_hash_input_manifest or {}),
        "budget_status_receipt": {
            "status": status.value,
            "can_dispatch": report.can_dispatch,
        },
        "request_id": request_id,
        "policy_hash": policy_hash,
        "replay_key": replay_key,
    }
    assert_no_forbidden(receipt, label="PA.5 doctrine receipt")
    return receipt


# ---------------------------------------------------------------------------
# PA.6
# ---------------------------------------------------------------------------


def pa6_doctrine_receipt(
    payload: "RenderedPayload | None",
    *,
    provider_lane: str,
    rendered: bool,
    missing_provider_feature: bool = False,
    schema_render_failed: bool = False,
    tool_render_failed: bool = False,
    render_hash: str = "",
    request_id: str = "",
    policy_hash: str = "",
    replay_key: str = "",
) -> dict[str, Any]:
    """Build the PA.6 ProviderRenderManifest envelope."""
    status = status_for_pa6(
        rendered=rendered,
        missing_provider_feature=missing_provider_feature,
        schema_render_failed=schema_render_failed,
        tool_render_failed=tool_render_failed,
    )

    rendered_packet: dict[str, Any] = {}
    if payload is not None:
        rendered_packet = {
            "provider_lane": provider_lane,
            "system_field_present": bool(getattr(payload, "system_text", "")),
            "user_field_present": bool(getattr(payload, "user_text", "")),
            "tools_field_present": bool(getattr(payload, "tools", ())),
            "response_schema_present": bool(getattr(payload, "response_schema", None)),
        }

    receipt = {
        "stage": "PA.6",
        "doctrine_status": status.value,
        "ProviderRenderManifest": {
            "status": status.value,
            "provider_lane": provider_lane,
            "render_hash": render_hash,
            "render_warnings": [],
        },
        "rendered_prompt_packet": rendered_packet,
        "provider_field_mapping_receipt": {
            "provider_lane": provider_lane,
            "rendered": rendered,
        },
        "provider_feature_gap_report": {
            "missing_provider_feature": missing_provider_feature,
            "schema_render_failed": schema_render_failed,
            "tool_render_failed": tool_render_failed,
        },
        "schema_render_receipt": {
            "ok": not schema_render_failed,
        },
        "tool_render_receipt": {
            "ok": not tool_render_failed,
        },
        "request_id": request_id,
        "policy_hash": policy_hash,
        "replay_key": replay_key,
    }
    assert_no_forbidden(receipt, label="PA.6 doctrine receipt")
    return receipt


# ---------------------------------------------------------------------------
# PA.7
# ---------------------------------------------------------------------------


def pa7_doctrine_receipt(
    *,
    artifact_id: str,
    manifest_hash: str,
    hmac_sig: str,
    signed: bool,
    handoff_ready: bool,
    signed_fields: Sequence[str] = (),
    signature_algorithm: str = "HMAC-SHA256",
    signing_key_ref: str = "",
    l2_handoff_envelope: Mapping[str, Any] | None = None,
    final_artifact_gap_reasons: Sequence[str] = (),
    request_id: str = "",
    run_id: str = "",
    trace_id: str = "",
    route_id: str = "",
    plan_id: str = "",
    policy_hash: str = "",
    replay_key: str = "",
) -> dict[str, Any]:
    """Build the PA.7 CompiledPromptArtifact + L2 handoff envelope."""
    status = status_for_pa7(
        signed=signed,
        manifest_hash=manifest_hash,
        handoff_ready=handoff_ready,
    )

    receipt = {
        "stage": "PA.7",
        "doctrine_status": status.value,
        "CompiledPromptArtifact": {
            "compiled_prompt_artifact_id": artifact_id,
            "manifest_hash": manifest_hash,
            "hmac_sig": hmac_sig,
            "artifact_status": status.value,
            "request_id": request_id,
            "run_id": run_id,
            "trace_id": trace_id,
            "route_id": route_id,
            "plan_id": plan_id,
            "policy_hash": policy_hash,
            "replay_key": replay_key,
        },
        "compiled_prompt_artifact_receipt": {
            "status": status.value,
            "signed": signed,
            "handoff_ready": handoff_ready,
        },
        "manifest_hash_receipt": {
            "manifest_hash": manifest_hash,
            "present": bool(manifest_hash),
        },
        "hmac_signature_receipt": {
            "signature_algorithm": signature_algorithm,
            "signing_key_ref": signing_key_ref,
            "signed_fields": list(signed_fields),
            "hmac_sig_present": bool(hmac_sig),
        },
        "l2_handoff_envelope": dict(l2_handoff_envelope or {}),
        "final_artifact_gap_report": {
            "reasons": list(final_artifact_gap_reasons),
            "signed": signed,
            "manifest_hash_present": bool(manifest_hash),
            "handoff_ready": handoff_ready,
        },
    }
    assert_no_forbidden(receipt, label="PA.7 doctrine receipt")
    return receipt


# ---------------------------------------------------------------------------
# Aggregate
# ---------------------------------------------------------------------------


def aggregate_doctrine_status(receipts: Sequence[Mapping[str, Any]]) -> PAStatus:
    """Compute the worst-case (most-blocking) doctrine status across stages.

    Used by the pipeline to publish a single top-level status when the
    caller wants one summary value. The mapping below is doctrine-aware:
    a budget-overflow at PA.5 is more blocking than a render gap at
    PA.6, so the function does not just pick the *latest* stage status —
    it picks the most-blocking one.
    """
    severity = {
        # success / pass-through
        PAStatus.PA_READY: 0,
        PAStatus.PA_BOM_RESOLVED: 0,
        PAStatus.PA_SLOTS_COMPOSED: 0,
        PAStatus.PA_SECURITY_PASS: 0,
        PAStatus.PA_SLOT_CONTRACT_VALID: 0,
        PAStatus.PA_BUDGET_FIT: 0,
        PAStatus.PA_BUDGET_TRIMMED: 1,
        PAStatus.PA_RENDERED: 0,
        PAStatus.PA_ARTIFACT_SIGNED: 0,
        PAStatus.PA_L2_HANDOFF_READY: 0,
        PAStatus.PA_SAFE_EXTRACTION_PARTIAL: 1,
        # gaps
        PAStatus.PA_BOM_GAP: 3,
        PAStatus.PA_SLOT_COMPOSITION_GAP: 3,
        PAStatus.PA_AUTHORITY_CONFLICT: 3,
        PAStatus.PA_SECURITY_GAP: 2,
        PAStatus.PA_SLOT_CONTRACT_INVALID: 3,
        PAStatus.PA_CONTEXT_CONTRACT_GAP: 3,
        PAStatus.PA_AUTHORITY_INVERSION_GAP: 3,
        PAStatus.PA_SCHEMA_BINDING_GAP: 3,
        PAStatus.PA_TOOL_BINDING_GAP: 3,
        PAStatus.PA_RENDER_GAP: 3,
        PAStatus.PA_PROVIDER_FEATURE_GAP: 3,
        PAStatus.PA_SCHEMA_RENDER_GAP: 3,
        PAStatus.PA_TOOL_RENDER_GAP: 3,
        PAStatus.PA_ARTIFACT_NOT_SIGNED: 4,
        PAStatus.PA_SIGNATURE_GAP: 4,
        PAStatus.PA_MANIFEST_HASH_GAP: 4,
        PAStatus.PA_L2_HANDOFF_GAP: 4,
        # hardest blockers
        PAStatus.PA_INPUT_INCOMPLETE: 5,
        PAStatus.PA_BOUNDARY_MISMATCH: 5,
        PAStatus.PA_SLOT_PAYLOAD_REJECTED: 5,
        PAStatus.PA_BUDGET_OVERFLOW: 5,
        PAStatus.PA_REQUIRES_UPSTREAM_REPAIR: 6,
    }
    return _select_worst_status(receipts, severity)


def _select_worst_status(
    receipts: Sequence[Mapping[str, Any]],
    severity: Mapping[PAStatus, int],
) -> PAStatus:
    worst: PAStatus = PAStatus.PA_READY
    worst_score = -1
    for entry in receipts:
        status = _parse_status(entry.get("doctrine_status"))
        if status is None:
            continue
        score = severity.get(status, 0)
        if score > worst_score:
            worst_score = score
            worst = status
    return worst


def _parse_status(raw: Any) -> PAStatus | None:
    if raw is None:
        return None
    try:
        return PAStatus(raw)
    except ValueError:  # guardian: allow-return-none-swallow -- PAStatus enum coercion: unknown status string; None signals invalid status to caller
        return None


__all__ = [
    "aggregate_doctrine_status",
    "pa0_doctrine_receipt",
    "pa1_doctrine_receipt",
    "pa2_doctrine_receipt",
    "pa3_doctrine_receipt",
    "pa4_doctrine_receipt",
    "pa5_doctrine_receipt",
    "pa6_doctrine_receipt",
    "pa7_doctrine_receipt",
]
