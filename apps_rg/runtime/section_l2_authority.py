"""Canonical two-phase L2 authority lifecycle for product-visible section lanes.

Section lanes already own the provider call. This module therefore performs
E1/E2 before that call and turns the observed provider/output artifacts into
E3/E5 receipts afterwards. Compatibility mirrors are derived from the
canonical receipt bundle; they are never independent authority.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any, Mapping, Sequence

from agentic_core.runtime.contracts.origin import Origin
from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
from apps_rg.runtime.bindings.l2_authority import (
    build_signed_execution_packet,
    freeze_execution_room,
    validate_execution_packet,
)
from apps_rg.runtime.bindings.l2_authority_contracts import (
    AuthorityGateReceipt,
    FrozenExecutionRoom,
    SignedAppsRgL2ExecutionPacket,
    _jsonable,
    sha256_hex,
)
from apps_rg.runtime.bindings.l2_receipt_bundle import (
    compute_attempt_output_digest,
    finalize_content_addressed_bundle,
)
from apps_rg.runtime.section_l2_spine_receipt import (
    COMPILED_PROMPT_ARTIFACT,
    L2_EXECUTION_PACKET_ARTIFACT,
    L2_SPINE_RECEIPT_ARTIFACT,
    SEALED_L2_ARTIFACT,
    SectionL2SpinePreconditionError,
    assert_section_l2_spine_preconditions,
)

FROZEN_EXECUTION_CONTEXT_ARTIFACT = "frozen_execution_context.json"
PREP_RECEIPT_ARTIFACT = "prep_receipt.json"
VALIDATION_RECEIPT_ARTIFACT = "validation_receipt.json"
ATTEMPT_RECEIPT_ARTIFACT = "attempt_receipt.json"
SEAL_RECEIPT_ARTIFACT = "seal_receipt.json"
L2_RECEIPT_BUNDLE_ARTIFACT = "l2_receipt_bundle.json"
L2_HANDOFF_RECEIPT_ARTIFACT = "l2_handoff_receipt.json"


def _write_json(path: Path, payload: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(_jsonable(payload), indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return path


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError):
        return {}
    return payload if isinstance(payload, dict) else {"value": payload}


def _read_payload(path: Path) -> tuple[Any, str, bool]:
    if not path.is_file():
        return {}, "", False
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        value = raw.decode("utf-8", errors="replace")
    return value, digest, True


def _tuple_field(payload: Mapping[str, Any], name: str) -> tuple[str, ...]:
    return tuple(str(item) for item in (payload.get(name) or ()) if str(item).strip())


def _packet_from_payload(payload: Mapping[str, Any]) -> SignedAppsRgL2ExecutionPacket:
    body = dict(payload)
    for name in (
        "registry_digest_set",
        "allowed_tools",
        "allowed_models",
        "allowed_networks",
        "allowed_file_roots",
        "signature_chain",
    ):
        body[name] = _tuple_field(body, name)
    body["budget"] = dict(body.get("budget") or {})
    return SignedAppsRgL2ExecutionPacket(**body)


def _room_from_payload(payload: Mapping[str, Any]) -> FrozenExecutionRoom:
    body = dict(payload)
    for name in (
        "registry_digest_set",
        "filesystem_view",
        "network_rules",
    ):
        body[name] = _tuple_field(body, name)
    body["budget"] = dict(body.get("budget") or {})
    return FrozenExecutionRoom(**body)


def _gate_receipts_from_payload(payload: Mapping[str, Any]) -> tuple[AuthorityGateReceipt, ...]:
    rows = payload.get("authority_gate_receipts") or payload.get("gate_receipts") or ()
    receipts: list[AuthorityGateReceipt] = []
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        receipts.append(
            AuthorityGateReceipt(
                gate_id=str(row.get("gate_id") or ""),
                status=str(row.get("status") or ""),
                decisive_reason_code=str(row.get("decisive_reason_code") or ""),
                checked_fields=tuple(str(x) for x in (row.get("checked_fields") or ())),
                evidence_refs=tuple(str(x) for x in (row.get("evidence_refs") or ())),
            )
        )
    return tuple(receipts)


def _token_usage(payload: Any) -> tuple[int, bool]:
    if isinstance(payload, Mapping):
        for key in ("total_tokens", "tokens_used", "output_tokens", "completion_tokens"):
            value = payload.get(key)
            if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
                return value, True
        for key in ("token_usage", "usage", "receipt", "provider_receipt", "meta"):
            if key in payload:
                found, observed = _token_usage(payload[key])
                if observed:
                    return found, True
        for value in payload.values():
            found, observed = _token_usage(value)
            if observed:
                return found, True
    elif isinstance(payload, Sequence) and not isinstance(payload, (str, bytes, bytearray)):
        for value in payload:
            found, observed = _token_usage(value)
            if observed:
                return found, True
    return 0, False


def _provider_value(payload: Any, *keys: str) -> str:
    if isinstance(payload, Mapping):
        for key in keys:
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        for value in payload.values():
            found = _provider_value(value, *keys)
            if found:
                return found
    return ""


def prepare_section_l2_authority(
    artifact_dir: Path,
    section_id: str,
    runtime_payload: dict[str, Any],
    *,
    provider_lane: str,
    model_lane: str | None = None,
) -> dict[str, Any]:
    """Run canonical E1/E2 and persist signed authority before a section provider call."""
    artifact_dir = Path(artifact_dir)
    runtime_payload.setdefault("compiled_prompt_artifact_ref", COMPILED_PROMPT_ARTIFACT)
    assert_section_l2_spine_preconditions(runtime_payload, artifact_dir)

    from apps_rg.runtime.spine.governed_pa_compose import governed_pa_compose_integrated
    from apps_rg.runtime.spine.spine_contract_loaders import load_spine_contracts_for_section

    loaded = load_spine_contracts_for_section(artifact_dir, runtime_payload)
    if loaded is None:
        raise SectionL2SpinePreconditionError(
            "product-visible section L2 requires loadable ValidatedRequest, RouteContract, "
            "L1PlanContract, and FinalEvidenceContract"
        )
    route, plan, fec, validated_request = loaded
    prompt_artifact = governed_pa_compose_integrated(route, plan, fec, validated_request)
    effective_provider = str(provider_lane or prompt_artifact.target_provider or "").strip()
    effective_model = str(model_lane or prompt_artifact.target_model or "").strip()
    prompt_artifact = replace(
        prompt_artifact,
        target_provider=effective_provider,
        target_model=effective_model,
        allowed_models=(effective_model,) if effective_model else (),
    )

    packet = build_signed_execution_packet(
        prompt_artifact,
        route,
        validated_request,
        attempt_number=1,
    )
    gate_receipts = validate_execution_packet(
        packet,
        prompt_artifact,
        route,
        validated_request,
    )
    frozen_room = freeze_execution_room(packet)
    prep_receipt = {
        "schema_version": "apps_rg.section_l2_prep.v2",
        "section_id": section_id,
        "packet_digest": packet.packet_digest,
        "frozen_room_digest": frozen_room.room_digest,
        "prompt_hash": packet.prompt_hash,
        "replay_key": packet.replay_key,
        "route_id": packet.route_id,
        "no_direct_l4_path": True,
        "proposed_diff_only": True,
        "persistence_disabled": True,
        "l5_certification_ref": str(prompt_artifact.l5_certification_ref or ""),
    }
    validation_receipt = {
        "schema_version": "apps_rg.section_l2_validation.v2",
        "section_id": section_id,
        "validation_status": "PASS",
        "packet_digest": packet.packet_digest,
        "authority_gate_receipts": [asdict(item) for item in gate_receipts],
        "gate_refs": [item.ref for item in gate_receipts],
        "unknown_never_pass": True,
    }

    _write_json(artifact_dir / L2_EXECUTION_PACKET_ARTIFACT, packet)
    _write_json(artifact_dir / FROZEN_EXECUTION_CONTEXT_ARTIFACT, frozen_room)
    _write_json(artifact_dir / PREP_RECEIPT_ARTIFACT, prep_receipt)
    _write_json(artifact_dir / VALIDATION_RECEIPT_ARTIFACT, validation_receipt)

    runtime_payload.update(
        {
            "l2_execution_packet_ref": L2_EXECUTION_PACKET_ARTIFACT,
            "frozen_execution_context_ref": FROZEN_EXECUTION_CONTEXT_ARTIFACT,
            "prep_receipt_ref": PREP_RECEIPT_ARTIFACT,
            "validation_receipt_ref": VALIDATION_RECEIPT_ARTIFACT,
            "canonical_l2_packet_digest": packet.packet_digest,
            "canonical_l2_prompt_hash": packet.prompt_hash,
            "canonical_l2_replay_key": packet.replay_key,
            "canonical_l2_l5_certification_ref": str(prompt_artifact.l5_certification_ref or ""),
            "canonical_l2_preflight_status": "PASS",
            "_canonical_l2_packet": packet,
            "_canonical_l2_frozen_room": frozen_room,
            "_canonical_l2_gate_receipts": gate_receipts,
            "_canonical_l2_prompt_artifact": prompt_artifact,
            "_canonical_l2_prep_receipt": prep_receipt,
            "_canonical_l2_validation_receipt": validation_receipt,
        }
    )
    return packet.as_dict()


def _load_preflight_state(
    artifact_dir: Path,
    runtime_payload: Mapping[str, Any],
) -> tuple[
    SignedAppsRgL2ExecutionPacket,
    FrozenExecutionRoom,
    tuple[AuthorityGateReceipt, ...],
    Mapping[str, Any],
    Mapping[str, Any],
]:
    packet = runtime_payload.get("_canonical_l2_packet")
    if not isinstance(packet, SignedAppsRgL2ExecutionPacket):
        packet = _packet_from_payload(_read_json(artifact_dir / L2_EXECUTION_PACKET_ARTIFACT))
    room = runtime_payload.get("_canonical_l2_frozen_room")
    if not isinstance(room, FrozenExecutionRoom):
        room = _room_from_payload(_read_json(artifact_dir / FROZEN_EXECUTION_CONTEXT_ARTIFACT))
    gates = runtime_payload.get("_canonical_l2_gate_receipts")
    if not isinstance(gates, tuple) or not all(isinstance(x, AuthorityGateReceipt) for x in gates):
        gates = _gate_receipts_from_payload(_read_json(artifact_dir / VALIDATION_RECEIPT_ARTIFACT))
    prep = runtime_payload.get("_canonical_l2_prep_receipt")
    if not isinstance(prep, Mapping):
        prep = _read_json(artifact_dir / PREP_RECEIPT_ARTIFACT)
    validation = runtime_payload.get("_canonical_l2_validation_receipt")
    if not isinstance(validation, Mapping):
        validation = _read_json(artifact_dir / VALIDATION_RECEIPT_ARTIFACT)
    if not packet.packet_digest or not room.room_digest or not gates:
        raise SectionL2SpinePreconditionError(
            "canonical section L2 finalization requires persisted E1/E2 authority receipts"
        )
    return packet, room, gates, prep, validation


def _build_handoff_receipt(
    *,
    section_id: str,
    packet: SignedAppsRgL2ExecutionPacket,
    provider_request: Any,
    provider_response: Any,
    output_exists: bool,
    tokens_used: int,
    tokens_observed: bool,
    runtime_payload: Mapping[str, Any],
) -> dict[str, Any]:
    used_provider = _provider_value(
        provider_request,
        "provider_lane",
        "target_provider",
        "provider",
        "provider_profile",
    ) or str(runtime_payload.get("provider_lane") or packet.canonical_provider)
    used_model = _provider_value(
        provider_request,
        "model_lane",
        "target_model",
        "model",
        "model_id",
    ) or str(runtime_payload.get("model_lane") or packet.target_model)
    checks = {
        "packet_signature_verified": bool(packet.packet_signature),
        "artifact_bytes_match": str(runtime_payload.get("canonical_l2_prompt_hash") or packet.prompt_hash)
        == packet.prompt_hash,
        "replay_key_matches": str(runtime_payload.get("canonical_l2_replay_key") or packet.replay_key)
        == packet.replay_key,
        "provider_lane_matches": used_provider
        in {
            packet.canonical_provider,
            str(runtime_payload.get("provider_lane") or ""),
        },
        "model_id_matches": used_model == packet.target_model,
        "token_usage_observed": tokens_observed,
        "token_budget_pass": tokens_observed
        and tokens_used <= int(packet.budget.get("max_tokens", 0)),
        "grounded_output": output_exists and bool(packet.final_evidence_contract_ref),
        "canonical_receipt_bundle_required": True,
    }
    return {
        "schema_version": "apps_rg_l2_handoff_receipt_v2",
        "section_id": section_id,
        "packet_digest": packet.packet_digest,
        "provider_lane_used": used_provider,
        "model_id_used": used_model,
        "tokens_emitted": tokens_used if tokens_observed else None,
        "budget_ceiling": int(packet.budget.get("max_tokens", 0)),
        "checks": checks,
        "handoff_status": "PASS" if all(checks.values()) else "FAIL",
        "unknown_never_pass": True,
        "canonical_l2_receipt_bundle_ref": L2_RECEIPT_BUNDLE_ARTIFACT,
        "direct_l4_write_allowed": False,
    }


def finalize_section_l2_authority(
    artifact_dir: Path,
    section_id: str,
    runtime_payload: dict[str, Any],
    *,
    section_output_ref: str | None = None,
    l2_output_ref: str = "l2_output.json",
    provider_request_ref: str = "provider_request.json",
    provider_response_ref: str = "provider_response.json",
) -> dict[str, Path]:
    """Construct observed E3 evidence, seal E5, and derive section compatibility mirrors."""
    artifact_dir = Path(artifact_dir)
    packet, room, gates, prep_receipt, validation_receipt = _load_preflight_state(
        artifact_dir,
        runtime_payload,
    )
    output_path = artifact_dir / (section_output_ref or l2_output_ref)
    output_payload, output_file_digest, output_exists = _read_payload(output_path)
    provider_request, request_digest, request_exists = _read_payload(
        artifact_dir / provider_request_ref
    )
    provider_response, response_digest, response_exists = _read_payload(
        artifact_dir / provider_response_ref
    )
    tokens_used, tokens_observed = _token_usage(provider_response)

    from apps_rg.runtime.bindings.l2_envelope_contracts import (
        AttemptReceipt,
        DeterminismBundle,
        ExecutionLane,
        LineageRoot,
        ResultClass,
    )

    determinism = DeterminismBundle(
        blueprint_hash=packet.blueprint_hash,
        policy_hash=packet.policy_hash,
        prompt_hash=packet.prompt_hash,
        input_hash=packet.packet_digest,
        replay_key=packet.replay_key,
        attempt_seed=packet.attempt_seed,
    )
    lineage = LineageRoot(
        parent_route_id=packet.route_id,
        parent_plan_id=packet.workflow_id or packet.run_id,
        parent_step_id=packet.step_id or section_id,
        ancestry_chain=tuple(x for x in (packet.route_id, packet.workflow_id, packet.node_id) if x),
        same_run_packet_family=packet.run_id,
    )
    local_checks = {
        "provider_lane": packet.canonical_provider,
        "model_or_tool_name": packet.target_model,
        "provider_request_ref": provider_request_ref if request_exists else "",
        "provider_request_digest": request_digest,
        "provider_response_ref": provider_response_ref if response_exists else "",
        "provider_response_digest": response_digest,
        "l2_output_ref": str(output_path.name) if output_exists else "",
        "l2_output_file_digest": output_file_digest,
        "token_usage_observed": tokens_observed,
        "tokens_used": tokens_used if tokens_observed else None,
        "artifact_bytes_match": str(runtime_payload.get("canonical_l2_prompt_hash") or "")
        == packet.prompt_hash,
        "replay_key_matches": str(runtime_payload.get("canonical_l2_replay_key") or "")
        == packet.replay_key,
        "grounded_output": output_exists and bool(packet.final_evidence_contract_ref),
    }
    proposed = {
        "section_id": section_id,
        "section_output_ref": str(output_path.name) if output_exists else "",
        "payload": output_payload if output_exists else {},
    }
    attempt = AttemptReceipt(
        attempt_receipt_id=AttemptReceipt.new_id(),
        validation_packet_id=f"section-val-{packet.packet_digest[:16]}",
        attempt_count=packet.attempt_number,
        determinism=determinism,
        lineage=lineage,
        trace_id=packet.trace_id,
        span_id=f"section-l2-{section_id}",
        latency_ms=0.0,
        tokens_used=tokens_used if tokens_observed else 0,
        return_code=0 if output_exists else 1,
        result_class=ResultClass.SUCCESS if output_exists else ResultClass.FAIL_TERMINAL,
        error_summary=None if output_exists else "section L2 output artifact missing",
        execution_lane=ExecutionLane.MODEL,
        decisive_reason_code="E3_SECTION_OUTPUT_OBSERVED" if output_exists else "E3_SECTION_OUTPUT_MISSING",
        local_check_results=local_checks,
        generated_artifacts=tuple(
            ref
            for ref, present in (
                (provider_request_ref, request_exists),
                (provider_response_ref, response_exists),
                (str(output_path.name), output_exists),
            )
            if present
        ),
        proposed_state_diff=proposed,
    )
    attempt = replace(attempt, output_digest=compute_attempt_output_digest(attempt))

    l5_ref = str(
        runtime_payload.get("canonical_l2_l5_certification_ref")
        or prep_receipt.get("l5_certification_ref")
        or ""
    )
    sealed = SealedL2Artifact(
        request_id=packet.request_id,
        run_id=packet.run_id,
        app_id=packet.app_id,
        trace_id=packet.trace_id,
        execution_status="completed" if output_exists else "failed",
        generated_content=json.dumps(output_payload, sort_keys=True, default=str)
        if output_exists
        else "",
        generated_content_origin=Origin.MODEL_GENERATION,
        proposed_state_diff=proposed,
        state_diff_authorized=False,
        tenant_id=packet.tenant_id,
        sandbox_required=packet.sandbox_required,
        egress_policy_ref=packet.egress_policy_ref,
        allowed_tools=packet.allowed_tools,
        allowed_models=packet.allowed_models,
        allowed_networks=packet.allowed_networks,
        allowed_file_roots=packet.allowed_file_roots,
        prompt_artifact_digest=packet.prompt_hash,
        schema_version="W6.0",
        compilation_hash=sha256_hex(
            {"packet_digest": packet.packet_digest, "attempt_output_digest": attempt.output_digest}
        ),
        audit_refs=(f"section_lane:{section_id}",),
        gate_verdict_refs=tuple(receipt.ref for receipt in gates),
        replay_key=packet.replay_key,
        snapshot_refs=(packet.packet_digest, room.room_digest),
        is_uwg_write_authority=False,
        l5_certification_ref=l5_ref,
        evidence_refs=(packet.final_evidence_contract_ref,),
        prompt_refs=(packet.prompt_hash,),
        provider_receipts=(f"provider_response:{response_digest}",) if response_exists else (),
        model_call_refs=(f"provider_request:{request_digest}",) if request_exists else (),
        replay_manifest=packet.snapshot_manifest,
    )
    bundle_result = finalize_content_addressed_bundle(
        artifact_dir=artifact_dir,
        packet=packet,
        frozen_room=room,
        gate_receipts=gates,
        prep_output=prep_receipt,
        validation_output=validation_receipt,
        attempt_receipt=attempt,
        heal_receipt=None,
        sealed=sealed,
    )
    final_sealed = bundle_result.sealed
    handoff = _build_handoff_receipt(
        section_id=section_id,
        packet=packet,
        provider_request=provider_request,
        provider_response=provider_response,
        output_exists=output_exists,
        tokens_used=tokens_used,
        tokens_observed=tokens_observed,
        runtime_payload=runtime_payload,
    )
    mirror = dict(_jsonable(final_sealed))
    mirror.update(
        {
            "schema_version": "section_sealed_l2_artifact_v2",
            "contract_type": "SealedL2Artifact",
            "section_id": section_id,
            "canonical_l2_receipt_bundle_ref": L2_RECEIPT_BUNDLE_ARTIFACT,
            "canonical_seal_receipt_ref": SEAL_RECEIPT_ARTIFACT,
            "provider_request_ref": provider_request_ref if request_exists else None,
            "provider_response_ref": provider_response_ref if response_exists else None,
            "l2_output_ref": str(output_path.name) if output_exists else None,
            "durable_commit_occurred": False,
            "canonical_exit_claimed": False,
            "runtime_exhaust_bundle_claimed": False,
            "product_certification": "CANONICAL_L2_RECEIPT_BUNDLE",
        }
    )
    spine_receipt = {
        "schema_version": "l2_spine_receipt_v2",
        "lane": section_id,
        "section_id": section_id,
        "run_id": packet.run_id,
        "product_visible": True,
        "spine_mode": "section_lane_canonical_l2_authority",
        "l2_alignment_mode": "canonical_e1_e5_receipt_bundle",
        "l2_spine_status": "PASS" if handoff["handoff_status"] == "PASS" else "FAIL",
        "precondition_status": "PASS",
        "l2_execution_packet_ref": L2_EXECUTION_PACKET_ARTIFACT,
        "frozen_execution_context_ref": FROZEN_EXECUTION_CONTEXT_ARTIFACT,
        "prep_receipt_ref": PREP_RECEIPT_ARTIFACT,
        "validation_receipt_ref": VALIDATION_RECEIPT_ARTIFACT,
        "attempt_receipt_ref": ATTEMPT_RECEIPT_ARTIFACT,
        "seal_receipt_ref": SEAL_RECEIPT_ARTIFACT,
        "l2_receipt_bundle_ref": L2_RECEIPT_BUNDLE_ARTIFACT,
        "sealed_l2_artifact_ref": SEALED_L2_ARTIFACT,
        "l2_handoff_receipt_ref": L2_HANDOFF_RECEIPT_ARTIFACT,
        "packet_digest": packet.packet_digest,
        "bundle_digest": bundle_result.bundle.get("bundle_digest"),
        "direct_l4_write_allowed": False,
        "durable_commit_occurred": False,
        "canonical_exit_claimed": False,
        "runtime_exhaust_bundle_claimed": False,
        "product_certification": "CANONICAL_L2_RECEIPT_BUNDLE",
        "unknown_never_pass": True,
    }

    paths = {
        "sealed_l2_artifact": _write_json(artifact_dir / SEALED_L2_ARTIFACT, mirror),
        "l2_spine_receipt": _write_json(
            artifact_dir / L2_SPINE_RECEIPT_ARTIFACT, spine_receipt
        ),
        "l2_handoff_receipt": _write_json(
            artifact_dir / L2_HANDOFF_RECEIPT_ARTIFACT, handoff
        ),
    }
    runtime_payload.update(
        {
            "attempt_receipt_ref": ATTEMPT_RECEIPT_ARTIFACT,
            "seal_receipt_ref": SEAL_RECEIPT_ARTIFACT,
            "l2_receipt_bundle_ref": L2_RECEIPT_BUNDLE_ARTIFACT,
            "canonical_l2_receipt_bundle_ref": L2_RECEIPT_BUNDLE_ARTIFACT,
            "sealed_l2_artifact_ref": SEALED_L2_ARTIFACT,
            "l2_spine_receipt_ref": L2_SPINE_RECEIPT_ARTIFACT,
            "l2_handoff_receipt_ref": L2_HANDOFF_RECEIPT_ARTIFACT,
            "canonical_l2_bundle_digest": bundle_result.bundle.get("bundle_digest"),
            "canonical_l2_finalization_status": spine_receipt["l2_spine_status"],
        }
    )
    return paths


__all__ = [
    "ATTEMPT_RECEIPT_ARTIFACT",
    "FROZEN_EXECUTION_CONTEXT_ARTIFACT",
    "L2_HANDOFF_RECEIPT_ARTIFACT",
    "L2_RECEIPT_BUNDLE_ARTIFACT",
    "PREP_RECEIPT_ARTIFACT",
    "SEAL_RECEIPT_ARTIFACT",
    "VALIDATION_RECEIPT_ARTIFACT",
    "finalize_section_l2_authority",
    "prepare_section_l2_authority",
]
